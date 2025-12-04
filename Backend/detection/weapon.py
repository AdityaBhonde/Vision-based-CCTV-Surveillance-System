# Backend/detection/weapon.py
import time
from datetime import datetime
import traceback
from typing import Tuple, Optional

import cv2
import numpy as np

import shared_state as state
from utils.telegram_utils import send_telegram_alert
from utils.db_utils import save_alert_to_db


# -------------------------
# Safe helpers for YOLO 'box' formats
# -------------------------
def _safe_get_conf_and_cls(box) -> Tuple[Optional[float], Optional[int]]:
    try:
        conf_val = None
        if hasattr(box, "conf"):
            c = box.conf
            try:
                # some objects are arrays, some scalars
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


def _safe_get_xyxy(box) -> Optional[Tuple[int, int, int, int]]:
    """Return (x1,y1,x2,y2) or None"""
    try:
        if hasattr(box, "xyxy"):
            pts = box.xyxy[0] if hasattr(box.xyxy, "__len__") else box.xyxy
            # convert to python ints
            xy = pts.int().tolist()
            return int(xy[0]), int(xy[1]), int(xy[2]), int(xy[3])
        # fallback older API:
        if hasattr(box, "xyxyxy"):  # unlikely
            pts = box.xyxyxy
            return tuple(int(x) for x in pts)
    except Exception:
        pass
    return None


# -------------------------
# Color mapping for subclasses
# -------------------------
DEFAULT_COLOR = (255, 255, 255)  # white
CLASS_COLOR_MAP = {
    # case-insensitive keys expected; we'll `.lower()` model names
    "gun": (0, 0, 255),        # red
    "pistol": (0, 0, 255),
    "revolver": (0, 0, 255),
    "firearm": (0, 0, 255),
    "rifle": (0, 0, 255),
    "knife": (0, 165, 255),    # orange
    "blade": (0, 165, 255),
    "weapon": (255, 0, 0),     # bright red
}


# ==================================================================================
#                                WEAPON DETECTION THREAD
# ==================================================================================
def weapon_detection():
    print("[weapon] Weapon detection thread started.")

    # Wait until the main app has loaded the model & signalled detection_active
    while True:
        if getattr(state, "detection_active", False) and getattr(state, "yolo_weapon_model", None) is not None:
            break
        time.sleep(0.1)

    # Print model class map for debug
    try:
        print(f"[weapon] Loaded YOLO Weapon Model classes: {state.yolo_weapon_model.names}")
    except Exception:
        print("[weapon] WARNING: Could not print model.names")

    # Tweak these to adjust sensitivity
    MIN_CONF = getattr(state, "DETECTION_CONF_THRESHOLD", 0.55)  # default high confidence
    VALID_CLASS_KEYWORDS = ["gun", "knife", "pistol", "revolver", "firearm", "rifle", "weapon"]

    COOLDOWN = getattr(state, "ALERT_COOLDOWN", 12)  # seconds between alerts for same detection
    last_alert_time = None

    while True:
        try:
            # Acquire a frame (prefer crowd-processed frame)
            with state.frame_lock:
                frame = state.processed_frames.get("crowd")

            if frame is None:
                ok, cam_frame = state.camera_manager.read()
                if not ok or cam_frame is None:
                    time.sleep(0.01)
                    continue
                frame = cam_frame.copy()
            else:
                frame = frame.copy()

            annotated = frame.copy()

            # Run inference (we pass conf=MIN_CONF to YOLO call to prefilter)
            results = state.yolo_weapon_model(frame, conf=MIN_CONF)

            if not results:
                # no detections: still push the frame for frontend
                with state.frame_lock:
                    state.processed_frames["weapon"] = annotated
                time.sleep(0.01)
                continue

            res = results[0]

            boxes = getattr(res, "boxes", None)
            weapon_detected = False
            detected_name = None
            detected_conf = None
            detected_box = None

            # iterate boxes if present
            if boxes is not None and len(boxes) > 0:
                for box in boxes:
                    conf_val, cls_val = _safe_get_conf_and_cls(box)
                    if conf_val is None:
                        continue

                    # get label string (fallback to cls index)
                    try:
                        name = state.yolo_weapon_model.names.get(cls_val, str(cls_val))
                    except Exception:
                        name = str(cls_val)

                    name = str(name).lower()

                    # quick filter: class keyword match + confidence
                    if any(k in name for k in VALID_CLASS_KEYWORDS) and conf_val >= MIN_CONF:
                        # small box filtering (optional) — reduce false positives for tiny detections
                        xy = _safe_get_xyxy(box)
                        if xy:
                            x1, y1, x2, y2 = xy
                            box_area = max(0, (x2 - x1) * (y2 - y1))
                            # ignore extremely small boxes; threshold tuned for 480x640 input (adjust if needed)
                            min_box_area = getattr(state, "WEAPON_MIN_BOX_AREA", 1500)
                            if box_area < min_box_area:
                                # skip tiny detection
                                continue

                        weapon_detected = True
                        detected_name = name
                        detected_conf = float(conf_val)
                        detected_box = _safe_get_xyxy(box)
                        break  # take first confident valid detection

            # Draw using YOLO's plot if available (it is helpful) then overlay custom colored box for clarity
            try:
                if hasattr(res, "plot"):
                    annotated = res.plot(annotated)
            except Exception:
                pass

            # If we have a detection, draw clearer color-coded rectangle & label
            if detected_box is not None:
                x1, y1, x2, y2 = detected_box
                color = DEFAULT_COLOR
                # choose color by best matching keyword
                for k, c in CLASS_COLOR_MAP.items():
                    if k in detected_name:
                        color = c
                        break
                # rectangle & label
                cv2.rectangle(annotated, (x1, y1), (x2, y2), color, 2)
                label_text = f"{detected_name} {detected_conf:.2f}"
                cv2.rectangle(annotated, (x1, y2 - 24), (x2, y2), color, -1)
                cv2.putText(annotated, label_text, (x1 + 6, y2 - 6), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)

            # If weapon confirmed, handle alerting & DB save
            if weapon_detected and detected_name is not None:
                now = time.time()
                if not last_alert_time or (now - last_alert_time >= COOLDOWN):
                    last_alert_time = now
                    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    alert_text = f"🚨 WEAPON DETECTED: {detected_name.upper()} ({detected_conf:.2f}) at {timestamp}"

                    # Send telegram (annotated image)
                    try:
                        send_telegram_alert(alert_text, annotated)
                    except Exception as e:
                        print(f"[weapon] Telegram send failed: {e}")

                    # determine people_count from shared_state (best-effort)
                    people_count_val = None
                    try:
                        if isinstance(state.crowd_count, str):
                            import re
                            m = re.search(r"\d+", state.crowd_count)
                            if m:
                                people_count_val = int(m.group(0))
                        elif isinstance(state.crowd_count, int):
                            people_count_val = state.crowd_count
                    except Exception:
                        people_count_val = None

                    # Save to DB — store subtype as detected_name (lowercase)
                    try:
                        save_alert_to_db(
                            alert_type="Weapon",
                            sub_type=str(detected_name),
                            confidence=float(detected_conf) if detected_conf is not None else None,
                            people_count=people_count_val,
                            person_name=None,
                            violence_detected=(getattr(state, "last_violence_info", "Safe") != "Safe"),
                        )
                    except Exception as e:
                        print(f"[weapon] DB save error: {e}")

                    # update shared status fields
                    with state.status_lock:
                        state.last_weapon_detection_time = now
                        state.last_weapon_info = f"{detected_name} ({detected_conf:.2f})"
                        state.last_weapon_confidence = detected_conf

            # clear "weapon" info after cooldown
            if last_alert_time and (time.time() - last_alert_time > COOLDOWN):
                with state.status_lock:
                    state.last_weapon_info = "Safe"
                    state.last_weapon_confidence = None

            # always push annotated frame for frontend
            with state.frame_lock:
                state.processed_frames["weapon"] = annotated

        except Exception as e:
            print(f"[weapon] Unexpected error: {e}")
            traceback.print_exc()

        # tiny sleep to yield CPU
        time.sleep(0.01)
