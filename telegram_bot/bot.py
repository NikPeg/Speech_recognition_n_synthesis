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
from aiogram import Bot, Dispatcher,  types
from aiogram import Bot, Dispatcher, F, types # импортируем классы из aiogram
from aiogram.types.input_file import InputFile
from dotenv import load_dotenv
from aiogram import  html
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.types import Message
from aiogram.enums.content_type import ContentType
from aiogram.types import FSInputFile
from stt import STT
from tts import TTS

# load_dotenv()



# bot = Bot(token=TELEGRAM_TOKEN)  # Объект бота
dp = Dispatcher()  # Диспетчер для бота
tts = TTS()
stt = STT()

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    filename="bot.log",
)


# Хэндлер на команду /start , /help
@dp.message(CommandStart())
async def cmd_start(message: types.Message):
    await message.reply(
        "Привет! Это Бот для конвертации голосового/аудио сообщения в текст"
        " и создания аудио из текста."
    )


# # Хэндлер на команду /test
# @dp.message_handler(commands="test")
# async def cmd_test(message: types.Message):
#     """
#     Обработчик команды /test
#     """
#     await message.answer("Test")


# Хэндлер на получение текста
@dp.message(F.text)
async def cmd_text(message: types.Message ,bot: Bot):
    """
    Обработчик на получение текста
    """
    await message.reply("Текст получен")

    out_filename = tts._get_ogg(message.text)

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

    os.remove(file_on_disk)  # Удаление временного файла

async def main() -> None:
    # Initialize Bot instance with default bot properties which will be passed to all API calls
    bot = Bot(token="TOKEN TELEGRAMM", default=DefaultBotProperties(parse_mode=ParseMode.HTML))

    # And the run events dispatching
    await dp.start_polling(bot)


if __name__ == "__main__":
    print("Запуск бота")
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
    