# pip install plutoprint

# PlutoPrint — лёгкая и мощная Python-библиотека, которая конвертирует HTML/XML в качественные PDF и изображения.
# Основана на движке от PlutoBook, встроенные бинарники идут из коробки.
#
# ⌨️ CLI интерфейс
# Хочешь быстро сделать PDF из HTML?
# plutoprint input.html output.pdf --size=A4


import plutoprint

book = plutoprint.Book(plutoprint.PAGE_SIZE_A4)
book.load_url("hello.html")

# Весь документ
book.write_to_pdf("hello.pdf")

# Страницы 2–15
book.write_to_pdf("hello-range.pdf", 2, 15, 1)

# В обратном порядке
book.write_to_pdf("hello-reverse.pdf", 15, 2, -1)

# Ручной рендер
with plutoprint.PDFCanvas("hello-canvas.pdf", book.get_page_size()) as canvas:
    canvas.scale(plutoprint.UNITS_PX, plutoprint.UNITS_PX)
    for page_index in range(book.get_page_count() - 1, -1, -1):
        canvas.set_size(book.get_page_size_at(page_index))
        book.render_page(canvas, page_index)
        canvas.show_page()