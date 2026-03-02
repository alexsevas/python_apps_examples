# pip install openai pypdf python-docx

# summarize big_report.pdf -v
# summarize contract.docx --mode executive -o exec.txt
# summarize book.txt --mode outline --chunk-tokens 2000

# v0.0.4:
# - Progress bar - tqdm, показывает реальный прогресс по чанкам
# - Auto language - определяем язык через LLM один раз, до суммаризации
# - Режимы вывода - управляются prompt-шаблонами, не хардкодом
# - Production-CLI - флаги, предсказуемое поведение, расширяемость



#!/usr/bin/env python3
import os
import sys
import argparse
from pathlib import Path

from openai import OpenAI
from pypdf import PdfReader
from docx import Document
from tqdm import tqdm

CHARS_PER_TOKEN = 4


# ================= FILE LOADERS =================

def load_txt(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def load_pdf(path: Path) -> str:
    reader = PdfReader(path)
    pages = []
    for page in reader.pages:
        text = page.extract_text()
        if text:
            pages.append(text)
    return "\n\n".join(pages)


def load_docx(path: Path) -> str:
    doc = Document(path)
    return "\n".join(p.text for p in doc.paragraphs if p.text.strip())


def load_text(path: Path) -> str:
    suffix = path.suffix.lower()
    if suffix == ".txt":
        return load_txt(path)
    elif suffix == ".pdf":
        return load_pdf(path)
    elif suffix == ".docx":
        return load_docx(path)
    else:
        raise ValueError(f"Неподдерживаемый формат: {suffix}")


# ================= TEXT UTILS =================

def split_text(text: str, max_tokens: int) -> list[str]:
    max_chars = max_tokens * CHARS_PER_TOKEN
    return [text[i:i + max_chars] for i in range(0, len(text), max_chars)]


# ================= LLM HELPERS =================

def detect_language(client: OpenAI, text: str, model: str) -> str:
    """Определяем язык один раз"""
    sample = text[:2000]

    resp = client.responses.create(
        model=model,
        input=[
            {"role": "system", "content": "Ты лингвист."},
            {
                "role": "user",
                "content": (
                    "Определи язык текста одним словом "
                    "(например: Russian, English, German):\n\n"
                    f"{sample}"
                )
            }
        ],
        max_output_tokens=10
    )
    return resp.output_text.strip()


def build_prompt(mode: str, language: str) -> str:
    if mode == "outline":
        return (
            f"Сделай структурированный outline (иерархия пунктов) "
            f"на языке {language}."
        )
    if mode == "bullet":
        return (
            f"Сделай краткое резюме в виде маркированных списков "
            f"на языке {language}."
        )
    if mode == "executive":
        return (
            f"Сделай executive summary: суть, выводы, ключевые решения. "
            f"Язык: {language}."
        )
    raise ValueError("Неизвестный режим")


def summarize_chunk(client: OpenAI, text: str, model: str, instruction: str) -> str:
    resp = client.responses.create(
        model=model,
        input=[
            {"role": "system", "content": "Ты точный аналитический ассистент."},
            {
                "role": "user",
                "content": f"{instruction}\n\nТекст:\n{text}"
            }
        ],
        max_output_tokens=300
    )
    return resp.output_text.strip()


# ================= PIPELINE =================

def summarize_document(
    text: str,
    model: str,
    chunk_tokens: int,
    mode: str,
    verbose: bool
) -> str:
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    if verbose:
        print("🌍 Определение языка...")
    language = detect_language(client, text, model)

    instruction = build_prompt(mode, language)

    chunks = split_text(text, chunk_tokens)
    summaries = []

    for chunk in tqdm(chunks, desc="🧩 Суммаризация", unit="chunk"):
        summaries.append(
            summarize_chunk(client, chunk, model, instruction)
        )

    combined = "\n\n".join(summaries)

    if verbose:
        print("🧠 Финальная агрегация...")

    final = client.responses.create(
        model=model,
        input=[
            {"role": "system", "content": "Ты эксперт по итоговым резюме."},
            {
                "role": "user",
                "content": (
                    f"{instruction}\n\n"
                    "Сделай итоговое резюме на основе:\n\n"
                    f"{combined}"
                )
            }
        ],
        max_output_tokens=700
    )

    return final.output_text.strip()


# ================= CLI =================

def main() -> None:
    parser = argparse.ArgumentParser(
        prog="summarize",
        description="Production CLI: суммаризация TXT / PDF / DOCX"
    )

    parser.add_argument("input", help="Путь к файлу")
    parser.add_argument(
        "-m", "--model",
        default="gpt-4.1-mini",
        help="Модель OpenAI"
    )
    parser.add_argument(
        "--chunk-tokens",
        type=int,
        default=3000,
        help="Размер чанка в токенах"
    )
    parser.add_argument(
        "--mode",
        choices=["outline", "bullet", "executive"],
        default="bullet",
        help="Режим суммаризации"
    )
    parser.add_argument(
        "-o", "--output",
        help="Файл для сохранения результата"
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Подробный вывод"
    )

    args = parser.parse_args()
    path = Path(args.input)

    if not path.exists():
        print("Файл не найден", file=sys.stderr)
        sys.exit(1)

    text = load_text(path)

    result = summarize_document(
        text=text,
        model=args.model,
        chunk_tokens=args.chunk_tokens,
        mode=args.mode,
        verbose=args.verbose
    )

    if args.output:
        Path(args.output).write_text(result, encoding="utf-8")
    else:
        print("\n📄 SUMMARY:\n")
        print(result)


if __name__ == "__main__":
    main()