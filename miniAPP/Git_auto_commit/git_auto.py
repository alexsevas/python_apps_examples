'''
Скрипт автоматизирует рутинные git-операции: добавление файлов, коммит с шаблоном сообщения и пуш в ветку — всё одной командой.
Python 3.7+
Модули: subprocess, argparse, datetime

Что делает:
- Выполняет добавление всех изменений (git add .)
- Составляет коммит-сообщение с временной меткой (например: Auto commit 2025-08-19 · Обновления)
- Делает git commit и git push, используя default-ветку
- Позволяет один раз запускать скрипт и забыть про многострочные команды—автоматизация на максималках

Пример использования (CLI):
python git_auto.py
'''

import subprocess
import argparse
from datetime import datetime

def auto_git():
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    msg = f"Auto commit {timestamp}"
    try:
        subprocess.run(["git", "add", "."], check=True)
        subprocess.run(["git", "commit", "-m", msg], check=True)
        subprocess.run(["git", "push"], check=True)
        print(f"✅ Changes pushed with message: '{msg}'")
    except subprocess.CalledProcessError as e:
        print(f"❌ Git operation failed: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser("Automate Git Operations")
    args = parser.parse_args()
    auto_git()
