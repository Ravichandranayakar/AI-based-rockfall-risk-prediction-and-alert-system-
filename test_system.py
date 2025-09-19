"""
System Integration Test Script
Tests the complete rockfall prediction system
"""

import sys
import os
import json
import pandas as pd
import numpy as np
from datetime import datetime

# Add paths to import modules
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))
sys.path.append(os.path.join(os.path.dirname(__file__), 'dashboard'))

def test_data_loading():
    """Test data file loading"""
    print("🔍 Testing data loading...")
    
    try:
        # Test zones data
        zones_file = os.path.join('sample-data', 'zones.json')
        with open(zones_file, 'r') as f:
            zones_data = json.load(f)
        print(f"✅ Zones data loaded: {len(zones_data['zones'])} zones")
        
        # Test sensor data
        sensor_file = os.path.join('sample-data', 'demo_sensor.csv')
        sensor_df = pd.read_csv(sensor_file)
        print(f"✅ Sensor data loaded: {len(sensor_df)} records")
        
        # Test alerts data
        alerts_file = os.path.join('sample-data', 'fake_alerts.csv')
        alerts_df = pd.read_csv(alerts_file)
        print(f"✅ Alerts data loaded: {len(alerts_df)} alerts")
        
        return True
    except Exception as e:
        print(f"❌ Data loading failed: {e}")
        return False

def test_ml_model():
    """Test ML model functionality"""
    print("\n🤖 Testing ML model...")
    
    try:
        from backend.train_model import RockfallRiskModel
        
        # Create model instance
        model = RockfallRiskModel()
        
        # Test with sample data
        sample_data = {
            'zone_id': 'A',
            'displacement_mm': 5.2,
            'vibration_mm_s': 1.3,
            'temperature_c': 23.0,
            'humidity_percent': 65.0,
            'pressure_kpa': 101.2,
            'accelerometer_x': 0.12,
            'accelerometer_y': 0.08,
            'accelerometer_z': 9.76
        }
        
        # Check if model file exists
        model_file = os.path.join('backend', 'ml_model.pkl')
        if os.path.exists(model_file):
            model.load_model(model_file)
            result = model.predict_risk(sample_data)
            print(f"✅ Model prediction: Risk Level = {result['risk_level']}, Score = {result['risk_score']:.1f}")
        else:
            print("⚠️  Model file not found, would use fallback prediction")
        
        return True
    except Exception as e:
        print(f"❌ ML model test failed: {e}")
        return False

def test_data_processing():
    """Test data processing pipeline"""
    print("\n⚙️ Testing data processing...")
    
    try:
        from backend.process_data import DataProcessor
        
        # Create processor
        processor = DataProcessor()
        
        # Load sample data
        sensor_file = os.path.join('sample-data', 'demo_sensor.csv')
        df = pd.read_csv(sensor_file)
        
        # Test cleaning
        clean_df = processor.clean_sensor_data(df)
        print(f"✅ Data cleaning: {len(df)} → {len(clean_df)} records")
        
        # Test feature engineering
        features_df = processor.engineer_features(clean_df)
        print(f"✅ Feature engineering: {features_df.shape[1]} features created")
        
        # Test risk calculation
        risk_df = processor.calculate_risk_scores(features_df)
        print(f"✅ Risk calculation: Risk scores computed")
        
        return True
    except Exception as e:
        print(f"❌ Data processing test failed: {e}")
        return False

def test_alert_system():
    """Test alert management system"""
    print("\n🚨 Testing alert system...")
    
    try:
        from dashboard.alert_manager import AlertManager
        
        # Create alert manager
        alert_manager = AlertManager()
        
        # Test with sample risk data
        sample_risks = {
            'A': {
                'sensor_data': {
                    'displacement_mm': 6.5,
                    'vibration_mm_s': 1.8,
                    'temperature_c': 23.0,
                    'humidity_percent': 65.0
                },
                'prediction': {
                    'risk_level': 'high',
                    'risk_score': 7.2
                }
            }
        }
        
        # Check for alerts
        new_alerts = alert_manager.check_alerts(sample_risks)
        print(f"✅ Alert generation: {len(new_alerts)} alerts generated")
        
        # Get summary
        summary = alert_manager.get_alert_summary()
        print(f"✅ Alert summary: {summary['total_alerts']} total, {summary['active_alerts']} active")
        
        return True
    except Exception as e:
        print(f"❌ Alert system test failed: {e}")
        return False

def test_dashboard_utils():
    """Test dashboard utilities"""
    print("\n📊 Testing dashboard utilities...")
    
    try:
        from dashboard.dashboard_utils import (
            load_zones_data, load_sensor_data, load_alerts_data,
            get_risk_color, calculate_statistics
        )
        
        # Test data loading functions
        zones = load_zones_data()
        sensors = load_sensor_data()
        alerts = load_alerts_data()
        
        print(f"✅ Dashboard data loading: {len(zones['zones']) if zones else 0} zones, "
              f"{len(sensors)} sensors, {len(alerts)} alerts")
        
        # Test utility functions
        color = get_risk_color('high')
        print(f"✅ Risk color mapping: 'high' → {color}")
        
        if not sensors.empty:
            stats = calculate_statistics(sensors, 'displacement_mm')
            print(f"✅ Statistics calculation: displacement mean = {stats.get('mean', 0):.1f}")
        
        return True
    except Exception as e:
        print(f"❌ Dashboard utilities test failed: {e}")
        return False

def test_api_simulation():
    """Simulate API functionality"""
    print("\n🌐 Testing API simulation...")
    
    try:
        # Simulate API prediction request
        from backend.app import RockfallAPI
        
        api = RockfallAPI()
        
        # Test prediction
        test_data = {
            'zone_id': 'A',
            'displacement_mm': 5.2,
            'vibration_mm_s': 1.3,
            'temperature_c': 23.0,
            'humidity_percent': 65.0,
            'pressure_kpa': 101.2,
            'accelerometer_x': 0.12,
            'accelerometer_y': 0.08,
            'accelerometer_z': 9.76
        }
        
        result = api.predict_risk(test_data)
        print(f"✅ API prediction: {result['risk_level']} risk with score {result['risk_score']:.1f}")
        
        return True
    except Exception as e:
        print(f"❌ API simulation failed: {e}")
        return False

def run_system_test():
    """Run complete system integration test"""
    print("🚀 Starting AI-Based Rockfall System Integration Test")
    print("=" * 60)
    
    tests = [
        ("Data Loading", test_data_loading),
        ("ML Model", test_ml_model),
        ("Data Processing", test_data_processing),
        ("Alert System", test_alert_system),
        ("Dashboard Utils", test_dashboard_utils),
        ("API Simulation", test_api_simulation)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
        except Exception as e:
            print(f"❌ {test_name} test crashed: {e}")
    
    print("\n" + "=" * 60)
    print(f"🎯 System Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! System is ready for demo.")
        print("\n📋 Next Steps:")
        print("1. Start backend: cd backend && python app.py")
        print("2. Start dashboard: cd dashboard && streamlit run streamlit_app.py")
        print("3. Open browser to http://localhost:8501")
        print("4. Begin demo with live data simulation")
    else:
        print("⚠️  Some tests failed. Check error messages above.")
    
    return passed == total

if __name__ == "__main__":
    run_system_test()