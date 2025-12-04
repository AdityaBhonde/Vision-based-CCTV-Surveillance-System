import cv2
from ultralytics import YOLO

# Load your custom-trained YOLOv8 model
model = YOLO('best.pt')

def count_people_in_frame(frame):
    results = model.predict(frame)
    people_count = 0

    for r in results:
        for box in r.boxes:
            cls = int(box.cls[0].item())
            conf = float(box.conf[0].item())

            # CONFIDENCE FILTER ADDED HERE
            if conf >= 0.40 and r.names[cls] == 'person':
                people_count += 1

    return people_count

def main():
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error: Could not open webcam.")
        return

    print("\nStarting crowd detection. Press 'q' to exit.")

    while True:
        success, frame = cap.read()
        if not success:
            print("Failed to grab frame.")
            break

        # Count people using the function
        people_count = count_people_in_frame(frame)

        # Print the total count to the console
        print(f"Total people detected: {people_count}")

        # Annotate and display the frame
        cv2.putText(frame, f"People: {people_count}",
                    (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1,
                    (255, 255, 0), 2)

        cv2.imshow("Crowd Detection", frame)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()
    print("\nCrowd detection complete.")

if __name__ == '__main__':
    main()
