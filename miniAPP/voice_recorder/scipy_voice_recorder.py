# conda activate allpy311

# pip install sounddevice scipy

'''
Запись голоса.
- Вводишь количество секунд;
- Нажимаешь Enter — и идёт запись;
- На выходе — готовый аудиофайл.

Используем библиотеки:
- sounddevice — захват аудио
- scipy — для сохранения .wav файлов

Не забыть дать доступ к микрофону в настройках windows, иначе будет ошибка.
'''

import sounddevice as sd
from scipy.io.wavfile import write


def record_voice(duration: int, filename: str = "recording.wav", sample_rate: int = 44100) -> None:
    """
    Записывает звук с микрофона и сохраняет его в .wav файл.

    :param duration: Время записи в секундах
    :param filename: Название выходного файла
    :param sample_rate: Частота дискретизации (по умолчанию 44100 Гц)
    """
    print(f"🎙 Запись началась на {duration} секунд...")
    audio_data = sd.rec(int(duration * sample_rate), samplerate=sample_rate, channels=2)
    sd.wait()
    write(filename, sample_rate, audio_data)
    print(f"✅ Запись завершена. Файл сохранён как: {filename}")


if __name__ == "__main__":
    try:
        seconds = int(input("⏱️ Введите длительность записи в секундах: "))
        record_voice(seconds)
    except Exception as e:
        print(f"❌ Ошибка: {e}")
