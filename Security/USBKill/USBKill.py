# Cкрипт-защита от несанкционированных USB-устройств:
# - Мониторит список USB-устройств
# - Сравнивает с белым списком
# - При обнаружении “чужого” устройства — выполняет “жёсткое” действие (shutdown, удаление, очистка)
# - Полезен как антифизическая защита при чувствительных данных


import time
import subprocess

WHITELIST = ["Device1_ID", "Device2_ID"]
CHECK_INTERVAL = 1  # секунда

def list_usb_devices():
    # команда lsusb — показывает USB-устройства на Linux
    output = subprocess.check_output(["lsusb"]).decode()
    return output.splitlines()

def monitor():
    while True:
        devices = list_usb_devices()
        for d in devices:
            # простая проверка: если строка не содержит ни одного whitelist ID
            if all(w not in d for w in WHITELIST):
                # небелое устройство — активируем защиту
                print("Unknown USB device detected:", d)
                # Пример действия: выключить систему
                subprocess.call(["shutdown", "now", "-h"])
                return
        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    monitor()
