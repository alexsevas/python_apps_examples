# Скрипт, который автоматически создаёт резервные копии указанной папки с отметкой даты и времени, может запускаться по
# расписанию (через cron или schedule)
# Пример использования (CLI):
# python backup_scheduler.py --src /home/user/docs --dst /home/user/backups --schedule 24


import os
import shutil
import argparse
from datetime import datetime
import time

def backup(src, dst):
    timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    backup_path = os.path.join(dst, timestamp)
    os.makedirs(backup_path, exist_ok=True)
    for root, dirs, files in os.walk(src):
        rel = os.path.relpath(root, src)
        dest_dir = os.path.join(backup_path, rel)
        os.makedirs(dest_dir, exist_ok=True)
        for file in files:
            shutil.copy2(os.path.join(root, file), os.path.join(dest_dir, file))
    print(f"✅ Backup created at: {backup_path}")

def main():
    parser = argparse.ArgumentParser("Directory Backup Scheduler")
    parser.add_argument("--src", required=True, help="Source directory to backup")
    parser.add_argument("--dst", required=True, help="Destination directory for backups")
    parser.add_argument("--schedule", type=int, help="Interval in hours between backups")
    args = parser.parse_args()

    if args.schedule:
        while True:
            backup(args.src, args.dst)
            time.sleep(args.schedule * 3600)
    else:
        backup(args.src, args.dst)

if __name__ == "__main__":
    main()
