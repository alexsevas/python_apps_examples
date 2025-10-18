# conda activate allpy311

'''
Утилита, которая берёт изображения из заданной папки, подгоняет их под нужный формат/размер (например, A4),
и объединяет в один PDF-документ.
Удобно, если у тебя есть множество JPG/PNG, и ты хочешь получить единый PDF без сторонних инструментов.
'''

from PIL import Image
import os

def images_to_pdf(img_folder, output_pdf_path, paper_size=(595, 842)):
    # paper_size в пунктах — примерно A4 (в зависимости от DPI)
    imgs = []
    for fname in sorted(os.listdir(img_folder)):
        if fname.lower().endswith(('.png', '.jpg', '.jpeg')):
            img_path = os.path.join(img_folder, fname)
            img = Image.open(img_path).convert('RGB')
            img = img.resize(paper_size)  # подгонка под формат
            imgs.append(img)
    if not imgs:
        print("Нет изображений для конвертации")
        return
    first, rest = imgs[0], imgs[1:]
    first.save(output_pdf_path, save_all=True, append_images=rest)
    print(f"Создан PDF: {output_pdf_path}")

if __name__ == "__main__":
    images_to_pdf("D:\Projects\Data\Images\Faces", "out.pdf")


'''
Скрипт 
- Сканирует папку с изображениями (JPG, PNG и др.)
- Подгоняет каждый кадр под заданный размер (например, формат страницы)
- Объединяет все изображения в один PDF-файл
- Сохраняет PDF с указанным именем
'''