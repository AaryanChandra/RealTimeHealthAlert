import random
import time
from datetime import datetime
from models import Patient, Vital, Alert, Session

patients_info = [
    {"id": 1, "name": "John Doe", "age": 22, "gender": "Male", "condition": "Asthma"},
    {"id": 2, "name": "Saumya Singh", "age": 27, "gender": "Female", "condition": "Hypertension"},
    {"id": 3, "name": "Manish Verma", "age": 35, "gender": "Male", "condition": "Diabetes"},
    {"id": 4, "name": "Sara Ali", "age": 30, "gender": "Female", "condition": "Healthy"},
    {"id": 5, "name": "Karan Singh", "age": 40, "gender": "Male", "condition": "Cardiac"}
]

session = Session()

# Seed patients
if session.query(Patient).count() == 0:
    for p in patients_info:
        session.add(Patient(**p))
    session.commit()
    print("✅ Patients seeded.")

def simulate_vital_data():
    while True:
        for p in patients_info:
            heart_rate = random.randint(60, 160)
            spo2 = random.randint(85, 100)
            temperature = round(random.uniform(36.0, 40.0), 1)
            timestamp = datetime.now()

            # Save vitals
            vital = Vital(
                patient_id=p["id"],
                heart_rate=heart_rate,
                spo2=spo2,
                temperature=temperature,
                timestamp=timestamp
            )
            session.add(vital)

            # Alert logic
            if heart_rate > 140 or spo2 < 90 or temperature > 38.5:
                alert = Alert(
                    patient_id=p["id"],
                    anomaly=f"HR: {heart_rate}, SpO2: {spo2}, Temp: {temperature}",
                    timestamp=timestamp
                )
                session.add(alert)
                print(f"🚨 ALERT for {p['name']} → HR: {heart_rate}, SpO2: {spo2}, Temp: {temperature}")

        session.commit()
        time.sleep(5)

if __name__ == "__main__":
    simulate_vital_data()
