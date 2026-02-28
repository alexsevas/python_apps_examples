# Cкрипт, который принимает текстовый файл, отправляет его в OpenAI API и возвращает краткое резюме
# - Требуется переменная окружения OPENAI_API_KEY
# - Позволяет быстро получать краткое резюме больших текстов
#
# pip install openai
#
# Пример использования (CLI):
# python summarize.py --input article.txt --model gpt-3.5-turbo


import os
import openai
import argparse

def summarize_file(input_path, model="gpt-3.5-turbo"):
    with open(input_path, 'r', encoding='utf-8') as f:
        text = f.read()
    openai.api_key = os.getenv("OPENAI_API_KEY")
    resp = openai.ChatCompletion.create(
        model=model,
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": f"Summarize this text:\n\n{text}"}
        ]
    )
    return resp.choices[0].message.content.strip()

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--input", required=True, help="Путь к текстовому файлу")
    p.add_argument("--model", default="gpt-3.5-turbo", help="Модель OpenAI")
    args = p.parse_args()
    summary = summarize_file(args.input, args.model)
    print("📄 Summary:\n", summary)