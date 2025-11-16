# Quick Start Guide - AURALIS

Get up and running in 5 minutes!

## 🚀 Fastest Way (Docker)

```bash
# 1. Clone and enter directory
git clone <your-repo-url>
cd Auralis

# 2. Start everything
docker-compose up -d

# 3. Open Expo
# Visit: http://localhost:19000
# Scan QR code with Expo Go app
```

Done! 🎉

---

## 💻 Manual Setup (Windows)

### Step 1: Install Prerequisites (5 min)

```powershell
# Install Python, Node, FFmpeg, Git
winget install Python.Python.3.11
winget install OpenJS.NodeJS
winget install Gyan.FFmpeg.Essentials
winget install Git.Git
```

**Restart your terminal after installation!**

### Step 2: Backend (10 min)

```powershell
# Clone and setup
git clone <your-repo-url>
cd Auralis\backend

# Install Python packages
pip install -r requirements.txt
.\install_whisper.bat

# Start servers (2 terminals)
# Terminal 1:
python main.py

# Terminal 2:
.\start_transcription.bat
```

Wait for: "✅ Faster-Whisper model loaded successfully"

### Step 3: Frontend (2 min)

```powershell
# New terminal
cd Auralis\frontend

# Install and start
npm install

# IMPORTANT: Update IP in App.tsx
# 1. Run: ipconfig
# 2. Find your IPv4 address (e.g., 192.168.1.100)
# 3. Edit frontend/App.tsx, replace IP addresses

npx expo start
```

### Step 4: Mobile App (1 min)

1. Install **Expo Go** on your phone (App Store/Play Store)
2. Scan QR code from terminal
3. Start recording!

---

## 🍎 Manual Setup (macOS)

```bash
# 1. Install prerequisites
brew install python@3.11 node ffmpeg git

# 2. Backend
cd Auralis/backend
pip3 install -r requirements.txt
pip3 install faster-whisper

# Start (2 terminals)
python3 main.py                    # Terminal 1
python3 transcription_server.py    # Terminal 2

# 3. Frontend
cd ../frontend
npm install
# Update IP in App.tsx (find with: ifconfig)
npx expo start

# 4. Scan QR with Expo Go app
```

---

## 🐧 Manual Setup (Linux)

```bash
# 1. Install prerequisites
sudo apt update
sudo apt install python3.11 python3-pip nodejs npm ffmpeg git -y

# 2. Backend
cd Auralis/backend
pip3 install -r requirements.txt
pip3 install faster-whisper

# Start (2 terminals)
python3 main.py                    # Terminal 1
python3 transcription_server.py    # Terminal 2

# 3. Frontend
cd ../frontend
npm install
# Update IP in App.tsx (find with: ip addr)
npx expo start

# 4. Scan QR with Expo Go app
```

---

## ✅ Verify Installation

### Check Backend

```bash
# Should return: {"message":"Audio Recording API is running"}
curl http://localhost:8002

# Should show: 🚀 Faster-Whisper transcription server running
# Check terminal running transcription_server.py
```

### Check Frontend

```bash
# Should show QR code and Metro bundler
# Visit: http://localhost:19000
```

---

## 🎯 First Recording

1. **Open app** on your phone (via Expo Go)
2. **Select language**: Hindi (हिंदी) or English
3. **Tap microphone** button
4. **Speak** clearly
5. **Tap Stop** button
6. **View transcription** in the box below

---

## 🔧 Common Issues

### "Module not found: faster_whisper"
```bash
pip install faster-whisper
```

### "FFmpeg not found"
```bash
# Windows
winget install Gyan.FFmpeg.Essentials

# Mac
brew install ffmpeg

# Linux
sudo apt install ffmpeg
```

### "Can't connect to backend"
1. Check both servers are running (ports 8002 & 8003)
2. Update IP address in `frontend/App.tsx`
3. Ensure phone and computer on same WiFi network

### "Port already in use"
```bash
# Windows
netstat -ano | findstr :8002
taskkill /PID <number> /F

# Mac/Linux
lsof -i :8002
kill -9 <PID>
```

---

## 📱 Mobile App Setup

### iOS
1. Install **Expo Go** from App Store
2. Open Expo Go
3. Scan QR code from terminal
4. Grant microphone permission

### Android
1. Install **Expo Go** from Play Store
2. Open Expo Go
3. Scan QR code from terminal
4. Grant microphone permission

---

## 🎨 Features to Try

- ✅ Switch between Hindi and English
- ✅ Translate transcriptions
- ✅ View transcription history
- ✅ Clear and restart
- ✅ Watch the animated waveform

---

## 📚 Next Steps

- Read full [README.md](README.md) for detailed documentation
- Check [INSTALL.md](INSTALL.md) for platform-specific guides
- Review API documentation in README
- Explore Docker deployment options

---

## 🆘 Need Help?

1. Check error messages in terminal
2. Review [Troubleshooting](#common-issues) section
3. Read [INSTALL.md](INSTALL.md) for detailed steps
4. Open GitHub issue with error logs

---

**Happy transcribing! 🎤✨**
