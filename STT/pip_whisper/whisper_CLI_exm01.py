# conda allpy310

import sys
import os
import subprocess
import torch
import whisper


def extract_audio(video_path, audio_path):
    """
    Извлекает аудиодорожку из видеофайла с помощью ffmpeg.
    """
    command = [
        'ffmpeg', '-y', '-i', video_path, '-vn', '-acodec', 'pcm_s16le', '-ar', '16000', '-ac', '1', audio_path
    ]
    result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if result.returncode != 0:
        print("Ошибка при извлечении аудио:", result.stderr.decode())
        sys.exit(1)

def transcribe_audio(audio_path, model_name="medium"):  # Можно выбрать 'base', 'small', 'medium', 'large'
    """
    Расшифровывает аудиофайл с помощью Whisper (CUDA, если доступно).
    """
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"Загрузка модели Whisper ({model_name}) на устройство: {device}")
    model = whisper.load_model(model_name, device=device)
    print("Начинается расшифровка...")
    result = model.transcribe(audio_path)
    return result["text"]

def main():
    if len(sys.argv) < 2:
        print("Использование: python whisper_CLI_exm01.py <путь_к_видео>")
        sys.exit(1)
    video_path = sys.argv[1]
    if not os.path.isfile(video_path):
        print(f"Файл не найден: {video_path}")
        sys.exit(1)
    base_name = os.path.splitext(os.path.basename(video_path))[0]
    audio_path = base_name + "_audio.wav"
    text_path = base_name + "_transcript.txt"

    extract_audio(video_path, audio_path)
    text = transcribe_audio(audio_path)
    with open(text_path, "w", encoding="utf-8") as f:
        f.write(text)
    print(f"Расшифровка завершена. Результат сохранён в: {text_path}")
    # Удалить временный аудиофайл
    if os.path.exists(audio_path):
        os.remove(audio_path)

if __name__ == "__main__":
    main()