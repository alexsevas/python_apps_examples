from pathlib import Path
from pypdf import PdfReader
from docx import Document


def load_text(path):
    path = Path(path)
    if path.suffix.lower() == ".txt":
        return path.read_text(encoding="utf8")

    if path.suffix.lower() == ".pdf":
        reader = PdfReader(path)
        return "\n".join(
            page.extract_text() or ""
            for page in reader.pages
        )

    if path.suffix.lower() == ".docx":
        doc = Document(path)
        return "\n".join(
            p.text for p in doc.paragraphs
        )

    raise Exception("Unsupported file")