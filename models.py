from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, create_engine
from sqlalchemy.orm import declarative_base, relationship, sessionmaker
from datetime import datetime

Base = declarative_base()

class Patient(Base):
    __tablename__ = 'patients'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    age = Column(Integer)
    gender = Column(String)
    condition = Column(String)

    vitals = relationship("Vital", back_populates="patient")
    alerts = relationship("Alert", back_populates="patient")


class Vital(Base):
    __tablename__ = 'vitals'
    id = Column(Integer, primary_key=True)
    patient_id = Column(Integer, ForeignKey('patients.id'))
    heart_rate = Column(Integer)
    spo2 = Column(Integer)
    temperature = Column(Float)
    timestamp = Column(DateTime, default=datetime.now)

    patient = relationship("Patient", back_populates="vitals")


class Alert(Base):
    __tablename__ = 'alerts'
    id = Column(Integer, primary_key=True)
    patient_id = Column(Integer, ForeignKey('patients.id'))
    anomaly = Column(String)
    timestamp = Column(DateTime, default=datetime.now)

    patient = relationship("Patient", back_populates="alerts")


# DB setup
engine = create_engine("sqlite:///health_data.db")
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
