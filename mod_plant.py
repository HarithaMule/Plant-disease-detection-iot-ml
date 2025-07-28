import os
import cv2
import serial
import time
from ultralytics import YOLO

# Connect to Arduino
try:
    arduino = serial.Serial("COM3", baudrate=9600, timeout=1)  # Update COM Port
    time.sleep(2)
    print("✅ Connected to Arduino")
except Exception as e:
    print(f"❌ Serial Connection Failed: {e}")
    exit()

# Load the trained YOLOv8 model
model_path = r"C:\Users\jeeva\OneDrive\Desktop\PLANT\train5\weights\best.pt"
print("📂 Loading YOLOv8 Model...")
model = YOLO(model_path)
print("✅ Model Loaded Successfully!")

# Pesticide recommendations
pesticides = {
    "Early_blight": [
        ("Chlorothalonil", "2.5 g/L"),
        ("Mancozeb", "2 g/L"),
        ("Azoxystrobin", "1 mL/L")
    ],
    "Bacterial_spot": [
        ("Crop Rotation", "Preventive method"),
        ("Copper Oxychloride", "3 g/L"),
        ("Oxytetracycline", "2 g/L")
    ]
}

while True:
    try:
        # Receive Sensor Data from Arduino
        print("\n📡 Requesting Sensor Data from Arduino...")
        arduino.write(b"request_data\n")  
        time.sleep(1)  

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

        # Ask for Image Path
        while True:
            image_path = input("\n📷 Enter the image path (or type 'exit' to quit): ").strip()

            if image_path.lower() == "exit":
                print("🚪 Exiting the Program. Goodbye!")
                arduino.close()
                exit()

            image_path = os.path.abspath(image_path)
            image_path = image_path.replace("\\", "/")

            if os.path.exists(image_path) and image_path.lower().endswith(('.jpg', '.png', '.jpeg')):
                print(f"🖼️ Processing Image: {image_path}")
                break
            else:
                print("⚠️ Invalid file! Please enter a valid image path (JPG, PNG, JPEG).")

        # Run YOLO Detection
        print("🔍 Running YOLO Detection...")
        results = model.predict(source=image_path, conf=0.3)

        image = cv2.imread(image_path)
        detected_diseases = []

        # Process YOLO Results
        for r in results:
            for box in r.boxes:
                cls_id = int(box.cls[0])  
                conf = box.conf[0].item()  
                x1, y1, x2, y2 = map(int, box.xyxy[0])  

                class_name = model.names[cls_id]
                detected_diseases.append(class_name)

                print(f"🔍 Detected: {class_name} | Confidence: {conf:.2f}")

                if class_name in pesticides:
                    recommended_pesticides = ", ".join(f"{p[0]} ({p[1]})" for p in pesticides[class_name])
                    print(f"🩺 Recommended Pesticides for {class_name}: {recommended_pesticides}")

                    # Send disease & pesticide info to Arduino
                    arduino_data = f"Disease:{class_name}|{pesticides[class_name][0][0]} {pesticides[class_name][0][1]}\n"
                    arduino.write(arduino_data.encode())
                    time.sleep(2)  

                # Draw bounding box
                cv2.rectangle(image, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cv2.putText(image, f"{class_name} ({conf:.2f})", (x1, y1 - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

        if not detected_diseases:
            print("✅ No disease detected.")

        cv2.imshow("🌱 Plant Disease Detection", image)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

        print("\n🔄 Image closed. Requesting new data from Arduino...")

    except Exception as e:
        print(f"❌ Error: {e}")
