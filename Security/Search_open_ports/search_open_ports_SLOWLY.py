# conda activate allpy311

# Поиск всех открытых портов для веб сайта

from socket import *
import time
startTime = time.time()

if __name__ == '__main__':
    target = input('Enter the host to be scanned: ')
    t_IP = gethostbyname(target)
    print ('Starting scan on host: ', t_IP)

    for i in range(50, 500):
        s = socket(AF_INET, SOCK_STREAM)

        conn = s.connect_ex((t_IP, i))
        if(conn == 0) :
            print ('Port %d: OPEN' % (i,))
        s.close()
print('Time taken:', time.time() - startTime)



'''
Не лучшая реализация - медленная.
Cкрипт выполняет последовательное сканирование портов (от 50 до 499) с помощью блокирующих сокетов, и именно это делает 
его медленным. По умолчанию socket.connect() (и, соответственно, connect_ex()) — блокирующая операция, и если порт 
закрыт или хост не отвечает, система может ждать несколько секунд на каждое соединение:
- Блокирующий режим сокета: по умолчанию сокет ждёт ответа до таймаута (часто 1–3 секунды на порт).
- Последовательное сканирование: порты проверяются один за другим, без параллелизма.
- Отсутствие таймаута: вы не установили s.settimeout(), поэтому ОС использует системный таймаут, который может быть большим.
'''