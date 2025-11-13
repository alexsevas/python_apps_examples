# conda activate ttsp311

# Данный скрипт реализует систему синтеза речи (Text-to-Speech, TTS) с использованием модели `Kokoro-82M`.
# Особенности реализации
# - Асинхронная обработка: текст генерируется в одном потоке, воспроизводится в другом
# - Буферизация: позволяет начать воспроизведение после получения первых N блоков, не дожидаясь полной генерации
# - Управление скоростью: первый блок может воспроизводиться с другой скоростью (например, для "разогрева")
# - Обработка пустых текстов: проверяет, есть ли вообще текст для синтеза
# - Управление ресурсами: корректное закрытие аудио потоков и освобождение PyAudio ресурсов


import re
import numpy as np
import pyaudio
import threading
import warnings
from kokoro import KPipeline
from queue import Queue

warnings.filterwarnings("ignore", message="dropout option adds dropout after all but last recurrent layer.*")
warnings.filterwarnings("ignore", message=".*torch.nn.utils.weight_norm.*is deprecated.*")

REPO_ID = 'hexgrad/Kokoro-82M'
LANG_CODE = 'a'
VOICE = 'am_michael'
SPEED = 1.3
SAMPLE_RATE = 24000
FRAMES_PER_BUFFER = 1024
PIPELINE = KPipeline(lang_code=LANG_CODE, repo_id=REPO_ID)

def split_into_sentences(text):
    if not text or not text.strip():
        return []
    parts = re.split(r'(?<!\w-\w)(?<=[.!?])\s+(?=[A-Z])', text.strip())
    return [p.strip() for p in parts if p.strip()]

def group_sentences(sentences, block_size=2):
    for i in range(0, len(sentences), block_size):
        yield ' '.join(sentences[i:i+block_size])

def speak(
        text,
        voice=VOICE,
        base_speed=SPEED,
        fast_speed=SPEED+0.3,
        block_size=2,
        initial_buffer_blocks=1):
    sentences = split_into_sentences(text)

    if not sentences:
        print('No text to speak.')
        return False

    audio_queue=Queue(maxsize=initial_buffer_blocks+2)
    done_sentinel=object()

    def producer():
        for idx, block in enumerate(group_sentences(sentences, block_size)):
            speed = fast_speed if idx == 0 else base_speed
            print(f'[gen] Block {idx+1}: "{block[:50]}..." @ speed {speed}')
            chunk_list =[]
            #kokoro yields (graphems, phonemes, audio) tuples
            for _, _, audio in PIPELINE(block, voice=voice, speed=speed):
                chunk_list.append(np.array(audio.tolist(), dtype=np.float32))
            if chunk_list:
                full_block = np.concatenate(chunk_list)
                audio_queue.put(full_block)
        audio_queue.put(done_sentinel)

    def consumer():
        p = pyaudio.PyAudio()
        stream = p.open(format=pyaudio.paFloat32,channels=1,rate=SAMPLE_RATE,output=True, frames_per_buffer=FRAMES_PER_BUFFER)

        try:
            # Wait for initial buffer of N blocks
            print(f'[play] Buffering {initial_buffer_blocks} block(s)...')
            for _ in range(initial_buffer_blocks):
                blk = audio_queue.get()
                if blk is done_sentinel:
                    return
                stream.write(blk.tobytes())

            # Now drane the rest as they come
            while True:
                blk = audio_queue.get()
                if blk is done_sentinel:
                    break
                stream.write(blk.tobytes())
        finally:
            stream.stop_stream()
            stream.close()
            p.terminate()
            print('[play] Playback complete')

    prod_t = threading.Thread(target=producer, daemon=True)
    const_t = threading.Thread(target=consumer, daemon=True)
    prod_t.start()
    const_t.start()
    prod_t.join()
    const_t.join()

    return True

if __name__ == '__main__':
    text_to_speak = '''From fairest creatures we desire increase, That thereby beauty\'s rose might never die. 
    But as the riper should by time decease, His tender heir might bear his memory: But thou contracted to thine own bright eyes. 
    Feed\'st thy light\'s flame with self-substantial fuel, Making a famine where abundance lies. 
    Thy self thy foe, to thy sweet self too cruel: Thou that art now the world\'s fresh ornament. 
    And only herald to the gaudy spring, Within thine own bud buriest thy content. 
    And, tender churl, mak\'st waste in niggarding: Pity the world, or else this glutton be, To eat the world\'s due, by the grave and thee.'''

    print("Start TTS...")
    speak(text_to_speak)
    print("Done.")

'''
1) Проблема с требованием установки huggingface_hub[hf_xet] возникает потому, что hf_xet обеспечивает эффективную передачу 
больших файлов моделей с использованием стратегии дедупликации на основе чанков. 
Это компонент, который интегрируется с huggingface_hub для оптимизации загрузки и выгрузки файлов в Hugging Face Hub.

pip install huggingface_hub[hf_xet]

2) Долгий первый запуск. Модели автоматически загружаются при первом запуске, что занимает значительное время. 
Первоначальная загрузка во время первого старта действительно требует времени в зависимости от размера модели и скорости 
интернет-соединения.
'''
