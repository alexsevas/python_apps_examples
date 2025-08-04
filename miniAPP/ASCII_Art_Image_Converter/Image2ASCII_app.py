# conda activate allpy311

'''
python Image2ASCII_app.py --input image.jpg --width 80 --output ascii.txt --detailed
'''

import os
import argparse
from PIL import Image
import numpy as np

GSCALE_SIMPLE = "@%#*+=-:. "
GSCALE_EXTENDED = "$@B%8&WM#*oahkbdpqwmZO0QLCJUYXzcvunxrjft/\\|()1{}[]?-_+~i!lI;:,\"^`'. "

def avg_brightness(tile):
    return np.array(tile).mean()

def image_to_ascii(image_path, cols=80, more_levels=False):
    image = Image.open(image_path).convert('L')
    W, H = image.size
    scale = 0.43  # поправка на соотношение символов в терминале
    w = W / cols
    h = w / scale
    rows = int(H / h)

    print(f"[ASCII] Рисунок: cols={cols}, rows={rows}")

    ascii_img = []
    gs = GSCALE_EXTENDED if more_levels else GSCALE_SIMPLE
    levels = len(gs)

    for row in range(rows):
        y1 = int(row * h)
        y2 = int((row + 1) * h) if row < rows - 1 else H
        line = ""
        for col in range(cols):
            x1 = int(col * w)
            x2 = int((col + 1) * w) if col < cols - 1 else W
            tile = image.crop((x1, y1, x2, y2))
            brightness = avg_brightness(tile)
            idx = int(brightness * (levels - 1) / 255)
            line += gs[idx]
        ascii_img.append(line)
    return ascii_img

def main():
    parser = argparse.ArgumentParser(description="ASCII Art Image Converter")
    parser.add_argument('--input', required=True, help='Путь к изображению')
    parser.add_argument('--width', '-w', type=int, default=80, help='Ширина в символах')
    parser.add_argument('--output', '-o', help='Выходной .txt файл (по умолчанию — stdout)')
    parser.add_argument('--detailed', action='store_true',
                        help='Использовать мелкую градацию (GSCALE_EXTENDED)')
    args = parser.parse_args()

    art = image_to_ascii(args.input, cols=args.width, more_levels=args.detailed)
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write('\n'.join(art))
        print(f"✅ Сохранено в {args.output}")
    else:
        print()
        print('\n'.join(art))

if __name__ == "__main__":
    main()
