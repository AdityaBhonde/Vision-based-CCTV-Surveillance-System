from flask import Flask, Response, jsonify, render_template
from flask_cors import CORS
from ultralytics import YOLO
import threading, time, cv2
from pathlib import Path

# Internal imports (modular)
import shared_state as state
from detection.crowd import crowd_detection
from detection.weapon import weapon_detection
from detection.criminal import criminal_detection        # <-- NEW: criminal thread
from routes.status import status_bp
from routes.alerts import alerts_bp
from routes.analytics import analytics_bp

# ================= FLASK INIT =================
app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": ["http://localhost:8080", "http://127.0.0.1:8080"]}})

# ================= CAMERA STREAM CLASS =================
class CameraStream:
    """Handles safe threaded video capture."""
    def __init__(self, src=0):
        self.stream = cv2.VideoCapture(src, cv2.CAP_DSHOW)
        if not self.stream.isOpened():
            raise IOError(f"Cannot open camera index {src}.")
        (self.grabbed, self.frame) = self.stream.read()
        self.started = False
        self.thread = threading.Thread(target=self.update)

    def start(self):
        if not self.started:
            self.started = True
            self.thread.start()
        return self

    def update(self):
        while self.started:
            (grabbed, frame) = self.stream.read()
            if grabbed:
                self.grabbed, self.frame = grabbed, frame
            time.sleep(0.01)

    def read(self):
        return self.grabbed, self.frame

    def stop(self):
        self.started = False
        if self.thread.is_alive():
            self.thread.join()
        self.stream.release()

# ================= START DETECTION =================
@app.route('/api/start_detection', methods=['POST'])
def start_detection_system():
    if state.detection_active:
        return jsonify({"status": "Detection already running.", "active": True}), 200

    try:
        print("\n--- Starting AI System Boot Process ---")

        # Resolve repo relative paths robustly
        BASE_DIR = Path(__file__).resolve().parent

        # Load YOLO models (paths resolved relative to Backend/)
        state.yolo_crowd_model = YOLO(str(BASE_DIR / "models" / "CrowdDetection" / "best.pt"))
        state.yolo_weapon_model = YOLO(str(BASE_DIR / "models" / "Weapon_Detection" / "weapon.pt"))
        # NOTE: face encodings are handled inside detection/criminal.py

        print("✅ Crowd and Weapon Models loaded successfully.")

        # Start camera stream
        state.camera_manager = CameraStream(src=0).start()
        print("✅ Camera stream started successfully.")

        # Activate detection threads (use criminal thread instead of old violence)
        state.detection_active = True
        threading.Thread(target=crowd_detection, daemon=True).start()
        time.sleep(0.5)
        threading.Thread(target=weapon_detection, daemon=True).start()
        time.sleep(0.5)
        threading.Thread(target=criminal_detection, daemon=True).start()   # <-- starts face/criminal detection

        print("🚀 AI System Booted and Threads Started ---")
        return jsonify({"status": "Detection system started successfully.", "active": True}), 200

    except Exception as e:
        print(f"❌ FATAL ERROR STARTING AI SYSTEM: {str(e)}")
        state.detection_active = False
        return jsonify({"status": f"Error: {str(e)}", "active": False}), 500

# ================= FRAME GENERATOR =================
def generate_frames(stream_type):
    boundary = "frame"
    while True:
        frame = None
        with state.frame_lock:
            if stream_type == 'crowd':
                frame = state.processed_frames.get('crowd')
            elif stream_type == 'weapon':
                frame = state.processed_frames.get('weapon')
            elif stream_type == 'violence':
                # keep endpoint name 'violence' for frontend compatibility
                frame = state.processed_frames.get('violence')

            if frame is None:
                frame = (state.processed_frames.get('violence')
                         or state.processed_frames.get('weapon')
                         or state.processed_frames.get('crowd'))

        if frame is not None:
            ret, buf = cv2.imencode('.jpeg', frame)
            if ret:
                yield (
                    b'--' + boundary.encode() + b'\r\n'
                    b'Content-Type: image/jpeg\r\n'
                    b'Content-Length: ' + str(len(buf)).encode() + b'\r\n\r\n' +
                    buf.tobytes() + b'\r\n'
                )
        else:
            time.sleep(0.03)

# ================= ROUTES =================
@app.route('/crowd_feed')
def crowd_feed():
    return Response(generate_frames('crowd'), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/weapon_feed')
def weapon_feed():
    return Response(generate_frames('weapon'), mimetype='multipart/x-mixed-replace; boundary=frame')

# keep same endpoint name for frontend (violence_feed)
@app.route('/violence_feed')
def violence_feed():
    return Response(generate_frames('violence'), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/')
def index():
    return render_template('dashboard.html')

# ================= BLUEPRINTS =================
app.register_blueprint(status_bp)
app.register_blueprint(alerts_bp)
app.register_blueprint(analytics_bp)

# ================= MAIN =================
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False, threaded=True, use_reloader=False)
