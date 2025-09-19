@echo off
echo ============================================================
echo 🎯 AI Rockfall System - FULL STACK DEMO
echo ============================================================
echo.
echo Starting complete system with React Frontend:
echo 1. Flask Backend API (Port 5000)
echo 2. React Frontend Dashboard (Port 3000)
echo.
echo Press any key to continue, or Ctrl+C to cancel...
pause >nul

echo.
echo 🚀 Starting Backend API Server...
start cmd /k "cd /d "%~dp0" && venv\Scripts\activate && cd backend && python app.py"

echo ⏳ Waiting 5 seconds for API to initialize...
timeout /t 5 /nobreak >nul

echo.
echo 📊 Installing Frontend Dependencies (if needed)...
cd /d "%~dp0\frontend"
if not exist "node_modules" (
    echo Installing npm packages...
    npm install
    echo.
)

echo 🌐 Starting React Frontend Dashboard...
start cmd /k "cd /d "%~dp0\frontend" && npm start"

echo.
echo ============================================================
echo ✅ FULL STACK DEMO STARTED SUCCESSFULLY!
echo ============================================================
echo.
echo 🌐 Frontend Dashboard: http://localhost:3000
echo 🔧 Backend API: http://localhost:5000
echo.
echo 📝 Demo Instructions:
echo • The React dashboard will open automatically in your browser
echo • Modern UI with real-time data and interactive charts
echo • Click on mine zones to see detailed information
echo • Monitor alerts and system status in real-time
echo.
echo ⚠️  To stop the demo: Close both command prompt windows
echo.
echo 🎉 Enjoy your modern React-based mine safety dashboard!
echo ============================================================
pause