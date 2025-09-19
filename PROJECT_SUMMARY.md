# 🏗️ AI-Based Rockfall Risk Prediction System

## 📋 Project Overview
Complete mine safety monitoring system with AI-powered rockfall prediction, real-time alerts, and dual frontend interfaces.

## 🚀 Quick Start Commands

### Simple Dashboard (Best for Presentations)
```bash
.\SIMPLE_DASHBOARD.bat
```
- **URL:** http://localhost:8501
- **Features:** Easy-to-understand interface, perfect for jury/client presentations
- **Color System:** Green = Safe, Yellow = Caution, Red = Danger

### Modern React Dashboard (Full Features)
```bash
.\REACT_DEMO.bat
```
- **URL:** http://localhost:3000
- **Features:** Interactive maps, charts, login system, fullscreen mode
- **Login Credentials:**
  - admin / admin123
  - demo / demo123
  - john / password

### Technical Dashboard (For Engineers)
```bash
.\QUICK_START_DEMO.bat
```
- **URL:** http://localhost:8501 (Technical version)
- **Features:** Advanced metrics, detailed sensor data, technical analysis

## 🛠️ Tech Stack

### Backend (Python)
- **Flask** - REST API server
- **Scikit-learn** - Machine learning models
- **Pandas** - Data processing
- **SQLite** - Database

### Frontend Options
1. **Streamlit** (Simple) - Pure Python
2. **Streamlit** (Technical) - Advanced Python with charts
3. **React** (Modern) - React + Tailwind + Chart.js + Axios

## 📁 Project Structure
```
├── backend/                 # Flask API server
├── dashboard/              # Streamlit dashboards
│   ├── streamlit_app.py   # Technical dashboard
│   └── simple_app.py      # Simple presentation dashboard
├── frontend/              # React modern dashboard
├── models/                # AI/ML models
├── data/                  # Sample data and databases
├── QUICK_START_DEMO.bat   # Technical Streamlit
├── SIMPLE_DASHBOARD.bat   # Simple Streamlit
└── REACT_DEMO.bat         # Modern React

```

## 🔧 Features Built

### ✅ Working Features
- **Real-time monitoring** - 30-second auto-refresh
- **Zone risk assessment** - AI-powered predictions
- **Interactive mine map** - Click zones for details
- **Alert system** - Critical/Warning notifications
- **Login system** - Secure access with demo accounts
- **Fullscreen mode** - Presentation ready
- **Responsive design** - Works on all devices
- **Data visualization** - Charts and graphs
- **Report generation** - Daily/weekly reports
- **Settings panel** - Configurable thresholds

### 🎯 Presentation Ready
- **Color-coded zones** - Green/Yellow/Red system
- **Professional UI** - Clean, modern interface
- **Live demonstrations** - Real-time refresh button
- **Clear explanations** - No technical jargon in simple version
- **Multiple views** - Technical and business-friendly

## 🆘 If You Need Help Later

### Common Issues & Solutions
1. **Login not working?** 
   - Use: admin / admin123
   - Check browser console (F12)

2. **React page won't load?**
   - Run: `cd frontend && npm install`
   - Then: `.\REACT_DEMO.bat`

3. **Streamlit errors?**
   - Activate virtual environment: `venv\Scripts\activate`
   - Install packages: `pip install -r requirements.txt`

4. **API errors?**
   - Backend might not be running
   - Check if localhost:5000 is accessible

### Development Commands
```bash
# Activate Python environment
venv\Scripts\activate

# Install Python packages
pip install -r requirements.txt

# Start backend only
cd backend && python app.py

# Start React development
cd frontend && npm start

# Install React packages
cd frontend && npm install
```

## 📝 What We Built Together
- Complete AI rockfall prediction system
- 3 different dashboard interfaces
- Login/authentication system
- Real-time data monitoring
- Interactive mine safety visualization
- Professional presentation tools
- Working buttons and navigation
- Settings and configuration panels
- Report generation system
- Fullscreen presentation mode

## 💡 Future Enhancements
- Email/SMS alert integration
- Database connectivity
- More AI models
- Mobile app version
- Advanced reporting
- User management system

---
**Created:** September 2025  
**Tech Stack:** Python (Flask/Streamlit) + React + AI/ML  
**Purpose:** Mine safety monitoring and rockfall risk prediction  
**Status:** Fully functional demo system ready for presentations