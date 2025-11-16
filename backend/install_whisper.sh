#!/bin/bash
# Faster-Whisper Installation Script for Linux/Mac

echo "Installing Faster-Whisper for Python..."
echo ""

echo "Step 1: Upgrading pip, setuptools, wheel..."
pip install --upgrade pip setuptools wheel

echo ""
echo "Step 2: Installing ctranslate2..."
pip install ctranslate2

echo ""
echo "Step 3: Installing huggingface-hub..."
pip install huggingface-hub

echo ""
echo "Step 4: Installing tokenizers (pre-built)..."
pip install tokenizers --only-binary :all:

echo ""
echo "Step 5: Installing av (PyAV)..."
pip install av --only-binary :all:

echo ""
echo "Step 6: Installing faster-whisper..."
pip install "faster-whisper>=1.0" --no-deps
pip install "av>=16.0"

echo ""
echo "Step 7: Checking FFmpeg..."
if command -v ffmpeg &> /dev/null
then
    echo "FFmpeg OK!"
    ffmpeg -version | head -n 1
else
    echo "WARNING: FFmpeg not found!"
    echo "Please install FFmpeg:"
    echo "  macOS: brew install ffmpeg"
    echo "  Ubuntu/Debian: sudo apt install ffmpeg"
    echo "  Fedora: sudo dnf install ffmpeg"
fi

echo ""
echo "Installation complete!"
echo ""
echo "To start the server:"
echo "  python transcription_server.py"
