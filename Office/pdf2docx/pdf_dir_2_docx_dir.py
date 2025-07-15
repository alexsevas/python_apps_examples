# conda activate allpy311

# pip install pdf2docx (подтягивает numpy 2.x.x и opencv-python-headless)

from pathlib import Path
from pdf2docx import Converter

# Определяем путь к директории с PDF файлами
pdf_dir = Path('D:\\AI_DATA\\PDF_ENG')
# Определяем путь к директории, куда будут сохранены DOCX файлы
docx_dir = Path('D:\\AI_DATA\\PDF_ENG\\docx_files')

# Проверяем, существует ли директория для DOCX файлов
if not docx_dir.exists():
    # Если директория не существует, создаём её
    docx_dir.mkdir()

# Проходимся по всем PDF файлам в директории pdf_files
for pdf_file in pdf_dir.glob('*.pdf'):  # Используем метод glob для поиска всех файлов с расширением .pdf
    # Создаём путь для нового DOCX файла, заменяя расширение на .docx
    docx_file = docx_dir / pdf_file.with_suffix('.docx').name
    # Создаем экземпляр Converter для текущего PDF файла
    cv = Converter(pdf_file)
    # Конвертируем PDF файл в DOCX и сохраняем его по указанному пути
    cv.convert(docx_file)
    # Закрываем экземпляр Converter после завершения конвертации
    cv.close()
