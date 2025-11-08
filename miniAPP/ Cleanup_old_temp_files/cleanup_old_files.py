# conda activate allpy311
# Очистка временных файлов по расписанию

# Автоматически чистит устаревшие файлы и папки из временного каталога, чтобы кэш не разрастался.
# Полезно для бэкендов, аналитических скриптов и ML-сервисов.
# Никаких зависимостей — работает из коробки.


import os
import time
import shutil

TEMP_DIR = '/tmp/my_app_cache'
MAX_FILE_AGE = 60 * 60 * 24  # 1 день в секундах
CLEAN_INTERVAL = 60 * 10     # каждые 10 минут

def cleanup_old_files():
    now = time.time()
    for filename in os.listdir(TEMP_DIR):
        filepath = os.path.join(TEMP_DIR, filename)
        try:
            if os.path.isfile(filepath) and now - os.path.getmtime(filepath) > MAX_FILE_AGE:
                os.remove(filepath)
            elif os.path.isdir(filepath) and now - os.path.getmtime(filepath) > MAX_FILE_AGE:
                shutil.rmtree(filepath)
        except Exception as e:
            print(f"Ошибка при удалении {filepath}: {e}")

while True:
    cleanup_old_files()
    time.sleep(CLEAN_INTERVAL)
