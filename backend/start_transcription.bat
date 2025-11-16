@echo off
echo Starting Faster-Whisper Transcription Server...
echo.
echo Checking Faster-Whisper installation...
python -c "from faster_whisper import WhisperModel" 2>nul
if %errorlevel% neq 0 (
    echo ERROR: Faster-Whisper not installed!
    echo Please run: .\install_whisper.bat
    pause
    exit /b 1
)
echo.
echo Starting Faster-Whisper WebSocket server on port 8003...
python transcription_server.py
