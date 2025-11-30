# Генерируем мультикартинку в стиле Pixar с помощью OpenAI + PIL

# pip install openai pillow requests

# - Берёт твоё фото, стилизует его под мультяшку и показывает
# - Используется openai, PIL, requests
# - Нужно своё фото (портрет) и OpenAI API-ключ
# - Работает на GPT-4+ DALL·E через OpenAI API


from PIL import Image, ImageDraw, ImageFont
import openai
import requests
from io import BytesIO

openai.api_key = "sk-..."  # вставь свой ключ

def cartoonify(image_url, style="Pixar-style 3D render"):
    response = openai.Image.create_variation(
        image=openai.Image.create_edit(
            image=openai.Image.from_url(image_url),
            prompt=style,
            n=1,
            size="512x512"
        )
    )
    return response['data'][0]['url']

img_url = "https://i.imgur.com/your_photo.jpg"  # замени на своё фото
new_img_url = cartoonify(img_url)

img = Image.open(BytesIO(requests.get(new_img_url).content))
img.show()
