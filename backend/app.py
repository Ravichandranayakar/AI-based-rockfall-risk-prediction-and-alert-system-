"""
Flask REST API Backend for Rockfall Risk Prediction System
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
import numpy as np
import joblib
import json
import os
from datetime import datetime
import logging

app = Flask(__name__)
CORS(app)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RockfallAPI:
    def __init__(self):
        self.model = None
        self.scaler = None
        self.label_encoder = None
        self.feature_columns = None
        self.zones_data = None
        self.load_model()
        self.load_zones()
    
    def load_model(self):
        """Load the trained ML model"""
        try:
            model_path = os.path.join(os.path.dirname(__file__), 'ml_model.pkl')
            if os.path.exists(model_path):
                model_data = joblib.load(model_path)
                self.model = model_data['model']
                self.scaler = model_data['scaler']
                self.label_encoder = model_data['label_encoder']
                self.feature_columns = model_data['feature_columns']
                logger.info("Model loaded successfully")
            else:
                logger.warning("Model file not found, using dummy predictions")
        except Exception as e:
            logger.error(f"Error loading model: {e}")
    
    def load_zones(self):
        """Load zone configuration"""
        try:
            zones_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 
                                    'sample-data', 'zones.json')
            with open(zones_path, 'r') as f:
                self.zones_data = json.load(f)
            logger.info("Zones data loaded successfully")
        except Exception as e:
            logger.error(f"Error loading zones data: {e}")
    
    def prepare_features(self, df):
        """Prepare features for prediction"""
        try:
            # Create additional features
            df['displacement_rate'] = 0  # For single prediction, assume no change
            df['vibration_rate'] = 0
            df['acceleration_magnitude'] = np.sqrt(
                df['accelerometer_x']**2 + 
                df['accelerometer_y']**2 + 
                df['accelerometer_z']**2
            )
            
            # Zone encoding
            if self.label_encoder is not None:
                try:
                    df['zone_encoded'] = self.label_encoder.transform(df['zone_id'])
                except:
                    # If zone not in training data, use a default value
                    df['zone_encoded'] = 0
            else:
                df['zone_encoded'] = 0
            
            feature_cols = self.feature_columns + [
                'displacement_rate', 'vibration_rate', 
                'acceleration_magnitude', 'zone_encoded'
            ]
            
            return df[feature_cols]
        except Exception as e:
            logger.error(f"Error preparing features: {e}")
            return None
    
    def predict_risk(self, sensor_data):
        """Predict risk level for sensor data"""
        try:
            if self.model is None:
                # Dummy prediction if model not loaded
                return self.dummy_prediction(sensor_data)
            
            # Convert to DataFrame
            if isinstance(sensor_data, dict):
                df = pd.DataFrame([sensor_data])
            else:
                df = sensor_data.copy()
            
            # Prepare features
            X = self.prepare_features(df)
            if X is None:
                return self.dummy_prediction(sensor_data)
            
            # Scale features
            X_scaled = self.scaler.transform(X)
            
            # Predict
            risk_proba = self.model.predict_proba(X_scaled)
            risk_pred = self.model.predict(X_scaled)
            
            # Calculate risk score (0-10 scale)
            risk_score = np.max(risk_proba[0]) * 10
            
            return {
                'risk_level': risk_pred[0],
                'risk_score': float(risk_score),
                'risk_probabilities': {
                    label: float(prob) for label, prob in 
                    zip(self.model.classes_, risk_proba[0])
                }
            }
        except Exception as e:
            logger.error(f"Error in prediction: {e}")
            return self.dummy_prediction(sensor_data)
    
    def dummy_prediction(self, sensor_data):
        """Dummy prediction when model is not available"""
        # Simple rule-based prediction
        displacement = sensor_data.get('displacement_mm', 0)
        vibration = sensor_data.get('vibration_mm_s', 0)
        zone_id = sensor_data.get('zone_id', 'A')
        
        # Default thresholds (more sensitive for demonstration)
        thresholds = {
            'displacement_warning': 5, 
            'displacement_critical': 8,
            'vibration_warning': 1.5, 
            'vibration_critical': 2.5
        }
        
        # Try to get zone-specific thresholds
        if self.zones_data and 'zones' in self.zones_data:
            for zone in self.zones_data['zones']:
                if zone.get('zone_id') == zone_id and 'risk_thresholds' in zone:
                    thresholds.update(zone['risk_thresholds'])
                    break
        
        logger.info(f"Zone {zone_id}: displacement={displacement}, vibration={vibration}")
        logger.info(f"Thresholds: {thresholds}")
        
        # Calculate risk with explicit logging
        is_critical = (displacement >= thresholds['displacement_critical'] or 
                      vibration >= thresholds['vibration_critical'])
        is_warning = (displacement >= thresholds['displacement_warning'] or 
                     vibration >= thresholds['vibration_warning'])
        
        if is_critical:
            risk_level = 'critical'
            risk_score = min(10.0, 7.0 + (displacement / 10.0) + (vibration / 2.0))
            logger.warning(f"CRITICAL RISK DETECTED: Zone {zone_id}, Score {risk_score}")
        elif is_warning:
            risk_level = 'high'
            risk_score = min(8.0, 5.0 + (displacement / 10.0) + (vibration / 2.0))
            logger.warning(f"HIGH RISK DETECTED: Zone {zone_id}, Score {risk_score}")
        else:
            risk_level = 'low'
            risk_score = min(5.0, 1.0 + (displacement / 10.0) + (vibration / 2.0))
        
        result = {
            'risk_level': risk_level,
            'risk_score': float(risk_score),
            'risk_probabilities': {
                'low': 0.8 if risk_level == 'low' else 0.1,
                'high': 0.8 if risk_level == 'high' else 0.1,
                'critical': 0.8 if risk_level == 'critical' else 0.1
            }
        }
        
        logger.info(f"Prediction result: {result}")
        return result

# Initialize API
api = RockfallAPI()

@app.route('/', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'Rockfall Risk Prediction API',
        'timestamp': datetime.now().isoformat(),
        'model_loaded': api.model is not None
    })

@app.route('/predict', methods=['POST'])
def predict():
    """Predict risk for sensor data"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Validate required fields
        required_fields = ['zone_id', 'displacement_mm', 'vibration_mm_s']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Set default values for optional fields
        sensor_data = {
            'zone_id': data['zone_id'],
            'displacement_mm': float(data['displacement_mm']),
            'vibration_mm_s': float(data['vibration_mm_s']),
            'temperature_c': float(data.get('temperature_c', 22.0)),
            'humidity_percent': float(data.get('humidity_percent', 60.0)),
            'pressure_kpa': float(data.get('pressure_kpa', 101.3)),
            'accelerometer_x': float(data.get('accelerometer_x', 0.1)),
            'accelerometer_y': float(data.get('accelerometer_y', 0.1)),
            'accelerometer_z': float(data.get('accelerometer_z', 9.8))
        }
        
        # Get prediction
        prediction = api.predict_risk(sensor_data)
        
        # Add recommendation
        recommendation = get_recommendation(prediction['risk_level'], 
                                          prediction['risk_score'])
        
        result = {
            'zone_id': data['zone_id'],
            'timestamp': datetime.now().isoformat(),
            'prediction': prediction,
            'recommendation': recommendation
        }
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error in predict endpoint: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/predict/batch', methods=['POST'])
def predict_batch():
    """Predict risk for multiple sensor readings"""
    try:
        data = request.get_json()
        
        if not data or 'sensors' not in data:
            return jsonify({'error': 'No sensor data provided'}), 400
        
        results = []
        for sensor_data in data['sensors']:
            try:
                prediction = api.predict_risk(sensor_data)
                recommendation = get_recommendation(prediction['risk_level'], 
                                                  prediction['risk_score'])
                
                result = {
                    'zone_id': sensor_data.get('zone_id'),
                    'prediction': prediction,
                    'recommendation': recommendation
                }
                results.append(result)
            except Exception as e:
                logger.error(f"Error processing sensor {sensor_data}: {e}")
                continue
        
        return jsonify({
            'timestamp': datetime.now().isoformat(),
            'results': results
        })
        
    except Exception as e:
        logger.error(f"Error in batch predict endpoint: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/zones', methods=['GET'])
def get_zones():
    """Get all zone information"""
    try:
        if api.zones_data:
            return jsonify(api.zones_data)
        else:
            return jsonify({'error': 'Zones data not available'}), 500
    except Exception as e:
        logger.error(f"Error in zones endpoint: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/zones/<zone_id>', methods=['GET'])
def get_zone(zone_id):
    """Get specific zone information"""
    try:
        if not api.zones_data:
            return jsonify({'error': 'Zones data not available'}), 500
        
        for zone in api.zones_data['zones']:
            if zone['zone_id'] == zone_id:
                return jsonify(zone)
        
        return jsonify({'error': 'Zone not found'}), 404
        
    except Exception as e:
        logger.error(f"Error in zone endpoint: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/alerts', methods=['GET'])
def get_alerts():
    """Get alert history"""
    try:
        alerts_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 
                                 'sample-data', 'fake_alerts.csv')
        
        if os.path.exists(alerts_path):
            df = pd.read_csv(alerts_path)
            # Convert to list of dictionaries
            alerts = df.to_dict('records')
            return jsonify({'alerts': alerts})
        else:
            return jsonify({'alerts': []})
            
    except Exception as e:
        logger.error(f"Error in alerts endpoint: {e}")
        return jsonify({'error': str(e)}), 500

def get_recommendation(risk_level, risk_score):
    """Get recommendation based on risk level"""
    if risk_level == 'critical':
        return {
            'action': 'IMMEDIATE_EVACUATION',
            'message': 'Critical risk detected. Immediate evacuation required.',
            'priority': 'HIGH',
            'color': 'red'
        }
    elif risk_level == 'high':
        return {
            'action': 'INCREASED_MONITORING',
            'message': 'High risk detected. Increase monitoring and restrict access.',
            'priority': 'MEDIUM',
            'color': 'orange'
        }
    else:
        return {
            'action': 'NORMAL_OPERATIONS',
            'message': 'Low risk. Continue normal operations with routine monitoring.',
            'priority': 'LOW',
            'color': 'green'
        }

if __name__ == '__main__':
    # Train model if it doesn't exist
    model_path = os.path.join(os.path.dirname(__file__), 'ml_model.pkl')
    if not os.path.exists(model_path):
        logger.info("Training model...")
        try:
            from train_model import train_and_save_model
            train_and_save_model()
            # Reload API with new model
            api = RockfallAPI()
        except Exception as e:
            logger.error(f"Error training model: {e}")
    
    app.run(debug=True, host='0.0.0.0', port=5000)