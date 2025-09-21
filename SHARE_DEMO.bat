@echo off
title SIH Demo - PUBLIC SHARING
cls
echo ==============================================
echo    🌍 SIH ROCKFALL DEMO - PUBLIC SHARING
echo ==============================================
echo.
echo Creating public web link for sharing...
echo.

REM Start backend for network access
echo [1/3] Starting backend server...
start /min cmd /c "cd backend && ..\venv\Scripts\python network_app.py"

REM Start React frontend FIRST
echo [2/3] Starting dashboard...
start /min cmd /c "cd frontend && npm start"

REM Wait for React app to fully start
echo Waiting for React app to start completely...
echo This may take 30-60 seconds for first time...
timeout /t 45 /nobreak >nul

REM Now start ngrok tunnel after React is ready
echo [3/3] Creating public tunnel...
start cmd /c "ngrok http 3000"

echo.
echo ✅ Setting up public access...
echo.
echo ⏳ Please wait 30 seconds for everything to start...
echo.
echo 🌍 Your demo will be available at a public URL!
echo 📋 Check the ngrok window for your public link
echo.
echo Instructions:
echo 1. Look for the ngrok window that opened
echo 2. Find the line that says "Forwarding https://xxxxx.ngrok.io"
echo 3. Share that https://xxxxx.ngrok.io link with anyone!
echo.
echo Press any key to close this window...
pause >nul