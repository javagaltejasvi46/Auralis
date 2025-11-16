@echo off
echo Installing Faster-Whisper for Python 3.14...
echo.

echo Step 1: Installing core dependencies...
pip install --upgrade pip setuptools wheel

echo.
echo Step 2: Installing ctranslate2...
pip install ctranslate2

echo.
echo Step 3: Installing huggingface-hub...
pip install huggingface-hub

echo.
echo Step 4: Installing tokenizers (pre-built)...
pip install tokenizers --only-binary :all:

echo.
echo Step 5: Installing av (PyAV)...
pip install av --only-binary :all:

echo.
echo Step 6: Installing faster-whisper (forcing compatible av version)...
pip install "faster-whisper>=1.0" --no-deps
pip install "av>=16.0"

echo.
echo Step 7: Installing indic-transliteration (for Hindi script)...
pip install indic-transliteration

echo.
echo Step 8: Installing onnxruntime (optional, for VAD)...
pip install onnxruntime --only-binary :all:

echo.
echo Step 9: Checking FFmpeg...
ffmpeg -version >nul 2>&1
if %errorlevel% neq 0 (
    echo WARNING: FFmpeg not found!
    echo Please install: winget install Gyan.FFmpeg.Essentials
    echo FFmpeg is required for audio conversion.
) else (
    echo FFmpeg OK!
)

echo.
echo Installation complete!
pause
