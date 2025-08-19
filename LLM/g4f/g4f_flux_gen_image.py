# conda activate allpy311

# Для генерации изображения в коде используется библиотека g4f, а для скачивания - requests.
# pip install g4f requests

import requests
from g4f.client import Client

# Запрашиваем у пользователя текстовое описание (промпт) для генерации изображения
prompt = input("Введите описание изображения: ")

# Создаём экземпляр клиента
client = Client()

# Отправляем запрос на генерацию изображения по заданному промпту
response = client.images.generate(
    model="flux",
    prompt=prompt,
    response_format="url"
)

# Получаем URL сгенерированного изображения
image_url = response.data[0].url
print(f"URL сгенерированного изображения: {image_url}")

# Загружаем изображение по полученному URL
image_data = requests.get(image_url).content

# Сохраняем изображение
with open("generated_image.jpg", "wb") as file:
    file.write(image_data)

print("Изображение сохранено как generated_image.jpg")
