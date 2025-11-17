# ИИ-агент для анализа резюме кандидатов
# Агент автоматически извлекает навыки, опыт и делает краткий HR-вывод по резюме.

# pip install openai

import openai

openai.api_key = "YOUR_OPENAI_API_KEY"

def resume_analysis_agent(resume_text, model="gpt-3.5-turbo"):
    system_msg = (
        "Ты HR-агент. Твоя задача — проанализировать резюме кандидата. "
        "Выдели ключевые навыки, опыт, уровень английского и дай краткий вывод. "
        "Верни JSON с ключами: {'skills': [...], 'experience': '...', 'english': '...', 'summary': '...'}"
    )
    response = openai.ChatCompletion.create(
        model=model,
        messages=[
            {"role": "system", "content": system_msg},
            {"role": "user", "content": resume_text}
        ]
    )
    return response.choices[0].message.content

if __name__ == "__main__":
    sample_resume = """
    Иван Иванов, Python-разработчик.
    Опыт: 5 лет. Django, FastAPI, PostgreSQL, Docker, AWS.
    Английский — Upper-Intermediate.
    Работал над highload-системами.
    """
    result = resume_analysis_agent(sample_resume)
    print("Результат анализа:\n", result)
