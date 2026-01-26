# Cкрипт, который скачивает все изображения из одного или нескольких сабреддитов.
# Удобен, если ты хочешь быстро собрать изображения по теме:
# - Делает HTTP-запрос к API Reddit (JSON)
# - Парсит посты, проверяет, есть ли в url изображения (.jpg/.png)
# - Скачивает найденные изображения в папку
# - Поддерживает указание количества постов через параметр limit
# - Печатает статус каждого скачанного файла


import os
import requests
import argparse

def download_subreddit_images(subreddit, limit=50, dest="downloads"):
    os.makedirs(dest, exist_ok=True)
    url = f"https://www.reddit.com/r/{subreddit}/.json?limit={limit}"
    headers = {"User-Agent": "Mozilla/5.0"}
    resp = requests.get(url, headers=headers)
    data = resp.json()

    for post in data.get("data", {}).get("children", []):
        img_url = post["data"].get("url")
        if img_url and (img_url.endswith(".jpg") or img_url.endswith(".png")):
            filename = os.path.basename(img_url)
            path = os.path.join(dest, filename)
            try:
                img_data = requests.get(img_url).content
                with open(path, "wb") as f:
                    f.write(img_data)
                print("Downloaded:", filename)
            except Exception as e:
                print("Ошибка скачивания", img_url, e)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Download images from subreddit")
    parser.add_argument("subreddit", help="Name of subreddit")
    parser.add_argument("--limit", type=int, default=20, help="How many posts to parse")
    parser.add_argument("--dest", default="downloads", help="Destination folder")
    args = parser.parse_args()

    download_subreddit_images(args.subreddit, limit=args.limit, dest=args.dest)
