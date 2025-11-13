@echo off
echo Starting Transcription Server...
echo.
echo Checking FFmpeg...
ffmpeg -version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: FFmpeg not found!
    echo Please install: winget install Gyan.FFmpeg.Essentials
    echo Then restart this terminal.
    pause
    exit /b 1
)
echo FFmpeg OK!
echo.
echo Starting WebSocket server on port 8003...
python transcription_server.py
