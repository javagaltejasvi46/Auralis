# Auralis Backend

Medical voice transcription system with AI-powered summarization for mental health therapy sessions.

## Features

- 🎤 **Real-time Transcription** - Faster-Whisper for multilingual speech-to-text
- 🌍 **Auto-Translation** - Automatic translation to English with speaker diarization
- 🔐 **Authentication** - JWT-based secure user authentication
- 👥 **Patient Management** - Complete patient and session tracking
- 🤖 **AI Summarization** - Google Gemini for professional therapy summaries
- 🌐 **Auto-Configuration** - Automatic network IP detection and configuration

## Quick Start

### 1. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 2. Download Whisper Model

```bash
# The medium model will be downloaded automatically on first run
# Or download manually:
python -c "from faster_whisper import WhisperModel; WhisperModel('medium')"
```

### 3. Configure Gemini API

Get your API key from: https://makersuite.google.com/app/apikey

Update `summarization_service.py` line 6:
```python
self.api_key = "YOUR_GEMINI_API_KEY_HERE"
```

### 4. Start Services

**Option A: Use startup scripts (Recommended)**
```bash
# Windows
start_backend.bat

# PowerShell
.\start_backend.ps1
```

**Option B: Manual start**
```bash
# Terminal 1: Main API Server
python main.py

# Terminal 2: Transcription Server
python transcription_server.py
```

## API Endpoints

### Authentication
- `POST /auth/register` - Register new therapist
- `POST /auth/login` - Login
- `GET /auth/me` - Get current user

### Patients
- `GET /patients/` - List all patients
- `POST /patients/` - Create patient
- `GET /patients/{id}` - Get patient details
- `PUT /patients/{id}` - Update patient
- `DELETE /patients/{id}` - Delete patient

### Sessions
- `GET /sessions/patient/{patient_id}` - Get patient sessions
- `POST /sessions/` - Create session
- `GET /sessions/{id}` - Get session details
- `PUT /sessions/{id}` - Update session
- `DELETE /sessions/{id}` - Delete session

### Summarization
- `POST /summarize-sessions` - Generate AI summary
  ```json
  {
    "patient_id": 1
  }
  ```

### Translation
- `POST /translate` - Translate text
  ```json
  {
    "text": "Hello",
    "target_language": "hi"
  }
  ```

## Configuration

### Auto-Configuration
The system automatically detects your local IP and updates configurations:
- Frontend config (`frontend/src/config.ts`)
- Backend config (`backend/config.py`)
- Cached in `.ip_cache`

To manually run:
```bash
python auto_config.py
```

### Database
- SQLite database: `auralis.db`
- Automatic table creation on startup
- Models: Therapist, Patient, Session

### File Uploads
- Audio files stored in `uploads/`
- Automatic directory creation

## Architecture

```
backend/
├── main.py                      # Main API server (port 8002)
├── transcription_server.py      # WebSocket transcription (port 8003)
├── summarization_service.py     # Gemini AI integration
├── auto_config.py              # Network auto-configuration
├── auth.py                     # JWT authentication
├── models.py                   # Database models
├── config.py                   # Configuration settings
├── routers/                    # API route modules
│   ├── auth_router.py
│   ├── patient_router.py
│   └── session_router.py
└── requirements.txt            # Python dependencies
```

## Transcription Features

### Supported Languages
- English, Hindi, Tamil, Telugu, Kannada, Malayalam
- Bengali, Punjabi, Marathi, Gujarati
- 90+ languages total

### Auto-Translation
- All languages automatically translated to English
- Original transcription preserved
- Speaker diarization included

### WebSocket Protocol
```javascript
// Connect
ws://YOUR_IP:8003

// Send audio chunks
{
  "audio": "base64_encoded_audio",
  "language": "hindi"  // optional
}

// Receive transcription
{
  "text": "Transcribed text",
  "speaker": "Person 1"
}
```

## AI Summarization

### Gemini Integration
- Model: gemini-2.5-flash
- Professional therapy summaries
- Sensitive keyword highlighting
- Markdown formatting support

### Summary Format
```
**Chief Complaint:** [main issue]
**Emotional State:** [mood]
**Risk:** [safety concerns - {{RED:urgent}}]
**Intervention:** [what was done]
**Plan:** [next steps]
```

### Sensitive Keywords (Highlighted in Red)
- suicide, suicidal, kill myself
- self-harm, cut myself, hurt myself
- violence, hurt others
- abuse (sexual, physical)
- overdose, pills, weapon

## Troubleshooting

### Port Already in Use
```bash
# Find process using port
netstat -ano | findstr "8002"

# Kill process (Windows)
taskkill /PID <PID> /F
```

### Whisper Model Issues
```bash
# Clear cache and re-download
rm -rf ~/.cache/huggingface
python -c "from faster_whisper import WhisperModel; WhisperModel('medium')"
```

### Gemini API Errors
- **403 Leaked Key**: Get new API key
- **404 Model Not Found**: Check model name is "gemini-2.5-flash"
- **429 Rate Limit**: Wait or upgrade plan

### Database Issues
```bash
# Reset database
rm auralis.db
python main.py  # Will recreate tables
```

## Development

### Adding New Endpoints
1. Create router in `routers/`
2. Import in `main.py`
3. Add to app: `app.include_router(your_router)`

### Database Migrations
```python
# Add new model field
class Patient(Base):
    new_field = Column(String)

# Restart server - tables auto-update
```

### Testing
```bash
# Test API
curl http://localhost:8002/docs

# Test WebSocket
python test_websocket.py
```

## Security

### Best Practices
- ✅ JWT tokens with expiration
- ✅ Password hashing with bcrypt
- ✅ CORS configuration
- ✅ Input validation
- ✅ SQL injection protection (SQLAlchemy)

### HIPAA Compliance
- All processing is local
- No data sent to external services (except Gemini for summaries)
- Encrypted authentication
- Audit trail in database

## Performance

### Optimization Tips
1. **Transcription**: Use GPU if available
2. **Database**: Add indexes for large datasets
3. **API**: Enable caching for frequent queries
4. **WebSocket**: Limit concurrent connections

### Resource Usage
- **RAM**: ~2GB (Whisper medium model)
- **CPU**: Moderate (transcription intensive)
- **Disk**: ~1GB (model) + database
- **Network**: Minimal (local only)

## Support

### Common Issues
- **Slow transcription**: Use smaller model or GPU
- **Network errors**: Check firewall settings
- **Import errors**: Reinstall requirements

### Logs
- Server logs: Console output
- Database: `auralis.db`
- Uploads: `uploads/` directory

## License

Proprietary - Auralis Medical Transcription System

---

**Status**: Production Ready
**Version**: 2.0.0
**Last Updated**: November 2025
