


import socket
import argparse

def scan_ports(host, ports):
    print(f"Сканирование {host}...")
    for port in ports:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(0.5)
            result = sock.connect_ex((host, port))
            if result == 0:
                print(f"[+] Порт {port} открыт")
            sock.close()
        except Exception as e:
            print(f"Ошибка при проверке порта {port}: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Простой сканер портов")
    parser.add_argument("host", help="IP или домен для проверки")
    parser.add_argument("--ports", nargs="+", type=int, default=[21,22,80,443,3306],
                        help="Список портов через пробел (по умолчанию: 21 22 80 443 3306)")
    args = parser.parse_args()

    scan_ports(args.host, args.ports)
