@echo off
echo ============================================================
echo 🚀 Starting React Frontend Dashboard
echo ============================================================
echo.
echo Installing dependencies (first time only)...
cd /d "%~dp0\frontend"
if not exist "node_modules" (
    echo Installing npm packages...
    npm install
    echo.
)

echo Starting React development server...
echo Dashboard will open at: http://localhost:3000
echo Backend API should be running at: http://localhost:5000
echo.
npm start

pause