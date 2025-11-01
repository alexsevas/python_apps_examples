# conda activate allpy311

# Работа с переменными окружения в Python с помощью python-dotenv
# python-dotenv загружает значения из файла .env в переменные окружения — удобно для конфигов без хардкода.
# Пример: создать .env → загрузить → привести типы → обновить ключ

# pip install python-dotenv


import os
from pathlib import Path
from dotenv import load_dotenv, set_key

env_path = Path(".env")

# Создадим .env с дефолтами, если его нет
if not env_path.exists():
    env_path.write_text(
        "APP_NAME=Ghostly\n"
        "DEBUG=true\n"
        "DB_HOST=localhost\n"
        "DB_PORT=5432\n"
        "SECRET_KEY=s3cr3t_key_123\n",
        encoding="utf-8"
    )

# Загрузка переменных из .env в окружение процесса (override=False не перезапишет уже заданные в ОС)
load_dotenv(dotenv_path=env_path, override=False)

# Чтение с приведением типов
APP_NAME = os.getenv("APP_NAME", "App")
DEBUG    = os.getenv("DEBUG", "false").lower() in {"1", "true", "yes", "on"}
DB_HOST  = os.getenv("DB_HOST", "localhost")
DB_PORT  = int(os.getenv("DB_PORT", "5432"))
SECRET   = os.getenv("SECRET_KEY")  # None, если не задан

print(APP_NAME, DEBUG, DB_HOST, DB_PORT, SECRET is not None)

# Обновление/добавление ключей в .env
set_key(str(env_path), "DEBUG", "false")
set_key(str(env_path), "API_URL", "https://api.github.com")

# Показать обновлённый .env
print(env_path.read_text(encoding="utf-8"))
