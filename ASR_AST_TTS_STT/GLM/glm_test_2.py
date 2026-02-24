import requests

# 1. Убрали лишние пробелы в конце URL
url = "https://api.routeway.ai/v1/chat/completions"

headers = {
    "Authorization": "Bearer YOUR_API_KEY",  # ЗАМЕНИТЕ НА ВАШ РЕАЛЬНЫЙ КЛЮЧ
    "Content-Type": "application/json"
}

payload = {
    "model": "glm-4.7",
    "messages": [
        {"role": "user", "content": "Привет, расскажи о Routeway API"}
    ],
    "stream": False
}

try:
    response = requests.post(url, headers=headers, json=payload)

    # 2. Печатаем статус и сырой текст ответа для отладки
    print(f"Status Code: {response.status_code}")
    print(f"Response Text: {response.text}")

    # 3. Проверяем, успешен ли запрос (код 200-299)
    if response.status_code == 200:
        data = response.json()
        print("\nОтвет модели:")
        print(data['choices'][0]['message']['content'])
    else:
        print(f"\nОшибка сервера: {response.status_code}")
        print("Вероятно, неверный API ключ, модель или URL.")

except requests.exceptions.JSONDecodeError as e:
    print(f"\nОшибка декодирования JSON: {e}")
    print("Сервер вернул не JSON. Посмотрите 'Response Text' выше.")
except Exception as e:
    print(f"\nПроизошла другая ошибка: {e}")