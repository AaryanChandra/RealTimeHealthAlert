import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from flask import Flask, render_template, jsonify, request
import random
from datetime import datetime, timedelta
from mongo_models import MongoPatient, MongoVital, MongoAlert, MongoStaff, MongoAssignment, init_mongo_db
from ml_predictor import predictor
import numpy as np
from sklearn.linear_model import LinearRegression

app = Flask(__name__)

# Initialize MongoDB
init_mongo_db()

# Deployment configuration
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)), debug=False)

def get_patient_name(patient_id):
    try:
        from mongo_models import patients
        patient = patients.find_one({'_id': patient_id})
        return patient['name'] if patient else f"Patient {patient_id}"
    except Exception as e:
        print(f"Error getting patient name: {e}")
        return f"Patient {patient_id}"

def get_latest_vitals():
    try:
        vitals_data = MongoVital.get_latest(50)
        print(f"Found {len(vitals_data)} vital records")
        
        data = []
        for vital in vitals_data:
            patient_name = get_patient_name(vital['patient_id'])
            data.append({
                "name": patient_name,
                "heart_rate": vital['heart_rate'],
                "spo2": vital['spo2'],
                "temperature": vital['temperature'],
                "timestamp": vital['timestamp'].isoformat() if isinstance(vital['timestamp'], datetime) else vital['timestamp'],
            })
        return data[::-1]  # Reverse to get chronological order
    except Exception as e:
        print(f"Error getting vitals: {e}")
        return []

def get_patient_vitals_by_name(patient_name):
    """Get all vitals for a specific patient"""
    try:
        from mongo_models import patients, vitals
        
        # Get patient ID first
        patient = patients.find_one({'name': patient_name})
        if not patient:
            return []
        
        patient_id = patient['_id']
        
        # Get all vitals for this patient
        vitals_data = vitals.find({'patient_id': patient_id}).sort('timestamp', 1)
        
        vitals_list = []
        for vital in vitals_data:
            vitals_list.append({
                "heart_rate": vital['heart_rate'],
                "spo2": vital['spo2'],
                "temperature": vital['temperature'],
                "timestamp": vital['timestamp'].isoformat() if isinstance(vital['timestamp'], datetime) else vital['timestamp'],
            })
        
        return vitals_list
    except Exception as e:
        print(f"Error getting patient vitals: {e}")
        return []

@app.route("/")
def dashboard():
    return render_template("dashboard.html")

@app.route("/vitals")
def vitals():
    data = get_latest_vitals()
    print(f"Returning {len(data)} vital records")
    return jsonify(data)

@app.route("/add-patient", methods=["POST"])
def add_patient():
    try:
        data = request.get_json()
        name = data.get('name')
        age = data.get('age')
        gender = data.get('gender')
        condition = data.get('condition')
        notes = data.get('notes', '')
        
        if not all([name, age, gender, condition]):
            return jsonify({"success": False, "error": "Missing required fields"}), 400
        
        # Add patient using MongoDB
        patient = MongoPatient(name, age, gender, condition)
        result = patient.save()
        patient_id = result.inserted_id
        
        # Generate sample vitals for the new patient
        now = datetime.now()
        for i in range(20):  # Add 20 sample vital records
            vital = MongoVital(
                patient_id=patient_id,
                heart_rate=random.randint(60, 140),
                spo2=random.randint(88, 100),
                temperature=round(random.uniform(36.0, 40.0), 1),
                timestamp=now - timedelta(minutes=i*5)
            )
            vital.save()
        
        print(f"✅ Added patient: {name} (ID: {patient_id})")
        return jsonify({"success": True, "patient_id": str(patient_id), "message": f"Patient {name} added successfully!"})
        
    except Exception as e:
        print(f"Error adding patient: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route("/predict-risk/<patient_name>")
def predict_risk(patient_name):
    """Get ML risk prediction for a patient"""
    try:
        vitals = get_patient_vitals_by_name(patient_name)
        if len(vitals) < 5:
            return jsonify({"error": "Insufficient data for prediction"})
        
        # Get prediction
        prediction = predictor.predict_risk(vitals)
        insights = predictor.get_patient_insights(vitals)
        
        return jsonify({
            "patient_name": patient_name,
            "prediction": prediction,
            "insights": insights
        })
        
    except Exception as e:
        print(f"Error predicting risk: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/forecast/<patient_name>")
def forecast_vitals(patient_name):
    """Get 24-hour forecast for a patient"""
    try:
        vitals = get_patient_vitals_by_name(patient_name)
        if len(vitals) < 10:
            return jsonify({"error": "Insufficient data for forecasting"})
        
        # Prepare data for forecasting
        def parse_ts(ts):
            if isinstance(ts, str):
                return datetime.fromisoformat(ts.replace('Z', '+00:00'))
            return ts
        
        # Get recent vitals (last 20 readings)
        recent_vitals = vitals[-20:]
        
        # Create time series for each vital
        timestamps = [parse_ts(v['timestamp']) for v in recent_vitals]
        heart_rates = [v['heart_rate'] for v in recent_vitals]
        spo2_values = [v['spo2'] for v in recent_vitals]
        temperatures = [v['temperature'] for v in recent_vitals]
        
        # Convert timestamps to numerical values for ML
        time_nums = [(t - timestamps[0]).total_seconds() / 3600 for t in timestamps]
        
        # Train forecasting models
        forecast_hours = 24
        future_times = [time_nums[-1] + i for i in range(1, forecast_hours + 1)]
        
        # Heart rate forecast
        hr_model = LinearRegression()
        hr_model.fit(np.array(time_nums).reshape(-1, 1), heart_rates)
        hr_forecast = hr_model.predict(np.array(future_times).reshape(-1, 1))
        
        # SpO2 forecast
        spo2_model = LinearRegression()
        spo2_model.fit(np.array(time_nums).reshape(-1, 1), spo2_values)
        spo2_forecast = spo2_model.predict(np.array(future_times).reshape(-1, 1))
        
        # Temperature forecast
        temp_model = LinearRegression()
        temp_model.fit(np.array(time_nums).reshape(-1, 1), temperatures)
        temp_forecast = temp_model.predict(np.array(future_times).reshape(-1, 1))
        
        # Prepare response
        history = []
        for i, vital in enumerate(recent_vitals):
            history.append({
                'timestamp': vital['timestamp'],
                'heart_rate': heart_rates[i],
                'spo2': spo2_values[i],
                'temperature': temperatures[i]
            })
        
        forecast = []
        for i in range(forecast_hours):
            forecast.append({
                'timestamp': (timestamps[-1] + timedelta(hours=i+1)).isoformat(),
                'heart_rate': max(40, min(200, int(hr_forecast[i]))),
                'spo2': max(70, min(100, int(spo2_forecast[i]))),
                'temperature': max(35.0, min(42.0, round(temp_forecast[i], 1)))
            })
        
        return jsonify({
            'patient_name': patient_name,
            'history': history,
            'forecast': forecast
        })
        
    except Exception as e:
        print(f"Error forecasting: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/alerts")
def get_alerts():
    """Get all alerts"""
    try:
        alerts_data = MongoAlert.get_all()
        return jsonify(alerts_data)
    except Exception as e:
        print(f"Error getting alerts: {e}")
        return jsonify([])

@app.route("/patients")
def get_patients():
    """Get all patients"""
    try:
        patients_data = MongoPatient.get_all()
        return jsonify(patients_data)
    except Exception as e:
        print(f"Error getting patients: {e}")
        return jsonify([])

if __name__ == "__main__":
    app.run(debug=True) 