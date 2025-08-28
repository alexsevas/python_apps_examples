# Автоочистка старых файлов в папке

'''
Удаляет файлы старше указанного числа дней в папке. Полезно для логов, временных файлов и кэшей.
Стандартная библиотека, без зависимостей
'''

import os, time

def clean_old_files(path, days=7):
    now = time.time()
    cutoff = now - days * 86400
    for f in os.listdir(path):
        full = os.path.join(path, f)
        if os.path.isfile(full) and os.path.getmtime(full) < cutoff:
            os.remove(full)
            print(f"🗑 Удален: {full}")

if __name__ == "__main__":
    clean_old_files("D:\\tmp", days=3)
