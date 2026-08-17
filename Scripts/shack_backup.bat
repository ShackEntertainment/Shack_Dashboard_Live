@echo off
cd /d C:\Users\Bola\Documents\Shack_Project
git add -A
git commit -m "auto backup %date% %time%"
git push origin main