# AI text summarizer - GUI-вариант для Windows на PyQt5
# - TXT / PDF / DOCX
# - большие файлы (chunking)
# - streaming-progress по токенам
# -auto-language
# - режимы outline / bullet / executive
# - domain: legal / technical / scientific
# - светлая / тёмная тема
# - responsive UI (ничего не «висит»)


# pip install openai PyQt5 pypdf python-docx tqdm


import os
import sys
from pathlib import Path

from PyQt5.QtWidgets import (
    QApplication, QWidget, QPushButton, QLabel, QTextEdit,
    QFileDialog, QComboBox, QVBoxLayout, QHBoxLayout,
    QProgressBar, QMessageBox, QCheckBox
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal

from openai import OpenAI
from pypdf import PdfReader
from docx import Document


# ================= CONFIG =================

CHARS_PER_TOKEN = 4


# ================= FILE LOADERS =================

def load_text(path: Path) -> str:
    if path.suffix.lower() == ".txt":
        return path.read_text(encoding="utf-8", errors="ignore")
    if path.suffix.lower() == ".pdf":
        reader = PdfReader(path)
        return "\n\n".join(p.extract_text() or "" for p in reader.pages)
    if path.suffix.lower() == ".docx":
        doc = Document(path)
        return "\n".join(p.text for p in doc.paragraphs if p.text.strip())
    raise ValueError("Неподдерживаемый формат")


def split_text(text: str, max_tokens: int) -> list[str]:
    max_chars = max_tokens * CHARS_PER_TOKEN
    return [text[i:i + max_chars] for i in range(0, len(text), max_chars)]


# ================= PROMPTS =================

def domain_instruction(domain: str) -> str:
    return {
        "legal": "Юридический стиль: точные формулировки и правовые выводы.",
        "technical": "Технический стиль: чёткие определения, алгоритмы.",
        "scientific": "Научный стиль: формальная подача, методы, выводы."
    }.get(domain, "")


def build_instruction(mode: str, language: str, domain: str) -> str:
    base = {
        "outline": f"Сделай структурированный outline на языке {language}.",
        "bullet": f"Сделай краткое резюме в bullet-пунктах на языке {language}.",
        "executive": f"Сделай executive summary на языке {language}."
    }[mode]
    return f"{base}\n{domain_instruction(domain)}"


# ================= WORKER THREAD =================

class SummarizeWorker(QThread):
    progress = pyqtSignal(int)
    text_chunk = pyqtSignal(str)
    finished = pyqtSignal(str)
    error = pyqtSignal(str)

    def __init__(self, text, model, chunk_tokens, mode, domain):
        super().__init__()
        self.text = text
        self.model = model
        self.chunk_tokens = chunk_tokens
        self.mode = mode
        self.domain = domain

    def run(self):
        try:
            client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

            # detect language
            lang_resp = client.responses.create(
                model=self.model,
                input="Определи язык текста одним словом:\n\n" + self.text[:2000],
                max_output_tokens=10
            )
            language = lang_resp.output_text.strip()

            instruction = build_instruction(self.mode, language, self.domain)
            chunks = split_text(self.text, self.chunk_tokens)

            summaries = []
            token_count = 0

            for chunk in chunks:
                collected = []
                with client.responses.stream(
                    model=self.model,
                    input=[
                        {"role": "system", "content": "Ты точный аналитический ассистент."},
                        {"role": "user", "content": f"{instruction}\n\n{chunk}"}
                    ],
                    max_output_tokens=300
                ) as stream:
                    for event in stream:
                        if event.type == "response.output_text.delta":
                            token = event.delta
                            collected.append(token)
                            token_count += 1
                            self.progress.emit(token_count)
                            self.text_chunk.emit(token)

                summaries.append("".join(collected))

            final_resp = client.responses.create(
                model=self.model,
                input=f"{instruction}\n\n" + "\n\n".join(summaries),
                max_output_tokens=800
            )

            self.finished.emit(final_resp.output_text.strip())

        except Exception as e:
            self.error.emit(str(e))


# ================= GUI =================

class SummarizerGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("LLM Document Summarizer")
        self.resize(900, 700)

        self.file_label = QLabel("Файл не выбран")
        self.open_btn = QPushButton("Открыть файл")
        self.run_btn = QPushButton("Суммаризировать")

        self.mode_box = QComboBox()
        self.mode_box.addItems(["bullet", "outline", "executive"])

        self.domain_box = QComboBox()
        self.domain_box.addItems(["technical", "legal", "scientific"])

        self.theme_toggle = QCheckBox("Тёмная тема")

        self.output = QTextEdit()
        self.output.setReadOnly(True)

        self.progress = QProgressBar()
        self.progress.setMaximum(0)

        layout = QVBoxLayout()
        top = QHBoxLayout()

        top.addWidget(self.open_btn)
        top.addWidget(QLabel("Mode"))
        top.addWidget(self.mode_box)
        top.addWidget(QLabel("Domain"))
        top.addWidget(self.domain_box)
        top.addWidget(self.theme_toggle)

        layout.addLayout(top)
        layout.addWidget(self.file_label)
        layout.addWidget(self.run_btn)
        layout.addWidget(self.progress)
        layout.addWidget(self.output)

        self.setLayout(layout)

        self.open_btn.clicked.connect(self.open_file)
        self.run_btn.clicked.connect(self.run)
        self.theme_toggle.stateChanged.connect(self.toggle_theme)

        self.text = ""

    def open_file(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Выбрать файл", "", "Documents (*.txt *.pdf *.docx)"
        )
        if path:
            self.file_label.setText(path)
            self.text = load_text(Path(path))

    def run(self):
        if not self.text:
            QMessageBox.warning(self, "Ошибка", "Файл не выбран")
            return

        self.output.clear()
        self.progress.setValue(0)

        self.worker = SummarizeWorker(
            text=self.text,
            model="gpt-4.1-mini",
            chunk_tokens=3000,
            mode=self.mode_box.currentText(),
            domain=self.domain_box.currentText()
        )

        self.worker.progress.connect(lambda v: self.progress.setValue(v))
        self.worker.text_chunk.connect(self.output.insertPlainText)
        self.worker.finished.connect(self.on_finished)
        self.worker.error.connect(self.on_error)

        self.worker.start()

    def on_finished(self, text):
        self.output.append("\n\n=== FINAL SUMMARY ===\n")
        self.output.append(text)

    def on_error(self, msg):
        QMessageBox.critical(self, "Ошибка", msg)

    def toggle_theme(self):
        if self.theme_toggle.isChecked():
            self.setStyleSheet("""
                QWidget { background: #121212; color: #e0e0e0; }
                QTextEdit { background: #1e1e1e; }
                QPushButton { background: #2c2c2c; }
            """)
        else:
            self.setStyleSheet("")


# ================= ENTRY =================

if __name__ == "__main__":
    app = QApplication(sys.argv)
    gui = SummarizerGUI()
    gui.show()
    sys.exit(app.exec_())