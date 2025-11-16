# Installation Guide - AURALIS

Complete step-by-step installation instructions for all platforms.

## Table of Contents
- [Windows Installation](#windows-installation)
- [macOS Installation](#macos-installation)
- [Linux Installation](#linux-installation)
- [Docker Installation](#docker-installation)
- [Troubleshooting](#troubleshooting)

---

## Windows Installation

### Prerequisites

1. **Python 3.10-3.13**
   ```powershell
   # Download from python.org or use winget
   winget install Python.Python.3.11
   ```

2. **Node.js 16+**
   ```powershell
   winget install OpenJS.NodeJS
   ```

3. **FFmpeg**
   ```powershell
   winget install Gyan.FFmpeg.Essentials
   ```

4. **Git**
   ```powershell
   winget install Git.Git
   ```

### Backend Setup

```powershell
# Clone repository
git clone <your-repo-url>
cd Auralis\backend

# Create virtual environment (recommended)
python -m venv venv
.\venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install Faster-Whisper
.\install_whisper.bat

# Start servers (open 2 terminals)
# Terminal 1:
python main.py

# Terminal 2:
.\start_transcription.bat
```

### Frontend Setup

```powershell
# Open new terminal
cd Auralis\frontend

# Install dependencies
npm install

# Update IP address in App.tsx
# Find your IP: ipconfig
# Edit frontend/App.tsx and replace IP addresses

# Start Expo
npx expo start

# Scan QR code with Expo Go app on your phone
```

---

## macOS Installation

### Prerequisites

1. **Homebrew** (if not installed)
   ```bash
   /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
   ```

2. **Python 3.10-3.13**
   ```bash
   brew install python@3.11
   ```

3. **Node.js**
   ```bash
   brew install node
   ```

4. **FFmpeg**
   ```bash
   brew install ffmpeg
   ```

### Backend Setup

```bash
# Clone repository
git clone <your-repo-url>
cd Auralis/backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
pip install -r requirements_whisper.txt
pip install faster-whisper

# Start servers (open 2 terminals)
# Terminal 1:
python main.py

# Terminal 2:
python transcription_server.py
```

### Frontend Setup

```bash
# Open new terminal
cd Auralis/frontend

# Install dependencies
npm install

# Update IP address
# Find your IP: ifconfig | grep "inet "
# Edit frontend/App.tsx

# Start Expo
npx expo start

# Scan QR code with Expo Go app
```

---

## Linux Installation

### Prerequisites (Ubuntu/Debian)

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python
sudo apt install python3.11 python3.11-venv python3-pip -y

# Install Node.js
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install nodejs -y

# Install FFmpeg
sudo apt install ffmpeg -y

# Install Git
sudo apt install git -y
```

### Backend Setup

```bash
# Clone repository
git clone <your-repo-url>
cd Auralis/backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
pip install -r requirements_whisper.txt
pip install faster-whisper

# Start servers (use tmux or screen for multiple terminals)
# Terminal 1:
python main.py

# Terminal 2:
python transcription_server.py
```

### Frontend Setup

```bash
# Open new terminal
cd Auralis/frontend

# Install dependencies
npm install

# Update IP address
# Find your IP: ip addr show | grep inet
# Edit frontend/App.tsx

# Start Expo
npx expo start

# Scan QR code with Expo Go app
```

---

## Docker Installation

### Prerequisites

1. **Docker Desktop**
   - Windows: Download from docker.com
   - Mac: `brew install --cask docker`
   - Linux: Follow docker.com instructions

2. **Docker Compose** (included with Docker Desktop)

### Quick Start

```bash
# Clone repository
git clone <your-repo-url>
cd Auralis

# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### Access Services

- Frontend: http://localhost:19000
- Backend API: http://localhost:8002
- WebSocket: ws://localhost:8003

### Docker Commands

```bash
# Rebuild containers
docker-compose build

# Restart specific service
docker-compose restart backend-api

# View service logs
docker-compose logs backend-ws

# Execute command in container
docker-compose exec backend-api python --version

# Remove all containers and volumes
docker-compose down -v
```

---

## Post-Installation

### Verify Installation

```bash
# Check Python
python --version

# Check Node
node --version

# Check FFmpeg
ffmpeg -version

# Check pip packages
pip list | grep faster-whisper
```

### First Run

1. **Backend**: First run downloads Whisper model (~1.5GB)
   - Wait for "✅ Faster-Whisper model loaded successfully"
   - Takes 5-10 minutes depending on internet speed

2. **Frontend**: Update IP address in `frontend/App.tsx`
   ```typescript
   const urls = ['http://YOUR_IP:8002', ...];
   const wsUrls = ['ws://YOUR_IP:8003', ...];
   ```

3. **Mobile App**: Install Expo Go
   - iOS: App Store
   - Android: Play Store

---

## Troubleshooting

### Python Version Issues

```bash
# Check Python version
python --version

# If wrong version, use specific version
python3.11 --version

# Create venv with specific version
python3.11 -m venv venv
```

### FFmpeg Not Found

```bash
# Windows
winget install Gyan.FFmpeg.Essentials
# Then restart terminal

# Mac
brew install ffmpeg

# Linux
sudo apt install ffmpeg
```

### Port Already in Use

```bash
# Windows - Find process using port
netstat -ano | findstr :8002
taskkill /PID <PID> /F

# Mac/Linux
lsof -i :8002
kill -9 <PID>
```

### Model Download Fails

```bash
# Check internet connection
ping huggingface.co

# Check disk space
# Windows: dir
# Mac/Linux: df -h

# Manual download location
# Windows: C:\Users\<user>\.cache\huggingface\
# Mac/Linux: ~/.cache/huggingface/
```

### Frontend Can't Connect

1. Check both backend servers are running
2. Verify IP address in App.tsx
3. Check firewall settings
4. Ensure phone and computer on same network
5. Try http://localhost:8002 if testing on same machine

### Expo Issues

```bash
# Clear cache
npx expo start -c

# Reinstall dependencies
rm -rf node_modules package-lock.json
npm install

# Update Expo
npm install expo@latest
```

---

## Development Setup

### VS Code Extensions (Recommended)

- Python
- Pylance
- React Native Tools
- ESLint
- Prettier

### Environment Variables

Create `.env` file in backend/:

```env
API_PORT=8002
WS_PORT=8003
DEBUG=True
LOG_LEVEL=INFO
```

### Hot Reload

```bash
# Backend with auto-reload
uvicorn main:app --reload --port 8002

# Frontend with hot reload (default)
npx expo start
```

---

## Production Deployment

### Backend

```bash
# Use production WSGI server
pip install gunicorn
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8002
```

### Frontend

```bash
# Build APK (Android)
eas build --platform android

# Build IPA (iOS)
eas build --platform ios
```

---

## Support

For additional help:
- Check README.md
- Review error logs
- Open GitHub issue
- Check Expo documentation: docs.expo.dev
- Check FastAPI documentation: fastapi.tiangolo.com

---

**Installation complete! Start building amazing voice transcription apps! 🎉**
