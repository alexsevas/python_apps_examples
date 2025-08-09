# conda activate allpy311, allpy310

# Локальный (оффлайн) переводчик документов и текста (PDF, DOCX, TXT)

'''
Для установки библиотек, используемых в предоставленном коде, выполните следующие команды:

1. Базовые зависимости (обязательные для всех вариантов):
pip install pdfplumber docx2txt argostranslate

2. Для работы на CPU (стандартная установка):
# Установка CPU-версии PyTorch (автоматически подтянется через argostranslate)
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu

3. Для работы на GPU (требуется CUDA 11.8+):
# Установка GPU-версии PyTorch
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121

# Проверьте доступность GPU в Python после установки:
python -c "import torch; print(torch.cuda.is_available())"
'''

import argostranslate.package, argostranslate.translate
import pdfplumber
import docx2txt
import os

def load_model(from_code="ru", to_code="en"):
    installed_languages = argostranslate.translate.get_installed_languages()
    from_lang = next(filter(lambda l: l.code == from_code, installed_languages), None)
    to_lang = next(filter(lambda l: l.code == to_code, installed_languages), None)
    return from_lang.get_translation(to_lang) if from_lang and to_lang else None

def extract_text(file_path):
    if file_path.endswith(".pdf"):
        with pdfplumber.open(file_path) as pdf:
            return "\n".join(page.extract_text() or "" for page in pdf.pages)
    elif file_path.endswith(".docx"):
        return docx2txt.process(file_path)
    elif file_path.endswith(".txt"):
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    else:
        raise ValueError("Неподдерживаемый формат")

def save_text(text, out_path):
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(text)

# Пример использования
file_path = "D:\\Projects\\Data\\PDF_DOC_DOCX_TXT_XML\\PDF_Для_перевода\\test_pdf_eng.pdf"
out_path = "translated_ru.txt"
translation = load_model("en", "ru")
text = extract_text(file_path)
translated = translation.translate(text)
save_text(translated, out_path)
print(f"✅ Перевод сохранён: {out_path}")
