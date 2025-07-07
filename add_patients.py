import sqlite3
import random
from datetime import datetime, timedelta

def add_patient(name, age, gender, condition):
    conn = sqlite3.connect('health_data.db')
    cursor = conn.cursor()
    
    # Add patient
    cursor.execute("""
        INSERT INTO patients (name, age, gender, condition) 
        VALUES (?, ?, ?, ?)
    """, (name, age, gender, condition))
    
    patient_id = cursor.lastrowid
    
    # Generate some sample vitals for the new patient
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
    
    conn.commit()
    conn.close()
    print(f"✅ Added patient: {name} (ID: {patient_id})")

# Example: Add a new patient
if __name__ == "__main__":
    print("🏥 Adding new patients to the database...")
    
    # Add some example patients
    add_patient("Dr. Emily Chen", 28, "Female", "Healthy")
    add_patient("Robert Johnson", 45, "Male", "Hypertension")
    add_patient("Maria Garcia", 33, "Female", "Diabetes")
    
    print("\n🎉 New patients added successfully!")
    print("Refresh your dashboard to see the new patients.") 