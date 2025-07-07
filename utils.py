def get_patient_name(patient_id):
    names = {
        1: "John Doe",
        2: "Saumya Singh",
        3: "Manish Verma",
        4: "Sara Ali",
        5: "Karan Singh"
    }
    return names.get(patient_id, f"Patient {patient_id}")

def get_severity(hr, spo2, temp):
    if hr > 140 or spo2 < 85 or temp > 39.5:
        return "critical"
    elif hr > 120 or spo2 < 90 or temp > 39.0:
        return "warning"
    else:
        return "normal"
