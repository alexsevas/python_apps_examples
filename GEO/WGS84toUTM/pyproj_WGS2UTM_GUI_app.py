# conda activate allpy311

# pip install pyproj pyperclip customtkinter

# WGS84 ↔ UTM конвертер с GUI (customtkinter)

import customtkinter as ctk
from customtkinter import CTkLabel, CTkButton, CTkTextbox, CTkFrame, CTkRadioButton, CTkScrollableFrame
import re
from pyproj import Transformer, CRS
import pyperclip

class CoordinateConverterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Конвертер координат WGS84 ↔ UTM")
        self.root.geometry("650x600")
        self.root.resizable(False, False)

        # Тема
        ctk.set_appearance_mode("dark")  # "light" или "dark"
        ctk.set_default_color_theme("blue")

        # Переменная для выбора режима
        self.mode_var = ctk.StringVar(value="wgs_to_utm")

        # Заголовок
        title_label = CTkLabel(root, text="Конвертер координат\nWGS84 ↔ UTM",
                               font=("Arial", 16, "bold"))
        title_label.pack(pady=15)

        # Режим выбора
        mode_frame = CTkFrame(root)
        mode_frame.pack(pady=5)

        self.wgs_to_utm_rb = CTkRadioButton(mode_frame, text="WGS84 → UTM", variable=self.mode_var,
                                            value="wgs_to_utm", command=self.update_labels)
        self.utm_to_wgs_rb = CTkRadioButton(mode_frame, text="UTM → WGS84", variable=self.mode_var,
                                            value="utm_to_wgs", command=self.update_labels)
        self.wgs_to_utm_rb.grid(row=0, column=0, padx=10)
        self.utm_to_wgs_rb.grid(row=0, column=1, padx=10)

        # Инструкции
        self.instructions = CTkLabel(root, text="", font=("Arial", 9), text_color="gray")
        self.instructions.pack(pady=5)

        # Поле ввода
        input_frame = CTkFrame(root)
        input_frame.pack(pady=10, padx=20, fill="x")

        self.input_label = CTkLabel(input_frame, text="", font=("Arial", 10))  # Пока пусто
        self.input_label.grid(row=0, column=0, sticky="w", pady=5, padx=(10, 0))

        self.input_text = CTkTextbox(input_frame, height=120, width=500, font=("Courier", 10))
        self.input_text.grid(row=1, column=0, columnspan=2, padx=10, pady=5, sticky="ew")

        # Кнопки
        btn_frame = CTkFrame(root)
        btn_frame.pack(pady=10)

        self.convert_btn = CTkButton(btn_frame, text="Конвертировать", font=("Arial", 10),
                                     fg_color="#1E88E5", hover_color="#1976D2", command=self.convert)
        self.convert_btn.grid(row=0, column=0, padx=10)

        self.copy_btn = CTkButton(btn_frame, text="Копировать результат", font=("Arial", 10),
                                  fg_color="gray", hover_color="#666666", command=self.copy_to_clipboard)
        self.copy_btn.grid(row=0, column=1, padx=10)

        self.clear_btn = CTkButton(btn_frame, text="Очистить", font=("Arial", 10),
                                   fg_color="red", hover_color="#C62828", command=self.clear_all)
        self.clear_btn.grid(row=0, column=2, padx=10)

        # Результат
        result_frame = CTkFrame(root)
        result_frame.pack(pady=10, padx=20, fill="x", expand=True)

        CTkLabel(result_frame, text="Результат", font=("Arial", 12, "bold")).pack(anchor="w", padx=10)

        self.result_text = CTkTextbox(result_frame, height=180, width=500, font=("Courier", 10))
        self.result_text.pack(padx=10, pady=5, fill="both", expand=True)

        # === ВАЖНО: вызываем update_labels ПОСЛЕ создания всех виджетов ===
        self.update_labels()

    def update_labels(self):
        mode = self.mode_var.get()
        if mode == "wgs_to_utm":
            self.input_label.configure(text="Широта, Долгота (список):")
            self.instructions.configure(
                text="Примеры:\n55.75,37.62\n-33.86,151.20\nили построчно"
            )
        else:
            self.input_label.configure(text="Easting, Northing;Zone (список):")
            self.instructions.configure(
                text="Примеры:\n360470,6181416;37N\n630000,4833438;10S\nили построчно"
            )

    def convert(self):
        self.result_text.delete("1.0", "end")
        user_input = self.input_text.get("1.0", "end").strip()
        if not user_input:
            ctk.CTkMessageBox(title="Пустой ввод", message="Введите данные для конвертации.")
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

        self.result_text.insert("1.0", "\n".join(results))

    def copy_to_clipboard(self):
        result = self.result_text.get("1.0", "end").strip()
        if result:
            pyperclip.copy(result)
            ctk.CTkMessageBox(title="Скопировано", message="Результат скопирован в буфер обмена!")
        else:
            ctk.CTkMessageBox(title="Нет данных", message="Нечего копировать.")

    def clear_all(self):
        self.input_text.delete("1.0", "end")
        self.result_text.delete("1.0", "end")


if __name__ == "__main__":
    try:
        import pyproj
        import pyperclip
    except ImportError as e:
        print("Ошибка: Установите зависимости:")
        print("pip install pyproj pyperclip customtkinter")
        exit(1)

    ctk.set_appearance_mode("dark")  # Можно: "light", "dark"
    ctk.set_default_color_theme("blue")

    root = ctk.CTk()
    app = CoordinateConverterApp(root)
    root.mainloop()