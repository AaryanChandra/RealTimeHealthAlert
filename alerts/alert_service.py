def trigger_alert(patient_id, anomalies, timestamp):
    print(f"[ALERT] Patient {patient_id} has issues: {', '.join(anomalies)} at {timestamp}")
