# SynthForge Backend - Simple & Working
# Single FastAPI service that does everything

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime
import json
import asyncpg
import os
from typing import List, Dict, Any, Optional
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# FastAPI app
app = FastAPI(
    title="SynthForge Backend",
    description="Simple rockfall prediction API",
    version="1.0.0"
)

# CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

# Database connection
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/synthforge")

# Data models
class SensorReading(BaseModel):
    sensor_id: str
    sensor_type: str
    location_lat: float
    location_lon: float
    timestamp: datetime
    value: float
    unit: str

class PredictionRequest(BaseModel):
    sensor_data: List[Dict[str, Any]]
    location_lat: float
    location_lon: float

class Alert(BaseModel):
    id: Optional[int] = None
    sensor_id: str
    risk_level: str
    risk_score: float
    message: str
    timestamp: datetime
    acknowledged: bool = False

# In-memory storage (replace with database later)
sensor_readings = []
predictions = []
alerts = []

# Your team's model goes here
def your_ml_prediction(sensor_data: List[Dict], lat: float, lon: float) -> Dict:
    """
    🎯 THIS IS WHERE YOUR TEAM PLUGS IN THE TRAINED MODEL
    
    Replace this function with your trained model inference:
    
    def your_ml_prediction(sensor_data, lat, lon):
        # Load your trained model
        model = torch.load('your_model.pth')
        
        # Preprocess data
        features = preprocess_sensor_data(sensor_data)
        
        # Make prediction
        risk_score = model.predict(features)
        
        return {
            "risk_score": float(risk_score),
            "risk_level": "HIGH" if risk_score > 0.7 else "MEDIUM" if risk_score > 0.4 else "LOW"
        }
    """
    
    # Mock prediction (your team replaces this)
    import random
    risk_score = random.uniform(0.1, 0.9)
    
    if risk_score > 0.7:
        risk_level = "CRITICAL"
    elif risk_score > 0.5:
        risk_level = "HIGH"
    elif risk_score > 0.3:
        risk_level = "MEDIUM"
    else:
        risk_level = "LOW"
    
    return {
        "risk_score": round(risk_score, 3),
        "risk_level": risk_level,
        "confidence": round(random.uniform(0.8, 0.95), 3),
        "model_version": "your_model_v1"
    }

# Health check
@app.get("/")
@app.get("/health")
async def health_check():
    """System health check"""
    return {
        "status": "healthy",
        "service": "SynthForge Backend",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    }

# Sensor data endpoints
@app.post("/api/sensors/data")
async def receive_sensor_data(reading: SensorReading):
    """Receive sensor data from IoT devices"""
    try:
        # Store sensor reading
        sensor_readings.append(reading.dict())
        
        # Trigger real-time prediction if critical sensor
        if reading.sensor_type in ["seismic", "vibration"]:
            prediction_data = {
                "sensor_data": [reading.dict()],
                "location_lat": reading.location_lat,
                "location_lon": reading.location_lon
            }
            
            # Get prediction
            result = your_ml_prediction(
                prediction_data["sensor_data"],
                reading.location_lat,
                reading.location_lon
            )
            
            # Create alert if high risk
            if result["risk_level"] in ["HIGH", "CRITICAL"]:
                alert = {
                    "id": len(alerts) + 1,
                    "sensor_id": reading.sensor_id,
                    "risk_level": result["risk_level"],
                    "risk_score": result["risk_score"],
                    "message": f"High risk detected at sensor {reading.sensor_id}",
                    "timestamp": datetime.now(),
                    "acknowledged": False,
                    "location": {
                        "lat": reading.location_lat,
                        "lon": reading.location_lon
                    }
                }
                alerts.append(alert)
                logger.warning(f"Alert created: {alert}")
        
        logger.info(f"Sensor data received from {reading.sensor_id}")
        return {
            "status": "success",
            "message": "Sensor data processed",
            "sensor_id": reading.sensor_id
        }
        
    except Exception as e:
        logger.error(f"Error processing sensor data: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/sensors/data")
async def get_sensor_data(limit: int = 100):
    """Get recent sensor readings"""
    return {
        "readings": sensor_readings[-limit:],
        "total": len(sensor_readings)
    }

@app.get("/api/sensors/latest/{sensor_id}")
async def get_latest_reading(sensor_id: str):
    """Get latest reading from specific sensor"""
    for reading in reversed(sensor_readings):
        if reading["sensor_id"] == sensor_id:
            return reading
    
    raise HTTPException(status_code=404, detail="Sensor not found")

# Prediction endpoints
@app.post("/api/predict")
async def predict_rockfall_risk(request: PredictionRequest):
    """
    🎯 MAIN PREDICTION ENDPOINT - YOUR TEAM'S MODEL GOES HERE
    
    This is the main endpoint where your trained model will be called.
    Replace the your_ml_prediction() function with your actual model.
    """
    try:
        # Call your ML model
        result = your_ml_prediction(
            request.sensor_data,
            request.location_lat,
            request.location_lon
        )
        
        # Store prediction
        prediction = {
            "id": len(predictions) + 1,
            "timestamp": datetime.now().isoformat(),
            "location": {
                "lat": request.location_lat,
                "lon": request.location_lon
            },
            "input_sensors": len(request.sensor_data),
            **result
        }
        predictions.append(prediction)
        
        logger.info(f"Prediction made: {result['risk_level']} ({result['risk_score']})")
        
        return {
            "status": "success",
            "prediction": prediction,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Prediction failed: {e}")
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")

@app.get("/api/predictions")
async def get_predictions(limit: int = 50):
    """Get recent predictions"""
    return {
        "predictions": predictions[-limit:],
        "total": len(predictions)
    }

# Alert endpoints
@app.get("/api/alerts")
async def get_alerts(active_only: bool = True):
    """Get alerts"""
    if active_only:
        active_alerts = [alert for alert in alerts if not alert.get("acknowledged", False)]
        return {
            "alerts": active_alerts,
            "total_active": len(active_alerts),
            "total_all": len(alerts)
        }
    else:
        return {
            "alerts": alerts,
            "total": len(alerts)
        }

@app.put("/api/alerts/{alert_id}/acknowledge")
async def acknowledge_alert(alert_id: int):
    """Acknowledge an alert"""
    for alert in alerts:
        if alert.get("id") == alert_id:
            alert["acknowledged"] = True
            alert["acknowledged_at"] = datetime.now().isoformat()
            logger.info(f"Alert {alert_id} acknowledged")
            return {
                "status": "success",
                "message": f"Alert {alert_id} acknowledged"
            }
    
    raise HTTPException(status_code=404, detail="Alert not found")

@app.delete("/api/alerts/{alert_id}")
async def delete_alert(alert_id: int):
    """Delete an alert"""
    global alerts
    original_count = len(alerts)
    alerts = [alert for alert in alerts if alert.get("id") != alert_id]
    
    if len(alerts) < original_count:
        return {"status": "success", "message": f"Alert {alert_id} deleted"}
    else:
        raise HTTPException(status_code=404, detail="Alert not found")

# Dashboard data endpoints
@app.get("/api/dashboard/summary")
async def get_dashboard_summary():
    """Get dashboard summary data"""
    active_alerts = [a for a in alerts if not a.get("acknowledged", False)]
    
    # Calculate risk distribution
    risk_levels = {"LOW": 0, "MEDIUM": 0, "HIGH": 0, "CRITICAL": 0}
    for pred in predictions[-50:]:  # Last 50 predictions
        risk_level = pred.get("risk_level", "LOW")
        if risk_level in risk_levels:
            risk_levels[risk_level] += 1
    
    return {
        "total_sensors": len(set([r["sensor_id"] for r in sensor_readings])),
        "total_readings": len(sensor_readings),
        "active_alerts": len(active_alerts),
        "total_predictions": len(predictions),
        "risk_distribution": risk_levels,
        "system_status": "operational",
        "last_updated": datetime.now().isoformat()
    }

@app.get("/api/dashboard/recent-activity")
async def get_recent_activity(limit: int = 20):
    """Get recent system activity"""
    activities = []
    
    # Recent sensor readings
    for reading in sensor_readings[-limit//2:]:
        activities.append({
            "type": "sensor_reading",
            "timestamp": reading["timestamp"],
            "message": f"Data received from {reading['sensor_id']}",
            "details": reading
        })
    
    # Recent alerts
    for alert in alerts[-limit//2:]:
        activities.append({
            "type": "alert",
            "timestamp": alert["timestamp"],
            "message": f"{alert['risk_level']} risk alert",
            "details": alert
        })
    
    # Sort by timestamp
    activities.sort(key=lambda x: x["timestamp"], reverse=True)
    
    return {
        "activities": activities[:limit],
        "total": len(activities)
    }

# System stats
@app.get("/api/stats")
async def get_system_stats():
    """Get comprehensive system statistics"""
    return {
        "service": "SynthForge Backend",
        "version": "1.0.0",
        "uptime": "running",
        "database": "in-memory",
        "total_sensors": len(set([r["sensor_id"] for r in sensor_readings])),
        "total_readings": len(sensor_readings),
        "total_predictions": len(predictions),
        "total_alerts": len(alerts),
        "active_alerts": len([a for a in alerts if not a.get("acknowledged", False)]),
        "timestamp": datetime.now().isoformat()
    }

# Test endpoint for your team
@app.post("/api/test/mock-sensor")
async def create_mock_sensor_data():
    """Create mock sensor data for testing"""
    import random
    
    mock_reading = SensorReading(
        sensor_id=f"sensor_{random.randint(1, 10)}",
        sensor_type=random.choice(["seismic", "vibration", "temperature"]),
        location_lat=round(random.uniform(40.0, 41.0), 6),
        location_lon=round(random.uniform(-74.5, -73.5), 6),
        timestamp=datetime.now(),
        value=round(random.uniform(0.1, 10.0), 2),
        unit=random.choice(["m/s²", "°C", "Hz"])
    )
    
    return await receive_sensor_data(mock_reading)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )