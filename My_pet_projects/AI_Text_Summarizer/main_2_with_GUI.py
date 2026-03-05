# AI text summarizer v0.0.2, GUI-вариант: добавлена возможность выбора "движка" LLM (OpenAI, Google, g4f, ollama)
# Поддерживаемые движки:
# - OpenAI API – текущая реализация (responses.stream)
# - Google API (Gemini) – через google-generativeai
# - g4f (бесплатные провайдеры) – выбор моделей, доступных внутри g4f, без ключей (нестабильно, но полезно)
# - Оффлайн-режим (Ollama) – локальные модели (llama3, mistral, qwen, и т.п.), корпоративный / air-gapped сценарий

# pip install PyQt5 openai google-generativeai g4f pypdf python-docx requests


import os
import sys
import requests
from pathlib import Path

from PyQt5.QtWidgets import (
    QApplication, QWidget, QPushButton, QLabel, QTextEdit,
    QFileDialog, QComboBox, QVBoxLayout, QHBoxLayout,
    QProgressBar, QMessageBox, QCheckBox
)
from PyQt5.QtCore import QThread, pyqtSignal

from pypdf import PdfReader
from docx import Document

# ================= FILE LOADING =================

def load_text(path: Path) -> str:
    if path.suffix == ".txt":
        return path.read_text(encoding="utf-8", errors="ignore")
    if path.suffix == ".pdf":
        r = PdfReader(path)
        return "\n".join(p.extract_text() or "" for p in r.pages)
    if path.suffix == ".docx":
        d = Document(path)
        return "\n".join(p.text for p in d.paragraphs if p.text.strip())
    raise ValueError("Unsupported format")

# ================= PROMPTS =================

def domain_instruction(domain):
    return {
        "legal": "Юридический стиль, правовые выводы.",
        "technical": "Технический стиль, алгоритмы, определения.",
        "scientific": "Научный стиль, методы, гипотезы, выводы."
    }[domain]

def build_prompt(mode, language, domain, text):
    base = {
        "bullet": f"Суммируй в bullet-пунктах на языке {language}.",
        "outline": f"Сделай структурированный outline на языке {language}.",
        "executive": f"Сделай executive summary на языке {language}."
    }[mode]
    return f"{base}\n{domain_instruction(domain)}\n\n{text}"

# ================= ENGINE INTERFACES =================

class BaseEngine:
    def stream(self, prompt):
        raise NotImplementedError

# -------- OpenAI --------

class OpenAIEngine(BaseEngine):
    def __init__(self, model):
        from openai import OpenAI
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.model = model

    def stream(self, prompt):
        with self.client.responses.stream(
            model=self.model,
            input=prompt,
            max_output_tokens=500
        ) as stream:
            for ev in stream:
                if ev.type == "response.output_text.delta":
                    yield ev.delta

# -------- Google Gemini --------

class GeminiEngine(BaseEngine):
    def __init__(self, model):
        import google.generativeai as genai
        genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
        self.model = genai.GenerativeModel(model)

    def stream(self, prompt):
        resp = self.model.generate_content(prompt, stream=True)
        for chunk in resp:
            if chunk.text:
                yield chunk.text

# -------- g4f --------

class G4FEngine(BaseEngine):
    def __init__(self, model):
        import g4f
        self.g4f = g4f
        self.model = model

    def stream(self, prompt):
        resp = self.g4f.ChatCompletion.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            stream=True
        )
        for r in resp:
            yield r["choices"][0]["delta"].get("content", "")

# -------- Ollama --------

class OllamaEngine(BaseEngine):
    def __init__(self, model):
        self.model = model

    def stream(self, prompt):
        r = requests.post(
            "http://localhost:11434/api/generate",
            json={"model": self.model, "prompt": prompt, "stream": True},
            stream=True
        )
        for line in r.iter_lines():
            if line:
                yield line.decode(errors="ignore")

# ================= WORKER =================

class SummarizeWorker(QThread):
    token = pyqtSignal(str)
    finished = pyqtSignal()
    error = pyqtSignal(str)

    def __init__(self, engine, prompt):
        super().__init__()
        self.engine = engine
        self.prompt = prompt

    def run(self):
        try:
            for tok in self.engine.stream(self.prompt):
                self.token.emit(tok)
            self.finished.emit()
        except Exception as e:
            self.error.emit(str(e))

# ================= GUI =================

class GUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("LLM Summarizer (Multi-Engine)")
        self.resize(900, 700)

        self.file_btn = QPushButton("Открыть файл")
        self.run_btn = QPushButton("Суммаризировать")

        self.engine_box = QComboBox()
        self.engine_box.addItems(["OpenAI", "Google Gemini", "g4f", "Ollama"])

        self.model_box = QComboBox()

        self.mode_box = QComboBox()
        self.mode_box.addItems(["bullet", "outline", "executive"])

        self.domain_box = QComboBox()
        self.domain_box.addItems(["technical", "legal", "scientific"])

        self.output = QTextEdit()
        self.progress = QProgressBar()
        self.progress.setMaximum(0)

        top = QHBoxLayout()
        for w in [self.file_btn, QLabel("Engine"), self.engine_box,
                  QLabel("Model"), self.model_box,
                  self.mode_box, self.domain_box]:
            top.addWidget(w)

        layout = QVBoxLayout(self)
        layout.addLayout(top)
        layout.addWidget(self.run_btn)
        layout.addWidget(self.progress)
        layout.addWidget(self.output)

        self.file_btn.clicked.connect(self.open_file)
        self.run_btn.clicked.connect(self.run)
        self.engine_box.currentTextChanged.connect(self.update_models)

        self.text = ""
        self.update_models()

    def update_models(self):
        self.model_box.clear()
        eng = self.engine_box.currentText()
        if eng == "OpenAI":
            self.model_box.addItems(["gpt-4.1-mini", "gpt-4.1"])
        elif eng == "Google Gemini":
            self.model_box.addItems(["gemini-1.5-flash", "gemini-1.5-pro"])
        elif eng == "g4f":
            self.model_box.addItems(["gpt-4", "gpt-3.5-turbo"])
        elif eng == "Ollama":
            self.model_box.addItems(["llama3", "mistral", "qwen2.5"])

    def open_file(self):
        p, _ = QFileDialog.getOpenFileName(self, "", "", "Docs (*.txt *.pdf *.docx)")
        if p:
            self.text = load_text(Path(p))

    def run(self):
        if not self.text:
            QMessageBox.warning(self, "Ошибка", "Файл не выбран")
            return

        engine_name = self.engine_box.currentText()
        model = self.model_box.currentText()

        if engine_name == "OpenAI":
            engine = OpenAIEngine(model)
        elif engine_name == "Google Gemini":
            engine = GeminiEngine(model)
        elif engine_name == "g4f":
            engine = G4FEngine(model)
        else:
            engine = OllamaEngine(model)

        prompt = build_prompt(
            self.mode_box.currentText(),
            "auto",
            self.domain_box.currentText(),
            self.text
        )

        self.output.clear()
        self.worker = SummarizeWorker(engine, prompt)
        self.worker.token.connect(self.output.insertPlainText)
        self.worker.start()

# ================= ENTRY =================

if __name__ == "__main__":
    app = QApplication(sys.argv)
    gui = GUI()
    gui.show()
    sys.exit(app.exec_())