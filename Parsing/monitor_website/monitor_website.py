# Автоматизированная система мониторинга веб-сайтов с BeautifulSoup и Selenium
# Необходимо скачать и указать путь к chromedriver для корректной работы Selenium.

# pip install beautifulsoup4 selenium requests


from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import requests
import time

def get_page_content(url: str) -> str:
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.text
    except requests.RequestException as e:
        print(f"Ошибка при получении содержимого страницы: {e}")
        return ""

def parse_content(html: str) -> str:
    soup = BeautifulSoup(html, 'html.parser')
    title = soup.find('title').text if soup.find('title') else 'Заголовок не найден'
    return title

def monitor_website(url: str, check_interval: int):
    content = get_page_content(url)
    current_title = parse_content(content)
    print(f"Начальный заголовок: {current_title}")

    options = Options()
    options.headless = True
    service = Service('/path/to/chromedriver')
    driver = webdriver.Chrome(service=service, options=options)
    driver.get(url)

    try:
        while True:
            driver.refresh()
            new_content = driver.page_source
            new_title = parse_content(new_content)
            if new_title != current_title:
                print(f"Содержание сайта изменилось! Новый заголовок: {new_title}")
                current_title = new_title
            time.sleep(check_interval)
    except Exception as e:
        print(f"Ошибка во время мониторинга: {e}")
    finally:
        driver.quit()

# Пример использования
monitor_website("https://example.com", check_interval=60)
