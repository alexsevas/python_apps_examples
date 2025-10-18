# conda activate allpy311

# Поиск всех открытых портов для веб-сайта. Оптимизированный и ускоренный вариант скрипта.

from socket import *
import time
from concurrent.futures import ThreadPoolExecutor

def scan_port(ip, port):
    s = socket(AF_INET, SOCK_STREAM)
    s.settimeout(0.5)
    result = s.connect_ex((ip, port))
    s.close()
    if result == 0:
        return port
    return None

if __name__ == '__main__':
    target = input('Enter the host to be scanned: ')
    t_IP = gethostbyname(target)
    print('Starting scan on host:', t_IP)

    startTime = time.time()
    open_ports = []

    with ThreadPoolExecutor(max_workers=100) as executor:
        futures = {executor.submit(scan_port, t_IP, port): port for port in range(50, 500)}
        for future in futures:
            port = future.result()
            if port is not None:
                print(f'Port {port}: OPEN')
                open_ports.append(port)

    print('Time taken:', time.time() - startTime)


'''
Как ускорено:
 1. Установлен небольшой таймаут
s.settimeout(0.5)  # например, 0.5 секунды
Это резко сокращает время ожидания на каждый порт.
 2. Используется многопоточность (threading)
Проверяет несколько портов одновременно.

max_workers=100 — можно настроить под вашу систему и сеть. Слишком много потоков может вызвать ложные срабатывания или
быть заблокировано фаерволом.

Дополнительно:
Убедитесь, что вы имеете право сканировать хост (иначе это может быть незаконно или вызовет блокировку).
На Windows (учитывая вашу память о предпочтении консоли) многопоточность работает нормально, но избегайте слишком
агрессивного сканирования — это может вызвать срабатывание защиты.
'''