# Auto-Configuration System

## Overview
Auralis now automatically detects your local IP address and updates all configuration files when the network changes. No more manual IP updates!

## How It Works

### Automatic Detection
- Detects your current local IP address on startup
- Compares with cached IP to detect network changes
- Updates both frontend and backend configurations automatically

### What Gets Updated
1. **Frontend** (`frontend/src/config.ts`):
   - `API_BASE_URL` - Main API endpoint
   - `TRANSCRIPTION_WS_URL` - WebSocket endpoint

2. **Backend** (`backend/config.py`):
   - `LOCAL_IP` - Local network IP address

## Usage

### Method 1: Use Startup Scripts (Recommended)
```bash
# Windows Command Prompt
start_backend.bat

# Windows PowerShell
.\start_backend.ps1
```

These scripts will:
1. Run auto-configuration
2. Start the main API server (port 8002)
3. Start the transcription server (port 8003)

### Method 2: Manual Configuration
```bash
cd backend
python auto_config.py
```

### Method 3: Automatic on Server Start
The configuration runs automatically when you start:
- `python main.py`
- `python transcription_server.py`

## Network Change Detection

The system automatically detects when your IP changes:
- ✅ First run: Configures everything
- ✅ Same network: Skips configuration (fast startup)
- ✅ Network changed: Updates all configs automatically

## Cache File
The system stores the current IP in `backend/.ip_cache` to detect changes. This file is automatically managed.

## Troubleshooting

### IP Not Detected Correctly
If the auto-detected IP is wrong, you can manually edit:
- `frontend/src/config.ts`
- `backend/config.py`

### Configuration Not Updating
1. Check file permissions
2. Ensure you're running from the project root
3. Try running `python backend/auto_config.py` manually

### Multiple Network Interfaces
The system connects to Google DNS (8.8.8.8) to determine which interface is used for internet access. This ensures the correct IP is selected.

## Benefits

✅ **No Manual Updates**: Network changes are handled automatically
✅ **Fast Development**: Switch between networks seamlessly
✅ **Error Prevention**: Eliminates manual configuration mistakes
✅ **Team Friendly**: Each developer's network is auto-configured

## Example Output

```
============================================================
🔧 AURALIS AUTO-CONFIGURATION
============================================================
📡 Detected IP Address: 192.168.1.100
🔄 IP changed: 10.49.49.231 → 192.168.1.100

📝 Updating configuration files...
✅ Frontend config updated: frontend/src/config.ts
✅ Backend config updated: backend/config.py

============================================================
✅ Configuration updated successfully!
🌐 API Base URL: http://192.168.1.100:8002
🎤 WebSocket URL: ws://192.168.1.100:8003
============================================================
```
