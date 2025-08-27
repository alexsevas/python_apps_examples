# conda activate OCRpy310

import cv2
import pytesseract

# Путь к изображению
img = cv2.imread("D:\\Projects\\Data\\OCR\\m_passport.jpg")

# Предобработка (можно настроить под тип документа)
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
gray = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)[1]

# Распознавание + координаты
data = pytesseract.image_to_data(gray, lang="rus", output_type=pytesseract.Output.DICT)

# Визуализация найденных слов
for i in range(len(data["text"])):
    if int(data["conf"][i]) > 60:  # достоверность
        x, y, w, h = data["left"][i], data["top"][i], data["width"][i], data["height"][i]
        text = data["text"][i]
        cv2.rectangle(img, (x, y), (x+w, y+h), (0, 255, 0), 2)
        cv2.putText(img, text, (x, y - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 1)

cv2.imwrite("document_result.png", img)
print("✅ Готово: документ размечен и сохранён в document_result.png")
