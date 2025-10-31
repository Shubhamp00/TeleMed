# TeleHealth Platform - Installation & Setup Guide

This guide will walk you through setting up and running the TeleHealth Teleconsultation Platform from scratch.

---

## Prerequisites

Before you begin, ensure you have the following installed on your system:

- **Python 3.11 or higher** - [Download Python](https://www.python.org/downloads/)
- **pip** (Python package manager) - Usually comes with Python
- **Git** (optional, for cloning the repository)

---

## Step 1: Download or Clone the Project

### Option A: Clone from Git Repository
```bash
git clone <your-repository-url>
cd <project-directory>
```

### Option B: Download ZIP
1. Download the project ZIP file
2. Extract it to your desired location
3. Open terminal/command prompt and navigate to the project directory

---

## Step 2: Set Up Python Virtual Environment (Recommended)

Creating a virtual environment keeps your project dependencies isolated.

### On Windows:
```bash
python -m venv venv
venv\Scripts\activate
```

### On macOS/Linux:
```bash
python3 -m venv venv
source venv/bin/activate
```

You should see `(venv)` appear in your terminal prompt.

---

## Step 3: Install Required Dependencies

Install all required Python packages using the requirements file:

```bash
pip install -r requirements.txt
```

This will install:
- Flask and Flask extensions
- OpenCV and MediaPipe for Computer Vision
- Faster Whisper for speech-to-text
- WebRTC libraries (aiortc)
- Socket.IO for real-time communication
- Other supporting libraries

**Note:** Installation may take 5-10 minutes depending on your internet speed.

---

## Step 4: Set Up Environment Variables (Optional)

Create a `.env` file in the project root directory (optional):

```bash
SESSION_SECRET=your-secret-key-here
```

If you don't create this file, the application will use a default development secret.

---

## Step 5: Verify Installation

Check if all modules are installed correctly:

```bash
python -c "import flask, cv2, mediapipe, faster_whisper; print('All dependencies installed successfully!')"
```

If you see the success message, you're ready to proceed!

---

## Step 6: Run the Application

Start the Flask server:

```bash
python app.py
```

You should see output similar to:
```
Loading Faster Whisper model: base
Faster Whisper model loaded successfully
 * Running on http://0.0.0.0:5000
```

**Note:** The first time you run the application, it will download the Faster Whisper model (~145MB). This is a one-time download.

---

## Step 7: Access the Application

Open your web browser and navigate to:

```
http://localhost:5000
```

You should see the TeleHealth welcome page with two options:
- **Doctor Portal** (blue button)
- **Patient Portal** (green button)

---

## Step 8: Test the Platform

### Testing with Two Browser Windows:

1. **Window 1 - Doctor:**
   - Click "Enter as Doctor"
   - Click "Create New Consultation"
   - Note the Session ID that appears
   - You'll be redirected to the consultation room

2. **Window 2 - Patient:**
   - Click "Enter as Patient"
   - Enter the Session ID from the doctor
   - Click "Join Session"
   - Allow camera and microphone access when prompted

3. **During the Call:**
   - Both video feeds should appear
   - CV Analysis panel will show facial expression and posture data
   - Live Transcription panel will display the conversation as text
   - Use camera/microphone toggle buttons to control media
   - Click "End Consultation" to terminate the session

---

## Troubleshooting

### Issue: "Module not found" error
**Solution:** Make sure you activated the virtual environment and ran `pip install -r requirements.txt`

### Issue: Camera/Microphone not working
**Solution:** 
- Ensure you clicked "Allow" when the browser asks for permissions
- Check your browser settings for camera/microphone access
- Try using Chrome or Firefox (best WebRTC support)

### Issue: Port 5000 already in use
**Solution:** 
- Stop any other applications using port 5000
- Or modify the port in `app.py` (last line): `socketio.run(app, host='0.0.0.0', port=8080)`

### Issue: Video connection not establishing
**Solution:**
- Check your firewall settings
- Ensure both browsers can access the STUN servers
- Try opening both browser windows on the same computer first

### Issue: Slow performance
**Solution:**
- The CV analysis runs every 2 seconds by default
- Audio transcription processes 5-second chunks
- For better performance, ensure you have adequate RAM (4GB+ recommended)

---

## System Requirements

### Minimum:
- **CPU:** Dual-core processor
- **RAM:** 4GB
- **Internet:** Stable broadband connection
- **Browser:** Chrome 90+, Firefox 88+, or Edge 90+

### Recommended:
- **CPU:** Quad-core processor or better
- **RAM:** 8GB or more
- **Internet:** High-speed broadband
- **Webcam:** 720p or higher
- **Microphone:** Built-in or external

---

## Stopping the Application

To stop the server:
1. Press `Ctrl + C` in the terminal where the app is running
2. Wait for the shutdown message
3. Deactivate the virtual environment (optional): `deactivate`

---

## Project Structure

```
telehealth-platform/
│
├── app.py                      # Main Flask application
├── cv_module.py                # Computer Vision analysis module
├── whisper_module.py           # Speech-to-text module
├── requirements.txt            # Python dependencies
├── README.md                   # Project overview
├── SETUP.md                    # This file
│
├── templates/                  # HTML templates
│   ├── index.html             # Landing page
│   ├── doctor.html            # Doctor portal
│   ├── patient.html           # Patient portal
│   └── consultation.html      # Video consultation interface
│
└── static/                     # Static assets
    ├── css/
    │   └── style.css          # Custom styles
    └── js/
        └── consultation.js    # WebRTC & real-time logic
```

---

## Next Steps

Once the application is running successfully:

1. **Test all features** with multiple users
2. **Customize the UI** to match your branding (edit CSS files)
3. **Configure security** settings for production deployment
4. **Set up a production server** (Gunicorn, Nginx) for live deployment
5. **Add database** for storing consultation history (optional)

---

## Need Help?

If you encounter any issues not covered in this guide:

1. Check the terminal output for error messages
2. Verify all dependencies are installed correctly
3. Ensure your Python version is 3.11 or higher
4. Review the browser console for JavaScript errors (F12)

---

## Production Deployment Notes

For production use:

- Use a proper WSGI server (Gunicorn) instead of Flask's development server
- Set up HTTPS/SSL certificates for secure video transmission
- Configure a reverse proxy (Nginx/Apache)
- Use environment variables for sensitive configuration
- Consider using a TURN server for better WebRTC connectivity
- Implement proper authentication and authorization
- Add database for user management and consultation records
- Consider HIPAA compliance requirements for medical applications

---

**Congratulations!** You now have a fully functional AI-powered teleconsultation platform running on your system.
