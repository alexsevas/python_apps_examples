# Поиск геолокации по IP-адресу

import requests

def get_ip_info(ip_address):
    try:
        response = requests.get(f"http://ip-api.com/json/{ip_address}")
        data = response.json()

        if data['status'] == 'success':
            print(f"🌍 IP: {ip_address}")
            print(f"🗺️ Страна: {data['country']}")
            print(f"🏙️ Город: {data['city']}")
            print(f"🛰️ Провайдер: {data['isp']}")
            print(f"🧭 Координаты: {data['lat']}, {data['lon']}")
        else:
            print("❌ Не удалось определить данные.")
    except Exception as e:
        print("⚠️ Ошибка:", e)

# 🔹 Пример использования
get_ip_info("8.8.8.8")  # Google DNS
