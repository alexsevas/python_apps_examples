# conda activate allpy310_2

# Извлечение данных из сканов паспортов, чеков, справок

import cv2
import pytesseract
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import pprint
import os

# Путь к изображению
img_path = r"D:\\Projects\\Data\\OCR\\test_med_ocr.jpg"
img = cv2.imread(img_path)

if img is None:
    raise FileNotFoundError(f"Изображение не найдено: {img_path}")

# Предобработка
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
gray = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)[1]

# Распознавание текста с координатами
data = pytesseract.image_to_data(gray, lang="eng+rus", output_type=pytesseract.Output.DICT)

# Преобразуем OpenCV-изображение в PIL для поддержки кириллицы
img_pil = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
draw = ImageDraw.Draw(img_pil)

# Подключаем шрифт, поддерживающий кириллицу
# Попробуем найти шрифт (на разных ОС разные пути)
def get_font():
    font_paths = [
        "C:/Windows/Fonts/arial.ttf",  # Windows
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",  # Linux
        "/System/Library/Fonts/Arial.ttf",  # macOS
        "DejaVuSans.ttf",  # если положить в папку проекта
    ]
    for path in font_paths:
        if os.path.isfile(path):
            try:
                return ImageFont.truetype(path, 32)
            except Exception as e:
                print(f"Не удалось загрузить шрифт {path}: {e}")
    print("⚠️ Шрифт не найден, используем шрифт по умолчанию (может не поддерживать кириллицу)")
    return ImageFont.load_default()

font = get_font()

# Визуализация найденных слов
for i in range(len(data["text"])):
    conf = int(data["conf"][i])
    if conf > 60:  # порог уверенности
        x, y, w, h = data["left"][i], data["top"][i], data["width"][i], data["height"][i]
        text = data["text"][i].strip()

        # Рисуем прямоугольник (через OpenCV или PIL — здесь через PIL для единообразия)
        draw.rectangle([x, y, x + w, y + h], outline=(0, 255, 0), width=2)

        # Рисуем текст (с возможностью кириллицы)
        if text:  # только если текст не пустой
            # Определяем цвет текста
            text_color = (255, 0, 0)  # красный

            # Позиция текста: над рамкой
            text_position = (x, y - 5)

            # Рисуем текст
            draw.text(text_position, text, font=font, fill=text_color)

# Преобразуем обратно в OpenCV-формат (BGR)
img_output = cv2.cvtColor(np.array(img_pil), cv2.COLOR_RGB2BGR)

# Сохраняем результат
output_path = "document_result_with_russian.png"
cv2.imwrite(output_path, img_output)

print("✅ Готово: документ размечен и сохранён в", output_path)
pprint.pprint([text for text in data["text"] if text.strip()])  # только непустые тексты