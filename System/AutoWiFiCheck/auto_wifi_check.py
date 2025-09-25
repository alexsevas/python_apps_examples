'''
Cкрипт, который следит за состоянием подключения к WiFi или интернету и автоматически переподключается или выполняет
уведомление, если связь пропала. Полезен для ноутбуков, Raspberry Pi, серверов в нестабильной сети.

Python 3.7+
Модули: subprocess, time, platform, возможно os — внешний вызов системных команд (ping, nmcli, netsh и т.д.).
'''

import subprocess
import time
import platform

def is_connected(host="8.8.8.8", count=1, timeout=1):
    param = "-n" if platform.system().lower() == "windows" else "-c"
    cmd = ["ping", param, str(count), "-W", str(timeout), host]
    result = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return result.returncode == 0

def reconnect_wifi(interface_name=None):
    system = platform.system().lower()
    try:
        if system == "linux":
            # пример для NetworkManager
            subprocess.run(["nmcli", "networking", "off"], check=True)
            time.sleep(1)
            subprocess.run(["nmcli", "networking", "on"], check=True)
        elif system == "windows":
            # отключить / включить адаптер
            subprocess.run(["netsh", "interface", "set", "interface", interface_name, "disable"], check=True)
            time.sleep(1)
            subprocess.run(["netsh", "interface", "set", "interface", interface_name, "enable"], check=True)
        else:
            print("OS не поддерживается для авто-переподключения")
    except Exception as e:
        print("Ошибка при переподключении:", e)

def watch_loop(interval=10, interface=None):
    while True:
        if is_connected():
            print("Связь OK")
        else:
            print("Связь пропала — переподключаем...")
            reconnect_wifi(interface)
        time.sleep(interval)

if __name__ == "__main__":
    # Можно передать название интерфейса через аргументы
    watch_loop(interval=15, interface="Wi-Fi")
