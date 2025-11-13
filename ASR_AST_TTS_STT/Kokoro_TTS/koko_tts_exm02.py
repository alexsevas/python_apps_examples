# conda activate ttsp311

# Основные преимущества второй версии
# - Лучшая производительность: Кэширование модели предотвращает повторную загрузку при многократных вызовах
# - Более надежная работа: Добавлена обработка ошибок для предотвращения падений
# - Лучшая диагностика: Более подробные логи и измерение времени выполнения
# - Более чистый код: Исправлены опечатки и улучшена структура
# - Более безопасная работа с ресурсами: Улучшена обработка исключений в критических участках


import re
import numpy as np
import pyaudio
import threading
import warnings
import time  # <-- добавлен недостающий импорт
from kokoro import KPipeline
from queue import Queue

# Подавление предупреждений
warnings.filterwarnings("ignore", message="dropout option adds dropout after all but last recurrent layer.*")
warnings.filterwarnings("ignore", message=".*torch.nn.utils.weight_norm.*is deprecated.*")

# Конфигурация
REPO_ID = 'hexgrad/Kokoro-82M'
LANG_CODE = 'a'
VOICE = 'am_michael'
SPEED = 1.3
SAMPLE_RATE = 24000
FRAMES_PER_BUFFER = 1024

# Глобальный кэш для pipeline (загружается один раз)
_CACHED_PIPELINE = None


def get_cached_pipeline():
    """
    Возвращает единственный экземпляр KPipeline.
    Модель автоматически кэшируется Hugging Face в ~/.cache/huggingface/hub
    """
    global _CACHED_PIPELINE
    if _CACHED_PIPELINE is None:
        print("[init] Loading Kokoro TTS model. This may take a while on first run...")
        start_time = time.time()
        try:
            _CACHED_PIPELINE = KPipeline(lang_code=LANG_CODE, repo_id=REPO_ID)
            load_time = time.time() - start_time
            print(f"[init] Model loaded successfully in {load_time:.2f} seconds")
        except Exception as e:
            print(f"[init] Error loading model: {e}")
            raise
    return _CACHED_PIPELINE


def split_into_sentences(text):
    if not text or not text.strip():
        return []
    parts = re.split(r'(?<!\w-\w)(?<=[.!?])\s+(?=[A-Z])', text.strip())
    return [p.strip() for p in parts if p.strip()]


def group_sentences(sentences, block_size=2):
    # Исправлено: block_size используется корректно
    for i in range(0, len(sentences), block_size):
        yield ' '.join(sentences[i:i + block_size])


def speak(
        text,
        voice=VOICE,
        base_speed=SPEED,
        fast_speed=SPEED + 0.3,
        block_size=2,
        initial_buffer_blocks=1):
    sentences = split_into_sentences(text)

    if not sentences:
        print('[tts] No text to speak.')
        return False

    audio_queue = Queue(maxsize=initial_buffer_blocks + 2)
    done_sentinel = object()
    pipeline = get_cached_pipeline()

    def producer():
        try:
            for idx, block in enumerate(group_sentences(sentences, block_size)):
                speed = fast_speed if idx == 0 else base_speed
                print(f'[gen] Block {idx + 1}: "{block[:50]}..." @ speed {speed}')
                chunk_list = []
                for _, _, audio in pipeline(block, voice=voice, speed=speed):
                    chunk_list.append(np.array(audio.tolist(), dtype=np.float32))
                if chunk_list:
                    full_block = np.concatenate(chunk_list)
                    audio_queue.put(full_block)
            audio_queue.put(done_sentinel)
        except Exception as e:
            print(f'[gen] Producer error: {e}')
            audio_queue.put(done_sentinel)

    def consumer():
        p = pyaudio.PyAudio()
        stream = p.open(
            format=pyaudio.paFloat32,
            channels=1,
            rate=SAMPLE_RATE,
            output=True,
            frames_per_buffer=FRAMES_PER_BUFFER
        )
        try:
            print(f'[play] Buffering {initial_buffer_blocks} block(s)...')
            for _ in range(initial_buffer_blocks):
                blk = audio_queue.get()
                if blk is done_sentinel:
                    return
                stream.write(blk.tobytes())

            while True:
                blk = audio_queue.get()
                if blk is done_sentinel:
                    break
                stream.write(blk.tobytes())
        except Exception as e:
            print(f'[play] Playback error: {e}')
        finally:
            stream.stop_stream()
            stream.close()
            p.terminate()
            print('[play] Playback complete')

    prod_t = threading.Thread(target=producer, daemon=True)
    cons_t = threading.Thread(target=consumer, daemon=True)
    prod_t.start()
    cons_t.start()
    prod_t.join()
    cons_t.join()

    return True


def preload_model():
    """Выполняет тестовый запуск для кэширования модели."""
    print('[preload] Preloading model...')
    pipeline = get_cached_pipeline()
    try:
        start_time = time.time()
        # Выполняем минималистичный прогон
        list(pipeline("cache", voice=VOICE, speed=SPEED))
        elapsed = time.time() - start_time
        print(f'[preload] Preloading completed in {elapsed:.2f} seconds')
        return True
    except Exception as e:
        print(f'[preload] Preload failed: {e}')
        return False


if __name__ == '__main__':
    # Предзагрузка модели (опционально, но полезно для кэширования)
    preload_model()

    text_to_speak = '''From fairest creatures we desire increase, That thereby beauty\'s rose might never die. 
        But as the riper should by time decease, His tender heir might bear his memory: But thou contracted to thine own bright eyes. 
        Feed\'st thy light\'s flame with self-substantial fuel, Making a famine where abundance lies. 
        Thy self thy foe, to thy sweet self too cruel: Thou that art now the world\'s fresh ornament. 
        And only herald to the gaudy spring, Within thine own bud buriest thy content. 
        And, tender churl, mak\'st waste in niggarding: Pity the world, or else this glutton be, To eat the world\'s due, by the grave and thee.'''

    print("\n=== Starting TTS ===")
    start_time = time.time()

    success = speak(text_to_speak)

    total_time = time.time() - start_time
    if success:
        print(f"\n=== Done in {total_time:.2f} seconds ===")
    else:
        print("\n=== TTS failed ===")