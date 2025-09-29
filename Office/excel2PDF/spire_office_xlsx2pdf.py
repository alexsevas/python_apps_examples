# pip install Spire.Office

'''
Код для конвертации Excel в PDF.
Для конвертации XLS/XLSX в PDF в коде используется библиотека Spire.Office.
'''

from spire.xls import *

# Создаём объект класса Workbook
workbook = Workbook()

# Загружаем Excel документ
workbook.LoadFromFile("test.xlsx")

# Устанавливаем соответствие листа странице при конвертации
workbook.ConverterSetting.SheetFitToPage = True

# Конвертируем Excel в PDF-файл
workbook.SaveToFile("new_pdf.pdf", FileFormat.PDF)
workbook.Dispose()
