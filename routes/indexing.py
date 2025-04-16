from fastapi import APIRouter, HTTPException
from services.text_processing import process_text
from database import add_document

from pydantic import BaseModel

router = APIRouter()


class IndexingRequest(BaseModel):
    title: str
    year: int
    text: str


@router.post("/")
async def index_document(request: IndexingRequest):
    """Добавление нового документа с автоматической индексацией"""
    try:
        processing_result = await process_text(request.text)

        add_document(
            title=request.title,
            year=request.year,
            original_text=request.text,
            modern_translation=processing_result["translation"],
            summary=processing_result["summary"],
            keywords=", ".join(processing_result["keywords"])
        )

        return {"message": "Документ успешно проиндексирован"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка индексации: {str(e)}")
