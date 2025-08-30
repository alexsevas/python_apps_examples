# conda activate allpy311

# Автоматическая проверка активных сессий SSH на сервере
# Без зависимостей. Работает на Linux и macOS. Использует стандартную команду who.

# Проверяет, кто сейчас подключён к серверу по SSH. Удобно для безопасности, DevOps-логов, cron-уведомлений или
# триггеров (например, не перезапускать сервис, пока есть админы).

import subprocess
import time

def get_active_ssh_users():
    result = subprocess.run(['who'], capture_output=True, text=True)
    users = set()
    for line in result.stdout.strip().split('\n'):
        if 'pts/' in line:
            parts = line.split()
            if parts:
                users.add(parts[0])
    return users

if __name__ == '__main__':
    users = get_active_ssh_users()
    if users:
        print(f"🧑‍💻 Активные SSH-сессии: {', '.join(users)}")
    else:
        print("🟢 Нет активных SSH-сессий")
