# Auralis Setup Guide
## Quick Setup for New Laptop

This guide will help you set up Auralis on a new laptop with all required AI models.

---

## Prerequisites

Before running the setup scripts, ensure you have:

1. **Python 3.8 or higher**
   - Download: https://www.python.org/downloads/
   - During installation, check "Add Python to PATH"

2. **Node.js 16 or higher** (for frontend)
   - Download: https://nodejs.org/

3. **Git** (to clone the repository)
   - Download: https://git-scm.com/downloads

4. **Internet Connection**
   - Required to download models (~4GB total)

---

## Quick Setup (Recommended)

### Option 1: Python Script (Cross-platform)

```bash
# Run the automated setup script
python setup_models.py
```

This script will:
- ✓ Check Python version
- ✓ Install/check Ollama
- ✓ Download Phi-3-Mini model (~2.5GB)
- ✓ Install Python dependencies
- ✓ Download Faster-Whisper model (~1.5GB)
- ✓ Verify all components

### Option 2: Windows Batch Script

```cmd
# Double-click or run:
setup_models.bat
```

### Option 3: PowerShell Script

```powershell
# Run in PowerShell:
.\setup_models.ps1
```

---

## Manual Setup (Step-by-Step)

If you prefer to set up manually or the automated scripts fail:

### Step 1: Install Ollama

**Windows:**
1. Download from: https://ollama.ai/download/windows
2. Run the installer
3. Ollama will start automatically

**macOS:**
```bash
curl -fsSL https://ollama.ai/install.sh | sh
```

**Linux:**
```bash
curl -fsSL https://ollama.ai/install.sh | sh
```

### Step 2: Download Phi-3-Mini Model

```bash
# This downloads ~2.5GB
ollama pull phi3:mini
```

Wait for download to complete (5-10 minutes depending on internet speed).

### Step 3: Verify Phi-3 Model

```bash
# Test the model
ollama run phi3:mini "Hello, are you working?"
```

You should see a response from the model.

### Step 4: Install Python Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### Step 5: Download Faster-Whisper Model

The Whisper model will download automatically on first use, or you can pre-download:

```python
python -c "from faster_whisper import WhisperModel; WhisperModel('medium', device='cpu', compute_type='int8')"
```

This downloads ~1.5GB to your cache directory.

---

## Verification

### Check All Components

Run this command to verify everything is set up:

```bash
python setup_models.py
```

It will show a status report like:

```
Component Status:
----------------------------------------
✓ Python 3.8+
✓ Ollama Installed
✓ Ollama Running
✓ Phi-3-Mini Model
✓ Faster-Whisper Model
========================================
All components are ready!
```

### Test Backend

```bash
# Terminal 1: Start API server
python backend/main.py

# Terminal 2: Start transcription server
python backend/transcription_server.py
```

Visit http://localhost:8002/docs to see the API documentation.

### Test Frontend

```bash
cd frontend
npm install
npx expo start
```

Scan the QR code with Expo Go app on your phone.

---

## Troubleshooting

### Ollama Not Found

**Problem:** `ollama: command not found`

**Solution:**
1. Install Ollama from https://ollama.ai/download
2. Restart your terminal
3. On Windows, restart your computer if needed

### Ollama Service Not Running

**Problem:** `Error: could not connect to ollama app`

**Solution:**
- **Windows**: Start Ollama from Start Menu or system tray
- **macOS/Linux**: Run `ollama serve` in a terminal

### Phi-3 Model Download Fails

**Problem:** Download interrupted or fails

**Solution:**
```bash
# Try again
ollama pull phi3:mini

# Or use a different mirror (if available)
ollama pull phi3:mini --insecure
```

### Python Dependencies Fail

**Problem:** `pip install` fails

**Solution:**
```bash
# Upgrade pip first
python -m pip install --upgrade pip

# Try again
pip install -r backend/requirements.txt

# Or install individually
pip install fastapi uvicorn sqlalchemy faster-whisper websockets
```

### Whisper Model Download Fails

**Problem:** Whisper model download interrupted

**Solution:**
```bash
# Clear cache and retry
rm -rf ~/.cache/huggingface

# Download again
python -c "from faster_whisper import WhisperModel; WhisperModel('medium')"
```

### Out of Disk Space

**Problem:** Not enough space for models

**Solution:**
- Phi-3-Mini: ~2.5GB
- Faster-Whisper: ~1.5GB
- Total needed: ~5GB (including dependencies)

Free up space and try again.

---

## Model Locations

### Phi-3-Mini (via Ollama)
- **Windows**: `C:\Users\<username>\.ollama\models`
- **macOS**: `~/.ollama/models`
- **Linux**: `~/.ollama/models`

### Faster-Whisper
- **Windows**: `C:\Users\<username>\.cache\huggingface\hub`
- **macOS**: `~/.cache/huggingface/hub`
- **Linux**: `~/.cache/huggingface/hub`

---

## System Requirements

### Minimum Requirements
- **CPU**: 4 cores
- **RAM**: 8GB
- **Disk**: 10GB free space
- **OS**: Windows 10+, macOS 10.15+, Ubuntu 20.04+

### Recommended Requirements
- **CPU**: 8 cores
- **RAM**: 16GB
- **Disk**: 20GB free space
- **GPU**: NVIDIA GPU with 8GB+ VRAM (optional, for faster processing)

---

## Performance Expectations

### CPU-Only (No GPU)
- **Transcription**: 30-60 seconds per minute of audio
- **Summarization**: 10-15 seconds per summary
- **Concurrent Users**: 2-5

### With GPU (NVIDIA)
- **Transcription**: 5-10 seconds per minute of audio
- **Summarization**: 2-4 seconds per summary
- **Concurrent Users**: 10-20

---

## Next Steps

After setup is complete:

1. **Configure Gemini API** (optional, for fallback):
   - Get API key from: https://makersuite.google.com/app/apikey
   - Update `backend/summarization_service.py`

2. **Start Backend**:
   ```bash
   python backend/main.py
   python backend/transcription_server.py
   ```

3. **Start Frontend**:
   ```bash
   cd frontend
   npx expo start
   ```

4. **Test the App**:
   - Scan QR code with Expo Go
   - Register a therapist account
   - Create a patient
   - Record a test session

---

## Getting Help

If you encounter issues:

1. Check the troubleshooting section above
2. Review the error messages carefully
3. Check system requirements
4. Ensure internet connection is stable
5. Try running setup scripts again

For more help:
- Backend docs: `backend/README.md`
- Frontend docs: `frontend/README.md`
- Full documentation: `PRESENTATION_DOCUMENTATION.md`

---

## Quick Reference

### Start Backend
```bash
# Windows
start_backend.bat

# PowerShell
.\start_backend.ps1

# Manual
python backend/main.py  # Terminal 1
python backend/transcription_server.py  # Terminal 2
```

### Check Model Status
```bash
# Check Ollama models
ollama list

# Check Whisper cache
ls ~/.cache/huggingface/hub  # macOS/Linux
dir %USERPROFILE%\.cache\huggingface\hub  # Windows
```

### Test Models
```bash
# Test Phi-3
ollama run phi3:mini "Hello"

# Test Whisper (will download if needed)
python -c "from faster_whisper import WhisperModel; m = WhisperModel('medium'); print('OK')"
```

---

**Setup complete! You're ready to use Auralis.**

