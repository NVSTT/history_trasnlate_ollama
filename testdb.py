import sqlite3
import json

def create_semantic_db():
    conn = sqlite3.connect("test_old_russian_texts.db")
    c = conn.cursor()

    # Создаем таблицу с дополнительным столбцом embedding
    c.execute('''
        CREATE TABLE IF NOT EXISTS texts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            year INTEGER,
            original_text TEXT,
            modern_translation TEXT,
            summary TEXT,
            keywords TEXT,
            embedding TEXT  -- хранение эмбеддинга в виде JSON строки
        )
    ''')

    # Пример тестовых данных (без эмбеддингов, их можно добавить позже)
    test_data = [
        (
            "Царский указ",
            1700,
            "Божиею милостьюю, мы, царь и великий князь ...",
            "По Божьей милости, мы, царь и великий князь ...",
            "Указ о введении нового летоисчисления в Русском царстве.",
            "указ, летоисчисление, Петр I",
            None
        ),
        (
            "Грамота боярина",
            1654,
            "Се бо аз, боярин Гаврила ...",
            "Вот я, боярин Гаврила ...",
            "Документ о пожаловании земель боярину Гавриле.",
            "грамота, боярин, пожалование земель",
            None
        ),
        (
            "Соборное уложение",
            1649,
            "В лето 1649 по указу государя ...",
            "В 1649 году по указу государя ...",
            "Свод законов, принятый при Алексее Михайловиче.",
            "законы, уложение, царь Алексей",
            None
        )
    ]

    c.executemany('''
        INSERT INTO texts (title, year, original_text, modern_translation, summary, keywords, embedding)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', test_data)

    conn.commit()
    conn.close()
    print("✅ База данных для семантического поиска создана!")

if __name__ == "__main__":
    create_semantic_db()
