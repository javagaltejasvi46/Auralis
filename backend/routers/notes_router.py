"""
Notes Router - API endpoints for AI-generated session notes
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from models import Session as SessionModel, get_db
from auth import get_current_therapist


router = APIRouter(prefix="/sessions", tags=["notes"])


class GenerateNotesRequest(BaseModel):
    regenerate: bool = False


class GenerateNotesResponse(BaseModel):
    success: bool
    session_id: int
    generated_notes: str
    can_edit: bool = True
    inference_time: Optional[float] = None


class UpdateNotesRequest(BaseModel):
    notes: str
    is_ai_generated: bool = False
    edited_from_ai: bool = False


@router.post("/{session_id}/generate-notes", response_model=GenerateNotesResponse)
async def generate_session_notes(
    session_id: int,
    request: GenerateNotesRequest,
    db: Session = Depends(get_db),
    current_therapist = Depends(get_current_therapist)
):
    """Auto-generate clinical notes for a specific session"""
    try:
        # Get session
        session = db.query(SessionModel).filter(SessionModel.id == session_id).first()
        
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        # Check if notes already exist
        if session.notes and not request.regenerate:
            raise HTTPException(
                status_code=400,
                detail="Notes already exist. Set regenerate=true to overwrite."
            )
        
        # Get transcription
        transcription = session.original_transcription
        
        if not transcription or len(transcription.strip()) < 50:
            raise HTTPException(
                status_code=400,
                detail="Session transcription is too short for summarization"
            )
        
        # Import summarization service
        try:
            from summarization_service_phi3 import summarization_service
            
            if summarization_service is None:
                raise HTTPException(
                    status_code=503,
                    detail="Summarization service not available"
                )
        except ImportError:
            # Fallback to old service if new one not available
            from summarization_service import summarization_service
        
        # Generate notes
        import time
        start_time = time.time()
        
        generated_notes = summarization_service.summarize_single_session(transcription)
        
        inference_time = time.time() - start_time
        
        # Update session
        session.notes = generated_notes
        session.notes_is_ai_generated = True
        session.notes_edited_from_ai = False
        session.notes_generated_at = datetime.utcnow()
        session.notes_last_edited_at = datetime.utcnow()
        
        db.commit()
        db.refresh(session)
        
        return GenerateNotesResponse(
            success=True,
            session_id=session_id,
            generated_notes=generated_notes,
            can_edit=True,
            inference_time=round(inference_time, 2)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Generate notes error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{session_id}/notes")
async def update_session_notes(
    session_id: int,
    request: UpdateNotesRequest,
    db: Session = Depends(get_db),
    current_therapist = Depends(get_current_therapist)
):
    """Update session notes (user-edited or confirmed AI-generated)"""
    try:
        # Get session
        session = db.query(SessionModel).filter(SessionModel.id == session_id).first()
        
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        # Check if notes were AI-generated and are being edited
        was_ai_generated = session.notes_is_ai_generated
        notes_changed = session.notes != request.notes
        
        # Update notes
        session.notes = request.notes
        
        # Update metadata
        if request.is_ai_generated:
            session.notes_is_ai_generated = True
            session.notes_edited_from_ai = False
            if not session.notes_generated_at:
                session.notes_generated_at = datetime.utcnow()
        elif was_ai_generated and notes_changed:
            # User edited AI-generated notes
            session.notes_is_ai_generated = True
            session.notes_edited_from_ai = True
        else:
            # User-written notes
            session.notes_is_ai_generated = False
            session.notes_edited_from_ai = False
        
        session.notes_last_edited_at = datetime.utcnow()
        
        db.commit()
        db.refresh(session)
        
        return {
            "success": True,
            "session_id": session_id,
            "notes": session.notes,
            "updated_at": session.notes_last_edited_at.isoformat(),
            "notes_metadata": {
                "is_ai_generated": session.notes_is_ai_generated,
                "edited_from_ai": session.notes_edited_from_ai
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Update notes error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{session_id}")
async def get_session_with_notes(
    session_id: int,
    db: Session = Depends(get_db),
    current_therapist = Depends(get_current_therapist)
):
    """Get session with notes and metadata"""
    try:
        session = db.query(SessionModel).filter(SessionModel.id == session_id).first()
        
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        return session.to_dict()
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Get session error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
