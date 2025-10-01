# conda activate allpy311

# pip install pywin32

import win32com.client
import pythoncom


def main():
    print("=== Подключение к Civil 3D через COM ===")

    try:
        # Инициализация COM (обязательно для многопоточных приложений)
        pythoncom.CoInitialize()

        # Подключение к уже запущенному экземпляру Civil 3D
        # Если его нет, эта строка вызовет ошибку.
        acad = win32com.client.GetActiveObject("AutoCAD.Application")
        print(f"[OK] Подключено к: {acad.Caption}")

        # Получаем активный документ
        doc = acad.ActiveDocument
        print(f"[OK] Активный документ: {doc.Name}")

        # Получаем пространство модели (Model Space)
        mspace = doc.ModelSpace

        # Пример: найдем все объекты на слое "C-ROAD-CENTERLINE"
        # и выведем их тип и количество вершин (если это полилиния)
        centerline_count = 0
        Layer = '0'
        for i in range(mspace.Count):
            try:
                obj = mspace.Item(i)
                if obj.Layer == Layer:
                    centerline_count += 1
                    if obj.ObjectName == "AcDbPolyline":
                        print(f"  Найдена 2D полилиния с {obj.Coordinates.Count // 2} вершинами.")
                    elif obj.ObjectName == "AcDb3dPolyline":
                        print(f"  Найдена 3D полилиния.")
            except:
                # Некоторые объекты могут не иметь свойства Layer или ObjectName
                continue

        print(f"\n[INFO] Найдено {centerline_count} объектов на слое '{Layer}'.")

        # Пример: создадим простую точку в начале координат
        # point = mspace.AddPoint((0, 0, 0))
        # print("[OK] Точка создана в (0,0,0)")

    except Exception as e:
        print(f"[ERR] Ошибка: {e}")
        print("Убедитесь, что Civil 3D запущен и открыт чертеж!")
    finally:
        # Завершаем работу с COM
        pythoncom.CoUninitialize()


if __name__ == "__main__":
    main()