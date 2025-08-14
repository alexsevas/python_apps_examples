# conda activate allpy311

# Проверка подписания PDF-документа (наличие цифровой подписи)
# Для более надёжной проверки подписей рекомендуется использовать PyMuPDF (fitz).

import fitz  # pip install PyMuPDF

def is_pdf_signed(file_path):
    try:
        doc = fitz.open(file_path)
        # Проверяем наличие подписей
        for page in doc:
            for annot in page.annots():
                if annot.type[0] == 8:  # Тип 8 — это подпись
                    return True
        return False
    except Exception as e:
        print(f"Ошибка при проверке PDF: {e}")
        return False

if __name__ == '__main__':
    path = 'doc.pdf'
    if is_pdf_signed(path):
        print("🔐 Документ подписан")
    else:
        print("⚠️ Подпись не найдена")