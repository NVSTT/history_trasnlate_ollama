import pathlib
import sys
import json
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from routes.translation import router as translation_router
from routes.indexing import router as indexing_router
from routes.questions import router as questions_router
from routes.search import router as search_router
from routes.documents import router as documents_router

# Указываем, что BASE_DIR - это директория, где лежит main.py
BASE_DIR = pathlib.Path(__file__).resolve().parent
sys.path.append(str(BASE_DIR))  # Добавляем путь для импорта модулей

STATIC_DIR = BASE_DIR / "static"
TEMPLATE_DIR = BASE_DIR / "templates"
BOT_CONFIG_PATH = BASE_DIR / "telegram_bot" 
INDEX_FILE = TEMPLATE_DIR / "index.html"
BOT_JSON_FILE = BOT_CONFIG_PATH / "bot_config.json"

app = FastAPI(title="Old Russian Texts API", redirect_slashes=False)

app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")
app.mount("/templates", StaticFiles(directory=str(TEMPLATE_DIR)), name="templates")

# Читаем WEB_APP_URL из bot_config.json
def get_web_app_url():
    try:
        with open(BOT_JSON_FILE, "r", encoding="utf-8") as f:
            config_data = json.load(f)
            return config_data.get("WEB_APP_URL", "*")
    except Exception as e:
        print(f"Ошибка чтения bot_config.json: {e}")
        return "*"

# CORS настройки
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        get_web_app_url(),
        "http://localhost:*",
        "https://*.ngrok.io"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключаем эндпоинты
app.include_router(translation_router, prefix="/api/translate", tags=["Translation"])
app.include_router(documents_router, prefix="/api/documents", tags=["Documents"])
app.include_router(search_router, prefix="/api/search", tags=["Search"])
app.include_router(questions_router, prefix="/api/questions", tags=["Questions"])
app.include_router(indexing_router, prefix="/api/index", tags=["Indexing"])

@app.get("/")
async def root():
    return FileResponse(INDEX_FILE)

@app.get("/health")
def health_check():
    return {"status": "ok", "version": "1.0.0"}

@app.on_event("startup")
async def startup_event():
    # Импортируем функцию из config.py
    from config import setup_ngrok
    setup_ngrok()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
