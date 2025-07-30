# conda activate allpy311

'''
Анализ и визуализация использования папки.

Где применимо:
- Определить, что занимает диск
- Очистка ненужного (например, временные папки)
- Анализ по категориям (если доработать)
- Быстрый обзор на уровне пользователя или сервера
'''

import os
import matplotlib.pyplot as plt

def get_folder_size(path):
    total = 0
    for dirpath, dirnames, filenames in os.walk(path):
        for f in filenames:
            try:
                fp = os.path.join(dirpath, f)
                total += os.path.getsize(fp)
            except:
                pass
    return total

def scan_directory(path, depth=1):
    items = []
    for item in os.listdir(path):
        full_path = os.path.join(path, item)
        if os.path.isdir(full_path):
            size = get_folder_size(full_path)
        else:
            size = os.path.getsize(full_path)
        items.append((item, size))
    items.sort(key=lambda x: -x[1])
    return items

def visualize_pie(path):
    print(f"🔍 Анализ папки: {path}")
    items = scan_directory(path)
    labels = [name if size > 10**6 else '' for name, size in items[:10]]
    sizes = [size for _, size in items[:10]]

    plt.figure(figsize=(8, 8))
    plt.pie(sizes, labels=labels, autopct=lambda p: f'{p:.1f}%' if p > 3 else '', startangle=140)
    plt.title("📁 Использование пространства (топ 10)")
    plt.axis('equal')
    plt.tight_layout()
    plt.savefig("folder_usage.png")
    print("📊 График сохранён: folder_usage.png")

# Пример использования
visualize_pie("D:/VIDEO_05_2025")  # или "." — текущая папка
