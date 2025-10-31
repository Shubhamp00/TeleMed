# TeleHealth Platform - Troubleshooting Guide

This guide helps you resolve common issues when setting up and running the TeleHealth platform.

---

## 🔴 CRITICAL: Network Timeout Error When Starting

### Error Message:
```
TimeoutError: [WinError 10060] A connection attempt failed...
Error in whisper_module.py when initializing WhisperModel
```

### What's Happening:
The Faster Whisper AI model needs to download ~145MB from HuggingFace servers on first run. If your network is blocked, slow, or behind a firewall/proxy, the download will timeout.

### ✅ SOLUTION 1: Run with Network Access

**Step 1: Check Your Internet Connection**
- Ensure you have a stable internet connection
- Try opening https://huggingface.co in your browser
- Speed test: You need at least 2-5 Mbps download speed

**Step 2: Disable Restrictions (Temporarily)**
- Turn off VPN or proxy
- Disable corporate firewall (if allowed)
- Try using a personal hotspot/different network

**Step 3: Run the Application**
```bash
python app.py
```

The model will download once (takes 2-5 minutes), then it's cached locally for future use.

---

### ✅ SOLUTION 2: Manual Model Download

If automatic download keeps failing, download the model manually:

**Windows:**
```bash
# Create cache directory
mkdir %USERPROFILE%\.cache\huggingface\hub

# Download model manually from:
# https://huggingface.co/guillaumekln/faster-whisper-base
# Extract to: %USERPROFILE%\.cache\huggingface\hub\models--guillaumekln--faster-whisper-base
```

**macOS/Linux:**
```bash
# Create cache directory
mkdir -p ~/.cache/huggingface/hub

# Download using wget or curl
wget https://huggingface.co/guillaumekln/faster-whisper-base/resolve/main/model.bin
wget https://huggingface.co/guillaumekln/faster-whisper-base/resolve/main/config.json
wget https://huggingface.co/guillaumekln/faster-whisper-base/resolve/main/vocabulary.txt
wget https://huggingface.co/guillaumekln/faster-whisper-base/resolve/main/tokenizer.json
```

---

### ✅ SOLUTION 3: Run Without Transcription (Recommended for Quick Start)

**Good News:** The application is now designed to work even if the Whisper model fails to load!

When you run `python app.py`, you'll see one of these messages:

**✓ Success:**
```
✓ Faster Whisper model loaded successfully!
```
All features work including transcription.

**⚠ Partial Success:**
```
⚠ Network Error: Unable to download Whisper model
   Transcription feature will be DISABLED.
   The app will continue to work without speech-to-text.
```

**What Still Works:**
- ✅ WebRTC video calling
- ✅ Computer Vision analysis (facial expressions, posture)
- ✅ All UI features
- ❌ Speech-to-text transcription (disabled)

You can still use the platform for video consultations with CV analysis. Transcription will show: `[Transcription unavailable - Model not loaded]`

---

## 🔧 Other Common Issues

### Issue: "Module not found" Errors

**Error:**
```
ModuleNotFoundError: No module named 'flask' (or other packages)
```

**Solution:**
```bash
# Activate virtual environment first
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate     # Windows

# Then install dependencies
pip install -r requirements.txt
```

---

### Issue: Camera/Microphone Not Working

**Symptoms:**
- Black screen in video feed
- No audio being captured
- Browser doesn't ask for permissions

**Solutions:**

1. **Grant Browser Permissions:**
   - Chrome: Settings → Privacy and Security → Site Settings → Camera/Microphone
   - Firefox: Preferences → Privacy & Security → Permissions
   - Allow access for `localhost` or your server address

2. **Check Device Availability:**
   - Close other apps using camera/mic (Zoom, Teams, Skype)
   - Verify devices work in other applications
   - Restart browser

3. **Use HTTPS (for remote access):**
   - WebRTC requires HTTPS for non-localhost connections
   - Use ngrok or similar for testing: `ngrok http 5000`

---

### Issue: Port 5000 Already in Use

**Error:**
```
OSError: [Errno 48] Address already in use
```

**Solution 1 - Stop Other Process:**
```bash
# Windows
netstat -ano | findstr :5000
taskkill /PID <PID> /F

# macOS/Linux
lsof -i :5000
kill -9 <PID>
```

**Solution 2 - Use Different Port:**

Edit `app.py` (last line):
```python
socketio.run(app, host='0.0.0.0', port=8080, debug=True)
```

Then access: `http://localhost:8080`

---

### Issue: CV Analysis Not Showing

**Symptoms:**
- Video works but no facial expression data appears
- CV Analysis panel shows "Waiting for video analysis..."

**Solutions:**

1. **Ensure Good Lighting:**
   - CV requires clear visibility of the face
   - Use adequate front-facing light

2. **Face the Camera:**
   - MediaPipe needs to detect face landmarks
   - Look directly at camera for best results

3. **Check Console for Errors:**
   - Press F12 in browser
   - Look for JavaScript errors
   - Check terminal/Python console for CV errors

---

### Issue: Video Peer Connection Not Establishing

**Symptoms:**
- Both users in session but can't see each other
- "Waiting for peer to join" message persists

**Solutions:**

1. **Check Firewall:**
   - Allow Python through Windows Firewall
   - Allow port 5000 for incoming connections

2. **Same Network Test:**
   - Try both browsers on same computer first
   - Open incognito/private windows for doctor & patient

3. **STUN Server Issues:**
   - Default uses Google STUN servers
   - If blocked, edit `static/js/consultation.js`:
   ```javascript
   const configuration = {
       iceServers: [
           { urls: 'stun:stun.l.google.com:19302' },
           { urls: 'stun:stun1.l.google.com:19302' },
           { urls: 'stun:stun.stunprotocol.org:3478' }
       ]
   };
   ```

---

### Issue: Slow Performance / Lag

**Symptoms:**
- Video is choppy
- CV analysis delayed
- Transcription very slow

**Solutions:**

1. **Reduce Processing Frequency:**

   Edit `static/js/consultation.js`:
   ```javascript
   // Change from 2000ms to 5000ms
   videoFrameInterval = setInterval(() => {
       // ... frame capture code
   }, 5000);  // Process every 5 seconds instead of 2
   ```

2. **Close Other Applications:**
   - Free up CPU/RAM
   - Close unnecessary browser tabs

3. **Check System Requirements:**
   - Minimum: 4GB RAM, dual-core CPU
   - Recommended: 8GB RAM, quad-core CPU

---

### Issue: MediaPipe Warnings

**Warning Messages:**
```
W0000 00:00:... inference_feedback_manager.cc:114] Feedback manager requires...
```

**Solution:**
These are harmless warnings from MediaPipe. You can safely ignore them. They don't affect functionality.

---

### Issue: Python Version Mismatch

**Error:**
```
SyntaxError: ... (or other syntax errors)
```

**Solution:**
Ensure you're using Python 3.11 or higher:
```bash
python --version
# Should show: Python 3.11.x or higher

# If not, install Python 3.11+
# Then recreate virtual environment:
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

---

## 📞 Need More Help?

### Debugging Steps:

1. **Check Server Logs:**
   - Look at terminal where `python app.py` is running
   - Note any red error messages

2. **Check Browser Console:**
   - Press F12 in browser
   - Go to Console tab
   - Look for JavaScript errors

3. **Test Components Separately:**
   - Video calling: Works without CV/transcription
   - CV analysis: Should work even if transcription fails
   - Transcription: Requires model download

### Getting Support:

Include this information when seeking help:
- Operating system and version
- Python version (`python --version`)
- Error message (full text)
- What you were doing when error occurred
- Browser and version

---

## ✅ Success Checklist

Your application is working correctly if:
- [ ] Server starts without errors
- [ ] Homepage loads at http://localhost:5000
- [ ] Can create/join sessions as doctor/patient
- [ ] Video feeds appear for both users
- [ ] CV analysis panel updates (even if basic)
- [ ] No red errors in browser console
- [ ] (Optional) Transcription shows text or unavailable message

---

## 🚀 Quick Recovery Commands

If everything breaks, start fresh:

```bash
# Stop the server (Ctrl+C)

# Deactivate environment
deactivate

# Remove virtual environment
rm -rf venv  # Linux/Mac
rmdir /s venv  # Windows

# Recreate everything
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
pip install -r requirements.txt

# Run again
python app.py
```

This resets everything except your code and configurations.
