@echo off
title SIH Rockfall Demo
cls
echo ==============================================
echo    🚀 SIH ROCKFALL PREDICTION DEMO
echo ==============================================
echo.
echo Starting system components...
echo.

REM Start backend
echo [1/3] Starting backend server...
start /min cmd /c "cd backend && ..\venv\Scripts\python simple_app.py"

REM Wait for backend to start
timeout /t 2 /nobreak >nul

REM Start React frontend
echo [2/3] Starting React dashboard...
start /min cmd /c "cd frontend && npm start"

REM Wait for React to start
echo [3/3] Waiting for dashboard to load...
timeout /t 10 /nobreak >nul

REM Open browser to dashboard (npm won't auto-open now)
echo Opening dashboard in browser...
start "" "http://localhost:3000"

echo.
echo ✅ Demo is starting!
echo ✅ Dashboard will open automatically
echo.
echo Press any key to close this window...
pause >nul