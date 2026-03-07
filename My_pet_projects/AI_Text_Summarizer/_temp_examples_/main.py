# pip install tqdm openai pypdf python-docx

# Примеры использования:
# export OPENAI_API_KEY="sk-..."
# # Юридический договор
# summarize contract.pdf --domain legal --mode executive -v
# # Техническая документация
# summarize spec.docx --domain technical --mode outline
# # Научная статья
# summarize paper.pdf --domain scientific --mode bullet
# # Большой текст с выводом в файл
# summarize book.txt --chunk-tokens 2000 -o summary.txt

# v0.0.5:
# - TXT / PDF / DOCX
# - chunking больших файлов
# - progress-bar по реальным токенам (streaming)
# - auto-language
# - режимы outline / bullet / executive
# - domain-режимы legal / technical / scientific
# - современный OpenAI SDK (responses.stream)



#!/usr/bin/env python3
"""
summarize.py — production CLI для суммаризации TXT / PDF / DOCX
"""

import os
import sys
import argparse
from pathlib import Path

from openai import OpenAI
from pypdf import PdfReader
from docx import Document
from tqdm import tqdm


# ==========================================================
# CONFIG
# ==========================================================

CHARS_PER_TOKEN = 4   # безопасная аппроксимация


# ==========================================================
# FILE LOADERS
# ==========================================================

def load_txt(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="ignore")


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
    if suffix == ".pdf":
        return load_pdf(path)
    if suffix == ".docx":
        return load_docx(path)
    raise ValueError(f"Неподдерживаемый формат: {suffix}")


# ==========================================================
# TEXT UTILS
# ==========================================================

def split_text(text: str, max_tokens: int) -> list[str]:
    max_chars = max_tokens * CHARS_PER_TOKEN
    return [text[i:i + max_chars] for i in range(0, len(text), max_chars)]


# ==========================================================
# LLM HELPERS
# ==========================================================

def detect_language(client: OpenAI, text: str, model: str) -> str:
    sample = text[:2000]

    resp = client.responses.create(
        model=model,
        input=[
            {"role": "system", "content": "Ты профессиональный лингвист."},
            {
                "role": "user",
                "content": (
                    "Определи язык текста одним словом "
                    "(Russian, English, German, French и т.д.):\n\n"
                    f"{sample}"
                )
            }
        ],
        max_output_tokens=10
    )
    return resp.output_text.strip()


def domain_instruction(domain: str) -> str:
    if domain == "legal":
        return (
            "Юридический стиль: точные формулировки, "
            "чёткое разделение фактов, выводов и правовых последствий."
        )
    if domain == "technical":
        return (
            "Технический стиль: чёткие определения, алгоритмы, "
            "причинно-следственные связи, без воды."
        )
    if domain == "scientific":
        return (
            "Научный стиль: формальная подача, термины, "
            "гипотезы, методы, выводы."
        )
    return ""


def build_instruction(mode: str, language: str, domain: str) -> str:
    base = {
        "outline": f"Сделай структурированный outline на языке {language}.",
        "bullet": f"Сделай краткое резюме в виде bullet-пунктов на языке {language}.",
        "executive": (
            f"Сделай executive summary (суть, выводы, решения) "
            f"на языке {language}."
        ),
    }[mode]

    dom = domain_instruction(domain)
    return f"{base}\n{dom}".strip()


# ==========================================================
# STREAMING SUMMARIZATION
# ==========================================================

def summarize_chunk_streaming(
    client: OpenAI,
    text: str,
    model: str,
    instruction: str,
    pbar: tqdm
) -> str:
    collected = []

    with client.responses.stream(
        model=model,
        input=[
            {"role": "system", "content": "Ты точный аналитический ассистент."},
            {
                "role": "user",
                "content": f"{instruction}\n\nТекст:\n{text}"
            }
        ],
        max_output_tokens=300
    ) as stream:
        for event in stream:
            if event.type == "response.output_text.delta":
                token = event.delta
                collected.append(token)
                pbar.update(1)

    return "".join(collected).strip()


# ==========================================================
# PIPELINE
# ==========================================================

def summarize_document(
    text: str,
    model: str,
    chunk_tokens: int,
    mode: str,
    domain: str,
    verbose: bool
) -> str:
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    if verbose:
        print("🌍 Определение языка…")
    language = detect_language(client, text, model)

    instruction = build_instruction(mode, language, domain)
    chunks = split_text(text, chunk_tokens)

    summaries = []

    with tqdm(
        desc="🧩 Генерация (tokens)",
        unit="tok",
        dynamic_ncols=True
    ) as pbar:
        for chunk in chunks:
            summaries.append(
                summarize_chunk_streaming(
                    client, chunk, model, instruction, pbar
                )
            )

    combined = "\n\n".join(summaries)

    if verbose:
        print("\n🧠 Финальная агрегация…")

    final = client.responses.create(
        model=model,
        input=[
            {"role": "system", "content": "Ты эксперт по итоговым резюме."},
            {
                "role": "user",
                "content": f"{instruction}\n\n{combined}"
            }
        ],
        max_output_tokens=800
    )

    return final.output_text.strip()


# ==========================================================
# CLI
# ==========================================================

def main() -> None:
    parser = argparse.ArgumentParser(
        prog="summarize",
        description="Production CLI для суммаризации TXT / PDF / DOCX"
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
        help="Размер чанка (в токенах)"
    )
    parser.add_argument(
        "--mode",
        choices=["outline", "bullet", "executive"],
        default="bullet",
        help="Формат результата"
    )
    parser.add_argument(
        "--domain",
        choices=["legal", "technical", "scientific"],
        default="technical",
        help="Предметная область"
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
        domain=args.domain,
        verbose=args.verbose
    )

    if args.output:
        Path(args.output).write_text(result, encoding="utf-8")
    else:
        print("\n📄 SUMMARY:\n")
        print(result)


if __name__ == "__main__":
    main()