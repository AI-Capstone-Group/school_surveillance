import face_recognition
import cv2
import numpy as np
import os
import time
import csv
import threading
import argparse
import sys
from datetime import datetime
import pygame

CONFIG = {
    "DIRS": {
        "KNOWN": "known_faces",
        "UNKNOWN": "unknown_faces",
        "LOGS": "logs.csv",
        "SOUND": "alert.mp3"
    },
    "AI": {
        "TOLERANCE": 0.45,
        "SCALE": 0.25,
        "MODEL": "hog",
        "CONFIRM_FRAMES": 4,
        "SKIP_FRAMES": 2
    },
    "MOTION": {
        "AREA": 500,
        "SENSITIVITY": 25,
        "BLUR": 21
    },
    "TIMING": {
        "SAVE_CD": 3,
        "LOG_CD": 15,
        "RECONNECT": 2
    }
}

class IOManager:
    def __init__(self):
        self.last_save = 0
        self.last_log = {}
        self.sound_ready = False
        self._setup()

    def _setup(self):
        for d in [CONFIG["DIRS"]["KNOWN"], CONFIG["DIRS"]["UNKNOWN"]]:
            os.makedirs(d, exist_ok=True)
        
        if not os.path.exists(CONFIG["DIRS"]["LOGS"]):
            with open(CONFIG["DIRS"]["LOGS"], "w", newline="") as f:
                csv.writer(f).writerow(["Timestamp", "Source", "Data", "Type"])

        pygame.mixer.init()
        if os.path.exists(CONFIG["DIRS"]["SOUND"]):
            try:
                self.sound = pygame.mixer.Sound(CONFIG["DIRS"]["SOUND"])
                self.sound_ready = True
            except: pass

    def save_snapshot(self, frame):
        if time.time() - self.last_save > CONFIG["TIMING"]["SAVE_CD"]:
            self.last_save = time.time()
            threading.Thread(target=self._write_img, args=(frame.copy(),)).start()

    def _write_img(self, img):
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        path = os.path.join(CONFIG["DIRS"]["UNKNOWN"], f"{ts}.jpg")
        cv2.imwrite(path, img)

    def log_event(self, name, data, kind):
        if time.time() - self.last_log.get(name, 0) > CONFIG["TIMING"]["LOG_CD"]:
            self.last_log[name] = time.time()
            threading.Thread(target=self._write_csv, args=(name, data, kind)).start()

    def _write_csv(self, name, data, kind):
        with open(CONFIG["DIRS"]["LOGS"], "a", newline="") as f:
            csv.writer(f).writerow([
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                name, data, kind
            ])

    def trigger_alarm(self):
        if self.sound_ready and not pygame.mixer.get_busy():
            threading.Thread(target=self.sound.play).start()

class FaceSystem:
    def __init__(self):
        self.encodings = []
        self.names = []
        self.load_data()

    def load_data(self):
        print("[SYSTEM] Loading biometrics...")
        for f in os.listdir(CONFIG["DIRS"]["KNOWN"]):
            if f.lower().endswith(('.jpg', '.png', '.jpeg')):
                try:
                    path = os.path.join(CONFIG["DIRS"]["KNOWN"], f)
                    img = face_recognition.load_image_file(path)
                    enc = face_recognition.face_encodings(img)
                    if enc:
                        self.encodings.append(enc[0])
                        self.names.append(os.path.splitext(f)[0])
                except: continue
        print(f"[SYSTEM] Database loaded: {len(self.names)} identities.")

    def identify(self, frame):
        small = cv2.resize(frame, (0, 0), fx=CONFIG["AI"]["SCALE"], fy=CONFIG["AI"]["SCALE"])
        rgb = cv2.cvtColor(small, cv2.COLOR_BGR2RGB)
        
        locs = face_recognition.face_locations(rgb, model=CONFIG["AI"]["MODEL"])
        encs = face_recognition.face_encodings(rgb, locs)
        
        results = []
        for loc, enc in zip(locs, encs):
            name = "Unknown"
            conf = 0.0
            if self.encodings:
                dists = face_recognition.face_distance(self.encodings, enc)
                best = np.argmin(dists)
                if dists[best] < CONFIG["AI"]["TOLERANCE"]:
                    name = self.names[best]
                    conf = round((1 - dists[best]) * 100, 1)
            results.append((loc, name, conf))
        return results

class SecurityApp:
    def __init__(self, source):
        self.source = source
        self.io = IOManager()
        self.fs = FaceSystem()
        
        self.prev_frame = None
        self.unknown_streak = 0
        self.alert_mode = False
        self.frame_idx = 0
        
        self.locs = []
        self.names = []
        self.confs = []

    def _draw_brackets(self, frame, l, t, r, b, color, length=20, thick=2):
        cv2.line(frame, (l, t), (l + length, t), color, thick)
        cv2.line(frame, (l, t), (l, t + length), color, thick)
        cv2.line(frame, (r, t), (r - length, t), color, thick)
        cv2.line(frame, (r, t), (r, t + length), color, thick)
        cv2.line(frame, (l, b), (l + length, b), color, thick)
        cv2.line(frame, (l, b), (l, b - length), color, thick)
        cv2.line(frame, (r, b), (r - length, b), color, thick)
        cv2.line(frame, (r, b), (r, b - length), color, thick)

    def _draw_hud(self, frame, fps):
        h, w = frame.shape[:2]
        
        cv2.rectangle(frame, (0, 0), (w, 50), (10, 10, 10), -1)
        cv2.line(frame, (0, 50), (w, 50), (50, 50, 50), 1)

        ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cv2.putText(frame, f"CAM_01 | {ts}", (20, 32), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200, 200, 200), 1)
        cv2.putText(frame, f"{fps} FPS", (w - 100, 32), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (100, 255, 100), 1)

        if self.alert_mode:
            if int(time.time() * 4) % 2 == 0:
                cv2.rectangle(frame, (0, 0), (w, h), (0, 0, 255), 10)
                cv2.putText(frame, "UNAUTHORIZED ACCESS", (w//2 - 180, 85), cv2.FONT_HERSHEY_DUPLEX, 1.0, (0, 0, 255), 2)

    def process_motion(self, frame):
        small = cv2.resize(frame, (0, 0), fx=CONFIG["AI"]["SCALE"], fy=CONFIG["AI"]["SCALE"])
        gray = cv2.GaussianBlur(cv2.cvtColor(small, cv2.COLOR_BGR2GRAY), (CONFIG["MOTION"]["BLUR"], CONFIG["MOTION"]["BLUR"]), 0)
        
        if self.prev_frame is None:
            self.prev_frame = gray
            return True
            
        diff = cv2.absdiff(self.prev_frame, gray)
        thresh = cv2.threshold(diff, CONFIG["MOTION"]["SENSITIVITY"], 255, cv2.THRESH_BINARY)[1]
        self.prev_frame = gray
        
        return np.sum(thresh) > CONFIG["MOTION"]["AREA"]

    def run(self):
        cap = cv2.VideoCapture(self.source)
        
        while True:
            if not cap.isOpened() or not cap.read()[0]:
                print(f"[ERROR] Camera lost. Retrying in {CONFIG['TIMING']['RECONNECT']}s...")
                time.sleep(CONFIG['TIMING']['RECONNECT'])
                cap = cv2.VideoCapture(self.source)
                continue

            start = time.time()
            ret, frame = cap.read()
            if not ret: continue

            if self.frame_idx % CONFIG["AI"]["SKIP_FRAMES"] == 0:
                if self.process_motion(frame):
                    results = self.fs.identify(frame)
                    
                    self.locs = [x[0] for x in results]
                    self.names = [x[1] for x in results]
                    self.confs = [x[2] for x in results]
                    
                    unknown_present = "Unknown" in self.names
                    
                    if unknown_present:
                        self.unknown_streak += 1
                    else:
                        self.unknown_streak = 0
                        self.alert_mode = False

                    if self.unknown_streak >= CONFIG["AI"]["CONFIRM_FRAMES"]:
                        self.alert_mode = True
                        self.io.trigger_alarm()
                        self.io.save_snapshot(frame)
                        self.io.log_event("Unknown", "N/A", "ALERT")
                    
                    for n, c in zip(self.names, self.confs):
                        if n != "Unknown":
                            self.io.log_event(n, f"{c}%", "ENTRY")
                else:
                    self.locs, self.names, self.confs = [], [], []
                    self.alert_mode = False

            scale = int(1 / CONFIG["AI"]["SCALE"])
            for (t, r, b, l), name, conf in zip(self.locs, self.names, self.confs):
                t, r, b, l = t*scale, r*scale, b*scale, l*scale
                color = (0, 0, 255) if name == "Unknown" else (0, 255, 0)
                
                self._draw_brackets(frame, l, t, r, b, color)
                
                label = name if name == "Unknown" else f"{name} [{conf}%]"
                cv2.putText(frame, label, (l + 5, b - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)

            self.frame_idx += 1
            fps = int(1 / (time.time() - start))
            self._draw_hud(frame, fps)
            
            cv2.imshow("Sentinet v3.0", frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        cap.release()
        cv2.destroyAllWindows()
        pygame.mixer.quit()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", default=0, help="Camera Index or URL")
    args = parser.parse_args()
    
    src = int(args.source) if str(args.source).isdigit() else args.source
    
    try:
        app = SecurityApp(src)
        app.run()
    except KeyboardInterrupt:
        sys.exit()
