

"""
Jarvis-like async voice assistant (single-file).
Requirements and instructions are below this file (README style).
Wake word "Джарвис"
"""

import asyncio
import json
import os
import tempfile
import time
from datetime import datetime
from pathlib import Path

import sounddevice as sd
import numpy as np
import soundfile as sf
import simpleaudio as sa  # playback
from vosk import Model as VoskModel, KaldiRecognizer
# Vosk-TTS (vosk-tts) - optional; fallback to pyttsx3 if not installed
try:
    from vosk_tts import Model as VoskTTSModel, Synth as VoskSynth
    HAS_VOSK_TTS = True
except Exception:
    HAS_VOSK_TTS = False

import whisper
import g4f  # g4f (gpt4free) — used with ChatCompletion.create

# GUI
from PyQt5 import QtWidgets, QtCore
import qasync

# -------------------
# Config
# -------------------
WAKE_WORD = "джарвис"  # на русском
SAMPLE_RATE = 16000
CHANNELS = 1
BLOCKSIZE = 1024  # frames per block
MEMORY_FILE = "assistant_memory.json"
VOSK_MODEL_PATH = "vosk-model-small-ru-0.22"  # пример - укажите путь к вашей модели VOSK
VOSK_TTS_MODEL_NAME = "vosk-model-tts-ru-0.9-multi"  # для vosk-tts
WHISPER_MODEL = "small"  # для CPU возможно лучше 'tiny' или 'base'
LLM_MODEL_NAME = "deepseek-r1-0528-turbo"  # модель g4f по запросу пользователя
MAX_COMMAND_SECONDS = 20  # максимальная длина записи команды после wake word
SILENCE_THRESHOLD = 500  # порог RMS для VAD (потребует калибровки)
SILENCE_SECONDS_TO_END = 0.8  # сколько секунд тишины, чтобы считать конец реплики

# -------------------
# Helper functions: memory
# -------------------
def load_memory(path=MEMORY_FILE):
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []
    return []


def save_memory(history, path=MEMORY_FILE):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=2)


# -------------------
# Assistant core
# -------------------
class VoiceAssistant:
    def __init__(self, gui_callback=None):
        # gui_callback: function(status_str) to update GUI log/status
        self.gui_callback = gui_callback
        self.running = False
        self.audio_queue = None  # will be asyncio.Queue
        self.vosk_model = None
        self.whisper_model = None
        self.tts_model = None
        self.history = load_memory()
        self.loop = asyncio.get_event_loop()
        self.recognizer = None

    async def init_models(self):
        # Load Vosk model (offline STT / wake-word)
        if not os.path.exists(VOSK_MODEL_PATH):
            self._log(f"VOSK model not found at {VOSK_MODEL_PATH}. Скачайте модель и распакуйте.")
            # raise FileNotFoundError
        else:
            self._log("Загружаю VOSK модель (offline STT / wake-word)...")
            self.vosk_model = VoskModel(VOSK_MODEL_PATH)
            # recognizer will be created per stream
        # Whisper
        self._log(f"Загружаю Whisper модель '{WHISPER_MODEL}' (может занять время)...")
        # Выполняем загрузку в потоке, т.к. это blocking
        self.whisper_model = await asyncio.to_thread(whisper.load_model, WHISPER_MODEL)
        self._log("Whisper загружен.")
        # VOSK-TTS
        if HAS_VOSK_TTS:
            try:
                self._log("Загружаю VOSK-TTS модель...")
                self.tts_model = VoskTTSModel(model_name=VOSK_TTS_MODEL_NAME)
                self.tts_synth = VoskSynth(self.tts_model)
                self._log("VOSK-TTS готов.")
            except Exception as e:
                self._log("Не удалось инициализировать VOSK-TTS: " + str(e))
                self.tts_model = None
        else:
            self._log("vosk-tts не установлен — будет использован pyttsx3 (если установлен).")

    def _log(self, text):
        ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        line = f"[{ts}] {text}"
        print(line)
        if callable(self.gui_callback):
            # send to GUI (non-blocking)
            try:
                self.loop.call_soon_threadsafe(self.gui_callback, line)
            except Exception:
                pass

    # -------------------
    # Audio I/O: starts the input stream and sets up queue/callback
    # -------------------
    async def start_listening_loop(self):
        if not self.vosk_model:
            await self.init_models()
        self.audio_queue = asyncio.Queue()
        self.running = True

        # create recognizer focused on wake-word grammar to reduce false positives
        # third parameter - optional grammar: use wake word only (helps spot)
        grammar = f'["{WAKE_WORD}"]'
        self.recognizer = KaldiRecognizer(self.vosk_model, SAMPLE_RATE, grammar)

        # get current loop for callback
        loop = asyncio.get_running_loop()
        self._log("Запуск аудио-потока микрофона...")

        def callback(indata, frames, time_info, status):
            # indata is numpy array with shape (frames, channels)
            # copy to avoid overwrite
            try:
                data_bytes = bytes(indata.copy().tobytes())
                loop.call_soon_threadsafe(self.audio_queue.put_nowait, data_bytes)
            except Exception:
                pass

        # InputStream with int16 dtype to match Vosk expectation
        try:
            self.stream = sd.InputStream(samplerate=SAMPLE_RATE, blocksize=BLOCKSIZE,
                                         dtype='int16', channels=CHANNELS, callback=callback)
            self.stream.start()
        except Exception as e:
            self._log("Ошибка при старте микрофона: " + str(e))
            raise

        self._log("Асинхронный процессор аудио стартует...")
        # запустить обработчик (не блокирует GUI)
        asyncio.create_task(self._audio_processor())

    async def stop_listening_loop(self):
        self.running = False
        # stop stream
        try:
            if hasattr(self, "stream"):
                self.stream.stop()
                self.stream.close()
        except Exception:
            pass
        self._log("Остановлен аудио поток.")

    # -------------------
    # Audio processing: detect wake-word then record command
    # -------------------
    async def _audio_processor(self):
        """
        Основной loop: берёт блоки из audio_queue и прогоняет через VOSK recognizer.
        При нахождении wake-word — запускает запись команды, трансформирует аудио и обрабатывает.
        """
        partial_hits = ""
        self._log("Начало прослушивания эфира (ждём wake-word)...")
        while self.running:
            try:
                data = await self.audio_queue.get()
            except asyncio.CancelledError:
                return
            if not data:
                continue
            # Vosk expects bytes with int16 pcm
            try:
                if self.recognizer.AcceptWaveform(data):
                    res = json.loads(self.recognizer.Result())
                    txt = res.get("text", "").strip().lower()
                    if txt:
                        self._log(f"VOSK result: {txt}")
                    if WAKE_WORD in txt:
                        # wake-word detected
                        self._log("Ключевое слово обнаружено — слушаю команду...")
                        # record command
                        wav_path = await self._record_command()
                        if wav_path:
                            # transcribe via whisper
                            self._log(f"Отправляю на транскрипцию Whisper: {wav_path}")
                            try:
                                whisper_res = await asyncio.to_thread(self.whisper_model.transcribe, wav_path, {"language": "ru"})
                                user_text = whisper_res.get("text", "").strip()
                            except Exception as e:
                                self._log("Ошибка при транскрибировании Whisper: " + str(e))
                                user_text = ""
                            if user_text:
                                self._log("Пользователь сказал: " + user_text)
                                # save to history
                                self._append_history("user", user_text)
                                # query LLM
                                assistant_text = await self._ask_llm(user_text)
                                if assistant_text:
                                    self._append_history("assistant", assistant_text)
                                    # synthesize and play
                                    await self._synthesize_and_play(assistant_text)
                                    save_memory(self.history)
                        # after finishing, continue listening
                    else:
                        # not wake word; continue
                        pass
                else:
                    # partial result
                    pr = json.loads(self.recognizer.PartialResult()).get("partial", "").lower()
                    # we can detect wake-word in partials too (faster)
                    if WAKE_WORD in pr and pr != partial_hits:
                        partial_hits = pr
                        self._log("Partial hit wake-word (partial): " + pr)
                        # we may choose to trigger immediately; here we continue until AcceptWaveform confirms
            except Exception as exc:
                self._log("Ошибка в аудио-обработчике: " + str(exc))
                await asyncio.sleep(0.1)

    async def _record_command(self):
        """
        Когда обнаружили wake-word — записываем последующую речь до тишины или MAX_SECONDS.
        Берём блоки из audio_queue.
        Возвращаем путь к WAV-файлу (16kHz PCM16) или None.
        """
        self._log("Начинаю запись команды до тишины или лимита.")
        frames = []
        start_time = time.time()
        silent_seconds = 0.0
        last_sound_time = time.time()
        while True:
            try:
                # ждём максимум 0.5 s для очередного блока
                data = await asyncio.wait_for(self.audio_queue.get(), timeout=2.0)
            except asyncio.TimeoutError:
                # если долго тишина — прервём
                if time.time() - last_sound_time > SILENCE_SECONDS_TO_END:
                    break
                else:
                    continue
            if not data:
                continue
            frames.append(data)
            # compute RMS on this block
            arr = np.frombuffer(data, dtype=np.int16)
            if arr.size == 0:
                rms = 0
            else:
                rms = int(np.sqrt(np.mean(arr.astype(np.float32) ** 2)))
            if rms > SILENCE_THRESHOLD:
                last_sound_time = time.time()
            # end conditions
            if time.time() - last_sound_time > SILENCE_SECONDS_TO_END:
                # пользователь замолк
                break
            if time.time() - start_time > MAX_COMMAND_SECONDS:
                self._log("Достигнут предел времени записи команды.")
                break
        if not frames:
            self._log("Не записано ни одного блока команды.")
            return None
        # merge frames and write to temp wav file
        merged = b"".join(frames)
        # convert bytes to numpy (int16)
        arr = np.frombuffer(merged, dtype=np.int16)
        # write wav
        tmp = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
        tmp_name = tmp.name
        tmp.close()
        try:
            sf.write(tmp_name, arr, SAMPLE_RATE, subtype='PCM_16')
            self._log(f"Команда записана во временный файл: {tmp_name}")
            return tmp_name
        except Exception as e:
            self._log("Ошибка записи WAV: " + str(e))
            return None

    async def _ask_llm(self, user_text: str) -> str:
        """
        Отправляет в g4f (gpt4free). Использует историю (memory) как контекст.
        Возвращает текст ответа (или пустую строку).
        """
        self._log("Отправляю запрос в LLM...")
        # prepare messages (history limited to last N messages)
        messages = []
        # load memory into messages
        max_entries = 20
        last_entries = self.history[-max_entries:]
        for item in last_entries:
            role = item.get("role")
            content = item.get("content")
            if role and content:
                messages.append({"role": role, "content": content})
        # add current user
        messages.append({"role": "user", "content": user_text})
        try:
            def blocking_call():
                # try primary g4f API
                try:
                    resp = g4f.ChatCompletion.create(
                        model=LLM_MODEL_NAME,
                        messages=messages,
                        # timeout может понадобиться больше
                        timeout=120
                    )
                    # resp может быть строкой или итератор
                    if isinstance(resp, str):
                        return resp
                    elif hasattr(resp, "__iter__"):
                        # собрать части
                        out = ""
                        for p in resp:
                            out += str(p)
                        return out
                    else:
                        return str(resp)
                except Exception as e:
                    return "Ошибка LLM: " + str(e)
            result = await asyncio.to_thread(blocking_call)
            # чистим результат от лишних управляющих символов
            if result is None:
                return ""
            # Если g4f возвращает JSON-like, пробуем извлечь 'content'
            # Но большинство реализаций дают plain text
            res_text = str(result).strip()
            self._log("LLM ответ: " + (res_text[:200] + ("..." if len(res_text) > 200 else "")))
            return res_text
        except Exception as e:
            self._log("Ошибка при общении с LLM: " + str(e))
            return ""

    async def _synthesize_and_play(self, text: str):
        """
        Синтезируем ответ в WAV и воспроизводим (не блокируем GUI).
        Используем vosk-tts если установлен, иначе пытаемся pyttsx3.
        """
        if not text:
            return
        self._log("Синтез речи для ответа...")
        tmp = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
        out_wav = tmp.name
        tmp.close()
        try:
            if HAS_VOSK_TTS and self.tts_model:
                # blocking synth
                await asyncio.to_thread(self.tts_synth.synth, text, out_wav, 2)  # speaker_id — пример
            else:
                # fallback: pyttsx3 (if installed). pyttsx3 может работать по-разному по платформам
                try:
                    import pyttsx3
                    def tts_block():
                        engine = pyttsx3.init()
                        # установить голос и скорость можно здесь
                        engine.save_to_file(text, out_wav)
                        engine.runAndWait()
                    await asyncio.to_thread(tts_block)
                except Exception as e:
                    self._log("Отсутствует TTS движок: " + str(e))
                    return
            # воспроизведение (не блокирующее)
            try:
                wave_obj = sa.WaveObject.from_wave_file(out_wav)
                play_obj = wave_obj.play()
                # не ждём завершения (асинхронно можно дождаться play_obj.wait_done() при необходимости)
                self._log("Воспроизведение ответа запущено.")
            except Exception as e:
                self._log("Ошибка воспроизведения: " + str(e))
        except Exception as e:
            self._log("Ошибка синтеза TTS: " + str(e))

    def _append_history(self, role, content):
        entry = {"role": role, "content": content, "ts": datetime.now().isoformat()}
        self.history.append(entry)
        # trim size to reasonable amount
        if len(self.history) > 200:
            self.history = self.history[-200:]
        # save incrementally
        save_memory(self.history)
        # update GUI display
        if callable(self.gui_callback):
            self.loop.call_soon_threadsafe(self.gui_callback, f"history|{role}|{content[:200]}")

# -------------------
# PyQt GUI
# -------------------
class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Джарвис — голосовой ассистент (demo)")
        self.resize(700, 500)
        central = QtWidgets.QWidget()
        vbox = QtWidgets.QVBoxLayout(central)

        self.log_view = QtWidgets.QTextEdit()
        self.log_view.setReadOnly(True)
        vbox.addWidget(self.log_view)

        h = QtWidgets.QHBoxLayout()
        self.start_btn = QtWidgets.QPushButton("Start Listening")
        self.stop_btn = QtWidgets.QPushButton("Stop Listening")
        self.stop_btn.setEnabled(False)
        h.addWidget(self.start_btn)
        h.addWidget(self.stop_btn)
        vbox.addLayout(h)

        self.setCentralWidget(central)

        self.assistant = VoiceAssistant(gui_callback=self.gui_update)
        self.start_btn.clicked.connect(self.on_start)
        self.stop_btn.clicked.connect(self.on_stop)

    def gui_update(self, text):
        # Called from assistant via loop.call_soon_threadsafe
        # support special history updates
        if text.startswith("history|"):
            parts = text.split("|", 2)
            if len(parts) == 3:
                role, content = parts[1], parts[2]
                self.log_view.append(f"<b>{role}:</b> {content}")
                return
        # normal log
        self.log_view.append(text)

    @qasync.asyncSlot()
    async def on_start(self):
        self.start_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        self.log_view.append("Инициализация моделей и запуск прослушивания...")
        try:
            await self.assistant.init_models()
            await self.assistant.start_listening_loop()
            self.log_view.append("Ассистент запущен. Говорите 'Джарвис'...")
        except Exception as e:
            self.log_view.append("Ошибка запуска: " + str(e))
            self.start_btn.setEnabled(True)
            self.stop_btn.setEnabled(False)

    @qasync.asyncSlot()
    async def on_stop(self):
        self.stop_btn.setEnabled(False)
        self.start_btn.setEnabled(True)
        await self.assistant.stop_listening_loop()
        self.log_view.append("Ассистент остановлен.")


# -------------------
# Entrypoint
# -------------------
def main():
    import sys
    app = QtWidgets.QApplication(sys.argv)
    loop = qasync.QEventLoop(app)
    asyncio.set_event_loop(loop)
    window = MainWindow()
    window.show()
    with loop:
        loop.run_forever()


if __name__ == "__main__":
    main()