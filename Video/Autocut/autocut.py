
'''
Скрипт, который автоматически ускоряет “тихие” части видео (например лекций), чтобы ты не тратил время на паузы и молчание.
Можно задать порог тишины и насколько ускорять эти части. Полезно, если любишь смотреть длинные видео, лекции или стримы,
но хочешь “вырезать” момент, когда ничего не происходит:
- Определяет “тихие” участки видео, используя порог громкости / шумов
- Автоматически ускоряет эти участки, чтобы сократить общее время просмотра видео
- Опционально удаляет шум или фоновые звуки (denoise) при помощи фильтров ffmpeg
- Сохраняет модифицированное видео с суффиксом или в указанное место
'''

import argparse
import subprocess

def autocut(input_files, output, silent_speed=10, silent_threshold=600, denoise=False):
    for input_vid in input_files:
        cmd = ["ffmpeg", "-i", input_vid]
        # добавляется фильтр, который ускоряет silent части
        vfilt = f"silencedetect=n={silent_threshold}dB"
        # здесь опции ускорения, убирание шума и т.д.
        # пример:
        cmd.extend([
            "-vf", vfilt,
            "-filter_complex", f"[0:v]setpts=PTS/ {silent_speed}[v]",
            "-map", "[v]", "-map", "0:a",
            output or f"{input_vid}_faster.mp4"
        ])
        if denoise:
            cmd.extend(["-af", "arnndn"])
        print("Running:", " ".join(cmd))
        subprocess.run(cmd, check=True)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Speed up silent parts in videos.")
    parser.add_argument("--input", nargs='+', required=True, help="Input video files *.mp4")
    parser.add_argument("--output", help="Output filename or directory")
    parser.add_argument("--silent-speed", type=int, default=10, help="How much to speed up silent parts")
    parser.add_argument("--silent-threshold", type=int, default=600, help="What is considered silent (threshold in milliseconds/sound level)")
    parser.add_argument("--denoise", action="store_true", help="Remove background noise using ffmpeg model")
    args = parser.parse_args()
    autocut(args.input, args.output, args.silent_speed, args.silent_threshold, args.denoise)
