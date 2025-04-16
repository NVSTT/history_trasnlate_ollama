from fastapi import APIRouter
from services.text_processing import process_text
from pydantic import BaseModel

router = APIRouter()

class TranslationRequest(BaseModel):
    text: str

@router.post("/")
async def translate_text(request: TranslationRequest):
    """Перевод дореформенного текста (не сохраняется в БД)."""
    return await process_text(request.text)
