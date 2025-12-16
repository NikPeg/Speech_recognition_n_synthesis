# -*- coding: utf8 -*-
"""
Упрощенная STT через готовую модель или API.
Варианты для тех, кто не справился с ДЗ1, но хочет полноценного бота.
"""
import os
import subprocess
from datetime import datetime
from pathlib import Path

# Попробуем импортировать различные варианты STT
try:
    import whisper
    WHISPER_AVAILABLE = True
except ImportError:
    WHISPER_AVAILABLE = False

try:
    import speech_recognition as sr
    SPEECH_RECOGNITION_AVAILABLE = True
except ImportError:
    SPEECH_RECOGNITION_AVAILABLE = False


class STT_Simple:
    """
    Упрощенный класс для распознавания речи.
    Использует готовые модели/API вместо обучения своей.
    """
    
    def __init__(self, method="whisper", model_size="base"):
        """
        Инициализация STT.
        
        :param method: str - метод распознавания ("whisper" или "google")
        :param model_size: str - размер модели whisper ("tiny", "base", "small", "medium", "large")
        """
        self.method = method
        self.model_size = model_size
        self.model = None
        self.recognizer = None
        
        os.makedirs("Data", exist_ok=True)
        
        if method == "whisper":
            if not WHISPER_AVAILABLE:
                raise ImportError(
                    "Whisper не установлен. Установите: pip install openai-whisper"
                )
            print(f"Загрузка модели Whisper ({model_size})...")
            self.model = whisper.load_model(model_size)
            print("Модель Whisper загружена")
            
        elif method == "google":
            if not SPEECH_RECOGNITION_AVAILABLE:
                raise ImportError(
                    "SpeechRecognition не установлен. Установите: pip install SpeechRecognition"
                )
            self.recognizer = sr.Recognizer()
            print("Инициализирован Google Speech Recognition")
        else:
            raise ValueError(f"Неизвестный метод: {method}")

    def audio_to_text(self, audio_file_name=None) -> str:
        """
        Распознавание аудио в текст.
        
        :param audio_file_name: str - путь к аудио файлу
        :return: str - распознанный текст
        """
        if audio_file_name is None:
            raise Exception("Укажите путь и имя файла")
        if not os.path.exists(audio_file_name):
            raise Exception("Укажите правильный путь и имя файла")
        
        audio_file_name = str(audio_file_name)
        
        try:
            if self.method == "whisper":
                # Whisper работает с разными форматами напрямую
                result = self.model.transcribe(audio_file_name, language="ru")
                text = result["text"].strip()
                print(f"ASR (Whisper): {text}")
                return text
                
            elif self.method == "google":
                # Конвертируем в wav для Google Speech Recognition
                name_wav = f"Data/temp_{datetime.utcnow().timestamp()}.wav"
                subprocess.run([
                    'ffmpeg', '-i', audio_file_name,
                    '-acodec', 'pcm_s16le', '-ac', '1', '-ar', '16000',
                    name_wav
                ], check=True, capture_output=True)
                
                # Распознавание через Google
                with sr.AudioFile(name_wav) as source:
                    audio = self.recognizer.record(source)
                    text = self.recognizer.recognize_google(audio, language="ru-RU")
                
                os.remove(name_wav)
                print(f"ASR (Google): {text}")
                return text
                
        except Exception as e:
            print(f"Ошибка распознавания: {e}")
            return ""


if __name__ == "__main__":
    # Тестирование
    print("Тестирование упрощенной STT...")
    
    # Вариант 1: Whisper (рекомендуется)
    try:
        stt = STT_Simple(method="whisper", model_size="base")
        # Раскомментируйте для теста:
        # print(stt.audio_to_text("test-1.ogg"))
    except Exception as e:
        print(f"Whisper недоступен: {e}")
        print("Установите: pip install openai-whisper")
    
    # Вариант 2: Google Speech Recognition (требует интернет)
    try:
        stt = STT_Simple(method="google")
        # Раскомментируйте для теста:
        # print(stt.audio_to_text("test-1.ogg"))
    except Exception as e:
        print(f"Google Speech Recognition недоступен: {e}")
        print("Установите: pip install SpeechRecognition")

