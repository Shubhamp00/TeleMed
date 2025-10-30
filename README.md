# TeleHealth - AI-Powered Teleconsultation Platform

A comprehensive doctor-patient teleconsultation platform with custom WebRTC video calling, Computer Vision analysis, and Faster Whisper speech-to-text transcription.

## Features

### 🎥 Real-Time Video Calling
- Custom WebRTC implementation for peer-to-peer video and audio streaming
- Low-latency communication with STUN server support
- Camera and microphone controls

### 👁️ Computer Vision Analysis
Powered by MediaPipe and OpenCV to detect:
- **Facial Expressions**: Pain indicators, emotional state, squinting, smiling
- **Posture Analysis**: Head tilt, shoulder alignment, leaning posture
- **Skin Conditions**: Brightness, contrast, texture irregularities
- **Visual Health Indicators**: Real-time alerts for detected anomalies

### 🎤 Speech-to-Text Transcription
- Real-time audio transcription using Faster Whisper
- Automatic symptom keyword extraction
- Live transcript display during consultations
- Conversation summarization

### 🏥 Medical-Grade Interface
- Separate Doctor and Patient portals
- Session-based consultations with unique IDs
- Professional medical-themed UI with Bootstrap 5
- Real-time synchronization via Socket.IO

## How to Use

### For Doctors:
1. Click "Enter as Doctor" on the homepage
2. Create a new consultation session
3. Share the Session ID with your patient
4. Wait for the patient to join
5. Conduct the consultation with AI-assisted analysis

### For Patients:
1. Click "Enter as Patient" on the homepage
2. Enter the Session ID provided by your doctor
3. Allow camera and microphone access
4. Join the consultation

## During Consultation

### Video Controls:
- **Camera Toggle**: Turn video on/off
- **Microphone Toggle**: Mute/unmute audio
- **End Call**: Terminate the consultation

### Live Analysis Panels:
- **CV Analysis**: Real-time visual health indicators from the patient's video
- **Live Transcription**: Automatic speech-to-text of the conversation

## Technical Architecture

### Backend (Python/Flask)
- Flask with Socket.IO for real-time communication
- MediaPipe & OpenCV for computer vision
- Faster Whisper for speech transcription
- WebRTC signaling server

### Frontend
- HTML5, Bootstrap 5, Vanilla JavaScript
- WebRTC for peer-to-peer video streaming
- Socket.IO client for real-time data sync

## Requirements

All dependencies are pre-installed:
- Python 3.11
- Flask, Flask-SocketIO, Flask-CORS
- OpenCV, MediaPipe
- Faster Whisper
- aiortc, aiohttp
- Eventlet for async support

## Running the Application

The server runs automatically on port 5000. Simply access the application URL and choose your role (Doctor or Patient).

## Privacy & Security

- Peer-to-peer video communication (not stored on server)
- Session-based architecture with unique IDs
- No persistent storage of medical data
- All processing happens in real-time

## Future Enhancements

- Medical note generation from transcripts
- Patient history database integration
- Appointment scheduling system
- HIPAA-compliance features
- GPU acceleration for CV processing
- Multi-language support for transcription

## Support

For issues or questions, please contact your system administrator.

---

Built with ❤️ for better healthcare accessibility
