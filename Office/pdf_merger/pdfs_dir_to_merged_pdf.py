# conda activate allpy311

# pip install PyPDF2

'''
Программа объединяет все PDF-файлы из указанной папки в один итоговый документ:
- Ищет все файлы .pdf в указанной директории
- Объединяет их в порядке сортировки по имени в единственный PDF
- Сохраняет итоговое объединение в указанное имя файла

Модули: PyPDF2, argparse, os

Пример использования (CLI):
python pdf_merger.py --input-dir ./pdfs --output merged_all.pdf
'''

import os
import argparse
from PyPDF2 import PdfMerger

def merge_pdfs(input_dir, output_file):
    merger = PdfMerger()
    pdf_files = sorted([
        f for f in os.listdir(input_dir)
        if f.lower().endswith('.pdf')
    ])
    for pdf in pdf_files:
        path = os.path.join(input_dir, pdf)
        merger.append(path)
        print(f"✅ Appended: {pdf}")
    merger.write(output_file)
    merger.close()
    print(f"📄 Merged into: {output_file}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Bulk PDF Merger")
    parser.add_argument('--input-dir', required=True, help='Папка с PDF')
    parser.add_argument('--output', required=True, help='Имя итогового PDF')
    args = parser.parse_args()
    merge_pdfs(args.input_dir, args.output)
