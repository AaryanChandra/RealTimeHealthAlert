import os
import sys
sys.path.append(os.path.abspath(os.path.dirname(__file__)))
from models import Patient, Vital, Session, Staff
from datetime import datetime, timedelta
import random

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

session = Session()

# Seed staff if not present
if session.query(Staff).count() == 0:
    print('Populating staff...')
    staff_members = [
        Staff(name='Dr. Alice Smith', role='Doctor'),
        Staff(name='Dr. Bob Lee', role='Doctor'),
        Staff(name='Nurse Carol White', role='Nurse'),
        Staff(name='Nurse David Kim', role='Nurse')
    ]
    session.add_all(staff_members)
    session.commit()
    print('Staff seeded.')
else:
    print('Staff already exist.')

# Check if there are any patients
if session.query(Patient).count() == 0:
    print('Populating sample patients...')
    patients = [
        Patient(name=f'Patient {i}', age=random.randint(20, 80), gender=random.choice(['M', 'F']), condition='Healthy')
        for i in range(1, 6)
    ]
    session.add_all(patients)
    session.commit()
else:
    patients = session.query(Patient).all()

# Check if there are any vitals
if session.query(Vital).count() == 0:
    print('Populating sample vitals...')
    now = datetime.now()
    for p in patients:
        for i in range(50):
            v = Vital(
                patient_id=p.id,
                heart_rate=random.randint(60, 140),
                spo2=random.randint(88, 100),
                temperature=round(random.uniform(36.0, 40.0), 1),
                timestamp=now - timedelta(minutes=i*5)
            )
            session.add(v)
    session.commit()
    print('Sample vitals added.')
else:
    print('Vitals already exist.')

print('Setup complete.')

print("✅ Project setup completed. Open the folder in VS Code and run main.py.")
