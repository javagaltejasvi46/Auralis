"""
Session management routes
"""
from fastapi import APIRouter, Depends, HTTPException, status, File, UploadFile
from sqlalchemy.orm import Session as DBSession
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from models import Session, Patient, Therapist, get_db
from auth import get_current_therapist
import os
import uuid
import shutil

router = APIRouter(prefix="/sessions", tags=["Sessions"])

class SessionCreate(BaseModel):
    patient_id: int
    language: str = "hindi"
    duration: Optional[int] = None
    original_transcription: Optional[str] = None
    notes: Optional[str] = None

class SessionUpdate(BaseModel):
    duration: Optional[int] = None
    original_transcription: Optional[str] = None
    translated_transcription: Optional[str] = None
    translation_language: Optional[str] = None
    notes: Optional[str] = None
    diagnosis: Optional[str] = None
    treatment_plan: Optional[str] = None
    is_completed: Optional[bool] = None

@router.post("/", response_model=dict)
async def create_session(
    session_data: SessionCreate,
    current_therapist: Therapist = Depends(get_current_therapist),
    db: DBSession = Depends(get_db)
):
    """Create new therapy session"""
    
    # Verify patient belongs to therapist
    patient = db.query(Patient).filter(
        Patient.id == session_data.patient_id,
        Patient.therapist_id == current_therapist.id
    ).first()
    
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient not found"
        )
    
    # Get next session number
    last_session = db.query(Session).filter(
        Session.patient_id == session_data.patient_id
    ).order_by(Session.session_number.desc()).first()
    
    session_number = (last_session.session_number + 1) if last_session else 1
    
    # Create session
    new_session = Session(
        patient_id=session_data.patient_id,
        session_number=session_number,
        language=session_data.language,
        duration=session_data.duration,
        original_transcription=session_data.original_transcription,
        notes=session_data.notes
    )
    
    db.add(new_session)
    db.commit()
    db.refresh(new_session)
    
    return {
        "success": True,
        "message": "Session created successfully",
        "session": new_session.to_dict()
    }

@router.get("/patient/{patient_id}", response_model=dict)
async def get_patient_sessions(
    patient_id: int,
    current_therapist: Therapist = Depends(get_current_therapist),
    db: DBSession = Depends(get_db)
):
    """Get all sessions for a patient"""
    
    # Verify patient belongs to therapist
    patient = db.query(Patient).filter(
        Patient.id == patient_id,
        Patient.therapist_id == current_therapist.id
    ).first()
    
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient not found"
        )
    
    sessions = db.query(Session).filter(
        Session.patient_id == patient_id
    ).order_by(Session.session_date.desc()).all()
    
    return {
        "success": True,
        "count": len(sessions),
        "sessions": [s.to_dict() for s in sessions]
    }

@router.get("/{session_id}", response_model=dict)
async def get_session(
    session_id: int,
    current_therapist: Therapist = Depends(get_current_therapist),
    db: DBSession = Depends(get_db)
):
    """Get session details"""
    
    session = db.query(Session).join(Patient).filter(
        Session.id == session_id,
        Patient.therapist_id == current_therapist.id
    ).first()
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )
    
    return {
        "success": True,
        "session": session.to_dict()
    }

@router.put("/{session_id}", response_model=dict)
async def update_session(
    session_id: int,
    session_data: SessionUpdate,
    current_therapist: Therapist = Depends(get_current_therapist),
    db: DBSession = Depends(get_db)
):
    """Update session"""
    
    session = db.query(Session).join(Patient).filter(
        Session.id == session_id,
        Patient.therapist_id == current_therapist.id
    ).first()
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )
    
    # Update fields
    update_data = session_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(session, field, value)
    
    session.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(session)
    
    return {
        "success": True,
        "message": "Session updated successfully",
        "session": session.to_dict()
    }

@router.post("/{session_id}/audio", response_model=dict)
async def upload_session_audio(
    session_id: int,
    file: UploadFile = File(...),
    current_therapist: Therapist = Depends(get_current_therapist),
    db: DBSession = Depends(get_db)
):
    """Upload audio file for session"""
    
    session = db.query(Session).join(Patient).filter(
        Session.id == session_id,
        Patient.therapist_id == current_therapist.id
    ).first()
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )
    
    # Create uploads directory if not exists
    upload_dir = f"uploads/sessions/{session.patient_id}"
    os.makedirs(upload_dir, exist_ok=True)
    
    # Generate unique filename
    file_extension = os.path.splitext(file.filename)[1]
    filename = f"session_{session_id}_{uuid.uuid4()}{file_extension}"
    file_path = os.path.join(upload_dir, filename)
    
    # Save file
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # Update session
    session.audio_file_path = file_path
    session.audio_file_size = os.path.getsize(file_path)
    session.updated_at = datetime.utcnow()
    db.commit()
    
    return {
        "success": True,
        "message": "Audio uploaded successfully",
        "file_path": file_path
    }

@router.delete("/{session_id}", response_model=dict)
async def delete_session(
    session_id: int,
    current_therapist: Therapist = Depends(get_current_therapist),
    db: DBSession = Depends(get_db)
):
    """Delete session"""
    
    session = db.query(Session).join(Patient).filter(
        Session.id == session_id,
        Patient.therapist_id == current_therapist.id
    ).first()
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )
    
    # Delete audio file if exists
    if session.audio_file_path and os.path.exists(session.audio_file_path):
        os.remove(session.audio_file_path)
    
    db.delete(session)
    db.commit()
    
    return {
        "success": True,
        "message": "Session deleted successfully"
    }
