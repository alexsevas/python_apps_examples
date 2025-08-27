# activate allpy310_2 (тут установлена mediapipe)

# Интерактивная система для распознания жестов через веб-камеру

import cv2
import mediapipe as mp
import pyautogui

mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils

cap = cv2.VideoCapture(0)

with mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.7) as hands:
    while cap.isOpened():
        success, frame = cap.read()
        if not success:
            break

        # Отзеркаливаем изображение и конвертируем
        frame = cv2.flip(frame, 1)
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        result = hands.process(rgb)

        if result.multi_hand_landmarks:
            for hand_landmarks in result.multi_hand_landmarks:
                mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

                # Пример: "палец вверх" — большой палец вытянут, остальные согнуты
                thumb = hand_landmarks.landmark[4].y < hand_landmarks.landmark[3].y
                index = hand_landmarks.landmark[8].y < hand_landmarks.landmark[6].y
                middle = hand_landmarks.landmark[12].y < hand_landmarks.landmark[10].y
                ring = hand_landmarks.landmark[16].y < hand_landmarks.landmark[14].y
                pinky = hand_landmarks.landmark[20].y < hand_landmarks.landmark[18].y

                if thumb and not index and not middle and not ring and not pinky:
                    cv2.putText(frame, "Finger UP!", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                    # Пример действия: нажать play/pause
                    pyautogui.press("playpause")

        cv2.imshow("Gestures hands", frame)
        if cv2.waitKey(5) & 0xFF == 27:  # ESC
            break

cap.release()
cv2.destroyAllWindows()
