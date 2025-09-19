# AI-Based Rockfall Risk Prediction and Alert System

## 🎯 Quick Start Guide

This is a comprehensive MVP demonstration of an AI-powered rockfall monitoring system for open-pit mines. The system provides real-time risk assessment, interactive dashboards, and automated alerting capabilities.

## ⚡ Quick Demo Setup

### Prerequisites
- Python 3.8 or higher
- Git (for cloning)
- 4GB RAM minimum
- Modern web browser

### 1. Clone and Setup
```bash
git clone <your-repo-url>
cd "AI-based rockfall risk prediction and alert system"

# Create virtual environment (if not exists)
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# Install dependencies (some may already be installed)
pip install -r requirements.txt
```

### 2. Start the Backend API
```bash
cd backend
python app.py
```
The API will start on `http://localhost:5000`

### 3. Launch Dashboard (New Terminal)
```bash
# Activate virtual environment in new terminal
venv\Scripts\activate

cd dashboard
streamlit run streamlit_app.py
```
The dashboard will open automatically in your browser at `http://localhost:8501`

### 4. Start Data Simulation (Optional - New Terminal)
```bash
# Activate virtual environment in new terminal
venv\Scripts\activate

cd backend
python data_ingest.py --mode simulate --duration 30
```

## 🚀 System Features

### 📊 Interactive Dashboard
- **Real-time mine map** with risk visualization
- **Live sensor monitoring** for 4 mine zones
- **Risk gauges and metrics** with color-coded alerts
- **Historical trend analysis** and data export
- **Alert management** with status tracking

### 🤖 AI-Powered Risk Assessment
- **Machine Learning model** for risk prediction (Random Forest)
- **Multi-factor analysis** including displacement, vibration, environmental data
- **Zone-specific thresholds** based on geological characteristics
- **Real-time scoring** on 0-10 risk scale

### 🚨 Automated Alert System
- **Threshold-based alerting** with three levels (INFO, WARNING, CRITICAL)
- **Multi-channel notifications** (dashboard, email, SMS simulation)
- **Alert lifecycle management** with resolution tracking
- **Emergency response integration** for critical situations

### 📡 Real-time Data Integration
- **Sensor data simulation** with realistic patterns
- **MQTT streaming support** for live data feeds
- **REST API endpoints** for system integration
- **Data validation and quality checks**

## 🏗️ Architecture Overview

```
Sensor Data → Data Processing → ML Model → Risk Assessment → Dashboard/Alerts
     ↓              ↓             ↓           ↓              ↓
   CSV/MQTT     Feature Eng.   Prediction   Thresholds   Visualization
```

### Core Components
- **Backend API** (Flask): Risk prediction and data management
- **Dashboard** (Streamlit): Interactive web interface
- **Alert Manager**: Notification and alert handling
- **Data Pipeline**: Processing and feature engineering
- **ML Model**: Risk prediction and scoring

## 📁 Project Structure

```
rockfall-ai-mvp/
├── backend/              # API and ML services
│   ├── app.py           # Main Flask API
│   ├── train_model.py   # ML model training
│   ├── data_ingest.py   # Data simulation
│   └── process_data.py  # Data processing
├── dashboard/           # Web interface
│   ├── streamlit_app.py # Main dashboard
│   ├── dashboard_utils.py # Helper functions
│   └── alert_manager.py # Alert system
├── sample-data/         # Demo data
│   ├── demo_sensor.csv  # Sensor readings
│   ├── zones.json       # Mine configuration
│   └── fake_alerts.csv  # Alert history
└── docs/               # Documentation
    └── masterplan.md   # Detailed architecture
```

## 🎮 Demo Scenarios

### Scenario 1: Normal Operations
1. Start the system and observe normal risk levels (green indicators)
2. Monitor real-time sensor data across all zones
3. View historical trends and patterns

### Scenario 2: Warning Alert
1. Wait for or simulate elevated readings in a zone
2. Observe warning alerts (orange indicators) 
3. Review recommended actions and monitoring

### Scenario 3: Critical Emergency
1. Simulate critical conditions (high displacement/vibration)
2. Watch emergency alerts (red indicators) appear
3. See evacuation recommendations and emergency protocols

## 📋 API Endpoints

### Health Check
```
GET /
Returns: System status and health information
```

### Risk Prediction
```
POST /predict
Body: {
    "zone_id": "A",
    "displacement_mm": 5.2,
    "vibration_mm_s": 1.3,
    "temperature_c": 23.0,
    "humidity_percent": 65.0
}
Returns: Risk assessment and recommendations
```

### Zone Information
```
GET /zones
Returns: All mine zone configurations

GET /zones/{zone_id}
Returns: Specific zone details
```

### Alert History
```
GET /alerts
Returns: Recent alert history and status
```

## 🔧 Configuration

### Zone Thresholds
Edit `sample-data/zones.json` to modify:
- Risk thresholds for each zone
- Geological characteristics
- Sensor configurations
- Emergency contacts

### Model Parameters
Modify `backend/train_model.py` for:
- ML algorithm selection
- Feature engineering options
- Training parameters
- Validation metrics

### Dashboard Settings
Customize `dashboard/streamlit_app.py` for:
- Refresh intervals
- Visualization options
- Alert thresholds
- Display preferences

## 🚨 Alert Levels

### 🟢 LOW (0-3)
- **Status**: Normal operations
- **Action**: Routine monitoring
- **Frequency**: Continuous background monitoring

### 🟡 WARNING (3-6)
- **Status**: Elevated risk detected
- **Action**: Increased monitoring, restrict access
- **Frequency**: Enhanced monitoring intervals

### 🔴 CRITICAL (6-10)
- **Status**: Immediate danger
- **Action**: Evacuation, emergency response
- **Frequency**: Continuous monitoring, immediate alerts

## 📊 Sample Data

The system includes realistic sample data:
- **4 Mine Zones**: North Pit Wall, South Slope, East Bench, West Highwall
- **Multi-sensor Data**: Displacement, vibration, temperature, humidity, acceleration
- **Historical Patterns**: 24+ hours of simulated sensor readings
- **Alert Examples**: Various alert types and resolutions

## 🔬 Technical Details

### Machine Learning
- **Algorithm**: Random Forest Classifier
- **Features**: 8+ sensor parameters plus engineered features
- **Training**: Historical data with labeled risk levels
- **Validation**: Cross-validation with 80/20 split

### Data Processing
- **Real-time**: 15-second update intervals
- **Quality Checks**: Outlier detection and data validation
- **Feature Engineering**: Rate calculations, moving averages
- **Storage**: CSV files (production would use database)

### Performance
- **API Response**: <2 seconds for predictions
- **Dashboard Refresh**: 15-second auto-refresh
- **Data Throughput**: 1000+ readings per hour
- **Concurrent Users**: Optimized for demo use

## 🛠️ Troubleshooting

### Common Issues

**API not starting:**
- Check if port 5000 is available
- Verify Python dependencies are installed
- Check for error messages in terminal

**Dashboard not loading:**
- Ensure Streamlit is installed (`pip install streamlit`)
- Check if port 8501 is available
- Verify API is running on localhost:5000

**No data appearing:**
- Check if sample data files exist in `sample-data/`
- Verify file permissions and paths
- Run data simulation script

**MQTT not connecting:**
- MQTT is optional for demo
- Check if MQTT broker is running (if using)
- Verify network connectivity

### Log Files
Check terminal output for detailed error messages and system logs.

## 🔮 Future Enhancements

### Immediate (Demo Ready)
- ✅ Interactive dashboard with mine map
- ✅ Real-time risk assessment
- ✅ Automated alert system
- ✅ MQTT integration
- ✅ Data export capabilities

### Short-term
- [ ] Mobile-responsive design
- [ ] Advanced ML algorithms
- [ ] Weather data integration
- [ ] Automated reporting

### Long-term
- [ ] Multi-mine support
- [ ] Database integration
- [ ] User authentication
- [ ] Cloud deployment
- [ ] Edge computing

## 📞 Support and Contact

For technical questions or support:
- Review the detailed `docs/masterplan.md`
- Check API documentation in code comments
- Examine sample data formats in `sample-data/`
- Test individual components using provided scripts

## 🏆 Demo Highlights

This system demonstrates:
- **Real-world applicability** with realistic mine scenarios
- **Technical sophistication** using modern ML and web technologies
- **Operational readiness** with complete alert workflows
- **Scalable architecture** suitable for production deployment

Perfect for showcasing AI-powered industrial monitoring solutions! 🎯

---

**Ready to explore mine safety innovation? Start the demo now!** 🚀