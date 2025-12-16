# pip install reportlab

# Таблица с использованием platypus
# Для отчетов удобен модуль platypus (он входит в ReportLab)


from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from reportlab.lib import colors

def create_table_pdf(filename):
    doc = SimpleDocTemplate(filename)
    data = [
        ["Name", "Quantity", "Price"],
        ["Apples", 3, "$5"],
        ["Oranges", 5, "$7"],
        ["Bananas", 2, "$4"],
    ]

    table = Table(data)
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.black),
        ("ALIGN", (1, 1), (-1, -1), "CENTER"),
    ]))

    doc.build([table])

create_table_pdf("table_report.pdf")
