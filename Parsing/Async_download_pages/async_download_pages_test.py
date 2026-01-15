# Асинхронное скачивание веб-страниц с помощью asyncio
# pip install aiohttp

'''
Этот код позволяет асинхронно загружать несколько веб-страниц одновременно, что может существенно повысить скорость
выполнения задачи по сравнению с последовательными HTTP-запросами. Он подходит для ситуаций, когда требуется обработка
большого количества запросов с минимальной задержкой, например, при создании веб-скрейперов или загрузке данных из API
'''

import asyncio
import aiohttp
from aiohttp import ClientError

async def fetch(session, url):
    try:
        async with session.get(url) as response:
            return await response.text()
    except ClientError as e:
        print(f"Ошибка при загрузке {url}: {e}")
        return None

async def download_pages(urls):
    async with aiohttp.ClientSession() as session:
        tasks = [fetch(session, url.strip()) for url in urls]  # Создаем задачи для каждой URL
        return await asyncio.gather(*tasks)

# Пример использования
urls = [
    "https://ya.ru",
    "https://google.com",
    "https://chat.qwen.ai"
]

async def main():
    pages = await download_pages(urls)
    for i, page in enumerate(pages):
        if page:
            print(f"Содержимое страницы {urls[i]} загружено.")
        else:
            print(f"Не удалось загрузить страницу {urls[i]}.")

asyncio.run(main())