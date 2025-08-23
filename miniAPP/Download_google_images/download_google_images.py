# conda activate allpy311

import os
import requests
from bs4 import BeautifulSoup

def download_google_images(query, folder="images", limit=10):
    os.makedirs(folder, exist_ok=True)
    url = "https://www.google.com/search"
    params = {"q": query, "tbm": "isch"}
    headers = {"User-Agent": "Mozilla/5.0"}
    resp = requests.get(url, params=params, headers=headers)
    soup = BeautifulSoup(resp.text, "html.parser")
    imgs = soup.find_all("img")[:limit]

    for i, img in enumerate(imgs, 1):
        src = img.get("src")
        if not src:
            continue
        img_data = requests.get(src).content
        path = os.path.join(folder, f"{query.replace(' ', '_')}_{i}.jpg")
        with open(path, "wb") as f:
            f.write(img_data)
        print(f"✅ Скачал: {path}")

if __name__ == "__main__":
    download_google_images("cats", limit=5)
