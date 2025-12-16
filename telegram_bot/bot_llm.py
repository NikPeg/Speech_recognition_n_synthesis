"""
Telegram бот для конвертации голосового/аудио сообщения в текст и
создания аудио из текста.
"""
import asyncio
import logging
import os
# from os import getenv
from pathlib import Path
import sys
from aiogram.filters import CommandStart, Command
from aiogram import Bot, Dispatcher, F, types , Router # импортируем классы из aiogram
from aiogram.types.input_file import InputFile
from dotenv import load_dotenv
from aiogram import  html
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from aiogram.types import Message
from aiogram.enums.content_type import ContentType
from aiogram.types import FSInputFile
from stt import STT
from tts import TTS
from llm import LLM
# load_dotenv()


# bot = Bot(token=TELEGRAM_TOKEN)  # Объект бота
dp = Dispatcher()  # Диспетчер для бота
tts = TTS()
stt = STT()
llm = LLM()
start_router = Router()
dp.include_router(start_router)

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    filename="bot.log",
)


# Хэндлер на команду /start , /help
@dp.message(CommandStart())
async def cmd_start(message: types.Message):
    await message.reply(
        "Привет! Это Бот для общения с LLM голосом и текстом"
        "Команда /new  - начинает новую беседу"
    )


# # Хэндлер на команду /new
# @start_router.message(Command('new'))
# async def cmd_start_2(message: Message):
#
#
#
#
#     """
#     Обработчик команды /new
#     """
#     llm.sbros()
#     await message.answer("Новая беседа")


# Хэндлер на получение текста
@dp.message(F.text)
async def cmd_text(message: types.Message ,bot: Bot):
    """
    Обработчик на получение текста
    """

    text=message.text
    if text=="/new":
        llm.sbros()
        await message.answer("Новая беседа")
    else:
        otvet=llm.generate(text)
        await message.reply(otvet)

        out_filename = tts._get_ogg(otvet)

        # Отправка голосового сообщения
        # path = Path("", out_filename)
        voice = FSInputFile(out_filename, filename=os.path.basename(out_filename))
        # voice = InputFile(path)
        await bot.send_voice(message.from_user.id, voice,
                             caption="Ответ от бота")

        # Удаление временного файла
        os.remove(out_filename)


# Хэндлер на получение голосового и аудио сообщения
@dp.message(F.voice)

async def voice_message_handler(message: types.Message, bot: Bot):
    """
    Обработчик на получение голосового и аудио сообщения.
    """
    if message.content_type == types.ContentType.VOICE:
        file_id = message.voice.file_id
    elif message.content_type == types.ContentType.AUDIO:
        file_id = message.audio.file_id
    elif message.content_type == types.ContentType.DOCUMENT:
        file_id = message.document.file_id
    else:
        await message.reply("Формат документа не поддерживается")
        return

    file = await bot.get_file(file_id)
    file_path = file.file_path
    file_on_disk = Path("./Data", f"{file_id}.ogg")
    await bot.download_file(file_path, destination=file_on_disk)
    await message.reply("Аудио получено")

    text = stt.audio_to_text(file_on_disk)
    if not text:
        text = "Формат документа не поддерживается"
    await message.answer(text)
    otvet=llm.generate(text)
    await message.reply(otvet)

    out_filename = tts._get_ogg(otvet)

    # Отправка голосового сообщения
    # path = Path("", out_filename)
    voice = FSInputFile(out_filename, filename=os.path.basename(out_filename))
    # voice = InputFile(path)
    await bot.send_voice(message.from_user.id, voice,
                         caption="Ответ от бота")

    # Удаление временного файла
    os.remove(out_filename)
    os.remove(file_on_disk)  # Удаление временного файла

async def main() -> None:
    # Initialize Bot instance with default bot properties which will be passed to all API calls
    bot = Bot(token="TOKEN_TELEGRAMM", default=DefaultBotProperties(parse_mode=ParseMode.HTML))

    # And the run events dispatching
    await dp.start_polling(bot)


if __name__ == "__main__":
    print("Запуск бота")
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
    