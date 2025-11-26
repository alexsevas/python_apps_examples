import requests

API_KEY = "___"

url = "https://openrouter.ai/api/v1/chat/completions"

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "HTTP-Referer": "http://localhost",
    "X-Title": "My Python Script"
}

payload = {
    "model": "google/gemma-2-9b-it",
    "messages": [
        {"role": "user", "content": "Привет! Объясни, как работает OpenRouter в Python."}
    ]
}

response = requests.post(url, headers=headers, json=payload)
print(response.json()["choices"][0]["message"]["content"])
