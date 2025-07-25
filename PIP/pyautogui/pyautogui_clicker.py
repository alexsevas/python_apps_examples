# conda activate allpy311
# pip install pyautogui

# Код простого кликера

import pyautogui
import time


def clicker(x, y, clicks, interval):
    # Перемещаем указатель мыши в указанную позицию
    pyautogui.moveTo(x, y)
    for _ in range(clicks):
        # Выполняем клик мышью
        pyautogui.click()
        # Ждем указанный интервал времени между кликами
        time.sleep(interval)


# Кликаем 2 разf в позиции (800, 200) с интервалом 0.1 секунды
clicker(500, 500, 2, 0.1)
