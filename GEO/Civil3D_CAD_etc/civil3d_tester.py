import os
import clr
import ctypes
from pathlib import Path
import sys
from System.Reflection import Assembly

# --- список нужных DLL ---
REQUIRED_DLLS = [
    "acmgd.dll",
    "acdbmgd.dll",
    "AecBaseMgd.dll",
    "AeccDbMgd.dll"
]

# --- поиск DLL ---
def find_dlls(start_dir="C:\\"):
    found = {}
    for root, dirs, files in os.walk(start_dir):
        for dll in REQUIRED_DLLS:
            if dll in files and dll not in found:
                full_path = os.path.join(root, dll)
                found[dll] = full_path
                print(f"[+] Нашёл {dll}: {full_path}")
        if len(found) == len(REQUIRED_DLLS):
            break
    return found

# --- загрузка DLL ---
def load_dlls(dll_map):
    from System.Reflection import Assembly

    # Загружаем в правильном порядке (сначала AutoCAD, потом Civil 3D)
    ac_dlls = ["acmgd.dll", "acdbmgd.dll"]
    civil_dlls = ["AecBaseMgd.dll", "AeccDbMgd.dll"]

    # Сначала загружаем базовые сборки AutoCAD
    for dll in ac_dlls:
        if dll in dll_map:
            try:
                Assembly.LoadFrom(dll_map[dll])
                print(f"[OK] Подключено: {dll}")
            except Exception as e:
                print(f"[ERR] Не удалось подключить {dll}: {e}")

    # Затем загружаем сборки Civil 3D
    for dll in civil_dlls:
        if dll in dll_map:
            try:
                Assembly.LoadFrom(dll_map[dll])
                print(f"[OK] Подключено: {dll}")
            except Exception as e:
                print(f"[ERR] Не удалось подключить {dll}: {e}")

def test_civil_api():
    try:
        from Autodesk.AutoCAD.ApplicationServices import Application
        from Autodesk.Civil.ApplicationServices import CivilApplication

        doc = CivilApplication.ActiveDocument
        if doc:
            print("[+] Civil API доступен. Активный DWG:", doc.Name)
        else:
            print("[-] Civil API подключен, но ActiveDocument = None (нет открытых DWG?)")
    except Exception as e:
        print("[ERR] Ошибка при вызове API:", e)

if __name__ == "__main__":
    print("=== Поиск DLL Civil 3D на диске C: ===")
    dlls = find_dlls("C:\\Program Files\\Autodesk")
    if len(dlls) < len(REQUIRED_DLLS):
        print("[-] Нашёл не все DLL! Проверьте установку Civil3D.")
    else:
        print("[+] Все DLL найдены. Пробую подключить...")
        load_dlls(dlls)
        print("=== Тест API ===")
        test_civil_api()