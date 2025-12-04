# ===================== app.py (FINAL WORKING VERSION) =====================
from flask import Flask, Response, jsonify, render_template
from flask_cors import CORS
import threading, time, cv2
from pathlib import Path
from ultralytics import YOLO

# Shared state
import shared_state as state

# Detection pipelines
from detection.crowd import crowd_detection
from detection.weapon import weapon_detection
from detection.criminal import criminal_detection

# Blueprints
from routes.status import status_bp
from routes.alerts import alerts_bp
from routes.analytics import analytics_bp   # <--- IMPORTANT

# ===================== FLASK APP INIT =====================
app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": ["http://localhost:8080", "http://127.0.0.1:8080"]}})

# ===================== CAMERA STREAM CLASS =====================
class CameraStream:
    def __init__(self, src=0):
        self.stream = cv2.VideoCapture(src, cv2.CAP_DSHOW)
        if not self.stream.isOpened():
            raise IOError(f"Cannot open camera index {src}")

        self.grabbed, self.frame = self.stream.read()
        self.started = False
        self.thread = threading.Thread(target=self.update)

    def start(self):
        if not self.started:
            self.started = True
            self.thread.start()
        return self

    def update(self):
        while self.started:
            grabbed, frame = self.stream.read()
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

# ===================== START DETECTION API =====================
@app.route('/api/start_detection', methods=['POST'])
def start_detection_system():
    if state.detection_active:
        return jsonify({"status": "Already running", "active": True}), 200

    try:
        print("\n🚀 Starting AI Surveillance System...")

        BASE = Path(__file__).resolve().parent

        # Load YOLO models from correct folders
        state.yolo_crowd_model = YOLO(str(BASE / "models/CrowdDetection/best.pt"))
        state.yolo_weapon_model = YOLO(str(BASE / "models/Weapon_Detection/weapon.pt"))
        print("➡️ Models loaded successfully")

        # Start camera
        state.camera_manager = CameraStream(src=0).start()
        state.detection_active = True

        # Start detection threads
        threading.Thread(target=crowd_detection, daemon=True).start()
        time.sleep(0.3)
        threading.Thread(target=weapon_detection, daemon=True).start()
        time.sleep(0.3)
        threading.Thread(target=criminal_detection, daemon=True).start()

        print("✔️ AI Surveillance System Running")
        return jsonify({"status": "Detection started", "active": True})

    except Exception as e:
        print("❌ ERROR starting system:", e)
        state.detection_active = False
        return jsonify({"status": f"Error starting: {str(e)}"}), 500

# ===================== STREAM GENERATOR =====================
def generate_frames(stream_type):
    boundary = "frame"

    while True:
        with state.frame_lock:
            frame = state.processed_frames.get(stream_type)

            # fallback stream
            if frame is None:
                frame = (
                    state.processed_frames.get('weapon') or
                    state.processed_frames.get('crowd') or
                    state.processed_frames.get('violence')
                )

        if frame is not None:
            ret, buf = cv2.imencode('.jpeg', frame)
            if ret:
                yield (
                    b'--' + boundary.encode() + b'\r\n'
                    b'Content-Type: image/jpeg\r\n\r\n' +
                    buf.tobytes() + b'\r\n'
                )
        else:
            time.sleep(0.03)

# ===================== VIDEO FEEDS =====================
@app.route('/crowd_feed')
def crowd_feed():
    return Response(generate_frames('crowd'),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/weapon_feed')
def weapon_feed():
    return Response(generate_frames('weapon'),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/violence_feed')
def violence_feed():
    return Response(generate_frames('violence'),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

# ===================== HOME =====================
@app.route('/')
def home():
    return render_template("dashboard.html")

# ===================== REGISTER BLUEPRINTS =====================
app.register_blueprint(status_bp)
app.register_blueprint(alerts_bp)
app.register_blueprint(analytics_bp)   # <--- THIS ENABLES PDF ROUTE

# ===================== RUN SERVER =====================
if __name__ == "__main__":
    # Debug OFF is correct so PDF generator works
    app.run(host="0.0.0.0", port=5000, debug=False, threaded=True, use_reloader=False)

