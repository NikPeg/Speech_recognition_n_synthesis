# -*- coding: utf8 -*-
"""
Ответы на вопросы с помощью LLM
"""
# import os
# import re
# import subprocess
# from datetime import datetime
#
# import wave
# from piper import PiperVoice
from transformers import pipeline

class LLM:
    """
    Класс для LLM
    """
    default_init = {

        "model_path": "MTSAIR/Cotype-Nano",  # путь к LLM

    }

    def __init__(
        self,

        model_path=None,
            ) -> None:


        self.model_path = model_path if model_path else LLM.default_init["model_path"]
        self.pipe = pipeline("text-generation", model=self.model_path , device="cuda")
        self.promt= {"role": "system", "content": "Ты — ИИ-помощник. Тебе дано задание: необходимо сгенерировать точный краткий лаконичный ответ, длиною меньше 30 слов ."}
        self.history=[]



    def generate(
        self,
        zapros: str,

                   ) -> str:
        """
        Генерирует ответ LLM.

        :arg zapros:  str  # запрос пользователя

        :return: str  # ответ LLM
        """
        if zapros=="":
            return "Что, что ? Не раслышал"


        self.history.append({"role": "user", "content": zapros})
        messages = [self.promt]
        messages.extend(self.history)
        res = self.pipe(messages, max_length=500)
        otvet=res[0]['generated_text'][-1]['content']
        self.history.append({"role": "asistent", "content": otvet})
        if len(self.history)>10: #Храним 10 последних сообщений
            self.history=self.history[-10:]
        print("LLM: ", otvet)
        return otvet
    def sbros(self):
        self.history=[]
        