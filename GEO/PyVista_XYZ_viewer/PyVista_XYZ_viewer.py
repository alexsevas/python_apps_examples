# conda activate cv311

# Пример программы на Python, которая позволяет загрузить облако точек (в формате CSV или LAS/LAZ) и построить
# TIN-поверхность (триангуляцию) с помощью библиотеки SciPy (или других средств).
# Программа рассчитана на базовое использование: загрузка, фильтрация, построение триангуляции (триангуляция Делоне)
# и визуализация с помощью matplotlib или pyvista.


import numpy as np
from scipy.spatial import Delaunay
import matplotlib.pyplot as plt

# Для трёхмерной визуализации
try:
    import pyvista as pv
    use_pyvista = True
except ImportError:
    use_pyvista = False

def load_point_cloud_csv(path, x_idx=0, y_idx=1, z_idx=2, delimiter=',', skip_header=0):
    """
    Загружает облако точек из CSV-файла.
    path – путь к файлу
    x_idx, y_idx, z_idx – индексы столбцов
    """
    data = np.loadtxt(path, delimiter=delimiter, skiprows=skip_header)
    pts = data[:, [x_idx, y_idx, z_idx]]
    return pts

def filter_points(pts, z_min=None, z_max=None):
    """
    Простейшая фильтрация по высоте Z.
    """
    if z_min is not None:
        pts = pts[pts[:,2] >= z_min]
    if z_max is not None:
        pts = pts[pts[:,2] <= z_max]
    return pts

def build_tin(pts_xy, pts_z):
    """
    Строит Delaunay-триангуляцию по проекции XY, потом возвращает вершины + треугольники.
    """
    tri = Delaunay(pts_xy)
    triangles = tri.simplices
    return triangles

def visualize_tin(pts, triangles):
    """
    Визуализация TIN.
    """
    if use_pyvista:
        mesh = pv.PolyData(pts, np.hstack([np.full((triangles.shape[0],1),3), triangles]).astype(np.int64))
        mesh.point_data["Z"] = pts[:,2]
        mesh.plot(scalars="Z", show_edges=True)
    else:
        fig = plt.figure()
        ax = fig.add_subplot(111, projection='3d')
        ax.plot_trisurf(pts[:,0], pts[:,1], pts[:,2], triangles=triangles, cmap='viridis', edgecolor='none')
        ax.set_xlabel('X')
        ax.set_ylabel('Y')
        ax.set_zlabel('Z')
        plt.show()

def main():
    # Пример: загрузка облака точек
    pts = load_point_cloud_csv("points.csv", delimiter=',', skip_header=1)

    # Фильтрация – опционально
    # pts = filter_points(pts, z_min=0)

    # Подготовка для триангуляции: используем только X,Y для триангуляции
    pts_xy = pts[:, :2]
    pts_z  = pts[:, 2]

    # Построение TIN
    triangles = build_tin(pts_xy, pts_z)

    # Визуализация
    visualize_tin(pts, triangles)

if __name__ == "__main__":
    main()