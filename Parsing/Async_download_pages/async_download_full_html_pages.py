# Код, который сохраняет содержимое каждой страницы в отдельный файл в подпапке "data"
# pip install aiohttp

'''
- Добавлены необходимые импорты: os для работы с файловой системой и re для очистки имен файлов
- Функция sanitize_filename: Очищает URL от недопустимых символов для файловой системы и создает понятное имя файла
- Создание папки: os.makedirs('data', exist_ok=True) создает папку data, если она не существует
- Сохранение файлов: Для каждой успешно загруженной страницы:
  - Генерируется уникальное имя файла на основе URL
  - Создается полный путь к файлу в папке data
  - Содержимое страницы записывается в файл с кодировкой UTF-8
- Информативные сообщения: Выводится информация о сохранении каждого файла

Если в URL есть специальные символы (например, https://example.com/path?query=1), они будут заменены на подчеркивания,
и получится что-то вроде data/example.com_path_query_1.html
'''


import asyncio
import aiohttp
from aiohttp import ClientError
import os
import re


async def fetch(session, url):
    try:
        async with session.get(url) as response:
            return await response.text()
    except ClientError as e:
        print(f"Ошибка при загрузке {url}: {e}")
        return None


async def download_pages(urls):
    async with aiohttp.ClientSession() as session:
        tasks = [fetch(session, url.strip()) for url in urls]
        return await asyncio.gather(*tasks)


def sanitize_filename(url):
    """Очистка URL для использования в качестве имени файла"""
    # Удаляем протокол и оставляем только домен и путь
    clean_url = re.sub(r'^https?://', '', url.strip())
    # Заменяем недопустимые символы для файловой системы
    clean_url = re.sub(r'[<>:"/\\|?*]', '_', clean_url)
    # Ограничиваем длину имени файла
    return clean_url[:100] + '.html'


async def main():
    urls = [
        "https://ya.ru",
        "https://google.com",
        "https://chat.qwen.ai"
    ]

    # Создаем папку data если она не существует
    os.makedirs('data', exist_ok=True)

    pages = await download_pages(urls)

    for i, page in enumerate(pages):
        url = urls[i].strip()
        if page:
            # Генерируем имя файла из URL
            filename = sanitize_filename(url)
            filepath = os.path.join('data', filename)

            # Сохраняем содержимое в файл
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(page)

            print(f"Содержимое страницы {url} сохранено в {filepath}")
        else:
            print(f"Не удалось загрузить страницу {url}")


asyncio.run(main())