# conda activate allpy311, allpy310
# pip install requests

'''
Код для обновления обоев рабочего стола Windows на Python
Данный скрипт загружает случайное изображение и устанавливает его в качестве обоев рабочего стола.
Для получения случайных изображений в коде используется библиотека requests.
'''

from pathlib import Path
import requests
import ctypes
import tempfile


def set_random_wallpaper():
    url = "https://picsum.photos/1920/1080"  # Ссылка на случайное изображение
    wallpaper_path = Path(tempfile.gettempdir()) / "wallpaper.jpg"  # Путь к временной папке для сохранения изображения

    # Отправляем GET-запрос с потоковой загрузкой (stream=True) для экономии памяти
    response = requests.get(url, stream=True)
    # Проверяем, что запрос выполнен успешно (код 200)
    response.raise_for_status()

    # Открываем файл для записи в бинарном режиме
    with wallpaper_path.open("wb") as file:
        # Загружаем файл частями по 8192 байта
        for chunk in response.iter_content(8192):
            file.write(chunk)

    # Устанавливаем загруженное изображение в качестве обоев рабочего стола
    ctypes.windll.user32.SystemParametersInfoW(20, 0, str(wallpaper_path), 0)
    # Выводим сообщение об успешном обновлении
    print("Обои рабочего стола обновлены!")


if __name__ == "__main__":
    set_random_wallpaper()
