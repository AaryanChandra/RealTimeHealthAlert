import sqlite3
import random
import time
from datetime import datetime

DB_FILE = "health_data.db"

def generate_vital_signs():
    return {
        "heart_rate": random.randint(60, 160),
        "spo2": random.randint(85, 100),
        "temperature": round(random.uniform(36.0, 40.0), 1),
    }

def insert_data(patient_id, vitals):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("""
        INSERT INTO vitals (patient_id, heart_rate, spo2, temperature, timestamp)
        VALUES (?, ?, ?, ?, ?)
    """, (patient_id, vitals["heart_rate"], vitals["spo2"], vitals["temperature"], datetime.now()))
    conn.commit()
    conn.close()

while True:
    for patient_id in range(1, 6):
        vitals = generate_vital_signs()
        insert_data(patient_id, vitals)
        print(f"Patient {patient_id} | HR: {vitals['heart_rate']} | SPO2: {vitals['spo2']} | Temp: {vitals['temperature']}")
    time.sleep(5)
