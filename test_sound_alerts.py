"""
Sound Alert Test System
Demonstrates audio alarm functionality for critical danger detection
"""

import time
import json
import os
from datetime import datetime

def create_test_scenario_data():
    """Create test data with critical danger scenarios"""
    
    # Create mock sensor data with danger scenarios
    danger_scenarios = [
        {
            "scenario_name": "Critical Displacement - Zone B",
            "zones": [
                {"id": "A", "name": "North_Pit_Wall", "status": "SAFE", "risk": "Low", "displacement": 2.1, "vibration": 0.8},
                {"id": "B", "name": "South_Slope", "status": "DANGER", "risk": "High", "displacement": 12.4, "vibration": 3.8},
                {"id": "C", "name": "East_Wall", "status": "SAFE", "risk": "Low", "displacement": 1.9, "vibration": 1.0},
                {"id": "D", "name": "West_Highwall", "status": "WARNING", "risk": "Medium", "displacement": 7.2, "vibration": 2.9},
                {"id": "E", "name": "Central_Zone", "status": "SAFE", "risk": "Low", "displacement": 2.3, "vibration": 1.3}
            ]
        },
        {
            "scenario_name": "Multiple Critical Zones",
            "zones": [
                {"id": "A", "name": "North_Pit_Wall", "status": "DANGER", "risk": "High", "displacement": 15.2, "vibration": 4.1},
                {"id": "B", "name": "South_Slope", "status": "DANGER", "risk": "High", "displacement": 18.7, "vibration": 5.2},
                {"id": "C", "name": "East_Wall", "status": "WARNING", "risk": "Medium", "displacement": 8.1, "vibration": 2.1},
                {"id": "D", "name": "West_Highwall", "status": "SAFE", "risk": "Low", "displacement": 3.2, "vibration": 1.5},
                {"id": "E", "name": "Central_Zone", "status": "WARNING", "risk": "Medium", "displacement": 6.8, "vibration": 2.4}
            ]
        },
        {
            "scenario_name": "All Safe - No Alarms",
            "zones": [
                {"id": "A", "name": "North_Pit_Wall", "status": "SAFE", "risk": "Low", "displacement": 1.2, "vibration": 0.5},
                {"id": "B", "name": "South_Slope", "status": "SAFE", "risk": "Low", "displacement": 1.8, "vibration": 0.7},
                {"id": "C", "name": "East_Wall", "status": "SAFE", "risk": "Low", "displacement": 0.9, "vibration": 0.4},
                {"id": "D", "name": "West_Highwall", "status": "SAFE", "risk": "Low", "displacement": 1.5, "vibration": 0.6},
                {"id": "E", "name": "Central_Zone", "status": "SAFE", "risk": "Low", "displacement": 1.1, "vibration": 0.5}
            ]
        }
    ]
    
    return danger_scenarios

def simulate_danger_scenarios():
    """Simulate different danger scenarios for testing audio alerts"""
    
    print("🎵 Testing Sound Alert System")
    print("=" * 50)
    print("This test will demonstrate the audio alarm system:")
    print("1. Critical danger alarms (rapid high-pitched beeps)")
    print("2. Warning alarms (moderate beeps)")
    print("3. Safe conditions (no alarms)")
    print()
    
    scenarios = create_test_scenario_data()
    
    # Save test data to the demo file location
    demo_file = "dashboard/demo_data.json"
    
    for i, scenario in enumerate(scenarios, 1):
        print(f"🎯 Test Scenario {i}: {scenario['scenario_name']}")
        print("   Zones:")
        
        # Count status types
        danger_count = sum(1 for z in scenario['zones'] if z['status'] == 'DANGER')
        warning_count = sum(1 for z in scenario['zones'] if z['status'] == 'WARNING')
        safe_count = sum(1 for z in scenario['zones'] if z['status'] == 'SAFE')
        
        for zone in scenario['zones']:
            status_icon = {"DANGER": "🔴", "WARNING": "🟡", "SAFE": "🟢"}[zone['status']]
            print(f"     {status_icon} Zone {zone['id']}: {zone['name']} - {zone['status']}")
        
        print(f"   Expected Sound Alert:")
        if danger_count > 0:
            print("     🚨 CRITICAL ALARM: Rapid high-pitched beeps (continuous)")
        elif warning_count > 0:
            print("     ⚠️ WARNING ALARM: Moderate beeps (periodic)")
        else:
            print("     🔇 NO ALARM: All zones safe")
        
        # Save scenario data for testing
        try:
            os.makedirs(os.path.dirname(demo_file), exist_ok=True)
            with open(demo_file, 'w') as f:
                json.dump(scenario, f, indent=2)
            print(f"   ✅ Test data saved to {demo_file}")
        except Exception as e:
            print(f"   ❌ Error saving test data: {e}")
        
        print()
        input(f"Press Enter to continue to next scenario...")
        print()
    
    print("🎉 Audio Alert System Test Complete!")
    print()
    print("📋 Testing Instructions:")
    print("1. Start the Simple Dashboard: .\\SIMPLE_DASHBOARD.bat")
    print("2. Start the React Dashboard: .\\REACT_DEMO.bat")
    print("3. Use the test buttons in both dashboards")
    print("4. Check that sound alerts play for danger scenarios")
    print("5. Verify mute/unmute controls work properly")
    print()
    print("🔊 Sound Alert Features:")
    print("✅ React Dashboard: Browser-based audio with Web Audio API")
    print("✅ Streamlit Dashboard: JavaScript audio system with mute controls")
    print("✅ Automatic detection of danger/warning conditions")
    print("✅ Different sounds for critical vs warning levels")
    print("✅ Continuous alarms for critical situations")
    print("✅ User-controllable mute/unmute functionality")

def test_audio_api_integration():
    """Test audio integration with the backend API"""
    
    print("\n🔌 Testing API Integration for Audio Alerts")
    print("-" * 50)
    
    try:
        import requests
        
        # Test API endpoint
        test_data = {
            "zone_id": "B",
            "displacement_mm": 15.5,
            "vibration_mm_s": 4.2,
            "temperature_c": 25.0,
            "humidity_percent": 60.0
        }
        
        print("📡 Testing backend API prediction...")
        print(f"   Sending critical test data: {test_data}")
        
        # Try to call the prediction API
        try:
            response = requests.post("http://localhost:5000/predict", json=test_data, timeout=5)
            if response.status_code == 200:
                prediction = response.json()
                print(f"   ✅ API Response: {prediction}")
                
                risk_level = prediction.get('prediction', {}).get('risk_level', 'unknown')
                risk_score = prediction.get('prediction', {}).get('risk_score', 0)
                
                print(f"   🎯 Risk Level: {risk_level}")
                print(f"   📊 Risk Score: {risk_score}")
                
                if risk_level == 'critical' or risk_score >= 8.0:
                    print("   🚨 CRITICAL: Should trigger audio alarm!")
                elif risk_level == 'high' or risk_score >= 6.0:
                    print("   ⚠️ WARNING: Should trigger warning beep!")
                else:
                    print("   🟢 SAFE: No audio alarm needed")
            else:
                print(f"   ❌ API Error: {response.status_code}")
        except requests.exceptions.ConnectionError:
            print("   ❌ Backend API not running - start with: python backend/app.py")
        except Exception as e:
            print(f"   ❌ API Test Error: {e}")
    
    except ImportError:
        print("   ⚠️ Requests library not available for API testing")

if __name__ == "__main__":
    simulate_danger_scenarios()
    test_audio_api_integration()