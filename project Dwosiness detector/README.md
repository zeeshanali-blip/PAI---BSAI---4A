# Drowsiness Detection System using OpenCV and Flask

This project is a simple AI-based drowsiness detection system built with Python, OpenCV, and Flask. It uses Haarcascade classifiers to detect faces and eyes from a webcam feed and displays a live video stream in the browser.

## Folder Structure

```text
project Dwosiness detector/
├── app.py
├── requirements.txt
├── README.md
├── haarcascade_frontalface_default.xml
├── haarcascade_eye.xml
└── templates/
    └── index.html
```

## Files

- `app.py`: Main Flask application and webcam video processing logic.
- `requirements.txt`: Required Python libraries.
- `README.md`: Project instructions.
- `haarcascade_frontalface_default.xml`: Haarcascade file for face detection.
- `haarcascade_eye.xml`: Haarcascade file for eye detection.
- `templates/index.html`: Frontend page to show live video feed.

## How it Works

1. `app.py` starts a Flask web server.
2. The webcam captures frames in real time.
3. Haarcascade classifiers detect faces and eyes in each frame.
4. If the system does not detect eyes for a set number of consecutive frames, it marks the status as `Drowsy`.
5. The video stream is sent to the web page using `multipart/x-mixed-replace`.

## Run the Project

1. Open a terminal in the project folder.
1. Activate your virtual environment if you have one:

```powershell
.venv\Scripts\Activate.ps1
```

1. Install dependencies:

```powershell
pip install -r requirements.txt
```

1. Run the app:

```powershell
python app.py
```

1. Open your browser and go to:

```text
http://127.0.0.1:5000
```

1. Click `Start Camera` on the page to begin the live feed.

## Common Fixes

- `ModuleNotFoundError: No module named 'cv2'`: Install OpenCV with `pip install opencv-python`.
- `Could not open webcam`: Make sure no other app is using the camera and the camera is connected.
- `Failed to load Haarcascade XML files`: Verify the XML files are in the project root and the names are correct.
- `Permission denied` on Windows: Run PowerShell as administrator or use `Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned`.

## Notes

- This project is beginner-friendly and suitable for a university AI assignment.
- The system uses a simple frame counter to detect drowsiness, which is a good starting point for further improvement.
- You can extend it by adding sound alerts, logging, or saving snapshots when drowsiness is detected.
