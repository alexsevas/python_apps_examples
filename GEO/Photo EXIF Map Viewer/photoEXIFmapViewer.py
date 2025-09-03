# conda activate allpy311

import os
import csv
import exifread
from PyQt5.QtWidgets import (QApplication, QMainWindow, QPushButton, QFileDialog,
                             QVBoxLayout, QWidget, QProgressBar, QLabel)
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtCore import QUrl
import folium

class PhotoMapApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Photo EXIF Map Viewer")
        self.setGeometry(100, 100, 1000, 800)

        # Создаем интерфейс
        container = QWidget()
        layout = QVBoxLayout()

        self.btn_select = QPushButton("Выбрать папку с фотографиями")
        self.btn_select.clicked.connect(self.select_folder)
        layout.addWidget(self.btn_select)

        self.status_label = QLabel("Готов к работе")
        layout.addWidget(self.status_label)

        self.progress = QProgressBar()
        layout.addWidget(self.progress)

        self.web_view = QWebEngineView()
        layout.addWidget(self.web_view)

        container.setLayout(layout)
        self.setCentralWidget(container)

        # Инициализируем карту
        self.init_map()

    def init_map(self):
        """Создает пустую карту"""
        m = folium.Map(location=[0, 0], zoom_start=2, tiles='OpenStreetMap')
        m.save('map.html')
        self.web_view.load(QUrl.fromLocalFile(os.path.abspath('map.html')))

    def select_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Выберите папку с фотографиями")
        if folder:
            self.process_folder(folder)

    def process_folder(self, folder_path):
        try:
            # Поиск фотографий
            self.status_label.setText("Поиск фотографий...")
            photos = self.find_photos(folder_path)

            if not photos:
                self.status_label.setText("Фотографии не найдены")
                return

            # Обработка EXIF
            self.status_label.setText(f"Найдено {len(photos)} фотографий. Обработка EXIF...")
            self.progress.setMaximum(len(photos))

            processed_photos = []
            for i, photo in enumerate(photos):
                coords = self.get_coordinates(photo)
                if coords:
                    processed_photos.append({
                        'path': photo,
                        'filename': os.path.basename(photo),
                        'lat': coords[0],
                        'lon': coords[1]
                    })
                self.progress.setValue(i + 1)

            if not processed_photos:
                self.status_label.setText("Координаты не найдены в EXIF")
                return

            # Сохранение CSV
            self.save_to_csv(processed_photos)

            # Отображение на карте
            self.status_label.setText(f"Найдено {len(processed_photos)} фотографий с координатами. Генерация карты...")
            self.generate_map(processed_photos)

            self.status_label.setText(f"Готово! Найдено {len(processed_photos)} фотографий с координатами")

        except Exception as e:
            self.status_label.setText(f"Ошибка: {str(e)}")

    def find_photos(self, folder_path):
        """Ищет фотографии в папке"""
        photo_extensions = ('.jpg', '.jpeg', '.png', '.heic', '.webp')
        photos = []

        for root, _, files in os.walk(folder_path):
            for file in files:
                if file.lower().endswith(photo_extensions):
                    photos.append(os.path.join(root, file))

        return photos

    def get_coordinates(self, file_path):
        """Извлекает координаты из EXIF"""
        try:
            with open(file_path, 'rb') as f:
                tags = exifread.process_file(f, details=False)

                # Проверяем наличие GPS-данных
                if 'GPS GPSLatitude' in tags and 'GPS GPSLongitude' in tags:
                    lat = self.convert_to_degrees(tags['GPS GPSLatitude'])
                    lon = self.convert_to_degrees(tags['GPS GPSLongitude'])

                    # Корректировка знака
                    if 'GPS GPSLatitudeRef' in tags and str(tags['GPS GPSLatitudeRef']) == 'S':
                        lat = -lat
                    if 'GPS GPSLongitudeRef' in tags and str(tags['GPS GPSLongitudeRef']) == 'W':
                        lon = -lon

                    return (lat, lon)
        except Exception as e:
            print(f"Ошибка обработки {file_path}: {e}")
        return None

    def convert_to_degrees(self, value):
        """Преобразует координаты из формата DMS в десятичные градусы"""
        d = float(value.values[0].num) / float(value.values[0].den)
        m = float(value.values[1].num) / float(value.values[1].den)
        s = float(value.values[2].num) / float(value.values[2].den)

        return d + (m / 60.0) + (s / 3600.0)

    def save_to_csv(self, photos):
        """Сохраняет данные в CSV"""
        with open('photo_coordinates.csv', 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['Имя файла', 'Полный путь', 'Широта', 'Долгота'])

            for photo in photos:
                writer.writerow([
                    photo['filename'],
                    photo['path'],
                    photo['lat'],
                    photo['lon']
                ])

    def generate_map(self, photos):
        """Генерирует карту с метками"""
        # Определяем центральную точку
        avg_lat = sum(p['lat'] for p in photos) / len(photos)
        avg_lon = sum(p['lon'] for p in photos) / len(photos)

        m = folium.Map(location=[avg_lat, avg_lon], zoom_start=10, tiles='OpenStreetMap')

        for photo in photos:
            folium.Marker(
                location=[photo['lat'], photo['lon']],
                popup=f"{photo['filename']}<br>{photo['path']}",
                icon=folium.Icon(color='blue', icon='info-sign')
            ).add_to(m)

        m.save('map.html')
        self.web_view.load(QUrl.fromLocalFile(os.path.abspath('map.html')))

if __name__ == "__main__":
    app = QApplication([])
    window = PhotoMapApp()
    window.show()
    app.exec_()