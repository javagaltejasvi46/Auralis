@echo off
echo ============================================
echo AURALIS Backend - Complete Installation
echo ============================================
echo.

echo Step 1: Upgrading pip, setuptools, and wheel...
python -m pip install --upgrade pip setuptools wheel
echo.

echo Step 2: Installing core dependencies...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo ERROR: Failed to install core dependencies
    pause
    exit /b 1
)
echo.

echo Step 3: Installing Faster-Whisper dependencies...
pip install ctranslate2 huggingface-hub tokenizers
if %errorlevel% neq 0 (
    echo ERROR: Failed to install Whisper dependencies
    pause
    exit /b 1
)
echo.

echo Step 4: Installing PyAV (audio processing)...
pip install av --only-binary :all:
if %errorlevel% neq 0 (
    echo WARNING: PyAV installation failed, trying alternative...
    pip install av
)
echo.

echo Step 5: Installing Faster-Whisper...
pip install faster-whisper --no-deps
pip install "av>=16.0"
if %errorlevel% neq 0 (
    echo ERROR: Failed to install Faster-Whisper
    pause
    exit /b 1
)
echo.

echo Step 6: Verifying installation...
python -c "import fastapi; print('✅ FastAPI:', fastapi.__version__)"
python -c "import websockets; print('✅ WebSockets:', websockets.__version__)"
python -c "from faster_whisper import WhisperModel; print('✅ Faster-Whisper: OK')"
python -c "import sqlalchemy; print('✅ SQLAlchemy:', sqlalchemy.__version__)"
python -c "from deep_translator import GoogleTranslator; print('✅ Deep-Translator: OK')"
echo.

echo Step 7: Checking FFmpeg...
ffmpeg -version >nul 2>&1
if %errorlevel% neq 0 (
    echo ⚠️  WARNING: FFmpeg not found!
    echo Please install: winget install Gyan.FFmpeg.Essentials
    echo FFmpeg is required for audio conversion.
    echo.
) else (
    echo ✅ FFmpeg: OK
    echo.
)

echo ============================================
echo Installation Complete!
echo ============================================
echo.
echo Next steps:
echo 1. Start HTTP API: python main.py
echo 2. Start WebSocket: python transcription_server.py
echo.
echo Note: First run will download Whisper model (~1.5GB)
echo.
pause
