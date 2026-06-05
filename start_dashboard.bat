@echo off
title Shack Dashboard
echo Starting Shack Entertainment Dashboard...
cd /d "%~dp0"
py -m streamlit run dashboard.py
pause