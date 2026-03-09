from PyQt5.QtWidgets import *
from PyQt5.QtCore import QSettings
from core.api_profiles import APIProfiles
from core.document_loader import load_text
from core.prompt_builder import build_prompt
from engines.ollama_engine import OllamaEngine
from engines.openai_engine import OpenAIEngine
from engines.gemini_engine import GeminiEngine
from engines.g4f_engine import G4FEngine
from gui.worker import Worker
from gui.viewer import PDFViewer


class MainWindow(QWidget):

    def __init__(self):
        super().__init__()
        self.setWindowTitle("LLM Summarizer")
        screen = QApplication.primaryScreen().size()
        self.resize(
            int(screen.width()*0.8),
            int(screen.height()*0.8)
        )
        self.settings = QSettings("LLM","Summarizer")
        self.api = APIProfiles()
        self.engine_box = QComboBox()
        self.engine_box.addItems(self.api.available_engines())
        self.engine_box.setCurrentText("Ollama")
        self.model_box = QComboBox()
        self.mode_box = QComboBox()
        self.mode_box.addItems(["bullet","outline","executive"])
        self.domain_box = QComboBox()
        self.domain_box.addItems(["technical","legal","scientific"])
        self.viewer = PDFViewer()
        self.output = QTextEdit()
        self.progress = QProgressBar()
        self.progress.setMaximum(0)

        open_btn = QPushButton("Open File")
        run_btn = QPushButton("Summarize")
        open_btn.clicked.connect(self.open_file)
        run_btn.clicked.connect(self.run)

        top = QHBoxLayout()

        for w in [
            open_btn,
            self.engine_box,
            self.model_box,
            self.mode_box,
            self.domain_box,
            run_btn
        ]:
            top.addWidget(w)

        main = QHBoxLayout()

        main.addWidget(self.viewer,1)
        main.addWidget(self.output,1)

        layout = QVBoxLayout(self)

        layout.addLayout(top)
        layout.addLayout(main)
        layout.addWidget(self.progress)


    def open_file(self):
        path,_ = QFileDialog.getOpenFileName()
        if not path:
            return
        self.text = load_text(path)
        if path.endswith(".pdf"):
            self.viewer.load_pdf(path)


    def run(self):
        engine_name = self.engine_box.currentText()
        model = self.model_box.currentText()
        if engine_name == "Ollama":
            engine = OllamaEngine(model)
        elif engine_name == "OpenAI":
            engine = OpenAIEngine(model)
        elif engine_name == "Google":
            engine = GeminiEngine(model)
        else:
            engine = G4FEngine(model)

        prompt = build_prompt(
            self.mode_box.currentText(),
            self.domain_box.currentText(),
            self.text
        )

        self.output.clear()
        self.worker = Worker(engine, prompt)
        self.worker.token.connect(
            lambda t: self.output.insertPlainText(t)
        )
        self.worker.start()