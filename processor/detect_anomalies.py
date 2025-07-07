def check_for_anomaly(data):
    anomalies = []

    if data["heart_rate"] > 130:
        anomalies.append("High Heart Rate")
    if data["spo2"] < 94:
        anomalies.append("Low SpO2")
    if data["temperature"] > 38.5:
        anomalies.append("High Temperature")

    return anomalies
