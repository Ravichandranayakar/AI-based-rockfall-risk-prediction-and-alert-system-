# SynthForge ML Pipeline Service
# Production-grade ML pipeline with PyTorch, MLflow, and real-time inference

from fastapi import FastAPI, HTTPException, BackgroundTasks, Depends
from fastapi.middleware.cors import CORSMiddleware
import torch
import torch.nn as nn
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from sklearn.ensemble import IsolationForest
import mlflow
import mlflow.pytorch
import mlflow.sklearn
from mlflow.tracking import MlflowClient
import asyncio
import asyncpg
import aioredis
import aiokafka
from datetime import datetime, timedelta, timezone
import json
import logging
import pickle
import joblib
from typing import Dict, List, Optional, Any, Tuple
from pydantic import BaseModel, Field, validator
import os
from pathlib import Path
import structlog
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
import warnings
warnings.filterwarnings('ignore')

# Configure structured logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger(__name__)

# Initialize FastAPI
app = FastAPI(
    title="SynthForge ML Pipeline",
    description="Production-grade ML pipeline for rockfall prediction",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

# Configuration
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://synthforge:synthforge123@localhost/synthforge_db")
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_SERVERS", "localhost:9092")
MLFLOW_TRACKING_URI = os.getenv("MLFLOW_TRACKING_URI", "http://localhost:5000")
MODEL_REGISTRY_PATH = os.getenv("MODEL_REGISTRY_PATH", "./models")

# Initialize MLflow
mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)
mlflow_client = MlflowClient()

# Initialize database
engine = create_async_engine(DATABASE_URL, echo=False)
async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

# Global connections
redis_pool = None
kafka_consumer = None
kafka_producer = None

# Device configuration for PyTorch
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
logger.info(f"Using device: {device}")

# Pydantic models
class PredictionRequest(BaseModel):
    sensor_data: List[Dict[str, Any]] = Field(..., min_items=1)
    location_lat: float = Field(..., ge=-90, le=90)
    location_lon: float = Field(..., ge=-180, le=180)
    prediction_horizon: int = Field(default=24, ge=1, le=168)  # Hours
    include_confidence: bool = Field(default=True)
    model_version: Optional[str] = None

class TrainingRequest(BaseModel):
    data_start_date: datetime
    data_end_date: datetime
    model_type: str = Field(..., regex="^(lstm|cnn|ensemble|xgboost)$")
    hyperparameters: Optional[Dict[str, Any]] = None
    experiment_name: str = Field(default="rockfall_prediction")
    auto_deploy: bool = Field(default=False)

class ModelInfo(BaseModel):
    model_id: str
    model_type: str
    version: str
    accuracy: float
    created_at: datetime
    status: str
    metadata: Optional[Dict[str, Any]] = None

# LSTM Model Architecture
class RockfallLSTM(nn.Module):
    """Advanced LSTM model for time-series rockfall prediction"""
    
    def __init__(self, input_size: int, hidden_size: int = 128, num_layers: int = 3, 
                 output_size: int = 1, dropout: float = 0.2):
        super(RockfallLSTM, self).__init__()
        
        self.hidden_size = hidden_size
        self.num_layers = num_layers
        
        # LSTM layers with dropout
        self.lstm = nn.LSTM(
            input_size=input_size,
            hidden_size=hidden_size,
            num_layers=num_layers,
            dropout=dropout if num_layers > 1 else 0,
            batch_first=True,
            bidirectional=False
        )
        
        # Attention mechanism
        self.attention = nn.MultiheadAttention(
            embed_dim=hidden_size,
            num_heads=8,
            dropout=dropout,
            batch_first=True
        )
        
        # Classification layers
        self.classifier = nn.Sequential(
            nn.Linear(hidden_size, hidden_size // 2),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(hidden_size // 2, hidden_size // 4),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(hidden_size // 4, output_size),
            nn.Sigmoid()
        )
        
    def forward(self, x):
        batch_size = x.size(0)
        
        # LSTM forward pass
        lstm_out, (hidden, cell) = self.lstm(x)
        
        # Apply attention
        attn_out, _ = self.attention(lstm_out, lstm_out, lstm_out)
        
        # Use the last output for classification
        final_out = attn_out[:, -1, :]
        
        # Classification
        risk_score = self.classifier(final_out)
        
        return risk_score

# CNN Model for Spatial Analysis
class RockfallCNN(nn.Module):
    """CNN model for spatial pattern recognition in rockfall data"""
    
    def __init__(self, input_channels: int = 1, num_classes: int = 5):
        super(RockfallCNN, self).__init__()
        
        # Convolutional layers
        self.conv_layers = nn.Sequential(
            nn.Conv2d(input_channels, 32, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.MaxPool2d(2, 2),
            
            nn.Conv2d(32, 64, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.MaxPool2d(2, 2),
            
            nn.Conv2d(64, 128, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.AdaptiveAvgPool2d((4, 4))
        )
        
        # Classification layers
        self.classifier = nn.Sequential(
            nn.Linear(128 * 4 * 4, 256),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(256, 64),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(64, num_classes),
            nn.Softmax(dim=1)
        )
        
    def forward(self, x):
        x = self.conv_layers(x)
        x = x.view(x.size(0), -1)  # Flatten
        x = self.classifier(x)
        return x

# Model Management Class
class ModelManager:
    """Manages model lifecycle, training, and deployment"""
    
    def __init__(self):
        self.models = {}
        self.scalers = {}
        self.active_model_version = None
        
    async def load_model(self, model_id: str, model_type: str) -> bool:
        """Load model from MLflow registry"""
        try:
            model_uri = f"models:/{model_id}/Production"
            
            if model_type == "lstm":
                # Load PyTorch model
                model = mlflow.pytorch.load_model(model_uri, map_location=device)
                model.eval()
                self.models[model_id] = model
                
            elif model_type == "xgboost":
                # Load sklearn model
                model = mlflow.sklearn.load_model(model_uri)
                self.models[model_id] = model
                
            # Load associated scaler
            scaler_path = f"{MODEL_REGISTRY_PATH}/{model_id}_scaler.pkl"
            if os.path.exists(scaler_path):
                with open(scaler_path, 'rb') as f:
                    self.scalers[model_id] = pickle.load(f)
                    
            logger.info("Model loaded successfully", model_id=model_id, model_type=model_type)
            return True
            
        except Exception as e:
            logger.error("Failed to load model", model_id=model_id, error=str(e))
            return False
    
    async def predict(self, model_id: str, features: np.ndarray) -> Tuple[float, float]:
        """Make prediction with confidence score"""
        try:
            if model_id not in self.models:
                raise ValueError(f"Model {model_id} not loaded")
                
            model = self.models[model_id]
            
            # Scale features if scaler available
            if model_id in self.scalers:
                features = self.scalers[model_id].transform(features)
            
            # Make prediction based on model type
            if isinstance(model, torch.nn.Module):
                # PyTorch model
                model.eval()
                with torch.no_grad():
                    features_tensor = torch.FloatTensor(features).to(device)
                    if len(features_tensor.shape) == 2:
                        features_tensor = features_tensor.unsqueeze(0)
                    
                    prediction = model(features_tensor)
                    risk_score = prediction.cpu().numpy().flatten()[0]
                    confidence = 0.95  # TODO: Implement uncertainty estimation
                    
            else:
                # Sklearn model
                prediction_proba = model.predict_proba(features)
                risk_score = prediction_proba[:, 1][0]  # Probability of positive class
                confidence = max(prediction_proba[0])
                
            return float(risk_score), float(confidence)
            
        except Exception as e:
            logger.error("Prediction failed", model_id=model_id, error=str(e))
            raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")

# Feature Engineering
class FeatureEngineer:
    """Advanced feature engineering for rockfall prediction"""
    
    @staticmethod
    def extract_time_series_features(data: pd.DataFrame, window_size: int = 24) -> pd.DataFrame:
        """Extract statistical features from time series data"""
        features = []
        
        for i in range(len(data) - window_size + 1):
            window = data.iloc[i:i+window_size]
            
            feature_row = {
                'mean': window['value'].mean(),
                'std': window['value'].std(),
                'min': window['value'].min(),
                'max': window['value'].max(),
                'median': window['value'].median(),
                'skewness': window['value'].skew(),
                'kurtosis': window['value'].kurtosis(),
                'trend': np.polyfit(range(window_size), window['value'], 1)[0],
                'range': window['value'].max() - window['value'].min(),
                'iqr': window['value'].quantile(0.75) - window['value'].quantile(0.25),
                'timestamp': window['timestamp'].iloc[-1]
            }
            features.append(feature_row)
        
        return pd.DataFrame(features)
    
    @staticmethod
    def create_sequences(data: np.ndarray, sequence_length: int = 50) -> Tuple[np.ndarray, np.ndarray]:
        """Create sequences for LSTM training"""
        X, y = [], []
        
        for i in range(len(data) - sequence_length):
            X.append(data[i:(i + sequence_length)])
            y.append(data[i + sequence_length])
        
        return np.array(X), np.array(y)

# Global instances
model_manager = ModelManager()
feature_engineer = FeatureEngineer()

# Startup and shutdown events
@app.on_event("startup")
async def startup_event():
    """Initialize ML pipeline service"""
    global redis_pool, kafka_consumer, kafka_producer
    
    try:
        # Initialize Redis
        redis_pool = aioredis.from_url(REDIS_URL)
        await redis_pool.ping()
        
        # Initialize Kafka
        kafka_producer = aiokafka.AIOKafkaProducer(
            bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
            value_serializer=lambda x: json.dumps(x, default=str).encode()
        )
        await kafka_producer.start()
        
        kafka_consumer = aiokafka.AIOKafkaConsumer(
            'sensor_readings', 'critical_readings',
            bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
            group_id='ml_pipeline',
            auto_offset_reset='latest'
        )
        await kafka_consumer.start()
        
        # Load default models
        await model_manager.load_model("rockfall_lstm_v1", "lstm")
        
        # Start background ML processing
        asyncio.create_task(process_real_time_data())
        
        logger.info("ML Pipeline Service initialized successfully")
        
    except Exception as e:
        logger.error("Failed to initialize ML service", error=str(e))
        raise

@app.on_event("shutdown")
async def shutdown_event():
    """Clean up ML service"""
    try:
        if kafka_producer:
            await kafka_producer.stop()
        if kafka_consumer:
            await kafka_consumer.stop()
        if redis_pool:
            await redis_pool.close()
        logger.info("ML Pipeline Service shut down gracefully")
    except Exception as e:
        logger.error("Error during ML service shutdown", error=str(e))

async def process_real_time_data():
    """Background task to process incoming sensor data"""
    try:
        async for msg in kafka_consumer:
            try:
                data = json.loads(msg.value.decode('utf-8'))
                
                # Process critical readings immediately
                if msg.topic == 'critical_readings':
                    await process_critical_reading(data)
                else:
                    await process_sensor_reading(data)
                    
            except Exception as e:
                logger.error("Error processing Kafka message", error=str(e))
    except Exception as e:
        logger.error("Error in real-time processing loop", error=str(e))

async def process_critical_reading(data: Dict[str, Any]):
    """Process critical sensor readings for immediate risk assessment"""
    try:
        # Extract features
        features = np.array([[
            data['value'],
            data.get('quality_score', 1.0),
            data.get('location_lat', 0),
            data.get('location_lon', 0)
        ]])
        
        # Make prediction
        risk_score, confidence = await model_manager.predict("rockfall_lstm_v1", features)
        
        # If high risk, trigger alert
        if risk_score > 0.7:
            alert_data = {
                "sensor_id": data['sensor_id'],
                "risk_score": risk_score,
                "confidence": confidence,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "alert_type": "high_risk_prediction",
                "location": {
                    "lat": data.get('location_lat'),
                    "lon": data.get('location_lon')
                }
            }
            
            # Publish alert
            await kafka_producer.send('ml_alerts', alert_data)
            
            logger.warning("High risk prediction generated",
                          sensor_id=data['sensor_id'],
                          risk_score=risk_score)
        
    except Exception as e:
        logger.error("Error processing critical reading", error=str(e))

async def process_sensor_reading(data: Dict[str, Any]):
    """Process regular sensor readings"""
    # Implement batch processing logic here
    pass

# Health check
@app.get("/health")
async def health_check():
    """ML service health check"""
    health = {
        "status": "healthy",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "version": "1.0.0",
        "device": str(device),
        "loaded_models": list(model_manager.models.keys()),
        "dependencies": {}
    }
    
    # Check dependencies
    try:
        if redis_pool:
            await redis_pool.ping()
            health["dependencies"]["redis"] = "healthy"
    except Exception:
        health["dependencies"]["redis"] = "unhealthy"
    
    return health

# Model management endpoints
@app.get("/models")
async def list_models():
    """List all available models"""
    try:
        models = []
        
        # Get models from MLflow registry
        registered_models = mlflow_client.list_registered_models()
        
        for model in registered_models:
            latest_version = mlflow_client.get_latest_versions(
                model.name, 
                stages=["Production", "Staging"]
            )
            
            if latest_version:
                version_info = latest_version[0]
                models.append({
                    "model_id": model.name,
                    "version": version_info.version,
                    "stage": version_info.current_stage,
                    "created_at": version_info.creation_timestamp,
                    "description": model.description
                })
        
        return {
            "models": models,
            "loaded_models": list(model_manager.models.keys())
        }
        
    except Exception as e:
        logger.error("Error listing models", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to list models")

@app.post("/predict")
async def predict_risk(request: PredictionRequest):
    """Generate risk prediction for given sensor data"""
    try:
        # Prepare features from sensor data
        features_list = []
        
        for reading in request.sensor_data:
            features_list.append([
                reading.get('value', 0),
                reading.get('quality_score', 1.0),
                request.location_lat,
                request.location_lon,
                reading.get('timestamp', datetime.now().timestamp())
            ])
        
        features = np.array(features_list)
        
        # Use specified model or default
        model_id = request.model_version or "rockfall_lstm_v1"
        
        # Make prediction
        risk_score, confidence = await model_manager.predict(model_id, features)
        
        # Determine risk level
        if risk_score < 0.3:
            risk_level = "LOW"
        elif risk_score < 0.6:
            risk_level = "MEDIUM"
        elif risk_score < 0.8:
            risk_level = "HIGH"
        else:
            risk_level = "CRITICAL"
        
        result = {
            "risk_score": round(risk_score, 4),
            "risk_level": risk_level,
            "prediction_timestamp": datetime.now(timezone.utc).isoformat(),
            "model_used": model_id,
            "location": {
                "lat": request.location_lat,
                "lon": request.location_lon
            }
        }
        
        if request.include_confidence:
            result["confidence"] = round(confidence, 4)
        
        # Cache result
        if redis_pool:
            cache_key = f"prediction:{request.location_lat}:{request.location_lon}"
            await redis_pool.setex(cache_key, 300, json.dumps(result, default=str))
        
        logger.info("Prediction generated",
                   risk_score=risk_score,
                   risk_level=risk_level,
                   model=model_id)
        
        return result
        
    except Exception as e:
        logger.error("Prediction request failed", error=str(e))
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")

@app.post("/train")
async def trigger_training(request: TrainingRequest, background_tasks: BackgroundTasks):
    """Trigger model training with specified parameters"""
    try:
        # Validate request
        if request.data_end_date <= request.data_start_date:
            raise HTTPException(status_code=400, detail="Invalid date range")
        
        # Start training in background
        training_id = f"training_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        background_tasks.add_task(
            run_model_training,
            training_id,
            request.dict()
        )
        
        return {
            "status": "training_started",
            "training_id": training_id,
            "estimated_duration": "30-60 minutes",
            "model_type": request.model_type
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to start training", error=str(e))
        raise HTTPException(status_code=500, detail="Training initialization failed")

async def run_model_training(training_id: str, config: Dict[str, Any]):
    """Background task for model training"""
    try:
        # Start MLflow run
        with mlflow.start_run(run_name=training_id) as run:
            # Log parameters
            mlflow.log_params(config)
            
            # Fetch training data
            training_data = await fetch_training_data(
                config['data_start_date'],
                config['data_end_date']
            )
            
            # Prepare features
            X, y = prepare_training_features(training_data, config['model_type'])
            
            # Train model
            if config['model_type'] == 'lstm':
                model, metrics = train_lstm_model(X, y, config.get('hyperparameters', {}))
            elif config['model_type'] == 'xgboost':
                model, metrics = train_xgboost_model(X, y, config.get('hyperparameters', {}))
            else:
                raise ValueError(f"Unsupported model type: {config['model_type']}")
            
            # Log metrics
            mlflow.log_metrics(metrics)
            
            # Save model
            model_name = f"rockfall_{config['model_type']}_{training_id}"
            
            if config['model_type'] == 'lstm':
                mlflow.pytorch.log_model(model, "model", registered_model_name=model_name)
            else:
                mlflow.sklearn.log_model(model, "model", registered_model_name=model_name)
            
            # Auto-deploy if requested and performance is good
            if config['auto_deploy'] and metrics.get('accuracy', 0) > 0.85:
                # Promote to production
                model_version = mlflow_client.get_latest_versions(model_name)[0]
                mlflow_client.transition_model_version_stage(
                    name=model_name,
                    version=model_version.version,
                    stage="Production"
                )
                
                # Load new model
                await model_manager.load_model(model_name, config['model_type'])
                
            logger.info("Model training completed",
                       training_id=training_id,
                       model_name=model_name,
                       accuracy=metrics.get('accuracy', 0))
                       
    except Exception as e:
        logger.error("Model training failed", training_id=training_id, error=str(e))

async def fetch_training_data(start_date: datetime, end_date: datetime) -> pd.DataFrame:
    """Fetch training data from database"""
    async with async_session() as session:
        query = """
            SELECT sensor_id, sensor_type, location_lat, location_lon,
                   timestamp, value, quality_score
            FROM sensor_readings
            WHERE timestamp BETWEEN $1 AND $2
            ORDER BY timestamp
        """
        
        result = await session.execute(query, [start_date, end_date])
        rows = await result.fetchall()
        
        return pd.DataFrame(rows, columns=[
            'sensor_id', 'sensor_type', 'location_lat', 'location_lon',
            'timestamp', 'value', 'quality_score'
        ])

def prepare_training_features(data: pd.DataFrame, model_type: str) -> Tuple[np.ndarray, np.ndarray]:
    """Prepare features for training"""
    # Feature engineering based on model type
    if model_type == 'lstm':
        # Time series features for LSTM
        features = feature_engineer.extract_time_series_features(data)
        X = features[['mean', 'std', 'min', 'max', 'trend']].values
        y = (features['max'] > features['mean'] + 2 * features['std']).astype(int).values
        
        # Create sequences
        X, y = feature_engineer.create_sequences(X, sequence_length=24)
        
    else:
        # Statistical features for traditional ML
        features = feature_engineer.extract_time_series_features(data)
        X = features[['mean', 'std', 'min', 'max', 'trend', 'skewness', 'kurtosis']].values
        y = (features['max'] > features['mean'] + 2 * features['std']).astype(int).values
    
    return X, y

def train_lstm_model(X: np.ndarray, y: np.ndarray, hyperparams: Dict[str, Any]) -> Tuple[nn.Module, Dict[str, float]]:
    """Train LSTM model"""
    # Model parameters
    input_size = X.shape[-1]
    hidden_size = hyperparams.get('hidden_size', 128)
    num_layers = hyperparams.get('num_layers', 3)
    learning_rate = hyperparams.get('learning_rate', 0.001)
    epochs = hyperparams.get('epochs', 100)
    batch_size = hyperparams.get('batch_size', 32)
    
    # Initialize model
    model = RockfallLSTM(
        input_size=input_size,
        hidden_size=hidden_size,
        num_layers=num_layers
    ).to(device)
    
    # Training setup
    criterion = nn.BCELoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=learning_rate)
    
    # Convert to tensors
    X_tensor = torch.FloatTensor(X).to(device)
    y_tensor = torch.FloatTensor(y.reshape(-1, 1)).to(device)
    
    # Training loop
    model.train()
    for epoch in range(epochs):
        optimizer.zero_grad()
        outputs = model(X_tensor)
        loss = criterion(outputs, y_tensor)
        loss.backward()
        optimizer.step()
        
        if epoch % 10 == 0:
            logger.info(f"Epoch {epoch}/{epochs}, Loss: {loss.item():.4f}")
    
    # Calculate metrics
    model.eval()
    with torch.no_grad():
        predictions = model(X_tensor)
        predicted_classes = (predictions > 0.5).float()
        accuracy = (predicted_classes == y_tensor).float().mean().item()
    
    metrics = {
        "accuracy": accuracy,
        "final_loss": loss.item()
    }
    
    return model, metrics

def train_xgboost_model(X: np.ndarray, y: np.ndarray, hyperparams: Dict[str, Any]) -> Tuple[Any, Dict[str, float]]:
    """Train XGBoost model"""
    from xgboost import XGBClassifier
    from sklearn.model_selection import train_test_split
    from sklearn.metrics import accuracy_score, precision_score, recall_score
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    
    # Model parameters
    params = {
        'n_estimators': hyperparams.get('n_estimators', 100),
        'max_depth': hyperparams.get('max_depth', 6),
        'learning_rate': hyperparams.get('learning_rate', 0.1),
        'random_state': 42
    }
    
    # Train model
    model = XGBClassifier(**params)
    model.fit(X_train, y_train)
    
    # Calculate metrics
    y_pred = model.predict(X_test)
    metrics = {
        "accuracy": accuracy_score(y_test, y_pred),
        "precision": precision_score(y_test, y_pred, average='weighted'),
        "recall": recall_score(y_test, y_pred, average='weighted')
    }
    
    return model, metrics

@app.get("/stats")
async def get_ml_stats():
    """Get ML pipeline statistics"""
    try:
        return {
            "status": "operational",
            "loaded_models": len(model_manager.models),
            "active_experiments": len(mlflow_client.list_experiments()),
            "device": str(device),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    except Exception as e:
        logger.error("Error getting ML stats", error=str(e))
        raise HTTPException(status_code=500, detail="Stats retrieval failed")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8002,
        reload=True,
        log_level="info"
    )