# pip install openai

# Требуется переменная окружения OPENAI_API_KEY. Добавь ключ в окружение: export OPENAI_API_KEY="твой_ключ"

# Пример использования (CLI):
# python main.py --input text.txt


import os
import argparse

from openai import OpenAI  # современный клиент

def summarize_file(input_path: str, model: str = "gpt-4.1") -> str:
    """
    Считывает текст из файла и делает запрос к OpenAI API для суммаризации.

    :param input_path: путь к файлу
    :param model: модель OpenAI для суммаризации
    :returns: итоговое краткое содержание
    """
    # читаем весь текст
    with open(input_path, "r", encoding="utf-8") as f:
        text = f.read()

    # создаём клиент
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    # формируем вход для модели
    prompt = (
        "Сократи и обобщи следующий текст:\n\n"
        f"{text}"
    )

    # делаем вызов API через responses.create
    resp = client.responses.create(
        model=model,
        input=[
            {"role": "system", "content": "Ты — полезный помощник."},
            {"role": "user", "content": prompt},
        ],
        max_output_tokens=1024  # можно настроить
    )

    # получаем основной текст из ответа
    # .output_text автоматически объединяет части текста
    return resp.output_text.strip()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, help="Путь к текстовому файлу")
    parser.add_argument(
        "--model",
        default="gpt-4.1",
        help="Модель OpenAI (например, gpt-4.1 или gpt-4.1-mini)"
    )
    args = parser.parse_args()

    summary = summarize_file(args.input, args.model)
    print("📄 Summary:\n", summary)