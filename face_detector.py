import face_recognition
import cv2
import numpy as np
import os
import time
import csv
from datetime import datetime
import pygame

# ---------------- CONFIG ----------------
KNOWN_FACES_DIR = "known_faces"
UNKNOWN_FACES_DIR = "unknown_faces"
ALERT_SOUND = "alert.mp3"
LOG_FILE = "logs.csv"

TOLERANCE = 0.5
SAVE_COOLDOWN = 5
LOG_COOLDOWN = 2
UNKNOWN_GRACE_PERIOD = 1.5
# ---------------------------------------

os.makedirs(UNKNOWN_FACES_DIR, exist_ok=True)

# -------- INIT AUDIO --------
pygame.mixer.init()
alert_sound = pygame.mixer.Sound(ALERT_SOUND)

def play_alert():
    if not pygame.mixer.get_busy():
        alert_sound.play()

# -------- CSV HEADER --------
if not os.path.exists(LOG_FILE):
    with open(LOG_FILE, "w", newline="") as f:
        csv.writer(f).writerow(["timestamp", "name", "confidence"])

# -------- LOAD KNOWN FACES --------
known_face_encodings = []
known_face_names = []

for file in os.listdir(KNOWN_FACES_DIR):
    path = os.path.join(KNOWN_FACES_DIR, file)
    try:
        image = face_recognition.load_image_file(path)
        encodings = face_recognition.face_encodings(image)
        if encodings:
            known_face_encodings.append(encodings[0])
            known_face_names.append(os.path.splitext(file)[0])
    except Exception as e:
        print(f"❌ Skipped {file}: {e}")

print(f"✅ Loaded {len(known_face_names)} known faces")

# -------- CAMERA --------
video = cv2.VideoCapture(0)

last_save_time = 0
last_log_time = 0

unknown_present = False
last_unknown_seen = 0

while True:
    ret, frame = video.read()
    if not ret:
        break

    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    locations = face_recognition.face_locations(rgb)
    encodings = face_recognition.face_encodings(rgb, locations)

    now = time.time()
    unknown_seen_this_frame = False

    for (top, right, bottom, left), encoding in zip(locations, encodings):

        name = "Unknown"
        color = (0, 0, 255)
        confidence = 0

        if known_face_encodings:
            distances = face_recognition.face_distance(
                known_face_encodings, encoding
            )
            best_match = np.argmin(distances)
            distance = distances[best_match]
            confidence = round((1 - distance) * 100, 2)

            if distance < TOLERANCE:
                name = known_face_names[best_match]
                color = (0, 255, 0)

        # ---------- UNKNOWN LOGIC ----------
        if name == "Unknown":
            unknown_seen_this_frame = True
            last_unknown_seen = now

            if not unknown_present:
                play_alert()
                unknown_present = True

            if now - last_save_time > SAVE_COOLDOWN:
                face_img = frame[top:bottom, left:right]
                filename = datetime.now().strftime("%Y%m%d_%H%M%S") + ".jpg"
                cv2.imwrite(os.path.join(UNKNOWN_FACES_DIR, filename), face_img)
                last_save_time = now

        # ---------- LOG ----------
        if now - last_log_time > LOG_COOLDOWN:
            with open(LOG_FILE, "a", newline="") as f:
                csv.writer(f).writerow([
                    datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    name,
                    confidence
                ])
            last_log_time = now

        # ---------- DRAW ----------
        label = f"{name} ({confidence}%)"
        cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
        cv2.putText(
            frame,
            label,
            (left, top - 10),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            color,
            2
        )

    # ---------- RESET UNKNOWN STATE ----------
    if unknown_present and not unknown_seen_this_frame:
        if now - last_unknown_seen > UNKNOWN_GRACE_PERIOD:
            unknown_present = False

    cv2.imshow("Facial Recognition System", frame)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

video.release()
cv2.destroyAllWindows()
pygame.mixer.quit()
