# Этот код демонстрирует работу с изображениями с помощью OpenCV: загрузка, преобразование в градации серого и обнаружение границ.
# Эти операции полезны для задач компьютерного зрения, таких как распознавание объектов или улучшение изображений для анализа.
#
# pip install opencv-python-headless


import cv2
import numpy as np

def apply_grayscale_and_edges(image_path: str):
    # Загрузка изображения
    image = cv2.imread(image_path)
    if image is None:
        raise FileNotFoundError(f"Не удалось загрузить изображение: {image_path}")

    # Преобразование в градации серого
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Обнаружение границ с помощью Canny
    edges = cv2.Canny(gray_image, 100, 200)

    # Отображение результатов
    cv2.imshow("Grayscale", gray_image)
    cv2.imshow("Edges", edges)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

# Пример использования
image_path = "example.jpg"
try:
    apply_grayscale_and_edges(image_path)
except FileNotFoundError as e:
    print(e)