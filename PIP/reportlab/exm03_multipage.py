# pip install reportlab

# PDF — не только один лист
# Каждый вызов showPage() завершает текущую страницу и начинает следующую


from reportlab.pdfgen import canvas

def create_multipage_pdf(filename):
    c = canvas.Canvas(filename)

    for page_num in range(1, 4):
        c.drawString(100, 750, f"Page {page_num}")
        c.showPage()  # переход на новую страницу

    c.save()

create_multipage_pdf("multipage.pdf")
