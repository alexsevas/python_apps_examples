# conda activate g4fpy311
# pip install pywhispercpp sounddevice numpy

'''
Логика работы:
(1) Цикл непрерывно слушает микрофон.
(2) Распознавание идёт на лету: ищем wake-word “Алиса”.
(3) Если найдено → переключаемся в режим записи фразы пользователя.
(4) Когда наступает пауза > 1.5 сек, считаем, что фраза закончилась.
(5) Распечатываем текст и возвращаемся к шагу (1).

Как работает
- Пока вы не сказали “Алиса”, модель анализирует последние 3 секунды потока и ищет ключевое слово.
- После триггера начинается запись вашей фразы.
- Когда тишина >1.5 секунды → фраза обрабатывается и выводится текст.
- Затем ассистент снова ждёт “Алиса”.
'''

import asyncio
import sounddevice as sd
import numpy as np
import queue
import time
from pywhispercpp.model import Model

# === НАСТРОЙКИ ===
WAKE_WORD = "алиса"
SAMPLE_RATE = 16000
BLOCK_SIZE = 1024
SILENCE_TIMEOUT = 1.5  # секунда паузы для завершения фразы

# Загружаем Whisper.cpp модель
model = Model('large-v3-turbo-q5_0')
#model = Model("D:/AI/TalkLlamaFast/TalkLlama/ggml-medium-q5_0.bin")

# Очередь для аудио
audio_queue = queue.Queue()


def audio_callback(indata, frames, time_info, status):
    """Захват аудио с микрофона"""
    if status:
        print(status)
    audio_queue.put(indata.copy())


async def transcribe_stream():
    """Асинхронный цикл работы ассистента"""
    print("🎤 Ассистент запущен. Скажите 'Алиса'...")

    with sd.InputStream(
        samplerate=SAMPLE_RATE,
        channels=1,
        blocksize=BLOCK_SIZE,
        dtype="float32",
        callback=audio_callback,
    ):
        buffer = []
        in_session = False
        last_voice_time = None

        while True:
            # ждем аудио
            data = audio_queue.get()
            buffer.extend(data[:, 0].tolist())

            # если сессии еще нет → ищем wake word
            if not in_session:
                if len(buffer) > SAMPLE_RATE * 3:  # проверяем последние 3 секунды
                    audio_chunk = np.array(buffer[-SAMPLE_RATE * 3 :], dtype=np.float32)
                    segments = model.transcribe(audio_chunk, language="ru")
                    text = " ".join(segment.text for segment in segments).lower().strip()
                    if WAKE_WORD in text:
                        print("✅ Wake word обнаружено!")
                        in_session = True
                        buffer = []  # очищаем буфер
                        last_voice_time = time.time()
            else:
                # мы в сессии → слушаем до паузы
                rms = np.sqrt(np.mean(np.square(data)))
                if rms > 0.01:  # есть голос
                    last_voice_time = time.time()

                # проверка на паузу
                if last_voice_time and (time.time() - last_voice_time > SILENCE_TIMEOUT):
                    if buffer:
                        audio_chunk = np.array(buffer, dtype=np.float32)
                        result = model.transcribe(audio_chunk, language="ru")
                        text = result["text"].strip()
                        print(f"📝 Пользователь сказал: {text}")
                    else:
                        print("⚠️ Пустая фраза")
                    # сброс в режим ожидания
                    in_session = False
                    buffer = []
                    print("🎤 Скажите 'Алиса'...")


async def main():
    await transcribe_stream()


if __name__ == "__main__":
    asyncio.run(main())