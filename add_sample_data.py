import sqlite3
import random
from datetime import datetime, timedelta
import os

def get_db_path():
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), 'health_data.db')

def add_sample_data():
    """Add sample patients and vital data for ML training"""
    conn = sqlite3.connect(get_db_path())
    cursor = conn.cursor()
    
    # Sample patients with different conditions
    sample_patients = [
        ("John Smith", 45, "Male", "Hypertension"),
        ("Sarah Johnson", 32, "Female", "Diabetes"),
        ("Michael Brown", 58, "Male", "Heart Disease"),
        ("Emily Davis", 28, "Female", "Asthma"),
        ("Robert Wilson", 67, "Male", "COPD"),
        ("Lisa Anderson", 41, "Female", "Hypertension"),
        ("David Taylor", 55, "Male", "Diabetes"),
        ("Jennifer Martinez", 35, "Female", "Asthma"),
        ("James Garcia", 62, "Male", "Heart Disease"),
        ("Amanda Rodriguez", 29, "Female", "Healthy"),
        ("Christopher Lee", 48, "Male", "Hypertension"),
        ("Michelle White", 37, "Female", "Diabetes"),
        ("Daniel Thompson", 71, "Male", "COPD"),
        ("Ashley Clark", 33, "Female", "Asthma"),
        ("Matthew Lewis", 52, "Male", "Heart Disease")
    ]
    
    print("🏥 Adding sample patients...")
    
    # Add patients
    for name, age, gender, condition in sample_patients:
        cursor.execute("""
            INSERT OR IGNORE INTO patients (name, age, gender, condition) 
            VALUES (?, ?, ?, ?)
        """, (name, age, gender, condition))
    
    # Get all patient IDs
    cursor.execute("SELECT id FROM patients")
    patient_ids = [row[0] for row in cursor.fetchall()]
    
    print(f"📊 Adding vital data for {len(patient_ids)} patients...")
    
    # Add vital data for each patient
    now = datetime.now()
    for patient_id in patient_ids:
        # Generate 30-50 vital records per patient
        num_records = random.randint(30, 50)
        
        for i in range(num_records):
            # Base vitals with some variation
            if patient_id % 3 == 0:  # Some patients with higher risk
                heart_rate = random.randint(80, 160)
                spo2 = random.randint(85, 98)
                temperature = round(random.uniform(36.5, 40.5), 1)
            elif patient_id % 5 == 0:  # Some patients with very high risk
                heart_rate = random.randint(100, 180)
                spo2 = random.randint(80, 95)
                temperature = round(random.uniform(37.0, 41.0), 1)
            else:  # Normal patients
                heart_rate = random.randint(60, 100)
                spo2 = random.randint(92, 100)
                temperature = round(random.uniform(36.0, 38.5), 1)
            
            timestamp = now - timedelta(minutes=i*10)
            
            cursor.execute("""
                INSERT INTO vitals (patient_id, heart_rate, spo2, temperature, timestamp)
                VALUES (?, ?, ?, ?, ?)
            """, (patient_id, heart_rate, spo2, temperature, timestamp))
    
    conn.commit()
    conn.close()
    
    print("✅ Sample data added successfully!")
    print(f"📈 Added {len(patient_ids)} patients with vital data")
    
    # Show summary
    conn = sqlite3.connect(get_db_path())
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM patients")
    patient_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM vitals")
    vital_count = cursor.fetchone()[0]
    
    conn.close()
    
    print(f"📊 Database now contains:")
    print(f"   👥 {patient_count} patients")
    print(f"   💓 {vital_count} vital records")

if __name__ == "__main__":
    add_sample_data() 