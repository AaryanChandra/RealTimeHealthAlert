import csv
import os

def trigger_alert(patient_id, anomalies, timestamp, filename="alert_history.csv"):
    print(f"[ALERT] Patient {patient_id} has issues: {', '.join(anomalies)} at {timestamp}")
    
    # Save alert to CSV
    data = {
        "patient_id": patient_id,
        "anomalies": ', '.join(anomalies),
        "timestamp": timestamp
    }

    file_exists = os.path.isfile(filename)
    with open(filename, mode='a', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=data.keys())
        if not file_exists:
            writer.writeheader()
        writer.writerow(data)
