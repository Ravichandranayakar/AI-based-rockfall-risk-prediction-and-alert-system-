# SynthForge - Simplified Architecture

## 📁 CLEAN PROJECT STRUCTURE

```
synthforge/
├── README.md                 # This file
├── docker-compose.simple.yml # Simple 3-service setup
├── backend/                  # Single Python backend
│   ├── main.py              # FastAPI app
│   ├── requirements.txt     # Dependencies
│   └── Dockerfile           # Docker build
├── frontend/                # React dashboard
│   ├── src/
│   ├── package.json
│   └── Dockerfile
└── database/
    └── init.sql            # Database setup
```

## 🎯 ONLY 3 SERVICES:

### 1. **Backend API** (Python FastAPI)
- ✅ Sensor data endpoints
- ✅ Prediction API (plug your model here)
- ✅ Alert system
- ✅ Authentication

### 2. **Frontend Dashboard** (React)
- ✅ Real-time charts
- ✅ Risk monitoring
- ✅ Mobile responsive

### 3. **Database** (PostgreSQL)
- ✅ Store sensor data
- ✅ Store predictions
- ✅ Store alerts

## 🚀 HOW TO RUN:

```bash
# Start everything
docker-compose -f docker-compose.simple.yml up

# Access:
Frontend: http://localhost:3000
Backend API: http://localhost:8000
Database: localhost:5432
```

## 🔧 WHERE YOUR TEAM PLUGS IN MODEL:

**File:** `backend/main.py`
**Function:** `predict_rockfall()`
**Replace with your trained model**

## 💡 BENEFITS:
- ✅ **3 services instead of 15**
- ✅ **Easy to understand**
- ✅ **Quick to deploy**
- ✅ **Actually works**
- ✅ **Your team can focus on ML**

---

**SIMPLE = BETTER** 🎯