# conda activate rtts

# pip install PyQt5 asyncio sounddevice numpy RealtimeSTT RealtimeTTS g4f

'''
ОШИБКИ:
- долго запускается
-❌ Ошибка инициализации STT: One or more keywords are not available by default.
Available default keywords are:\nok google, hey google, grapefruit, jarvis, porcupine, grasshopper, picovoice, computer,
bumblebee, blueberry, pico clock, alexa, hey siri, terminator, americano
-
'''


import sys
import asyncio
import json
import os
import threading
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QTextEdit, QPushButton,
    QVBoxLayout, QWidget, QLabel, QHBoxLayout
)
from PyQt5.QtCore import pyqtSignal, QObject, Qt
import sounddevice as sd
import numpy as np
from RealtimeSTT import AudioToTextRecorder
from RealtimeTTS import TextToAudioStream, SystemEngine
import g4f
from g4f.client import Client

# ========================
# Конфигурация
# ========================
KEYWORD = "джарвис"
HISTORY_FILE = "dialog_history.json"
SAMPLE_RATE = 16000
BLOCK_SIZE = 1024

# ========================
# Асинхронный обработчик для PyQt
# ========================
class AsyncHelper(QObject):
    finished = pyqtSignal(object)

    def __init__(self, coroutine):
        super().__init__()
        self.coroutine = coroutine

    def run(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result = loop.run_until_complete(self.coroutine)
            self.finished.emit(result)
        except Exception as e:
            self.finished.emit(e)
        finally:
            loop.close()

# ========================
# Основной класс ассистента
# ========================
class JarvisAssistant(QMainWindow):
    update_log_signal = pyqtSignal(str)
    update_status_signal = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Голосовой Ассистент Джарвис")
        self.setGeometry(100, 100, 600, 500)
        self.is_listening = False
        self.dialog_history = self.load_history()
        self.recorder = None
        self.tts_engine = SystemEngine()
        self.tts_stream = TextToAudioStream(self.tts_engine)
        self.client = Client()

        # Инициализация GUI
        self.init_ui()
        self.update_log_signal.connect(self.append_log)
        self.update_status_signal.connect(self.set_status)

        # Запуск фонового асинхронного слушателя
        self.start_background_listener()

    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout()

        # Лог диалога
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        layout.addWidget(self.log_text)

        # Статус
        self.status_label = QLabel("Статус: Ожидание...")
        self.status_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.status_label)

        # Кнопка управления
        button_layout = QHBoxLayout()
        self.toggle_button = QPushButton("Начать прослушивание")
        self.toggle_button.clicked.connect(self.toggle_listening)
        button_layout.addWidget(self.toggle_button)

        layout.addLayout(button_layout)
        central_widget.setLayout(layout)

    def set_status(self, text):
        self.status_label.setText(f"Статус: {text}")

    def append_log(self, text):
        self.log_text.append(text)

    def toggle_listening(self):
        self.is_listening = not self.is_listening
        self.toggle_button.setText(
            "Остановить прослушивание" if self.is_listening else "Начать прослушивание"
        )
        if self.is_listening:
            self.update_log_signal.emit("<b>🎙️ Система активна. Говорите 'Джарвис' для активации.</b>")
        else:
            self.update_log_signal.emit("<i>🔇 Прослушивание остановлено.</i>")

    def load_history(self):
        if os.path.exists(HISTORY_FILE):
            try:
                with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Ошибка загрузки истории: {e}")
                return []
        return []

    def save_history(self):
        try:
            with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.dialog_history, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Ошибка сохранения истории: {e}")

    def start_background_listener(self):
        thread = threading.Thread(target=self.run_async_listener, daemon=True)
        thread.start()

    def run_async_listener(self):
        asyncio.run(self.background_listener())

    async def background_listener(self):
        try:
            self.recorder = AudioToTextRecorder(
                model="base",
                language="ru",
                wake_words=KEYWORD,
                wake_word_activation_delay=0.5,
                enable_realtime_transcription=True,
                realtime_processing_pause=0.5
            )
        except Exception as e:
            self.update_log_signal.emit(f"<b>❌ Ошибка инициализации STT: {e}</b>")
            return

        self.update_status_signal.emit("Ожидание ключевого слова...")
        while True:
            if not self.is_listening:
                await asyncio.sleep(0.5)
                continue

            try:
                self.update_status_signal.emit("Слушаю 'Джарвис'...")
                text = await asyncio.to_thread(self.recorder.text)
                if not text.strip():
                    continue

                self.update_log_signal.emit(f"<b>👂 Распознано:</b> {text}")

                if KEYWORD in text.lower():
                    await self.handle_query()
                else:
                    self.update_status_signal.emit("Ожидаю 'Джарвис'...")

            except Exception as e:
                self.update_log_signal.emit(f"<b>⚠️ Ошибка распознавания: {e}</b>")
                await asyncio.sleep(1)

    async def handle_query(self):
        self.update_status_signal.emit("Записываю ваш вопрос...")
        self.update_log_signal.emit("<i>🎙️ Говорите ваш вопрос...</i>")

        try:
            # Очищаем буфер после активации
            self.recorder.stop()
            await asyncio.sleep(0.2)
            self.recorder.start()

            question = await asyncio.to_thread(self.recorder.text)
            if not question.strip():
                self.update_log_signal.emit("<i>❓ Не удалось распознать вопрос.</i>")
                self.update_status_signal.emit("Ожидаю 'Джарвис'...")
                return

            self.update_log_signal.emit(f"<b>Вы:</b> {question}")
            self.dialog_history.append({"role": "user", "content": question})

            # Отправка в LLM
            self.update_status_signal.emit("Думаю...")
            answer = await self.get_llm_response(question)

            self.update_log_signal.emit(f"<b>Джарвис:</b> {answer}")
            self.dialog_history.append({"role": "assistant", "content": answer})
            self.save_history()

            # Произнесение ответа
            self.update_status_signal.emit("Говорю ответ...")
            await asyncio.to_thread(self.speak, answer)

            self.update_status_signal.emit("Ожидаю 'Джарвис'...")

        except Exception as e:
            self.update_log_signal.emit(f"<b>❌ Ошибка обработки: {e}</b>")
            self.update_status_signal.emit("Ожидаю 'Джарвис'...")

    async def get_llm_response(self, question: str) -> str:
        try:
            messages = [
                {"role": "system", "content": "Ты — Джарвис, вежливый и умный голосовой ассистент. Отвечай кратко, ясно и по делу."},
            ] + self.dialog_history + [
                {"role": "user", "content": question}
            ]

            response = await asyncio.to_thread(
                self.client.chat.completions.create,
                model="deepseek-r1-0528-turbo",
                messages=messages,
                temperature=0.7,
                max_tokens=500
            )

            return response.choices[0].message.content.strip()

        except Exception as e:
            return f"Произошла ошибка при генерации ответа: {str(e)}"

    def speak(self, text: str):
        try:
            if self.tts_stream.is_playing():
                self.tts_stream.stop()
            self.tts_stream.feed(text)
            self.tts_stream.play()
        except Exception as e:
            print(f"Ошибка TTS: {e}")

    def closeEvent(self, event):
        self.save_history()
        if self.recorder:
            self.recorder.shutdown()
        event.accept()

# ========================
# Запуск приложения
# ========================
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = JarvisAssistant()
    window.show()
    sys.exit(app.exec_())