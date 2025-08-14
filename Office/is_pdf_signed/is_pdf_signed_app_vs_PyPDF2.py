# conda activate allpy311

# Проверка подписания PDF-документа (наличие цифровой подписи)
# Проверяет, содержит ли PDF файл цифровую подпись (вида /Sig в полях формы). Подходит для автоматической валидации
# юридических или бухгалтерских документов.

from PyPDF2 import PdfReader


def is_pdf_signed(file_path):
    try:
        reader = PdfReader(file_path)

        # Получаем Root объект
        root = reader.trailer['/Root'].get_object()

        # Проверяем наличие AcroForm
        if '/AcroForm' not in root:
            return False

        acroform = root['/AcroForm'].get_object()

        # Проверяем наличие полей
        if '/Fields' not in acroform:
            return False

        fields = acroform['/Fields'].get_object()

        # Поля могут быть массивом или одиночным объектом
        if hasattr(fields, '__iter__') and not isinstance(fields, dict):
            # Если это список (массив полей)
            field_objects = [field.get_object() for field in fields]
        else:
            # Если только одно поле
            field_objects = [fields.get_object()]

        # Проверяем каждое поле
        for field in field_objects:
            ft = field.get('/FT')  # Теперь field — разыменованный словарь
            if ft == '/Sig':
                return True

    except Exception as e:
        print(f'Ошибка при проверке PDF: {e}')
        return False

    return False


if __name__ == '__main__':
    path = 'doc.pdf'
    if is_pdf_signed(path):
        print("🔐 Документ подписан")
    else:
        print("⚠️ Подпись не найдена")

'''
Заметки:
1) Не все подписи видны через /FT == /Sig
Некоторые PDF используют встроенные подписи (PAdES), которые могут быть скрыты или не представлены как поля формы.
Но в большинстве случаев, если PDF подписан через Adobe или аналоги — подпись будет в AcroForm.

2) PyPDF2 ограничен
PyPDF2 — устаревшая библиотека. Рассмотри переход на pypdf (её активно развивают, это форк PyPDF2) или PyMuPDF (fitz) — 
они мощнее и лучше работают с подписями.
Пример с pypdf: pip install pypdf
Код остаётся почти тем же, но pypdf — более стабильный форк.
'''