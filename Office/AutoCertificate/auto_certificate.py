# Скрипт для массовой генерации электронных сертификатов

'''
Инструмент, который автоматически генерирует сертификаты (например, участникам курсов) на основе шаблона
изображения + списка имён/данных. Можно задать шрифт, положение текста, цвет и выходной формат (PDF или изображение).
Подходит, когда много людей, и делать вручную каждый сертификат — долго.
- Читает CSV / Excel с именами (и другими данными)
- Открывает шаблон сертификата как изображение
- Накладывает текст (имя / данные) в указанную позицию

Python 3.6+
ℹ️ Модули: Pillow (для работы с изображениями), openpyxl или xlsxwriter (для чтения данных из Excel / CSV), os, argparse и др.
'''

from PIL import Image, ImageDraw, ImageFont
import csv
import os

def generate_cert(template_path, data_csv, output_folder, font_path, font_size, text_position):
    img = Image.open(template_path)
    draw = ImageDraw.Draw(img)
    font = ImageFont.truetype(font_path, font_size)

    with open(data_csv, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            name = row['name']
            cert = img.copy()
            d = ImageDraw.Draw(cert)
            d.text(text_position, name, font=font, fill=(0, 0, 0))
            out_path = os.path.join(output_folder, f"cert_{name}.png")
            cert.save(out_path)
            print(f"Saved certificate for {name} → {out_path}")

if __name__ == "__main__":
    generate_cert(
        template_path="templates/cert_template.png",
        data_csv="data/people.csv",
        output_folder="out",
        font_path="fonts/Times.ttf",
        font_size=64,
        text_position=(300, 400)
    )
