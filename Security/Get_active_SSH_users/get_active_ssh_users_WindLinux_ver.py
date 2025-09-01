# conda activate allpy311

# Универсальная версия, которая работает как на Windows, так и на Linux/macOS, и определяет активных пользователей через SSH.


import subprocess
import platform
import re

def get_active_ssh_users():
    users = set()
    system = platform.system()

    if system == "Linux" or system == "Darwin":  # Linux или macOS
        try:
            result = subprocess.run(['who'], capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                for line in result.stdout.strip().split('\n'):
                    if 'pts/' in line or 'tty' in line:  # pts — SSH, tty — локальные сессии
                        parts = line.split()
                        if parts:
                            users.add(parts[0])
        except Exception as e:
            print(f"⚠️ Ошибка при выполнении 'who': {e}")

    elif system == "Windows":
        try:
            # Используем PowerShell для получения активных сессий (включая RDP, но SSH тоже отображается)
            # Для OpenSSH Server в Windows: посмотрим активные SSH-сессии через `Get-NetTCPConnection` и `Query User`
            result = subprocess.run(
                ['query', 'user'],
                capture_output=True,
                text=True,
                shell=True  # обязательно для встроенных команд Windows
            )
            if result.returncode == 0:
                for line in result.stdout.strip().split('\n')[1:]:  # Пропускаем заголовок
                    if line.strip():
                        # Пример строки: "username  SESSIONNAME    ID  STATE   IDLE TIME  LOGON TIME"
                        parts = re.split(r'\s+', line.strip())
                        if parts:
                            username = parts[0].strip()
                            if not username.startswith('>') and username != 'console':
                                users.add(username)
        except Exception as e:
            print(f"⚠️ Ошибка при выполнении 'query user': {e}")

    else:
        print(f"⚠️ Неподдерживаемая ОС: {system}")

    return users

if __name__ == '__main__':
    users = get_active_ssh_users()
    if users:
        print(f"🧑‍💻 Активные SSH-сессии: {', '.join(users)}")
    else:
        print("🟢 Нет активных SSH-сессий")