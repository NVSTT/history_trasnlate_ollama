from fastapi import APIRouter
from pydantic import BaseModel
import sqlite3
import json
import numpy as np
from sentence_transformers import SentenceTransformer
from database import DB_NAME  # файл с настройками БД

router = APIRouter()

class SemanticSearchRequest(BaseModel):
    query: str
    top_k: int = 5  # количество возвращаемых результатов

# Загружаем модель один раз при старте сервиса
model = SentenceTransformer('all-MiniLM-L6-v2')

def cosine_similarity(vec1, vec2):
    """Вычисляет косинусное сходство между двумя векторами."""
    return np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))

@router.post("/")
def semantic_search_documents(request: SemanticSearchRequest):
    try:
        # Получаем эмбеддинг запроса
        query_embedding = model.encode(request.query)
    except Exception as e:
        return {"detail": f"Ошибка при получении эмбеддинга запроса: {str(e)}"}

    # Подключаемся к базе данных
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # Извлекаем документы с их эмбеддингами
    cursor.execute("SELECT id, title, year, summary, embedding FROM texts")
    rows = cursor.fetchall()
    conn.close()

    results = []
    for row in rows:
        try:
            doc_id, title, year, summary, embedding_json = row
            if not embedding_json:
                continue

            # Преобразуем JSON-строку обратно в вектор
            doc_embedding = np.array(json.loads(embedding_json))
            norm_query = np.linalg.norm(query_embedding)
            norm_doc = np.linalg.norm(doc_embedding)
            if norm_query == 0 or norm_doc == 0:
                sim = 0.0
            else:
                sim = cosine_similarity(query_embedding, doc_embedding)

            results.append({
                "id": doc_id,
                "title": title,
                "year": year,
                "summary": summary,
                "similarity": sim
            })
        except Exception as ex:
            print(f"Ошибка обработки документа {doc_id}: {ex}")
            continue

    results = sorted(results, key=lambda x: x["similarity"], reverse=True)
    return {"results": results[:request.top_k]}
