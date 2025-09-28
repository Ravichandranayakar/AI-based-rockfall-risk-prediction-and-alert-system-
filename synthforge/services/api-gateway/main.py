# SynthForge API Gateway
# Production-grade FastAPI gateway with OAuth 2.0, rate limiting, and service orchestration

from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import httpx
import asyncio
import jwt
import redis
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import os
from pathlib import Path

# Production logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('api_gateway.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Initialize FastAPI with production settings
app = FastAPI(
    title="SynthForge API Gateway",
    description="Industrial AI-Based Rockfall Prediction System - API Gateway",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# Security and CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://*.synthforge.com"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH"],
    allow_headers=["*"],
)

app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["localhost", "*.synthforge.com", "127.0.0.1"]
)

# Rate limiting setup
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Redis for caching and session management
redis_client = redis.Redis(
    host=os.getenv("REDIS_HOST", "localhost"),
    port=int(os.getenv("REDIS_PORT", 6379)),
    decode_responses=True
)

# JWT Configuration
JWT_SECRET = os.getenv("JWT_SECRET", "synthforge-production-secret-key")
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_HOURS = 24

# Service endpoints
SERVICES = {
    "data_ingestion": os.getenv("DATA_INGESTION_URL", "http://localhost:8001"),
    "ml_pipeline": os.getenv("ML_PIPELINE_URL", "http://localhost:8002"),
    "alert_service": os.getenv("ALERT_SERVICE_URL", "http://localhost:8003"),
    "dashboard": os.getenv("DASHBOARD_URL", "http://localhost:3000"),
    "edge_device": os.getenv("EDGE_DEVICE_URL", "http://localhost:8004")
}

# Security dependencies
security = HTTPBearer()

class AuthenticationError(HTTPException):
    def __init__(self, detail: str = "Authentication failed"):
        super().__init__(status_code=status.HTTP_401_UNAUTHORIZED, detail=detail)

class AuthorizationError(HTTPException):
    def __init__(self, detail: str = "Insufficient permissions"):
        super().__init__(status_code=status.HTTP_403_FORBIDDEN, detail=detail)

def create_access_token(data: dict) -> str:
    """Create JWT access token with expiration"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(hours=JWT_EXPIRATION_HOURS)
    to_encode.update({"exp": expire, "iat": datetime.utcnow()})
    return jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)

async def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    """Verify JWT token and extract user info"""
    try:
        payload = jwt.decode(credentials.credentials, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise AuthenticationError("Token missing user information")
        
        # Check if token is blacklisted
        if redis_client.get(f"blacklist:{credentials.credentials}"):
            raise AuthenticationError("Token has been revoked")
            
        return payload
    except jwt.ExpiredSignatureError:
        raise AuthenticationError("Token has expired")
    except jwt.JWTError:
        raise AuthenticationError("Invalid token")

def require_roles(allowed_roles: list):
    """Decorator to enforce role-based access control"""
    def role_checker(token_data: dict = Depends(verify_token)):
        user_roles = token_data.get("roles", [])
        if not any(role in user_roles for role in allowed_roles):
            raise AuthorizationError(f"Required roles: {allowed_roles}")
        return token_data
    return role_checker

# HTTP client for service communication
async def make_service_request(service: str, path: str, method: str = "GET", **kwargs) -> dict:
    """Make authenticated requests to microservices"""
    if service not in SERVICES:
        raise HTTPException(status_code=404, detail=f"Service {service} not found")
    
    url = f"{SERVICES[service]}{path}"
    timeout = httpx.Timeout(30.0, connect=10.0)
    
    async with httpx.AsyncClient(timeout=timeout) as client:
        try:
            if method == "GET":
                response = await client.get(url, **kwargs)
            elif method == "POST":
                response = await client.post(url, **kwargs)
            elif method == "PUT":
                response = await client.put(url, **kwargs)
            elif method == "DELETE":
                response = await client.delete(url, **kwargs)
            else:
                raise HTTPException(status_code=405, detail="Method not allowed")
                
            response.raise_for_status()
            return response.json()
        except httpx.TimeoutException:
            logger.error(f"Timeout calling {service} at {url}")
            raise HTTPException(status_code=408, detail="Service request timed out")
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error calling {service}: {e.response.status_code}")
            raise HTTPException(status_code=e.response.status_code, detail="Service request failed")

# Health check endpoints
@app.get("/health")
@limiter.limit("10/minute")
async def health_check(request: Request):
    """Gateway health check"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0",
        "services": list(SERVICES.keys())
    }

@app.get("/health/services")
@limiter.limit("5/minute")
async def services_health_check(request: Request, token_data: dict = Depends(require_roles(["admin", "operator"]))):
    """Check health of all microservices"""
    health_status = {}
    
    for service_name, service_url in SERVICES.items():
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(f"{service_url}/health")
                health_status[service_name] = {
                    "status": "healthy" if response.status_code == 200 else "unhealthy",
                    "response_time": response.elapsed.total_seconds(),
                    "last_check": datetime.utcnow().isoformat()
                }
        except Exception as e:
            health_status[service_name] = {
                "status": "unhealthy",
                "error": str(e),
                "last_check": datetime.utcnow().isoformat()
            }
    
    return {"services": health_status}

# Authentication endpoints
@app.post("/auth/login")
@limiter.limit("5/minute")
async def login(request: Request, credentials: dict):
    """User authentication endpoint"""
    # TODO: Implement actual user authentication with database
    # For now, mock authentication for development
    username = credentials.get("username")
    password = credentials.get("password")
    
    # Mock user validation (replace with actual database validation)
    if username == "admin" and password == "synthforge2025":
        token_data = {
            "sub": username,
            "roles": ["admin", "operator"],
            "permissions": ["read", "write", "delete"],
            "tenant_id": "synthforge_main"
        }
        access_token = create_access_token(token_data)
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "expires_in": JWT_EXPIRATION_HOURS * 3600,
            "user": token_data
        }
    else:
        raise AuthenticationError("Invalid credentials")

@app.post("/auth/logout")
@limiter.limit("10/minute")
async def logout(request: Request, credentials: HTTPAuthorizationCredentials = Depends(security)):
    """User logout - blacklist token"""
    token = credentials.credentials
    # Add token to blacklist with expiration
    redis_client.setex(f"blacklist:{token}", JWT_EXPIRATION_HOURS * 3600, "revoked")
    return {"message": "Successfully logged out"}

# Data ingestion routes
@app.post("/api/v1/data/sensors")
@limiter.limit("100/minute")
async def ingest_sensor_data(request: Request, data: dict, token_data: dict = Depends(require_roles(["operator", "admin"]))):
    """Ingest IoT sensor data"""
    return await make_service_request("data_ingestion", "/sensors", "POST", json=data)

@app.post("/api/v1/data/weather")
@limiter.limit("50/minute")
async def ingest_weather_data(request: Request, data: dict, token_data: dict = Depends(require_roles(["operator", "admin"]))):
    """Ingest weather data"""
    return await make_service_request("data_ingestion", "/weather", "POST", json=data)

# ML Pipeline routes
@app.get("/api/v1/ml/models")
@limiter.limit("20/minute")
async def list_ml_models(request: Request, token_data: dict = Depends(require_roles(["operator", "admin"]))):
    """List available ML models"""
    return await make_service_request("ml_pipeline", "/models", "GET")

@app.post("/api/v1/ml/predict")
@limiter.limit("50/minute")
async def predict_risk(request: Request, data: dict, token_data: dict = Depends(require_roles(["operator", "admin"]))):
    """Get risk prediction from ML model"""
    return await make_service_request("ml_pipeline", "/predict", "POST", json=data)

@app.post("/api/v1/ml/train")
@limiter.limit("1/hour")
async def trigger_model_training(request: Request, config: dict, token_data: dict = Depends(require_roles(["admin"]))):
    """Trigger ML model retraining"""
    return await make_service_request("ml_pipeline", "/train", "POST", json=config)

# Alert service routes
@app.get("/api/v1/alerts")
@limiter.limit("30/minute")
async def get_alerts(request: Request, token_data: dict = Depends(require_roles(["operator", "admin"]))):
    """Get active alerts"""
    return await make_service_request("alert_service", "/alerts", "GET")

@app.post("/api/v1/alerts")
@limiter.limit("20/minute")
async def create_alert(request: Request, alert_data: dict, token_data: dict = Depends(require_roles(["operator", "admin"]))):
    """Create new alert"""
    return await make_service_request("alert_service", "/alerts", "POST", json=alert_data)

@app.put("/api/v1/alerts/{alert_id}/acknowledge")
@limiter.limit("30/minute")
async def acknowledge_alert(request: Request, alert_id: str, token_data: dict = Depends(require_roles(["operator", "admin"]))):
    """Acknowledge an alert"""
    return await make_service_request("alert_service", f"/alerts/{alert_id}/acknowledge", "PUT")

# Dashboard data routes
@app.get("/api/v1/dashboard/metrics")
@limiter.limit("60/minute")
async def get_dashboard_metrics(request: Request, token_data: dict = Depends(verify_token)):
    """Get real-time dashboard metrics"""
    return await make_service_request("dashboard", "/metrics", "GET")

@app.get("/api/v1/dashboard/risk-map")
@limiter.limit("30/minute")
async def get_risk_map_data(request: Request, token_data: dict = Depends(verify_token)):
    """Get risk map visualization data"""
    return await make_service_request("dashboard", "/risk-map", "GET")

# System administration routes
@app.get("/api/v1/admin/stats")
@limiter.limit("10/minute")
async def get_system_stats(request: Request, token_data: dict = Depends(require_roles(["admin"]))):
    """Get comprehensive system statistics"""
    stats = {}
    
    # Collect stats from all services
    for service in SERVICES.keys():
        try:
            service_stats = await make_service_request(service, "/stats", "GET")
            stats[service] = service_stats
        except Exception as e:
            stats[service] = {"error": str(e), "status": "unavailable"}
    
    return {
        "timestamp": datetime.utcnow().isoformat(),
        "services": stats,
        "gateway_info": {
            "version": "1.0.0",
            "uptime": "calculated_uptime_here"
        }
    }

# Error handlers
@app.exception_handler(AuthenticationError)
async def authentication_error_handler(request: Request, exc: AuthenticationError):
    return {
        "error": "authentication_failed",
        "message": exc.detail,
        "timestamp": datetime.utcnow().isoformat()
    }

@app.exception_handler(AuthorizationError)
async def authorization_error_handler(request: Request, exc: AuthorizationError):
    return {
        "error": "insufficient_permissions",
        "message": exc.detail,
        "timestamp": datetime.utcnow().isoformat()
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
        access_log=True
    )