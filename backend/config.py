import os
from typing import Optional

class Settings:
    # Network Configuration
    LOCAL_IP: str = "10.157.95.160"
    # API Configuration
    API_TITLE: str = "Audio Recording API"
    API_VERSION: str = "1.0.0"
    API_DESCRIPTION: str = "FastAPI backend for audio recording application"
    
    # File Upload Configuration
    UPLOAD_DIR: str = "uploads"
    MAX_FILE_SIZE: int = 50 * 1024 * 1024  # 50MB
    ALLOWED_AUDIO_TYPES: list = [
        "audio/mpeg",
        "audio/wav", 
        "audio/mp4",
        "audio/m4a",
        "audio/aac",
        "audio/ogg"
    ]
    
    # Database Configuration
    DATABASE_URL: str = "sqlite:///./audio_records.db"
    
    # CORS Configuration
    CORS_ORIGINS: list = ["*"]  # In production, specify exact origins
    
    # Future ML Model Configuration
    MODEL_DIR: str = "models"
    ENABLE_TRANSCRIPTION: bool = False
    ENABLE_AUDIO_ANALYSIS: bool = False

settings = Settings()

# Create necessary directories
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
os.makedirs(settings.MODEL_DIR, exist_ok=True)