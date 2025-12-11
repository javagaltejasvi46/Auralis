# 🚀 Auralis Quick Start Guide
**Get connected in under 2 minutes!**

## Step 1: Start the Backend (30 seconds)

### Windows
```bash
# Double-click this file:
start_auralis.bat
```

### Mac/Linux
```bash
chmod +x start_auralis.sh
./start_auralis.sh
```

### Manual (any OS)
```bash
cd backend
pip install -r requirements.txt
python startup.py
```

## Step 2: Get Your Connection Info (10 seconds)

After starting the backend, you'll see:

```
📱 MOBILE APP CONNECTION INFO
========================================
🌐 Server IP: 192.168.1.100
🔗 API URL: http://192.168.1.100:8002
🎤 WebSocket: ws://192.168.1.100:8003

📋 Manual Setup:
   1. Open Auralis mobile app
   2. Tap connection status
   3. Enter IP: 192.168.1.100
   4. Tap 'Connect'
========================================
```

**OR** open your browser and go to: `http://YOUR_IP:8002/connection`

## Step 3: Start Mobile App (30 seconds)

```bash
cd frontend
npm install
npx expo start
```

Scan QR code with Expo Go app.

## Step 4: Connect Mobile to Backend (30 seconds)

### Method 1: Automatic (Recommended)
1. Open the Auralis app
2. Wait 5 seconds for auto-discovery
3. ✅ Connected!

### Method 2: Manual (If auto fails)
1. Tap the connection status in the app
2. Tap "Connect Manually"
3. Enter the IP from Step 2 (e.g., `192.168.1.100`)
4. Tap "Connect"
5. ✅ Connected!

### Method 3: QR Code (Coming Soon)
1. Open `http://YOUR_IP:8002/connection` in browser
2. Scan QR code with app
3. ✅ Connected!

## ✅ You're Ready!

- **Green dot** = Connected ✅
- **Red dot** = Not connected ❌
- **Yellow dot** = Connecting ⏳

## 🔧 Troubleshooting

### "Can't find server"
1. Make sure phone and computer are on **same WiFi**
2. Try manual connection with the IP shown in terminal
3. Check Windows Firewall (temporarily disable to test)

### "Connection failed"
1. Restart the backend: `python startup.py`
2. Check the IP hasn't changed
3. Try a different IP from the same network range

### "Still not working"
1. Get your computer's IP:
   - Windows: `ipconfig`
   - Mac/Linux: `ifconfig`
2. Use manual connection with that IP
3. Make sure ports 8002 and 8003 are not blocked

## 🎯 Common IP Ranges
- Home WiFi: `192.168.1.x` or `192.168.0.x`
- Office: `10.x.x.x` or `172.16.x.x`
- Mobile Hotspot: `192.168.43.x`

---

**Need help?** The app will automatically try to find your server. If it doesn't work in 5 seconds, use manual connection!