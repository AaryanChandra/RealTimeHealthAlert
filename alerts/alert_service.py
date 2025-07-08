from models import Session, Staff, PatientAssignment
from datetime import datetime

def assign_staff_to_patient(patient_id):
    session = Session()
    # Find available staff (prefer doctors, then nurses)
    staff = session.query(Staff).filter(Staff.status == 'available').order_by(Staff.role).first()
    if staff:
        # Create assignment
        assignment = PatientAssignment(patient_id=patient_id, staff_id=staff.id, assigned_at=datetime.now())
        session.add(assignment)
        # Set staff to busy
        staff.status = 'busy'
        session.commit()
        print(f"[ASSIGNMENT] {staff.role} {staff.name} assigned to Patient {patient_id}")
        return staff.name, staff.role
    else:
        print(f"[ASSIGNMENT] No available staff for Patient {patient_id}")
        return None, None

def trigger_alert(patient_id, anomalies, timestamp):
    print(f"[ALERT] Patient {patient_id} has issues: {', '.join(anomalies)} at {timestamp}")
    staff_name, staff_role = assign_staff_to_patient(patient_id)
    if staff_name:
        print(f"[ALERT] {staff_role} {staff_name} assigned to Patient {patient_id}")
    else:
        print(f"[ALERT] No staff available for Patient {patient_id}")
