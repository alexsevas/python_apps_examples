# pip install reportlab

# Создадим файл hello.pdf с одной строкой текста
# - Координаты считаются в поинтах (1/72 дюйма), (0, 0) — левый нижний угол.
# - save() обязателен, иначе файл будет пустым.

from reportlab.pdfgen import canvas

def create_simple_pdf(filename):
    c = canvas.Canvas(filename)
    c.drawString(100, 750, "Hello, ReportLab!")
    c.save()

create_simple_pdf("hello.pdf")
