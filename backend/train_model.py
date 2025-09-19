"""
Machine Learning Model Training for Rockfall Risk Prediction
"""

import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.model_selection import train_test_split
import joblib
import json
import os

class RockfallRiskModel:
    def __init__(self):
        self.model = RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            random_state=42
        )
        self.scaler = StandardScaler()
        self.label_encoder = LabelEncoder()
        self.feature_columns = [
            'displacement_mm', 'vibration_mm_s', 'temperature_c', 
            'humidity_percent', 'pressure_kpa', 'accelerometer_x',
            'accelerometer_y', 'accelerometer_z'
        ]
        
    def create_risk_labels(self, df):
        """Create risk labels based on thresholds"""
        def calculate_risk(row):
            # Load zone thresholds
            zones_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 
                                    'sample-data', 'zones.json')
            with open(zones_file, 'r') as f:
                zones_data = json.load(f)
            
            # Find zone thresholds
            zone_thresh = None
            for zone in zones_data['zones']:
                if zone['zone_id'] == row['zone_id']:
                    zone_thresh = zone['risk_thresholds']
                    break
            
            if zone_thresh is None:
                return 'low'
            
            # Calculate risk based on displacement and vibration
            displacement_risk = 0
            vibration_risk = 0
            
            if row['displacement_mm'] >= zone_thresh['displacement_critical']:
                displacement_risk = 3
            elif row['displacement_mm'] >= zone_thresh['displacement_warning']:
                displacement_risk = 2
            else:
                displacement_risk = 1
                
            if row['vibration_mm_s'] >= zone_thresh['vibration_critical']:
                vibration_risk = 3
            elif row['vibration_mm_s'] >= zone_thresh['vibration_warning']:
                vibration_risk = 2
            else:
                vibration_risk = 1
            
            # Combine risks
            total_risk = max(displacement_risk, vibration_risk)
            
            if total_risk >= 3:
                return 'critical'
            elif total_risk >= 2:
                return 'high'
            else:
                return 'low'
        
        df['risk_level'] = df.apply(calculate_risk, axis=1)
        return df
    
    def prepare_features(self, df):
        """Prepare features for training"""
        # Create additional features
        df['displacement_rate'] = df.groupby('zone_id')['displacement_mm'].diff().fillna(0)
        df['vibration_rate'] = df.groupby('zone_id')['vibration_mm_s'].diff().fillna(0)
        df['acceleration_magnitude'] = np.sqrt(
            df['accelerometer_x']**2 + 
            df['accelerometer_y']**2 + 
            df['accelerometer_z']**2
        )
        
        # Zone encoding
        df['zone_encoded'] = self.label_encoder.fit_transform(df['zone_id'])
        
        feature_cols = self.feature_columns + [
            'displacement_rate', 'vibration_rate', 
            'acceleration_magnitude', 'zone_encoded'
        ]
        
        return df[feature_cols]
    
    def train(self, data_file):
        """Train the model"""
        # Load data
        df = pd.read_csv(data_file)
        
        # Create risk labels
        df = self.create_risk_labels(df)
        
        # Prepare features
        X = self.prepare_features(df)
        y = df['risk_level']
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )
        
        # Scale features
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        # Train model
        self.model.fit(X_train_scaled, y_train)
        
        # Evaluate
        train_score = self.model.score(X_train_scaled, y_train)
        test_score = self.model.score(X_test_scaled, y_test)
        
        print(f"Training Accuracy: {train_score:.3f}")
        print(f"Testing Accuracy: {test_score:.3f}")
        
        return self.model
    
    def predict_risk(self, sensor_data):
        """Predict risk for new sensor data"""
        # Convert to DataFrame if it's a dictionary
        if isinstance(sensor_data, dict):
            df = pd.DataFrame([sensor_data])
        else:
            df = sensor_data.copy()
        
        # Prepare features
        X = self.prepare_features(df)
        
        # Scale features
        X_scaled = self.scaler.transform(X)
        
        # Predict
        risk_proba = self.model.predict_proba(X_scaled)
        risk_pred = self.model.predict(X_scaled)
        
        return {
            'risk_level': risk_pred[0],
            'risk_probabilities': {
                label: prob for label, prob in 
                zip(self.model.classes_, risk_proba[0])
            },
            'risk_score': np.max(risk_proba[0]) * 10  # Scale to 0-10
        }
    
    def save_model(self, filepath):
        """Save the trained model"""
        model_data = {
            'model': self.model,
            'scaler': self.scaler,
            'label_encoder': self.label_encoder,
            'feature_columns': self.feature_columns
        }
        joblib.dump(model_data, filepath)
        print(f"Model saved to {filepath}")
    
    def load_model(self, filepath):
        """Load a trained model"""
        model_data = joblib.load(filepath)
        self.model = model_data['model']
        self.scaler = model_data['scaler']
        self.label_encoder = model_data['label_encoder']
        self.feature_columns = model_data['feature_columns']
        print(f"Model loaded from {filepath}")

def train_and_save_model():
    """Train and save the model"""
    # Get the path to the data file
    current_dir = os.path.dirname(__file__)
    data_file = os.path.join(os.path.dirname(current_dir), 'sample-data', 'demo_sensor.csv')
    model_file = os.path.join(current_dir, 'ml_model.pkl')
    
    # Create and train model
    model = RockfallRiskModel()
    model.train(data_file)
    
    # Save model
    model.save_model(model_file)
    
    return model

if __name__ == "__main__":
    train_and_save_model()