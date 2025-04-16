from fastapi import APIRouter, HTTPException
from database import get_text_by_id
from services.text_processing import answer_question
from pydantic import BaseModel

router = APIRouter()

class QuestionRequest(BaseModel):
    text_id: int
    question: str

@router.post("/")
async def ask_question(request: QuestionRequest):
    """Ответ на вопрос по тексту"""
    text = get_text_by_id(request.text_id)
    if not text:
        raise HTTPException(status_code=404, detail="Документ не найден")

    context = {
        "original_text": text["original_text"],
        "modern_translation": text["modern_translation"],
        "summary": text["summary"],
        "keywords": text["keywords"]
    }

    try:
        answer = await answer_question(request.question, context)
        return {"answer": answer}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка обработки вопроса: {str(e)}")
