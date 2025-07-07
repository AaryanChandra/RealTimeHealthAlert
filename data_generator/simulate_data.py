import random
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
