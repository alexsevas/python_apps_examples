# Безопасное скачивание файла с логами и таймаутом


import requests
import logging
from pathlib import Path
from requests.exceptions import RequestException, Timeout

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

def download_file(url: str, dest: Path, timeout: float = 5.0):
    try:
        response = requests.get(url, stream=True, timeout=timeout)
        response.raise_for_status()

        dest.parent.mkdir(parents=True, exist_ok=True)
        with open(dest, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)

        logging.info(f"✅ Файл сохранён: {dest.resolve()}")
    except (RequestException, Timeout) as e:
        logging.error(f"❌ Ошибка при скачивании: {e}")

# Пример использования
download_file(
    url="https://github.com/datalab-to/chandra/archive/refs/heads/master.zip",
    dest=Path("./downloads/master.zip")
)
