# Берёт обычный PDF и создаёт копию, защищённую паролем

# pip install PyPDF2


from __future__ import annotations
from pathlib import Path
from typing import Union

from PyPDF2 import PdfReader, PdfWriter

PDFPath = Union[str, Path]


def encrypt_pdf(input_path: PDFPath, output_path: PDFPath, password: str) -> Path:
    """
    Шифрует PDF-файл паролем и сохраняет в output_path.
    Возвращает путь к зашифрованному файлу.
    """
    in_path = Path(input_path)
    out_path = Path(output_path)

    reader = PdfReader(in_path)
    writer = PdfWriter()

    for page in reader.pages:
        writer.add_page(page)

    writer.encrypt(password)

    with out_path.open("wb") as f:
        writer.write(f)

    return out_path


def encrypt_with_suffix(input_path: PDFPath, password: str, suffix: str = "_encrypted") -> Path:
    """
    Создаёт зашифрованную копию рядом с исходным файлом.
    Например: secret.pdf → secret_encrypted.pdf
    """
    in_path = Path(input_path)
    output_path = in_path.with_name(f"{in_path.stem}{suffix}{in_path.suffix}")
    return encrypt_pdf(in_path, output_path, password)


if __name__ == "__main__":
    pdf_file = "secret.pdf"
    pdf_password = "pythontoday"

    encrypted_path = encrypt_with_suffix(pdf_file, pdf_password)
    print(f"Создан зашифрованный файл: {encrypted_path}")
