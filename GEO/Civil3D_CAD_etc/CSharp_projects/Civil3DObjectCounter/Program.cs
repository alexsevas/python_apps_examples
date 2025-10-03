using System;
using System.Collections.Generic;
using Autodesk.AutoCAD.ApplicationServices;
using Autodesk.AutoCAD.DatabaseServices;
using Autodesk.AutoCAD.EditorInput;
using Autodesk.AutoCAD.Runtime;
using Autodesk.Civil.DatabaseServices;

namespace Civil3DObjectCounter
{
    class Program
    {
        [STAThread]
        static void Main(string[] args)
        {
            Console.WriteLine("=== Анализ объектов в чертеже Civil 3D ===\n");

            try
            {
                // Получаем активное приложение AutoCAD/Civil 3D
                var app = Application.AcadApplication;
                if (app == null)
                {
                    Console.WriteLine("[ERR] AutoCAD/Civil 3D не запущен.");
                    return;
                }

                Console.WriteLine($"[OK] Подключено к: {app.Caption}");

                // Получаем активный документ
                var doc = Application.DocumentManager.MdiActiveDocument;
                if (doc == null)
                {
                    Console.WriteLine("[ERR] Нет активного документа.");
                    return;
                }

                Console.WriteLine($"[OK] Анализ чертежа: {doc.Name}\n");

                var objectCounts = new Dictionary<string, int>();
                var db = doc.Database;

                // Начинаем транзакцию для чтения базы данных
                using (var tr = db.TransactionManager.StartTransaction())
                {
                    // Получаем таблицу блоков и запись пространства модели
                    var bt = tr.GetObject(db.BlockTableId, OpenMode.ForRead) as BlockTable;
                    var ms = tr.GetObject(bt[BlockTableRecord.ModelSpace], OpenMode.ForRead) as BlockTableRecord;

                    Console.WriteLine("Анализ объектов. Это может занять некоторое время...\n");

                    // Перебираем все ObjectId в пространстве модели
                    foreach (ObjectId objId in ms)
                    {
                        try
                        {
                            // Открываем объект для чтения
                            var entity = tr.GetObject(objId, OpenMode.ForRead);

                            string objectType = "Неизвестный объект";

                            // --- Классификация объектов Civil 3D ---
                            if (entity is TinSurface)
                                objectType = "Civil 3D: Поверхность TIN";
                            else if (entity is GridSurface)
                                objectType = "Civil 3D: Поверхность Grid";
                            else if (entity is Alignment)
                                objectType = "Civil 3D: Трасса (Alignment)";
                            else if (entity is Profile)
                                objectType = "Civil 3D: Профиль (Profile)";
                            else if (entity is Corridor)
                                objectType = "Civil 3D: Коридор (Corridor)";
                            else if (entity is PipeNetwork)
                                objectType = "Civil 3D: Сеть трубопроводов (PipeNetwork)";
                            else if (entity is Parcel)
                                objectType = "Civil 3D: Земельный участок (Parcel)";
                            else if (entity is ViewFrameGroup)
                                objectType = "Civil 3D: Группа рамок разрезов (ViewFrameGroup)";
                            // --- Классификация базовых объектов AutoCAD ---
                            else if (entity is Line)
                                objectType = "AutoCAD: Линия (Line)";
                            else if (entity is Polyline)
                                objectType = "AutoCAD: 2D Полилиния (LWPolyline)";
                            else if (entity is Polyline3d)
                                objectType = "AutoCAD: 3D Полилиния (3DPoly)";
                            else if (entity is DBPoint)
                                objectType = "AutoCAD: Точка (Point)";
                            else if (entity is DBText)
                                objectType = "AutoCAD: Текст (Text)";
                            else if (entity is MText)
                                objectType = "AutoCAD: Многострочный текст (MText)";
                            else if (entity is Circle)
                                objectType = "AutoCAD: Окружность (Circle)";
                            else if (entity is BlockReference)
                                objectType = "AutoCAD: Вставка блока (Block Reference)";
                            else
                                objectType = $"AutoCAD: {entity.GetType().Name}";

                            // Увеличиваем счетчик
                            if (objectCounts.ContainsKey(objectType))
                                objectCounts[objectType]++;
                            else
                                objectCounts[objectType] = 1;

                        }
                        catch (Exception ex)
                        {
                            // Пропускаем объекты, которые не удалось прочитать
                            var errorKey = "Ошибки при чтении объектов";
                            if (objectCounts.ContainsKey(errorKey))
                                objectCounts[errorKey]++;
                            else
                                objectCounts[errorKey] = 1;
                        }
                    }

                    tr.Commit();
                }

                // Вывод результатов
                if (objectCounts.Count > 0)
                {
                    Console.WriteLine("Статистика по типам объектов:");
                    Console.WriteLine(new string('-', 50));
                    // Сортируем по количеству (можно использовать LINQ, но для простоты оставим как есть)
                    foreach (var kvp in objectCounts)
                    {
                        Console.WriteLine($"{kvp.Value,6} | {kvp.Key}");
                    }
                    Console.WriteLine(new string('-', 50));
                }
                else
                {
                    Console.WriteLine("Не найдено объектов для анализа.");
                }

            }
            catch (System.Exception ex)
            {
                Console.WriteLine($"[FATAL ERROR] {ex.Message}");
                Console.WriteLine(ex.StackTrace);
            }

            Console.WriteLine("\nНажмите любую клавишу для выхода...");
            Console.ReadKey();
        }
    }
}