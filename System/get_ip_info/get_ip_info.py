# Скрипт на Python для быстрого получения информации об IP-адресе или домене прямо из терминала
# Использует API сервиса ipinfo.io для получения данных об IP: страна, город, провайдер, ASN, координаты.


import requests
import argparse

def get_ip_info(ip):
    url = f"https://ipinfo.io/{ip}/json"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        for k, v in data.items():
            print(f"{k}: {v}")
    else:
        print("Ошибка запроса")

if name == "__main__":
    parser = argparse.ArgumentParser(description="IPinfo Lookup Script")
    parser.add_argument("ip", help="IP или домен для проверки")
    args = parser.parse_args()
    get_ip_info(args.ip)
