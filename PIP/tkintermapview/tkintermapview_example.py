# conda activate allpy311

# Библиотека tkintermapview предоставляет виджет для отображения карт в приложениях, разработанных с использованием tkinter.
# Позволяет интегрировать карты на основе OpenStreetMap.

import tkinter as tk
from tkintermapview import TkinterMapView

# Создание главного окна
root = tk.Tk()
root.title("Пример TkinterMapView")

# Создание виджета карты
map_view = TkinterMapView(root, width=800, height=600, corner_radius=0)
map_view.pack(fill="both", expand=True)

# Установка начального местоположения и уровня масштабирования
map_view.set_position(55.030204, 82.920430)  # Новосибирск
map_view.set_zoom(10)

# Добавление маркера
map_view.set_marker(55.030204, 82.920430, "Новосибирск")

# Запуск главного цикла приложения
root.mainloop()
