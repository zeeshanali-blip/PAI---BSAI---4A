import os
import cv2
from flask import Flask, Response, render_template, jsonify
import logging

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Paths for Haarcascade XML files in the project folder
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FACE_CASCADE_PATH = os.path.join(BASE_DIR, 'haarcascade_frontalface_default.xml')
EYE_CASCADE_PATH = os.path.join(BASE_DIR, 'haarcascade_eye.xml')

# Load Haarcascade classifiers
face_cascade = cv2.CascadeClassifier(FACE_CASCADE_PATH)
eye_cascade = cv2.CascadeClassifier(EYE_CASCADE_PATH)

if face_cascade.empty() or eye_cascade.empty():
    logger.error('Failed to load Haarcascade XML files. Check the file names and paths.')

class VideoCamera:
    def __init__(self):
        self.cap = None
        self.closed_eye_frames = 0
        self.drowsy_threshold = 15
        self.camera_initialized = False
        self.error_message = None
        self._init_camera()

    def _init_camera(self):
        """Initialize camera with error handling."""
        try:
            self.cap = cv2.VideoCapture(0)
            if not self.cap.isOpened():
                self.error_message = 'Camera not available. Please check your webcam connection.'
                logger.error(self.error_message)
                return False
            self.camera_initialized = True
            logger.info('Camera initialized successfully')
            return True
        except Exception as e:
            self.error_message = f'Error initializing camera: {str(e)}'
            logger.error(self.error_message)
            return False

    def __del__(self):
        if self.cap and self.cap.isOpened():
            self.cap.release()

    def get_frame(self):
        if not self.camera_initialized or self.cap is None:
            return None

        try:
            success, frame = self.cap.read()
            if not success:
                return None

            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(100, 100))

            status_text = 'Awake'
            alert_text = ''
            face_detected = len(faces) > 0

            for (x, y, w, h) in faces:
                cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)
                roi_gray = gray[y:y + h, x:x + w]
                roi_color = frame[y:y + h, x:x + w]

                eyes = eye_cascade.detectMultiScale(roi_gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
                if len(eyes) == 0:
                    self.closed_eye_frames += 1
                else:
                    self.closed_eye_frames = 0

                for (ex, ey, ew, eh) in eyes:
                    cv2.rectangle(roi_color, (ex, ey), (ex + ew, ey + eh), (0, 255, 0), 2)

            if not face_detected:
                self.closed_eye_frames = 0
                status_text = 'No Face Detected'

            if self.closed_eye_frames >= self.drowsy_threshold:
                status_text = 'Drowsy'
                alert_text = 'DROWSINESS ALERT'

            cv2.putText(frame, f'Status: {status_text}', (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
            if alert_text:
                cv2.putText(frame, alert_text, (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 255), 2)

            ret, jpeg = cv2.imencode('.jpg', frame)
            return jpeg.tobytes() if ret else None
        except Exception as e:
            logger.error(f'Error processing frame: {str(e)}')
            return None

camera = None

def get_camera():
    """Get or initialize camera instance."""
    global camera
    if camera is None:
        camera = VideoCamera()
    return camera

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/camera_status')
def camera_status():
    """Check camera status."""
    cam = get_camera()
    return jsonify({
        'initialized': cam.camera_initialized,
        'error': cam.error_message
    })

def gen_frames():
    """Generate frames for video stream."""
    cam = get_camera()
    if not cam.camera_initialized:
        logger.error('Camera not initialized, cannot generate frames')
        return

    while True:
        try:
            frame = cam.get_frame()
            if frame is None:
                continue

            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
        except Exception as e:
            logger.error(f'Error in frame generation: {str(e)}')
            break

@app.route('/video_feed')
def video_feed():
    """Video feed endpoint."""
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.errorhandler(404)
def not_found(error):
    return {'error': 'Resource not found'}, 404

@app.errorhandler(500)
def internal_error(error):
    logger.error(f'Internal error: {str(error)}')
    return {'error': 'Internal server error'}, 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)
