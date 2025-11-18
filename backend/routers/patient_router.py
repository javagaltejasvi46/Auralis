"""
Patient management routes
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime
from models import Patient, Therapist, get_db
from auth import get_current_therapist
import uuid

router = APIRouter(prefix="/patients", tags=["Patients"])

class PatientCreate(BaseModel):
    patient_id: Optional[str] = None  # Allow custom patient ID
    full_name: str
    date_of_birth: Optional[str] = None
    gender: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[EmailStr] = None
    address: Optional[str] = None
    emergency_contact: Optional[str] = None
    medical_history: Optional[str] = None
    notes: Optional[str] = None

class PatientUpdate(BaseModel):
    full_name: Optional[str] = None
    date_of_birth: Optional[str] = None
    gender: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[EmailStr] = None
    address: Optional[str] = None
    emergency_contact: Optional[str] = None
    medical_history: Optional[str] = None
    notes: Optional[str] = None
    is_active: Optional[bool] = None

@router.post("/", response_model=dict)
async def create_patient(
    patient_data: PatientCreate,
    current_therapist: Therapist = Depends(get_current_therapist),
    db: Session = Depends(get_db)
):
    """Create new patient profile"""
    
    # Use provided patient ID or generate unique one
    patient_id = patient_data.patient_id or f"P{datetime.now().strftime('%Y%m%d')}{str(uuid.uuid4())[:8].upper()}"
    
    # Check if patient ID already exists
    existing = db.query(Patient).filter(Patient.patient_id == patient_id).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Patient ID already exists"
        )
    
    # Parse date of birth
    dob = None
    if patient_data.date_of_birth:
        try:
            dob = datetime.fromisoformat(patient_data.date_of_birth.replace('Z', '+00:00'))
        except:
            pass
    
    # Create patient
    new_patient = Patient(
        therapist_id=current_therapist.id,
        patient_id=patient_id,
        full_name=patient_data.full_name,
        date_of_birth=dob,
        gender=patient_data.gender,
        phone=patient_data.phone,
        email=patient_data.email,
        address=patient_data.address,
        emergency_contact=patient_data.emergency_contact,
        medical_history=patient_data.medical_history,
        notes=patient_data.notes
    )
    
    db.add(new_patient)
    db.commit()
    db.refresh(new_patient)
    
    return {
        "success": True,
        "message": "Patient created successfully",
        "patient": new_patient.to_dict()
    }

@router.get("/", response_model=dict)
async def get_patients(
    current_therapist: Therapist = Depends(get_current_therapist),
    db: Session = Depends(get_db),
    active_only: bool = True
):
    """Get all patients for current therapist"""
    
    query = db.query(Patient).filter(Patient.therapist_id == current_therapist.id)
    
    if active_only:
        query = query.filter(Patient.is_active == True)
    
    patients = query.order_by(Patient.created_at.desc()).all()
    
    return {
        "success": True,
        "count": len(patients),
        "patients": [p.to_dict() for p in patients]
    }

@router.get("/{patient_id}", response_model=dict)
async def get_patient(
    patient_id: int,
    current_therapist: Therapist = Depends(get_current_therapist),
    db: Session = Depends(get_db),
    include_sessions: bool = True
):
    """Get patient details"""
    
    patient = db.query(Patient).filter(
        Patient.id == patient_id,
        Patient.therapist_id == current_therapist.id
    ).first()
    
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient not found"
        )
    
    return {
        "success": True,
        "patient": patient.to_dict(include_sessions=include_sessions)
    }

@router.put("/{patient_id}", response_model=dict)
async def update_patient(
    patient_id: int,
    patient_data: PatientUpdate,
    current_therapist: Therapist = Depends(get_current_therapist),
    db: Session = Depends(get_db)
):
    """Update patient profile"""
    
    patient = db.query(Patient).filter(
        Patient.id == patient_id,
        Patient.therapist_id == current_therapist.id
    ).first()
    
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient not found"
        )
    
    # Update fields
    update_data = patient_data.dict(exclude_unset=True)
    
    if 'date_of_birth' in update_data and update_data['date_of_birth']:
        try:
            update_data['date_of_birth'] = datetime.fromisoformat(
                update_data['date_of_birth'].replace('Z', '+00:00')
            )
        except:
            del update_data['date_of_birth']
    
    for field, value in update_data.items():
        setattr(patient, field, value)
    
    patient.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(patient)
    
    return {
        "success": True,
        "message": "Patient updated successfully",
        "patient": patient.to_dict()
    }

@router.delete("/{patient_id}", response_model=dict)
async def delete_patient(
    patient_id: int,
    current_therapist: Therapist = Depends(get_current_therapist),
    db: Session = Depends(get_db)
):
    """Delete patient (soft delete)"""
    
    patient = db.query(Patient).filter(
        Patient.id == patient_id,
        Patient.therapist_id == current_therapist.id
    ).first()
    
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient not found"
        )
    
    patient.is_active = False
    patient.updated_at = datetime.utcnow()
    db.commit()
    
    return {
        "success": True,
        "message": "Patient deactivated successfully"
    }
