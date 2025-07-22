#conda activate allpy311, extras2, g4fpy311

import g4f
import pprint

with open("transcript.txt", "r", encoding='utf-8') as f:
    transcript = f.read()
# Вызов конечной точки openai ChatCompletion с помощью ChatGPT
response = g4f.ChatCompletion.create(
    model="gpt-4o-mini",
    messages=[
        {"role": "system", "content": "Ты полезный помощник."},
        {"role": "user", "content": "Резюмируй следующий текст"},
        {"role": "assistant", "content": "Да."},
        {"role": "user", "content": transcript},
    ]
)

#pprint.pprint(response["choices"][0]["message"]["content"])
#print(response)
pprint.pprint(response)  # или просто print(response)