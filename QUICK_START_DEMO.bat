@echo off
echo ============================================================
echo 🎯 AI-Based Rockfall Prediction System - QUICK START DEMO
echo ============================================================
echo.
echo This will start the complete demo system automatically:
echo 1. Backend API Server (Port 5000)
echo 2. Streamlit Dashboard (Port 8501)
echo.
echo Press any key to continue, or Ctrl+C to cancel...
pause >nul

echo.
echo 🚀 Starting Backend API Server...
start cmd /k "cd /d "%~dp0" && venv\Scripts\activate && cd backend && python app.py"

echo ⏳ Waiting 5 seconds for API to initialize...
timeout /t 5 /nobreak >nul

echo.
echo 📊 Starting Streamlit Dashboard...
start cmd /k "cd /d "%~dp0" && venv\Scripts\activate && cd dashboard && streamlit run streamlit_app.py"

pause