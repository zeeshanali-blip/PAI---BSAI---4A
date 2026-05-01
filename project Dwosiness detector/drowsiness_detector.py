import os
import cv2

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FACE_CASCADE_PATH = os.path.join(BASE_DIR, 'haarcascade_frontalface_default.xml')
EYE_CASCADE_PATH = os.path.join(BASE_DIR, 'haarcascade_eye.xml')

if not os.path.exists(FACE_CASCADE_PATH):
    raise FileNotFoundError(f"Face cascade file not found: {FACE_CASCADE_PATH}")

if not os.path.exists(EYE_CASCADE_PATH):
    raise FileNotFoundError(f"Eye cascade file not found: {EYE_CASCADE_PATH}")

face_cascade = cv2.CascadeClassifier(FACE_CASCADE_PATH)
eye_cascade = cv2.CascadeClassifier(EYE_CASCADE_PATH)

if face_cascade.empty() or eye_cascade.empty():
    raise RuntimeError('Failed to load Haar cascade classifiers. Check the XML files.')

cap = cv2.VideoCapture(0)
if not cap.isOpened():
    raise RuntimeError('Unable to open the webcam. Check your camera and try again.')

while True:
    ret, frame = cap.read()
    if not ret:
        print('Failed to read from camera.')
        break

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.3, minNeighbors=5)

    for (x, y, w, h) in faces:
        cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)
        roi_gray = gray[y:y + h, x:x + w]
        roi_color = frame[y:y + h, x:x + w]
        eyes = eye_cascade.detectMultiScale(roi_gray)

        for (ex, ey, ew, eh) in eyes:
            cv2.rectangle(roi_color, (ex, ey), (ex + ew, ey + eh), (0, 255, 0), 2)

    cv2.imshow('Drowsiness Detection - Basic', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
