import os
import requests
from bs4 import BeautifulSoup


def download_images(query, num_images=10, dest_folder="images"):
    # Создаем папку
    os.makedirs(dest_folder, exist_ok=True)

    # URL поиска
    search_url = f"https://www.google.com/search?tbm=isch&q={query}"

    # User-Agent обязателен, иначе Google вернет ошибку или пустую страницу
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
    }

    try:
        resp = requests.get(search_url, headers=headers)
        resp.raise_for_status()  # Проверка на ошибки HTTP
    except Exception as e:
        print(f"Ошибка доступа к Google: {e}")
        return

    soup = BeautifulSoup(resp.text, "html.parser")
    img_tags = soup.find_all("img")

    count = 0
    for img in img_tags:
        # Пропускаем счетчик запросов Google, если попадается, и ищем реальный URL
        # Обычно в простом HTML Google кладет картинку в src, но иногда она может быть в data-src
        img_url = img.get("src")

        # Фильтрация: пропускаем пустые и не HTTP ссылки (например, base64 иконки)
        if not img_url or not img_url.startswith("http"):
            continue

        # Google часто возвращает логотипы или иконки интерфейса, фильтруем их по ключевым словам url
        # Ссылки на картинки обычно содержат 'images' или 'gstatic'
        if "gstatic" not in img_url and "googleusercontent" not in img_url:
            continue

        filename = f"{query}_{count}.jpg"
        filepath = os.path.join(dest_folder, filename)

        try:
            img_data = requests.get(img_url, timeout=10).content
            with open(filepath, "wb") as f:
                f.write(img_data)
            print(f"Downloaded: {filename}")
            count += 1

            if count >= num_images:
                break
        except Exception as e:
            print(f"Error downloading {img_url}: {e}")
            continue

    if count == 0:
        print("Не удалось найти или скачать изображения. Возможно, Google изменил верстку.")


if __name__ == "__main__":
    download_images("sunset", num_images=15)