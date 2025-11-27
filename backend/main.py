"""
AURALIS Backend API - Main Application
Medical Voice Transcription with Authentication & Patient Management
"""
from fastapi import FastAPI, File, UploadFile, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel
import os
import uuid
from datetime import datetime
from typing import List
import shutil
from models import AudioRecord, get_db, create_tables
from config import settings
from deep_translator import GoogleTranslator

# Import routers
from routers import auth_router, patient_router, session_router, notes_router

# Import summarization service (try new Phi-3 service first, fallback to Gemini)
try:
    from summarization_service_phi3 import summarization_service
    print("✅ Using Phi-3-Mini local model for summarization")
except Exception as e:
    print(f"⚠️  Phi-3 service not available, falling back to Gemini: {e}")
    from summarization_service import summarization_service

# Auto-configure network on startup
from auto_config import configure_network
LOCAL_IP = configure_network()

app = FastAPI(
    title="AURALIS API",
    version="2.0.0",
    description="Medical Voice Transcription with Authentication & Patient Management"
)

# Create database tables on startup
@app.on_event("startup")
async def startup_event():
    create_tables()
    print("✅ Database tables created")
    print("🚀 AURALIS API Server started")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_router.router)
app.include_router(patient_router.router)
app.include_router(session_router.router)
app.include_router(notes_router.router)

@app.get("/")
async def root():
    return {
        "message": "AURALIS API is running",
        "version": "2.0.0",
        "features": [
            "Authentication",
            "Patient Management",
            "Session Management",
            "Audio Transcription",
            "Translation"
        ]
    }

@app.get("/health")
async def health_check():
    """Enhanced health check with model information"""
    health_data = {
        "status": "healthy",
        "version": "2.0.0",
        "database": "connected"
    }
    
    # Add model information if using Phi-3
    try:
        if hasattr(summarization_service, 'get_statistics'):
            stats = summarization_service.get_statistics()
            health_data.update({
                "model_loaded": stats['model_info']['loaded'],
                "model_name": stats['model_info'].get('model_path', 'unknown'),
                "model_size_mb": stats['model_info'].get('model_size_mb', 0),
                "total_inferences": stats['total_inferences'],
                "success_rate": stats['success_rate'],
                "avg_inference_time": stats['avg_inference_time']
            })
    except:
        pass
    
    return health_data

# Legacy audio upload endpoint (for backward compatibility)
@app.post("/upload-audio")
async def upload_audio(file: UploadFile = File(...), db: Session = Depends(get_db)):
    """Upload and store audio file (legacy endpoint)"""
    try:
        # Validate file type
        if file.content_type not in settings.ALLOWED_AUDIO_TYPES:
            raise HTTPException(status_code=400, detail="File must be a supported audio format")
        
        # Check file size
        if file.size and file.size > settings.MAX_FILE_SIZE:
            raise HTTPException(status_code=400, detail="File too large")
        
        # Generate unique filename
        file_id = str(uuid.uuid4())
        file_extension = os.path.splitext(file.filename)[1]
        filename = f"{file_id}{file_extension}"
        file_path = os.path.join(settings.UPLOAD_DIR, filename)
        
        # Save file
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Store record in database
        record = AudioRecord(
            id=file_id,
            filename=filename,
            original_name=file.filename,
            file_path=file_path,
            size=os.path.getsize(file_path)
        )
        db.add(record)
        db.commit()
        db.refresh(record)
        
        return JSONResponse(content={
            "success": True,
            "file_id": file_id,
            "message": "Audio uploaded successfully"
        })
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/recordings")
async def get_recordings(db: Session = Depends(get_db)):
    """Get list of all recordings (legacy endpoint)"""
    recordings = db.query(AudioRecord).order_by(AudioRecord.upload_time.desc()).all()
    return {"recordings": [record.to_dict() for record in recordings]}

@app.delete("/recordings/{file_id}")
async def delete_recording(file_id: str, db: Session = Depends(get_db)):
    """Delete a recording (legacy endpoint)"""
    try:
        record = db.query(AudioRecord).filter(AudioRecord.id == file_id).first()
        if not record:
            raise HTTPException(status_code=404, detail="Recording not found")
        
        # Delete file
        if os.path.exists(record.file_path):
            os.remove(record.file_path)
        
        # Remove from database
        db.delete(record)
        db.commit()
        
        return {"success": True, "message": "Recording deleted successfully"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

class TranslateRequest(BaseModel):
    text: str
    target_language: str
    source_language: str = 'auto'

@app.post("/translate")
async def translate_text(request: TranslateRequest):
    """Translate text to target language"""
    try:
        # Use deep-translator for translation
        translator = GoogleTranslator(
            source=request.source_language,
            target=request.target_language
        )
        
        translated = translator.translate(request.text)
        
        return {
            "success": True,
            "original_text": request.text,
            "translated_text": translated,
            "source_language": request.source_language,
            "target_language": request.target_language
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

class SummarizeRequest(BaseModel):
    patient_id: int

@app.post("/summarize-sessions")
async def summarize_patient_sessions(request: SummarizeRequest, db: Session = Depends(get_db)):
    """Summarize all sessions for a patient"""
    try:
        # Import here to avoid circular dependency
        from models import Session
        
        # Get all sessions for the patient
        sessions = db.query(Session).filter(
            Session.patient_id == request.patient_id
        ).order_by(Session.session_date).all()
        
        if not sessions:
            return {
                "success": False,
                "message": "No sessions found for this patient"
            }
        
        # Convert to dict format
        session_dicts = [
            {
                "original_transcription": s.original_transcription,
                "notes": s.notes,
                "session_date": str(s.session_date)
            }
            for s in sessions
        ]
        
        # Generate summary
        summary_result = summarization_service.summarize_sessions(session_dicts)
        
        return {
            "success": True,
            "summary": summary_result["summary"],
            "session_count": summary_result["session_count"],
            "key_points": summary_result["key_points"]
        }
        
    except Exception as e:
        print(f"❌ Summarization error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)
