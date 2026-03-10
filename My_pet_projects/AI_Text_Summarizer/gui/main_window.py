from PyQt5.QtWidgets import *
from PyQt5.QtCore import QSettings
from PyQt5.QtWidgets import QApplication, QWidget, QComboBox, QPushButton, QTextEdit, QProgressBar, QHBoxLayout, QVBoxLayout, QFileDialog, QMessageBox
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
        self.text = ""
        self.engine_box = QComboBox()
        self.engine_box.addItems(self.api.available_engines())
        self.engine_box.setCurrentText("Ollama")
        self.engine_box.currentTextChanged.connect(self.update_models)
        self.model_box = QComboBox()
        self.mode_box = QComboBox()
        self.mode_box.addItems(["bullet","outline","executive"])
        self.domain_box = QComboBox()
        self.domain_box.addItems(["technical","legal","scientific"])
        self.viewer = PDFViewer()
        self.output = QTextEdit()
        self.progress = QProgressBar()
        self.progress.setMaximum(0)
        self.progress.hide()
        
        self.update_models()

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
        path,_ = QFileDialog.getOpenFileName(
            self,
            "Open Document",
            "",
            "Documents (*.pdf *.txt *.docx);;All Files (*)"
        )
        if not path:
            return
        try:
            self.text = load_text(path)
            if path.lower().endswith(".pdf"):
                self.viewer.load_pdf(path)
            else:
                self.viewer.scene.clear()
            QMessageBox.information(self, "Success", f"Loaded {len(self.text)} characters")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load file: {str(e)}")


    def update_models(self):
        engine_name = self.engine_box.currentText()
        self.model_box.clear()
        
        if engine_name == "Ollama":
            self.model_box.addItems([
                "llama3.2",
                "llama3.1",
                "llama2",
                "mistral",
                "mixtral",
                "phi3",
                "gemma2",
                "qwen2.5"
            ])
        elif engine_name == "OpenAI":
            self.model_box.addItems([
                "gpt-4o",
                "gpt-4o-mini",
                "gpt-4-turbo",
                "gpt-3.5-turbo"
            ])
        elif engine_name == "Google":
            self.model_box.addItems([
                "gemini-1.5-pro",
                "gemini-1.5-flash",
                "gemini-pro"
            ])
        else:  # g4f
            self.model_box.addItems([
                "gpt-4",
                "gpt-3.5-turbo"
            ])

    def run(self):
        if not self.text:
            QMessageBox.warning(self, "Warning", "Please open a document first!")
            return
            
        engine_name = self.engine_box.currentText()
        model = self.model_box.currentText()
        
        if not model:
            QMessageBox.warning(self, "Warning", "Please select a model!")
            return
        
        try:
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
            self.progress.show()
            self.worker = Worker(engine, prompt)
            self.worker.token.connect(
                lambda t: self.output.insertPlainText(t)
            )
            self.worker.error.connect(self.on_error)
            self.worker.finished.connect(self.on_finished)
            self.worker.start()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to start: {str(e)}")
    
    def on_error(self, error_msg):
        self.progress.hide()
        QMessageBox.critical(self, "Error", f"Summarization failed: {error_msg}")
    
    def on_finished(self):
        self.progress.hide()