import requests

url = "https://api.routeway.ai/v1/chat/completions"
headers = {
    "Authorization": "Bearer YOUR_API_KEY",
    "Content-Type": "application/json"
}
payload = {
    "model": "glm-4.7",  # Или "glm-4.5-air:free" для бесплатной
    "messages": [
        {"role": "user", "content": "Привет, расскажи о Routeway API"}
    ],
    "stream": False  # True для стриминга
}
response = requests.post(url, headers=headers, json=payload)
print(response.json()['choices'][0]['message']['content'])