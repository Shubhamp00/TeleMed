from faster_whisper import WhisperModel
import base64
import io
import wave
import numpy as np
import tempfile
import os
import sys

class WhisperTranscriber:
    def __init__(self, model_size="base"):
        print(f"Attempting to load Faster Whisper model: {model_size}")
        print("Note: First-time setup will download ~145MB model from HuggingFace")
        print("This may take a few minutes depending on your internet connection...")
        
        self.model = None
        self.model_available = False
        
        try:
            import socket
            original_timeout = socket.getdefaulttimeout()
            socket.setdefaulttimeout(60)
            
            self.model = WhisperModel(
                model_size, 
                device="cpu", 
                compute_type="int8",
                download_root=None,
                local_files_only=False
            )
            
            socket.setdefaulttimeout(original_timeout)
            
            self.model_available = True
            print("✓ Faster Whisper model loaded successfully!")
            
        except ConnectionError as e:
            print(f"\n⚠ Network Error: Unable to download Whisper model")
            print(f"   Reason: {str(e)[:100]}")
            print(f"\n   Transcription feature will be DISABLED.")
            print(f"   The app will continue to work without speech-to-text.\n")
            self.model = None
            
        except TimeoutError as e:
            print(f"\n⚠ Timeout Error: Model download took too long")
            print(f"   Your internet connection may be slow or blocked.")
            print(f"\n   Transcription feature will be DISABLED.")
            print(f"   The app will continue to work without speech-to-text.\n")
            self.model = None
            
        except Exception as e:
            error_msg = str(e)
            print(f"\n⚠ Error loading Whisper model: {error_msg[:200]}")
            
            if "timeout" in error_msg.lower() or "connection" in error_msg.lower():
                print(f"\n   SOLUTION:")
                print(f"   1. Check your internet connection")
                print(f"   2. Disable VPN/Proxy if enabled")
                print(f"   3. Check firewall settings")
                print(f"   4. Try again when you have stable internet\n")
            
            print(f"   Transcription feature will be DISABLED.")
            print(f"   The app will continue to work with CV analysis only.\n")
            self.model = None
    
    def decode_audio(self, audio_data):
        try:
            if ',' in audio_data:
                audio_data = audio_data.split(',')[1]
            
            audio_bytes = base64.b64decode(audio_data)
            
            return audio_bytes
        except Exception as e:
            print(f'Error decoding audio: {e}')
            return None
    
    def transcribe_audio(self, audio_data):
        if self.model is None or not self.model_available:
            return "[Transcription unavailable - Model not loaded]"
        
        try:
            audio_bytes = self.decode_audio(audio_data)
            
            if audio_bytes is None:
                return None
            
            with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as temp_audio:
                temp_audio.write(audio_bytes)
                temp_audio_path = temp_audio.name
            
            try:
                segments, info = self.model.transcribe(
                    temp_audio_path,
                    beam_size=5,
                    language="en",
                    condition_on_previous_text=False
                )
                
                transcription = ""
                for segment in segments:
                    transcription += segment.text + " "
                
                return transcription.strip()
            
            finally:
                if os.path.exists(temp_audio_path):
                    os.unlink(temp_audio_path)
        
        except Exception as e:
            print(f'Error transcribing audio: {e}')
            return None
    
    def extract_keywords(self, transcript):
        symptom_keywords = [
            'pain', 'ache', 'hurt', 'sore', 'fever', 'cough', 'headache',
            'nausea', 'dizzy', 'tired', 'weak', 'swelling', 'rash',
            'breathing', 'chest', 'stomach', 'back', 'joint', 'muscle'
        ]
        
        found_keywords = []
        transcript_lower = transcript.lower()
        
        for keyword in symptom_keywords:
            if keyword in transcript_lower:
                found_keywords.append(keyword)
        
        return found_keywords
    
    def generate_summary(self, transcripts):
        full_text = " ".join([t['text'] for t in transcripts])
        
        keywords = self.extract_keywords(full_text)
        
        summary = {
            'total_transcripts': len(transcripts),
            'total_words': len(full_text.split()),
            'detected_symptoms': keywords,
            'full_transcript': full_text[:500]
        }
        
        return summary
