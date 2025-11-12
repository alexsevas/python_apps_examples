# conda activate cv311

'''
v0.0.3
- импорт форматов .CSV/.TXT/.LAS/.LAZ/.PLY/.OBJ/.XYZ,
- трансформирование координат через pyproj,
- построение TIN-поверхность с помощью Delaunay-триангуляции (визуализация её в PyVista)
- эспорт в OBJ, PLY, VTK и другие форматы

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


import os
import numpy as np
from scipy.spatial import Delaunay
import pyvista as pv
import laspy
from pyproj import Transformer, CRS


def load_points_csv(path, x_idx=0, y_idx=1, z_idx=2,
                    delimiter=',', skip_header=0):
    data = np.loadtxt(path, delimiter=delimiter, skiprows=skip_header)
    pts = data[:, [x_idx, y_idx, z_idx]]
    return pts


def load_points_las(path):
    las = laspy.read(path)
    xs = las.x
    ys = las.y
    zs = las.z
    pts = np.vstack((xs, ys, zs)).T
    try:
        crs = las.header.parse_crs()
    except Exception:
        crs = None
    return pts, crs


def load_points_other(path):
    # Например, .xyz или .txt с тремя колонками
    ext = os.path.splitext(path)[1].lower()
    if ext in ['.xyz', '.txt']:
        return load_points_csv(path, delimiter=' ', skip_header=0), None
    else:
        raise ValueError(f"Не поддерживаемый формат: {ext}")


def reproject_points(pts, src_crs, dst_crs="EPSG:4326"):
    if src_crs is None:
        return pts
    transformer = Transformer.from_crs(src_crs, dst_crs, always_xy=True)
    xs, ys = transformer.transform(pts[:, 0], pts[:, 1])
    zs = pts[:, 2]
    return np.vstack((xs, ys, zs)).T


def build_tin(pts):
    tri = Delaunay(pts[:, :2])
    return tri.simplices


def visualize_and_export(pts, triangles,
                         export_path=None,
                         export_format="obj",
                         show_edges=True, cmap="viridis"):
    # Создаём mesh в PyVista
    faces = np.hstack([np.full((triangles.shape[0], 1), 3, dtype=np.int64), triangles.astype(np.int64)])
    mesh = pv.PolyData(pts, faces)
    mesh.point_data["Z"] = pts[:, 2]

    plotter = pv.Plotter()
    plotter.add_mesh(mesh, scalars="Z", cmap=cmap, show_edges=show_edges)
    plotter.add_axes()
    plotter.show_grid()

    if export_path:
        ext = export_format.lower()
        if ext in ["obj"]:
            plotter.export_obj(export_path)
            print(f"Экспортировано в OBJ: {export_path}")
        else:
            mesh.save(export_path)
            print(f"Экспортировано в {export_format.upper()}: {export_path}")

    plotter.show()


def main():
    input_path = "points.csv"  # замените на свой файл (.las/.laz/.csv/.xyz)
    dst_crs = "EPSG:4326"

    ext = os.path.splitext(input_path)[1].lower()
    if ext in ['.las', '.laz']:
        pts, src_crs = load_points_las(input_path)
    elif ext in ['.csv', '.txt']:
        pts = load_points_csv(input_path, delimiter=',', skip_header=1)
        src_crs = None
    else:
        pts, src_crs = load_points_other(input_path)

    pts = reproject_points(pts, src_crs, dst_crs)

    # Опционально: фильтрация / снижение плотности
    # pts = pts[::10]

    triangles = build_tin(pts)

    export_path = "tin_surface.obj"
    visualize_and_export(pts, triangles, export_path=export_path, export_format="obj")


if __name__ == "__main__":
    main()