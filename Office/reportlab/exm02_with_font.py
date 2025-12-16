# pip install reportlab

# Добавляем шрифт и несколько строк
# Можно управлять шрифтами и цветами.

from reportlab.pdfgen import canvas
from reportlab.lib.colors import blue, red

def create_styled_pdf(filename):
    c = canvas.Canvas(filename)

    c.setFont("Helvetica-Bold", 20)
    c.setFillColor(blue)
    c.drawString(100, 780, "Invoice #42")

    c.setFont("Helvetica", 12)
    c.setFillColor(red)
    c.drawString(100, 750, "Customer: John Smith")
    c.drawString(100, 730, "Total: $199.99")

    c.save()

create_styled_pdf("invoice.pdf")
