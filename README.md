# 🛡️ Real-Time Facial Recognition Security System

A robust Python-based security application that utilizes computer vision to identify known individuals and trigger automated alerts for unauthorized faces.

---

## 📌 Project Overview
This system leverages a live webcam feed to perform face detection and recognition in real-time. Designed as a monitoring tool, it demonstrates the practical integration of **Artificial Intelligence** and **Computer Vision** to solve real-world security challenges.

## 🎯 Key Features
* **Real-Time Detection:** Low-latency face processing using standard webcams.
* **Visual Feedback:** Dynamic bounding boxes (Green for recognized, Red for unknown).
* **Instant Alerts:** Automated audio alarms via `pygame` when an intruder is detected.
* **Smart Cooldown:** Logic-based alert system to prevent repetitive noise while a face is in frame.
* **Auto-Archiving:** Automatically saves snapshots of unknown faces to a dedicated folder.
* **Detailed Logging:** Records timestamps, names, and confidence scores to a `CSV` file for auditing.

---

## 🛠️ Technologies Used
| Category | Technology |
| :--- | :--- |
| **Language** | Python 3.10 |
| **Computer Vision** | OpenCV (cv2), face_recognition |
| **Data Handling** | NumPy, CSV Module |
| **Audio/UI** | Pygame |

---

## 📂 Folder Structure
```text
AI_project/
│
├── face_detector.py        # Main execution script
├── alert.mp3               # Alert sound file
├── known_faces/            # Database for authorized personnel images
│   └── person1.jpg         # Example: rahul.jpg
├── unknown_faces/          # Directory for captured intruder snapshots
├── logs.csv                # Automated detection logs
└── README.md               # Project documentation
```

---

## ▶️ Getting Started

### 1️⃣ Install Required Libraries
Ensure you have Python 3.10+ installed, then run:
```bash
pip install opencv-python face-recognition numpy pygame
```

### 2️⃣ Configure Known Faces
Add high-quality images of authorized people to the `known_faces/` directory.
> **Note:** The filename will be used as the person's name in the system (e.g., `john_doe.jpg` will appear as "John Doe").

### 3️⃣ Run the Application
```bash
python face_detector.py
```
* **To Exit:** Press `Q` on your keyboard.

---

## 🔍 How It Works
1.  **Frame Capture:** The system pulls live video frames from the webcam.
2.  **Encoding:** Detected faces are converted into a 128-dimension vector (Face Encoding).
3.  **Comparison:** The system calculates the Euclidean distance between the live encoding and the stored encodings.
4.  **Thresholding:**
    * If the distance is within the threshold: **Authorized Access** (Green Box).
    * If the distance exceeds the threshold: **Intruder Alert** (Red Box + Alarm).
5.  **Logging:** Data is appended to `logs.csv` using the following format:
    `[Timestamp, Name/Unknown, Confidence %]`

---

## 🚀 Future Roadmap
* [ ] **Mobile Integration:** Send push notifications via Telegram or WhatsApp.
* [ ] **Cloud Support:** Sync captured images to an AWS S3 bucket.
* [ ] **Web Dashboard:** A Flask/Streamlit interface to view logs and live feeds remotely.
* [ ] **ID Tracking:** Assign unique IDs to unknown faces to track movement history.

---

## 🧠 Educational Purpose
This project was developed to explore the intersection of AI and security. It highlights the use of **pre-trained deep learning models** and the implementation of practical logic, such as debouncing alerts and file I/O management.
