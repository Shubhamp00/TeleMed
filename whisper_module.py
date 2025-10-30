from faster_whisper import WhisperModel
import base64
import io
import wave
import numpy as np
import tempfile
import os

class WhisperTranscriber:
    def __init__(self, model_size="base"):
        print(f"Loading Faster Whisper model: {model_size}")
        try:
            self.model = WhisperModel(model_size, device="cpu", compute_type="int8")
            print("Faster Whisper model loaded successfully")
        except Exception as e:
            print(f"Error loading Whisper model: {e}")
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
        if self.model is None:
            return "Whisper model not available"
        
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
