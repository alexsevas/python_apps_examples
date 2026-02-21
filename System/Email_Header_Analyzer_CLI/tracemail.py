# Email Header Analyzer CLI
# Скрипт для разбора email-заголовков (.eml или простого текста), с возможностью видеть путь сообщения, промежуточные
# хосты, шифт времени и метрики по hop delay
# - Работает через Python, минимум зависимостей (python-dateutil + стандартная библиотека)
# - Показывает маршрут письма (hop chain), включая IP, Host, время задержки
# - CLI-интерфейс: передаёшь файл — получаешь аналитику в терминале
# - Лёгкий, быстрый, без GUI, прямо как для тебя надо

# pip install python-dateutil

# Пример использования (CLI):
# ./tracemail.py -r email_sample.eml
# # — покажет список hop’ов: от кого до кого, IP, delay в секундах


#!/usr/bin/env python3
import sys
from email import message_from_file
from datetime import datetime
from dateutil import parser as dateparser

def parse_hops(email_path):
    msg = message_from_file(open(email_path, encoding='utf-8'))
    received = msg.get_all('Received') or []
    hops = []
    for header in received:
        parts = header.split(';')
        from_part = parts[0].strip()
        date_part = parts[-1].strip()
        try:
            ts = dateparser.parse(date_part)
        except:
            ts = None
        hops.append((from_part, ts))
    return hops

def print_hops(hops):
    for i in range(len(hops)-1):
        src, t1 = hops[i]
        _, t2 = hops[i+1]
        delay = (t1 - t2).total_seconds() if t1 and t2 else '?'
        print(f"Hop {i+1}: {src} — Delay: {delay}s")
    if hops:
        print(f" final hop: {hops[-1][0]}")

if __name__ == '__main__':
    if len(sys.argv) < 3 or sys.argv[1] != '-r':
        print("Usage: tracemail.py -r <email_file>")
        sys.exit(1)
    hops = parse_hops(sys.argv[2])
    print_hops(hops)
