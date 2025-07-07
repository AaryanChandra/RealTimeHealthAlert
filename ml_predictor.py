import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier, IsolationForest
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix
import joblib
import sqlite3
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

class PatientRiskPredictor:
    def __init__(self):
        self.model = None
        self.scaler = StandardScaler()
        self.isolation_forest = IsolationForest(contamination=0.1, random_state=42)
        self.model_path = 'patient_risk_model.pkl'
        self.scaler_path = 'patient_scaler.pkl'
        self.anomaly_model_path = 'anomaly_model.pkl'
        
    def create_features(self, vitals_data):
        """Create features from vital signs for ML model"""
        features = []
        
        for patient_vitals in vitals_data:
            if len(patient_vitals) < 5:  # Need minimum data points
                continue
                
            # Recent vitals (last 5 readings)
            recent = patient_vitals[-5:]
            
            # Statistical features
            hr_mean = np.mean([v['heart_rate'] for v in recent])
            hr_std = np.std([v['heart_rate'] for v in recent])
            hr_trend = recent[-1]['heart_rate'] - recent[0]['heart_rate']
            
            spo2_mean = np.mean([v['spo2'] for v in recent])
            spo2_std = np.std([v['spo2'] for v in recent])
            spo2_trend = recent[-1]['spo2'] - recent[0]['spo2']
            
            temp_mean = np.mean([v['temperature'] for v in recent])
            temp_std = np.std([v['temperature'] for v in recent])
            temp_trend = recent[-1]['temperature'] - recent[0]['temperature']
            
            # Risk indicators
            hr_high = 1 if hr_mean > 120 else 0
            hr_low = 1 if hr_mean < 60 else 0
            spo2_low = 1 if spo2_mean < 92 else 0
            temp_high = 1 if temp_mean > 38 else 0
            
            # Combined risk score
            risk_score = (hr_high + hr_low + spo2_low + temp_high) / 4
            
            features.append({
                'hr_mean': hr_mean,
                'hr_std': hr_std,
                'hr_trend': hr_trend,
                'spo2_mean': spo2_mean,
                'spo2_std': spo2_std,
                'spo2_trend': spo2_trend,
                'temp_mean': temp_mean,
                'temp_std': temp_std,
                'temp_trend': temp_trend,
                'hr_high': hr_high,
                'hr_low': hr_low,
                'spo2_low': spo2_low,
                'temp_high': temp_high,
                'risk_score': risk_score
            })
            
        return pd.DataFrame(features)
    
    def create_labels(self, vitals_data):
        """Create labels for training (1 = critical, 0 = normal)"""
        labels = []
        
        for patient_vitals in vitals_data:
            if len(patient_vitals) < 5:
                continue
                
            # Check if patient has critical vitals
            recent = patient_vitals[-3:]  # Last 3 readings
            critical_count = 0
            
            for vital in recent:
                if (vital['heart_rate'] > 140 or vital['heart_rate'] < 50 or 
                    vital['spo2'] < 90 or vital['temperature'] > 39):
                    critical_count += 1
            
            # Label as critical if 2+ critical readings
            label = 1 if critical_count >= 2 else 0
            labels.append(label)
            
        return np.array(labels)
    
    def train_model(self, vitals_data):
        """Train the predictive model"""
        print("🔬 Training predictive model...")
        
        # Create features and labels
        features_df = self.create_features(vitals_data)
        labels = self.create_labels(vitals_data)
        
        if len(features_df) < 10:
            print("⚠️ Not enough data to train model. Need at least 10 patients.")
            return False
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            features_df, labels, test_size=0.2, random_state=42
        )
        
        # Scale features
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        # Train Random Forest
        self.model = RandomForestClassifier(
            n_estimators=100, 
            max_depth=10, 
            random_state=42
        )
        self.model.fit(X_train_scaled, y_train)
        
        # Train anomaly detection
        self.isolation_forest.fit(X_train_scaled)
        
        # Evaluate model
        y_pred = self.model.predict(X_test_scaled)
        accuracy = self.model.score(X_test_scaled, y_test)
        
        print(f"✅ Model trained successfully!")
        print(f"📊 Accuracy: {accuracy:.2%}")
        print(f"📈 Feature importance:")
        
        feature_importance = pd.DataFrame({
            'feature': features_df.columns,
            'importance': self.model.feature_importances_
        }).sort_values('importance', ascending=False)
        
        for _, row in feature_importance.head(5).iterrows():
            print(f"   {row['feature']}: {row['importance']:.3f}")
        
        # Save models
        joblib.dump(self.model, self.model_path)
        joblib.dump(self.scaler, self.scaler_path)
        joblib.dump(self.isolation_forest, self.anomaly_model_path)
        
        return True
    
    def predict_risk(self, patient_vitals):
        """Predict risk for a single patient"""
        if self.model is None:
            try:
                self.model = joblib.load(self.model_path)
                self.scaler = joblib.load(self.scaler_path)
                self.isolation_forest = joblib.load(self.anomaly_model_path)
            except:
                return {"risk_level": "Unknown", "confidence": 0, "anomaly_score": 0}
        
        # Create features for this patient
        features_df = self.create_features([patient_vitals])
        if len(features_df) == 0:
            return {"risk_level": "Unknown", "confidence": 0, "anomaly_score": 0}
        
        # Scale features
        features_scaled = self.scaler.transform(features_df)
        
        # Predict risk
        risk_prob = self.model.predict_proba(features_scaled)[0]
        risk_prediction = self.model.predict(features_scaled)[0]
        
        # Anomaly detection
        anomaly_score = self.isolation_forest.decision_function(features_scaled)[0]
        is_anomaly = self.isolation_forest.predict(features_scaled)[0] == -1
        
        # Determine risk level
        if risk_prediction == 1:
            risk_level = "High Risk"
        elif is_anomaly:
            risk_level = "Anomaly Detected"
        else:
            risk_level = "Low Risk"
        
        confidence = max(risk_prob)
        
        return {
            "risk_level": risk_level,
            "confidence": confidence,
            "anomaly_score": anomaly_score,
            "risk_probability": risk_prob[1] if len(risk_prob) > 1 else 0,
            "is_anomaly": is_anomaly
        }
    
    def get_patient_insights(self, patient_vitals):
        """Get detailed insights for a patient"""
        if len(patient_vitals) < 3:
            return {"insights": "Insufficient data for analysis"}
        
        recent = patient_vitals[-5:]
        
        insights = {
            "trends": {},
            "alerts": [],
            "recommendations": []
        }
        
        # Analyze trends
        hr_values = [v['heart_rate'] for v in recent]
        spo2_values = [v['spo2'] for v in recent]
        temp_values = [v['temperature'] for v in recent]
        
        # Heart rate analysis
        hr_trend = "increasing" if hr_values[-1] > hr_values[0] else "decreasing"
        if hr_values[-1] > 120:
            insights["alerts"].append("Elevated heart rate detected")
        elif hr_values[-1] < 60:
            insights["alerts"].append("Low heart rate detected")
        
        # SpO2 analysis
        if spo2_values[-1] < 92:
            insights["alerts"].append("Low oxygen saturation")
        
        # Temperature analysis
        if temp_values[-1] > 38:
            insights["alerts"].append("Elevated temperature")
        
        # Recommendations
        if len(insights["alerts"]) > 0:
            insights["recommendations"].append("Consider immediate medical attention")
        elif hr_trend == "increasing" and hr_values[-1] > 100:
            insights["recommendations"].append("Monitor heart rate closely")
        
        insights["trends"] = {
            "heart_rate": hr_trend,
            "spo2": "stable" if abs(spo2_values[-1] - spo2_values[0]) < 2 else "variable",
            "temperature": "stable" if abs(temp_values[-1] - temp_values[0]) < 0.5 else "variable"
        }
        
        return insights

# Initialize predictor
predictor = PatientRiskPredictor() 