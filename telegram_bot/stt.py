# -*- coding: utf8 -*-
"""
Конвертация wav/ogg -> текст
"""
import json
import os
import subprocess
from datetime import datetime

import nemo.collections.asr as nemo_asr
import os
os.makedirs("Data", exist_ok=True)
class STT:
    """
    Класс для распознования аудио через nemo и преобразования его в текст.
    Поддерживаются форматы аудио: wav, ogg
    """
    default_init = {
        "model_path": "/tf/experiments1/FastConformer-Hybrid-TDT-CTC-BPE.nemo",  # путь к папке с файлами STT модели nemo
        "sample_rate": "16000"}



    def __init__(self,
                 model_path=None,
                 sample_rate=None
                                 ) -> None:
        """
        Настройка модели nemo для распознования аудио и
        преобразования его в текст.

        :arg model_path:  str  путь до модели nemo
        :arg sample_rate: int  частота выборки, обычно 16000

        """
        self.model_path = model_path if model_path else STT.default_init["model_path"]
        self.sample_rate = sample_rate if sample_rate else STT.default_init["sample_rate"]
        self.asr_model = nemo_asr.models.EncDecHybridRNNTCTCBPEModel.restore_from(self.model_path)
        #
        # self._check_model()
        #
        # model = Model(self.model_path)
        # self.recognizer = KaldiRecognizer(model, self.sample_rate)
        # self.recognizer.SetWords(True)

    # def _check_model(self):
    #     """
    #     Проверка наличия модели Vosk на нужном языке в каталоге приложения
    #     """
    #     if not os.path.exists(self.model_path):
    #         raise Exception(
    #             "Vosk: сохраните папку model в папку vosk\n"
    #             "Скачайте модель по ссылке https://alphacephei.com/vosk/models"
    #                         )
    #
    #     isffmpeg_here = False
    #     for file in os.listdir(self.ffmpeg_path):
    #         if file.startswith('ffmpeg'):
    #             isffmpeg_here = True
    #
    #     if not isffmpeg_here:
    #         raise Exception(
    #             "Ffmpeg: сохраните ffmpeg.exe в папку ffmpeg\n"
    #             "Скачайте ffmpeg.exe по ссылке https://ffmpeg.org/download.html"
    #                         )
    #     self.ffmpeg_path = self.ffmpeg_path + '/ffmpeg'

    def audio_to_text(self, audio_file_name=None) -> str:
        """
        Offline-распознавание аудио в текст через Vosk
        :param audio_file_name: str путь и имя аудио файла
        :return: str распознанный текст
        """
        if audio_file_name is None:
            raise Exception("Укажите путь и имя файла")
        if not os.path.exists(audio_file_name):
            raise Exception("Укажите правильный путь и имя файла")
        audio_file_name=str(audio_file_name)
        kas=audio_file_name.rfind('.')
        rash=audio_file_name[kas:]
        # Конвертация аудио в wav и результат в process.stdout
        name_wav="Data/A"+str(datetime.utcnow())+'.wav'
        if rash in ['.wav','.oga','.mp3','.aac','.flac','.ogg']:
            process = subprocess.run(['ffmpeg', '-i', audio_file_name,'-acodec','pcm_s16le','-ac','1', '-ar',self.sample_rate,name_wav])
            if process.returncode != 0:
                print("fail bitii  no convert ffmpg)))))))))))))))))))))))")


        # Возвращаем распознанный текст в виде str
        output = self.asr_model.transcribe([name_wav])
        result_dict = output[0].text.replace(" ⁇ ","ё")
        print("ASR:",result_dict)
        return result_dict               # текст в виде str


if __name__ == "__main__":
    # Распознование аудио
    start_time = datetime.now()
    stt = STT()
    print(stt.audio_to_text("test-1.ogg"))
    print("Время выполнения:", datetime.now() - start_time)
    