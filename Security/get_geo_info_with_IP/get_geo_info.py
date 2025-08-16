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
geo_info = get_geo_info("14.81.23.35")

# Выводим информацию о геолокации
for key, value in geo_info.items():
    print(key, ":", value)

'''
# Вывод:
status : success
country : South Korea
countryCode : KR
region : 41
regionName : Gyeonggi-do
city : Seongnam-si
zip : 13606
lat : 37.3654
lon : 127.122
timezone : Asia/Seoul
isp : Korea Telecom
org : Kornet
as : AS4766 Korea Telecom
query : 14.81.23.35
'''