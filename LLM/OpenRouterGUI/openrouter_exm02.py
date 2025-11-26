import requests
import dotenv
import os

dotenv.load_dotenv(dotenv_path="D:\Projects\Data\.env")
API_KEY = os.getenv('OPENROUTER_TOKEN')

url = "https://openrouter.ai/api/v1/chat/completions"

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "HTTP-Referer": "http://localhost",
    "X-Title": "My Python Script"
}

payload = {
    "model": "google/gemma-2-9b-it",
    "messages": [
        {"role": "user", "content": "Что ты за модель? Ответь подробно."}
    ]
}

response = requests.post(url, headers=headers, json=payload)
print(response.json()["choices"][0]["message"]["content"])
