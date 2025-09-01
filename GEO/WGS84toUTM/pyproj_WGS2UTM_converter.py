# conda activate allpy310_2

# pip install pyproj pyperclip

# WGS84 ↔ UTM конвертер с GUI


import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from pyproj import Transformer, CRS
import re
import pyperclip  # Для копирования в буфер

class CoordinateConverterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Конвертер координат WGS84 ↔ UTM")
        self.root.geometry("650x600")
        self.root.resizable(False, False)

        # Переменная для выбора режима
        self.mode_var = tk.StringVar(value="wgs_to_utm")

        # Заголовок
        title_label = tk.Label(root, text="Конвертер координат\nWGS84 ↔ UTM",
                               font=("Arial", 14, "bold"), justify="center")
        title_label.pack(pady=10)

        # Режим выбора
        mode_frame = tk.Frame(root)
        mode_frame.pack(pady=5)
        tk.Radiobutton(mode_frame, text="WGS84 → UTM", variable=self.mode_var, value="wgs_to_utm", command=self.update_labels) \
            .grid(row=0, column=0, padx=10)
        tk.Radiobutton(mode_frame, text="UTM → WGS84", variable=self.mode_var, value="utm_to_wgs", command=self.update_labels) \
            .grid(row=0, column=1, padx=10)

        # Инструкции
        self.instructions = tk.Label(root, text="Формат: lat,lon или X,Y;Zone (например: 55.75,37.62 или 360470,6181416;37N)",
                                     font=("Arial", 8), fg="gray", wraplength=500)
        self.instructions.pack(pady=5)

        # Поле ввода
        input_frame = tk.Frame(root)
        input_frame.pack(pady=10, padx=20, fill="x")

        self.input_label = tk.Label(input_frame, text="Широта, Долгота:", font=("Arial", 10))
        self.input_label.grid(row=0, column=0, sticky="w", pady=5)
        self.input_text = scrolledtext.ScrolledText(input_frame, height=6, width=50, font=("Courier", 10))
        self.input_text.grid(row=1, column=0, columnspan=2, padx=10, pady=5)

        # Кнопки
        btn_frame = tk.Frame(root)
        btn_frame.pack(pady=10)

        self.convert_btn = tk.Button(btn_frame, text="Конвертировать", font=("Arial", 10), bg="#4CAF50", fg="white", command=self.convert)
        self.convert_btn.grid(row=0, column=0, padx=10)

        self.copy_btn = tk.Button(btn_frame, text="Копировать результат", font=("Arial", 10), command=self.copy_to_clipboard)
        self.copy_btn.grid(row=0, column=1, padx=10)

        self.clear_btn = tk.Button(btn_frame, text="Очистить", font=("Arial", 10), command=self.clear_all)
        self.clear_btn.grid(row=0, column=2, padx=10)

        # Результат
        result_frame = tk.LabelFrame(root, text="Результат", font=("Arial", 10, "bold"), padx=10, pady=10)
        result_frame.pack(pady=10, padx=20, fill="x", expand=True)

        self.result_text = scrolledtext.ScrolledText(result_frame, height=10, width=50, font=("Courier", 10), state="normal")
        self.result_text.pack(fill="both", expand=True)

        self.update_labels()  # Инициализация меток

    def update_labels(self):
        mode = self.mode_var.get()
        if mode == "wgs_to_utm":
            self.input_label.config(text="Широта, Долгота (список):")
            self.instructions.config(text="Примеры:\n55.75,37.62\n-33.86,151.20\nили построчно")
        else:
            self.input_label.config(text="Easting, Northing;Zone (список):")
            self.instructions.config(text="Примеры:\n360470,6181416;37N\n630000,4833438;10S\nили построчно")

    def convert(self):
        self.result_text.delete(1.0, tk.END)
        user_input = self.input_text.get("1.0", tk.END).strip()
        if not user_input:
            messagebox.showwarning("Пустой ввод", "Введите данные для конвертации.")
            return

        lines = [line.strip() for line in user_input.split('\n') if line.strip()]
        results = []

        mode = self.mode_var.get()

        for i, line in enumerate(lines):
            try:
                if mode == "wgs_to_utm":
                    lat_str, lon_str = re.split(r'[,;\s]+', line)
                    lat = float(lat_str.replace(',', '.'))
                    lon = float(lon_str.replace(',', '.'))
                    if not (-90 <= lat <= 90):
                        raise ValueError("Широта вне диапазона")
                    if not (-180 <= lon <= 180):
                        raise ValueError("Долгота вне диапазона")

                    zone_number = int((lon + 180) // 6) + 1
                    zone_letter = 'N' if lat >= 0 else 'S'

                    utm_crs = CRS.from_dict({
                        "proj": "utm", "zone": zone_number, "south": lat < 0, "ellps": "WGS84"
                    })
                    transformer = Transformer.from_crs("EPSG:4326", utm_crs, always_xy=True)
                    easting, northing = transformer.transform(lon, lat)

                    result_line = f"{i+1}: {easting:.2f}, {northing:.2f}; {zone_number}{zone_letter}"
                    results.append(result_line)

                elif mode == "utm_to_wgs":
                    # Поддержка формата: 360470,6181416;37N или 360470 6181416 37N
                    match = re.match(r'([^\d\-]+)?(\d+\.?\d*),?\s*(\d+\.?\d*)\s*;?\s*(\d+)([NnSs])', line)
                    if not match:
                        raise ValueError("Неверный формат UTM")

                    _, easting, northing, zone_num, zone_letter = match.groups()
                    easting = float(easting)
                    northing = float(northing)
                    zone_number = int(zone_num)
                    hemisphere = zone_letter.upper()

                    south = hemisphere == 'S'
                    utm_crs = CRS.from_dict({
                        "proj": "utm", "zone": zone_number, "south": south, "ellps": "WGS84"
                    })

                    transformer = Transformer.from_crs(utm_crs, "EPSG:4326", always_xy=True)
                    lon, lat = transformer.transform(easting, northing)

                    result_line = f"{i+1}: {lat:.6f}, {lon:.6f}"
                    results.append(result_line)

            except Exception as e:
                results.append(f"{i+1}: ОШИБКА — {str(e)}")

        # Показать результат
        self.result_text.insert(tk.END, "\n".join(results))

    def copy_to_clipboard(self):
        result = self.result_text.get("1.0", tk.END).strip()
        if result:
            pyperclip.copy(result)
            messagebox.showinfo("Скопировано", "Результат скопирован в буфер обмена!")
        else:
            messagebox.showwarning("Нет данных", "Нечего копировать.")

    def clear_all(self):
        self.input_text.delete("1.0", tk.END)
        self.result_text.delete("1.0", tk.END)


if __name__ == "__main__":
    # Проверка зависимостей
    try:
        import pyproj
        import pyperclip
    except ImportError as e:
        print("Ошибка: Установите зависимости:")
        print("pip install pyproj pyperclip")
        exit(1)

    root = tk.Tk()
    app = CoordinateConverterApp(root)
    root.mainloop()


'''
Функционал приложения:
- Ввод широты и долготы в формате WGS84.
- Автоматическое определение UTM-зоны и полушария (N/S).
- Преобразование с использованием точной проекции через pyproj.
- Отображение Easting, Northing, номер зоны и букву.
- Поддержка запятой или точки как десятичного разделителя.
- Обработка ошибок ввода.
- Копирование результата в буфер обмена.
- Поддержка нескольких точек (ввод через список).
- Обратное преобразование: UTM → WGS84 (lat/lon).
'''