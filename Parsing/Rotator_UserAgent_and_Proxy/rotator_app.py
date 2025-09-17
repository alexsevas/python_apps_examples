'''
Cкрипт, случайно чередующий User-Agent и прокси для каждого запроса,
чтобы обойти блокировки и ограничители при массовом сборе данных

Возможности скрипта:
- С рандомным User-Agent из списка для каждого HTTP-запроса
- Использует список прокси, отдавая по одному на каждый запрос
- Повышает анонимность: меняется IP + заголовки
- Полезен для OSINT, скрейпинга, разведки и обхода банов
'''

# python rotator_app.py urls.txt user_agents.txt proxies.txt

import requests, random
from itertools import cycle
import argparse

def load_list(path):
    with open(path, encoding='utf-8') as f:
        return [l.strip() for l in f if l.strip()]

def main(urls_file, ua_file, proxy_file, delay=1):
    urls = load_list(urls_file)
    uas = cycle(load_list(ua_file))
    proxies = cycle(load_list(proxy_file))

    for url in urls:
        ua = next(uas)
        proxy = next(proxies)
        headers = {'User-Agent': ua}
        proxy_dict = {'http': proxy, 'https': proxy}
        try:
            resp = requests.get(url, headers=headers, proxies=proxy_dict, timeout=10)
            print(f"[{resp.status_code}] {url} — UA: {ua[:30]}... via {proxy}")
        except Exception as e:
            print(f"❌ {url} — fail: {e}")
        time.sleep(delay)

if __name__ == '__main__':
    p = argparse.ArgumentParser("UA + Proxy Rotator")
    p.add_argument("urls", help="File with URLs list")
    p.add_argument("uas", help="File with User-Agent strings")
    p.add_argument("proxies", help="File with proxies (host:port)")
    p.add_argument("--delay", type=int, default=1, help="Delay between requests (s)")
    args = p.parse_args()
    main(args.urls, args.uas, args.proxies, args.delay)
