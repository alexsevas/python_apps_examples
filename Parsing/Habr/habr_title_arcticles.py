# парсинг названий статей с первй страницы выбранного хаба (переменная url)

import requests
from bs4 import BeautifulSoup

def get_python_articles():
    url = "https://habr.com/ru/hubs/python/articles/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    }

    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"❌ Ошибка при загрузке страницы: {e}")
        return []

    soup = BeautifulSoup(response.text, 'html.parser')

    # Находим все статьи на странице
    articles = soup.find_all('article', {'class': lambda x: x and 'tm-articles-list__item' in x})

    if not articles:
        print("⚠️  Не найдено ни одной статьи. Возможно, изменилась разметка или требуется авторизация.")
        return []

    article_titles = []

    for article in articles:
        # Извлекаем заголовок
        title_tag = article.find('a', class_='tm-title__link')
        if not title_tag:
            continue

        title = title_tag.get_text(strip=True)
        article_titles.append(title)

    return article_titles


def main():
    print("🔍 Сканируем статьи в хабе Python...\n")
    titles = get_python_articles()

    if not titles:
        print("❌ Не удалось получить статьи.")
        print("ℹ️  Проверьте доступ к странице: https://habr.com/ru/hubs/python/articles/")
        return

    print(f"✅ Найдено {len(titles)} статей:\n")
    for i, title in enumerate(titles, 1):
        print(f"{i}. {title}")

    print(f"\n📈 Всего: {len(titles)} статей на текущей странице.")


if __name__ == "__main__":
    main()

'''
🔍 Сканируем статьи в хабе Python...

✅ Найдено 20 статей:

1. Обзор WSGI, ASGI и RSGI: лидеры среди веб-серверов в 2025 году
2. Как написать свой TCP-порт-сканер на Python: опыт, код и примеры использования
3. Дженерики в Python, простыми словами
4. Тысячи асинхронных задач в секунду в облачных s3 на Rust/Axum/Tokio: шлифуем ржавчину до блеска
5. Как я сделал школьного бота в Telegram — и почему проект пришлось закрыть
6. Топ-6 Python-библиотек для визуализации
7. «Большие вызовы»: как школьники за 3 недели собрали модуль для офлайн-распознавания документов на Android
8. ИИ в 3 фазы… снижение рисков, экономия времени и помощь человеку. Но ...— нужно дать пользу уже на первом шаге
9. Telegram бот управления Docker контейнерами
10. Как избавиться от проприетарных ETL: кейс миграции на dbt
11. Агрегация и парсинг XML RSS ленты на Python
12. Prompt Engineering: Паттерны проектирования. Часть 2 — ToDo list
13. Снятие проклятия размерности: как познакомиться со своими данными
14. Что если представить habr в виде obsidian-графа?
15. Автоматизация геозадач: как NextGIS Web и open source экономят время
16. Что такое эмбеддинги и как с ними работать. Вводная для начинающих
17. Кольца Барромео и один забавный алгоритмический баг
18. Меньше магии, больше кода: мой способ писать Django views
19. Коротко об устройстве протокола MSK144 с примерами на Python
20. Прокачиваем RAG: тестируем техники и считаем их эффективность. Часть 1
'''