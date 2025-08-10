# conda activate allpy311

# Трекер активности за ПК с логом, визуализацией и отчетами

import win32gui
import time
from collections import defaultdict
import matplotlib.pyplot as plt

usage = defaultdict(int)
start = time.time()

print("🎯 Начался трекинг активности. Для остановки — Ctrl+C")
try:
    while True:
        hwnd = win32gui.GetForegroundWindow()
        title = win32gui.GetWindowText(hwnd)
        if title:
            usage[title] += 1
        time.sleep(1)
except KeyboardInterrupt:
    print("\n📝 Сбор завершён")

# Отображение отчёта
sorted_usage = sorted(usage.items(), key=lambda x: -x[1])[:10]
labels = [k[:30] + "..." if len(k) > 30 else k for k, _ in sorted_usage]
values = [v for _, v in sorted_usage]

plt.figure(figsize=(10, 6))
plt.barh(labels[::-1], values[::-1])
plt.title("⏱️ Топ-используемые окна")
plt.xlabel("Секунды активности")
plt.tight_layout()
plt.savefig("activity_report.png")
print("📊 Отчёт сохранён: activity_report.png")
