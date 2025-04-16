import sqlite3

DB_NAME = "test_old_russian_texts.db"

#
# def init_db():
#     conn = sqlite3.connect(DB_NAME)
#     cursor = conn.cursor()
#
#     # Основная таблица документов
#     cursor.execute('''
#         CREATE TABLE IF NOT EXISTS texts (
#             id INTEGER PRIMARY KEY AUTOINCREMENT,
#             title TEXT,
#             year INTEGER,
#             original_text TEXT,
#             modern_translation TEXT,
#             summary TEXT,
#             keywords TEXT
#         )
#     ''')
#
#     # Полнотекстовый поиск
#     cursor.execute('''
#         CREATE VIRTUAL TABLE IF NOT EXISTS documents_fts
#         USING fts5(original_text, modern_translation, summary, keywords);
#     ''')
#
#     conn.commit()
#     conn.close()
#
#
# def add_document(title, year, original_text, modern_translation, summary, keywords):
#     conn = sqlite3.connect(DB_NAME)
#     cursor = conn.cursor()
#     cursor.execute('''
#         INSERT INTO texts (title, year, original_text, modern_translation, summary, keywords)
#         VALUES (?, ?, ?, ?, ?, ?)
#     ''', (title, year, original_text, modern_translation, summary, keywords))
#
#     # Добавляем в FTS5
#     cursor.execute('''
#         INSERT INTO documents_fts (rowid, original_text, modern_translation, summary, keywords)
#         VALUES (last_insert_rowid(), ?, ?, ?, ?)
#     ''', (original_text, modern_translation, summary, keywords))
#
#     conn.commit()
#     conn.close()
#
#
# def get_all_documents(year=None, title=None, limit=10):
#     """Получение списка документов с фильтрацией"""
#     conn = sqlite3.connect(DB_NAME)
#     cursor = conn.cursor()
#
#     query = "SELECT id, title, year, summary FROM texts WHERE 1=1"
#     params = []
#
#     if year:
#         query += " AND year = ?"
#         params.append(year)
#
#     if title:
#         query += " AND title LIKE ?"
#         params.append(f"%{title}%")
#
#     query += " ORDER BY year DESC LIMIT ?"
#     params.append(limit)
#
#     cursor.execute(query, params)
#     results = cursor.fetchall()
#     conn.close()
#
#     return [
#         {"id": row[0], "title": row[1], "year": row[2], "summary": row[3]} for row in results
#     ]
#
#
# def get_text_by_id(doc_id):
#     """Получение конкретного документа по ID"""
#     conn = sqlite3.connect(DB_NAME)
#     cursor = conn.cursor()
#
#     cursor.execute("SELECT * FROM texts WHERE id = ?", (doc_id,))
#     row = cursor.fetchone()
#
#     conn.close()
#     if row:
#         return {
#             "id": row[0],
#             "title": row[1],
#             "year": row[2],
#             "original_text": row[3],
#             "modern_translation": row[4],
#             "summary": row[5],
#             "keywords": row[6]
#         }
#     return None

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # Создаем основную таблицу
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS texts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            year INTEGER,
            original_text TEXT,
            modern_translation TEXT,
            summary TEXT,
            keywords TEXT
        )
    ''')

    # Создаем полнотекстовый индекс, привязанный к таблице texts
    cursor.execute('''
        CREATE VIRTUAL TABLE IF NOT EXISTS texts_fts
        USING fts5(original_text, modern_translation, summary, keywords, content='texts', content_rowid='id');
    ''')

    conn.commit()
    conn.close()

def add_document(title, year, original_text, modern_translation, summary, keywords):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # Вставка в основную таблицу
    cursor.execute('''
        INSERT INTO texts (title, year, original_text, modern_translation, summary, keywords)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (title, year, original_text, modern_translation, summary, keywords))

    # Получаем ID только что вставленного документа
    doc_id = cursor.lastrowid

    # Вставляем в FTS индекс
    cursor.execute('''
        INSERT INTO texts_fts (rowid, original_text, modern_translation, summary, keywords)
        VALUES (?, ?, ?, ?, ?)
    ''', (doc_id, original_text, modern_translation, summary, keywords))

    conn.commit()
    conn.close()

def get_all_documents(year=None, title=None, limit=10):
    """Получение списка документов с фильтрацией"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    query = "SELECT id, title, year, summary FROM texts WHERE 1=1"
    params = []

    if year:
        query += " AND year = ?"
        params.append(year)

    if title:
        query += " AND title LIKE ?"
        params.append(f"%{title}%")

    query += " ORDER BY year DESC LIMIT ?"
    params.append(limit)

    cursor.execute(query, params)
    results = cursor.fetchall()
    conn.close()

    return [
        {"id": row[0], "title": row[1], "year": row[2], "summary": row[3]} for row in results
    ]

def get_text_by_id(doc_id):
    """Получение конкретного документа по ID"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM texts WHERE id = ?", (doc_id,))
    row = cursor.fetchone()

    conn.close()
    if row:
        return {
            "id": row[0],
            "title": row[1],
            "year": row[2],
            "original_text": row[3],
            "modern_translation": row[4],
            "summary": row[5],
            "keywords": row[6]
        }
    return None

