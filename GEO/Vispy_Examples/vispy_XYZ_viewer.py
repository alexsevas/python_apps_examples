# первый рабочий вариант

# conda activate hydro_env

import sys
import numpy as np
import pandas as pd
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QSlider, QLabel, QComboBox, QFileDialog, QGroupBox,
    QSizePolicy
)
from PyQt5.QtCore import Qt
from vispy.scene import SceneCanvas, Markers, XYZAxis
from vispy.color import get_colormap, BaseColormap


class HydrographicVisualizer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("XYZ-viewer (with VisPy)")
        self.setGeometry(100, 100, 1200, 800)

        # Основной виджет и макет
        main_widget = QWidget()
        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(5, 5, 5, 5)  # Уменьшаем отступы

        # Создаем VisPy Canvas и встраиваем его в PyQt5
        self.canvas = SceneCanvas(keys='interactive', show=True)
        self.canvas.create_native()
        self.canvas.native.setMinimumSize(800, 600)
        self.canvas.native.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.view = self.canvas.central_widget.add_view()

        # Добавляем 3D оси
        self.axis = XYZAxis(parent=self.view.scene)
        self.view.add(self.axis)

        # Панель управления (уменьшаем ширину)
        control_panel = QGroupBox("Панель управления")
        control_panel.setMaximumWidth(300)
        control_panel.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)
        control_layout = QVBoxLayout()
        control_layout.setSpacing(10)

        # Кнопка загрузки файла
        self.load_btn = QPushButton("Загрузить XYZ данные")
        self.load_btn.clicked.connect(self.load_data)
        control_layout.addWidget(self.load_btn)

        # Слайдер размера точек
        size_layout = QHBoxLayout()
        size_layout.addWidget(QLabel("Размер точек:"))
        self.size_slider = QSlider(Qt.Horizontal)
        self.size_slider.setRange(1, 20)
        self.size_slider.setValue(5)
        self.size_slider.valueChanged.connect(self.update_point_size)
        size_layout.addWidget(self.size_slider)
        self.size_label = QLabel("5")
        size_layout.addWidget(self.size_label)
        control_layout.addLayout(size_layout)

        # Выбор палитры
        palette_layout = QHBoxLayout()
        palette_layout.addWidget(QLabel("Цветовая палитра:"))
        self.palette_combo = QComboBox()
        # Используем только гарантированно доступные палитры
        self.available_palettes = [
            'viridis', 'plasma', 'inferno', 'magma',
            'cool', 'hot', 'hsv', 'bwr', 'grays'
        ]
        self.palette_combo.addItems(self.available_palettes)
        self.palette_combo.setCurrentText('viridis')
        self.palette_combo.currentIndexChanged.connect(self.update_colors)
        palette_layout.addWidget(self.palette_combo)
        control_layout.addLayout(palette_layout)

        # Информация о данных
        self.info_label = QLabel("Данные не загружены")
        self.info_label.setWordWrap(True)
        control_layout.addWidget(self.info_label)

        # Добавляем растяжку вниз, чтобы элементы не распределялись равномерно
        control_layout.addStretch(1)

        control_panel.setLayout(control_layout)

        # Добавляем элементы в основной макет
        # Делаем так, чтобы область визуализации занимала 70% ширины
        main_layout.addWidget(self.canvas.native, 70)
        main_layout.addWidget(control_panel, 30)
        main_widget.setLayout(main_layout)

        self.setCentralWidget(main_widget)

        # Переменные для данных
        self.points = None
        self.colors = None
        self.current_size = 5
        self.current_palette = 'viridis'

        # Инициализируем маркеры с "заглушкой"
        self.scatter = Markers()
        self.view.add(self.scatter)
        self.scatter.set_data(
            pos=np.zeros((1, 3)),
            size=0.001,
            face_color=(0, 0, 0, 0)
        )

        # Настройка камеры
        self.view.camera = 'turntable'
        self.view.camera.fov = 45
        # Устанавливаем фиксированный диапазон
        self.view.camera.set_range(x=(-100, 100), y=(-100, 100), z=(-100, 100))
        self.view.camera.distance = 5

    def load_data(self):
        """Загрузка данных из файла XYZ"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Открыть файл XYZ", "", "Текстовые файлы (*.txt *.csv *.dat);;Все файлы (*)"
        )

        if not file_path:
            return

        try:
            # Попробуем определить разделитель
            with open(file_path, 'r') as f:
                first_line = f.readline()
                if ',' in first_line:
                    delimiter = ','
                else:
                    delimiter = None  # Автоматическое определение пробелов

            # Загрузка данных
            data = np.loadtxt(file_path, delimiter=delimiter)

            if data.shape[1] < 3:
                raise ValueError("Файл должен содержать как минимум 3 колонки (X, Y, Z)")

            self.points = data[:, :3]

            # Нормализуем Z для использования в цветовой карте
            z_values = self.points[:, 2]
            z_min, z_max = z_values.min(), z_values.max()
            if z_max > z_min:
                self.z_normalized = (z_values - z_min) / (z_max - z_min)
            else:
                self.z_normalized = np.zeros_like(z_values)

            # Обновляем информацию
            self.info_label.setText(f"Загружено: {len(self.points)} точек\n"
                                    f"Z: от {z_min:.2f} до {z_max:.2f}")

            # ВАЖНО: обновляем визуализацию ПОСЛЕ установки данных
            self.update_visualization()

            # Автоматически настраиваем камеру на данные
            self.auto_adjust_camera()

        except Exception as e:
            self.info_label.setText(f"Ошибка: {str(e)}")

    def auto_adjust_camera(self):
        """Автоматическая настройка камеры под данные"""
        if self.points is None or len(self.points) == 0:
            return

        # Вычисляем диапазон данных
        x_min, y_min, z_min = self.points.min(axis=0)
        x_max, y_max, z_max = self.points.max(axis=0)

        # Добавляем небольшой отступ
        x_range = x_max - x_min
        y_range = y_max - y_min
        z_range = z_max - z_min

        margin = 0.1
        x_min -= x_range * margin
        x_max += x_range * margin
        y_min -= y_range * margin
        y_max += y_range * margin
        z_min -= z_range * margin
        z_max += z_range * margin

        # Устанавливаем диапазон камеры
        self.view.camera.set_range(x=(x_min, x_max),
                                   y=(y_min, y_max),
                                   z=(z_min, z_max))

        # Устанавливаем начальное расстояние камеры
        max_range = max(x_range, y_range, z_range)
        self.view.camera.distance = max_range * 1.5

    def update_visualization(self):
        """Обновление всей визуализации"""
        if self.points is None or len(self.points) == 0:
            return

        # Сначала обновляем цвета
        self.update_colors()

        # Затем обновляем размер
        self.update_point_size(self.size_slider.value())

    def update_colors(self):
        """Обновление цветовой схемы"""
        if self.points is None or len(self.points) == 0:
            return

        self.current_palette = self.palette_combo.currentText()

        try:
            # Проверяем, что палитра существует
            cmap = get_colormap(self.current_palette)
            self.colors = cmap[self.z_normalized]

            # Обновляем отображение
            self.scatter.set_data(
                pos=self.points,
                size=self.current_size,
                edge_color=None,
                face_color=self.colors.rgba
            )
            self.canvas.update()
        except KeyError:
            # Если палитра не найдена, используем viridis как fallback
            self.palette_combo.setCurrentText('viridis')
            self.current_palette = 'viridis'
            self.info_label.setText(f"Ошибка: палитра не найдена. Используется viridis.")

    def update_point_size(self, value):
        """Изменение размера точек"""
        self.current_size = value
        self.size_label.setText(str(value))

        if self.points is not None and len(self.points) > 0:
            self.scatter.set_data(
                pos=self.points,
                size=self.current_size,
                edge_color=None,
                face_color=self.colors.rgba if self.colors is not None else None
            )
            self.canvas.update()

    def resizeEvent(self, event):
        """Обработка изменения размера окна"""
        super().resizeEvent(event)
        # Убедимся, что canvas обновляет размер
        if hasattr(self, 'canvas') and self.canvas is not None:
            self.canvas.native.resize(self.canvas.native.size())

    def closeEvent(self, event):
        """Обработка закрытия окна"""
        if hasattr(self, 'canvas') and self.canvas is not None:
            self.canvas.close()
        event.accept()


if __name__ == "__main__":
    # Инициализация приложения
    app = QApplication(sys.argv)
    window = HydrographicVisualizer()
    window.show()
    sys.exit(app.exec_())