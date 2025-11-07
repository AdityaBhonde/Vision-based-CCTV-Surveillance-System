# ==============================
# encode_faces.py
# ==============================

import os
import cv2
import face_recognition
import pickle

DATASET_DIR = "faces"
ENCODINGS_FILE = "encodings.pkl"

known_encodings = []
known_names = []

print("[INFO] Starting face encoding process...")

# Loop through each person's folder
for person_name in os.listdir(DATASET_DIR):
    person_dir = os.path.join(DATASET_DIR, person_name)
    if not os.path.isdir(person_dir):
        continue

    print(f"[INFO] Processing {person_name}...")

    for image_name in os.listdir(person_dir):
        image_path = os.path.join(person_dir, image_name)

        # Load image
        image = face_recognition.load_image_file(image_path)
        encodings = face_recognition.face_encodings(image)

        if len(encodings) > 0:
            known_encodings.append(encodings[0])
            known_names.append(person_name)
        else:
            print(f"[WARNING] No face found in {image_name}")

print(f"[INFO] Total faces encoded: {len(known_encodings)}")

# Save all encodings to file
data = {"encodings": known_encodings, "names": known_names}
with open(ENCODINGS_FILE, "wb") as f:
    pickle.dump(data, f)

print(f"[SUCCESS] Encodings saved to {ENCODINGS_FILE}")
