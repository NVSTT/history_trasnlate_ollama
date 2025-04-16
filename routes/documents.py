# from fastapi import APIRouter, HTTPException, Query
# from database import get_all_documents, get_text_by_id
#
# router = APIRouter()
#
#
# @router.get("/")
# async def get_documents(
#         year: int = Query(None, description="Фильтр по году"),
#         title: str = Query(None, description="Фильтр по названию"),
#         limit: int = Query(10, description="Сколько документов показать (по умолчанию 10)")
# ):
#     """Получение списка документов с фильтрацией"""
#     try:
#         documents = get_all_documents(year=year, title=title, limit=limit)
#
#         if not documents:
#             return {"results": [], "message": "Документы не найдены"}
#
#         return {"results": documents}
#
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Ошибка загрузки документов: {str(e)}")
#
# @router.get("/{doc_id}")
# async def get_document(doc_id: int):
#     """Получение информации о конкретном документе"""
#     document = get_text_by_id(doc_id)
#     if not document:
#         raise HTTPException(status_code=404, detail="Документ не найден")
#
#     return {
#         "id": document["id"],
#         "title": document["title"],
#         "year": document["year"],
#         "original_text": document["original_text"],
#         "modern_translation": document["modern_translation"],
#         "summary": document["summary"],
#         "keywords": document["keywords"]
#     }

from fastapi import APIRouter, Query, HTTPException
from database import get_all_documents, get_text_by_id

router = APIRouter()


@router.get("/")
async def get_documents(
    year: int = Query(None, description="Фильтр по году"),
    title: str = Query(None, description="Фильтр по названию"),
    limit: int = Query(10, description="Сколько документов показать (по умолчанию 10)")
):
    """Получение списка документов с фильтрацией"""
    try:
        documents = get_all_documents(year=year, title=title, limit=limit)
        return {"results": [
            {**doc, "preview": doc['summary'][:100] + "..."} for doc in documents
        ]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка загрузки документов: {str(e)}")

@router.get("/{doc_id}")
async def get_document_info(doc_id: int):
    """Получение конкретного документа по ID"""
    document = get_text_by_id(doc_id)
    if not document:
        raise HTTPException(status_code=404, detail="Документ не найден")
    return document
