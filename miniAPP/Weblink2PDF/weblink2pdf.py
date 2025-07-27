# conda activate allpy311
# pip install pyppdf pyppeteer


# python weblink2pdf.py -l https://habr.com/ru/articles/931296/ -n habr.pdf

'''
Код для парсинга страниц по их URL с сохранением в PDF на Python
Для парсинга и сохранения страницы в PDF-файл в коде используются библиотеки pyppdf и pyppeteer.
'''
import argparse
import pyppdf
import re
from pyppeteer.errors import PageError, TimeoutError, NetworkError


def main():
    parser = argparse.ArgumentParser(description='Загрузка страницы в формате PDF')
    parser.add_argument('--link', '-l', action='store', dest='link',
                        required=True, help='Укажите ссылку на страницу.')
    parser.add_argument('--name', '-n', action='store', dest='name',
                        required=False, help='Укажите имя файла для сохранения.')

    arguments = parser.parse_args()

    url = arguments.link

    if not arguments.name:
        name = re.sub(r'^\w+://', '', url.lower())
        name = name.replace('/', '-')
    else:
        name = arguments.name

    if not name.endswith('.pdf'):
        name = name + '.pdf'

    print(f'Имя файла: {name}')

    try:
        pyppdf.save_pdf(name, url)
    except PageError:
        print('Не удалось загрузить страницу.')
    except TimeoutError:
        print('Тайм-аут.')
    except NetworkError:
        print('Нет доступа к сети.')


if __name__ == '__main__':
    main()


'''
При первом запуске:

[WARNING] Start patched secure https Chromium download from URL:
https://storage.googleapis.com/chromium-browser-snapshots/Win_x64/800229/chrome-win.zip
Download may take a few minutes.
160 Mb
[WARNING] 
chromium download done.
[INFO] Beginning extraction
[INFO] Chromium extracted to: C:\Users\------\AppData\Local\pyppeteer\pyppeteer\local-chromium\800229
'''