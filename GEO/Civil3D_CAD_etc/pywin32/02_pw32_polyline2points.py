# conda activate allpy311

# pip install pywin32

import win32com.client
import pythoncom


def get_3d_polyline_vertices(polyline_obj):
    """
    Извлекает вершины из 3D полилинии (AcDb3dPolyline)
    с помощью итеративного вызова Coordinate(i).
    """
    vertices = []
    i = 0
    while True:
        try:
            coord = polyline_obj.Coordinate(i)
            # coord - это объект Point, преобразуем в кортеж
            vertices.append((coord[0], coord[1], coord[2]))
            i += 1
        except:
            # Выход из цикла, когда индекс больше не существует
            break
    return vertices


def main():
    print("\n======================================================")
    print("=== Извлечение вершин (точек) полилиний в Civil 3D ===")
    print("======================================================\n")

    try:
        pythoncom.CoInitialize()
        acad = win32com.client.GetActiveObject("AutoCAD.Application")
        doc = acad.ActiveDocument
        mspace = doc.ModelSpace

        print(f"[OK] Подключено к: {acad.Caption}")
        print(f"[OK] Анализ чертежа: {doc.Name}\n")

        # Собираем полилинии
        polylines = []
        for i in range(mspace.Count):
            try:
                obj = mspace.Item(i)
                if obj.ObjectName in ["AcDbPolyline", "AcDb3dPolyline"]:
                    polylines.append(obj)
            except:
                continue

        if not polylines:
            print("В пространстве модели не найдено полилиний.")
            return

        print(f"Найдено полилиний: {len(polylines)}\n")
        for idx, pl in enumerate(polylines, start=1):
            layer = getattr(pl, 'Layer', 'Unknown')
            obj_type = "2D" if pl.ObjectName == "AcDbPolyline" else "3D"
            print(f"{idx}. [{obj_type}] Слой: '{layer}'")

        # Цикл выбора
        while True:
            choice = input(f"\nВведите номер полилинии (1-{len(polylines)}) или 'q' для выхода: ")
            if choice.lower() == 'q':
                break

            try:
                choice_idx = int(choice) - 1
                if not (0 <= choice_idx < len(polylines)):
                    print("Неверный номер.")
                    continue

                selected_pl = polylines[choice_idx]
                print(f"\n--- Информация о полилинии ---")

                if selected_pl.ObjectName == "AcDbPolyline":
                    coords = list(selected_pl.Coordinates)
                    vertices = [(coords[i], coords[i + 1], 0.0) for i in range(0, len(coords), 2)]
                    print("Тип: 2D Polyline (LWPOLYLINE)")
                else:  # AcDb3dPolyline
                    vertices = get_3d_polyline_vertices(selected_pl)
                    print("Тип: 3D Polyline")

                print(f"Количество вершин: {len(vertices)}")
                print("Координаты вершин (X, Y, Z):")
                for v_idx, (x, y, z) in enumerate(vertices, start=1):
                    print(f"  {v_idx}: ({x:.3f}, {y:.3f}, {z:.3f})")
                print("\n" + "-" * 40)

            except Exception as inner_e:
                print(f"Ошибка при обработке полилинии: {inner_e}")

    except Exception as e:
        print(f"[ERR] Ошибка: {e}")
        print("Убедитесь, что Civil 3D запущен и открыт чертеж!")
    finally:
        pythoncom.CoUninitialize()


if __name__ == "__main__":
    main()