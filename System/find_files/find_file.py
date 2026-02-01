# Поиск файла с помощью рекурсивного обхода
# Эта функция позволяет рекурсивно искать файл в указанной директории и её поддиректориях. Она использует os.walk для
# обхода файловой системы и возвращает полный путь к файлу, если он найден. Полезно для автоматизации задач, связанных с
# управлением файлами, и для скриптов, требующих динамического поиска файлов в системе.


import os

def find_file(filename: str, search_path: str) -> str:
    try:
        for root, dirs, files in os.walk(search_path):
            if filename in files:
                return os.path.join(root, filename)
        raise FileNotFoundError(f"'{filename}' не найден в '{search_path}'")
    except Exception as e:
        return str(e)

# Пример использования
file_path = find_file('example.txt', '/path/to/search')
print(file_path)