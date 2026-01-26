# Автоматизация с помощью Python: пакетное переименование файлов
# Данный код автоматизирует процесс пакетного переименования файлов в указанной директории, добавляя заданный префикс и уникальный
# номер к каждому файлу. Он обрабатывает ошибки, такие как отсутствие директории или проблемы с доступом, и выводит диагностические
# сообщения. Такой скрипт может быть полезен для организации файлов, подготовки данных для анализа или управления большими объемами
# медиафайлов.


import os

def rename_files_in_directory(directory: str, prefix: str):
    try:
        files = os.listdir(directory)
        for count, filename in enumerate(files):
            old_path = os.path.join(directory, filename)
            new_filename = f"{prefix}_{count}{os.path.splitext(filename)[1]}"
            new_path = os.path.join(directory, new_filename)
            os.rename(old_path, new_path)
        print(f"Успешно переименовано {len(files)} файлов.")
    except FileNotFoundError:
        print("Указанная директория не найдена.")
    except PermissionError:
        print("Отказано в доступе. Проверьте права доступа к директории.")
    except Exception as e:
        print(f"Произошла ошибка: {e}")

# Пример использования
# rename_files_in_directory("/path/to/your/folder", "new_prefix")
