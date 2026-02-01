# Генерация отчетов в формате PDF с Python и ReportLab.
# Этот код демонстрирует базовый процесс создания PDF-документа с помощью библиотеки ReportLab. Скрипт генерирует отчет
# с заголовком и таблицей данных, что полезно для автоматизации отчетности в бизнесе.
# ReportLab позволяет легко добавлять текст, таблицы и графики в документы, упрощая создание профессиональных отчетов.
#
# pip install reportlab


from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch


def create_pdf(filename: str):
    try:
        c = canvas.Canvas(filename, pagesize=A4)
        width, height = A4

        # Заголовок
        c.setFont("Helvetica-Bold", 16)
        c.drawString(1 * inch, height - 1 * inch, "Отчет о продажах")

        # Таблица данных
        data = [("Продукт", "Количество", "Цена"),
                ("Продукт A", "10", "$100"),
                ("Продукт B", "20", "$200"),
                ("Продукт C", "15", "$150")]

        c.setFont("Helvetica", 12)
        y_position = height - 1.5 * inch
        for row in data:
            x_position = 1 * inch
            for item in row:
                c.drawString(x_position, y_position, item)
                x_position += 2 * inch
            y_position -= 0.5 * inch

        # Завершение
        c.showPage()
        c.save()
        print(f"PDF создан: {filename}")
    except Exception as e:
        print(f"Ошибка при создании PDF: {e}")


# Пример использования
create_pdf("sales_report.pdf")
