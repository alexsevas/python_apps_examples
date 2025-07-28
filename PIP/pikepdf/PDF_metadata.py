# conda activate allpy311
# pip install pikepdf
'''
Извлечение метаданных PDF-файла на Python
Для извлечения метаданных из PDF-файла в коде используется библиотека pikepdf.
'''

import pikepdf

# Указываем путь к PDF-файлу
pdf_filename = "D:\\Projects\\Data\\PDF_DOC_DOCX_TXT_XML\\PDFDOC.pdf"

# Считываем PDF-файл
pdf = pikepdf.Pdf.open(pdf_filename)

# Извлекаем и выводим метаданные PDF-файла
doc_info = pdf.docinfo
for key, value in doc_info.items():
    print(key, ":", value)
