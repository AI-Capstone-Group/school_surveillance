📌 Project Overview

This project is a real-time facial recognition system built using Python.
It uses a webcam to detect faces, recognize known people, and trigger alerts when an unknown person is detected.

The system is designed as a security / monitoring application and demonstrates the practical use of Artificial Intelligence and Computer Vision concepts.

🎯 Key Features

Real-time face detection using webcam

Recognizes known faces (green box)

Detects unknown faces (red box)

Plays an alert sound when an unknown face appears

Saves images of unknown faces automatically

Logs detections (time, name, confidence) to a CSV file

Prevents repeated alerts using smart cooldown logic

🛠️ Technologies Used

Python 3.10

OpenCV (cv2) – for webcam and image processing

face_recognition – for face detection and recognition

NumPy – for numerical calculations

pygame – for playing alert sound

CSV module – for logging data

📂 Folder Structure
AI_project/
│
├── face_detector.py        # Main program
├── alert.mp3               # Alert sound
├── known_faces/             # Images of known people
│   └── person1.jpg
├── unknown_faces/           # Saved unknown face images
├── logs.csv                 # Detection logs
├── README.md                # Project documentation

▶️ How to Run the Program
1️⃣ Install Required Libraries

Run the following command in the terminal:

pip install opencv-python face-recognition numpy pygame

2️⃣ Add Known Faces

Place clear images of known people inside the known_faces folder

Image filename should be the person’s name
Example:

rahul.jpg

3️⃣ Run the Program
python face_detector.py


Press Q to exit the program

🔍 How the System Works (Simple Explanation)

The webcam captures live video frames.

Each frame is converted into a format suitable for face detection.

Faces are detected in the frame.

Each detected face is converted into numerical data (face encoding).

The system compares detected faces with known faces.

If a match is found → green box + name

If no match is found → red box + alert sound

Unknown face images are saved automatically.

All detections are logged with time and confidence.

📊 Confidence Score

The confidence value represents how closely a face matches a known face.

Higher percentage means higher similarity.

A threshold value is used to decide whether a face is known or unknown.

🚨 Alert Logic

The alert sound plays only once when an unknown face enters.

It does not repeat continuously.

The alert resets only after the face leaves the frame.

This prevents noise and false alarms.

🧾 Logging

Each detection is saved in logs.csv with:

Timestamp

Person name (or "Unknown")

Confidence percentage

This allows future review and analysis.

🧠 Educational Purpose

This project demonstrates:

Practical use of AI libraries

Real-time data processing

Logical decision-making using conditions

File handling and logging

Ethical and responsible use of AI

The AI models used are pre-trained, and the focus of the project is on application and logic, not training models from scratch.

🚀 Possible Future Improvements

Face tracking IDs

Mobile notifications

IP camera support

Web dashboard

Auto-enrollment of new faces

Executable (.exe) deployment
