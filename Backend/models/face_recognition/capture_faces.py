# ==============================
# capture_faces.py
# ==============================

import cv2
import os
import time

# === Configuration ===
person_name = "Aditya"          # <-- change this if you capture someone else
output_dir = f"faces/{person_name}"
num_samples = 100               # total images to capture
delay_between_snaps = 0.5       # seconds between captures

# === Create output directory ===
if not os.path.exists(output_dir):
    os.makedirs(output_dir)
    print(f"[INFO] Created folder: {output_dir}")

# === Initialize webcam ===
cam = cv2.VideoCapture(0, cv2.CAP_DSHOW)
if not cam.isOpened():
    raise IOError("Cannot access webcam!")

print("[INFO] Starting face capture session...")
print("[INFO] Press 'q' to quit early.")

count = 0

while count < num_samples:
    ret, frame = cam.read()
    if not ret:
        print("[ERROR] Frame capture failed.")
        break

    # Display live frame with info
    display_frame = frame.copy()
    cv2.putText(display_frame, f"Capturing {count+1}/{num_samples}", (30, 50),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

    cv2.imshow("Face Capture - Press 'q' to stop", display_frame)

    # Save snapshot
    img_path = os.path.join(output_dir, f"img_{count+1}.jpg")
    cv2.imwrite(img_path, frame)
    count += 1
    time.sleep(delay_between_snaps)

    # Exit early if user presses 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        print("[INFO] Capture stopped by user.")
        break

print(f"[INFO] Captured {count} images and saved to '{output_dir}'.")

cam.release()
cv2.destroyAllWindows()
