# pip install reportlab

from reportlab.pdfgen import canvas

def create_simple_pdf(filename):
    c = canvas.Canvas(filename)
    c.drawString(100, 750, "Hello, ReportLab!")
    c.save()

create_simple_pdf("hello.pdf")
