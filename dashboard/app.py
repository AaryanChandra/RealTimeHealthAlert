from flask import Flask, render_template, jsonify, request
import sqlite3
import os
import random
import sys
from datetime import datetime, timedelta

# Add parent directory to path to import ml_predictor
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from ml_predictor import predictor

app = Flask(__name__)

def get_db_path():
    # Get the path to the database file relative to the current script
    current_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(current_dir, '..', 'health_data.db')

def get_patient_name(patient_id):
    try:
        conn = sqlite3.connect(get_db_path())
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM patients WHERE id = ?", (patient_id,))
        result = cursor.fetchone()
        conn.close()
        return result[0] if result else f"Patient {patient_id}"
    except Exception as e:
        print(f"Error getting patient name: {e}")
        return f"Patient {patient_id}"

def get_latest_vitals():
    try:
        conn = sqlite3.connect(get_db_path())
        cursor = conn.cursor()
        # Increase limit to get more vital records and ensure new patients are included
        cursor.execute("SELECT * FROM vitals ORDER BY timestamp DESC LIMIT 50")
        rows = cursor.fetchall()
        conn.close()
        
        print(f"Found {len(rows)} vital records")
        
        data = []
        for row in rows:
            patient_id = row[1]
            data.append({
                "name": get_patient_name(patient_id),
                "heart_rate": row[2],
                "spo2": row[3],
                "temperature": row[4],
                "timestamp": row[5],
            })
        return data[::-1]  # Reverse to get chronological order
    except Exception as e:
        print(f"Error getting vitals: {e}")
        return []

def get_patient_vitals_by_name(patient_name):
    """Get all vitals for a specific patient"""
    try:
        conn = sqlite3.connect(get_db_path())
        cursor = conn.cursor()
        
        # Get patient ID first
        cursor.execute("SELECT id FROM patients WHERE name = ?", (patient_name,))
        patient_result = cursor.fetchone()
        
        if not patient_result:
            return []
        
        patient_id = patient_result[0]
        
        # Get all vitals for this patient
        cursor.execute("SELECT * FROM vitals WHERE patient_id = ? ORDER BY timestamp ASC", (patient_id,))
        rows = cursor.fetchall()
        conn.close()
        
        vitals = []
        for row in rows:
            vitals.append({
                "heart_rate": row[2],
                "spo2": row[3],
                "temperature": row[4],
                "timestamp": row[5],
            })
        
        return vitals
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
        
        conn = sqlite3.connect(get_db_path())
        cursor = conn.cursor()
        
        # Add patient
        cursor.execute("""
            INSERT INTO patients (name, age, gender, condition) 
            VALUES (?, ?, ?, ?)
        """, (name, age, gender, condition))
        
        patient_id = cursor.lastrowid
        
        # Generate sample vitals for the new patient
        now = datetime.now()
        for i in range(20):  # Add 20 sample vital records
            vital = {
                'patient_id': patient_id,
                'heart_rate': random.randint(60, 140),
                'spo2': random.randint(88, 100),
                'temperature': round(random.uniform(36.0, 40.0), 1),
                'timestamp': now - timedelta(minutes=i*5)
            }
            
            cursor.execute("""
                INSERT INTO vitals (patient_id, heart_rate, spo2, temperature, timestamp)
                VALUES (?, ?, ?, ?, ?)
            """, (vital['patient_id'], vital['heart_rate'], vital['spo2'], 
                  vital['temperature'], vital['timestamp']))
        
        # Save notes if provided
        if notes:
            # You could store notes in a separate table or use localStorage
            pass
        
        conn.commit()
        conn.close()
        
        print(f"✅ Added patient: {name} (ID: {patient_id})")
        return jsonify({"success": True, "patient_id": patient_id, "message": f"Patient {name} added successfully!"})
        
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

@app.route("/train-model")
def train_model():
    """Train the ML model with current data"""
    try:
        # Get all vitals grouped by patient
        conn = sqlite3.connect(get_db_path())
        cursor = conn.cursor()
        cursor.execute("SELECT patient_id, heart_rate, spo2, temperature, timestamp FROM vitals ORDER BY patient_id, timestamp")
        rows = cursor.fetchall()
        conn.close()
        
        # Group by patient
        patients_vitals = {}
        for row in rows:
            patient_id = row[0]
            if patient_id not in patients_vitals:
                patients_vitals[patient_id] = []
            
            patients_vitals[patient_id].append({
                "heart_rate": row[1],
                "spo2": row[2],
                "temperature": row[3],
                "timestamp": row[4]
            })
        
        # Convert to list for training
        vitals_data = list(patients_vitals.values())
        
        # Train model
        success = predictor.train_model(vitals_data)
        
        if success:
            return jsonify({"success": True, "message": "Model trained successfully!"})
        else:
            return jsonify({"success": False, "message": "Not enough data to train model"})
            
    except Exception as e:
        print(f"Error training model: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
