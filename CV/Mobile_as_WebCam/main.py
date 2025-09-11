# conda activate cv311

# DroidCam - установить на Windows и на Android

import cv2
import numpy as np

url = "http://192.168.31.18:4747/video"

cap = cv2.VideoCapture(url)
while (True):
    camera, frame = cap.read()
    if frame is not None:
        cv2.imshow('Frame', frame)
    q = cv2.waitKey(1)
    if q==ord('q'):
        break
cv2.destroyAllWindows()