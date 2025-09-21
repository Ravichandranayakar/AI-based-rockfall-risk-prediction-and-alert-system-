"""
Simplified Flask Backend for Audio Alert Testing
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import os
from datetime import datetime
import logging

app = Flask(__name__)
CORS(app)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.route('/', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'Rockfall Risk Prediction API (Audio Test)',
        'timestamp': datetime.now().isoformat()
    })

@app.route('/predict', methods=['POST'])
def predict():
    """Predict risk for sensor data - optimized for audio alert testing"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Get sensor readings
        displacement = float(data.get('displacement_mm', 0))
        vibration = float(data.get('vibration_mm_s', 0))
        zone_id = data.get('zone_id', 'A')
        
        logger.info(f"Testing Zone {zone_id}: displacement={displacement}mm, vibration={vibration}mm/s")
        
        # Audio alert thresholds (optimized for testing)
        thresholds = {
            'displacement_warning': 5.0,
            'displacement_critical': 8.0,
            'vibration_warning': 1.5,
            'vibration_critical': 2.5
        }
        
        # Determine risk level
        is_critical = (displacement >= thresholds['displacement_critical'] or 
                      vibration >= thresholds['vibration_critical'])
        is_warning = (displacement >= thresholds['displacement_warning'] or 
                     vibration >= thresholds['vibration_warning'])
        
        if is_critical:
            risk_level = 'critical'
            risk_score = min(10.0, 7.0 + (displacement * 0.1) + (vibration * 0.5))
            action = 'IMMEDIATE_EVACUATION'
            message = 'Critical risk detected. Immediate evacuation required.'
            color = 'red'
            logger.warning(f"🚨 CRITICAL ALERT: Zone {zone_id} - Score {risk_score:.1f}")
        elif is_warning:
            risk_level = 'high'
            risk_score = min(8.0, 4.0 + (displacement * 0.1) + (vibration * 0.5))
            action = 'INCREASED_MONITORING'
            message = 'High risk detected. Increase monitoring and restrict access.'
            color = 'orange'
            logger.warning(f"⚠️ WARNING ALERT: Zone {zone_id} - Score {risk_score:.1f}")
        else:
            risk_level = 'low'
            risk_score = max(1.0, (displacement * 0.05) + (vibration * 0.2))
            action = 'NORMAL_OPERATIONS'
            message = 'Low risk. Continue normal operations with routine monitoring.'
            color = 'green'
            logger.info(f"🟢 SAFE: Zone {zone_id} - Score {risk_score:.1f}")
        
        result = {
            'zone_id': zone_id,
            'timestamp': datetime.now().isoformat(),
            'prediction': {
                'risk_level': risk_level,
                'risk_score': float(risk_score),
                'risk_probabilities': {
                    'low': 0.8 if risk_level == 'low' else 0.1,
                    'high': 0.8 if risk_level == 'high' else 0.1,
                    'critical': 0.8 if risk_level == 'critical' else 0.1
                }
            },
            'recommendation': {
                'action': action,
                'message': message,
                'color': color,
                'priority': 'HIGH' if is_critical else 'MEDIUM' if is_warning else 'LOW'
            },
            'audio_alert': {
                'should_play': is_critical or is_warning,
                'alert_type': 'critical' if is_critical else 'warning' if is_warning else 'none',
                'frequency': 'continuous' if is_critical else 'periodic' if is_warning else 'none'
            }
        }
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error in predict endpoint: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/test-critical', methods=['GET'])
def test_critical():
    """Generate test data for critical audio alert"""
    return jsonify({
        'zone_id': 'TEST',
        'timestamp': datetime.now().isoformat(),
        'prediction': {
            'risk_level': 'critical',
            'risk_score': 9.5,
            'risk_probabilities': {'low': 0.1, 'high': 0.1, 'critical': 0.8}
        },
        'recommendation': {
            'action': 'IMMEDIATE_EVACUATION',
            'message': 'Test critical alert - Audio alarm should sound!',
            'color': 'red',
            'priority': 'HIGH'
        },
        'audio_alert': {
            'should_play': True,
            'alert_type': 'critical',
            'frequency': 'continuous'
        }
    })

@app.route('/test-warning', methods=['GET'])
def test_warning():
    """Generate test data for warning audio alert"""
    return jsonify({
        'zone_id': 'TEST',
        'timestamp': datetime.now().isoformat(),
        'prediction': {
            'risk_level': 'high',
            'risk_score': 7.2,
            'risk_probabilities': {'low': 0.1, 'high': 0.8, 'critical': 0.1}
        },
        'recommendation': {
            'action': 'INCREASED_MONITORING',
            'message': 'Test warning alert - Audio beep should sound!',
            'color': 'orange',
            'priority': 'MEDIUM'
        },
        'audio_alert': {
            'should_play': True,
            'alert_type': 'warning',
            'frequency': 'periodic'
        }
    })

if __name__ == '__main__':
    print("🚨 Starting Audio Alert Test Backend")
    print("=" * 50)
    print("🔊 This backend is optimized for testing sound alerts")
    print("📡 Test endpoints:")
    print("   POST /predict - Main prediction with audio alert logic")
    print("   GET /test-critical - Force critical alert")
    print("   GET /test-warning - Force warning alert")
    print("🎯 Critical thresholds: displacement >8mm OR vibration >2.5mm/s")
    print("⚠️ Warning thresholds: displacement >5mm OR vibration >1.5mm/s")
    print("🚀 Server starting on http://localhost:5000")
    print("=" * 50)
    
    app.run(debug=True, host='0.0.0.0', port=5000)