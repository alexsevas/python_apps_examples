# AI text summarizer v0.0.3, обновлённый GUI-вариант, где список моделей подгружается автоматически
# Как мы делаем автодетект:
# OpenAI - client.models.list()
# GoogleGemini - genai.list_models()
# g4f - introspection g4f.models
# Ollama - GET http://localhost:11434/api/tags
# GUI не знает деталей — вся логика инкапсулирована.

# pip install openai google-generativeai g4f requests PyQt5 pypdf python-docx


import os
import sys
import requests
from pathlib import Path

from PyQt5.QtWidgets import (
    QApplication, QWidget, QPushButton, QLabel, QTextEdit,
    QFileDialog, QComboBox, QVBoxLayout, QHBoxLayout,
    QProgressBar, QMessageBox
)
from PyQt5.QtCore import QThread, pyqtSignal

from pypdf import PdfReader
from docx import Document


# ================= FILE LOADING =================

def load_text(path: Path) -> str:
    if path.suffix.lower() == ".txt":
        return path.read_text(encoding="utf-8", errors="ignore")
    if path.suffix.lower() == ".pdf":
        r = PdfReader(path)
        return "\n".join(p.extract_text() or "" for p in r.pages)
    if path.suffix.lower() == ".docx":
        d = Document(path)
        return "\n".join(p.text for p in d.paragraphs if p.text.strip())
    raise ValueError("Unsupported format")


# ================= MODEL DISCOVERY =================

def openai_models():
    try:
        from openai import OpenAI
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        return sorted(
            m.id for m in client.models.list().data
            if "gpt" in m.id
        )
    except Exception as e:
        return [f"Ошибка OpenAI: {e}"]


def google_models():
    try:
        import google.generativeai as genai
        genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
        return sorted(
            m.name.replace("models/", "")
            for m in genai.list_models()
            if "generateContent" in m.supported_generation_methods
        )
    except Exception as e:
        return [f"Ошибка Google: {e}"]


def g4f_models():
    try:
        import g4f
        return sorted(str(m) for m in g4f.models)
    except Exception as e:
        return [f"Ошибка g4f: {e}"]


def ollama_models():
    try:
        r = requests.get("http://localhost:11434/api/tags", timeout=2)
        return sorted(m["name"] for m in r.json()["models"])
    except Exception as e:
        return [f"Ollama недоступен: {e}"]


# ================= PROMPTS =================

def domain_instruction(domain):
    return {
        "legal": "Юридический стиль, правовые выводы.",
        "technical": "Технический стиль, алгоритмы и точность.",
        "scientific": "Научный стиль, методы, выводы."
    }[domain]


def build_prompt(mode, domain, text):
    base = {
        "bullet": "Суммируй в bullet-пунктах.",
        "outline": "Сделай структурированный outline.",
        "executive": "Сделай executive summary."
    }[mode]
    return f"{base}\n{domain_instruction(domain)}\n\n{text}"


# ================= ENGINES =================

class BaseEngine:
    def stream(self, prompt):
        raise NotImplementedError


class OpenAIEngine(BaseEngine):
    def __init__(self, model):
        from openai import OpenAI
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.model = model

    def stream(self, prompt):
        with self.client.responses.stream(
            model=self.model,
            input=prompt,
            max_output_tokens=800
        ) as stream:
            for ev in stream:
                if ev.type == "response.output_text.delta":
                    yield ev.delta


class GeminiEngine(BaseEngine):
    def __init__(self, model):
        import google.generativeai as genai
        genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
        self.model = genai.GenerativeModel(model)

    def stream(self, prompt):
        for chunk in self.model.generate_content(prompt, stream=True):
            if chunk.text:
                yield chunk.text


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

class Worker(QThread):
    token = pyqtSignal(str)
    error = pyqtSignal(str)

    def __init__(self, engine, prompt):
        super().__init__()
        self.engine = engine
        self.prompt = prompt

    def run(self):
        try:
            for tok in self.engine.stream(self.prompt):
                self.token.emit(tok)
        except Exception as e:
            self.error.emit(str(e))


# ================= GUI =================

class GUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("LLM Summarizer (Auto-Detect Models)")
        self.resize(950, 700)

        self.file_btn = QPushButton("Открыть файл")
        self.run_btn = QPushButton("Суммаризировать")

        self.engine_box = QComboBox()
        self.engine_box.addItems(["OpenAI", "Google", "g4f", "Ollama"])

        self.model_box = QComboBox()

        self.mode_box = QComboBox()
        self.mode_box.addItems(["bullet", "outline", "executive"])

        self.domain_box = QComboBox()
        self.domain_box.addItems(["technical", "legal", "scientific"])

        self.output = QTextEdit()
        self.progress = QProgressBar()
        self.progress.setMaximum(0)

        top = QHBoxLayout()
        for w in (
            self.file_btn,
            QLabel("Engine"), self.engine_box,
            QLabel("Model"), self.model_box,
            self.mode_box, self.domain_box
        ):
            top.addWidget(w)

        layout = QVBoxLayout(self)
        layout.addLayout(top)
        layout.addWidget(self.run_btn)
        layout.addWidget(self.progress)
        layout.addWidget(self.output)

        self.file_btn.clicked.connect(self.open_file)
        self.run_btn.clicked.connect(self.run)
        self.engine_box.currentTextChanged.connect(self.load_models)

        self.text = ""
        self.load_models()

    def load_models(self):
        self.model_box.clear()
        eng = self.engine_box.currentText()

        if eng == "OpenAI":
            self.model_box.addItems(openai_models())
        elif eng == "Google":
            self.model_box.addItems(google_models())
        elif eng == "g4f":
            self.model_box.addItems(g4f_models())
        elif eng == "Ollama":
            self.model_box.addItems(ollama_models())

    def open_file(self):
        p, _ = QFileDialog.getOpenFileName(self, "", "", "Docs (*.txt *.pdf *.docx)")
        if p:
            self.text = load_text(Path(p))

    def run(self):
        if not self.text:
            QMessageBox.warning(self, "Ошибка", "Файл не выбран")
            return

        eng = self.engine_box.currentText()
        model = self.model_box.currentText()

        if eng == "OpenAI":
            engine = OpenAIEngine(model)
        elif eng == "Google":
            engine = GeminiEngine(model)
        elif eng == "g4f":
            engine = G4FEngine(model)
        else:
            engine = OllamaEngine(model)

        prompt = build_prompt(
            self.mode_box.currentText(),
            self.domain_box.currentText(),
            self.text
        )

        self.output.clear()
        self.worker = Worker(engine, prompt)
        self.worker.token.connect(self.output.insertPlainText)
        self.worker.error.connect(lambda e: QMessageBox.critical(self, "Ошибка", e))
        self.worker.start()


# ================= ENTRY =================

if __name__ == "__main__":
    app = QApplication(sys.argv)
    gui = GUI()
    gui.show()
    sys.exit(app.exec_())