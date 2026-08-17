@echo off
cd /d C:\Users\Bola\Documents\Shack_Project\Scripts
:loop
py shack_alerts.py "Shack bot online."
py shack_main_agent.py
echo [WATCHDOG] Bot exited (code %errorlevel%). Restarting in 5 seconds...
py shack_alerts.py "Shack bot CRASHED (code %errorlevel%). Auto-restarting now."
timeout /t 5 >nul
goto loop