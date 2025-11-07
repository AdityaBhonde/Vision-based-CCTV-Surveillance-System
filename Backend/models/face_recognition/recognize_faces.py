import cv2
import face_recognition
import pickle
import numpy as np

# Load encodings
print("[INFO] Loading face encodings...")
with open("encodings.pkl", "rb") as f:
    data = pickle.load(f)

known_encodings = data["encodings"]
known_names = data["names"]

# Initialize webcam
print("[INFO] Starting webcam...")
video_capture = cv2.VideoCapture(0)

if not video_capture.isOpened():
    raise IOError("Cannot open webcam")

process_every_n_frame = 2  # Process every 2nd frame for performance
frame_count = 0

# Initialize variables globally so they always exist
face_locations = []
face_encodings = []
face_names = []

while True:
    ret, frame = video_capture.read()
    if not ret:
        print("[ERROR] Failed to grab frame.")
        break

    frame_count += 1

    # Resize frame for faster processing
    small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
    rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)

    if frame_count % process_every_n_frame == 0:
        # Detect faces and get encodings
        face_locations = face_recognition.face_locations(rgb_small_frame)
        face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

        face_names = []
        for face_encoding in face_encodings:
            matches = face_recognition.compare_faces(known_encodings, face_encoding, tolerance=0.45)
            face_distances = face_recognition.face_distance(known_encodings, face_encoding)
            best_match_index = np.argmin(face_distances)

            if matches[best_match_index]:
                name = known_names[best_match_index]
            else:
                name = "Unknown"

            face_names.append(name)

    # Draw results (always safe now, even if no faces detected)
    for (top, right, bottom, left), name in zip(face_locations, face_names):
        # Scale back up to full frame size (since we processed a smaller frame)
        top *= 4
        right *= 4
        bottom *= 4
        left *= 4

        color = (0, 255, 0) if name != "Unknown" else (0, 0, 255)
        cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
        cv2.rectangle(frame, (left, bottom - 35), (right, bottom), color, cv2.FILLED)
        cv2.putText(frame, name, (left + 6, bottom - 6), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)

    # Display output
    cv2.imshow("Face Recognition - Press 'q' to quit", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

video_capture.release()
cv2.destroyAllWindows()
print("[INFO] Stopped video stream.")
