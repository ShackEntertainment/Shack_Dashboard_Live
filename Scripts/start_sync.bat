@echo off
echo Starting Shack Data Sync Agent...
cd /d "%~dp0agents_v2"
python data_sync.py
pause