@echo off
echo ========================================
echo AURALIS Backend Startup Script
echo ========================================
echo.

REM Change to backend directory
cd backend

echo [1/3] Running auto-configuration...
python auto_config.py
echo.

echo [2/3] Starting main API server (port 8002)...
start "Auralis API Server" cmd /k "python main.py"
timeout /t 3 /nobreak >nul

echo [3/3] Starting transcription server (port 8003)...
start "Auralis Transcription Server" cmd /k "python transcription_server.py"

echo.
echo ========================================
echo ✅ All backend services started!
echo ========================================
echo.
echo API Server: http://localhost:8002
echo Transcription: ws://localhost:8003
echo.
echo Press any key to exit this window...
pause >nul
