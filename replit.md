# TeleHealth - AI-Powered Teleconsultation Platform

## Overview
TeleHealth is a comprehensive doctor-patient teleconsultation platform built with Python that features:
- Custom WebRTC-based real-time video and audio communication
- Computer Vision analysis using MediaPipe and OpenCV for detecting facial expressions, posture, and visual health indicators
- Faster Whisper integration for real-time speech-to-text transcription
- AI-assisted medical note-taking and symptom detection

## Project Architecture

### Backend (Python/Flask)
- **app.py**: Main Flask application with Socket.IO for real-time communication
- **cv_module.py**: Computer Vision analysis module using MediaPipe and OpenCV
  - Facial expression detection (pain indicators, emotional state)
  - Posture analysis (head tilt, shoulder alignment)
  - Skin condition analysis (brightness, contrast, texture)
- **whisper_module.py**: Faster Whisper integration for speech-to-text
  - Real-time audio transcription
  - Symptom keyword extraction
  - Conversation summarization

### Frontend
- **templates/**: HTML templates with Bootstrap 5
  - `index.html`: Landing page with role selection
  - `doctor.html`: Doctor portal for creating/joining sessions
  - `patient.html`: Patient portal for joining consultations
  - `consultation.html`: Main consultation interface with video calling
- **static/**: CSS and JavaScript assets
  - `css/style.css`: Custom styling with medical theme
  - `js/consultation.js`: WebRTC implementation and real-time processing

### Key Features
1. **WebRTC Video Calling**: Peer-to-peer video/audio streaming with STUN servers
2. **Real-time CV Analysis**: Processes video frames every 2 seconds to detect:
   - Facial expressions (pain, distress, smiling, squinting)
   - Posture issues (head tilt, shoulder imbalance, leaning)
   - Visual health indicators
3. **Live Transcription**: Captures audio in 5-second segments for Faster Whisper processing
4. **Session Management**: Socket.IO-based signaling for WebRTC and data synchronization
5. **Role-Based Interface**: Separate doctor and patient portals with appropriate features

## Technology Stack
- **Backend**: Flask, Flask-SocketIO, Eventlet
- **Computer Vision**: OpenCV, MediaPipe
- **AI/ML**: Faster Whisper (speech-to-text)
- **Real-time Communication**: WebRTC, Socket.IO
- **Frontend**: HTML5, Bootstrap 5, Vanilla JavaScript
- **Media Processing**: Pillow, NumPy

## Recent Changes (October 30, 2025)
- Initial project setup with complete teleconsultation platform
- Implemented WebRTC video calling infrastructure
- Integrated MediaPipe for comprehensive CV analysis
- Added Faster Whisper for real-time transcription
- Created professional medical-themed UI with Bootstrap
- Set up Socket.IO for real-time data synchronization

## Running the Application
The application runs on port 5000 using Flask with Socket.IO in eventlet async mode.
Access the platform at the provided URL and select either Doctor or Patient portal.

## User Preferences
- Medical-grade application with professional UI
- Real-time processing of video and audio streams
- AI-assisted analysis for doctors during consultations
