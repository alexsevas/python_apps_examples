# conda activate allpy311
# pip install pywin32

# Программа, которая использует pywin32 для подключения к запущенному AutoCAD/Civil 3D и анализирует открытый чертеж.
# Она подсчитывает общее количество объектов в пространстве модели и затем выводит детальную статистику по каждому типу графических примитивов

import win32com.client
import pythoncom


def main():
    print("\n==================================================")
    print("=== Анализ объектов в чертеже AutoCAD/Civil 3D ===")
    print("==================================================")

    try:
        pythoncom.CoInitialize()
        acad = win32com.client.GetActiveObject("AutoCAD.Application")
        doc = acad.ActiveDocument
        mspace = doc.ModelSpace

        print(f"[OK] Подключено к: {acad.Caption}")
        print(f"[OK] Анализ чертежа: {doc.Name}\n")

        object_counts = {}
        total_count = mspace.Count
        print(f"Общее количество объектов в пространстве модели: {total_count}\n")

        if total_count == 0:
            print("Пространство модели пусто.")
            return

        # Счетчики для эвристики Civil 3D
        civil_hints = {
            "Возможные поверхности (по горизонталям)": 0,
            "Возможные трассы (по полилиниям)": 0,
            "Возможные сети (по точкам/линиям)": 0,
        }

        print("Подсчет объектов по типам...")
        for i in range(total_count):
            try:
                obj = mspace.Item(i)
                obj_name = obj.ObjectName
                layer_name = obj.Layer.upper() if hasattr(obj, 'Layer') else ""

                # --- 1. Попытка классифицировать как объект Civil 3D ---
                if obj_name.startswith("AeccDb"):
                    readable_name = convert_civil_object_name(obj_name)
                    object_counts[readable_name] = object_counts.get(readable_name, 0) + 1
                    continue

                # --- 2. Классификация как базовый объект AutoCAD ---
                readable_name = convert_autocad_object_name(obj_name)
                object_counts[readable_name] = object_counts.get(readable_name, 0) + 1

                # --- 3. Эвристика для обнаружения Civil 3D по графическим примитивам ---
                # Проверяем, может ли объект быть частью Civil 3D объекта
                if readable_name == "2D Полилиния (LWPolyline)":
                    if any(kw in layer_name for kw in ["CONTOUR", "ГОРИЗОНТ", "SURF"]):
                        civil_hints["Возможные поверхности (по горизонталям)"] += 1
                    elif any(kw in layer_name for kw in ["ALIGNMENT", "ТРАССА", "ROAD"]):
                        civil_hints["Возможные трассы (по полилиниям)"] += 1
                    elif any(kw in layer_name for kw in ["PIPE", "СЕТЬ", "NETWORK"]):
                        civil_hints["Возможные сети (по точкам/линиям)"] += 1

                elif readable_name == "Точка (Point)":
                    if any(kw in layer_name for kw in ["PIPE", "СЕТЬ", "STRUCTURE"]):
                        civil_hints["Возможные сети (по точкам/линиям)"] += 1

            except Exception as e:
                unknown_key = "Неизвестные/недоступные объекты"
                object_counts[unknown_key] = object_counts.get(unknown_key, 0) + 1
                continue

        # --- Вывод результатов ---
        if object_counts:
            print("Статистика по типам объектов:")
            print("-" * 55)
            for obj_type, count in sorted(object_counts.items(), key=lambda x: x[1], reverse=True):
                print(f"{count:6d} | {obj_type}")
            print("-" * 55)

        # --- Вывод подсказок по Civil 3D ---
        civil_detected = any(count > 0 for count in civil_hints.values())
        if civil_detected:
            print("\n[Эвристика Civil 3D] Обнаружены признаки следующих объектов:")
            print("-" * 55)
            for hint, count in civil_hints.items():
                if count > 0:
                    print(f"{count:6d} | {hint}")
            print("-" * 55)
            print("Примечание: Это косвенные признаки на основе слоев и графики.")
            print("Для точного анализа используйте API изнутри Civil 3D.")

    except Exception as e:
        print(f"[ERR] Ошибка: {e}")
        print("Убедитесь, что AutoCAD/Civil 3D запущен и открыт чертеж!")
    finally:
        pythoncom.CoUninitialize()


def convert_civil_object_name(technical_name):
    """Преобразует технические имена объектов Civil 3D в понятные пользователю названия."""
    civil_map = {
        # === Поверхности (Surfaces) ===
        "AeccDbSurfaceTin": "Civil 3D: Поверхность TIN (AeccDbSurfaceTin)",
        "AeccDbSurfaceGrid": "Civil 3D: Поверхность Grid (AeccDbSurfaceGrid)",

        # === Трассы (Alignments) ===
        "AeccDbAlignment": "Civil 3D: Горизонтальная трасса (AeccDbAlignment)",
        "AeccDbAlignmentStationLabeling": "Civil 3D: Маркировка пикетов (основные) (AeccDbAlignmentStationLabeling)",
        "AeccDbAlignmentMinorStationLabeling": "Civil 3D: Маркировка пикетов (дополнительные) (AeccDbAlignmentMinorStationLabeling)",

        # === Вертикальные трассы и профили (Vertical Alignments & Profiles) ===
        "AeccDbVAlignment": "Civil 3D: Вертикальная трасса (AeccDbVAlignment)",
        "AeccDbVAlignmentLineLabeling": "Civil 3D: Маркировка прямых участков (верт. трасса) (AeccDbVAlignmentLineLabeling)",
        "AeccDbVAlignmentPVILabeling": "Civil 3D: Маркировка точек перелома (PVI) (AeccDbVAlignmentPVILabeling)",
        "AeccDbVAlignmentSagCurveLabeling": "Civil 3D: Маркировка вогнутых кривых (AeccDbVAlignmentSagCurveLabeling)",
        "AeccDbVAlignmentCrestCurveLabeling": "Civil 3D: Маркировка выпуклых кривых (AeccDbVAlignmentCrestCurveLabeling)",
        "AeccDbGraphProfile": "Civil 3D: График профиля (например, уклонов, кривизны) (AeccDbGraphProfile)",

        # === Профили (Profiles) ===
        "AeccDbProfile": "Civil 3D: Продольный профиль (AeccDbProfile)",
        "AeccDbProfileDataBandLabeling": "Civil 3D: Маркировка в табличной части профиля (AeccDbProfileDataBandLabeling)",

        # === Коридоры и сборки (Corridors & Assemblies) ===
        "AeccDbCorridor": "Civil 3D: Коридор (AeccDbCorridor)",
        "AeccDbAssembly": "Civil 3D: Сборка (AeccDbAssembly)",
        "AeccDbSubassembly": "Civil 3D: Подсборка (AeccDbSubassembly)",

        # === Сети (Pipe Networks) ===
        "AeccDbPipeNetwork": "Civil 3D: Сеть трубопроводов (AeccDbPipeNetwork)",
        "AeccDbPipe": "Civil 3D: Труба (AeccDbPipe)",
        "AeccDbStructure": "Civil 3D: Колодец / Камера (AeccDbStructure)",
        "AeccDbPart": "Civil 3D: Элемент сети (AeccDbPart)",

        # === Землеустройство (Parcels) ===
        "AeccDbParcel": "Civil 3D: Земельный участок (AeccDbParcel)",
        "AeccDbParcelSegment": "Civil 3D: Сегмент границы участка (AeccDbParcelSegment)",

        # === Разрезы (Sections) ===
        "AeccDbSectionView": "Civil 3D: Вид разреза (AeccDbSectionView)",
        "AeccDbSampleLine": "Civil 3D: Линия разреза (AeccDbSampleLine)",
        "AeccDbViewFrameGroup": "Civil 3D: Группа рамок разрезов (AeccDbViewFrameGroup)",

        # === Общие и вспомогательные объекты ===
        "AeccDbGeneralNote": "Civil 3D: Общая заметка (AeccDbGeneralNote)",
        "AeccDbLabelStyle": "Civil 3D: Стиль маркировки (AeccDbLabelStyle)",
        "AeccDbTable": "Civil 3D: Таблица (например, ведомость) (AeccDbTable)",
        "AeccDbGradingGroup": "Civil 3D: Группа проектирования земляных масс (AeccDbGradingGroup)",
        "AeccDbGradingCriteria": "Civil 3D: Критерии проектирования (AeccDbGradingCriteria)",

        # === Динамические блоки и аннотации ===
        "AeccDbAlignmentEntityLabel": "Civil 3D: Маркировка элемента трассы (AeccDbAlignmentEntityLabel)",
        "AeccDbProfileViewLabel": "Civil 3D: Маркировка в виде профиля (AeccDbProfileViewLabel)",
    }

    # Если тип не найден в словаре, возвращаем обобщенное название с техническим именем
    return civil_map.get(technical_name, f"Civil 3D: Неизвестный объект ({technical_name})")


def convert_autocad_object_name(technical_name):
    """Преобразует имена базовых объектов AutoCAD."""
    name_map = {
        "AcDbLine": "Линия (Line)",
        "AcDbPolyline": "2D Полилиния (LWPolyline)",
        "AcDb3dPolyline": "3D Полилиния (3DPoly)",
        "AcDbCircle": "Окружность (Circle)",
        "AcDbArc": "Дуга (Arc)",
        "AcDbText": "Текст (Text)",
        "AcDbMText": "Многострочный текст (MText)",
        "AcDbPoint": "Точка (Point)",
        "AcDbHatch": "Штриховка (Hatch)",
        "AcDbBlockReference": "Вставка блока (Block Reference)",
        "AcDb3dSolid": "3D Тело (3D Solid)",
        "AcDbRasterImage": "Растровое изображение (Raster Image)",
    }
    return name_map.get(technical_name, technical_name)


if __name__ == "__main__":
    main()