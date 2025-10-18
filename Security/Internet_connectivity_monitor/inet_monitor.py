
# conda activate allpy311

# Скрипт периодически пингует выбранный IP/хост и логирует статус и задержки.
# Будет полезен, если хочешь видеть периоды провалов связи
# Работает под Win10x64

import subprocess
import time
import csv
import re
from datetime import datetime

HOST = "5.255.255.242"
INTERVAL = 10
LOG_FILE = "connectivity_log.csv"

def ping(host):
    cmd = ["ping", "-n", "1", "-w", "3000", host]
    try:
        # Важно: используем encoding='cp866' для корректного чтения русского вывода в Windows cmd
        result = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            encoding='cp866',  # <-- КЛЮЧЕВОЕ ИЗМЕНЕНИЕ
            errors='ignore'
        )
        return result
    except Exception as e:
        print(f"Ошибка ping: {e}")
        return None

def extract_latency(output):
    # Ищем "время=81мс" или "time=81ms" — поддержка обоих
    # Используем re.IGNORECASE и ищем число после "время" или "time"
    match = re.search(r'(?:время|time)[=\s<]*([0-9]+(?:\.[0-9]*)?)', output, re.IGNORECASE)
    if match:
        try:
            return float(match.group(1))
        except (ValueError, IndexError):
            pass
    return None

def main():
    # Создаём CSV с заголовком
    try:
        with open(LOG_FILE, "x", newline="", encoding="utf-8") as f:
            csv.writer(f).writerow(["timestamp", "status", "latency_ms"])
    except FileExistsError:
        pass

    while True:
        ts = datetime.now().isoformat()
        result = ping(HOST)

        if result is None:
            status, latency = "error", None
        elif result.returncode == 0:
            latency = extract_latency(result.stdout)
            status = "online" if latency is not None else "online_no_latency"
        else:
            status, latency = "outage", None

        # Логгирование
        with open(LOG_FILE, "a", newline="", encoding="utf-8") as f:
            csv.writer(f).writerow([ts, status, latency])

        print(f"{ts} — {status} — {latency} ms")
        time.sleep(INTERVAL)

if __name__ == "__main__":
    main()



'''
- Пингует указанный хост с интервалом
- Определяет, отвечает ли хост (если нет — “outage”)
- Если ответ — парсит задержку (ms)
- Записывает лог в формате CSV: временная метка, статус, задержка
- Выводит в консоль текущее состояние
- encoding='cp866' — правильно декодирует русский текст из cmd (включая слово «время»)
- Игнорирует регистр (re.IGNORECASE)
- Ловит целые числа (81) и дробные (12.5), если вдруг появятся.
- Работает с время=81мс, time=15ms, время<1мс и т.п.

Вывод:
2025-10-18T12:34:28.031723 — online — 50.0 ms
'''