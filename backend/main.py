from fastapi import FastAPI, File, UploadFile, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
import os
import uuid
from datetime import datetime
from typing import List
import shutil
from models import AudioRecord, get_db, create_tables
from config import settings

app = FastAPI(
    title=settings.API_TITLE,
    version=settings.API_VERSION,
    description=settings.API_DESCRIPTION
)

# Create database tables on startup
create_tables()

# CORS middleware for React Native
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Audio Recording API is running"}

@app.post("/upload-audio")
async def upload_audio(file: UploadFile = File(...), db: Session = Depends(get_db)):
    """Upload and store audio file"""
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
    """Get list of all recordings"""
    recordings = db.query(AudioRecord).order_by(AudioRecord.upload_time.desc()).all()
    return {"recordings": [record.to_dict() for record in recordings]}

@app.delete("/recordings/{file_id}")
async def delete_recording(file_id: str, db: Session = Depends(get_db)):
    """Delete a recording"""
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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)