# pip install cloudscraper

# Cloudflare - библиотека для парсинга данных с обходом защиты
# Пример использования


import cloudscraper

# Создаем объект Cloudscraper
scraper = cloudscraper.create_scraper()

# Отправляем запрос
response = scraper.get("https://www.google.com")

# Выводим содержимое ответа
print(response.content)
