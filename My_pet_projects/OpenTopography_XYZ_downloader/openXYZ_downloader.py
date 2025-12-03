
# Программа позволяет рисовать прямоугольник на карте Leaflet (через библиотеку folium), скачивать DEM-данные через
# OpenTopography API и конвертировать их в XYZ-файл с помощью rasterio.

# v0.0.2
# 1.Линейка масштаба (Scale Bar): Теперь на карте в левом нижнем углу есть черно-белая полоска, показывающая масштаб в километрах и милях. Она меняется при зуме.
# 2.Mouse Position: В правом верхнем углу карты бегущие цифры показывают точные координаты (широту и долготу), куда указывает курсор мыши. Это очень удобно для точного прицеливания.
# 3.Выпадающий список (ComboBox):
# SRTMGL3: Стоит по умолчанию (90 метров).
# SRTMGL1: (30 метров) — если выберете его без вставленного ключа API, программа выдаст понятную ошибку (в методе run добавлена проверка status_code == 401).
# NASADEM: Добавлена как альтернатива (тоже ~30 метров, переработанные данные SRTM).
# 4. Расчет размеров: При выборе области программа теперь пишет примерный размер участка в километрах (например, "Область: 5.2 x 3.1 км").

import sys
import io
import json
import requests
import numpy as np
import rasterio
from rasterio.transform import rowcol
from pyproj import CRS, Transformer

from PyQt5.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QWidget,
                             QPushButton, QLabel, QProgressBar, QMessageBox,
                             QFileDialog, QComboBox, QFormLayout)
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtCore import QThread, pyqtSignal

import folium
from folium.plugins import Draw, MousePosition

# ================= НАСТРОЙКИ =================
# Вставьте ваш ключ OpenTopography ниже
API_KEY = "ВАШ_КЛЮЧ_ЗДЕСЬ"

OPENTOPOGRAPHY_API_URL = "https://portal.opentopography.org/API/globaldem"


# ================= ЛОГИКА =================

class DownloadWorker(QThread):
    progress = pyqtSignal(str)
    finished = pyqtSignal(str)

    def __init__(self, bounds, output_file, dem_type):
        super().__init__()
        self.bounds = bounds
        self.output_file = output_file
        self.dem_type = dem_type  # Тип данных теперь приходит из UI

    def get_utm_epsg(self, lat, lon):
        """Определяет EPSG код зоны UTM"""
        zone = int((lon + 180) / 6) + 1
        if lat >= 0:
            return f"epsg:326{zone}"
        else:
            return f"epsg:327{zone}"

    def run(self):
        min_lat, min_lon, max_lat, max_lon = self.bounds

        # Параметры запроса с динамическим типом рельефа
        params = {
            'demtype': self.dem_type,
            'south': min_lat,
            'north': max_lat,
            'west': min_lon,
            'east': max_lon,
            'outputFormat': 'GTiff',
            'API_Key': API_KEY
        }

        self.progress.emit(f"Запрос данных ({self.dem_type})...")

        try:
            response = requests.get(OPENTOPOGRAPHY_API_URL, params=params, stream=True)

            # Обработка ошибок авторизации
            if response.status_code == 401:
                self.finished.emit("Ошибка 401: Неверный или отсутствующий API Key. Для SRTMGL1 (30м) ключ обязателен.")
                return
            if response.status_code != 200:
                self.finished.emit(f"Ошибка API: {response.text}")
                return

            temp_tiff = "temp_elevation.tif"
            with open(temp_tiff, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)

            self.progress.emit("Проекция WGS84 -> UTM...")

            with rasterio.open(temp_tiff) as src:
                elevation_data = src.read(1)
                height, width = elevation_data.shape
                transform = src.transform
                nodata = src.nodata

                cols, rows = np.meshgrid(np.arange(width), np.arange(height))
                xs_wgs, ys_wgs = rasterio.transform.xy(transform, rows, cols)
                xs_wgs = np.array(xs_wgs)
                ys_wgs = np.array(ys_wgs)

                # Определяем зону UTM по центру участка
                center_lat = (min_lat + max_lat) / 2
                center_lon = (min_lon + max_lon) / 2
                target_crs = self.get_utm_epsg(center_lat, center_lon)

                self.progress.emit(f"Трансформация в {target_crs}...")

                transformer = Transformer.from_crs("epsg:4326", target_crs, always_xy=True)
                xx_utm, yy_utm = transformer.transform(xs_wgs, ys_wgs)

                x_flat = xx_utm.flatten()
                y_flat = yy_utm.flatten()
                z_flat = elevation_data.flatten()

                self.progress.emit("Сохранение CSV (X, Y, Z)...")

                with open(self.output_file, 'w') as f:
                    buffer = []
                    count = 0
                    for x, y, z in zip(x_flat, y_flat, z_flat):
                        if z != nodata and z > -10000:
                            line = f"{x:.3f},{y:.3f},{z:.3f}\n"
                            buffer.append(line)
                            count += 1
                            if count >= 20000:
                                f.writelines(buffer)
                                buffer = []
                                count = 0
                    if buffer:
                        f.writelines(buffer)

            self.finished.emit(f"Успех! Зона: {target_crs}")

        except Exception as e:
            self.finished.emit(f"Критическая ошибка: {str(e)}")


# ================= ИНТЕРФЕЙС =================

class MapApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Geo XYZ Downloader Pro")
        self.resize(1100, 750)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # 1. Карта
        self.web_view = QWebEngineView()
        main_layout.addWidget(self.web_view, stretch=1)

        # 2. Панель управления
        controls_group = QWidget()
        controls_layout = QVBoxLayout(controls_group)
        controls_group.setStyleSheet("background-color: #f0f0f0; border-radius: 5px; padding: 5px;")

        # Инструкция
        self.info_label = QLabel(
            "1. Выберите прямоугольник на карте (инструмент ■ слева).\n2. Выберите детализацию и скачайте файл.")
        controls_layout.addWidget(self.info_label)

        # Выпадающий список детализации
        form_layout = QFormLayout()
        self.res_combo = QComboBox()
        # Добавляем пары: (Текст для пользователя, Значение для API)
        self.res_combo.addItem("SRTMGL3 (Разрешение ~90м) - Бесплатно, быстро", "SRTMGL3")
        self.res_combo.addItem("SRTMGL1 (Разрешение ~30м) - Требуется API Ключ", "SRTMGL1")
        self.res_combo.addItem("NASADEM (Разрешение ~30м) - Улучшенный SRTM", "NASADEM")

        form_layout.addRow(QLabel("<b>Детализация рельефа:</b>"), self.res_combo)
        controls_layout.addLayout(form_layout)

        # Метка координат
        self.coords_label = QLabel("Область не выбрана")
        self.coords_label.setStyleSheet("color: #555;")
        controls_layout.addWidget(self.coords_label)

        # Кнопка и прогресс
        self.btn_download = QPushButton("Скачать рельеф (XYZ UTM)")
        self.btn_download.setStyleSheet("background-color: #0078d7; color: white; font-weight: bold; padding: 8px;")
        self.btn_download.setEnabled(False)
        self.btn_download.clicked.connect(self.start_download)
        controls_layout.addWidget(self.btn_download)

        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        controls_layout.addWidget(self.progress_bar)

        main_layout.addWidget(controls_group)

        self.selected_bounds = None
        self.init_map()

    def init_map(self):
        # control_scale=True добавляет линейку масштаба в левый нижний угол
        m = folium.Map(location=[55.75, 37.61], zoom_start=6, control_scale=True)

        # Добавляем отображение координат курсора (полезно для геодезии)
        MousePosition().add_to(m)

        draw = Draw(
            export=False,
            position='topleft',
            draw_options={'polyline': False, 'polygon': False, 'circle': False, 'marker': False, 'circlemarker': False,
                          'rectangle': True},
            edit_options={'edit': False}
        )
        draw.add_to(m)

        data = io.BytesIO()
        m.save(data, close_file=False)
        html_content = data.getvalue().decode()

        # JS скрипт (без изменений)
        script_to_find_map = """
        <script>
            function setupDrawListener() {
                for (var key in window) {
                    if (key.startsWith('map_')) {
                        var map = window[key];
                        if (map && map.on) {
                            map.on('draw:created', function(e) {
                                var bounds = e.layer.getBounds();
                                var coords = {
                                    north: bounds.getNorth(), south: bounds.getSouth(),
                                    east: bounds.getEast(), west: bounds.getWest()
                                };
                                document.title = "BOUNDS|" + JSON.stringify(coords);
                            });
                            map.on('draw:drawstart', function(e) {
                                map.eachLayer(function(layer) {
                                    if (layer instanceof L.Rectangle && !layer._url) map.removeLayer(layer);
                                });
                            });
                            return;
                        }
                    }
                }
                setTimeout(setupDrawListener, 500);
            }
            setupDrawListener();
        </script>
        """
        self.web_view.setHtml(html_content + script_to_find_map)
        self.web_view.titleChanged.connect(self.on_title_changed)

    def on_title_changed(self, title):
        if title.startswith("BOUNDS|"):
            try:
                data = json.loads(title.split("|")[1])
                self.selected_bounds = (data['south'], data['west'], data['north'], data['east'])

                # Расчет примерной площади для информации
                width_km = abs(data['east'] - data['west']) * 111 * np.cos(np.radians(data['north']))
                height_km = abs(data['north'] - data['south']) * 111

                self.coords_label.setText(f"Область: {width_km:.1f} x {height_km:.1f} км "
                                          f"(Lat: {data['south']:.3f}, Lon: {data['west']:.3f})")
                self.btn_download.setEnabled(True)
            except:
                pass

    def start_download(self):
        file_path, _ = QFileDialog.getSaveFileName(self, "Сохранить точки XYZ", "", "CSV Files (*.csv)")
        if not file_path: return

        # Получаем техническое имя (SRTMGL1) из скрытых данных ComboBox
        selected_dem = self.res_combo.currentData()

        self.btn_download.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)

        # Передаем selected_dem в воркер
        self.worker = DownloadWorker(self.selected_bounds, file_path, selected_dem)
        self.worker.progress.connect(lambda s: self.info_label.setText(s))
        self.worker.finished.connect(self.on_finished)
        self.worker.start()

    def on_finished(self, msg):
        self.progress_bar.setVisible(False)
        self.btn_download.setEnabled(True)
        if "Успех" in msg:
            QMessageBox.information(self, "Готово", f"Файл сохранен.\n{msg}")
        else:
            QMessageBox.critical(self, "Ошибка", msg)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MapApp()
    window.show()
    sys.exit(app.exec_())