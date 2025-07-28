import os
import cv2
import serial
import time
from ultralytics import YOLO

# Connect to Arduino
try:
    arduino = serial.Serial("COM3", baudrate=9600, timeout=1)  # Change COM Port as needed
    time.sleep(2)
    print("✅ Connected to Arduino")
except Exception as e:
    print(f"❌ Serial Connection Failed: {e}")
    exit()

# Load the trained YOLOv8 model
model_path = r"C:\Users\jeeva\OneDrive\Desktop\TK184125_PLANT\train5\weights\best.pt"
print("📂 Loading YOLOv8 Model...")
model = YOLO(model_path)
print("✅ Model Loaded Successfully!")

while True:
    try:
        # Step 1: Receive Sensor Data from Arduino
        print("\n📡 Requesting Sensor Data from Arduino...")
        arduino.write(b"request_data\n")  # Request data from Arduino
        time.sleep(1)  # Wait for response
        
        sensor_data = arduino.readline().decode("utf-8").strip()
        if not sensor_data:
            continue

        print(f"🔹 Received: {sensor_data}")

        # Extract Temperature, Humidity, Soil Moisture
        if sensor_data.startswith("T:"):
            parts = sensor_data.split(" ")
            temperature = int(parts[0].split(":")[1])
            humidity = int(parts[1].split(":")[1])
            soil_moisture = int(parts[2].split(":")[1])

            print(f"🌡️ Temperature: {temperature}°C")
            print(f"💧 Humidity: {humidity}%")
            print(f"🌱 Soil Moisture: {soil_moisture}")

        # Step 2: Ask for Image Path
        while True:
            image_path = input("\n📷 Enter the image path (or type 'exit' to quit): ").strip()

            if image_path.lower() == "exit":
                print("🚪 Exiting the Program. Goodbye!")
                arduino.close()
                exit()

            # ✅ Automatically Fix Windows Path Issues
            image_path = os.path.abspath(image_path)  # Convert to absolute path
            image_path = image_path.replace("\\", "/")  # Convert backslashes to forward slashes

            # Validate Image Path
            if os.path.exists(image_path) and image_path.lower().endswith(('.jpg', '.png', '.jpeg')):
                print(f"🖼️ Processing Image: {image_path}")
                break
            else:
                print("⚠️ Invalid file! Please enter a valid image path (JPG, PNG, JPEG).")

        # Step 3: Run YOLO Detection
        print("🔍 Running YOLO Detection...")
        results = model.predict(source=image_path, conf=0.3)

        # Read the image using OpenCV
        image = cv2.imread(image_path)

        detected_diseases = []  # Store detected diseases

        # Process YOLO Results
        for r in results:
            for box in r.boxes:
                cls_id = int(box.cls[0])  # Class ID
                conf = box.conf[0].item()  # Confidence score
                x1, y1, x2, y2 = map(int, box.xyxy[0])  # Bounding box coordinates

                # Get class name from the trained model
                class_name = model.names[cls_id]
                detected_diseases.append(f"{class_name} ({conf:.2f})")

                # Print detected disease
                print(f"🔍 Detected: {class_name} | Confidence: {conf:.2f}")

                # Draw bounding box on the image
                cv2.rectangle(image, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cv2.putText(image, f"{class_name} ({conf:.2f})", (x1, y1 - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

        # If no diseases are detected
        if not detected_diseases:
            print("✅ No disease detected.")

        # Step 4: Show the image with detections
        cv2.imshow("🌱 Plant Disease Detection", image)
        cv2.waitKey(0)  # Wait until the window is closed by the user
        cv2.destroyAllWindows()

        print("\n🔄 Image closed. Requesting new data from Arduino...")

    except Exception as e:
        print(f"❌ Error: {e}")
        print("⚠️ Please check the image path or Arduino connection.")
