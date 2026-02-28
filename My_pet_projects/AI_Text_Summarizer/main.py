# pip install openai

# Пример использования (CLI):
# python main.py --input text.txt

# v0.0.2 - добавляем автоматическое разбиение текста на чанки, суммаризацию каждого чанка и финальную «сумму суммаризаций»:
# - Разбиваем исходный текст на чанки по ~N токенов (приближённо — по символам),
# - Делаем краткое резюме каждого чанка,
# - Склеиваем все промежуточные резюме,
# - Делаем финальную суммаризацию.



import os
import argparse
from openai import OpenAI

# ≈ 4 символа ~= 1 токен (приближённо, но надёжно)
CHARS_PER_TOKEN = 4


def split_text(text: str, max_tokens: int) -> list[str]:
    max_chars = max_tokens * CHARS_PER_TOKEN
    return [
        text[i:i + max_chars]
        for i in range(0, len(text), max_chars)
    ]


def summarize_chunk(client: OpenAI, text: str, model: str) -> str:
    resp = client.responses.create(
        model=model,
        input=[
            {"role": "system", "content": "Ты — полезный и точный ассистент."},
            {"role": "user", "content": f"Кратко суммируй текст:\n\n{text}"}
        ],
        max_output_tokens=300
    )
    return resp.output_text.strip()


def summarize_file(
    input_path: str,
    model: str = "gpt-4.1-mini",
    chunk_tokens: int = 3000
) -> str:

    with open(input_path, "r", encoding="utf-8") as f:
        text = f.read()

    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    chunks = split_text(text, chunk_tokens)

    partial_summaries = []
    for i, chunk in enumerate(chunks, 1):
        print(f"🧩 Суммаризация чанка {i}/{len(chunks)}...")
        summary = summarize_chunk(client, chunk, model)
        partial_summaries.append(summary)

    combined_summary = "\n\n".join(partial_summaries)

    print("🧠 Финальная суммаризация...")
    final = client.responses.create(
        model=model,
        input=[
            {"role": "system", "content": "Ты — эксперт по аналитическому резюмированию."},
            {
                "role": "user",
                "content": (
                    "Сделай итоговое краткое и связное резюме "
                    "на основе следующих промежуточных суммаризаций:\n\n"
                    f"{combined_summary}"
                )
            }
        ],
        max_output_tokens=500
    )

    return final.output_text.strip()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, help="Путь к текстовому файлу")
    parser.add_argument(
        "--model",
        default="gpt-4.1-mini",
        help="Модель (gpt-4.1 или gpt-4.1-mini)"
    )
    parser.add_argument(
        "--chunk-tokens",
        type=int,
        default=3000,
        help="Размер чанка в токенах"
    )
    args = parser.parse_args()

    summary = summarize_file(
        args.input,
        model=args.model,
        chunk_tokens=args.chunk_tokens
    )

    print("\n📄 FINAL SUMMARY:\n")
    print(summary)