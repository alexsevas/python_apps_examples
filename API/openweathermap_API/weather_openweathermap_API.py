# conda activate allpy311

# pip install requests

# Получает текущую погоду в указанном городе через OpenWeatherMap API

import requests

API_KEY = "your_openweathermap_api_key"
CITY = "Moscow"
URL = f"http://api.openweathermap.org/data/2.5/weather?q={CITY}&appid={API_KEY}&units=metric&lang=ru"

def get_weather():
    res = requests.get(URL)
    if res.status_code == 200:
        data = res.json()
        print(f"Погода в {CITY}: {data['weather'][0]['description'].capitalize()}, {data['main']['temp']}°C")
    else:
        print("Ошибка при получении данных")

if __name__ == "__main__":
    get_weather()
