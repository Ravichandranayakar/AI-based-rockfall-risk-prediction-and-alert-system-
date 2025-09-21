"""
Simple Flask Backend for Demo - No ML Dependencies
"""
from flask import Flask, jsonify
from flask_cors import CORS
from datetime import datetime
import json
import time

app = Flask(__name__)
CORS(app)

# Simple mock zones data
def get_zones_data():
    # Rotate scenarios every 20 seconds
    current_time = int(time.time())
    scenario = (current_time // 20) % 4
    
    scenarios = [
        # Scenario 1: All safe
        [
            {"zone_id": 1, "zone_name": "North Pit Wall", "risk_level": "LOW", "risk_score": 2.1},
            {"zone_id": 2, "zone_name": "South Slope", "risk_level": "LOW", "risk_score": 1.8},
            {"zone_id": 3, "zone_name": "East Bench", "risk_level": "LOW", "risk_score": 2.3},
            {"zone_id": 4, "zone_name": "West Highwall", "risk_level": "LOW", "risk_score": 1.9}
        ],
        # Scenario 2: Warning
        [
            {"zone_id": 1, "zone_name": "North Pit Wall", "risk_level": "WARNING", "risk_score": 5.2},
            {"zone_id": 2, "zone_name": "South Slope", "risk_level": "LOW", "risk_score": 1.8},
            {"zone_id": 3, "zone_name": "East Bench", "risk_level": "LOW", "risk_score": 2.3},
            {"zone_id": 4, "zone_name": "West Highwall", "risk_level": "LOW", "risk_score": 1.9}
        ],
        # Scenario 3: Critical
        [
            {"zone_id": 1, "zone_name": "North Pit Wall", "risk_level": "LOW", "risk_score": 2.1},
            {"zone_id": 2, "zone_name": "South Slope", "risk_level": "CRITICAL", "risk_score": 8.5},
            {"zone_id": 3, "zone_name": "East Bench", "risk_level": "WARNING", "risk_score": 4.8},
            {"zone_id": 4, "zone_name": "West Highwall", "risk_level": "LOW", "risk_score": 1.9}
        ],
        # Scenario 4: Multiple warnings
        [
            {"zone_id": 1, "zone_name": "North Pit Wall", "risk_level": "WARNING", "risk_score": 6.1},
            {"zone_id": 2, "zone_name": "South Slope", "risk_level": "LOW", "risk_score": 1.8},
            {"zone_id": 3, "zone_name": "East Bench", "risk_level": "WARNING", "risk_score": 5.3},
            {"zone_id": 4, "zone_name": "West Highwall", "risk_level": "WARNING", "risk_score": 4.7}
        ]
    ]
    
    return scenarios[scenario]

@app.route('/')
def home():
    return jsonify({
        'status': 'active',
        'message': 'AI Rockfall System - Simple Demo Backend',
        'version': '1.0'
    })

@app.route('/zones')
def get_zones():
    zones = get_zones_data()
    enhanced_zones = []
    
    for zone in zones:
        enhanced_zone = {
            'zone_id': zone['zone_id'],
            'zone_name': zone['zone_name'],
            'risk_level': zone['risk_level'],
            'risk_score': zone['risk_score'],
            'last_updated': datetime.now().isoformat(),
            'sensors_active': True,
            'location': {
                'x': 50 + (zone['zone_id'] * 20),
                'y': 50 + (zone['zone_id'] * 15)
            }
        }
        enhanced_zones.append(enhanced_zone)
    
    return jsonify({
        'zones': enhanced_zones,
        'total_zones': len(enhanced_zones),
        'last_updated': datetime.now().isoformat()
    })

@app.route('/alerts')
def get_alerts():
    zones = get_zones_data()
    alerts = []
    
    for zone in zones:
        if zone['risk_level'] in ['WARNING', 'CRITICAL']:
            alert = {
                'alert_id': f"ALERT_{zone['zone_id']}_{int(datetime.now().timestamp())}",
                'zone_id': zone['zone_id'],
                'zone_name': zone['zone_name'],
                'alert_level': zone['risk_level'],
                'risk_score': zone['risk_score'],
                'timestamp': datetime.now().isoformat(),
                'status': 'ACTIVE',
                'message': f"{zone['zone_name']} shows {zone['risk_level'].lower()} risk conditions",
                'recommended_action': (
                    'Immediate evacuation required - rockfall imminent' 
                    if zone['risk_level'] == 'CRITICAL' 
                    else 'Increase monitoring - restrict access to non-essential personnel'
                )
            }
            alerts.append(alert)
    
    return jsonify({
        'alerts': alerts,
        'total_alerts': len(alerts),
        'last_updated': datetime.now().isoformat()
    })

@app.route('/health')
def health_check():
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat()
    })

if __name__ == '__main__':
    print("🚀 Starting AI Rockfall System - Simple Backend")
    print("🌐 Backend will be available at: http://localhost:5000")
    print("📊 Serving dynamic demo data with 20-second scenario rotation")
    
    app.run(host='0.0.0.0', port=5000, debug=False)