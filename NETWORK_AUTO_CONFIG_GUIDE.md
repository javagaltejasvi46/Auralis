# 🌐 Network Auto-Configuration Guide

## Overview
Auralis now automatically detects and configures your network settings! No more manual IP updates when you switch WiFi networks.

## ✨ Features

### Automatic IP Detection
- Detects your local IP address on every server startup
- Compares with previous IP to detect network changes
- Updates all configuration files automatically

### Smart Caching
- Remembers your last IP address
- Skips configuration if IP hasn't changed (faster startup)
- Shows clear messages about what's happening

### What Gets Updated
1. **Frontend Config** (`frontend/src/config.ts`)
   - API_BASE_URL → `http://YOUR_IP:8002`
   - WS_BASE_URL → `ws://YOUR_IP:8003`

2. **Backend Config** (`backend/config.py`)
   - LOCAL_IP → `YOUR_IP`

## 🚀 Usage

### Option 1: Startup Scripts (Easiest)

**Windows Command Prompt:**
```cmd
start_backend.bat
```

**Windows PowerShell:**
```powershell
.\start_backend.ps1
```

These scripts will:
1. ✅ Run auto-configuration
2. ✅ Start main API server (port 8002)
3. ✅ Start transcription server (port 8003)

### Option 2: Manual Configuration
```bash
cd backend
python auto_config.py
```

### Option 3: Automatic (Built-in)
Just start the servers normally - auto-config runs automatically:
```bash
cd backend
python main.py
python transcription_server.py
```

## 📊 Example Output

### First Time Setup
```
============================================================
🔧 AURALIS AUTO-CONFIGURATION
============================================================
📡 Detected IP Address: 192.168.1.100
🆕 First time configuration

📝 Updating configuration files...
✅ Frontend config updated
✅ Backend config updated

============================================================
✅ Configuration updated successfully!
🌐 API Base URL: http://192.168.1.100:8002
🎤 WebSocket URL: ws://192.168.1.100:8003
============================================================
```

### Network Changed
```
============================================================
🔧 AURALIS AUTO-CONFIGURATION
============================================================
📡 Detected IP Address: 10.246.80.160
🔄 IP changed: 192.168.1.100 → 10.246.80.160

📝 Updating configuration files...
✅ Frontend config updated
✅ Backend config updated

============================================================
✅ Configuration updated successfully!
🌐 API Base URL: http://10.246.80.160:8002
🎤 WebSocket URL: ws://10.246.80.160:8003
============================================================
```

### Same Network (Fast Startup)
```
============================================================
🔧 AURALIS AUTO-CONFIGURATION
============================================================
📡 Detected IP Address: 10.246.80.160
✅ IP unchanged (10.246.80.160) - No configuration update needed
============================================================
```

## 🔧 How It Works

1. **IP Detection**: Connects to Google DNS (8.8.8.8) to determine which network interface is active
2. **Cache Check**: Compares with cached IP in `backend/.ip_cache`
3. **Update Configs**: If IP changed, updates both frontend and backend configs
4. **Save Cache**: Stores new IP for next comparison

## 💡 Benefits

✅ **Switch Networks Seamlessly**: Home → Office → Café - just restart the servers
✅ **No Manual Edits**: Eliminates configuration mistakes
✅ **Team Friendly**: Each developer's network auto-configures
✅ **Fast Startup**: Skips update if network hasn't changed
✅ **Clear Feedback**: Shows exactly what's happening

## 🐛 Troubleshooting

### Wrong IP Detected
If the auto-detected IP is incorrect, manually edit:
- `frontend/src/config.ts`
- `backend/config.py`

### Configuration Not Updating
1. Check file permissions
2. Ensure you're in the project root directory
3. Try running `python backend/auto_config.py` manually
4. Delete `backend/.ip_cache` and try again

### Multiple Network Interfaces
The system automatically selects the interface used for internet access by connecting to Google DNS (8.8.8.8).

## 📝 Files Involved

- `backend/auto_config.py` - Main auto-configuration script
- `backend/.ip_cache` - Cached IP address (auto-managed)
- `start_backend.bat` - Windows batch startup script
- `start_backend.ps1` - PowerShell startup script
- `backend/AUTO_CONFIG_README.md` - Detailed technical documentation

## 🎯 Use Cases

### Scenario 1: Daily Development
```bash
# Morning at home
.\start_backend.ps1
# Auto-configures to home WiFi IP

# Afternoon at office
.\start_backend.ps1
# Detects network change, auto-reconfigures
```

### Scenario 2: Team Collaboration
```bash
# Developer A (IP: 192.168.1.50)
python main.py
# Auto-configures to 192.168.1.50

# Developer B (IP: 192.168.1.75)
python main.py
# Auto-configures to 192.168.1.75
```

### Scenario 3: Mobile Testing
```bash
# Start backend
.\start_backend.ps1
# Shows: API Base URL: http://10.246.80.160:8002

# On mobile device, connect to same WiFi
# App automatically uses http://10.246.80.160:8002
```

## ✨ Summary

The auto-configuration system makes Auralis network-aware and eliminates manual IP configuration. Just start your servers and everything works!

**Before:** Manual IP updates in 2+ files every network change
**After:** Automatic detection and configuration on every startup

Happy coding! 🚀
