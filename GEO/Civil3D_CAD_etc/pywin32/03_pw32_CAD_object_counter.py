# conda activate allpy311
# pip install pywin32

'''
Программа, которая использует pywin32 для подключения к запущенному AutoCAD/Civil 3D и анализирует открытый чертеж.
Она подсчитывает общее количество объектов в пространстве модели и затем выводит детальную статистику по каждому типу
графических примитивов

Как это работает:
- Подключение: Скрипт подключается к уже запущенному процессу AutoCAD через win32com.client.GetActiveObject("AutoCAD.Application").
- Доступ к чертежу: Получает доступ к пространству модели (ModelSpace) активного документа.
- Подсчет: Цикл for перебирает все объекты в пространстве модели. Для каждого объекта запрашивается его тип через свойство ObjectName.
- Классификация: Функция convert_object_name преобразует технические имена вроде "AcDbPolyline" в понятные названия вроде "2D Полилиния (LWPolyline)".
- Агрегация: Результаты подсчета сохраняются в словаре object_counts.
- Вывод: Скрипт выводит общее количество объектов и детальную статистику, отсортированную по популярности.
'''


import win32com.client
import pythoncom


def main():
    print("\n==================================================")
    print("=== Анализ объектов в чертеже AutoCAD/Civil 3D ===")
    print("==================================================")

    try:
        # Инициализация COM
        pythoncom.CoInitialize()

        # Подключение к активному экземпляру AutoCAD
        acad = win32com.client.GetActiveObject("AutoCAD.Application")
        doc = acad.ActiveDocument
        mspace = doc.ModelSpace

        print(f"[OK] Подключено к: {acad.Caption}")
        print(f"[OK] Анализ чертежа: {doc.Name}\n")

        # Словарь для подсчета объектов по типам
        object_counts = {}
        total_count = mspace.Count

        print(f"Общее количество объектов в пространстве модели: {total_count}\n")

        # Если чертеж пустой
        if total_count == 0:
            print("Пространство модели пусто.")
            return

        # Перебираем все объекты
        print("Подсчет объектов по типам. Это может занять некоторое время...")
        for i in range(total_count):
            try:
                # Получаем объект
                obj = mspace.Item(i)
                # Получаем его внутреннее имя (например, "AcDbLine", "AcDbPolyline")
                obj_name = obj.ObjectName

                # Преобразуем техническое имя в понятное пользователю
                readable_name = convert_object_name(obj_name)

                # Увеличиваем счетчик для этого типа
                object_counts[readable_name] = object_counts.get(readable_name, 0) + 1

            except Exception as e:
                # Некоторые объекты (например, прокси-объекты) могут вызвать ошибку
                # Мы просто пропускаем их и считаем как "Неизвестные объекты"
                unknown_key = "Неизвестные/недоступные объекты"
                object_counts[unknown_key] = object_counts.get(unknown_key, 0) + 1
                continue

        # Вывод результатов
        if object_counts:
            print("Статистика по типам объектов:")
            print("-" * 45)
            # Сортируем по количеству (от большего к меньшему)
            for obj_type, count in sorted(object_counts.items(), key=lambda x: x[1], reverse=True):
                print(f"{count:6d} | {obj_type}")
            print("-" * 45)
        else:
            print("Не удалось проанализировать объекты.")

    except Exception as e:
        print(f"[ERR] Ошибка: {e}")
        print("Убедитесь, что AutoCAD или Civil 3D запущены и открыт чертеж!")
    finally:
        # Завершаем работу с COM
        pythoncom.CoUninitialize()


def convert_object_name(technical_name):
    """
    Преобразует техническое имя объекта AutoCAD (например, 'AcDbLine')
    в понятное человеку название.
    """
    name_map = {
        # Базовые примитивы
        "AcDbLine": "Линия (Line)",
        "AcDbPolyline": "2D Полилиния (LWPolyline)",
        "AcDb3dPolyline": "3D Полилиния (3DPoly)",
        "AcDbCircle": "Окружность (Circle)",
        "AcDbArc": "Дуга (Arc)",
        "AcDbEllipse": "Эллипс (Ellipse)",
        "AcDbSpline": "Сплайн (Spline)",

        # Текст
        "AcDbText": "Текст (Text)",
        "AcDbMText": "Многострочный текст (MText)",

        # Точки и штриховки
        "AcDbPoint": "Точка (Point)",
        "AcDbHatch": "Штриховка (Hatch)",
        "AcDbSolid": "Заливка (Solid - 2D Face)",

        # Блоки и атрибуты
        "AcDbBlockReference": "Вставка блока (Block Reference)",
        "AcDbAttributeDefinition": "Определение атрибута (Attribute Definition)",
        "AcDbAttribute": "Атрибут (Attribute)",

        # Размеры
        "AcDbAlignedDimension": "Выравненный размер (Aligned Dimension)",
        "AcDbRotatedDimension": "Повернутый размер (Rotated Dimension)",
        "AcDbRadialDimension": "Радиальный размер (Radial Dimension)",
        "AcDbDiametricDimension": "Диаметральный размер (Diametric Dimension)",
        "AcDbAngularDimension": "Угловой размер (Angular Dimension)",

        # 3D объекты
        "AcDb3dSolid": "3D Тело (3D Solid)",
        "AcDbRegion": "Регион (Region)",
        "AcDbSurface": "Поверхность (Surface)",
        "AcDb3dFace": "3D Грань (3D Face)",

        # Сетки и другие
        "AcDbWipeout": "Маска (Wipeout)",
        "AcDbRasterImage": "Растровое изображение (Raster Image)",
    }

    # Если тип не найден в словаре, возвращаем оригинальное имя
    return name_map.get(technical_name, technical_name)


if __name__ == "__main__":
    main()