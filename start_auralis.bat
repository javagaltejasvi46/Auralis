@echo off
echo ========================================
echo    AURALIS - Medical Voice Transcription
echo ========================================
echo.

cd /d "%~dp0"

echo Starting Auralis Backend...
echo.

cd backend
python startup.py

pause