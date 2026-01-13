# pip install Pillow

# Код для удаления метаданных изображения на Python (для удаления метаданных изображения используется библиотека Pillow)

from PIL import Image


# Функция для удаления метаданных из указанного изображения.
def clear_all_metadata(img_name):
    # Открываем файл изображения.
    img = Image.open(img_name)

    # Читаем данные изображения, исключая метаданные.
    data = list(img.getdata())

    # Создаем новое изображение с тем же режимом и размером, но без метаданных.
    img_without_metadata = Image.new(img.mode, img.size)
    img_without_metadata.putdata(data)

    # Сохраняем новое изображение поверх исходного файла, удаляя метаданные.
    img_without_metadata.save(img_name)

    print(f"Метаданные успешно удалены из '{img_name}'.")


clear_all_metadata("image.jpg")
