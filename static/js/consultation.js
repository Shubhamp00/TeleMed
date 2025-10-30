const socket = io();

let localStream = null;
let remoteStream = null;
let peerConnection = null;
let isVideoEnabled = true;
let isAudioEnabled = true;

const configuration = {
    iceServers: [
        { urls: 'stun:stun.l.google.com:19302' },
        { urls: 'stun:stun1.l.google.com:19302' }
    ]
};

let videoFrameInterval = null;
let audioRecorder = null;
let audioContext = null;

async function initializeMedia() {
    try {
        localStream = await navigator.mediaDevices.getUserMedia({
            video: { width: 1280, height: 720 },
            audio: {
                echoCancellation: true,
                noiseSuppression: true,
                sampleRate: 16000
            }
        });
        
        document.getElementById('localVideo').srcObject = localStream;
        
        startVideoFrameCapture();
        startAudioCapture();
        
    } catch (error) {
        console.error('Error accessing media devices:', error);
        alert('Cannot access camera/microphone. Please check permissions.');
    }
}

function startVideoFrameCapture() {
    const canvas = document.createElement('canvas');
    const video = document.getElementById('localVideo');
    
    videoFrameInterval = setInterval(() => {
        if (video.readyState === video.HAVE_ENOUGH_DATA) {
            canvas.width = video.videoWidth;
            canvas.height = video.videoHeight;
            const ctx = canvas.getContext('2d');
            ctx.drawImage(video, 0, 0);
            
            const frameData = canvas.toDataURL('image/jpeg', 0.7);
            
            socket.emit('video_frame', {
                session_id: sessionId,
                frame: frameData
            });
        }
    }, 2000);
}

function startAudioCapture() {
    try {
        audioContext = new (window.AudioContext || window.webkitAudioContext)();
        const source = audioContext.createMediaStreamSource(localStream);
        const processor = audioContext.createScriptProcessor(16384, 1, 1);
        
        let audioBuffer = [];
        let bufferDuration = 0;
        const TARGET_DURATION = 5;
        
        processor.onaudioprocess = (e) => {
            const inputData = e.inputBuffer.getChannelData(0);
            audioBuffer.push(new Float32Array(inputData));
            bufferDuration += inputData.length / audioContext.sampleRate;
            
            if (bufferDuration >= TARGET_DURATION) {
                const totalLength = audioBuffer.reduce((acc, arr) => acc + arr.length, 0);
                const combinedBuffer = new Float32Array(totalLength);
                let offset = 0;
                audioBuffer.forEach(arr => {
                    combinedBuffer.set(arr, offset);
                    offset += arr.length;
                });
                
                const wavBlob = encodeWAV(combinedBuffer, audioContext.sampleRate);
                const reader = new FileReader();
                reader.onloadend = () => {
                    const base64Audio = reader.result;
                    socket.emit('audio_chunk', {
                        session_id: sessionId,
                        audio: base64Audio,
                        speaker: userRole
                    });
                };
                reader.readAsDataURL(wavBlob);
                
                audioBuffer = [];
                bufferDuration = 0;
            }
        };
        
        source.connect(processor);
        processor.connect(audioContext.destination);
        
    } catch (error) {
        console.error('Error setting up audio capture:', error);
    }
}

function encodeWAV(samples, sampleRate) {
    const buffer = new ArrayBuffer(44 + samples.length * 2);
    const view = new DataView(buffer);
    
    const writeString = (offset, string) => {
        for (let i = 0; i < string.length; i++) {
            view.setUint8(offset + i, string.charCodeAt(i));
        }
    };
    
    writeString(0, 'RIFF');
    view.setUint32(4, 36 + samples.length * 2, true);
    writeString(8, 'WAVE');
    writeString(12, 'fmt ');
    view.setUint32(16, 16, true);
    view.setUint16(20, 1, true);
    view.setUint16(22, 1, true);
    view.setUint32(24, sampleRate, true);
    view.setUint32(28, sampleRate * 2, true);
    view.setUint16(32, 2, true);
    view.setUint16(34, 16, true);
    writeString(36, 'data');
    view.setUint32(40, samples.length * 2, true);
    
    const floatTo16BitPCM = (output, offset, input) => {
        for (let i = 0; i < input.length; i++, offset += 2) {
            const s = Math.max(-1, Math.min(1, input[i]));
            output.setInt16(offset, s < 0 ? s * 0x8000 : s * 0x7FFF, true);
        }
    };
    
    floatTo16BitPCM(view, 44, samples);
    
    return new Blob([buffer], { type: 'audio/wav' });
}

socket.on('connect', () => {
    console.log('Connected to server');
    socket.emit('join_session', {
        session_id: sessionId,
        role: userRole
    });
});

socket.on('joined_session', (data) => {
    console.log('Joined session:', data);
    initializeMedia();
});

socket.on('peer_joined', async (data) => {
    console.log('Peer joined:', data);
    document.getElementById('waitingMessage').style.display = 'none';
    
    if (userRole === 'doctor') {
        await createOffer();
    }
});

socket.on('webrtc_offer', async (data) => {
    console.log('Received offer');
    await handleOffer(data.offer);
});

socket.on('webrtc_answer', async (data) => {
    console.log('Received answer');
    await handleAnswer(data.answer);
});

socket.on('webrtc_ice_candidate', async (data) => {
    if (peerConnection && data.candidate) {
        try {
            await peerConnection.addIceCandidate(new RTCIceCandidate(data.candidate));
        } catch (error) {
            console.error('Error adding ICE candidate:', error);
        }
    }
});

socket.on('cv_analysis', (data) => {
    displayCVAnalysis(data.analysis);
});

socket.on('transcription', (data) => {
    displayTranscription(data.transcript);
});

socket.on('session_ended', () => {
    alert('Session has been ended');
    window.location.href = '/';
});

socket.on('peer_disconnected', () => {
    document.getElementById('waitingMessage').style.display = 'block';
    document.getElementById('waitingMessage').innerHTML = '<div class="spinner-border mb-2" role="status"></div><div>Peer disconnected. Waiting to reconnect...</div>';
});

async function createPeerConnection() {
    peerConnection = new RTCPeerConnection(configuration);
    
    localStream.getTracks().forEach(track => {
        peerConnection.addTrack(track, localStream);
    });
    
    peerConnection.ontrack = (event) => {
        if (!remoteStream) {
            remoteStream = new MediaStream();
            document.getElementById('remoteVideo').srcObject = remoteStream;
        }
        remoteStream.addTrack(event.track);
        document.getElementById('waitingMessage').style.display = 'none';
    };
    
    peerConnection.onicecandidate = (event) => {
        if (event.candidate) {
            socket.emit('webrtc_ice_candidate', {
                session_id: sessionId,
                candidate: event.candidate
            });
        }
    };
    
    peerConnection.onconnectionstatechange = () => {
        console.log('Connection state:', peerConnection.connectionState);
    };
}

async function createOffer() {
    await createPeerConnection();
    const offer = await peerConnection.createOffer();
    await peerConnection.setLocalDescription(offer);
    
    socket.emit('webrtc_offer', {
        session_id: sessionId,
        offer: offer
    });
}

async function handleOffer(offer) {
    await createPeerConnection();
    await peerConnection.setRemoteDescription(new RTCSessionDescription(offer));
    const answer = await peerConnection.createAnswer();
    await peerConnection.setLocalDescription(answer);
    
    socket.emit('webrtc_answer', {
        session_id: sessionId,
        answer: answer
    });
}

async function handleAnswer(answer) {
    await peerConnection.setRemoteDescription(new RTCSessionDescription(answer));
}

function displayCVAnalysis(analysis) {
    const panel = document.getElementById('cvAnalysisPanel');
    
    let html = '<div class="mb-3">';
    
    if (analysis.facial_expression) {
        html += `
            <div class="mb-2">
                <strong>Expression:</strong> ${analysis.facial_expression.expression}
                <div class="mt-1">
                    ${analysis.facial_expression.indicators.map(ind => 
                        `<span class="indicator-badge indicator-warning">${ind.replace(/_/g, ' ')}</span>`
                    ).join('')}
                </div>
            </div>
        `;
    }
    
    if (analysis.posture) {
        html += `
            <div class="mb-2">
                <strong>Posture:</strong> ${analysis.posture.status}
                <div class="mt-1">
                    ${analysis.posture.indicators.map(ind => 
                        `<span class="indicator-badge indicator-warning">${ind.replace(/_/g, ' ')}</span>`
                    ).join('')}
                </div>
            </div>
        `;
    }
    
    if (analysis.overall_indicators && analysis.overall_indicators.length > 0) {
        html += `
            <div class="alert alert-warning alert-sm p-2 mb-0">
                <small><strong>Alerts:</strong></small><br>
                ${analysis.overall_indicators.map(ind => 
                    `<span class="indicator-badge indicator-danger">${ind.replace(/_/g, ' ')}</span>`
                ).join('')}
            </div>
        `;
    }
    
    html += '</div>';
    panel.innerHTML = html + panel.innerHTML;
    
    if (panel.children.length > 10) {
        panel.removeChild(panel.lastChild);
    }
}

function displayTranscription(transcript) {
    const panel = document.getElementById('transcriptPanel');
    
    const time = new Date(transcript.timestamp).toLocaleTimeString();
    const html = `
        <div class="transcript-item">
            <div class="d-flex justify-content-between mb-1">
                <strong class="text-capitalize">${transcript.speaker}</strong>
                <small class="text-muted">${time}</small>
            </div>
            <div>${transcript.text}</div>
        </div>
    `;
    
    panel.innerHTML = html + panel.innerHTML;
    
    if (panel.children.length > 20) {
        panel.removeChild(panel.lastChild);
    }
}

document.getElementById('toggleVideo').addEventListener('click', () => {
    isVideoEnabled = !isVideoEnabled;
    localStream.getVideoTracks()[0].enabled = isVideoEnabled;
    
    const btn = document.getElementById('toggleVideo');
    btn.classList.toggle('btn-danger');
    btn.classList.toggle('btn-secondary');
});

document.getElementById('toggleAudio').addEventListener('click', () => {
    isAudioEnabled = !isAudioEnabled;
    localStream.getAudioTracks()[0].enabled = isAudioEnabled;
    
    const btn = document.getElementById('toggleAudio');
    btn.classList.toggle('btn-warning');
    btn.classList.toggle('btn-secondary');
});

document.getElementById('endCallBtn').addEventListener('click', () => {
    if (confirm('Are you sure you want to end this consultation?')) {
        socket.emit('end_session', { session_id: sessionId });
        
        if (videoFrameInterval) {
            clearInterval(videoFrameInterval);
        }
        
        if (localStream) {
            localStream.getTracks().forEach(track => track.stop());
        }
        
        if (peerConnection) {
            peerConnection.close();
        }
        
        window.location.href = '/';
    }
});
