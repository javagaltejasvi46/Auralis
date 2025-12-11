# Auralis - Medical Voice Transcription System

Professional therapy session transcription and management system with AI-powered summarization.

## Overview

Auralis is a complete medical transcription solution designed for mental health professionals. It provides real-time multilingual transcription, automatic translation, patient management, and AI-powered session summarization.

## Key Features

- 🎤 **Real-Time Transcription** - Faster-Whisper for accurate speech-to-text
- 🌍 **Multilingual Support** - 90+ languages with auto-translation to English
- 👥 **Speaker Diarization** - Identifies different speakers automatically
- 🤖 **AI Summarization** - Google Gemini for professional therapy summaries
- 📱 **Mobile App** - React Native app for iOS and Android
- 🔐 **Secure** - JWT authentication and HIPAA-compliant design
- 🌐 **Auto-Configuration** - Automatic network setup
- 📝 **Clinical Notes** - Add observations and treatment plans
- 🎯 **Risk Detection** - Automatic flagging of sensitive keywords

## Quick Start

### Prerequisites

- Python 3.8+
- Node.js 16+
- FFmpeg
- Expo Go app (for mobile testing)

### 1. Easy Startup (Recommended)

**Windows:**
```bash
# Double-click or run:
start_auralis.bat
```

**Linux/Mac:**
```bash
# Make executable and run:
chmod +x start_auralis.sh
./start_auralis.sh
```

**Manual Setup:**
```bash
cd backend
pip install -r requirements.txt
python startup.py  # This handles everything automatically
```

### 2. Frontend Setup

```bash
cd frontend
npm install
npx expo start
```

Scan QR code with Expo Go app on your phone.

### 3. Automatic Network Configuration

The system now **automatically detects your IP address** and configures itself:

- ✅ **No manual IP configuration needed**
- ✅ **Works on any device/network**
- ✅ **Automatic server discovery in mobile app**
- ✅ **Fallback to manual configuration if needed**

### 4. Configure AI Models (Optional)

**For Phi-3-Mini (Recommended - Free & Local):**
```bash
# Install Ollama
curl https://ollama.ai/install.sh | sh

# Pull Phi-3-Mini model
ollama pull phi3:mini

# Start Ollama (runs automatically with startup.py)
ollama serve
```

**For Gemini (Alternative):**
1. Get API key from: https://makersuite.google.com/app/apikey
2. Update `backend/summarization_service.py` line 6:
   ```python
   self.api_key = "YOUR_API_KEY_HERE"
   ```

## Project Structure

```
Auralis/
├── backend/                 # Python FastAPI backend
│   ├── main.py             # Main API server (port 8002)
│   ├── transcription_server.py  # WebSocket server (port 8003)
│   ├── summarization_service.py # Gemini AI integration
│   ├── auto_config.py      # Network auto-configuration
│   ├── routers/            # API endpoints
│   ├── models.py           # Database models
│   ├── requirements.txt    # Python dependencies
│   └── README.md           # Backend documentation
│
├── frontend/               # React Native mobile app
│   ├── src/
│   │   ├── screens/       # App screens
│   │   ├── components/    # Reusable components
│   │   ├── services/      # API integration
│   │   └── config.ts      # Configuration
│   ├── package.json       # Node dependencies
│   └── README.md          # Frontend documentation
│
├── start_backend.bat      # Windows startup script
├── start_backend.ps1      # PowerShell startup script
└── README.md              # This file
```

## Architecture

### Backend (Python)
- **FastAPI** - REST API framework
- **Faster-Whisper** - Speech-to-text transcription
- **SQLAlchemy** - Database ORM
- **Google Gemini** - AI summarization
- **WebSockets** - Real-time communication

### Frontend (React Native)
- **Expo** - Development platform
- **React Navigation** - Screen navigation
- **Expo AV** - Audio recording
- **WebSocket** - Real-time transcription

### Database
- **SQLite** - Local database
- **Models**: Therapist, Patient, Session

## Features in Detail

### Real-Time Transcription
- Supports 90+ languages including Hindi, Tamil, Telugu, Kannada
- Automatic translation to English
- Speaker diarization (identifies different speakers)
- WebSocket-based real-time streaming

### AI Summarization
- Professional therapy session summaries
- Sensitive keyword highlighting (suicide, self-harm, violence)
- Markdown formatting with bold and red text
- Context-aware summaries

### Patient Management
- Complete patient profiles
- Session history tracking
- Clinical notes
- Search and filter capabilities

### Security
- JWT-based authentication
- Password hashing with bcrypt
- HIPAA-compliant design
- Local data processing

## API Endpoints

### Authentication
- `POST /auth/register` - Register therapist
- `POST /auth/login` - Login
- `GET /auth/me` - Get current user

### Patients
- `GET /patients/` - List patients
- `POST /patients/` - Create patient
- `GET /patients/{id}` - Get patient
- `PUT /patients/{id}` - Update patient
- `DELETE /patients/{id}` - Delete patient

### Sessions
- `GET /sessions/patient/{id}` - Get patient sessions
- `POST /sessions/` - Create session
- `PUT /sessions/{id}` - Update session
- `DELETE /sessions/{id}` - Delete session

### AI Features
- `POST /summarize-sessions` - Generate summary
- `POST /translate` - Translate text

## Configuration

### Auto-Configuration
The system automatically detects your local IP address and updates:
- Frontend config (`frontend/src/config.ts`)
- Backend config (`backend/config.py`)

When you switch networks, just restart the backend and it reconfigures automatically.

### Manual Configuration
If needed, update these files:
- `frontend/src/config.ts` - API and WebSocket URLs
- `backend/summarization_service.py` - Gemini API key

## Development

### Backend Development
```bash
cd backend
python main.py  # API server on port 8002
```

API documentation: http://localhost:8002/docs

### Frontend Development
```bash
cd frontend
npx expo start
```

### Testing
- Backend: Use FastAPI docs at `/docs`
- Frontend: Test on physical device with Expo Go
- WebSocket: Connect to `ws://YOUR_IP:8003`

## Deployment

### Backend
```bash
# Production server
uvicorn main:app --host 0.0.0.0 --port 8002
```

### Frontend
```bash
# Build APK (Android)
eas build --platform android

# Build IPA (iOS)
eas build --platform ios
```

## Troubleshooting

### Network Connection Issues

**Mobile App Can't Connect:**
1. **Automatic Discovery**: The app will automatically try to find the server
2. **Manual Connection**: Tap the connection status → "Connect Manually" → Enter server IP
3. **Check Same Network**: Ensure phone and computer are on the same WiFi
4. **Firewall**: Temporarily disable firewall to test

**Find Your Server IP:**
```bash
# Windows
ipconfig

# Linux/Mac
ifconfig
# or
ip addr show
```

**Common IP Ranges:**
- Home networks: `192.168.1.x` or `192.168.0.x`
- Corporate: `10.x.x.x` or `172.16.x.x`
- Mobile hotspot: `192.168.43.x`

### Backend Issues
- **Port in use**: Kill process or change port in startup.py
- **Whisper model**: Will download automatically (~1GB)
- **Ollama not found**: Install Ollama and run `ollama pull phi3:mini`
- **Dependencies missing**: Run `pip install -r requirements.txt`

### Frontend Issues
- **Connection Status**: Check the connection indicator in the app
- **Audio not working**: Check microphone permissions
- **Auto-discovery fails**: Use manual IP entry
- **WebSocket fails**: Ensure transcription server is running (port 8003)

### Advanced Troubleshooting

**Reset Network Configuration:**
```bash
cd backend
rm .ip_cache
python auto_config.py
```

**Check Server Status:**
```bash
# Test API server
curl http://YOUR_IP:8002/health

# Test WebSocket server
curl http://YOUR_IP:8003
```

**Environment Variables (Optional):**
```bash
# Set in frontend/.env
EXPO_PUBLIC_API_HOST=192.168.1.100

# Set in backend/.env
LOCAL_IP=192.168.1.100
```

## Performance

### System Requirements
- **RAM**: 4GB minimum, 8GB recommended
- **Storage**: 2GB for models and data
- **CPU**: Multi-core recommended for transcription
- **Network**: Local WiFi (no internet required except for Gemini)

### Optimization
- Use GPU for faster transcription (if available)
- Adjust Whisper model size (tiny/base/small/medium)
- Enable caching for frequent queries
- Limit concurrent transcription sessions

## Security & Privacy

### HIPAA Compliance
- ✅ Local data processing
- ✅ Encrypted authentication
- ✅ No external data sharing (except Gemini summaries)
- ✅ Audit trail in database
- ✅ Secure password storage

### Best Practices
- Change default API keys
- Use HTTPS in production
- Regular database backups
- Limit API access
- Monitor system logs

## Support

### Documentation
- Backend: `backend/README.md`
- Frontend: `frontend/README.md`
- API Docs: http://localhost:8002/docs

### Common Issues
1. **Transcription slow**: Use smaller Whisper model
2. **Network errors**: Check IP configuration
3. **API errors**: Verify authentication token
4. **Audio issues**: Test microphone permissions

### Getting Help
- Check README files in each directory
- Review API documentation
- Test with provided examples
- Check system logs

## Technology Stack

### Backend
- Python 3.8+
- FastAPI
- Faster-Whisper
- SQLAlchemy
- Google Gemini API
- WebSockets

### Frontend
- React Native
- Expo
- TypeScript
- React Navigation
- Expo AV

### Database
- SQLite
- SQLAlchemy ORM

## Roadmap

### Planned Features
- [ ] Cloud backup
- [ ] Multi-therapist support
- [ ] Advanced analytics
- [ ] Custom AI model training
- [ ] Video session support
- [ ] Appointment scheduling

## License

Proprietary - Auralis Medical Transcription System

## Credits

Developed for mental health professionals to streamline therapy session documentation and improve patient care.

---

**Version**: 2.0.0
**Status**: Production Ready
**Last Updated**: November 2025

For detailed documentation, see:
- Backend: `backend/README.md`
- Frontend: `frontend/README.md`
