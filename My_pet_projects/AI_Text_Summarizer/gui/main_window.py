from PyQt5.QtWidgets import *
from PyQt5.QtCore import QSettings, QThread, pyqtSignal
from PyQt5.QtWidgets import QApplication, QWidget, QComboBox, QPushButton, QTextEdit, QProgressBar, QHBoxLayout, QVBoxLayout, QFileDialog, QMessageBox, QLabel, QProgressDialog
from core.api_profiles import APIProfiles
from core.document_loader import load_text
from core.prompt_builder import build_prompt
from core.ollama_helper import OllamaHelper
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
        self.ollama_helper = OllamaHelper()
        self.text = ""
        
        # Проверяем Ollama при запуске
        self.check_ollama_status()
        
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


    def check_ollama_status(self):
        """Проверяет статус Ollama и предлагает запустить если не запущена"""
        if not self.ollama_helper.is_running():
            reply = QMessageBox.question(
                self,
                "Ollama не запущена",
                "Ollama не запущена на вашем компьютере.\n\nЗапустить Ollama сейчас?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.Yes
            )
            
            if reply == QMessageBox.Yes:
                QMessageBox.information(
                    self,
                    "Запуск Ollama",
                    "Запускаю Ollama... Пожалуйста, подождите."
                )
                if self.ollama_helper.start_ollama():
                    QMessageBox.information(
                        self,
                        "Успех",
                        "Ollama успешно запущена!"
                    )
                else:
                    QMessageBox.warning(
                        self,
                        "Ошибка",
                        "Не удалось запустить Ollama автоматически.\n\n"
                        "Пожалуйста, запустите Ollama вручную командой:\nollama serve"
                    )
    
    def update_models(self):
        engine_name = self.engine_box.currentText()
        self.model_box.clear()
        
        if engine_name == "Ollama":
            # Получаем локальные модели
            local_models = self.ollama_helper.get_local_models()
            
            if local_models:
                # Добавляем заголовок для локальных моделей
                self.model_box.addItem("--- Локальные модели ---")
                self.model_box.model().item(0).setEnabled(False)
                for model in local_models:
                    self.model_box.addItem(f"📦 {model}")
            
            # Добавляем облачные модели
            self.model_box.addItem("--- Доступные для скачивания ---")
            self.model_box.model().item(self.model_box.count() - 1).setEnabled(False)
            
            cloud_models = self.ollama_helper.get_cloud_models()
            for model_info in cloud_models:
                model_name = model_info["name"]
                # Проверяем, не установлена ли уже эта модель
                if not any(model_name in local for local in local_models):
                    self.model_box.addItem(f"☁️ {model_name}")
            
            # Выбираем первую доступную модель
            if local_models:
                self.model_box.setCurrentIndex(1)  # Первая после заголовка
                
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
        model_text = self.model_box.currentText()
        
        if not model_text or model_text.startswith("---"):
            QMessageBox.warning(self, "Warning", "Please select a model!")
            return
        
        # Убираем эмодзи и пробелы из названия модели
        model = model_text.replace("📦 ", "").replace("☁️ ", "").strip()
        
        # Если модель облачная (с ☁️), предлагаем скачать
        if "☁️" in model_text:
            reply = QMessageBox.question(
                self,
                "Скачать модель?",
                f"Модель '{model}' не установлена локально.\n\n"
                f"Скачать её сейчас? (Это может занять некоторое время)",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.Yes
            )
            
            if reply == QMessageBox.Yes:
                self.download_model(model)
                return
            else:
                return
        
        # Проверяем Ollama перед запуском
        if engine_name == "Ollama" and not self.ollama_helper.is_running():
            QMessageBox.warning(
                self,
                "Ollama не запущена",
                "Ollama не запущена. Пожалуйста, запустите её сначала."
            )
            self.check_ollama_status()
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
    
    def download_model(self, model_name):
        """Скачивает модель Ollama"""
        progress_dialog = QProgressDialog(
            f"Скачивание модели {model_name}...",
            "Отмена",
            0,
            0,
            self
        )
        progress_dialog.setWindowTitle("Загрузка модели")
        progress_dialog.setWindowModality(2)  # Qt.WindowModal
        progress_dialog.show()
        
        def on_progress(data):
            status = data.get("status", "")
            if "total" in data and "completed" in data:
                total = data["total"]
                completed = data["completed"]
                percent = int((completed / total) * 100)
                progress_dialog.setLabelText(
                    f"Скачивание {model_name}...\n{status}: {percent}%"
                )
        
        # Запускаем скачивание в отдельном потоке
        from PyQt5.QtCore import QThread
        
        class DownloadThread(QThread):
            finished = pyqtSignal(bool)
            
            def __init__(self, helper, model):
                super().__init__()
                self.helper = helper
                self.model = model
            
            def run(self):
                success = self.helper.pull_model(self.model, on_progress)
                self.finished.emit(success)
        
        self.download_thread = DownloadThread(self.ollama_helper, model_name)
        self.download_thread.finished.connect(
            lambda success: self.on_download_finished(success, model_name, progress_dialog)
        )
        progress_dialog.canceled.connect(self.download_thread.terminate)
        self.download_thread.start()
    
    def on_download_finished(self, success, model_name, progress_dialog):
        """Обработчик завершения скачивания модели"""
        progress_dialog.close()
        
        if success:
            QMessageBox.information(
                self,
                "Успех",
                f"Модель {model_name} успешно скачана!"
            )
            # Обновляем список моделей
            self.update_models()
        else:
            QMessageBox.critical(
                self,
                "Ошибка",
                f"Не удалось скачать модель {model_name}"
            )
    
    def on_error(self, error_msg):
        self.progress.hide()
        QMessageBox.critical(self, "Error", f"Summarization failed: {error_msg}")
    
    def on_finished(self):
        self.progress.hide()