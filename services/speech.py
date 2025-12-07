"""
Сервис распознавания речи через OpenAI Whisper API.
"""

import os
from openai import OpenAI
from config.settings import OPENAI_API_KEY

# Инициализация клиента
client = OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None


def transcribe_voice(file_path: str) -> str:
    """
    Распознаёт речь из аудиофайла.
    
    Args:
        file_path: Путь к аудиофайлу (.ogg, .mp3, .wav, .m4a)
    
    Returns:
        Распознанный текст
    """
    if not client:
        return None
    
    if not os.path.exists(file_path):
        print(f"[SPEECH] File not found: {file_path}")
        return None
    
    try:
        with open(file_path, "rb") as audio_file:
            transcript = client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
                language="ru"  # Русский язык
            )
        
        text = transcript.text.strip()
        print(f"[SPEECH] Transcribed: {text}")
        return text
        
    except Exception as e:
        print(f"[SPEECH] Error: {e}")
        return None
    
    finally:
        # Удаляем временный файл
        try:
            os.remove(file_path)
        except:
            pass
