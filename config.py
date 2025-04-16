import os
import json
import logging
from dotenv import load_dotenv
from pyngrok import ngrok, conf
import pathlib
import sys

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


BASE_DIR = pathlib.Path(__file__).resolve().parent
sys.path.append(str(BASE_DIR)) 

# Путь к .env
ENV_FILE = BASE_DIR / ".env"

# Путь к bot_config.json (допустим, у вас папка telegram_bot/ лежит рядом с app/)
BOT_CONFIG_FILE = BASE_DIR / "telegram_bot" 
BOT_JSON_FILE = BOT_CONFIG_FILE / "bot_config.json"
# Загрузка переменных из .env
load_dotenv(dotenv_path=ENV_FILE)

# Теперь читаем переменные
DB_NAME = os.getenv("DB_NAME", "test_old_russian_texts.db")
API_HOST = os.getenv("API_HOST", "127.0.0.1")
API_PORT = int(os.getenv("API_PORT", 8000))
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
USE_NGROK = os.getenv("USE_NGROK", "False").lower() == "true"
NGROK_AUTH_TOKEN = os.getenv("NGROK_AUTH_TOKEN")

# Глобальная переменная для туннеля
NGROK_PUBLIC_URL = None

def setup_ngrok():
    global NGROK_PUBLIC_URL

    if not USE_NGROK:
        logger.info("Ngrok не используется.")
        return None

    try:
        if not NGROK_AUTH_TOKEN:
            raise ValueError("Ngrok auth token не найден. Укажите его в .env")

        conf.get_default().auth_token = NGROK_AUTH_TOKEN
        ngrok.kill()
        tunnel = ngrok.connect(API_PORT, bind_tls=True)
        NGROK_PUBLIC_URL = tunnel.public_url

        logger.info(f"🔗 Ngrok запущен: {NGROK_PUBLIC_URL}")

        # Обновляем .env
        update_env_file("NGROK_PUBLIC_URL", NGROK_PUBLIC_URL)

        # Обновляем конфиг бота
        update_bot_config(NGROK_PUBLIC_URL)

        return NGROK_PUBLIC_URL
    except Exception as e:
        logger.error(f"Ошибка при запуске ngrok: {e}")
        return None

def update_env_file(key, value):
    """
    Обновляет переменную в .env файле (ENV_FILE).
    """
    env_vars = {}

    # Считываем текущие переменные из ENV_FILE
    if ENV_FILE.exists():
        with ENV_FILE.open("r", encoding="utf-8") as f:
            for line in f:
                if "=" in line:
                    k, v = line.strip().split("=", 1)
                    env_vars[k] = v

    # Обновляем/добавляем ключ
    env_vars[key] = value

    # Записываем обратно
    with ENV_FILE.open("w", encoding="utf-8") as f:
        for k, v in env_vars.items():
            f.write(f"{k}={v}\n")

    logger.info(f"✅ Обновлена .env: {key}={value}")

def update_bot_config(web_app_url):
    """
    Обновляет telegram_bot/bot_config.json
    """
    try:
        config_data = {
            "TOKEN": TELEGRAM_BOT_TOKEN,
            "WEB_APP_URL": web_app_url
        }
        with BOT_JSON_FILE.open("w", encoding="utf-8") as f:
            json.dump(config_data, f, indent=4)

        logger.info("✅ Конфигурация бота обновлена.")
    except Exception as e:
        logger.error(f"Ошибка обновления конфигурации бота: {e}")

# Запускаем ngrok при импорте (по желанию)
setup_ngrok()
