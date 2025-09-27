# ИИ-агент для парсинга сайтов и извлечения данных
# Агент скачивает страницу, извлекает текст и с помощью ИИ ищет нужную информацию по запросу.

# pip install requests beautifulsoup4 openai

import requests
from bs4 import BeautifulSoup
import openai

openai.api_key = "YOUR_OPENAI_API_KEY"

def web_parser_agent(url, query, model="gpt-3.5-turbo"):
    res = requests.get(url)
    soup = BeautifulSoup(res.text, "html.parser")
    text = soup.get_text(separator="\n")

    prompt = (
        f"Вот текст с сайта:\n{text[:4000]}\n\n"
        f"Извлеки нужную информацию по запросу: {query}"
    )

    response = openai.ChatCompletion.create(
        model=model,
        messages=[
            {"role": "system", "content": "Ты агент для извлечения информации с веб-страниц."},
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message.content

if __name__ == "__main__":
    url = input("URL: ")
    query = input("Что извлечь: ")
    result = web_parser_agent(url, query)
    print("Результат:\n", result)