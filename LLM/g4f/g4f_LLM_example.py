# conda activate extras2

import g4f
import pprint

# Автоматический выбор работающего провайдера
response = g4f.ChatCompletion.create(
    model="gpt-4o-mini",
    messages=[{"role": "user", "content": "Привет! Что ты за модель? Ответь точно и конкретно, не увиливая от вопроса. Спасибо!"}]
)

pprint.pprint(response)