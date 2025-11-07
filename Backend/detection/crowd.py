# ==============================
# detection/crowd.py
# ==============================

import time, cv2
from datetime import datetime
import shared_state as state
from utils.telegram_utils import send_telegram_alert
from utils.db_utils import save_alert_to_db

def crowd_detection():
    print("[INFO] Crowd detection thread started.")
    last_crowd_alert_time = None

    while state.detection_active and state.yolo_crowd_model:
        _, frame = state.camera_manager.read()
        if frame is None or not _:
            time.sleep(0.01)
            continue

        annotated = frame.copy()
        results = state.yolo_crowd_model.track(annotated, conf=0.35, persist=True, tracker="bytetrack.yaml")

        people_count = 0
        if results and results[0].boxes.id is not None:
            track_ids = results[0].boxes.id.int().tolist()
            people_count = len(set(track_ids))

        if people_count > 35:
            now = time.time()
            if not last_crowd_alert_time or (now - last_crowd_alert_time >= state.ALERT_COOLDOWN):
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                send_telegram_alert(f"🚨 CROWD ALERT at {timestamp}\nPeople Count: {people_count}", annotated)
                save_alert_to_db(alert_type="Crowd", people_count=people_count)
                last_crowd_alert_time = now

        state.crowd_count = str(people_count)
        annotated = results[0].plot() if results else annotated
        cv2.putText(annotated, f'Count: {people_count}', (10,30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,0), 2)

        with state.frame_lock:
            state.processed_frames['crowd'] = annotated

        time.sleep(0.01)
