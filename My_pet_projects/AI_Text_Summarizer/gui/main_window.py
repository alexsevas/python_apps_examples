from PyQt5.QtWidgets import (QWidget, QComboBox, QPushButton, QTextEdit, 
                             QProgressBar, QHBoxLayout, QVBoxLayout, QFileDialog, 
                             QMessageBox, QProgressDialog, QApplication)
from PyQt5.QtCore import QSettings, QThread, pyqtSignal
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
        self.worker = None
        self.download_thread = None
        self.current_file_path = None
        
        # Проверяем Ollama при запуске
        self.check_ollama_status()
        
        # UI элементы
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
        self.output.setReadOnly(True)
        
        self.progress = QProgressBar()
        self.progress.setMaximum(0)
        self.progress.hide()
        
        self.update_models()

        # Кнопки
        open_btn = QPushButton("Open File")
        run_btn = QPushButton("Summarize")
        stop_btn = QPushButton("Stop")
        refresh_btn = QPushButton("🔄")
        save_btn = QPushButton("Save Result")
        copy_btn = QPushButton("Copy")
        
        refresh_btn.setMaximumWidth(40)
        refresh_btn.setToolTip("Обновить список моделей")
        stop_btn.setEnabled(False)
        save_btn.setEnabled(False)
        copy_btn.setEnabled(False)
        
        # Сохраняем ссылки на кнопки
        self.run_btn = run_btn
        self.stop_btn = stop_btn
        self.save_btn = save_btn
        self.copy_btn = copy_btn
        
        # Подключаем обработчики
        open_btn.clicked.connect(self.open_file)
        run_btn.clicked.connect(self.run)
        stop_btn.clicked.connect(self.stop_generation)
        refresh_btn.clicked.connect(self.update_models)
        save_btn.clicked.connect(self.save_result)
        copy_btn.clicked.connect(self.copy_result)

        # Layouts
        top = QHBoxLayout()
        for w in [open_btn, self.engine_box, self.model_box, refresh_btn,
                  self.mode_box, self.domain_box, run_btn, stop_btn]:
            top.addWidget(w)

        bottom_buttons = QHBoxLayout()
        bottom_buttons.addWidget(save_btn)
        bottom_buttons.addWidget(copy_btn)
        bottom_buttons.addStretch()

        main = QHBoxLayout()
        main.addWidget(self.viewer, 1)
        main.addWidget(self.output, 1)

        layout = QVBoxLayout(self)
        layout.addLayout(top)
        layout.addLayout(main)
        layout.addLayout(bottom_buttons)
        layout.addWidget(self.progress)

    def open_file(self):
        """Открывает файл с индикацией прогресса"""
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Open Document",
            "",
            "Documents (*.pdf *.txt *.docx);;All Files (*)"
        )
        if not path:
            return
        
        # Показываем индикатор загрузки
        self.progress.show()
        QApplication.processEvents()
        
        try:
            self.text = load_text(path)
            self.current_file_path = path
            
            if path.lower().endswith(".pdf"):
                self.viewer.load_pdf(path)
            else:
                self.viewer.clear()
            
            char_count = len(self.text)
            word_count = len(self.text.split())
            QMessageBox.information(
                self, 
                "Success", 
                f"Loaded successfully!\n\n"
                f"Characters: {char_count:,}\n"
                f"Words: {word_count:,}"
            )
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load file:\n{str(e)}")
            self.text = ""
            self.current_file_path = None
        finally:
            self.progress.hide()

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
                if self.ollama_helper.start_ollama():
                    QMessageBox.information(
                        self,
                        "Успех",
                        "Ollama успешно запущена!"
                    )
                    self.update_models()
                else:
                    QMessageBox.warning(
                        self,
                        "Ошибка",
                        "Не удалось запустить Ollama автоматически.\n\n"
                        "Пожалуйста, запустите Ollama вручную командой:\nollama serve"
                    )
    
    def update_models(self):
        """Обновляет список моделей"""
        engine_name = self.engine_box.currentText()
        self.model_box.clear()
        
        if engine_name == "Ollama":
            local_models = self.ollama_helper.get_local_models()
            print(f"DEBUG: Локальные модели Ollama: {local_models}")
            
            if local_models:
                self.model_box.addItem("--- Локальные модели ---")
                self.model_box.model().item(0).setEnabled(False)
                for model in local_models:
                    self.model_box.addItem(f"📦 {model}")
            else:
                print("DEBUG: Локальные модели не найдены")
            
            header_index = self.model_box.count()
            self.model_box.addItem("--- Доступные для скачивания ---")
            self.model_box.model().item(header_index).setEnabled(False)
            
            cloud_models = self.ollama_helper.get_cloud_models()
            for model_info in cloud_models:
                self.model_box.addItem(f"☁️ {model_info['name']}")
            
            if local_models:
                self.model_box.setCurrentIndex(1)
                
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
        """Запускает суммаризацию"""
        if not self.text:
            QMessageBox.warning(self, "Warning", "Please open a document first!")
            return
            
        engine_name = self.engine_box.currentText()
        model_text = self.model_box.currentText()
        
        if not model_text or model_text.startswith("---"):
            QMessageBox.warning(self, "Warning", "Please select a model!")
            return
        
        model = model_text.replace("📦 ", "").replace("☁️ ", "").strip()
        print(f"DEBUG: Выбран движок: {engine_name}, модель: {model}")
        
        # Проверяем Ollama
        if engine_name == "Ollama":
            if not self.ollama_helper.is_running():
                QMessageBox.warning(
                    self,
                    "Ollama не запущена",
                    "Ollama не запущена. Пожалуйста, запустите её сначала."
                )
                self.check_ollama_status()
                return
        
        # Если модель облачная, предлагаем скачать
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
        
        try:
            # Создаем движок
            if engine_name == "Ollama":
                engine = OllamaEngine(model)
            elif engine_name == "OpenAI":
                engine = OpenAIEngine(model)
            elif engine_name == "Google":
                engine = GeminiEngine(model)
            else:
                engine = G4FEngine(model)

            # Строим промпт
            prompt = build_prompt(
                self.mode_box.currentText(),
                self.domain_box.currentText(),
                self.text
            )
            
            print(f"DEBUG: Длина промпта: {len(prompt)} символов")

            # Запускаем worker
            self.output.clear()
            self.progress.show()
            self.run_btn.setEnabled(False)
            self.stop_btn.setEnabled(True)
            self.save_btn.setEnabled(False)
            self.copy_btn.setEnabled(False)
            
            self.worker = Worker(engine, prompt)
            self.worker.token.connect(self.on_token)
            self.worker.error.connect(self.on_error)
            self.worker.finished.connect(self.on_finished)
            self.worker.start()
            
        except ValueError as e:
            QMessageBox.warning(self, "Validation Error", str(e))
        except Exception as e:
            print(f"DEBUG: Ошибка при запуске: {e}")
            QMessageBox.critical(self, "Error", f"Failed to start: {str(e)}")
    
    def stop_generation(self):
        """Останавливает генерацию"""
        if self.worker and self.worker.isRunning():
            self.worker.stop()
            self.worker.wait(1000)  # Ждем 1 секунду
            if self.worker.isRunning():
                self.worker.terminate()
            self.on_finished()
            QMessageBox.information(self, "Stopped", "Generation stopped")
    
    def on_token(self, token):
        """Обработчик получения токена"""
        self.output.insertPlainText(token)
        # Автоскролл
        cursor = self.output.textCursor()
        cursor.movePosition(cursor.End)
        self.output.setTextCursor(cursor)
    
    def on_error(self, error_msg):
        """Обработчик ошибки"""
        self.progress.hide()
        self.run_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        QMessageBox.critical(self, "Error", f"Summarization failed:\n{error_msg}")
    
    def on_finished(self):
        """Обработчик завершения"""
        self.progress.hide()
        self.run_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        
        if self.output.toPlainText().strip():
            self.save_btn.setEnabled(True)
            self.copy_btn.setEnabled(True)
    
    def save_result(self):
        """Сохраняет результат в файл"""
        if not self.output.toPlainText().strip():
            return
        
        path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Result",
            "",
            "Text Files (*.txt);;Markdown Files (*.md);;All Files (*)"
        )
        
        if path:
            try:
                with open(path, 'w', encoding='utf-8') as f:
                    f.write(self.output.toPlainText())
                QMessageBox.information(self, "Success", "Result saved successfully!")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to save: {str(e)}")
    
    def copy_result(self):
        """Копирует результат в буфер обмена"""
        if not self.output.toPlainText().strip():
            return
        
        clipboard = QApplication.clipboard()
        clipboard.setText(self.output.toPlainText())
        QMessageBox.information(self, "Success", "Result copied to clipboard!")
    
    def download_model(self, model_name):
        """Скачивает модель Ollama"""
        progress_dialog = QProgressDialog(
            f"Скачивание модели {model_name}...",
            "Отмена",
            0,
            100,
            self
        )
        progress_dialog.setWindowTitle("Загрузка модели")
        progress_dialog.setWindowModality(2)
        progress_dialog.setValue(0)
        progress_dialog.show()
        
        def on_progress(data):
            status = data.get("status", "")
            if "total" in data and "completed" in data:
                total = data["total"]
                completed = data["completed"]
                percent = int((completed / total) * 100)
                progress_dialog.setValue(percent)
                progress_dialog.setLabelText(
                    f"Скачивание {model_name}...\n{status}: {percent}%"
                )
        
        class DownloadThread(QThread):
            finished_signal = pyqtSignal(bool)
            
            def __init__(self, helper, model, callback):
                super().__init__()
                self.helper = helper
                self.model = model
                self.callback = callback
                self.should_stop = False
            
            def run(self):
                success = self.helper.pull_model(self.model, self.callback)
                self.finished_signal.emit(success)
            
            def stop(self):
                self.should_stop = True
        
        self.download_thread = DownloadThread(self.ollama_helper, model_name, on_progress)
        self.download_thread.finished_signal.connect(
            lambda success: self.on_download_finished(success, model_name, progress_dialog)
        )
        progress_dialog.canceled.connect(lambda: self.cancel_download(progress_dialog))
        self.download_thread.start()
    
    def cancel_download(self, progress_dialog):
        """Отменяет скачивание модели"""
        if self.download_thread and self.download_thread.isRunning():
            self.download_thread.stop()
            self.download_thread.wait(1000)
            if self.download_thread.isRunning():
                self.download_thread.terminate()
            progress_dialog.close()
            QMessageBox.information(self, "Cancelled", "Download cancelled")
    
    def on_download_finished(self, success, model_name, progress_dialog):
        """Обработчик завершения скачивания модели"""
        progress_dialog.close()
        
        if success:
            QMessageBox.information(
                self,
                "Успех",
                f"Модель {model_name} успешно скачана!"
            )
            self.update_models()
        else:
            QMessageBox.critical(
                self,
                "Ошибка",
                f"Не удалось скачать модель {model_name}"
            )
    
    def closeEvent(self, event):
        """Очистка при закрытии окна"""
        # Останавливаем worker если работает
        if self.worker and self.worker.isRunning():
            self.worker.stop()
            self.worker.wait(1000)
            if self.worker.isRunning():
                self.worker.terminate()
        
        # Останавливаем скачивание если идет
        if self.download_thread and self.download_thread.isRunning():
            self.download_thread.stop()
            self.download_thread.wait(1000)
            if self.download_thread.isRunning():
                self.download_thread.terminate()
        
        # Очищаем viewer
        self.viewer.clear()
        
        event.accept()
