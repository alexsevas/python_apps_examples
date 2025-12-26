# pip install vosk pydub

# vosk - библиотека для распознавания речи на Python, поддерживает более 20 языков, включая русский, и позволяет создавать субтитры.


from vosk import Model, KaldiRecognizer
import wave
import json
import os
import tempfile
from pydub import AudioSegment
from pydub.exceptions import CouldntDecodeError


def preprocess_audio(input_path):
    """
    Предобработка аудиофайла до формата, необходимого для Vosk:
    - Моно (1 канал)
    - 16-bit PCM
    - Частота дискретизации 16000 Гц
    """
    try:
        print(f"Загружаем аудиофайл: {input_path}")
        # Загружаем аудио с помощью pydub
        audio = AudioSegment.from_file(input_path)

        print("Выполняем предобработку аудио...")
        # Конвертируем в моно
        if audio.channels != 1:
            print(f"  Конвертируем из {audio.channels} каналов в моно...")
            audio = audio.set_channels(1)

        # Конвертируем частоту дискретизации в 16000 Гц
        if audio.frame_rate != 16000:
            print(f"  Изменяем частоту дискретизации с {audio.frame_rate} Гц на 16000 Гц...")
            audio = audio.set_frame_rate(16000)

        # Конвертируем в 16-bit PCM
        if audio.sample_width != 2:  # 2 байта = 16 бит
            print(f"  Конвертируем в 16-bit формат...")
            audio = audio.set_sample_width(2)

        # Создаем временный файл для обработанного аудио
        temp_dir = tempfile.gettempdir()
        temp_path = os.path.join(temp_dir, "vosk_processed_temp.wav")

        print(f"Сохраняем обработанный файл во временный файл: {temp_path}")
        # Экспортируем в WAV формат
        audio.export(temp_path, format="wav")

        return temp_path

    except CouldntDecodeError:
        print(f"Ошибка: Не удалось декодировать аудиофайл '{input_path}'.")
        print("Поддерживаемые форматы: WAV, MP3, FLAC, OGG, M4A и другие.")
        return None
    except Exception as e:
        print(f"Ошибка при предобработке аудио: {str(e)}")
        return None


def recognize_speech(audio_path, model_path="model"):
    """
    Распознавание речи с использованием Vosk
    """
    # Предобработка аудио
    processed_path = preprocess_audio(audio_path)
    if not processed_path:
        return None

    try:
        # Открываем обработанный WAV файл
        wf = wave.open(processed_path, "rb")

        # Проверяем формат (на всякий случай)
        if wf.getnchannels() != 1:
            print(f"Предупреждение: Аудио имеет {wf.getnchannels()} каналов, требуется моно.")
            wf.close()
            return None

        if wf.getsampwidth() != 2:
            print(f"Предупреждение: Аудио имеет {wf.getsampwidth() * 8}-битную глубину, требуется 16 бит.")
            wf.close()
            return None

        print("Загружаем модель Vosk...")
        model = Model(model_path)

        print("Создаем распознаватель...")
        recognizer = KaldiRecognizer(model, wf.getframerate())

        # Для хранения полного результата
        full_text = []

        print("Начинаем распознавание...")
        while True:
            data = wf.readframes(4000)
            if len(data) == 0:
                break

            if recognizer.AcceptWaveform(data):
                result = recognizer.Result()
                result_json = json.loads(result)
                if "text" in result_json and result_json["text"]:
                    text = result_json["text"]
                    print(f"Распознано: {text}")
                    full_text.append(text)

        # Получаем финальный результат
        final_result = recognizer.FinalResult()
        final_json = json.loads(final_result)
        if "text" in final_json and final_json["text"]:
            text = final_json["text"]
            print(f"Финальный результат: {text}")
            full_text.append(text)

        # Закрываем файл
        wf.close()

        # Удаляем временный файл
        try:
            os.remove(processed_path)
            print(f"Временный файл удален: {processed_path}")
        except:
            print(f"Не удалось удалить временный файл: {processed_path}")

        # Возвращаем полный текст
        return " ".join(full_text)

    except Exception as e:
        print(f"Ошибка при распознавании: {str(e)}")
        # Удаляем временный файл даже при ошибке
        try:
            os.remove(processed_path)
        except:
            pass
        return None


# Основной код
if __name__ == "__main__":
    # Путь к аудиофайлу
    audio_path = "D:\\Projects\\Data\\Audio\\Audio_examples\\audio_RU_41sec.wav"

    # Путь к модели (по умолчанию "model")
    model_path = "vosk-model-small-ru-0.22"

    print("=== СИСТЕМА РАСПОЗНАВАНИЯ РЕЧИ VOSK ===")
    print(f"Исходный файл: {audio_path}")
    print(f"Путь к модели: {model_path}")
    print("-" * 50)

    # Выполняем распознавание
    result = recognize_speech(audio_path, model_path)

    if result:
        print("-" * 50)
        print("ПОЛНЫЙ РАСПОЗНАННЫЙ ТЕКСТ:")
        print(result)
    else:
        print("Распознавание не удалось. Проверьте файл и модель.")

    print("-" * 50)
    print("Готово!")


'''
Что делает этот код:

1.Автоматическая предобработка аудио:
- Конвертирует в моно (1 канал)
- Устанавливает частоту дискретизации 16000 Гц
- Конвертирует в 16-bit PCM формат
- Поддерживает различные входные форматы (MP3, FLAC, OGG, M4A и др.)
2.Проверки формата:
- Проверяет количество каналов
- Проверяет глубину семплов (16 бит)
- Проверяет частоту дискретизации
3.Обработка ошибок:
- Обработка ошибок загрузки аудио
- Обработка ошибок конвертации
- Очистка временных файлов
4.Улучшенный вывод:
- Показывает прогресс предобработки
- Выводит распознанный текст по мере поступления
- Показывает финальный результат
5.Управление ресурсами:
- Создает временный файл для обработанного аудио
- Автоматически удаляет временный файл после использования


- Для работы с MP3 и другими форматами может потребоваться установка ffmpeg
- Модель для русского языка можно скачать с https://alphacephei.com/vosk/models
- Временный файл создается в системной папке временных файлов и автоматически удаляется
'''