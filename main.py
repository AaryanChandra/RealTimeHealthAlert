import time
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
