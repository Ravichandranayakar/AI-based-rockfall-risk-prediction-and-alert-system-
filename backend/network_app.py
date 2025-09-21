"""
Flask REST API Backend for Rockfall Risk Prediction System - NETWORK MODE
Accessible from other devices on the same network
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
# Enable CORS for all domains (for network access)
CORS(app, origins=['*'])

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
            model_path = 'ml_model.pkl'
            if os.path.exists(model_path):
                model_data = joblib.load(model_path)
                self.model = model_data.get('model')
                self.scaler = model_data.get('scaler')
                self.label_encoder = model_data.get('label_encoder')
                self.feature_columns = model_data.get('feature_columns')
                logger.info("✅ ML model loaded successfully")
            else:
                logger.warning("⚠️ ML model file not found, using mock predictions")
        except Exception as e:
            logger.error(f"❌ Error loading model: {e}")
            self.model = None

    def load_zones(self):
        """Load zone configuration"""
        try:
            zones_file = '../sample-data/zones.json'
            if os.path.exists(zones_file):
                with open(zones_file, 'r') as f:
                    self.zones_data = json.load(f)
            else:
                # Fallback zone data
                self.zones_data = self.get_default_zones()
            logger.info(f"✅ Loaded {len(self.zones_data)} zones")
        except Exception as e:
            logger.error(f"❌ Error loading zones: {e}")
            self.zones_data = self.get_default_zones()

    def get_default_zones(self):
        """Default zone configuration with dynamic risk scenarios"""
        import time
        
        # Get current time for dynamic scenarios
        current_minute = int(time.time() / 20) % 4  # Change every 20 seconds, 4 scenarios
        
        scenarios = [
            # Scenario 1: Normal operations
            [
                {"zone_id": 1, "name": "North Pit Wall", "risk_level": "LOW", "risk_score": 2.1},
                {"zone_id": 2, "name": "South Slope", "risk_level": "LOW", "risk_score": 1.8},
                {"zone_id": 3, "name": "East Bench", "risk_level": "WARNING", "risk_score": 4.2},
                {"zone_id": 4, "name": "West Highwall", "risk_level": "LOW", "risk_score": 2.5}
            ],
            # Scenario 2: Warning in North
            [
                {"zone_id": 1, "name": "North Pit Wall", "risk_level": "WARNING", "risk_score": 5.3},
                {"zone_id": 2, "name": "South Slope", "risk_level": "LOW", "risk_score": 1.9},
                {"zone_id": 3, "name": "East Bench", "risk_level": "LOW", "risk_score": 2.1},
                {"zone_id": 4, "name": "West Highwall", "risk_level": "LOW", "risk_score": 2.8}
            ],
            # Scenario 3: Critical in South
            [
                {"zone_id": 1, "name": "North Pit Wall", "risk_level": "LOW", "risk_score": 2.3},
                {"zone_id": 2, "name": "South Slope", "risk_level": "CRITICAL", "risk_score": 7.8},
                {"zone_id": 3, "name": "East Bench", "risk_level": "WARNING", "risk_score": 4.8},
                {"zone_id": 4, "name": "West Highwall", "risk_level": "LOW", "risk_score": 1.9}
            ],
            # Scenario 4: Multiple warnings
            [
                {"zone_id": 1, "name": "North Pit Wall", "risk_level": "WARNING", "risk_score": 5.8},
                {"zone_id": 2, "name": "South Slope", "risk_level": "LOW", "risk_score": 2.2},
                {"zone_id": 3, "name": "East Bench", "risk_level": "WARNING", "risk_score": 6.1},
                {"zone_id": 4, "name": "West Highwall", "risk_level": "WARNING", "risk_score": 4.9}
            ]
        ]
        
        return scenarios[current_minute]

# Initialize API
api = RockfallAPI()

@app.route('/')
def home():
    """API status endpoint"""
    return jsonify({
        'status': 'active',
        'message': 'Rockfall Risk Prediction API - Network Mode',
        'version': '2.0',
        'network_access': True,
        'endpoints': ['/zones', '/alerts', '/predict']
    })

@app.route('/zones')
def get_zones():
    """Get current zone data with dynamic scenarios"""
    try:
        # Reload zones for dynamic updates
        api.load_zones()
        zones = api.zones_data or []
        
        # Add additional properties for each zone
        enhanced_zones = []
        for zone in zones:
            enhanced_zone = {
                'zone_id': zone.get('zone_id'),
                'zone_name': zone.get('name'),
                'risk_level': zone.get('risk_level', 'LOW'),
                'risk_score': zone.get('risk_score', 0),
                'last_updated': datetime.now().isoformat(),
                'sensors_active': True,
                'location': {
                    'x': 50 + (zone.get('zone_id', 1) * 20),
                    'y': 50 + (zone.get('zone_id', 1) * 15)
                }
            }
            enhanced_zones.append(enhanced_zone)
        
        return jsonify({
            'zones': enhanced_zones,
            'total_zones': len(enhanced_zones),
            'last_updated': datetime.now().isoformat(),
            'network_mode': True
        })
        
    except Exception as e:
        logger.error(f"❌ Error getting zones: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/alerts')
def get_alerts():
    """Get current alerts based on zone risk levels"""
    try:
        api.load_zones()
        zones = api.zones_data or []
        alerts = []
        
        for zone in zones:
            risk_level = zone.get('risk_level', 'LOW')
            risk_score = zone.get('risk_score', 0)
            
            if risk_level in ['WARNING', 'CRITICAL']:
                alert = {
                    'alert_id': f"ALERT_{zone.get('zone_id', 1)}_{int(datetime.now().timestamp())}",
                    'zone_id': zone.get('zone_id'),
                    'zone_name': zone.get('name'),
                    'alert_level': risk_level,
                    'risk_score': risk_score,
                    'timestamp': datetime.now().isoformat(),
                    'status': 'ACTIVE',
                    'message': f"{zone.get('name')} shows {risk_level.lower()} risk conditions",
                    'recommended_action': (
                        'Immediate evacuation required - rockfall imminent' 
                        if risk_level == 'CRITICAL' 
                        else 'Increase monitoring - restrict access to non-essential personnel'
                    )
                }
                alerts.append(alert)
        
        return jsonify({
            'alerts': alerts,
            'total_alerts': len(alerts),
            'last_updated': datetime.now().isoformat(),
            'network_mode': True
        })
        
    except Exception as e:
        logger.error(f"❌ Error getting alerts: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/predict', methods=['POST'])
def predict_risk():
    """Predict rockfall risk for given sensor data"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Mock prediction since this is for demo
        risk_score = np.random.uniform(0, 10)
        
        if risk_score < 3:
            risk_level = 'LOW'
        elif risk_score < 6:
            risk_level = 'WARNING'  
        else:
            risk_level = 'CRITICAL'
        
        prediction = {
            'risk_score': round(risk_score, 2),
            'risk_level': risk_level,
            'confidence': round(np.random.uniform(0.8, 0.98), 3),
            'timestamp': datetime.now().isoformat(),
            'network_mode': True
        }
        
        return jsonify(prediction)
        
    except Exception as e:
        logger.error(f"❌ Error in prediction: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'network_mode': True,
        'timestamp': datetime.now().isoformat()
    })

if __name__ == '__main__':
    print("🌐 Starting Rockfall API in NETWORK MODE...")
    print("📱 Accessible from other devices on same WiFi")
    print("🔧 Backend will be available at: http://10.129.21.66:5000")
    print("🚀 Starting server...")
    
    # Run with network access - accessible from other devices
    app.run(
        host='0.0.0.0',  # Listen on all network interfaces
        port=5000,
        debug=True,
        use_reloader=False  # Disable reloader for stability
    )