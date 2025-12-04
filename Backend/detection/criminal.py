# Backend/detection/criminal.py
import time
import cv2
import face_recognition
import pickle
from datetime import datetime
import shared_state as state
from utils.telegram_utils import send_telegram_alert
from utils.db_utils import save_alert_to_db
from pathlib import Path

# Configuration
PROCESS_EVERY_N_FRAMES = 2
TOLERANCE = 0.45   # face distance tolerance

# Load known encodings
BASE_DIR = Path(__file__).resolve().parent.parent
ENCODINGS_PATH = BASE_DIR / "models" / "face_recognition" / "encodings.pkl"

known_encodings = []
known_names = []
try:
    with open(str(ENCODINGS_PATH), "rb") as f:
        data = pickle.load(f)
        known_encodings = data.get("encodings", [])
        known_names = data.get("names", [])
    print(f"[criminal] Loaded {len(known_names)} known identities from encodings.")
except Exception as e:
    print(f"[criminal] Warning: could not load encodings.pkl: {e}")
    # The module will still run, but no matches will be found until encodings exist.

def criminal_detection():
    """Replace violence thread: perform face recognition and raise criminal alerts."""
    print("[INFO] Criminal (face) detection thread started.")
    frame_count = 0
    last_alert_time = None

    while state.detection_active:
        # Try get the weapon/processed frame, else camera direct
        with state.frame_lock:
            frame = state.processed_frames.get('weapon')

        if frame is None:
            ok, tmp = state.camera_manager.read()
            if not ok:
                time.sleep(0.01)
                continue
            frame = tmp.copy()

        frame_count += 1
        annotated = frame.copy()

        # Only process every N frames to save CPU
        if frame_count % PROCESS_EVERY_N_FRAMES == 0 and len(known_encodings) > 0:
            # Resize to speed up
            small = cv2.resize(annotated, (0, 0), fx=0.25, fy=0.25)
            rgb_small = cv2.cvtColor(small, cv2.COLOR_BGR2RGB)

            face_locations = face_recognition.face_locations(rgb_small)
            face_encodings = face_recognition.face_encodings(rgb_small, face_locations)

            # For each detected face, compare to known encodings
            for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
                distances = face_recognition.face_distance(known_encodings, face_encoding)
                if len(distances) == 0:
                    continue
                best_idx = int(distances.argmin())
                best_distance = float(distances[best_idx])
                match = best_distance <= TOLERANCE
                name = "Unknown"
                if match:
                    name = known_names[best_idx]

                # scale coords back to original
                top *= 4; right *= 4; bottom *= 4; left *= 4

                color = (0, 0, 255) if name == "Unknown" else (0, 255, 0)
                cv2.rectangle(annotated, (left, top), (right, bottom), color, 2)
                cv2.rectangle(annotated, (left, bottom - 30), (right, bottom), color, cv2.FILLED)
                cv2.putText(annotated, name, (left + 6, bottom - 8), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255,255,255), 2)

                # If name is a *known criminal* (you decide what names are criminals — here we just treat all known names as notable)
                if name != "Unknown":
                    now = time.time()
                    if not last_alert_time or (now - last_alert_time >= state.ALERT_COOLDOWN):
                        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        # Send telegram alert (image + message)
                        send_telegram_alert(f"🚨 CRIMINAL IDENTIFIED: {name} at {timestamp}", annotated)
                        # Save in DB with combined context (include crowd_count if present)
                        try:
                            people_count_val = None
                            if isinstance(state.crowd_count, str):
                                import re
                                m = re.search(r'\d+', state.crowd_count)
                                if m:
                                    people_count_val = int(m.group(0))
                            elif isinstance(state.crowd_count, int):
                                people_count_val = state.crowd_count

                            save_alert_to_db(alert_type="Criminal",
                                             sub_type=name,
                                             person_name=name,
                                             confidence=1.0 - best_distance,   # higher = more confident
                                             people_count=people_count_val)
                        except Exception as e:
                            print(f"[criminal] DB save error: {e}")

                        with state.status_lock:
                            state.last_violence_detection_time = now   # reuse violence timestamp fields
                            state.last_violence_info = f"CRIMINAL: {name}"

                        last_alert_time = now

        # Update the "violence" output frame so frontend shows annotated frame
        with state.frame_lock:
            state.processed_frames['violence'] = annotated

        time.sleep(0.01)

