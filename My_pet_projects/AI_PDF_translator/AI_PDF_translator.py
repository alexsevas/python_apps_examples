'''
Интерфейс: Окно разделено на две части. Слева — картинка оригинальной страницы PDF. Справа — редактируемое поле с переводом.
Логика: Мы извлекаем текст из PDF блоками, отправляем в LLM, получаем перевод и отображаем справа.
Бэкенд: Реализуем абстрактный класс-обертку для переключения между OpenAI, Mistral, Gemini, OpenRouter и g4f.

1.Архитектура "Слева оригинал - Справа перевод":
Почему так? Пытаться сгенерировать новый PDF с точным сохранением верстки, заменяя английский текст на русский — это невероятно сложная задача. Текст на русском обычно длиннее на 20-30%, он "поедет", наедет на картинки и таблицы.
Решение: CAT-tool подход (Side-by-side) позволяет пользователю видеть оригинальный контекст (графики, схемы) слева и читать чистый текст справа.
2.Многопоточность (QThread):
Весь процесс общения с API вынесен в класс TranslatorWorker. Это гарантирует, что GUI не зависнет ("Не отвечает"), даже если сервер OpenAI думает над ответом 30 секунд.
Используются pyqtSignal для безопасной передачи данных из потока в интерфейс.
3.Универсальный движок (LLMEngine):
Реализована поддержка 5 провайдеров, как вы просили.
Для OpenRouter используется клиент OpenAI с измененным base_url.
Для g4f реализована обертка, но учтите, что бесплатные библиотеки часто нестабильны.
Для Mistral используется прямой REST API запрос.
4.бработка PDF:
Используется pymupdf (fitz).
Для текста: page.get_text("blocks") — это позволяет извлекать текст абзацами, а не рваными строками, что критически важно для качества перевода нейросетью.
Для картинки: page.get_pixmap() — рендерит страницу в высоком качестве для левой панели.
5.Дополнительные фичи:
Кэширование: Переведенные страницы сохраняются в памяти (self.translated_pages). Если вы вернетесь на страницу назад, она не будет переводиться заново.
Живой просмотр: Если вы находитесь на странице 5, и поток только что закончил переводить страницу 5, текст в редакторе обновится автоматически.
Редактирование: Поле справа — это QTextEdit. Вы можете править перевод руками, если нейросеть ошиблась, перед сохранением.
Сохранение: Результат можно выгрузить в Markdown файл, где страницы разделены заголовками.
'''

# pip install PyQt5 pymupdf openai google-generativeai g4f requests markdown2


import sys
import os
import time
import requests
import fitz  # PyMuPDF
import markdown2

from PyQt5.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QHBoxLayout,
                             QWidget, QTextEdit, QPushButton, QLabel, QProgressBar,
                             QComboBox, QLineEdit, QSplitter, QFileDialog, QMessageBox,
                             QGroupBox, QFormLayout, QSpinBox)
from PyQt5.QtCore import QThread, pyqtSignal, Qt, QSize
from PyQt5.QtGui import QImage, QPixmap, QFont

# Импорты API
import openai
import google.generativeai as genai
import g4f

# ================= ЛОГИКА LLM (БЭКЕНД) =================

class LLMEngine:
    def __init__(self, provider, api_key, model_name):
        self.provider = provider
        self.api_key = api_key
        self.model_name = model_name

        # Системный промпт для технического перевода
        self.system_prompt = (
            "You are a professional technical translator. Translate the following text "
            "from English to Russian. Preserve the original formatting structure (markdown). "
            "Do not add any explanations, just the translation. "
            "Keep technical terms accurate."
        )

    def translate(self, text):
        if not text.strip():
            return ""

        try:
            if self.provider == "OpenAI":
                client = openai.OpenAI(api_key=self.api_key)
                response = client.chat.completions.create(
                    model=self.model_name,
                    messages=[
                        {"role": "system", "content": self.system_prompt},
                        {"role": "user", "content": text}
                    ]
                )
                return response.choices[0].message.content

            elif self.provider == "Mistral":
                url = "https://api.mistral.ai/v1/chat/completions"
                headers = {"Authorization": f"Bearer {self.api_key}"}
                json_data = {
                    "model": self.model_name,
                    "messages": [{"role": "user", "content": f"{self.system_prompt}\n\nText:\n{text}"}]
                }
                response = requests.post(url, headers=headers, json=json_data)
                response.raise_for_status()
                return response.json()["choices"][0]["message"]["content"]

            elif self.provider == "Gemini":
                genai.configure(api_key=self.api_key)
                model = genai.GenerativeModel(self.model_name)
                # Gemini иногда капризен к системным промптам, подаем в user message
                full_prompt = f"{self.system_prompt}\n\nTranslate this:\n{text}"
                response = model.generate_content(full_prompt)
                return response.text

            elif self.provider == "OpenRouter":
                # OpenRouter совместим с OpenAI client, нужно только поменять base_url
                client = openai.OpenAI(
                    base_url="https://openrouter.ai/api/v1",
                    api_key=self.api_key,
                )
                response = client.chat.completions.create(
                    model=self.model_name,
                    messages=[
                        {"role": "system", "content": self.system_prompt},
                        {"role": "user", "content": text}
                    ]
                )
                return response.choices[0].message.content

            elif self.provider == "G4F (Free)":
                # G4F не требует ключа, но требует выбора провайдера (Auto)
                response = g4f.ChatCompletion.create(
                    model=self.model_name or g4f.models.gpt_4,
                    messages=[{"role": "user", "content": f"{self.system_prompt}\n\n{text}"}],
                )
                return str(response)

        except Exception as e:
            return f"[ОШИБКА ПЕРЕВОДА]: {str(e)}"

        return "[Неизвестная ошибка]"

# ================= ПОТОК ПЕРЕВОДА =================

class TranslatorWorker(QThread):
    progress_update = pyqtSignal(int, int) # текущая, всего
    page_translated = pyqtSignal(int, str) # номер страницы, текст
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
            total_pages = len(doc)

            for page_num in range(self.start_page, total_pages):
                if not self.is_running:
                    break

                page = doc.load_page(page_num)
                # Получаем текст блоками, чтобы сохранить хоть какую-то структуру
                # sort=True пытается упорядочить колонки
                text_blocks = page.get_text("blocks", sort=True)

                full_page_translation = ""

                # Собираем текст страницы
                raw_text = ""
                for block in text_blocks:
                    # block[4] - это текст
                    raw_text += block[4] + "\n\n"

                # Если страница пустая (например, картинка без OCR)
                if not raw_text.strip():
                    full_page_translation = "[Текст не найден или это изображение]"
                else:
                    # Переводим
                    # Можно добавить разбивку на чанки, если страница огромная,
                    # но обычно 1 страница PDF влезает в контекст современных моделей.
                    full_page_translation = self.engine.translate(raw_text)

                self.page_translated.emit(page_num, full_page_translation)
                self.progress_update.emit(page_num + 1, total_pages)

                # Небольшая пауза, чтобы не дудосить API
                time.sleep(0.5)

            doc.close()
            self.finished_task.emit()

        except Exception as e:
            self.error_occurred.emit(str(e))

    def stop(self):
        self.is_running = False

# ================= ГЛАВНОЕ ОКНО =================

class PDFTranslatorApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("AI PDF Translator Pro (PyQt5)")
        self.resize(1200, 800)

        # Хранение данных
        self.pdf_doc = None
        self.pdf_path = ""
        self.translated_pages = {} # кэш: {page_num: text}
        self.current_page = 0
        self.worker = None

        self.init_ui()

    def init_ui(self):
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QVBoxLayout(main_widget)

        # 1. Панель настроек
        settings_group = QGroupBox("Настройки нейросети")
        settings_layout = QHBoxLayout()

        self.combo_provider = QComboBox()
        self.combo_provider.addItems(["OpenAI", "Mistral", "Gemini", "OpenRouter", "G4F (Free)"])
        self.combo_provider.currentTextChanged.connect(self.on_provider_change)

        self.input_key = QLineEdit()
        self.input_key.setPlaceholderText("API Key")
        self.input_key.setEchoMode(QLineEdit.Password)

        self.input_model = QLineEdit()
        self.input_model.setPlaceholderText("Model (e.g. gpt-4o, gemini-pro)")
        self.input_model.setText("gpt-4o") # default

        settings_layout.addWidget(QLabel("Провайдер:"))
        settings_layout.addWidget(self.combo_provider)
        settings_layout.addWidget(QLabel("Ключ:"))
        settings_layout.addWidget(self.input_key)
        settings_layout.addWidget(QLabel("Модель:"))
        settings_layout.addWidget(self.input_model)

        settings_group.setLayout(settings_layout)
        main_layout.addWidget(settings_group)

        # 2. Панель управления файлом
        file_toolbar = QHBoxLayout()

        self.btn_open = QPushButton("📂 Открыть PDF")
        self.btn_open.clicked.connect(self.open_pdf)

        self.btn_start = QPushButton("▶️ Начать перевод")
        self.btn_start.clicked.connect(self.start_translation)
        self.btn_start.setEnabled(False)

        self.btn_stop = QPushButton("⏹ Стоп")
        self.btn_stop.clicked.connect(self.stop_translation)
        self.btn_stop.setEnabled(False)

        self.btn_save = QPushButton("💾 Сохранить перевод")
        self.btn_save.clicked.connect(self.save_translation)
        self.btn_save.setEnabled(False)

        file_toolbar.addWidget(self.btn_open)
        file_toolbar.addWidget(self.btn_start)
        file_toolbar.addWidget(self.btn_stop)
        file_toolbar.addWidget(self.btn_save)
        file_toolbar.addStretch()

        main_layout.addLayout(file_toolbar)

        # 3. Рабочая область (Splitter)
        self.splitter = QSplitter(Qt.Horizontal)

        # Левая часть - Оригинал (Картинка)
        self.left_widget = QWidget()
        l_layout = QVBoxLayout(self.left_widget)
        l_layout.addWidget(QLabel("<b>Оригинал</b>"))
        self.lbl_pdf_image = QLabel("Загрузите PDF")
        self.lbl_pdf_image.setAlignment(Qt.AlignCenter)
        self.lbl_pdf_image.setStyleSheet("background-color: #eee; border: 1px solid #ccc;")
        l_layout.addWidget(self.lbl_pdf_image)

        # Правая часть - Перевод (Текст)
        self.right_widget = QWidget()
        r_layout = QVBoxLayout(self.right_widget)
        r_layout.addWidget(QLabel("<b>Перевод (Markdown)</b>"))
        self.text_editor = QTextEdit()
        self.text_editor.setReadOnly(False) # Можно править вручную
        self.text_editor.setStyleSheet("font-size: 14px; font-family: Segoe UI;")
        r_layout.addWidget(self.text_editor)

        self.splitter.addWidget(self.left_widget)
        self.splitter.addWidget(self.right_widget)
        self.splitter.setStretchFactor(0, 1)
        self.splitter.setStretchFactor(1, 1)

        main_layout.addWidget(self.splitter, stretch=1)

        # 4. Навигация по страницам
        nav_layout = QHBoxLayout()
        self.btn_prev = QPushButton("<< Пред.")
        self.btn_prev.clicked.connect(lambda: self.change_page(-1))
        self.btn_next = QPushButton("След. >>")
        self.btn_next.clicked.connect(lambda: self.change_page(1))
        self.lbl_page_info = QLabel("Стр: 0 / 0")

        nav_layout.addWidget(self.btn_prev)
        nav_layout.addWidget(self.lbl_page_info)
        nav_layout.addWidget(self.btn_next)

        main_layout.addLayout(nav_layout)

        # 5. Прогресс
        self.progress_bar = QProgressBar()
        main_layout.addWidget(self.progress_bar)

        self.status_bar = QLabel("Готов к работе")
        main_layout.addWidget(self.status_bar)

    # --- Обработчики ---

    def on_provider_change(self, text):
        # Дефолтные модели для удобства
        if text == "OpenAI":
            self.input_model.setText("gpt-4o")
            self.input_key.setEnabled(True)
        elif text == "Mistral":
            self.input_model.setText("mistral-large-latest")
            self.input_key.setEnabled(True)
        elif text == "Gemini":
            self.input_model.setText("gemini-2.5-pro")
            self.input_key.setEnabled(True)
        elif text == "OpenRouter":
            self.input_model.setText("anthropic/claude-3-opus")
            self.input_key.setEnabled(True)
        elif text == "G4F (Free)":
            self.input_model.setText("") # Auto
            self.input_key.setEnabled(False)
            self.input_key.setPlaceholderText("Ключ не нужен")

    def open_pdf(self):
        path, _ = QFileDialog.getOpenFileName(self, "Открыть PDF", "", "PDF Files (*.pdf)")
        if path:
            self.pdf_path = path
            try:
                self.pdf_doc = fitz.open(path)
                self.translated_pages = {}
                self.current_page = 0
                self.update_page_view()
                self.btn_start.setEnabled(True)
                self.status_bar.setText(f"Загружен: {os.path.basename(path)}")
                self.progress_bar.setValue(0)
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Не удалось открыть PDF: {e}")

    def update_page_view(self):
        if not self.pdf_doc:
            return

        # 1. Отображение оригинала (Рендер в картинку)
        page = self.pdf_doc.load_page(self.current_page)
        pix = page.get_pixmap(matrix=fitz.Matrix(1.5, 1.5)) # Zoom для четкости

        # Конвертация в QImage
        img_data = pix.tobytes("ppm")
        qimg = QImage.fromData(img_data)
        pixmap = QPixmap.fromImage(qimg)

        # Масштабирование под размер лейбла
        w = self.lbl_pdf_image.width()
        h = self.lbl_pdf_image.height()
        if w > 0 and h > 0:
            self.lbl_pdf_image.setPixmap(pixmap.scaled(w, h, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        else:
            self.lbl_pdf_image.setPixmap(pixmap)

        # 2. Отображение перевода
        if self.current_page in self.translated_pages:
            self.text_editor.setPlainText(self.translated_pages[self.current_page])
        else:
            self.text_editor.setPlaceholderText("Эта страница еще не переведена...")
            self.text_editor.clear()

        # 3. Инфо
        self.lbl_page_info.setText(f"Стр: {self.current_page + 1} / {len(self.pdf_doc)}")

        # Кнопки навигации
        self.btn_prev.setEnabled(self.current_page > 0)
        self.btn_next.setEnabled(self.current_page < len(self.pdf_doc) - 1)

    def change_page(self, delta):
        new_page = self.current_page + delta
        if 0 <= new_page < len(self.pdf_doc):
            self.current_page = new_page
            self.update_page_view()

    def resizeEvent(self, event):
        # Обновляем картинку при ресайзе окна
        self.update_page_view()
        super().resizeEvent(event)

    def start_translation(self):
        provider = self.combo_provider.currentText()
        key = self.input_key.text().strip()
        model = self.input_model.text().strip()

        if provider != "G4F (Free)" and not key:
            QMessageBox.warning(self, "Внимание", "Введите API Key!")
            return

        self.status_bar.setText("Инициализация перевода...")

        # Блокировка интерфейса
        self.btn_start.setEnabled(False)
        self.btn_stop.setEnabled(True)
        self.combo_provider.setEnabled(False)

        # Создаем движок
        engine = LLMEngine(provider, key, model)

        # Запускаем поток
        # Начинаем с текущей непереведенной, или с 0? Лучше с 0, но пропуская готовые.
        # В worker'е просто начнем с 0, а в callback будем сохранять.
        self.worker = TranslatorWorker(self.pdf_path, engine)
        self.worker.progress_update.connect(self.update_progress)
        self.worker.page_translated.connect(self.on_page_translated)
        self.worker.finished_task.connect(self.on_translation_finished)
        self.worker.error_occurred.connect(self.on_worker_error)

        self.worker.start()

    def stop_translation(self):
        if self.worker:
            self.worker.stop()
            self.status_bar.setText("Остановка...")

    def update_progress(self, current, total):
        self.progress_bar.setMaximum(total)
        self.progress_bar.setValue(current)
        self.status_bar.setText(f"Перевод страницы {current} из {total}...")

    def on_page_translated(self, page_num, text):
        self.translated_pages[page_num] = text

        # Если мы смотрим на эту страницу прямо сейчас, обновить текст
        if self.current_page == page_num:
            self.text_editor.setPlainText(text)

    def on_translation_finished(self):
        self.status_bar.setText("Перевод завершен!")
        self.btn_start.setEnabled(True)
        self.btn_stop.setEnabled(False)
        self.combo_provider.setEnabled(True)
        self.btn_save.setEnabled(True)
        QMessageBox.information(self, "Успех", "Документ полностью переведен!")

    def on_worker_error(self, err_msg):
        self.status_bar.setText("Ошибка!")
        self.btn_start.setEnabled(True)
        self.btn_stop.setEnabled(False)
        self.combo_provider.setEnabled(True)
        QMessageBox.critical(self, "Ошибка перевода", err_msg)

    def save_translation(self):
        path, _ = QFileDialog.getSaveFileName(self, "Сохранить перевод", "", "Markdown Files (*.md);;Text Files (*.txt)")
        if not path:
            return

        try:
            with open(path, 'w', encoding='utf-8') as f:
                for page_num in sorted(self.translated_pages.keys()):
                    f.write(f"## Страница {page_num + 1}\n\n")
                    f.write(self.translated_pages[page_num])
                    f.write("\n\n---\n\n")

            self.status_bar.setText(f"Сохранено в {path}")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка сохранения", str(e))

if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Настройка шрифтов для HighDPI
    font = QFont("Segoe UI", 9)
    app.setFont(font)

    window = PDFTranslatorApp()
    window.show()
    sys.exit(app.exec_())