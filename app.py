from flask import Flask, render_template, request, jsonify, session
from flask_socketio import SocketIO, emit, join_room, leave_room
from flask_cors import CORS
import os
import uuid
import threading
import queue
import base64
import io
from datetime import datetime
import json

from cv_module import CVAnalyzer
from whisper_module import WhisperTranscriber

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SESSION_SECRET', 'dev-secret-key-change-in-production')
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='eventlet', max_http_buffer_size=10**7)

cv_analyzer = CVAnalyzer()
whisper_transcriber = WhisperTranscriber()

active_sessions = {}
transcription_queues = {}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/doctor')
def doctor():
    return render_template('doctor.html')

@app.route('/patient')
def patient():
    return render_template('patient.html')

@app.route('/consultation/<session_id>')
def consultation(session_id):
    role = request.args.get('role', 'patient')
    return render_template('consultation.html', session_id=session_id, role=role)

@socketio.on('connect')
def handle_connect():
    print(f'Client connected: {request.sid}')
    emit('connected', {'sid': request.sid})

@socketio.on('disconnect')
def handle_disconnect():
    print(f'Client disconnected: {request.sid}')
    for session_id, session_data in active_sessions.items():
        if request.sid in [session_data.get('doctor_sid'), session_data.get('patient_sid')]:
            emit('peer_disconnected', {'session_id': session_id}, room=session_id)

@socketio.on('join_session')
def handle_join_session(data):
    session_id = data.get('session_id')
    role = data.get('role', 'patient')
    
    if session_id not in active_sessions:
        active_sessions[session_id] = {
            'created_at': datetime.now().isoformat(),
            'transcripts': [],
            'cv_analysis': []
        }
        transcription_queues[session_id] = queue.Queue()
    
    if role == 'doctor':
        active_sessions[session_id]['doctor_sid'] = request.sid
    else:
        active_sessions[session_id]['patient_sid'] = request.sid
    
    join_room(session_id)
    print(f'{role} joined session {session_id}')
    
    emit('joined_session', {
        'session_id': session_id,
        'role': role,
        'message': f'Successfully joined session as {role}'
    })
    
    emit('peer_joined', {
        'role': role,
        'session_id': session_id
    }, room=session_id, skip_sid=request.sid)

@socketio.on('webrtc_offer')
def handle_webrtc_offer(data):
    session_id = data.get('session_id')
    offer = data.get('offer')
    
    emit('webrtc_offer', {
        'offer': offer,
        'from_sid': request.sid
    }, room=session_id, skip_sid=request.sid)

@socketio.on('webrtc_answer')
def handle_webrtc_answer(data):
    session_id = data.get('session_id')
    answer = data.get('answer')
    
    emit('webrtc_answer', {
        'answer': answer,
        'from_sid': request.sid
    }, room=session_id, skip_sid=request.sid)

@socketio.on('webrtc_ice_candidate')
def handle_ice_candidate(data):
    session_id = data.get('session_id')
    candidate = data.get('candidate')
    
    emit('webrtc_ice_candidate', {
        'candidate': candidate,
        'from_sid': request.sid
    }, room=session_id, skip_sid=request.sid)

@socketio.on('video_frame')
def handle_video_frame(data):
    session_id = data.get('session_id')
    frame_data = data.get('frame')
    
    if not frame_data:
        return
    
    try:
        analysis = cv_analyzer.analyze_frame(frame_data)
        
        if analysis:
            if session_id in active_sessions:
                active_sessions[session_id]['cv_analysis'].append({
                    'timestamp': datetime.now().isoformat(),
                    'analysis': analysis
                })
            
            emit('cv_analysis', {
                'session_id': session_id,
                'analysis': analysis,
                'timestamp': datetime.now().isoformat()
            }, room=session_id)
    
    except Exception as e:
        print(f'Error analyzing video frame: {e}')

@socketio.on('audio_chunk')
def handle_audio_chunk(data):
    session_id = data.get('session_id')
    audio_data = data.get('audio')
    speaker = data.get('speaker', 'unknown')
    
    if not audio_data:
        return
    
    try:
        transcription = whisper_transcriber.transcribe_audio(audio_data)
        
        if transcription and transcription.strip():
            transcript_entry = {
                'timestamp': datetime.now().isoformat(),
                'speaker': speaker,
                'text': transcription
            }
            
            if session_id in active_sessions:
                active_sessions[session_id]['transcripts'].append(transcript_entry)
            
            emit('transcription', {
                'session_id': session_id,
                'transcript': transcript_entry
            }, room=session_id)
    
    except Exception as e:
        print(f'Error transcribing audio: {e}')

@socketio.on('get_session_data')
def handle_get_session_data(data):
    session_id = data.get('session_id')
    
    if session_id in active_sessions:
        emit('session_data', {
            'session_id': session_id,
            'data': active_sessions[session_id]
        })
    else:
        emit('session_data', {
            'session_id': session_id,
            'data': None,
            'error': 'Session not found'
        })

@socketio.on('end_session')
def handle_end_session(data):
    session_id = data.get('session_id')
    
    emit('session_ended', {
        'session_id': session_id,
        'message': 'Session has been ended'
    }, room=session_id)
    
    print(f'Session {session_id} ended')

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000, debug=True, allow_unsafe_werkzeug=True)
