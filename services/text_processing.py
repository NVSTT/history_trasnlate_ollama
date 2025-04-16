from typing import Dict
import ollama
import asyncio

OLLAMA_MODEL = "phi4:latest"

async def process_text(text):
    """Обрабатываем текст: перевод, суммаризация, ключевые слова"""
    translation = await translate(text)
    summary, keywords = await asyncio.gather(
        summarize(translation),
        extract_keywords(translation)
    )
    return {
        "translation": translation,
        "summary": summary,
        "keywords": keywords
    }

async def translate(text):
    """Перевод текста"""
    system_prompt = "Ты - русскоязычный эксперт по старорусским текстам. Отвечай только на русском языке."
    prompt = f"""
            Задача: переведи старорусский текст на современный русский язык.
            Важно: 
            1. Сохрани смысл и стиль оригинала
            2. Используй современные слова и обороты речи
            3. Ответ должен быть только на русском языке

            Текст для перевода: {text}
            """
    response = ollama.generate(
        model=OLLAMA_MODEL,
        prompt=system_prompt + "\n" + prompt
    )
    return response["response"]

async def summarize(text):
    """Краткое содержание"""
    system_prompt = "Ты - русскоязычный эксперт по анализу текстов. Отвечай ТОЛЬКО на русском языке. Никакого английского в ответах."
    prompt = f"""
            Задача: создай краткое содержание текста на русском языке.
            Требования:
            1. Напиши 3-4 содержательных предложения
            2. Выдели главные мысли и ключевые события
            3. Используй только русский язык
            4. Сохрани главный смысл текста

            Текст для анализа: {text}
            """
    response = ollama.generate(
        model=OLLAMA_MODEL,
        prompt=system_prompt + "\n" + prompt
    )
    return response["response"]

async def extract_keywords(text):
    """Ключевые слова"""
    system_prompt = "Ты - русскоязычный эксперт по анализу текстов. Отвечай только на русском языке."
    prompt = f"""
            Задача: выдели ключевые слова из текста.
            Требования:
            1. Выдели 5-7 важных слов или словосочетаний
            2. Используй только русские слова
            3. Перечисли слова через запятую
            4. Обрати особое внимание на исторические термины

            Текст для анализа: {text}
            """
    response = ollama.generate(
        model=OLLAMA_MODEL,
        prompt=system_prompt + "\n" + prompt
    )
    return response["response"].split(', ')

async def answer_question(question: str, context: Dict, model=OLLAMA_MODEL) -> str:
    system_prompt = """Ты - русскоязычный эксперт по анализу исторических текстов. 
    У тебя есть контекст документа, включающий оригинальный текст, современный перевод, 
    краткое содержание и ключевые слова. Используй эту информацию для ответа на вопросы."""

    context_str = f"""
    Оригинальный текст: {context['original_text']}
    Современный перевод: {context['translation']}
    Краткое содержание: {context['summary']}
    Ключевые слова: {context['keywords']}
    """

    prompt = f"""
    Контекст документа:
    {context_str}

    Вопрос: {question}

    Пожалуйста, ответь на вопрос, используя информацию из контекста. 
    Если информации недостаточно, укажи это. Отвечай только на русском языке.
    """
    response = ollama.generate(
        model=model,
        prompt=system_prompt + "\n" + prompt
    )
    return response["response"]
