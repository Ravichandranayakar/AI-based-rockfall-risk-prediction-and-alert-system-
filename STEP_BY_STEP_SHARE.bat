@echo off
title SIH Demo - STEP BY STEP SHARING
cls
echo ==============================================
echo    🌍 SIH DEMO - STEP BY STEP SHARING
echo ==============================================
echo.
echo Follow these steps to create your public link:
echo.

echo STEP 1: Starting React Dashboard...
echo =====================================
start cmd /c "cd frontend && npm start"
echo ✅ React app is starting (this takes 30-60 seconds)
echo ⏳ Wait for browser to open with http://localhost:3000
echo.

echo STEP 2: Starting Backend...
echo ===========================
start /min cmd /c "cd backend && ..\venv\Scripts\python network_app.py"
echo ✅ Backend server is starting
echo.

echo STEP 3: Instructions for ngrok tunnel...
echo =======================================
echo.
echo 🔴 IMPORTANT: Only proceed when you see your dashboard at localhost:3000
echo.
echo When your React app is ready, press any key to create public tunnel...
pause >nul

echo.
echo Creating public tunnel now...
start cmd /c "ngrok http 3000"

echo.
echo ✅ Done! Look for the ngrok window that just opened
echo 📋 Copy the https://xxxxx.ngrok.io link from that window
echo 🌍 Share that link with anyone worldwide!
echo.
echo Press any key to close this window...
pause >nul