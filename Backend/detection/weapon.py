# Backend/detection/weapon.py
import time
from datetime import datetime
import traceback

import shared_state as state
from utils.telegram_utils import send_telegram_alert
from utils.db_utils import save_alert_to_db

def _safe_get_conf_and_cls(box):
    try:
        conf_val = None
        if hasattr(box, "conf"):
            c = box.conf
            try:
                conf_val = float(c[0].item()) if hasattr(c, "__len__") else float(c)
            except Exception:
                conf_val = float(c)
        cls_val = None
        if hasattr(box, "cls"):
            cl = box.cls
            try:
                cls_val = int(cl[0].item()) if hasattr(cl, "__len__") else int(cl)
            except Exception:
                cls_val = int(cl)
        return conf_val, cls_val
    except Exception:
        return None, None

def weapon_detection():
    print("[weapon] Weapon detection thread started.")
    while True:
        # wait until system active and model loaded
        if not getattr(state, "detection_active", False) or not getattr(state, "yolo_weapon_model", None):
            time.sleep(0.1)
            continue

        try:
            frame = None
            with state.frame_lock:
                frame = state.processed_frames.get("crowd")

            if frame is None:
                ok, frame_raw = state.camera_manager.read()
                if not ok or frame_raw is None:
                    time.sleep(0.01)
                    continue
                frame = frame_raw.copy()
            else:
                frame = frame.copy()

            annotated = frame.copy()

            results = state.yolo_weapon_model(annotated, conf=0.75)

            if not results:
                with state.frame_lock:
                    state.processed_frames["weapon"] = annotated
                time.sleep(0.01)
                continue

            res = results[0]

            weapon_detected = False
            detected_info = None
            detected_name = None
            detected_conf = None

            boxes = getattr(res, "boxes", None)
            if boxes is not None and len(boxes) > 0:
                for box in boxes:
                    conf_val, cls_val = _safe_get_conf_and_cls(box)
                    try:
                        name = state.yolo_weapon_model.names.get(cls_val, str(cls_val)) if cls_val is not None else str(cls_val)
                    except Exception:
                        name = str(cls_val)

                    conf_numeric = conf_val if conf_val is not None else 0.0
                    threshold = getattr(state, "DETECTION_CONF_THRESHOLD", 0.20)

                    if name and str(name).lower() in ['gun', 'knife', 'handgun'] and conf_numeric >= threshold:
                        weapon_detected = True
                        detected_name = str(name).lower()
                        detected_conf = conf_numeric
                        detected_info = f"UNSAFE: {name} ({conf_numeric:.2f})"
                        break

            try:
                if hasattr(res, "plot"):
                    annotated = res.plot(annotated)
            except Exception:
                pass

            if weapon_detected:
                now = time.time()
                with state.status_lock:
                    last_time = getattr(state, "last_weapon_detection_time", None)

                if not last_time or (now - last_time >= getattr(state, "ALERT_COOLDOWN", 12)):
                    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    try:
                        send_telegram_alert(f"🚨 WEAPON DETECTED at {timestamp}\n{detected_info}", annotated)
                    except Exception as e:
                        print(f"[weapon] Telegram send error: {e}")

                    people_count_val = None
                    try:
                        people_count_val = int(state.crowd_count) if isinstance(state.crowd_count, str) and state.crowd_count.isdigit() else None
                    except Exception:
                        people_count_val = None

                    # DEBUG: show what we'll store
                    print(f"[weapon] Detected sub_type='{detected_name}', confidence={detected_conf}, people_count={people_count_val}")

                    try:
                        save_alert_to_db(
                            alert_type="Weapon",
                            sub_type=detected_name,
                            confidence=detected_conf,
                            people_count=people_count_val,
                            person_name=None,
                            violence_detected=(getattr(state, "last_violence_info", "Safe") != "Safe")
                        )
                    except Exception as e:
                        print(f"[weapon] DB save error: {e}")

                    with state.status_lock:
                        state.last_weapon_detection_time = now
                        state.last_weapon_info = detected_info
                        state.last_weapon_confidence = detected_conf

            if getattr(state, "last_weapon_detection_time", None) and time.time() - state.last_weapon_detection_time > getattr(state, "ALERT_COOLDOWN", 12):
                with state.status_lock:
                    state.last_weapon_info = "Safe"
                    state.last_weapon_confidence = None

            with state.frame_lock:
                state.processed_frames["weapon"] = annotated

        except Exception as e:
            print(f"[weapon] Unexpected error: {e}")
            traceback.print_exc()

        time.sleep(0.01)
