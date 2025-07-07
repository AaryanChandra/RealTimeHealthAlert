from flask import Flask, render_template, request
import csv
import os

app = Flask(__name__)

def read_latest_data(filename="../health_data.csv", max_records=50):
    try:
        with open(filename, mode='r') as file:
            reader = csv.DictReader(file)
            data = list(reader)[-max_records:]
            return data
    except FileNotFoundError:
        return []

def get_patient_history(patient_id, filename="../health_data.csv", max_records=30):
    history = []
    try:
        with open(filename, mode='r') as file:
            reader = csv.DictReader(file)
            for row in reversed(list(reader)):
                if row["patient_id"] == str(patient_id):
                    history.append(row)
                if len(history) >= max_records:
                    break
    except FileNotFoundError:
        pass
    return list(reversed(history))

def load_patient_info():
    info = {}
    try:
        with open("../patients.csv") as file:
            reader = csv.DictReader(file)
            for row in reader:
                info[row["patient_id"]] = row
    except FileNotFoundError:
        pass
    return info

def get_severity(row):
    hr = int(row["heart_rate"])
    spo2 = float(row["spo2"])
    temp = float(row["temperature"])

    if hr > 140 or hr < 50 or spo2 < 90 or temp > 39:
        return "Critical"
    elif hr > 120 or hr < 60 or spo2 < 94 or temp > 38:
        return "Warning"
    else:
        return "Normal"

@app.route('/')
def dashboard():
    selected_id = request.args.get('patient_id', '1')
    data = read_latest_data()
    history = get_patient_history(selected_id)
    patients = load_patient_info()

    for row in data:
        row["severity"] = get_severity(row)

    for row in history:
        row["severity"] = get_severity(row)

    return render_template('index.html', records=data, history=history, selected_id=selected_id, patients=patients)
@app.route('/alerts')
def alerts():
    alerts = []
    patients = load_patient_info()

    try:
        with open("../alert_history.csv", mode='r') as file:
            reader = csv.DictReader(file)
            alerts = list(reader)[-100:]
    except FileNotFoundError:
        pass

    for row in alerts:
        try:
            row["severity"] = get_severity(row)
        except KeyError:
            row["severity"] = "Unknown"

    return render_template('alerts.html', alerts=alerts, patients=patients)

if __name__ == '__main__':
    app.run(debug=True)
