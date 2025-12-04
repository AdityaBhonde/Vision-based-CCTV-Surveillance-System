import cv2
import asyncio
import threading
from flask import Flask, jsonify, Response
from ultralytics import YOLO
import telegram

# =============================================
# TELEGRAM SETUP
# =============================================
TELEGRAM_BOT_TOKEN = '8013386321:AAGD3EaPO3TBr5KJ8xnj274ryBb6K53fCE8'
TELEGRAM_CHAT_ID = '194798250'
bot = telegram.Bot(token=TELEGRAM_BOT_TOKEN)

async def send_telegram_alert(message, image_path):
    try:
        await bot.send_photo(
            chat_id=TELEGRAM_CHAT_ID,
            photo=open(image_path, 'rb'),
            caption=message
        )
        print("Telegram alert sent successfully!")
    except Exception as e:
        print(f"Telegram Error: {e}")


# =============================================
# GLOBAL MODEL + STATUS
# =============================================
model = YOLO("models/Weapon_Detection/weapon.pt")

VALID_WEAPONS = ['gun', 'knife', 'pistol', 'firearm', 'revolver', 'handgun']
min_conf = 0.60              # STRICT FILTER
min_box_area = 1500
min_consecutive_detections = 3
alert_cooldown = 20

weapon_status = "Safe"
crowd_count = 0
violence_status = "Safe"
system_active = False


# =============================================
# WEAPON DETECTION THREAD
# =============================================
def detection_thread():
    global weapon_status, system_active

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Camera error")
        return
    
    alert_sent = False
    alert_timer = 0
    consecutive_detections = 0

    while system_active:
        ret, frame = cap.read()
        if not ret:
            continue
        
        results = model(frame, stream=True)
        detected = False
        final_status_string = "Safe"
        best_conf = 0

        for r in results:
            for box in r.boxes:
                x1, y1, x2, y2 = box.xyxy[0].int().tolist()
                cls = int(box.cls[0].item())
                conf = round(box.conf[0].item(), 2)
                class_name = model.names[cls].lower()

                # AREA CHECK
                box_area = (x2 - x1) * (y2 - y1)
                if box_area < min_box_area:
                    continue

                # STRICT CONFIDENCE CHECK
                if class_name in VALID_WEAPONS and conf >= min_conf:
                    detected = True
                    best_conf = conf
                    final_status_string = f"{class_name} ({conf})"

        # =========================================
        # FRONTEND FILTER:
        # CONFIDENCE < 0.65 → FORCE "Safe"
        # =========================================
        if not detected:
            weapon_status = "Safe"
        else:
            weapon_status = final_status_string

        # TELEGRAM ALERT SYSTEM
        if detected:
            consecutive_detections += 1
            
            if consecutive_detections >= min_consecutive_detections and not alert_sent:
                cv2.imwrite("alert_image.jpg", frame)
                msg = f"🚨 *WEAPON DETECTED!* 🚨\nType: {class_name}\nAccuracy: {best_conf * 100:.2f}%"
                asyncio.run(send_telegram_alert(msg, "alert_image.jpg"))
                alert_sent = True
                alert_timer = 0

        else:
            consecutive_detections = 0

        if alert_sent:
            alert_timer += 1
            if alert_timer >= alert_cooldown:
                alert_sent = False

        # STREAM FRAME
        _, buffer = cv2.imencode(".jpg", frame)
        frame_bytes = buffer.tobytes()

        global latest_frame
        latest_frame = frame_bytes

    cap.release()
    cv2.destroyAllWindows()


# =============================================
# FLASK SETUP
# =============================================
app = Flask(__name__)
latest_frame = None


@app.route("/api/start_detection", methods=["POST"])
def start_detection():
    global system_active

    if not system_active:
        system_active = True
        threading.Thread(target=detection_thread, daemon=True).start()

    return jsonify({"status": "started"})


@app.route("/violence_feed")
def violence_feed():
    def generate():
        global latest_frame
        while True:
            if latest_frame:
                yield (b"--frame\r\n"
                       b"Content-Type: image/jpeg\r\n\r\n" + latest_frame + b"\r\n")

    return Response(generate(), mimetype="multipart/x-mixed-replace; boundary=frame")


@app.route("/get_status")
def get_status():
    global weapon_status, crowd_count, violence_status, system_active

    return jsonify({
        "weapon_status": weapon_status,      # STRICT FILTER APPLIED
        "crowd_count": str(crowd_count),
        "violence_status": violence_status,
        "system_active": system_active
    })


# =============================================
# MAIN
# =============================================
if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=False)
