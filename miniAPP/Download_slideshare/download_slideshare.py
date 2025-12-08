
# Утилита, которая позволяет скачивать презентации (Slideshare) в виде PDF или изображений, удобно сохранять копии слайдов.
# Если видишь полезную презентацию, которую хочешь держать офлайн — этот скрипт может помочь.
# - Загружает HTML страницы Slideshare
# - Парсит HTML и извлекает ссылки на изображения слайдов

import requests
from bs4 import BeautifulSoup
import os

def download_slideshare(slide_url, output_dir="slides"):
    os.makedirs(output_dir, exist_ok=True)
    resp = requests.get(slide_url)
    soup = BeautifulSoup(resp.text, "html.parser")
    # найти контейнер со слайдами, получить ссылки на изображения слайдов
    img_tags = soup.select("img.slide_image")  # пример селектора
    for idx, img in enumerate(img_tags):
        img_url = img.get("data-full") or img.get("src")
        if not img_url:
            continue
        ext = img_url.split('.')[-1]
        fname = f"slide_{idx}.{ext}"
        path = os.path.join(output_dir, fname)
        r = requests.get(img_url)
        with open(path, "wb") as f:
            f.write(r.content)
        print("Downloaded:", fname)

if __name__ == "__main__":
    url = "https://www.slideshare.net/some-presentation"
    download_slideshare(url)
