# 🎤 Auralis - AI-Ready Audio Recording App
version : 1.0
A modern, futuristic audio recording application built with React Native (Expo) and FastAPI. Features a clean, minimal dark UI with gradient effects and is designed to be easily extensible with AI/ML models for audio processing.

![Auralis App](https://img.shields.io/badge/Platform-iOS%20%7C%20Android-blue)
![Expo SDK](https://img.shields.io/badge/Expo%20SDK-49-green)
![React Native](https://img.shields.io/badge/React%20Native-0.72.6-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-Latest-green)

## ✨ Features

- 🎨 **Futuristic Dark UI** - Clean, minimal design with gradient backgrounds
- 🎙️ **High-Quality Audio Recording** - Using Expo AV with configurable quality settings
- ▶️ **Audio Playback** - Built-in playback functionality with visual feedback
- 📱 **Haptic Feedback** - Enhanced user experience with tactile responses
- 🌐 **FastAPI Backend** - RESTful API for audio storage and processing
- 💾 **SQLite Database** - Metadata storage for recordings
- 🔄 **Real-time Upload** - Automatic upload to backend after recording
- 🚀 **AI/ML Ready** - Architecture designed for easy integration of audio processing models

## 🏗️ Architecture

```
auralis/
├── backend/              # FastAPI Python backend
│   ├── main.py          # API endpoints and server
│   ├── models.py        # Database models (SQLAlchemy)
│   ├── config.py        # Configuration settings
│   └── requirements.txt # Python dependencies
├── frontend/            # React Native Expo app
│   ├── App.tsx         # Main application component
│   ├── package.json    # Node.js dependencies
│   └── app.json        # Expo configuration
└── README.md           # This file
```

## 🚀 Quick Start

### Prerequisites

- **Node.js** (v16 or higher)
- **Python** (v3.8 or higher)
- **Expo Go** app on your mobile device
- **Git** for cloning the repository

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/auralis.git
cd auralis
```

### 2. Backend Setup

```bash
# Navigate to backend directory
cd backend

# Install Python dependencies
pip install -r requirements.txt

# Start the FastAPI server
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The backend will be available at: `http://localhost:8000`
API documentation: `http://localhost:8000/docs`

### 3. Frontend Setup

```bash
# Navigate to frontend directory (in a new terminal)
cd frontend

# Install Node.js dependencies
npm install

# Start the Expo development server
npx expo start
```

### 4. Mobile App Testing

1. **Install Expo Go** on your mobile device:
   - [iOS App Store](https://apps.apple.com/app/expo-go/id982107779)
   - [Google Play Store](https://play.google.com/store/apps/details?id=host.exp.exponent)

2. **Connect to the app**:
   - Scan the QR code displayed in your terminal with Expo Go
   - Make sure your phone and computer are on the same WiFi network

3. **Update IP Address** (for physical device testing):
   - Find your computer's IP address: `ipconfig` (Windows) or `ifconfig` (Mac/Linux)
   - Update `frontend/App.tsx` line ~102: Change `192.168.0.140` to your IP address

## 📱 Usage

### Recording Audio
1. **Tap the red record button** to start recording
2. **Tap again to stop** recording
3. **Recordings appear** in the list below with timestamp and duration
4. **Tap play button** to listen to any recording

### Backend Integration
- Recordings are **automatically uploaded** to the FastAPI backend
- **Metadata is stored** in SQLite database
- **Files are saved** in the `backend/uploads/` directory

## 🛠️ Development

### Backend Development

```bash
# Run with auto-reload for development
cd backend
python -m uvicorn main:app --reload

# View API documentation
# Open http://localhost:8000/docs in your browser
```

### Frontend Development

```bash
# Start with cache clearing
cd frontend
npx expo start --clear

# Run on specific platform
npx expo start --android  # Android only
npx expo start --ios      # iOS only
```

### Database Management

The SQLite database is automatically created at `backend/audio_records.db`. To reset:

```bash
cd backend
rm audio_records.db
python -c "from models import create_tables; create_tables()"
```

## 🔧 Configuration

### Backend Configuration (`backend/config.py`)

```python
# File Upload Settings
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB
ALLOWED_AUDIO_TYPES = ["audio/mpeg", "audio/wav", "audio/mp4", "audio/m4a"]

# Database Settings
DATABASE_URL = "sqlite:///./audio_records.db"

# Future ML Model Settings
ENABLE_TRANSCRIPTION = False
ENABLE_AUDIO_ANALYSIS = False
```

### Frontend Configuration (`frontend/app.json`)

```json
{
  "expo": {
    "name": "Auralis",
    "orientation": "portrait",
    "userInterfaceStyle": "dark"
  }
}
```

## 🤖 AI/ML Integration Ready

Auralis is designed for easy integration with AI/ML models:

### Planned Features
- **Speech-to-Text** transcription
- **Audio classification** and analysis
- **Voice enhancement** processing
- **Real-time audio processing**

### Integration Points
- `backend/main.py` - Add new API endpoints for ML processing
- `backend/config.py` - Enable ML features
- `frontend/App.tsx` - Add UI for ML features

## 📦 Dependencies

### Backend
- **FastAPI** - Modern web framework for APIs
- **SQLAlchemy** - Database ORM
- **Uvicorn** - ASGI server
- **Python-multipart** - File upload support

### Frontend
- **Expo SDK 49** - React Native framework
- **expo-av** - Audio recording and playback
- **expo-linear-gradient** - UI gradients
- **expo-haptics** - Tactile feedback

## 🐛 Troubleshooting

### Common Issues

**"Upload failed" error:**
- Update the IP address in `frontend/App.tsx` to your computer's IP
- Ensure backend is running on port 8000
- Check that phone and computer are on same WiFi network

**Metro bundler errors:**
- Clear cache: `npx expo start --clear`
- Reinstall dependencies: `rm -rf node_modules && npm install`

**Backend not accessible:**
- Check if port 8000 is available
- Verify firewall settings allow connections on port 8000
- Try accessing `http://localhost:8000` in your browser

### Getting Help

1. Check the [Troubleshooting Guide](TROUBLESHOOTING.md)
2. Review [Expo documentation](https://docs.expo.dev/)
3. Check [FastAPI documentation](https://fastapi.tiangolo.com/)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Commit changes: `git commit -am 'Add feature'`
4. Push to branch: `git push origin feature-name`
5. Submit a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Expo Team** - For the amazing React Native framework
- **FastAPI** - For the high-performance web framework
- **React Native Community** - For the ecosystem and support

---

**Built with ❤️ for the future of audio applications**

*Ready to integrate AI/ML models for next-generation audio processing*