#7/5/2025  use thonny receive script (saved as main.py) must reboot pico with run switch hardware on board
#"F:\python3\python_2025\OCV_hand_finger\multi_finger_7_4_pico_and_python\pico_rcv_finger_states_5led.py"—
import time
time.sleep(2)
import cv2
import mediapipe as mp
import serial

#change from com16 to com 3 for led strip board
pico = serial.Serial('COM3', 115200)  # Adjust as needed
time.sleep(2)

mp_hands = mp.solutions.hands
hands = mp_hands.Hands(min_detection_confidence=0.7)
mp_drawing = mp.solutions.drawing_utils

cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(rgb_frame)

    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

            # Get finger landmarks
            tips = [
                hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP],
                hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP],
                hand_landmarks.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_TIP],
                hand_landmarks.landmark[mp_hands.HandLandmark.RING_FINGER_TIP],
                hand_landmarks.landmark[mp_hands.HandLandmark.PINKY_TIP]
            ]

            mcps = [
                hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_MCP],
                hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_MCP],
                hand_landmarks.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_MCP],
                hand_landmarks.landmark[mp_hands.HandLandmark.RING_FINGER_MCP],
                hand_landmarks.landmark[mp_hands.HandLandmark.PINKY_MCP]
            ]
            finger_states = ''
            for i in range(5):
                try:
                    if i == 0:
                        state = tips[i].x > mcps[i].x
                    else:
                        state = tips[i].y < mcps[i].y
                    finger_states += '1' if state else '0'
                except:
                    finger_states += '0'
            print(f"Finger States: {finger_states}")  # <- print AFTER loop finishes
            time.sleep(0.25)
            pico.write((finger_states + '\n').encode())

    flipped_frame = cv2.flip(frame, 1)
    cv2.imshow('Hand Tracking', flipped_frame)
    #cv2.imshow('Hand Tracking', frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
