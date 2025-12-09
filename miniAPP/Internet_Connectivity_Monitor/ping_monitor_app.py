# Утилита, которая следит за стабильностью интернет-подключения:
# - Пингует указанный хост (по умолчанию 8.8.8.8) с интервалом
# - Определяет, отвечает ли хост (если нет — “outage”)
# - Если ответ — парсит задержку (ms)
# - Записывает лог в формате CSV: временная метка, статус, задержка
# - Выводит в консоль текущее состояние


import subprocess
import time
import csv
from datetime import datetime

HOST = "8.8.8.8"
INTERVAL = 60  # секунда
LOG_FILE = "connectivity_log.csv"

def ping(host):
    # ping для Linux/macOS; под Windows может быть другой ключ
    result = subprocess.run(["ping", "-c", "1", host], capture_output=True)
    return result.returncode == 0, result

def log_status(timestamp, status, latency):
    with open(LOG_FILE, "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([timestamp, status, latency])

def extract_latency(output):
    # пробуем парсить строку ping-ответа
    out = output.decode('utf-8', errors='ignore')
    # строка вида: time=12.345 ms
    for part in out.split():
        if part.startswith("time="):
            try:
                return float(part.split("=")[1])
            except:
                pass
    return None

def main():
    # заголовок CSV, если файл новый
    try:
        with open(LOG_FILE, "x") as f:
            writer = csv.writer(f)
            writer.writerow(["timestamp", "status", "latency_ms"])
    except FileExistsError:
        pass

    while True:
        ts = datetime.now().isoformat()
        ok, res = ping(HOST)
        latency = None
        if ok:
            latency = extract_latency(res.stdout)
            status = "online"
        else:
            status = "outage"
        log_status(ts, status, latency)
        print(f"{ts} — {status} — {latency}")
        time.sleep(INTERVAL)

if name == "__main__":
    main()

