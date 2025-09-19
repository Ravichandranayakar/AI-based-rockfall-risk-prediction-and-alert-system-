"""
Final System Validation and Setup Guide
"""

import os
import sys
import subprocess

def check_requirements():
    """Check if all required packages are installed"""
    print("🔍 Checking Python package requirements...")
    
    package_mapping = {
        'streamlit': 'streamlit',
        'flask': 'flask', 
        'scikit-learn': 'sklearn',
        'pandas': 'pandas',
        'numpy': 'numpy',
        'plotly': 'plotly',
        'paho-mqtt': 'paho.mqtt',
        'requests': 'requests'
    }
    
    missing = []
    for package_name, import_name in package_mapping.items():
        try:
            __import__(import_name)
            print(f"✅ {package_name}")
        except ImportError:
            print(f"❌ {package_name} - Not installed")
            missing.append(package_name)
    
    if missing:
        print(f"\n⚠️  Missing packages: {', '.join(missing)}")
        print("Run: pip install " + " ".join(missing))
        return False
    else:
        print("✅ All required packages are installed!")
        return True

def check_project_structure():
    """Verify project structure is complete"""
    print("\n📁 Checking project structure...")
    
    required_files = [
        'backend/app.py',
        'backend/train_model.py',
        'backend/data_ingest.py',
        'backend/process_data.py',
        'dashboard/streamlit_app.py',
        'dashboard/dashboard_utils.py',
        'dashboard/alert_manager.py',
        'sample-data/demo_sensor.csv',
        'sample-data/zones.json',
        'sample-data/fake_alerts.csv',
        'docs/masterplan.md',
        'docs/README.md',
        'README.md',
        'requirements.txt'
    ]
    
    missing_files = []
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path} - Missing")
            missing_files.append(file_path)
    
    if missing_files:
        print(f"\n⚠️  Missing files: {len(missing_files)}")
        return False
    else:
        print("✅ All required files are present!")
        return True

def check_model_training():
    """Check if ML model is trained"""
    print("\n🤖 Checking ML model status...")
    
    model_file = 'backend/ml_model.pkl'
    if os.path.exists(model_file):
        print(f"✅ ML model found at {model_file}")
        return True
    else:
        print(f"❌ ML model not found. Training model...")
        try:
            os.chdir('backend')
            result = subprocess.run([sys.executable, 'train_model.py'], 
                                  capture_output=True, text=True)
            os.chdir('..')
            
            if result.returncode == 0:
                print("✅ ML model trained successfully!")
                return True
            else:
                print(f"❌ Model training failed: {result.stderr}")
                return False
        except Exception as e:
            print(f"❌ Error training model: {e}")
            return False

def generate_startup_scripts():
    """Generate convenient startup scripts"""
    print("\n📝 Generating startup scripts...")
    
    # Backend startup script
    backend_script = """@echo off
echo Starting Rockfall Prediction API Server...
cd backend
python app.py
pause
"""
    
    with open('start_backend.bat', 'w') as f:
        f.write(backend_script)
    print("✅ Created start_backend.bat")
    
    # Dashboard startup script  
    dashboard_script = """@echo off
echo Starting Rockfall Dashboard...
cd dashboard
streamlit run streamlit_app.py
pause
"""
    
    with open('start_dashboard.bat', 'w') as f:
        f.write(dashboard_script)
    print("✅ Created start_dashboard.bat")
    
    # Data simulation script
    simulation_script = """@echo off
echo Starting Data Simulation...
cd backend
python data_ingest.py --mode simulate --duration 60
pause
"""
    
    with open('start_simulation.bat', 'w') as f:
        f.write(simulation_script)
    print("✅ Created start_simulation.bat")

def display_demo_instructions():
    """Display demo setup instructions"""
    print("\n" + "="*60)
    print("🎯 SYSTEM VALIDATION COMPLETE!")
    print("="*60)
    print("\n🚀 DEMO SETUP INSTRUCTIONS:")
    print("\n1. START BACKEND API:")
    print("   Option A: Double-click 'start_backend.bat'")
    print("   Option B: Manual command:")
    print("           cd backend")
    print("           python app.py")
    print("   → API will start at http://localhost:5000")
    
    print("\n2. START DASHBOARD (New Terminal/Command Prompt):")
    print("   Option A: Double-click 'start_dashboard.bat'")
    print("   Option B: Manual command:")
    print("           cd dashboard")
    print("           streamlit run streamlit_app.py")
    print("   → Dashboard will open at http://localhost:8501")
    
    print("\n3. START DATA SIMULATION (Optional - New Terminal):")
    print("   Option A: Double-click 'start_simulation.bat'")
    print("   Option B: Manual command:")
    print("           cd backend")
    print("           python data_ingest.py --mode simulate")
    
    print("\n📊 DEMO FEATURES TO SHOWCASE:")
    print("• Real-time mine map with risk zones")
    print("• Live sensor monitoring and risk gauges")
    print("• Automated alert generation and notifications")
    print("• Historical trend analysis and data export")
    print("• Interactive zone details and recommendations")
    
    print("\n🎮 DEMO SCENARIOS:")
    print("• Normal Operations: Monitor stable conditions")
    print("• Warning Alerts: Observe elevated risk responses")
    print("• Critical Alerts: Experience emergency procedures")
    
    print("\n💡 TROUBLESHOOTING:")
    print("• If ports are busy, check for other applications")
    print("• Ensure virtual environment is activated")
    print("• Check terminal output for error messages")
    print("• All sample data is pre-loaded for immediate demo")
    
    print("\n🏆 SYSTEM READY FOR DEMONSTRATION!")
    print("="*60)

def main():
    """Main validation function"""
    print("🔧 AI-Based Rockfall System - Final Validation")
    print("="*60)
    
    # Run all checks
    checks = [
        ("Package Requirements", check_requirements),
        ("Project Structure", check_project_structure),
        ("ML Model Training", check_model_training)
    ]
    
    all_passed = True
    for check_name, check_func in checks:
        if not check_func():
            all_passed = False
    
    if all_passed:
        generate_startup_scripts()
        display_demo_instructions()
    else:
        print("\n❌ System validation failed. Please fix the issues above.")
        print("💡 Try running: pip install -r requirements.txt")

if __name__ == "__main__":
    main()