# conda activate cv311

'''
v0.0.2
Расширенный вариант, позволяет:
- загружать облака точек из разных форматов (например, CSV, LAS/LAZ)
- учитывать геопривязку и разные системы координат
- строить TIN-поверхность и визуализировать её с помощью PyVista
- обеспечивать базовую инфраструктуру, которую можно расширить под конкретные задачи

v0.0.01
Пример программы на Python, которая позволяет загрузить облако точек (в формате CSV или LAS/LAZ) и построить
TIN-поверхность (триангуляцию) с помощью библиотеки SciPy (или других средств).
Программа рассчитана на базовое использование: загрузка, фильтрация, построение триангуляции (триангуляция Делоне)
и визуализация с помощью matplotlib или pyvista.
'''


import numpy as np
import os
from scipy.spatial import Delaunay
import pyvista as pv
import laspy
import rasterio
from pyproj import Transformer


def load_points_from_csv(path, x_idx=0, y_idx=1, z_idx=2,
                         delimiter=',', skip_header=0):
    data = np.loadtxt(path, delimiter=delimiter, skiprows=skip_header)
    pts = data[:, [x_idx, y_idx, z_idx]]
    return pts


def load_points_from_las(path):
    # LAS/LAZ support via laspy
    las = laspy.read(path)
    # las.x, las.y, las.z are scaled values
    xs = las.x
    ys = las.y
    zs = las.z
    pts = np.vstack((xs, ys, zs)).T
    # Check for CRS: las.header has .crs or .vlrs
    try:
        crs = las.header.parse_crs()
    except Exception:
        crs = None
    return pts, crs


def reproject_points(pts, src_crs, dst_crs="EPSG:4326"):
    # pts: Nx3 numpy array; src_crs and dst_crs in PROJ format
    transformer = Transformer.from_crs(src_crs, dst_crs, always_xy=True)
    xs, ys = transformer.transform(pts[:, 0], pts[:, 1])
    zs = pts[:, 2]
    return np.vstack((xs, ys, zs)).T


def build_tin(pts):
    """Построить Delaunay-триангуляцию по XY и возвратить индексы треугольников."""
    tri = Delaunay(pts[:, :2])
    return tri.simplices


def visualize_tin(pts, triangles, show_edges=True, cmap="viridis"):
    mesh = pv.PolyData(pts, np.hstack([
        np.full((triangles.shape[0], 1), 3, dtype=np.int64),
        triangles.astype(np.int64)
    ]))
    mesh["Z"] = pts[:, 2]
    plotter = pv.Plotter()
    plotter.add_mesh(mesh, scalars="Z", cmap=cmap, show_edges=show_edges)
    plotter.add_axes()
    plotter.show_grid()
    plotter.show()


def main():
    # Настройки
    input_path = "your_pointcloud.las"  # или .csv
    dst_crs = "EPSG:4326"  # целевая система координат (например WGS84)

    ext = os.path.splitext(input_path)[1].lower()
    if ext in [".las", ".laz"]:
        pts, src_crs = load_points_from_las(input_path)
    elif ext in [".csv", ".txt"]:
        pts = load_points_from_csv(input_path, delimiter=',', skip_header=1)
        src_crs = None
    else:
        raise ValueError(f"Unsupported input format: {ext}")

    # Если есть система координат — преобразуем
    if src_crs is not None:
        pts = reproject_points(pts, src_crs, dst_crs)

    # Опционально: фильтрация или снижение плотности
    # pts = pts[::5]  # например, взять каждую 5-ю точку

    # Построение TIN
    triangles = build_tin(pts)

    # Визуализация
    visualize_tin(pts, triangles)


if __name__ == "__main__":
    main()
