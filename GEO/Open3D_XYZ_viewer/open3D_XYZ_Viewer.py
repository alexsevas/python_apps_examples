# conda activate py39test, 3dpy310

# pip install open3d

# Data example:
# D:\Projects\AS\GEO\Open3D_XYZ_viewer\data\SBE_data_01.xyz
# D:\Projects\AS\GEO\Open3D_XYZ_viewer\data\MBE_data_01.xyz

import open3d as o3d
import numpy as np
import matplotlib.cm as cm
import os

class HydroSurveyVisualizer:
    def __init__(self, file_path):
        self.points = self.load_xyz(file_path)
        # Создаем облако точек напрямую
        self.pcd = o3d.geometry.PointCloud()
        self.pcd.points = o3d.utility.Vector3dVector(self.points)

        self.current_cmap = 'viridis'
        self.point_size = 2.0
        self.vis = o3d.visualization.VisualizerWithKeyCallback()
        self.vis.create_window(window_name='Hydrographic XYZ viewer')

        # Сначала обновляем цвета, ТОЛЬКО ПОСЛЕ того как pcd создан
        self.update_colors()

        # Настройка интерфейса
        render_option = self.vis.get_render_option()
        render_option.background_color = np.asarray([0.1, 0.1, 0.1])
        render_option.point_size = self.point_size

        self.vis.add_geometry(self.pcd)
        self.setup_callbacks()

    def load_xyz(self, file_path):
        """Загрузка XYZ-данных из текстового файла"""
        points = []
        with open(file_path, 'r') as f:
            for line in f:
                # Определение разделителя (запятая или пробел)
                parts = line.strip().split(',')
                if len(parts) < 3:
                    parts = line.strip().split()

                if len(parts) >= 3:
                    try:
                        x, y, z = map(float, parts[:3])
                        points.append([x, y, z])
                    except ValueError:
                        continue
        return np.array(points)

    def update_colors(self):
        """Обновление цветов на основе текущей цветовой схемы"""
        if len(self.points) == 0:
            return

        z_values = np.asarray(self.pcd.points)[:, 2]
        z_min, z_max = z_values.min(), z_values.max()

        # Нормализация значений глубины
        normalized_z = (z_values - z_min) / (z_max - z_min + 1e-8)

        # Применение цветовой схемы
        colors = cm.get_cmap(self.current_cmap)(normalized_z)[:, :3]
        self.pcd.colors = o3d.utility.Vector3dVector(colors)

    def cycle_colormap(self, vis):
        """Смена цветовой схемы при нажатии 'C'"""
        colormaps = ['viridis', 'plasma', 'magma', 'inferno', 'coolwarm', 'jet', 'hsv']
        idx = (colormaps.index(self.current_cmap) + 1) % len(colormaps)
        self.current_cmap = colormaps[idx]
        self.update_colors()
        vis.update_geometry(self.pcd)
        vis.reset_view_point(True)
        print(f"Color map changed to: {self.current_cmap}")
        return False

    def increase_point_size(self, vis):
        """Увеличение размера точек при нажатии '+'"""
        self.point_size = min(20, self.point_size + 1)
        vis.get_render_option().point_size = self.point_size
        print(f"Point size: {self.point_size}")
        return False

    def decrease_point_size(self, vis):
        """Уменьшение размера точек при нажатии '-'"""
        self.point_size = max(1, self.point_size - 1)
        vis.get_render_option().point_size = self.point_size
        print(f"Point size: {self.point_size}")
        return False

    def reset_view(self, vis):
        """Сброс вида при нажатии 'R'"""
        vis.reset_view_point(True)
        print("View reset")
        return False

    def print_help(self, vis):
        """Вывод справки при нажатии 'H'"""
        print("\n===== Управление =====")
        print("C: Сменить цветовую схему")
        print("+/-: Увеличить/уменьшить размер точек")
        print("R: Сбросить вид")
        print("H: Показать эту справку")
        print("Q: Выход")
        print("=====================\n")
        return False

    def setup_callbacks(self):
        """Настройка обработчиков клавиш"""
        self.vis.register_key_callback(ord("C"), self.cycle_colormap)
        self.vis.register_key_callback(ord("+"), self.increase_point_size)
        self.vis.register_key_callback(ord("-"), self.decrease_point_size)
        self.vis.register_key_callback(ord("R"), self.reset_view)
        self.vis.register_key_callback(ord("H"), self.print_help)

    def run(self):
        """Запуск визуализации"""
        print("\nЗагружено точек:", len(self.points))
        print("Доступные команды (нажмите H для справки)")
        self.print_help(None)
        self.vis.run()
        self.vis.destroy_window()


if __name__ == "__main__":
    # Получение пути к файлу
    file_path = input("Введите путь к XYZ-файлу гидрографической съемки: ").strip()

    if not os.path.exists(file_path):
        print(f"Ошибка: Файл {file_path} не найден!")
        exit(1)

    try:
        visualizer = HydroSurveyVisualizer(file_path)
        visualizer.run()
    except Exception as e:
        print(f"Произошла ошибка: {str(e)}")
        print("Убедитесь, что файл содержит корректные XYZ-координаты")