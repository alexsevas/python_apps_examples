import sys
import os
import time
import requests
import fitz  # PyMuPDF
import markdown2

from PyQt5.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QHBoxLayout,
                             QWidget, QTextEdit, QPushButton, QLabel, QProgressBar,
                             QComboBox, QLineEdit, QSplitter, QFileDialog, QMessageBox,
                             QGroupBox, QScrollArea, QShortcut)
from PyQt5.QtCore import QThread, pyqtSignal, Qt, QSize
from PyQt5.QtGui import QImage, QPixmap, QFont, QKeySequence, QWheelEvent

# Импорты API
import openai
import google.generativeai as genai
import g4f


# ================= 1. ПРОДВИНУТЫЙ PDF VIEWER =================

class PDFViewerWidget(QScrollArea):
    """Виджет для просмотра PDF с зумом и скроллом"""

    def __init__(self):
        super().__init__()
        self.setWidgetResizable(True)
        self.setAlignment(Qt.AlignCenter)

        # Контейнер для изображения
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setStyleSheet("background-color: #555;")  # Темный фон
        self.setWidget(self.image_label)

        # Данные
        self.current_pixmap = None  # Оригинал (QPixmap)
        self.zoom_level = 1.0  # Текущий зум (1.0 = 100%)
        self.pdf_page = None  # Ссылка на страницу fitz

    def set_page(self, fitz_page):
        self.pdf_page = fitz_page
        self.render_page()

    def render_page(self):
        if not self.pdf_page:
            return

        # Рендерим с учетом зума прямо из вектора (для четкости)
        # Стандартное разрешение PDF ~72 DPI. Zoom 1.0 = 72 DPI.
        # matrix(2, 2) -> 144 DPI и т.д.
        mat = fitz.Matrix(self.zoom_level * 1.5, self.zoom_level * 1.5)
        pix = self.pdf_page.get_pixmap(matrix=mat)

        # Конвертация в QImage -> QPixmap
        img_data = pix.tobytes("ppm")
        qimg = QImage.fromData(img_data)
        self.current_pixmap = QPixmap.fromImage(qimg)

        self.image_label.setPixmap(self.current_pixmap)
        self.image_label.resize(self.current_pixmap.size())

    def zoom_in(self):
        self.zoom_level += 0.1
        self.render_page()

    def zoom_out(self):
        if self.zoom_level > 0.2:
            self.zoom_level -= 0.1
            self.render_page()

    def wheelEvent(self, event: QWheelEvent):
        # Если зажат Ctrl - зумим
        if event.modifiers() == Qt.ControlModifier:
            delta = event.angleDelta().y()
            if delta > 0:
                self.zoom_in()
            else:
                self.zoom_out()
            event.accept()
        else:
            # Иначе обычный скролл
            super().wheelEvent(event)


# ================= 2. ЛОГИКА LLM =================

class LLMEngine:
    def __init__(self, provider, api_key, model_name):
        self.provider = provider
        self.api_key = api_key
        self.model_name = model_name
        self.system_prompt = (
            "You are a professional technical translator. Translate the following text "
            "from English to Russian. Preserve the original formatting structure (markdown). "
            "Do not add any explanations, just the translation. "
            "Keep technical terms accurate."
        )

    def translate(self, text):
        if not text.strip(): return ""
        try:
            if self.provider == "OpenAI":
                client = openai.OpenAI(api_key=self.api_key)
                response = client.chat.completions.create(
                    model=self.model_name,
                    messages=[{"role": "system", "content": self.system_prompt}, {"role": "user", "content": text}]
                )
                return response.choices[0].message.content

            elif self.provider == "Mistral":
                url = "https://api.mistral.ai/v1/chat/completions"
                headers = {"Authorization": f"Bearer {self.api_key}"}
                json_data = {"model": self.model_name,
                             "messages": [{"role": "user", "content": f"{self.system_prompt}\n\n{text}"}]}
                response = requests.post(url, headers=headers, json=json_data)
                response.raise_for_status()
                return response.json()["choices"][0]["message"]["content"]

            elif self.provider == "Gemini":
                genai.configure(api_key=self.api_key)
                model = genai.GenerativeModel(self.model_name)
                return model.generate_content(f"{self.system_prompt}\n\nTranslate:\n{text}").text

            elif self.provider == "OpenRouter":
                client = openai.OpenAI(base_url="https://openrouter.ai/api/v1", api_key=self.api_key)
                response = client.chat.completions.create(
                    model=self.model_name,
                    messages=[{"role": "system", "content": self.system_prompt}, {"role": "user", "content": text}]
                )
                return response.choices[0].message.content

            elif self.provider == "G4F (Free)":
                response = g4f.ChatCompletion.create(
                    model=self.model_name or g4f.models.gpt_4,
                    messages=[{"role": "user", "content": f"{self.system_prompt}\n\n{text}"}],
                )
                return str(response)

        except Exception as e:
            return f"[ОШИБКА]: {str(e)}"
        return "[Ошибка]"


# ================= 3. ПОТОК СКАНИРОВАНИЯ МОДЕЛЕЙ =================

class ModelFetcherWorker(QThread):
    models_found = pyqtSignal(list)
    error_occurred = pyqtSignal(str)

    def __init__(self, provider, api_key):
        super().__init__()
        self.provider = provider
        self.api_key = api_key

    def run(self):
        try:
            models = []
            if self.provider == "OpenAI":
                client = openai.OpenAI(api_key=self.api_key)
                # Фильтруем, берем только gpt модели
                models = [m.id for m in client.models.list() if "gpt" in m.id]
                models.sort(reverse=True)

            elif self.provider == "Mistral":
                url = "https://api.mistral.ai/v1/models"
                headers = {"Authorization": f"Bearer {self.api_key}"}
                resp = requests.get(url, headers=headers)
                resp.raise_for_status()
                models = [m["id"] for m in resp.json()["data"]]

            elif self.provider == "Gemini":
                genai.configure(api_key=self.api_key)
                # Фильтруем только те, что умеют генерировать контент
                models = [m.name.replace("models/", "") for m in genai.list_models()
                          if 'generateContent' in m.supported_generation_methods]

            elif self.provider == "OpenRouter":
                # OpenRouter имеет endpoint /models
                resp = requests.get("https://openrouter.ai/api/v1/models")
                if resp.status_code == 200:
                    data = resp.json()
                    # OpenRouter возвращает много данных, берем id
                    models = [m["id"] for m in data["data"]]
                    models.sort()

            elif self.provider == "G4F (Free)":
                # Берем список из библиотеки
                # g4f.models - это объект, нужно вытащить имена
                # Основные рабочие модели
                models = [
                    "gpt-4", "gpt-4o", "gpt-3.5-turbo",
                    "gemini-pro", "mixtral-8x7b",
                    "claude-3-opus", "claude-3-sonnet"
                ]
                # Можно попробовать добавить все из _all_models, но их слишком много мусорных

            if models:
                self.models_found.emit(models)
            else:
                self.error_occurred.emit("Список моделей пуст")

        except Exception as e:
            self.error_occurred.emit(str(e))


# ================= 4. ПОТОК ПЕРЕВОДА =================

class TranslatorWorker(QThread):
    progress_update = pyqtSignal(int, int)
    page_translated = pyqtSignal(int, str)
    error_occurred = pyqtSignal(str)
    finished_task = pyqtSignal()

    def __init__(self, pdf_path, engine, start_page=0):
        super().__init__()
        self.pdf_path = pdf_path
        self.engine = engine
        self.start_page = start_page
        self.is_running = True

    def run(self):
        try:
            doc = fitz.open(self.pdf_path)
            total = len(doc)
            for i in range(self.start_page, total):
                if not self.is_running: break

                # Извлекаем текст
                page = doc.load_page(i)
                text = ""
                blocks = page.get_text("blocks", sort=True)
                for b in blocks: text += b[4] + "\n\n"

                if not text.strip():
                    trans = "[Нет текста]"
                else:
                    trans = self.engine.translate(text)

                self.page_translated.emit(i, trans)
                self.progress_update.emit(i + 1, total)

            doc.close()
            self.finished_task.emit()
        except Exception as e:
            self.error_occurred.emit(str(e))

    def stop(self):
        self.is_running = False


# ================= 5. ГЛАВНОЕ ОКНО =================

class PDFTranslatorApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("AI PDF Translator v0.2")
        self.resize(1280, 850)

        self.pdf_doc = None
        self.translated_pages = {}
        self.current_page = 0

        self.init_ui()
        self.setup_shortcuts()

    def init_ui(self):
        main = QWidget()
        self.setCentralWidget(main)
        layout = QVBoxLayout(main)

        # --- БЛОК НАСТРОЕК ---
        settings_box = QGroupBox("Параметры AI")
        h_layout = QHBoxLayout()

        self.combo_provider = QComboBox()
        self.combo_provider.addItems(["OpenAI", "Mistral", "Gemini", "OpenRouter", "G4F (Free)"])
        self.combo_provider.currentTextChanged.connect(self.on_provider_change)

        self.input_key = QLineEdit()
        self.input_key.setPlaceholderText("API Key")
        self.input_key.setEchoMode(QLineEdit.Password)

        # Теперь это ComboBox
        self.combo_model = QComboBox()
        self.combo_model.setEditable(True)  # Можно писать руками
        self.combo_model.setPlaceholderText("Выберите или введите модель")

        # Кнопка сканирования
        self.btn_scan = QPushButton("🔄")
        self.btn_scan.setToolTip("Сканировать доступные модели")
        self.btn_scan.setFixedWidth(40)
        self.btn_scan.clicked.connect(self.scan_models)

        h_layout.addWidget(QLabel("Провайдер:"))
        h_layout.addWidget(self.combo_provider)
        h_layout.addWidget(QLabel("Ключ:"))
        h_layout.addWidget(self.input_key)
        h_layout.addWidget(QLabel("Модель:"))
        h_layout.addWidget(self.combo_model)
        h_layout.addWidget(self.btn_scan)

        settings_box.setLayout(h_layout)
        layout.addWidget(settings_box)

        # --- ТУЛБАР ---
        toolbar = QHBoxLayout()
        self.btn_open = QPushButton("📂 Открыть PDF")
        self.btn_open.clicked.connect(self.open_pdf)

        self.btn_start = QPushButton("▶️ Старт")
        self.btn_start.clicked.connect(self.start_translation)
        self.btn_start.setEnabled(False)

        self.btn_stop = QPushButton("⏹ Стоп")
        self.btn_stop.clicked.connect(self.stop_translation)
        self.btn_stop.setEnabled(False)

        self.btn_save = QPushButton("💾 Сохранить")
        self.btn_save.clicked.connect(self.save_translation)
        self.btn_save.setEnabled(False)

        toolbar.addWidget(self.btn_open)
        toolbar.addWidget(self.btn_start)
        toolbar.addWidget(self.btn_stop)
        toolbar.addWidget(self.btn_save)
        toolbar.addStretch()
        layout.addLayout(toolbar)

        # --- РАБОЧАЯ ЗОНА ---
        self.splitter = QSplitter(Qt.Horizontal)

        # Левая часть - PDF Viewer (кастомный виджет)
        left_container = QWidget()
        lc_layout = QVBoxLayout(left_container)
        lc_layout.addWidget(QLabel("<b>Оригинал</b> (Ctrl + Wheel для зума)"))

        self.pdf_viewer = PDFViewerWidget()
        lc_layout.addWidget(self.pdf_viewer)

        # Правая часть - Текст
        right_container = QWidget()
        rc_layout = QVBoxLayout(right_container)
        rc_layout.addWidget(QLabel("<b>Перевод</b>"))

        self.text_editor = QTextEdit()
        self.text_editor.setStyleSheet("font-size: 14px; font-family: Segoe UI;")
        rc_layout.addWidget(self.text_editor)

        self.splitter.addWidget(left_container)
        self.splitter.addWidget(right_container)
        self.splitter.setStretchFactor(0, 1)
        self.splitter.setStretchFactor(1, 1)

        layout.addWidget(self.splitter, stretch=1)

        # --- НАВИГАЦИЯ ---
        nav_layout = QHBoxLayout()
        self.btn_prev = QPushButton("<< Назад")
        self.btn_prev.clicked.connect(lambda: self.change_page(-1))
        self.btn_next = QPushButton("Вперед >>")
        self.btn_next.clicked.connect(lambda: self.change_page(1))
        self.lbl_page = QLabel("Стр: 0/0")

        nav_layout.addWidget(self.btn_prev)
        nav_layout.addWidget(self.lbl_page)
        nav_layout.addWidget(self.btn_next)
        layout.addLayout(nav_layout)

        # --- СТАТУС ---
        self.progress = QProgressBar()
        layout.addWidget(self.progress)
        self.status = QLabel("Готов")
        layout.addWidget(self.status)

        # Установка дефолтных моделей
        self.on_provider_change("OpenAI")

    def setup_shortcuts(self):
        # Горячие клавиши для зума
        self.shortcut_zoom_in = QShortcut(QKeySequence("Ctrl+="), self)
        self.shortcut_zoom_in.activated.connect(self.pdf_viewer.zoom_in)

        self.shortcut_zoom_out = QShortcut(QKeySequence("Ctrl+-"), self)
        self.shortcut_zoom_out.activated.connect(self.pdf_viewer.zoom_out)

    # --- ЛОГИКА GUI ---

    def on_provider_change(self, text):
        self.combo_model.clear()
        self.input_key.setEnabled(True)
        self.input_key.setPlaceholderText("Введите API Key")

        if text == "OpenAI":
            self.combo_model.addItem("gpt-4o")
            self.combo_model.addItem("gpt-3.5-turbo")
        elif text == "Mistral":
            self.combo_model.addItem("mistral-large-latest")
        elif text == "Gemini":
            self.combo_model.addItem("gemini-1.5-pro")
        elif text == "OpenRouter":
            self.combo_model.addItem("anthropic/claude-3-opus")
        elif text == "G4F (Free)":
            self.input_key.setEnabled(False)
            self.input_key.setPlaceholderText("Ключ не нужен")
            self.combo_model.addItems(["gpt-4", "gpt-4o", "gemini-pro"])

    def scan_models(self):
        provider = self.combo_provider.currentText()
        key = self.input_key.text().strip()

        if provider != "G4F (Free)" and not key:
            QMessageBox.warning(self, "Ошибка", "Для сканирования нужен API Key!")
            return

        self.status.setText(f"Сканирование моделей {provider}...")
        self.btn_scan.setEnabled(False)
        self.combo_provider.setEnabled(False)

        self.fetcher = ModelFetcherWorker(provider, key)
        self.fetcher.models_found.connect(self.on_models_found)
        self.fetcher.error_occurred.connect(self.on_scan_error)
        self.fetcher.start()

    def on_models_found(self, models):
        self.combo_model.clear()
        self.combo_model.addItems(models)
        self.status.setText(f"Найдено {len(models)} моделей.")
        self.btn_scan.setEnabled(True)
        self.combo_provider.setEnabled(True)
        QMessageBox.information(self, "Успех", f"Список моделей обновлен ({len(models)} шт.)")

    def on_scan_error(self, err):
        self.status.setText("Ошибка сканирования")
        self.btn_scan.setEnabled(True)
        self.combo_provider.setEnabled(True)
        QMessageBox.warning(self, "Ошибка API", f"Не удалось получить список моделей:\n{err}")

    def open_pdf(self):
        path, _ = QFileDialog.getOpenFileName(self, "PDF", "", "*.pdf")
        if path:
            self.pdf_path = path
            try:
                self.pdf_doc = fitz.open(path)
                self.translated_pages = {}
                self.current_page = 0
                self.update_view()
                self.btn_start.setEnabled(True)
                self.status.setText(f"Файл: {os.path.basename(path)}")
                self.progress.setValue(0)
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", str(e))

    def update_view(self):
        if not self.pdf_doc: return

        # Рендер PDF через наш крутой виджет
        page = self.pdf_doc.load_page(self.current_page)
        self.pdf_viewer.set_page(page)

        # Текст
        txt = self.translated_pages.get(self.current_page, "")
        if not txt:
            self.text_editor.setPlaceholderText("Ожидание перевода...")
            self.text_editor.clear()
        else:
            self.text_editor.setPlainText(txt)

        self.lbl_page.setText(f"Стр: {self.current_page + 1}/{len(self.pdf_doc)}")

    def change_page(self, delta):
        if not self.pdf_doc: return
        new_p = self.current_page + delta
        if 0 <= new_p < len(self.pdf_doc):
            self.current_page = new_p
            self.update_view()

    def start_translation(self):
        provider = self.combo_provider.currentText()
        key = self.input_key.text().strip()
        model = self.combo_model.currentText().strip()

        if provider != "G4F (Free)" and not key:
            QMessageBox.warning(self, "Ключ?", "Введите API Key!")
            return

        self.btn_start.setEnabled(False)
        self.btn_stop.setEnabled(True)
        self.combo_provider.setEnabled(False)
        self.combo_model.setEnabled(False)
        self.input_key.setEnabled(False)

        engine = LLMEngine(provider, key, model)
        self.worker = TranslatorWorker(self.pdf_path, engine)
        self.worker.page_translated.connect(self.on_page_done)
        self.worker.progress_update.connect(self.update_progress)
        self.worker.finished_task.connect(self.on_finished)
        self.worker.error_occurred.connect(self.on_error)
        self.worker.start()

    def stop_translation(self):
        if hasattr(self, 'worker'):
            self.worker.stop()
            self.status.setText("Прервано пользователем")

    def on_page_done(self, idx, text):
        self.translated_pages[idx] = text
        if self.current_page == idx:
            self.text_editor.setPlainText(text)

    def update_progress(self, curr, total):
        self.progress.setMaximum(total)
        self.progress.setValue(curr)
        self.status.setText(f"Перевод: {curr}/{total}")

    def on_finished(self):
        self.status.setText("Готово!")
        self.reset_controls()
        self.btn_save.setEnabled(True)

    def on_error(self, err):
        self.status.setText("Ошибка!")
        self.reset_controls()
        QMessageBox.critical(self, "Ошибка перевода", err)

    def reset_controls(self):
        self.btn_start.setEnabled(True)
        self.btn_stop.setEnabled(False)
        self.combo_provider.setEnabled(True)
        self.combo_model.setEnabled(True)
        self.input_key.setEnabled(self.combo_provider.currentText() != "G4F (Free)")

    def save_translation(self):
        path, _ = QFileDialog.getSaveFileName(self, "Сохранить", "", "Markdown (*.md);;Text (*.txt)")
        if path:
            try:
                with open(path, 'w', encoding='utf-8') as f:
                    for i in sorted(self.translated_pages.keys()):
                        f.write(f"## Страница {i + 1}\n\n{self.translated_pages[i]}\n\n---\n\n")
                QMessageBox.information(self, "ОК", "Сохранено")
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", str(e))


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setFont(QFont("Segoe UI", 10))
    w = PDFTranslatorApp()
    w.show()
    sys.exit(app.exec_())