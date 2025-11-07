import cv2
import telegram
import asyncio
from ultralytics import YOLO

# --- Telegram API Configuration ---
# Your unique bot token from @BotFather
TELEGRAM_BOT_TOKEN = '8013386321:AAGD3EaPO3TBr5KJ8xnj274ryBb6K53fCE8'
# Your unique chat ID from @get_id_bot
TELEGRAM_CHAT_ID = '194798250' 

# Initialize the Telegram bot object
bot = telegram.Bot(token=TELEGRAM_BOT_TOKEN)

# An async function to send a message and photo
async def send_telegram_alert(message, image_path):
    try:
        # Send the photo with the caption
        await bot.send_photo(
            chat_id=TELEGRAM_CHAT_ID,
            photo=open(image_path, 'rb'),
            caption=message
        )
        print("Telegram alert sent successfully!")
    except Exception as e:
        print(f"Failed to send Telegram alert: {e}")

def run_fast_detection():
    try:
        # Update this line with the correct path to your 'best.pt' file.
        model = YOLO('C:/Users/aditya/Desktop/Hackathon/Weapon_Detection/runs/detect/train/weights/best.pt')
        colors = {'gun': (0, 0, 255), 'knife': (0, 255, 0)}
        
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            raise IOError("Cannot open webcam.")

        # --- New variables for a more precise alert system ---
        alert_sent = False
        alert_timer = 0
        alert_cooldown = 100  # Number of frames to wait before sending another alert
        consecutive_detections = 0
        min_consecutive_detections = 3  # Number of consecutive frames to confirm a detection
        min_conf = 0.60  # Only send alerts for detections over 70% confidence
        min_box_area = 5000  # Ignore detections with very small bounding boxes (in pixels)
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break

            # Run inference on the current frame.
            results = model(frame, stream=True)

            weapon_detected_this_frame = False
            last_alert_info = None  # Track the last detected weapon for alert
            for r in results:
                boxes = r.boxes
                for box in boxes:
                    x1, y1, x2, y2 = box.xyxy[0].int().tolist()
                    conf = round(box.conf[0].item(), 2)
                    cls = int(box.cls[0].item())
                    class_name = model.names[cls]

                    # Calculate bounding box area
                    box_area = (x2 - x1) * (y2 - y1)

                    # --- Precise Alert Logic ---
                    # Check for class, confidence, and minimum box size
                    if class_name in ['gun', 'knife'] and conf > min_conf and box_area > min_box_area:
                        weapon_detected_this_frame = True
                        last_alert_info = (class_name, conf, x1, y1)  # Save info for alert
                        color = colors.get(class_name, (255, 255, 255))
                        cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
                        cv2.putText(frame, f'{class_name} {conf}', (x1, y1 - 10),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
                        print(f"Potential {class_name} detected with confidence {conf}!")

            # Check for consecutive detections to confirm a genuine threat
            if weapon_detected_this_frame and last_alert_info:
                consecutive_detections += 1
                if consecutive_detections >= min_consecutive_detections and not alert_sent:
                    # Save the image to a file
                    alert_image_path = 'alert_image.jpg'
                    cv2.imwrite(alert_image_path, frame)

                    # Use the latest detected weapon info for the alert
                    class_name, conf, x1, y1 = last_alert_info
                    message = f"🚨 *PRECISE WEAPON DETECTED!* 🚨\nType: {class_name}\nAccuracy: {conf * 100:.2f}%\nLocation: [{x1}, {y1}]"

                    # Send the alert in a separate thread
                    asyncio.run(send_telegram_alert(message, alert_image_path))

                    alert_sent = True
                    alert_timer = 0
            else:
                consecutive_detections = 0  # Reset the counter if a frame has no weapon

            # Reset the alert flag after the cooldown period
            if alert_sent:
                alert_timer += 1
                if alert_timer >= alert_cooldown:
                    alert_sent = False

            # Display the resulting frame.
            cv2.imshow('Real-Time Weapon Detection', frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        if 'cap' in locals() and cap.isOpened():
            cap.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    run_fast_detection()  