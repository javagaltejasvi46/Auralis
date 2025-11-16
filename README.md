# AURALIS - Medical Voice Transcription

**Hear . Understand . Heal**

A real-time voice transcription application with multilingual support (Hindi & English), built with React Native and Faster-Whisper AI.

![Version](https://img.shields.io/badge/version-1.0.0-blue)
![Python](https://img.shields.io/badge/python-3.10--3.13-green)
![React Native](https://img.shields.io/badge/react--native-expo-blue)

## Features

✨ **Real-time Transcription** - Live voice-to-text conversion
🌍 **Multilingual** - Hindi (Devanagari) & English support
🔄 **Translation** - Translate between Hindi and English
📱 **Mobile-First** - Built with React Native/Expo
🎯 **High Accuracy** - Powered by Faster-Whisper Medium model
🔒 **Offline Capable** - Works without internet after setup
🎨 **Modern UI** - Beautiful gradient design with smooth animations

## Tech Stack

### Frontend
- React Native (Expo)
- TypeScript
- Expo Audio for recording
- WebSocket for real-time communication

### Backend
- Python 3.10+
- FastAPI (REST API)
- Faster-Whisper (AI transcription)
- WebSockets (real-time streaming)
- Deep-Translator (translation)
- SQLite (database)

## Quick Start

### Option 1: Docker (Recommended)

```bash
# Clone the repository
git clone <your-repo-url>
cd Auralis

# Start with Docker Compose
docker-compose up -d

# Frontend will be available at: http://localhost:19000
# Backend API: http://localhost:8002
# WebSocket: ws://localhost:8003
```

### Option 2: Manual Installation

#### Prerequisites
- Python 3.10-3.13
- Node.js 16+
- FFmpeg
- Git

#### Backend Setup

```bash
# Navigate to backend
cd backend

# Install dependencies
pip install -r requirements.txt

# Install Faster-Whisper
.\install_whisper.bat  # Windows
# or
./install_whisper.sh   # Linux/Mac

# Start HTTP API server (Terminal 1)
python main.py

# Start WebSocket transcription server (Terminal 2)
.\start_transcription.bat  # Windows
# or
python transcription_server.py  # Linux/Mac
```

#### Frontend Setup

```bash
# Navigate to frontend
cd frontend

# Install dependencies
npm install

# Start Expo development server
npx expo start

# Scan QR code with Expo Go app (iOS/Android)
# or press 'a' for Android emulator, 'i' for iOS simulator
```

## Configuration

### Backend Ports
- **8002** - HTTP REST API (file uploads, translation)
- **8003** - WebSocket (real-time transcription)

### Update IP Address
Edit `frontend/App.tsx` and update the IP address to your machine's local IP:

```typescript
const urls = ['http://YOUR_IP:8002', ...];
const wsUrls = ['ws://YOUR_IP:8003', ...];
```

Find your IP:
- Windows: `ipconfig`
- Linux/Mac: `ifconfig` or `ip addr`

## Usage

1. **Select Language** - Choose Hindi (हिंदी) or English
2. **Start Recording** - Tap the microphone button
3. **Speak** - The waveform shows your voice activity
4. **Stop Recording** - Tap the Stop button
5. **View Transcription** - Text appears in the transcription box
6. **Translate** (Optional) - Tap Translate to convert between languages

## Project Structure

```
Auralis/
├── frontend/              # React Native app
│   ├── App.tsx           # Main application
│   ├── package.json      # Dependencies
│   └── app.json          # Expo configuration
├── backend/              # Python backend
│   ├── main.py          # FastAPI HTTP server
│   ├── transcription_server.py  # WebSocket server
│   ├── audio_processor.py       # Audio processing
│   ├── models.py        # Database models
│   ├── config.py        # Configuration
│   └── requirements.txt # Python dependencies
├── docker-compose.yml   # Docker orchestration
├── Dockerfile.backend   # Backend container
├── Dockerfile.frontend  # Frontend container
└── README.md           # This file
```

## API Documentation

### REST API (Port 8002)

#### Upload Audio
```http
POST /upload-audio
Content-Type: multipart/form-data

Response: { "success": true, "file_id": "uuid" }
```

#### Translate Text
```http
POST /translate
Content-Type: application/json

Body: {
  "text": "Hello",
  "target_language": "hi",
  "source_language": "en"
}

Response: {
  "success": true,
  "translated_text": "नमस्ते"
}
```

#### Get Recordings
```http
GET /recordings

Response: {
  "recordings": [...]
}
```

### WebSocket API (Port 8003)

#### Connect
```javascript
ws = new WebSocket('ws://localhost:8003');
```

#### Set Language
```json
{
  "type": "set_language",
  "language": "hindi"  // or "english"
}
```

#### Send Audio File
```json
{
  "type": "audio_file",
  "data": "base64_encoded_audio",
  "format": "m4a"
}
```

#### Receive Transcription
```json
{
  "type": "final",
  "text": "transcribed text",
  "language": "hindi"
}
```

## Models

### Faster-Whisper Medium
- **Size**: ~1.5GB
- **Languages**: 99+ languages
- **Accuracy**: High
- **Speed**: ~5-10 seconds per minute of audio
- **Native Scripts**: Outputs Devanagari for Hindi

Downloaded automatically on first run to:
- Windows: `C:\Users\<user>\.cache\huggingface\`
- Linux/Mac: `~/.cache/huggingface/`

## Troubleshooting

### Backend won't start
```bash
# Check Python version
python --version  # Should be 3.10-3.13

# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

### Frontend can't connect
1. Check backend is running on both ports (8002 & 8003)
2. Update IP address in `frontend/App.tsx`
3. Ensure firewall allows connections
4. Try `http://localhost:8002` if testing on same machine

### FFmpeg not found
```bash
# Windows
winget install Gyan.FFmpeg.Essentials

# Mac
brew install ffmpeg

# Linux
sudo apt install ffmpeg
```

### Model download fails
- Check internet connection
- Ensure ~2GB free disk space
- Model downloads to cache automatically

### Hindi shows romanized text
- Ensure using **medium** model (not base/small)
- Check language is set to 'hindi' before recording
- Medium model natively outputs Devanagari

## Development

### Run in Development Mode

```bash
# Backend with auto-reload
cd backend
uvicorn main:app --reload --port 8002

# Frontend with hot reload
cd frontend
npx expo start
```

### Build for Production

```bash
# Android APK
cd frontend
eas build --platform android

# iOS IPA
eas build --platform ios
```

## Docker Details

### Services
- **backend-api**: FastAPI HTTP server
- **backend-ws**: WebSocket transcription server
- **frontend**: Expo development server

### Volumes
- `whisper-models`: Cached AI models
- `uploads`: Audio file storage
- `database`: SQLite database

### Environment Variables
```env
PYTHON_ENV=production
API_PORT=8002
WS_PORT=8003
```

## Performance

### System Requirements
- **CPU**: 4+ cores recommended
- **RAM**: 4GB minimum, 8GB recommended
- **Storage**: 5GB (includes models)
- **Network**: Required for initial model download

### Benchmarks
- Transcription: ~5-10 seconds per minute of audio
- Real-time factor: 0.1-0.2x (10-20% of audio duration)
- Concurrent users: 10+ (depends on CPU)

## Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## License

This project is licensed under the MIT License - see LICENSE file for details.

## Acknowledgments

- [Faster-Whisper](https://github.com/guillaumekln/faster-whisper) - AI transcription
- [OpenAI Whisper](https://github.com/openai/whisper) - Base model
- [Expo](https://expo.dev/) - React Native framework
- [FastAPI](https://fastapi.tiangolo.com/) - Backend framework

## Support

For issues and questions:
- Open an issue on GitHub
- Check existing documentation
- Review troubleshooting section

---

**Made with ❤️ for better healthcare communication**
