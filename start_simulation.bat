@echo off
echo Starting Data Simulation...
cd backend
python data_ingest.py --mode simulate --duration 60
pause
