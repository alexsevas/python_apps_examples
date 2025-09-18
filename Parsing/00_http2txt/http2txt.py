# conda activate allpy310

# pip install beautifulsoup4 requests lxml

import requests
from bs4 import BeautifulSoup
import json
import csv

# парсим страницу и сохраняем ее в index.html
url = "https://habr.com/ru/hubs/python/articles/"

headers = {
    "Accept": "*/*",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 YaBrowser/24.7.0.0 Safari/537.36"
}

req = requests.get(url, headers=headers)
src = req.text

#print(src)

with open("index.html", "w", encoding="utf-8") as file:
    file.write(src)
