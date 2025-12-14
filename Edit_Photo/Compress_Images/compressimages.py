'''
Cкрипт для пакетной обработки изображений: сжатия и изменения размера

Модули: PIL (Pillow), os, sys, argparse — используется для обработки изображения и работы с файловой системой.

Запускаешь в папке с изображениями (или указываешь исходную папку), скрипт изменяет размер изображений до заданных лимитов
(максимальная ширина/высота), сжимает качество (JPEG или др.), переименовывает по шаблону, и сохраняет в output-папку.
Полезно, когда надо оптимизировать папки с фотографиями, иконками, медиа-контентом:

- Идёт по всем изображениям в папке с разрешениями .jpg, .jpeg, .png
- Изменяет их размер до заданных максимальных ширины/высоты, сохраняя пропорции
- Сжимает качество (для JPG например), чтобы уменьшить размер файлов
- Опционально переименовывает файлы по шаблону с номером
- Сохраняет всё в выходную папку, чтобы не перезаписывать оригиналы
'''


import os
import sys
from PIL import Image
from argparse import ArgumentParser

def process_images(input_dir, output_dir, max_width, max_height, quality=70, rename_template=None):
    os.makedirs(output_dir, exist_ok=True)
    count = 0
    for fname in os.listdir(input_dir):
        if fname.lower().endswith(('.jpg', '.jpeg', '.png')):
            path = os.path.join(input_dir, fname)
            img = Image.open(path)
            # изменение размера с сохранением пропорций
            img.thumbnail((max_width, max_height))
            base_name, ext = os.path.splitext(fname)
            if rename_template:
                out_name = rename_template.replace("{count}", str(count)) + ext
            else:
                out_name = fname
            out_path = os.path.join(output_dir, out_name)
            img.save(out_path, quality=quality)
            print(f"Saved: {out_path}")
            count += 1

def main():
    parser = ArgumentParser()
    parser.add_argument("input_dir")
    parser.add_argument("output_dir")
    parser.add_argument("--max_width", type=int, default=800)
    parser.add_argument("--max_height", type=int, default=600)
    parser.add_argument("--quality", type=int, default=70)
    parser.add_argument("--rename", help="template, e.g. img_{count}")
    args = parser.parse_args()
    process_images(args.input_dir, args.output_dir, args.max_width, args.max_height, args.quality, args.rename)

if name == "__main__":
    main()
