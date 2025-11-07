import cv2
from ultralytics import YOLO

def train_and_detect():
    """
    Trains a YOLOv8 model and then uses it for real-time weapon detection.
    """
    try:
        # --- Step 1: Train the Model ---
        print("Step 1/2: Starting model training...")
        
        # Load a pre-trained YOLOv8 model.
        model = YOLO('yolov8n.pt')
        
        # Train the model and get the results object.
        results = model.train(data='data.yaml', epochs=100)
        
        # Get the path to the best-performing model after training.
        trained_model_path = results.save_dir / 'weights' / 'best.pt'
        
        print("\nTraining complete!")
        print(f"Trained model saved to: {trained_model_path}")
        
        # --- FIX: Get metrics from the new results_dict() method ---
        metrics = results.metrics.results_dict()
        
        # Print the final accuracy metrics from the training run
        print("\n--- Model Performance Metrics ---")
        print(f"Validation mAP50-95: {metrics['metrics/mAP50-95(B)']:.4f}")
        print(f"Validation mAP50: {metrics['metrics/mAP50(B)']:.4f}")
        print(f"Precision: {metrics['metrics/precision(B)']:.4f}")
        print(f"Recall: {metrics['metrics/recall(B)']:.4f}")

        # --- Step 2: Perform Real-Time Detection ---
        print("\nStep 2/2: Starting real-time detection. Press 'q' to exit.")
        
        # Load the newly trained model directly using its path.
        detection_model = YOLO(str(trained_model_path))
        colors = {'gun': (0, 0, 255), 'knife': (0, 255, 0)}
        
        # Open the camera stream.
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            raise IOError("Cannot open webcam.")

        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            # Run inference on the current frame.
            results = detection_model(frame, stream=True)
            
            # Process and display the results.
            for r in results:
                boxes = r.boxes
                for box in boxes:
                    x1, y1, x2, y2 = box.xyxy[0].int().tolist()
                    conf = round(box.conf[0].item(), 2)
                    cls = int(box.cls[0].item())
                    class_name = detection_model.names[cls]

                    if class_name in ['gun', 'knife']:
                        color = colors.get(class_name, (255, 255, 255))
                        cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
                        cv2.putText(frame, f'{class_name} {conf}', (x1, y1 - 10), 
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
                        print(f"ALERT! {class_name} detected with confidence {conf}!")
            
            # Display the resulting frame.
            cv2.imshow('Real-Time Weapon Detection', frame)
            
            # Exit on 'q' key press.
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        # Clean up resources.
        if 'cap' in locals() and cap.isOpened():
            cap.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    train_and_detect()
