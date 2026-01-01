'''
Phone Number Info + Map Generator

Скрипт разборчиво показывает детали по номеру телефона: геолокацию, поставщика, часовой пояс и метаданные. И всё это
выводится красиво и понятно, с возможностью сразу строить карту рядом с исполнением — удобно для быстрого OSINT-анализа.

Модули: phonenumbers, folium, opencage (при наличии API-ключа), argparse, colorama
pip install phonenumbers folium opencage colorama

- Парсит номер, определяет страну, тип номера (мобила/стационар), часовой пояс и оператора — через phonenumbers
- При наличии ключа OpenCage — преобразует локацию в координаты и строит интерактивную карту через folium, сохраняет как HTML
- Выделяет важные части цветом через colorama, чтобы сразу видеть страну, оператора и локацию — сок в UX

Использование:
python phone_info.py --number "+1234567890" --map --key YOUR_OPENCAGE_API_KEY
'''


import argparse
import phonenumbers
from phonenumbers import geocoder, carrier, timezone
import folium
from opencage.geocoder import OpenCageGeocode
from colorama import init, Fore

init()

def get_info(number):
    pn = phonenumbers.parse(number)
    info = {
        "formatted": phonenumbers.format_number(pn, phonenumbers.PhoneNumberFormat.INTERNATIONAL),
        "country": geocoder.description_for_number(pn, "en"),
        "carrier": carrier.name_for_number(pn, "en"),
        "timezone": timezone.time_zones_for_number(pn)
    }
    return info

def create_map(location_name, api_key, output="map.html"):
    geocoder = OpenCageGeocode(api_key)
    results = geocoder.geocode(location_name)
    if results:
        lat, lng = results[0]['geometry']['lat'], results[0]['geometry']['lng']
        m = folium.Map(location=[lat, lng], zoom_start=7)
        folium.Marker([lat, lng], popup=location_name).add_to(m)
        m.save(output)
        return output
    return None

if __name__ == "__main__":
    p = argparse.ArgumentParser("Phone Info with Map")
    p.add_argument("--number", required=True, help="Phone number with country code")
    p.add_argument("--map", action="store_true", help="Generate map HTML")
    p.add_argument("--key", help="OpenCage API key for map")
    args = p.parse_args()

    info = get_info(args.number)
    print(f"{Fore.GREEN}Number: {info['formatted']}")
    print(f"{Fore.CYAN}Country: {info['country']}")
    print(f"{Fore.YELLOW}Carrier: {info['carrier']}")
    print(f"{Fore.MAGENTA}Timezone: {', '.join(info['timezone'])}")

    if args.map and args.key:
        path = create_map(info['country'], args.key)
        if path:
            print(f"{Fore.BLUE} Map saved to: {path}")
        else:
            print(f"{Fore.RED}Failed to generate map")
