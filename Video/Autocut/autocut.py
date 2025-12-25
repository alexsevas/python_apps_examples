'''
--silence-threshold -55 (если фон шумный — сделай -50)
--min-silence-duration 0.2 (чтобы ловить короткие паузы)
--silent-speed 6..10


python autocut.py --input 2.mp4 --silent-speed 10 --silence-threshold -50 --min-silence-duration 0.1
python autocut.py --input Goto_Night.MP4 --silent-speed 8 --silence-threshold -50 --min-silence-duration 0.2
'''

import argparse
import subprocess
import re
import os
import sys

def run_ffmpeg(cmd):
    print("Выполняется:", " ".join(cmd))
    result = subprocess.run(cmd, stderr=subprocess.PIPE, text=True)
    if result.returncode != 0:
        print("Ошибка ffmpeg:", result.stderr)
        sys.exit(1)

def get_silence_segments(input_file, noise_level, min_duration):
    cmd = [
        "ffmpeg", "-i", input_file,
        "-af", f"silencedetect=noise={noise_level}dB:d={min_duration}",
        "-f", "null", "-"
    ]
    result = subprocess.run(cmd, stderr=subprocess.PIPE, text=True)
    lines = result.stderr.splitlines()

    silences = []
    for line in lines:
        if "silence_start:" in line:
            start = float(re.search(r"silence_start: ([\d.]+)", line).group(1))
        elif "silence_end:" in line:
            end = float(re.search(r"silence_end: ([\d.]+)", line).group(1))
            silences.append((start, end))
    return silences

def get_duration(input_file):
    cmd = [
        "ffprobe", "-v", "error", "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1", input_file
    ]
    result = subprocess.run(cmd, stdout=subprocess.PIPE, text=True)
    return float(result.stdout.strip())

def build_filter(duration, active_segments, speed):
    if not active_segments:
        # Если речи нет — ускоряем всё
        return f"[0:v]setpts=PTS/{speed}[v];[0:a]atempo={speed}[a]"

    v_select = []
    a_select = []
    prev_end = 0.0
    seg_id = 0

    for start, end in active_segments:
        # Тишина ДО активного сегмента
        if start > prev_end:
            v_select.append(f"between(t,{prev_end},{start})*{speed}")
            a_select.append(f"between(t,{prev_end},{start})*{speed}")
        # Речь (нормальная скорость = 1.0)
        v_select.append(f"between(t,{start},{end})*1.0")
        a_select.append(f"between(t,{start},{end})*1.0")
        prev_end = end

    # Тишина ПОСЛЕ последней речи
    if prev_end < duration:
        v_select.append(f"between(t,{prev_end},{duration})*{speed}")
        a_select.append(f"between(t,{prev_end},{duration})*{speed}")

    v_expr = "+".join(v_select)
    a_expr = "+".join(a_select)

    # Создаём фильтр, который динамически управляет скоростью
    return (
        f"[0:v]select=1,setpts='PTS*({v_expr})'[v];"
        f"[0:a]aselect=1,atempo='({a_expr})'[a]"
    )

def main():
    parser = argparse.ArgumentParser(description="Ускоряет тихие участки видео")
    parser.add_argument("--input", required=True)
    parser.add_argument("--output")
    parser.add_argument("--silent-speed", type=float, default=10.0)
    parser.add_argument("--silence-threshold", type=float, default=-60.0)
    parser.add_argument("--min-silence-duration", type=float, default=0.5)
    args = parser.parse_args()

    input_file = args.input
    if not os.path.exists(input_file):
        print(f"Файл не найден: {input_file}")
        sys.exit(1)

    output_file = args.output or f"{os.path.splitext(input_file)[0]}_faster.mp4"

    # Получаем тихие участки
    silences = get_silence_segments(
        input_file,
        args.silence_threshold,
        args.min_silence_duration
    )

    duration = get_duration(input_file)

    # Активные участки = всё, кроме тишины
    active = []
    last_end = 0.0
    for start, end in silences:
        if start > last_end:
            active.append((last_end, start))
        last_end = end
    if last_end < duration:
        active.append((last_end, duration))

    print(f"Длительность: {duration:.2f} сек")
    print(f"Тихие участки: {silences}")
    print(f"Активные участки (речь): {active}")

    if not active:
        print("Речь не найдена — ускоряем всё.")
        cmd = [
            "ffmpeg", "-i", input_file,
            "-filter_complex", f"[0:v]setpts=PTS/{args.silent_speed}[v];[0:a]atempo={args.silent_speed}[a]",
            "-map", "[v]", "-map", "[a]",
            "-c:v", "libx264", "-crf", "23", "-c:a", "aac", output_file
        ]
        run_ffmpeg(cmd)
    else:
        # ❌ ПЛОХАЯ НОВОСТЬ: `atempo` НЕ ПОДДЕРЖИВАЕТ ИЗМЕНЕНИЕ СКОРОСТИ ВО ВРЕМЕНИ!
        # Это невозможно в ffmpeg в одном проходе с `atempo`.
        #
        # Поэтому — ЕДИНСТВЕННОЕ РАБОЧЕЕ РЕШЕНИЕ:
        # Разрезать видео на сегменты и обрабатывать отдельно.

        # Мы сделаем это.
        segments = []
        last = 0.0
        for start, end in silences:
            if start > last:
                segments.append((last, start, 1.0))  # речь — норм. скорость
            segments.append((start, end, args.silent_speed))  # тишина — ускорить
            last = end
        if last < duration:
            segments.append((last, duration, 1.0))

        # Создаём временные файлы
        temp_files = []
        for i, (s, e, spd) in enumerate(segments):
            if e <= s:
                continue
            temp_video = f"temp_{i:03d}.mp4"
            if spd == 1.0:
                # Копируем без изменения (быстро)
                cmd = ["ffmpeg", "-i", input_file, "-ss", str(s), "-to", str(e), "-c", "copy", temp_video]
            else:
                # Ускоряем
                cmd = [
                    "ffmpeg", "-i", input_file,
                    "-ss", str(s), "-to", str(e),
                    "-filter_complex", f"[0:v]setpts=PTS/{spd}[v];[0:a]atempo={spd}[a]",
                    "-map", "[v]", "-map", "[a]",
                    "-c:v", "libx264", "-crf", "28", "-c:a", "aac", "-b:a", "96k",
                    temp_video
                ]
            run_ffmpeg(cmd)
            temp_files.append(temp_video)

        # Объединяем
        with open("filelist.txt", "w") as f:
            for tf in temp_files:
                f.write(f"file '{tf}'\n")

        cmd = ["ffmpeg", "-f", "concat", "-safe", "0", "-i", "filelist.txt", "-c", "copy", output_file]
        run_ffmpeg(cmd)

        # Удаляем временные файлы
        for tf in temp_files:
            os.remove(tf)
        os.remove("filelist.txt")

    print(f"✅ Готово: {output_file}")

if __name__ == "__main__":
    main()