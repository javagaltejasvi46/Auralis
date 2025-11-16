@echo off
echo Starting Whisper Transcription Server...
echo.
echo Checking dependencies...
python -c "import whisper" 2>nul
if %errorlevel% neq 0 (
    echo ERROR: Whisper not installed!
    echo Installing Whisper...
    pip install openai-whisper
)

python -c "import pydub" 2>nul
if %errorlevel% neq 0 (
    echo Installing pydub...
    pip install pydub
)

echo.
echo Starting Whisper server on port 8003...
python transcription_server_whisper.py
