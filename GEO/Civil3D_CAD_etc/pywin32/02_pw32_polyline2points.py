# conda activate allpy311

# pip install pywin32


import win32com.client
import pythoncom


def get_polyline_info(polyline_obj):
    """
    Извлекает информацию о полилинии: тип и координаты вершин.
    """
    info = {}
    obj_name = polyline_obj.ObjectName

    if obj_name == "AcDbPolyline":
        # Это легковесная 2D полилиния (LWPOLYLINE)
        # Координаты хранятся в одном плоском массиве: [x1, y1, x2, y2, ...]
        coords = list(polyline_obj.Coordinates)
        vertices = []
        for i in range(0, len(coords), 2):
            x, y = coords[i], coords[i + 1]
            # Z-координата по умолчанию 0 для 2D полилинии
            z = 0.0
            vertices.append((x, y, z))
        info['type'] = "2D Polyline (LWPOLYLINE)"
        info['vertices'] = vertices

    elif obj_name == "AcDb3dPolyline":
        # Это 3D полилиния (POLYLINE)
        # Вершины нужно перебирать по одной
        vertices = []
        for i in range(polyline_obj.Coordinates.Count):
            vertex = polyline_obj.Coordinates[i]
            vertices.append((vertex[0], vertex[1], vertex[2]))
        info['type'] = "3D Polyline"
        info['vertices'] = vertices

    else:
        # Неожиданный тип объекта
        info['type'] = f"Unknown ({obj_name})"
        info['vertices'] = []

    return info


def main():
    print("\n======================================================")
    print("=== Извлечение вершин (точек) полилиний в Civil 3D ===")
    print("======================================================\n")

    try:
        # Инициализация COM
        pythoncom.CoInitialize()

        # Подключение к запущенному экземпляру AutoCAD/Civil 3D
        acad = win32com.client.GetActiveObject("AutoCAD.Application")
        doc = acad.ActiveDocument
        mspace = doc.ModelSpace

        print(f"[OK] Подключено к: {acad.Caption}")
        print(f"[OK] Анализ чертежа: {doc.Name}\n")

        # Собираем все полилинии из пространства модели
        polylines = []
        for i in range(mspace.Count):
            try:
                obj = mspace.Item(i)
                if obj.ObjectName in ["AcDbPolyline", "AcDb3dPolyline"]:
                    polylines.append(obj)
            except:
                # Пропускаем объекты, которые не удалось прочитать
                continue

        if not polylines:
            print("В пространстве модели не найдено полилиний.")
            return

        print(f"Найдено полилиний: {len(polylines)}\n")

        # Выводим пронумерованный список
        for idx, pl in enumerate(polylines, start=1):
            layer = getattr(pl, 'Layer', 'Unknown')
            print(f"{idx}. Слой: '{layer}'")

        # Запрашиваем выбор у пользователя
        while True:
            try:
                choice = input(
                    f"\nВведите номер полилинии для просмотра вершин (1-{len(polylines)}) или 'q' для выхода: ")
                if choice.lower() == 'q':
                    break

                choice_idx = int(choice) - 1
                if 0 <= choice_idx < len(polylines):
                    selected_pl = polylines[choice_idx]
                    info = get_polyline_info(selected_pl)

                    print(f"\n--- Информация о полилинии ---")
                    print(f"Тип: {info['type']}")
                    print(f"Количество вершин: {len(info['vertices'])}")
                    print("Координаты вершин (X, Y, Z):")
                    for v_idx, (x, y, z) in enumerate(info['vertices'], start=1):
                        print(f"  {v_idx}: ({x:.3f}, {y:.3f}, {z:.3f})")
                    print("\n" + "-" * 40)
                else:
                    print("Неверный номер. Попробуйте снова.")

            except ValueError:
                print("Пожалуйста, введите число или 'q'.")
            except Exception as e:
                print(f"Ошибка при обработке полилинии: {e}")

    except Exception as e:
        print(f"[ERR] Ошибка: {e}")
        print("Убедитесь, что Civil 3D запущен и открыт чертеж!")
    finally:
        # Завершаем работу с COM
        pythoncom.CoUninitialize()


if __name__ == "__main__":
    main()