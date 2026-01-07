'''
Скрипт для суммирования общего количества страниц во всех PDF-файлах в указанной директории

# Пример запуска:
# python pdf_page_count.py /path/to/folder

Если запустить скрипт без аргументов — он проходит по текущей папке и подсчитывает суммарное число страниц во всех .pdf файлах.
Если передать путь к одному PDF-файлу или папке — подсчитывает страницы только там.
Выводит итоговый результат в консоль: имя файла / количество страниц / суммарное число страниц.
'''


import re, os, glob, sys

rxcountpages = re.compile(r"/Type\s*/Page([^s]|$)", re.MULTILINE|re.DOTALL)

def count_pages(filename):
    data = file(filename,"rb").read()
    return len(rxcountpages.findall(data))

def sum_pages(args):
    if len(args) > 1:
        if args[1].endswith(".pdf"):
            return count_pages(args[1])
        else:
            os.chdir(args[1])
    total_pages = 0
    fnames = glob.glob("./*.pdf")
    for fname in fnames:
        total_pages = total_pages + count_pages(fname)
    return total_pages

if __name__=="__main__":
    print(sum_pages(sys.argv))