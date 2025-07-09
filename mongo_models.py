from pymongo import MongoClient
from datetime import datetime
import os

# MongoDB connection
def get_mongo_client():
    # For local development
    if os.environ.get('MONGODB_URI'):
        return MongoClient(os.environ.get('MONGODB_URI'))
    else:
        return MongoClient('mongodb://localhost:27017/')

client = get_mongo_client()
db = client['healthcare_monitor']

# Collections
patients = db['patients']
vitals = db['vitals']
alerts = db['alerts']
staff = db['staff']
assignments = db['assignments']

# MongoDB Models
class MongoPatient:
    def __init__(self, name, age, gender, condition):
        self.name = name
        self.age = age
        self.gender = gender
        self.condition = condition
        self.created_at = datetime.now()
    
    def save(self):
        return patients.insert_one({
            'name': self.name,
            'age': self.age,
            'gender': self.gender,
            'condition': self.condition,
            'created_at': self.created_at
        })
    
    @staticmethod
    def get_all():
        return list(patients.find())
    
    @staticmethod
    def get_by_name(name):
        return patients.find_one({'name': name})

class MongoVital:
    def __init__(self, patient_id, heart_rate, spo2, temperature, timestamp=None):
        self.patient_id = patient_id
        self.heart_rate = heart_rate
        self.spo2 = spo2
        self.temperature = temperature
        self.timestamp = timestamp or datetime.now()
    
    def save(self):
        return vitals.insert_one({
            'patient_id': self.patient_id,
            'heart_rate': self.heart_rate,
            'spo2': self.spo2,
            'temperature': self.temperature,
            'timestamp': self.timestamp
        })
    
    @staticmethod
    def get_latest(limit=50):
        return list(vitals.find().sort('timestamp', -1).limit(limit))
    
    @staticmethod
    def get_by_patient(patient_id):
        return list(vitals.find({'patient_id': patient_id}).sort('timestamp', 1))

class MongoAlert:
    def __init__(self, patient_id, anomaly, timestamp=None):
        self.patient_id = patient_id
        self.anomaly = anomaly
        self.timestamp = timestamp or datetime.now()
    
    def save(self):
        return alerts.insert_one({
            'patient_id': self.patient_id,
            'anomaly': self.anomaly,
            'timestamp': self.timestamp
        })
    
    @staticmethod
    def get_all():
        return list(alerts.find().sort('timestamp', -1))

class MongoStaff:
    def __init__(self, name, role, status='available'):
        self.name = name
        self.role = role
        self.status = status
        self.created_at = datetime.now()
    
    def save(self):
        return staff.insert_one({
            'name': self.name,
            'role': self.role,
            'status': self.status,
            'created_at': self.created_at
        })
    
    @staticmethod
    def get_available():
        return list(staff.find({'status': 'available'}))

class MongoAssignment:
    def __init__(self, patient_id, staff_id, assigned_at=None):
        self.patient_id = patient_id
        self.staff_id = staff_id
        self.assigned_at = assigned_at or datetime.now()
        self.resolved = False
    
    def save(self):
        return assignments.insert_one({
            'patient_id': self.patient_id,
            'staff_id': self.staff_id,
            'assigned_at': self.assigned_at,
            'resolved': self.resolved
        })
    
    @staticmethod
    def get_active():
        return list(assignments.find({'resolved': False}))

# Initialize database with sample data
def init_mongo_db():
    """Initialize MongoDB with sample data"""
    try:
        # Check if data already exists
        if patients.count_documents({}) == 0:
            # Add sample patients
            sample_patients = [
                {'name': 'John Smith', 'age': 45, 'gender': 'Male', 'condition': 'Cardiac'},
                {'name': 'Sarah Johnson', 'age': 32, 'gender': 'Female', 'condition': 'Respiratory'},
                {'name': 'Mike Davis', 'age': 58, 'gender': 'Male', 'condition': 'Diabetes'},
                {'name': 'Emily Wilson', 'age': 29, 'gender': 'Female', 'condition': 'Hypertension'},
                {'name': 'Robert Brown', 'age': 67, 'gender': 'Male', 'condition': 'Arthritis'}
            ]
            
            for patient_data in sample_patients:
                patients.insert_one({
                    **patient_data,
                    'created_at': datetime.now()
                })
            
            print("✅ MongoDB initialized with sample patients")
        
        # Add sample staff
        if staff.count_documents({}) == 0:
            sample_staff = [
                {'name': 'Dr. Alice Cooper', 'role': 'Cardiologist', 'status': 'available'},
                {'name': 'Dr. Bob Wilson', 'role': 'Pulmonologist', 'status': 'available'},
                {'name': 'Nurse Carol Davis', 'role': 'ICU Nurse', 'status': 'available'},
                {'name': 'Dr. David Miller', 'role': 'Emergency Physician', 'status': 'available'}
            ]
            
            for staff_data in sample_staff:
                staff.insert_one({
                    **staff_data,
                    'created_at': datetime.now()
                })
            
            print("✅ MongoDB initialized with sample staff")
            
    except Exception as e:
        print(f"❌ Error initializing MongoDB: {e}")

if __name__ == "__main__":
    init_mongo_db() 