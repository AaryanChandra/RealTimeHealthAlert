import os

# Folder structure
folders = [
    "data_generator",
    "processor",
    "alerts",
    "storage",
    "dashboard",
    "templates",
    "static"
]

# File contents
files = {
    "main.py": '''import time
import json

from data_generator.simulate_data import generate_data
from processor.detect_anomalies import check_for_anomaly
from alerts.alert_service import trigger_alert
from storage.store_data import store_data

if __name__ == "__main__":
    print("🔴 Real-Time Health Emergency Alert System Started")

    while True:
        for patient_id in range(1, 6):  # Simulate 5 patients
            data = generate_data(patient_id)
            print(f"[DATA] {json.dumps(data)}")

            anomalies = check_for_anomaly(data)
            if anomalies:
                trigger_alert(patient_id, anomalies, data["timestamp"])

            store_data(data)
        time.sleep(2)
''',

    "requirements.txt": "flask\n",

    "data_generator/simulate_data.py": '''import random
import time

def generate_data(patient_id):
    data = {
        "patient_id": patient_id,
        "heart_rate": random.randint(60, 180),
        "spo2": round(random.uniform(90, 100), 2),
        "temperature": round(random.uniform(36.5, 40.5), 2),
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
    }
    return data
''',

    "processor/detect_anomalies.py": '''def check_for_anomaly(data):
    anomalies = []

    if data["heart_rate"] > 130:
        anomalies.append("High Heart Rate")
    if data["spo2"] < 94:
        anomalies.append("Low SpO2")
    if data["temperature"] > 38.5:
        anomalies.append("High Temperature")

    return anomalies
''',

    "alerts/alert_service.py": '''def trigger_alert(patient_id, anomalies, timestamp):
    print(f"[ALERT] Patient {patient_id} has issues: {', '.join(anomalies)} at {timestamp}")
''',

    "storage/store_data.py": '''import csv
import os

def store_data(data, filename="health_data.csv"):
    file_exists = os.path.isfile(filename)
    with open(filename, mode='a', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=data.keys())
        if not file_exists:
            writer.writeheader()
        writer.writerow(data)
'''
}

# Create folders
for folder in folders:
    os.makedirs(folder, exist_ok=True)

# Create and write files (UTF-8 encoding)
for path, content in files.items():
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)


print("✅ Project setup completed. Open the folder in VS Code and run main.py.")
