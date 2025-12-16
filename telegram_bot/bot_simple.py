"""
Упрощенный Telegram бот для синтеза речи (TTS).
Работает только с текстом -> голосовое сообщение.
Для тех, кто выполнил ДЗ2, но не справился с ДЗ1.
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

# Загрузка переменных окружения из .env файла
load_dotenv()

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("bot_simple.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Инициализация диспетчера и TTS
dp = Dispatcher()
# Используем вашу обученную модель из ДЗ2
# Путь можно задать через переменную окружения TTS_MODEL_PATH
# или изменить в tts.py в default_init
tts = TTS()

logger.info("Инициализация TTS завершена")


@dp.message(CommandStart())
async def cmd_start(message: types.Message):
    """Обработчик команды /start"""
    await message.reply(
        "👋 Привет! Я упрощенный бот для синтеза речи.\n\n"
        "📝 Отправь мне текст, и я преобразую его в голосовое сообщение.\n\n"
        "💡 Команды:\n"
        "/start - показать это сообщение\n"
        "/help - справка"
    )


@dp.message(F.text & F.text.startswith("/help"))
async def cmd_help(message: types.Message):
    """Обработчик команды /help"""
    await message.reply(
        "📚 Справка:\n\n"
        "Просто отправь мне любой текст, и я преобразую его в голосовое сообщение.\n\n"
        "Примеры использования:\n"
        "• Напиши: 'Привет, как дела?'\n"
        "• Я отвечу голосовым сообщением\n\n"
        "⚠️ Ограничения:\n"
        "• Максимальная длина текста: ~1000 символов\n"
        "• Поддерживается только русский язык"
    )


@dp.message(F.text)
async def cmd_text(message: types.Message, bot: Bot):
    """
    Обработчик текстовых сообщений.
    Преобразует текст в голосовое сообщение.
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
        await message.reply("❌ Пустое сообщение. Отправь текст для преобразования.")
        return
    
    try:
        # Показываем, что обрабатываем
        status_msg = await message.reply("🔄 Обрабатываю текст...")
        
        # Генерируем голосовое сообщение
        logger.info(f"Генерация аудио для текста: {text[:50]}...")
        out_filename = tts._get_ogg(text)
        
        # Отправка голосового сообщения
        voice = FSInputFile(out_filename, filename=os.path.basename(out_filename))
        await bot.send_voice(
            message.chat.id,
            voice,
            caption=f"📢 Ваш текст: {text[:100]}{'...' if len(text) > 100 else ''}"
        )
        
        # Удаление временного файла
        os.remove(out_filename)
        
        # Удаляем статусное сообщение
        await status_msg.delete()
        
        logger.info("Аудио успешно отправлено")
        
    except Exception as e:
        logger.error(f"Ошибка при обработке текста: {e}", exc_info=True)
        await message.reply(
            f"❌ Произошла ошибка при генерации аудио:\n{str(e)}"
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
    print("🚀 Запуск упрощенного бота для синтеза речи...")
    print("📝 Бот работает только с текстом -> голос")
    print("=" * 50)
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Бот остановлен пользователем")
    except Exception as e:
        logger.error(f"Критическая ошибка: {e}", exc_info=True)

