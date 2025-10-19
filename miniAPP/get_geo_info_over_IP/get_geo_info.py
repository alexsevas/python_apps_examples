# conda activate allpy311
# pip install requests

# Код для получения информации о геолокации по IP-адресу на Python

import requests


def get_geo_info(ip_address):
    # Формируем URL для запроса к API
    url = f"http://ip-api.com/json/{ip_address}"
    # Отправляем GET-запрос к API
    response = requests.get(url)
    # Сохраняем ответ в формате JSON
    data = response.json()
    return data


# Вызываем функцию get_geo_info() и указываем IP-адрес
geo_info = get_geo_info("77.78.55.242")

# Выводим информацию о геолокации
for key, value in geo_info.items():
    print(key, ":", value)

# Вывод:
# status : success
# country : Bulgaria
# countryCode : BG
# region : 18
# regionName : Ruse
# city : Rousse
# zip : 7000
# lat : 43.8627
# lon : 25.9648
# timezone : Europe/Sofia
# isp : NETWORX-BG Ltd. - Charodeika South
# org :
# as : AS8866 Vivacom Bulgaria EAD
# query : 77.78.55.242