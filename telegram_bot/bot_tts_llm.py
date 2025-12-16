"""
Telegram бот для синтеза речи с поддержкой LLM.
Работает: текст -> LLM -> голосовое сообщение.
Для тех, кто выполнил ДЗ2 (TTS), но не справился с ДЗ1 (STT).
"""
import asyncio
import logging
import os
import sys
from pathlib import Path
from aiogram import Bot, Dispatcher, F, types
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.types import FSInputFile
from dotenv import load_dotenv
from tts import TTS
from llm import LLM

# Загрузка переменных окружения из .env файла
load_dotenv()

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("bot_tts_llm.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Инициализация диспетчера, TTS и LLM
dp = Dispatcher()
# Используем вашу обученную модель из ДЗ2
# Путь можно задать через переменную окружения TTS_MODEL_PATH
# или изменить в tts.py в default_init
tts = TTS()
llm = LLM()

logger.info("Инициализация TTS и LLM завершена")


@dp.message(CommandStart())
async def cmd_start(message: types.Message):
    """Обработчик команды /start"""
    await message.reply(
        "👋 Привет! Я бот для общения с LLM через голос.\n\n"
        "📝 Отправь мне текст, и я:\n"
        "1. Отправлю его в LLM\n"
        "2. Преобразую ответ в голосовое сообщение\n\n"
        "💡 Команды:\n"
        "/start - показать это сообщение\n"
        "/new - начать новую беседу (очистить историю)\n"
        "/help - справка"
    )


@dp.message(F.text & F.text.startswith("/help"))
async def cmd_help(message: types.Message):
    """Обработчик команды /help"""
    await message.reply(
        "📚 Справка:\n\n"
        "Отправь мне текст, и я:\n"
        "1. Отправлю его в LLM для генерации ответа\n"
        "2. Преобразую ответ LLM в голосовое сообщение\n\n"
        "Команды:\n"
        "/new - начать новую беседу (очистить историю диалога)\n\n"
        "⚠️ Ограничения:\n"
        "• Максимальная длина текста: ~1000 символов\n"
        "• История диалога: последние 10 сообщений"
    )


@dp.message(F.text & F.text.startswith("/new"))
async def cmd_new(message: types.Message):
    """Обработчик команды /new - очистка истории"""
    llm.sbros()
    await message.reply("🔄 История диалога очищена. Начинаем новую беседу!")


@dp.message(F.text)
async def cmd_text(message: types.Message, bot: Bot):
    """
    Обработчик текстовых сообщений.
    Отправляет текст в LLM и преобразует ответ в голосовое сообщение.
    """
    text = message.text.strip()
    
    # Пропускаем команды
    if text.startswith("/"):
        return
    
    # Проверка длины текста
    if len(text) > 1000:
        await message.reply(
            "⚠️ Текст слишком длинный (максимум 1000 символов).\n"
            f"Ваш текст: {len(text)} символов."
        )
        return
    
    if not text:
        await message.reply("❌ Пустое сообщение. Отправь текст для обработки.")
        return
    
    try:
        # Показываем, что обрабатываем
        status_msg = await message.reply("🔄 Обрабатываю запрос...")
        
        # Генерируем ответ через LLM
        logger.info(f"Отправка в LLM: {text[:50]}...")
        otvet = llm.generate(text)
        
        # Отправляем текстовый ответ
        await message.reply(f"💬 Ответ LLM:\n{otvet}")
        
        # Генерируем голосовое сообщение
        logger.info(f"Генерация аудио для ответа: {otvet[:50]}...")
        out_filename = tts._get_ogg(otvet)
        
        # Отправка голосового сообщения
        voice = FSInputFile(out_filename, filename=os.path.basename(out_filename))
        await bot.send_voice(
            message.chat.id,
            voice,
            caption="📢 Голосовой ответ от бота"
        )
        
        # Удаление временного файла
        os.remove(out_filename)
        
        # Удаляем статусное сообщение
        await status_msg.delete()
        
        logger.info("Ответ успешно отправлен")
        
    except Exception as e:
        logger.error(f"Ошибка при обработке текста: {e}", exc_info=True)
        await message.reply(
            f"❌ Произошла ошибка:\n{str(e)}"
        )


async def main() -> None:
    """Главная функция запуска бота"""
    # ВАЖНО: Замените "YOUR_TELEGRAM_BOT_TOKEN" на ваш токен от @BotFather
    TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "YOUR_TELEGRAM_BOT_TOKEN")
    
    if TELEGRAM_TOKEN == "YOUR_TELEGRAM_BOT_TOKEN":
        logger.error(
            "⚠️ Не установлен TELEGRAM_TOKEN!\n"
            "Установите переменную окружения:\n"
            "export TELEGRAM_TOKEN='ваш_токен'\n"
            "Или создайте файл .env с содержимым: TELEGRAM_TOKEN=ваш_токен"
        )
        return
    
    # Инициализация бота
    bot = Bot(
        token=TELEGRAM_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    
    logger.info("Бот запущен и готов к работе!")
    
    # Запуск polling
    await dp.start_polling(bot)


if __name__ == "__main__":
    print("🚀 Запуск бота для общения с LLM через голос...")
    print("📝 Бот работает: текст -> LLM -> голос")
    print("=" * 50)
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Бот остановлен пользователем")
    except Exception as e:
        logger.error(f"Критическая ошибка: {e}", exc_info=True)

