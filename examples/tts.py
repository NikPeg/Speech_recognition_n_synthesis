# -*- coding: utf8 -*-
"""
Конвертация текст -> wav/ogg
"""
import os
import re
import subprocess
from datetime import datetime

import wave
from piper import PiperVoice


class TTS:
    """
    Класс для преобразования текста в аудио.
    Поддерживаются форматы аудио: wav, ogg
    """
    # default_init = {
    #     "sample_rate": 16000,
    #     "model_path": "tf/minazarko/TgBot/model4_2.onnx",  # путь к файлу TTS модели Silero
    # }

    default_init = {
        "sample_rate": 16000,
        "model_path": "/tf/minazarko/TgBot/tts/model4_2.onnx",  # путь к файлу TTS модели Silero
         # путь к ffmpeg
    }

    def __init__(
        self,
        sample_rate=None,
        model_path=None,
            ) -> None:
        """
        Настройка модели Silero для преобразования текста в аудио.

        :arg sample_rate: int       # 16000- качество звука
        :arg model_path: str        # путь до модели vits Piper onnx

        """
        self.sample_rate = sample_rate if sample_rate else TTS.default_init["sample_rate"]
        self.model_path = model_path if model_path else TTS.default_init["model_path"]
        self.voice = PiperVoice.load(self.model_path, use_cuda=True)




    def wav_to_ogg(
        self,
        in_filename: str,
        out_filename: str = None
                   ) -> str:
        """
        Конвертирует аудио в ogg формат.

        :arg in_filename:  str  # путь до входного файла
        :arg out_filename: str  # путь до выходного файла
        :return: str  # путь до выходного файла
        """
        if not in_filename:
            raise Exception("Укажите путь и имя файла in_filename")

        if out_filename is None:
            out_filename = "test_1.ogg"

        if os.path.exists(out_filename):
            os.remove(out_filename)

        command = [
            "ffmpeg",
            "-loglevel", "quiet",
            "-i", in_filename,
            "-acodec", "libvorbis",
            out_filename
        ]
        proc = subprocess.Popen(
            command,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
                                )
        proc.wait()
        return out_filename



    def _get_wav(self, text: str, ) -> str:
        """
        Конвертирует текст в wav файл

        :arg text:  str  # текст до 1000 символов
        :arg speaker_voice:  str  # голос диктора
        :arg sample_rate: str  # качество выходного аудио
        :return: str  # путь до выходного файла
        """
        if text is None:
            raise Exception("Передайте текст")

        # Удаляем существующий файл чтобы все хорошо работало
        if os.path.exists("test.wav"):
            os.remove("test.wav")



        # Сохранение результата в файл test.wav
        with wave.open("test.wav", "wb") as wav_file:
            self.voice.synthesize_wav(text, wav_file)



        return "test.wav"

    def _get_ogg(self, text: str) -> str:
        """
        Конвертирует текст в ogg файл

        :arg text:  str  # текст до 1000 символов
        :arg speaker_voice:  str  # голос диктора
        :arg sample_rate: str  # качество выходного аудио
        :return: str  # путь до выходного файла
        """
        # Конвертируем текст в wav, возвращаем путь до wav
        wav_audio_path = self._get_wav(text)

        # Конвертируем wav в ogg, возвращаем путь до ogg
        ogg_audio_path = self.wav_to_ogg(wav_audio_path)

        if os.path.exists(wav_audio_path):
            os.remove(wav_audio_path)
        print("STT:",text)
        return ogg_audio_path




if __name__ == "__main__":
    # Генерирование аудио из текста
    start_time = datetime.now()
    tts = TTS()
    print(_get_ogg("Привет,Хабр! Тэст 1 2 три четыре"))
    # print(tts.text_to_wav("Тэст! Как меня слышно? Пыш-пыш. Прием!", "test-2.wav"))
    print(_get_ogg("Слышу хорошо! Пыш-пыш."))
    print("Время выполнения:", datetime.now() - start_time)
