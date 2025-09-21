"""
Critical Danger Audio Test - Forces High Risk Scenarios
"""

import requests
import json
import time

def test_critical_scenarios():
    """Test scenarios that should definitely trigger audio alarms"""
    
    print("🚨 Testing CRITICAL DANGER Audio Alerts")
    print("=" * 50)
    
    # Very high values that should trigger critical alerts
    critical_scenarios = [
        {
            "name": "Extreme Displacement",
            "data": {
                "zone_id": "B",
                "displacement_mm": 25.0,  # Very high
                "vibration_mm_s": 5.0,    # Very high
                "temperature_c": 30.0,
                "humidity_percent": 40.0
            }
        },
        {
            "name": "Maximum Vibration",
            "data": {
                "zone_id": "A", 
                "displacement_mm": 20.0,
                "vibration_mm_s": 8.0,    # Extremely high
                "temperature_c": 28.0,
                "humidity_percent": 35.0
            }
        },
        {
            "name": "Combined Critical Factors",
            "data": {
                "zone_id": "D",
                "displacement_mm": 30.0,  # Maximum
                "vibration_mm_s": 10.0,   # Maximum
                "temperature_c": 35.0,
                "humidity_percent": 30.0
            }
        }
    ]
    
    print("📡 Testing with extremely high sensor values to force critical alerts...")
    print()
    
    for scenario in critical_scenarios:
        print(f"🎯 {scenario['name']}:")
        print(f"   Zone: {scenario['data']['zone_id']}")
        print(f"   Displacement: {scenario['data']['displacement_mm']}mm (Critical: >8mm)")
        print(f"   Vibration: {scenario['data']['vibration_mm_s']}mm/s (Critical: >2.5mm/s)")
        
        try:
            response = requests.post("http://localhost:5000/predict", 
                                   json=scenario['data'], timeout=5)
            
            if response.status_code == 200:
                result = response.json()
                prediction = result.get('prediction', {})
                risk_level = prediction.get('risk_level', 'unknown')
                risk_score = prediction.get('risk_score', 0)
                
                print(f"   📊 API Result: Risk Level = {risk_level}, Score = {risk_score:.1f}")
                
                if risk_level == 'critical' or risk_score >= 8.0:
                    print("   🚨 SUCCESS: Should trigger CRITICAL AUDIO ALARM!")
                elif risk_level == 'high' or risk_score >= 6.0:
                    print("   ⚠️ WARNING: Should trigger warning beep")
                else:
                    print("   ❌ UNEXPECTED: These values should trigger critical alarm")
                    print("       This might be due to the dummy prediction logic")
            else:
                print(f"   ❌ API Error: {response.status_code}")
                
        except requests.exceptions.ConnectionError:
            print("   ⚠️ Backend not running - using dummy logic test...")
            # Test the dummy logic manually
            displacement = scenario['data']['displacement_mm']
            vibration = scenario['data']['vibration_mm_s']
            
            if displacement >= 8 or vibration >= 2.5:
                print("   🚨 DUMMY LOGIC: Should trigger CRITICAL ALARM!")
            elif displacement >= 5 or vibration >= 1.5:
                print("   ⚠️ DUMMY LOGIC: Should trigger WARNING beep")
            else:
                print("   🟢 DUMMY LOGIC: Safe condition")
        
        print()
    
    print("🎯 To Test Audio Alerts:")
    print("1. Start React Dashboard: .\\REACT_DEMO.bat")
    print("2. Look for audio alarm in top-right corner when critical data appears")
    print("3. Start Simple Dashboard: .\\SIMPLE_DASHBOARD.bat") 
    print("4. Use the 'Test Danger Alarm' button to hear critical sound")
    print("5. Check that mute/unmute controls work")
    
    print("\n🔊 Expected Audio Behavior:")
    print("   Critical: Rapid beeps (1000Hz-1200Hz) every 3-4 seconds")
    print("   Warning: Single moderate beep (800Hz) every 8 seconds")
    print("   Mute button: Stops all audio alerts")

if __name__ == "__main__":
    test_critical_scenarios()