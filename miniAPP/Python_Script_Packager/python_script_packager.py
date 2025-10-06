
'''
Утилита, которая упаковывает несколько .py файлов в один минимизированный скрипт
 Python 3.8+
 Модули: os, shutil (стандартные), python_minifier (для удаления пробелов/комментариев и “минификации”),
 GitPython (для работы с git, если скрипты из репозитория).

Скрипт packer.py из gist пользователя JMcrafter26 автоматически берёт заданный перечень файлов Python (основной +
вспомогательные), минифицирует их, объединяет в один файл — удобно для дистрибуции, когда хочется отправить один
“собранный” скрипт вместо множества модулей.
Т.е. скрипт:
- Берёт список Python файлов, объединяет их содержимое в один файл.
- Минифицирует код: убирает комментарии, пробелы, возможно переименование переменных.
- Позволяет собрать все модули проекта в один “соло-скрипт”, удобно для простого деплоя или когда структура проекта не критична.
- Уменьшает количество файлов, упрощает распространение скрипта без множества зависимостей файловой структуры.
'''


import os
import shutil
from python_minifier import minify
from git import Repo  # GitPython

# Настройки
remove_comments = True
minify_rename_vars = False
program_allowed = [
    'main_server.py',
    'packets.py',
    'protocol.py',
    'regex_patterns.py',
    'socket_handler.py',
]

def load_files(files):
    contents = []
    for file in files:
        with open(file, 'r', encoding='utf-8') as f:
            text = f.read()
        if remove_comments:
            # python_minifier(minify) сам удаляет комментарии
            text = minify(text, rename_locals=minify_rename_vars)
        contents.append(f"# Begin {file}\n" + text + f"\n# End {file}\n")
    return "\n".join(contents)

def package_script(output_file='packaged.py'):
    code = load_files(program_allowed)
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(code)
    print(f"Packaged into {output_file}")

if name == "__main__":
    package_script()
