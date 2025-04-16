import sqlite3
import json
from sentence_transformers import SentenceTransformer

# Загружаем модель
model = SentenceTransformer('all-MiniLM-L6-v2')

def update_embeddings():
    conn = sqlite3.connect("test_old_russian_texts.db")
    c = conn.cursor()
    
    # Выбираем все записи, для которых еще не заполнено поле embedding
    c.execute("SELECT id, modern_translation FROM texts WHERE embedding IS NULL")
    rows = c.fetchall()
    
    for row in rows:
        doc_id, text = row
        # Получаем эмбеддинг для оригинального текста (можно комбинировать несколько полей)
        embedding = model.encode(text)
        # Преобразуем в список и затем в JSON-строку
        embedding_json = json.dumps(embedding.tolist())
        # Обновляем запись
        c.execute("UPDATE texts SET embedding = ? WHERE id = ?", (embedding_json, doc_id))
    
    conn.commit()
    conn.close()
    print("✅ Эмбеддинги обновлены!")

if __name__ == "__main__":
    update_embeddings()
