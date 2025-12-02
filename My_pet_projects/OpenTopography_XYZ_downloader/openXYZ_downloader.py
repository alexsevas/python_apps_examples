
# Программа позволяет рисовать прямоугольник на карте Leaflet (через библиотеку folium), скачивать DEM-данные через
# OpenTopography API и конвертировать их в XYZ-файл с помощью rasterio.

import sys
import io
import json
import requests
import numpy as np
import rasterio
from rasterio.transform import rowcol
from pyproj import CRS, Transformer

from PyQt5.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QWidget,
                             QPushButton, QLabel, QProgressBar, QMessageBox, QFileDialog)
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtCore import QThread, pyqtSignal

import folium
from folium.plugins import Draw

# ================= НАСТРОЙКИ =================
# Вставьте ваш ключ ниже
API_KEY = "________________"

OPENTOPOGRAPHY_API_URL = "https://portal.opentopography.org/API/globaldem"
# SRTMGL1 - 30 метров (требует ключ), SRTMGL3 - 90 метров (работает и так)
DEM_TYPE = "SRTMGL3"


# ================= ЛОГИКА =================

class DownloadWorker(QThread):
    progress = pyqtSignal(str)
    finished = pyqtSignal(str)

    def __init__(self, bounds, output_file):
        super().__init__()
        self.bounds = bounds  # (min_lat, min_lon, max_lat, max_lon)
        self.output_file = output_file

    def get_utm_epsg(self, lat, lon):
        """Определяет EPSG код зоны UTM по координатам"""
        zone = int((lon + 180) / 6) + 1
        # Северное или Южное полушарие
        if lat >= 0:
            return f"epsg:326{zone}"  # 326xx - Север
        else:
            return f"epsg:327{zone}"  # 327xx - Юг

    def run(self):
        min_lat, min_lon, max_lat, max_lon = self.bounds

        # 1. Формируем URL
        params = {
            'demtype': DEM_TYPE,
            'south': min_lat,
            'north': max_lat,
            'west': min_lon,
            'east': max_lon,
            'outputFormat': 'GTiff',
            'API_Key': API_KEY
        }

        self.progress.emit("Скачивание рельефа...")

        try:
            response = requests.get(OPENTOPOGRAPHY_API_URL, params=params, stream=True)
            if response.status_code != 200:
                self.finished.emit(f"Ошибка API: {response.text}")
                return

            temp_tiff = "temp_elevation.tif"
            with open(temp_tiff, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)

            self.progress.emit("Обработка и проекция в UTM...")

            # 2. Обработка GeoTIFF
            with rasterio.open(temp_tiff) as src:
                elevation_data = src.read(1)
                height, width = elevation_data.shape
                transform = src.transform
                nodata = src.nodata

                # Создаем сетку координат пикселей
                cols, rows = np.meshgrid(np.arange(width), np.arange(height))

                # Переводим пиксели в Географические координаты (Lon, Lat WGS84)
                # rasterio.transform.xy возвращает списки, переводим в numpy
                xs_wgs, ys_wgs = rasterio.transform.xy(transform, rows, cols)
                xs_wgs = np.array(xs_wgs)  # Longitude
                ys_wgs = np.array(ys_wgs)  # Latitude

                # 3. Настройка проекции (Геодезия -> Метры)
                # Берем центр области для определения зоны UTM
                center_lat = (min_lat + max_lat) / 2
                center_lon = (min_lon + max_lon) / 2

                target_crs = self.get_utm_epsg(center_lat, center_lon)
                self.progress.emit(f"Трансформация в {target_crs}...")

                # Создаем трансформер: WGS84 (4326) -> UTM
                transformer = Transformer.from_crs("epsg:4326", target_crs, always_xy=True)

                # Массовая конвертация координат (это быстро работает через numpy)
                xx_utm, yy_utm = transformer.transform(xs_wgs, ys_wgs)

                # Выпрямляем массивы в один длинный список
                x_flat = xx_utm.flatten()
                y_flat = yy_utm.flatten()
                z_flat = elevation_data.flatten()

                # 4. Запись в файл
                self.progress.emit("Сохранение XYZ файла...")

                with open(self.output_file, 'w') as f:
                    # Можно добавить заголовок, если нужно (X,Y,Z), но для CAD чистые данные лучше
                    # f.write("X,Y,Z\n")

                    buffer = []
                    count = 0

                    for x, y, z in zip(x_flat, y_flat, z_flat):
                        # Фильтр пустых данных и слишком низких значений (ошибок)
                        if z != nodata and z > -10000:
                            # Форматируем: 3 знака после запятой для метров
                            line = f"{x:.3f},{y:.3f},{z:.3f}\n"
                            buffer.append(line)

                            count += 1
                            if count >= 20000:  # Пишем порциями по 20к строк
                                f.writelines(buffer)
                                buffer = []
                                count = 0

                    if buffer:
                        f.writelines(buffer)

            self.finished.emit(f"Успех! Система координат: {target_crs}")

        except Exception as e:
            self.finished.emit(f"Ошибка: {str(e)}")


# ================= ИНТЕРФЕЙС (Без изменений логики) =================

class MapApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Geo XYZ Downloader (UTM/Metric)")
        self.resize(1000, 700)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        self.web_view = QWebEngineView()
        layout.addWidget(self.web_view, stretch=1)

        controls_layout = QVBoxLayout()
        self.info_label = QLabel("Выберите прямоугольник на карте.")
        controls_layout.addWidget(self.info_label)

        self.coords_label = QLabel("Зона не выбрана")
        controls_layout.addWidget(self.coords_label)

        self.btn_download = QPushButton("Скачать рельеф (XYZ UTM)")
        self.btn_download.setEnabled(False)
        self.btn_download.clicked.connect(self.start_download)
        controls_layout.addWidget(self.btn_download)

        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        controls_layout.addWidget(self.progress_bar)

        layout.addLayout(controls_layout)

        self.selected_bounds = None
        self.init_map()

    def init_map(self):
        m = folium.Map(location=[55.75, 37.61], zoom_start=5)  # Центр на Москву для удобства
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

        # JS скрипт для перехвата координат
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
                self.coords_label.setText(
                    f"Выбрано: Lat {data['south']:.2f}..{data['north']:.2f}, Lon {data['west']:.2f}..{data['east']:.2f}")
                self.btn_download.setEnabled(True)
            except:
                pass

    def start_download(self):
        file_path, _ = QFileDialog.getSaveFileName(self, "Сохранить XYZ", "", "CSV Files (*.csv);;Text Files (*.txt)")
        if not file_path: return

        self.btn_download.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)

        self.worker = DownloadWorker(self.selected_bounds, file_path)
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