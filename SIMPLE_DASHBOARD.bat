@echo off
echo ===============================================
echo   MINE SAFETY MONITOR - SIMPLE DASHBOARD
echo ===============================================
echo.
echo Starting Simple Dashboard...
echo Navigate to: http://localhost:8501
echo.
echo This is a SIMPLE, EASY-TO-UNDERSTAND version!
echo - Green = Safe Areas
echo - Yellow = Be Careful  
echo - Red = Danger Zones
echo - No confusing technical terms
echo.
echo Press any key to start...
pause >nul

cd /d "%~dp0dashboard"
streamlit run simple_app.py --server.port 8501