import os
import requests
from config import OPENROUTER_API_KEY

class VoiceHelper:
    """Handle voice message transcription using OpenAI Whisper via OpenRouter"""
    
    def __init__(self):
        self.api_key = OPENROUTER_API_KEY
        # Note: OpenRouter may not support Whisper directly
        # Alternative: Use OpenAI API directly for Whisper
        self.whisper_available = False
        
    def transcribe_voice(self, file_path):
        """
        Transcribe voice message to text
        
        Args:
            file_path (str): Path to audio file
            
        Returns:
            str: Transcribed text or error message
        """
        try:
            # For now, we'll use a placeholder
            # In production, you would:
            # 1. Use OpenAI Whisper API directly
            # 2. Or use a local Whisper model
            # 3. Or use Google Speech-to-Text
            
            # Placeholder implementation
            return self._transcribe_with_openai_fallback(file_path)
            
        except Exception as e:
            print(f"Error transcribing voice: {e}")
            return None
    
    def _transcribe_with_openai_fallback(self, file_path):
        """
        Fallback: Use OpenAI Whisper API directly
        Note: This requires OPENAI_API_KEY in .env
        """
        try:
            # Check if OpenAI API key is available
            openai_key = os.getenv('OPENAI_API_KEY')
            
            if not openai_key:
                return "⚠️ Voice transcription requires OpenAI API key. Please add OPENAI_API_KEY to .env file."
            
            import openai
            openai.api_key = openai_key
            
            with open(file_path, 'rb') as audio_file:
                transcript = openai.Audio.transcribe("whisper-1", audio_file)
                return transcript['text']
                
        except Exception as e:
            print(f"OpenAI Whisper error: {e}")
            return "⚠️ Voice transcription is currently unavailable. Please type your task."
    
    def convert_ogg_to_wav(self, ogg_path):
        """Convert Telegram OGG format to WAV for better compatibility"""
        try:
            from pydub import AudioSegment
            
            wav_path = ogg_path.replace('.ogg', '.wav')
            audio = AudioSegment.from_ogg(ogg_path)
            audio.export(wav_path, format='wav')
            
            return wav_path
        except Exception as e:
            print(f"Error converting audio: {e}")
            return ogg_path
