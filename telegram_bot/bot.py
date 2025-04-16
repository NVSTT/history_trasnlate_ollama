import os
import json
import logging
from dotenv import load_dotenv
from telegram import Update, WebAppInfo, KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Загружаем переменные окружения из .env
load_dotenv()

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Получаем токены из .env
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
WEB_APP_URL = os.getenv("NGROK_PUBLIC_URL")  # Используем актуальный ngrok URL

if not TOKEN or not WEB_APP_URL:
    logger.error("Ошибка: Не заданы TELEGRAM_BOT_TOKEN или NGROK_PUBLIC_URL в .env!")
    exit(1)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Отправляет кнопку для открытия Web App"""
    try:
        keyboard = [[KeyboardButton(text="🚀 Открыть Web App", web_app=WebAppInfo(url=WEB_APP_URL))]]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

        await update.message.reply_text(
            "Привет! Нажми на кнопку ниже, чтобы открыть Web App для обработки текстов:",
            reply_markup=reply_markup
        )
    except Exception as e:
        logger.error(f"Ошибка в команде /start: {e}")
        await update.message.reply_text("❌ Ошибка при запуске бота. Попробуйте позже.")

async def handle_web_app_data(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обрабатывает данные из Telegram Web App"""
    try:
        data = json.loads(update.message.web_app_data.data)
        logger.info(f"Получены данные из Web App: {data}")

        if data.get("action") == "text_processed":
            response = (
                f"✅ Текст успешно обработан!\n\n"
                f"📝 Оригинальный текст:\n{data.get('text', 'Нет данных')}\n\n"
                f"📝 Перевод:\n{data.get('translated', 'Нет данных')}\n\n"
                f"📋 Краткое содержание:\n{data.get('summary', 'Нет данных')}\n\n"
                f"🔑 Ключевые слова:\n{', '.join(data.get('keywords', []))}"
            )
            await update.message.reply_text(response)
        else:
            await update.message.reply_text("⚠️ Неизвестное действие из Web App.")
    except Exception as e:
        logger.error(f"Ошибка при обработке Web App данных: {e}")
        await update.message.reply_text("❌ Ошибка при обработке данных из Web App.")

def main() -> None:
    """Запуск Telegram бота"""
    try:
        app = Application.builder().token(TOKEN).build()

        app.add_handler(CommandHandler("start", start))
        app.add_handler(MessageHandler(filters.StatusUpdate.WEB_APP_DATA, handle_web_app_data))

        logger.info(f"✅ Бот запущен! Web App доступен по адресу: {WEB_APP_URL}")

        app.run_polling(allowed_updates=Update.ALL_TYPES)
    except Exception as e:
        logger.error(f"Ошибка при запуске бота: {e}")

if __name__ == "__main__":
    main()
