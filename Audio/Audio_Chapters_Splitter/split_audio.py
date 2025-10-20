# conda activate allpy311

# Скрипт, который автоматически делит длинное аудио (например, подкаст или лекцию) на главы по паузам или тишине.
# Удобно для разбиения больших треков и подготовки фрагментов для публикации, разбивки на главы или последующей расшифровки.
# - Загружает аудиофайл (.mp3, .wav и др.)
# - Находит паузы длиннее заданного порога (например, тишина ≥ 2 секунды)
# Python 3.8+
# pip install pydub
# Модули: pydub, argparse, os, scipy.signal (только если нужен алгоритм кластеризации пауз)
# Также потребуется ffmpeg или avlib — убедись, что установлен

# python split_audio.py --input lecture.mp3 --silence_thresh -40 --min_silence_len 2000 --output segmented/

import os
import argparse
from pydub import AudioSegment
from pydub.silence import detect_silence

def split_on_silence(input_path, silence_thresh=-40, min_silence_len=2000, keep_silence=500, output_dir="segments"):
    audio = AudioSegment.from_file(input_path)
    os.makedirs(output_dir, exist_ok=True)

    silence_ranges = detect_silence(audio, min_silence_len=min_silence_len, silence_thresh=silence_thresh)
    silence_ranges = [(start, stop) for start, stop in silence_ranges]

    prev_end = 0
    count = 1
    for start, stop in silence_ranges:
        segment = audio[prev_end:start]
        segment_name = os.path.join(output_dir, f"segment_{count:03}.mp3")
        segment.export(segment_name, format="mp3")
        print(f"✅ Saved {segment_name}")
        count += 1
        prev_end = stop

    # last segment
    if prev_end < len(audio):
        segment = audio[prev_end:]
        segment_name = os.path.join(output_dir, f"segment_{count:03}.mp3")
        segment.export(segment_name, format="mp3")
        print(f"✅ Saved {segment_name}")

def main():
    parser = argparse.ArgumentParser(description="Split audio on silence into chapters")
    parser.add_argument("--input", required=True, help="Input audio file (mp3/wav/etc.)")
    parser.add_argument("--silence_thresh", type=int, default=-40, help="Threshold (dBFS) to detect silence")
    parser.add_argument("--min_silence_len", type=int, default=2000, help="Minimum silence length (ms)")
    parser.add_argument("--keep_silence", type=int, default=500, help="Silence to leave at edges (ms)")
    parser.add_argument("--output", default="segments", help="Directory to save segments")
    args = parser.parse_args()
    split_on_silence(args.input, args.silence_thresh, args.min_silence_len, args.keep_silence, args.output)

if __name__ == "__main__":
    main()
