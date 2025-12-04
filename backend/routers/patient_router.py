"""
Patient management routes
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from sqlalchemy import or_
from pydantic import BaseModel, EmailStr
from typing import Optional, List, Dict, Any
from datetime import datetime
from models import Patient, Therapist, Session as SessionModel, get_db
from auth import get_current_therapist
from search_utils import (
    QueryType, 
    detect_query_type, 
    normalize_phone, 
    calculate_relevance,
    fuzzy_match
)
from summarization_service import summarization_service
import uuid
import io

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
    
    # Patient Information (Extended)
    age: Optional[int] = None
    residence: Optional[str] = None
    education: Optional[str] = None
    occupation: Optional[str] = None
    marital_status: Optional[str] = None
    date_of_assessment: Optional[str] = None
    
    # Medical History (Detailed)
    current_medical_conditions: Optional[str] = None
    past_medical_conditions: Optional[str] = None
    current_medications: Optional[str] = None
    allergies: Optional[str] = None
    hospitalizations: Optional[str] = None
    
    # Psychiatric History
    previous_psychiatric_diagnoses: Optional[str] = None
    previous_psychiatric_treatment: Optional[str] = None
    previous_psychiatric_hospitalizations: Optional[str] = None
    suicide_self_harm_history: Optional[str] = None
    substance_use_history: Optional[str] = None
    
    # Family History
    psychiatric_illness_family: Optional[str] = None
    medical_illness_family: Optional[str] = None
    family_dynamics: Optional[str] = None
    significant_family_events: Optional[str] = None
    
    # Social History
    childhood_developmental_history: Optional[str] = None
    educational_history: Optional[str] = None
    occupational_history: Optional[str] = None
    relationship_history: Optional[str] = None
    social_support_system: Optional[str] = None
    living_situation: Optional[str] = None
    cultural_religious_background: Optional[str] = None
    
    # Clinical Assessment
    chief_complaint: Optional[str] = None
    chief_complaint_description: Optional[str] = None
    illness_onset: Optional[str] = None
    illness_progression: Optional[str] = None
    previous_episodes: Optional[str] = None
    triggers: Optional[str] = None
    impact_on_functioning: Optional[str] = None
    
    # Mental Status Examination
    mse_appearance: Optional[str] = None
    mse_behavior: Optional[str] = None
    mse_speech: Optional[str] = None
    mse_mood: Optional[str] = None
    mse_affect: Optional[str] = None
    mse_thought_process: Optional[str] = None
    mse_thought_content: Optional[str] = None
    mse_perception: Optional[str] = None
    mse_cognition: Optional[str] = None
    mse_insight: Optional[str] = None
    mse_judgment: Optional[str] = None

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
    
    # Patient Information (Extended)
    age: Optional[int] = None
    residence: Optional[str] = None
    education: Optional[str] = None
    occupation: Optional[str] = None
    marital_status: Optional[str] = None
    date_of_assessment: Optional[str] = None
    
    # Medical History (Detailed)
    current_medical_conditions: Optional[str] = None
    past_medical_conditions: Optional[str] = None
    current_medications: Optional[str] = None
    allergies: Optional[str] = None
    hospitalizations: Optional[str] = None
    
    # Psychiatric History
    previous_psychiatric_diagnoses: Optional[str] = None
    previous_psychiatric_treatment: Optional[str] = None
    previous_psychiatric_hospitalizations: Optional[str] = None
    suicide_self_harm_history: Optional[str] = None
    substance_use_history: Optional[str] = None
    
    # Family History
    psychiatric_illness_family: Optional[str] = None
    medical_illness_family: Optional[str] = None
    family_dynamics: Optional[str] = None
    significant_family_events: Optional[str] = None
    
    # Social History
    childhood_developmental_history: Optional[str] = None
    educational_history: Optional[str] = None
    occupational_history: Optional[str] = None
    relationship_history: Optional[str] = None
    social_support_system: Optional[str] = None
    living_situation: Optional[str] = None
    cultural_religious_background: Optional[str] = None
    
    # Clinical Assessment
    chief_complaint: Optional[str] = None
    chief_complaint_description: Optional[str] = None
    illness_onset: Optional[str] = None
    illness_progression: Optional[str] = None
    previous_episodes: Optional[str] = None
    triggers: Optional[str] = None
    impact_on_functioning: Optional[str] = None
    
    # Mental Status Examination
    mse_appearance: Optional[str] = None
    mse_behavior: Optional[str] = None
    mse_speech: Optional[str] = None
    mse_mood: Optional[str] = None
    mse_affect: Optional[str] = None
    mse_thought_process: Optional[str] = None
    mse_thought_content: Optional[str] = None
    mse_perception: Optional[str] = None
    mse_cognition: Optional[str] = None
    mse_insight: Optional[str] = None
    mse_judgment: Optional[str] = None

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
    
    # Parse date of assessment
    doa = None
    if patient_data.date_of_assessment:
        try:
            doa = datetime.fromisoformat(patient_data.date_of_assessment.replace('Z', '+00:00'))
        except:
            pass
    
    # Create patient with all fields
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
        notes=patient_data.notes,
        
        # Patient Information (Extended)
        age=patient_data.age,
        residence=patient_data.residence,
        education=patient_data.education,
        occupation=patient_data.occupation,
        marital_status=patient_data.marital_status,
        date_of_assessment=doa,
        
        # Medical History (Detailed)
        current_medical_conditions=patient_data.current_medical_conditions,
        past_medical_conditions=patient_data.past_medical_conditions,
        current_medications=patient_data.current_medications,
        allergies=patient_data.allergies,
        hospitalizations=patient_data.hospitalizations,
        
        # Psychiatric History
        previous_psychiatric_diagnoses=patient_data.previous_psychiatric_diagnoses,
        previous_psychiatric_treatment=patient_data.previous_psychiatric_treatment,
        previous_psychiatric_hospitalizations=patient_data.previous_psychiatric_hospitalizations,
        suicide_self_harm_history=patient_data.suicide_self_harm_history,
        substance_use_history=patient_data.substance_use_history,
        
        # Family History
        psychiatric_illness_family=patient_data.psychiatric_illness_family,
        medical_illness_family=patient_data.medical_illness_family,
        family_dynamics=patient_data.family_dynamics,
        significant_family_events=patient_data.significant_family_events,
        
        # Social History
        childhood_developmental_history=patient_data.childhood_developmental_history,
        educational_history=patient_data.educational_history,
        occupational_history=patient_data.occupational_history,
        relationship_history=patient_data.relationship_history,
        social_support_system=patient_data.social_support_system,
        living_situation=patient_data.living_situation,
        cultural_religious_background=patient_data.cultural_religious_background,
        
        # Clinical Assessment
        chief_complaint=patient_data.chief_complaint,
        chief_complaint_description=patient_data.chief_complaint_description,
        illness_onset=patient_data.illness_onset,
        illness_progression=patient_data.illness_progression,
        previous_episodes=patient_data.previous_episodes,
        triggers=patient_data.triggers,
        impact_on_functioning=patient_data.impact_on_functioning,
        
        # Mental Status Examination
        mse_appearance=patient_data.mse_appearance,
        mse_behavior=patient_data.mse_behavior,
        mse_speech=patient_data.mse_speech,
        mse_mood=patient_data.mse_mood,
        mse_affect=patient_data.mse_affect,
        mse_thought_process=patient_data.mse_thought_process,
        mse_thought_content=patient_data.mse_thought_content,
        mse_perception=patient_data.mse_perception,
        mse_cognition=patient_data.mse_cognition,
        mse_insight=patient_data.mse_insight,
        mse_judgment=patient_data.mse_judgment,
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

@router.get("/search", response_model=dict)
async def search_patients(
    q: str = Query(..., min_length=2, description="Search query (min 2 characters)"),
    current_therapist: Therapist = Depends(get_current_therapist),
    db: Session = Depends(get_db)
):
    """
    Search patients by name, phone number, or patient ID.
    Automatically detects query type and returns results sorted by relevance.
    """
    query_type = detect_query_type(q)
    query_lower = q.lower().strip()
    
    # Get all active patients for this therapist
    patients = db.query(Patient).filter(
        Patient.therapist_id == current_therapist.id,
        Patient.is_active == True
    ).all()
    
    results = []
    
    for patient in patients:
        relevance, match_field, match_positions = calculate_relevance(
            patient_id=patient.patient_id or "",
            full_name=patient.full_name or "",
            phone=patient.phone or "",
            query=q,
            query_type=query_type
        )
        
        if relevance > 0:
            results.append({
                "patient": patient.to_dict(),
                "relevance_score": relevance,
                "match_field": match_field,
                "match_positions": match_positions
            })
    
    # Sort by relevance score (highest first)
    results.sort(key=lambda x: x["relevance_score"], reverse=True)
    
    return {
        "success": True,
        "query": q,
        "query_type": query_type.value,
        "count": len(results),
        "results": results
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
    
    # Parse date fields
    if 'date_of_birth' in update_data and update_data['date_of_birth']:
        try:
            update_data['date_of_birth'] = datetime.fromisoformat(
                update_data['date_of_birth'].replace('Z', '+00:00')
            )
        except:
            del update_data['date_of_birth']
    
    if 'date_of_assessment' in update_data and update_data['date_of_assessment']:
        try:
            update_data['date_of_assessment'] = datetime.fromisoformat(
                update_data['date_of_assessment'].replace('Z', '+00:00')
            )
        except:
            del update_data['date_of_assessment']
    
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

@router.get("/{patient_id}/overall-summary", response_model=dict)
async def get_overall_summary(
    patient_id: int,
    current_therapist: Therapist = Depends(get_current_therapist),
    db: Session = Depends(get_db)
):
    """Generate overall summary for a patient following psychotherapy report template"""
    
    patient = db.query(Patient).filter(
        Patient.id == patient_id,
        Patient.therapist_id == current_therapist.id
    ).first()
    
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient not found"
        )
    
    # Get all sessions for this patient
    sessions = db.query(SessionModel).filter(
        SessionModel.patient_id == patient_id
    ).order_by(SessionModel.session_date.asc()).all()
    
    # Convert to dict format
    sessions_data = [s.to_dict() for s in sessions]
    patient_data = patient.to_dict()
    
    # Generate overall summary
    overall_summary = summarization_service.generate_overall_summary(
        patient_data=patient_data,
        sessions=sessions_data,
        therapist_name=current_therapist.full_name
    )
    
    return {
        "success": True,
        "overall_summary": overall_summary
    }


class ExportReportRequest(BaseModel):
    """Request model for exporting PDF with edited data"""
    # Patient Information
    patient_name: Optional[str] = None
    patient_age: Optional[str] = None
    patient_gender: Optional[str] = None
    patient_dob: Optional[str] = None
    patient_residence: Optional[str] = None
    patient_education: Optional[str] = None
    patient_occupation: Optional[str] = None
    patient_marital_status: Optional[str] = None
    date_of_assessment: Optional[str] = None
    
    # Medical History
    current_medical_conditions: Optional[str] = None
    past_medical_conditions: Optional[str] = None
    current_medications: Optional[str] = None
    allergies: Optional[str] = None
    hospitalizations: Optional[str] = None
    
    # Psychiatric History
    previous_diagnoses: Optional[str] = None
    previous_treatment: Optional[str] = None
    previous_hospitalizations: Optional[str] = None
    suicide_self_harm_history: Optional[str] = None
    substance_use_history: Optional[str] = None
    
    # Family History
    psychiatric_illness_family: Optional[str] = None
    medical_illness_family: Optional[str] = None
    family_dynamics: Optional[str] = None
    significant_family_events: Optional[str] = None
    
    # Social History
    childhood_developmental: Optional[str] = None
    educational_history: Optional[str] = None
    occupational_history: Optional[str] = None
    relationship_history: Optional[str] = None
    social_support: Optional[str] = None
    living_situation: Optional[str] = None
    cultural_religious: Optional[str] = None
    
    # Chief Complaints
    chief_complaint: Optional[str] = None
    chief_complaint_description: Optional[str] = None
    
    # Course of Illness
    illness_onset: Optional[str] = None
    illness_progression: Optional[str] = None
    previous_episodes: Optional[str] = None
    triggers: Optional[str] = None
    impact_on_functioning: Optional[str] = None
    
    # Mental Status Examination
    mse_appearance: Optional[str] = None
    mse_behavior: Optional[str] = None
    mse_speech: Optional[str] = None
    mse_mood: Optional[str] = None
    mse_affect: Optional[str] = None
    mse_thought_process: Optional[str] = None
    mse_thought_content: Optional[str] = None
    mse_perception: Optional[str] = None
    mse_cognition: Optional[str] = None
    mse_insight: Optional[str] = None
    mse_judgment: Optional[str] = None
    
    # Session summaries (list of edited session summaries)
    session_summaries: Optional[List[Dict[str, Any]]] = None


@router.get("/{patient_id}/report-data", response_model=dict)
async def get_report_data(
    patient_id: int,
    current_therapist: Therapist = Depends(get_current_therapist),
    db: Session = Depends(get_db)
):
    """Get all report data for editing before PDF export - combines patient details and AI-generated summary"""
    
    patient = db.query(Patient).filter(
        Patient.id == patient_id,
        Patient.therapist_id == current_therapist.id
    ).first()
    
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient not found"
        )
    
    # Get all sessions
    sessions = db.query(SessionModel).filter(
        SessionModel.patient_id == patient_id
    ).order_by(SessionModel.session_date.asc()).all()
    
    sessions_data = [s.to_dict() for s in sessions]
    patient_data = patient.to_dict()
    
    # Generate overall summary with AI
    overall_summary = summarization_service.generate_overall_summary(
        patient_data=patient_data,
        sessions=sessions_data,
        therapist_name=current_therapist.full_name
    )
    
    return {
        "success": True,
        "report_data": overall_summary,
        "therapist_name": current_therapist.full_name,
        "generated_date": datetime.now().isoformat()
    }


@router.post("/{patient_id}/export-pdf")
async def export_patient_pdf_with_edits(
    patient_id: int,
    report_data: ExportReportRequest,
    current_therapist: Therapist = Depends(get_current_therapist),
    db: Session = Depends(get_db)
):
    """Export patient report as PDF with user-edited data"""
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
    
    patient = db.query(Patient).filter(
        Patient.id == patient_id,
        Patient.therapist_id == current_therapist.id
    ).first()
    
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient not found"
        )
    
    # Create PDF buffer
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=72, leftMargin=72, topMargin=72, bottomMargin=72)
    
    # Styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle('Title', parent=styles['Heading1'], fontSize=18, spaceAfter=20, alignment=1)
    heading_style = ParagraphStyle('Heading', parent=styles['Heading2'], fontSize=14, spaceAfter=10, spaceBefore=15, textColor=colors.darkblue)
    subheading_style = ParagraphStyle('SubHeading', parent=styles['Heading3'], fontSize=12, spaceAfter=8)
    normal_style = ParagraphStyle('Normal', parent=styles['Normal'], fontSize=10, spaceAfter=6)
    field_style = ParagraphStyle('Field', parent=styles['Normal'], fontSize=10, spaceAfter=4, leftIndent=20)
    
    story = []
    
    # Title
    story.append(Paragraph("PSYCHOTHERAPY REPORT", title_style))
    story.append(Paragraph(f"Generated: {datetime.now().strftime('%Y-%m-%d')}", normal_style))
    story.append(Paragraph(f"Therapist: {current_therapist.full_name}", normal_style))
    story.append(Spacer(1, 20))
    
    # Helper function to get value with fallback
    def get_val(edited_val, patient_attr, default='N/A'):
        if edited_val:
            return edited_val
        val = getattr(patient, patient_attr, None) if hasattr(patient, patient_attr) else None
        return val if val else default
    
    # Patient Information
    story.append(Paragraph("PATIENT INFORMATION", heading_style))
    story.append(Paragraph(f"Name: {report_data.patient_name or patient.full_name}", field_style))
    story.append(Paragraph(f"Age: {report_data.patient_age or patient.age or 'N/A'}", field_style))
    story.append(Paragraph(f"Gender: {report_data.patient_gender or patient.gender or 'N/A'}", field_style))
    story.append(Paragraph(f"Date of Birth: {report_data.patient_dob or (patient.date_of_birth.strftime('%Y-%m-%d') if patient.date_of_birth else 'N/A')}", field_style))
    story.append(Paragraph(f"Residence: {report_data.patient_residence or patient.residence or 'N/A'}", field_style))
    story.append(Paragraph(f"Education: {report_data.patient_education or patient.education or 'N/A'}", field_style))
    story.append(Paragraph(f"Occupation: {report_data.patient_occupation or patient.occupation or 'N/A'}", field_style))
    story.append(Paragraph(f"Marital Status: {report_data.patient_marital_status or patient.marital_status or 'N/A'}", field_style))
    story.append(Paragraph(f"Date of Assessment: {report_data.date_of_assessment or datetime.now().strftime('%Y-%m-%d')}", field_style))
    
    # Medical History
    story.append(Paragraph("MEDICAL HISTORY", heading_style))
    story.append(Paragraph(f"Current Medical Conditions: {report_data.current_medical_conditions or patient.current_medical_conditions or 'None'}", field_style))
    story.append(Paragraph(f"Past Medical Conditions: {report_data.past_medical_conditions or patient.past_medical_conditions or 'None'}", field_style))
    story.append(Paragraph(f"Current Medications: {report_data.current_medications or patient.current_medications or 'None'}", field_style))
    story.append(Paragraph(f"Allergies: {report_data.allergies or patient.allergies or 'None'}", field_style))
    story.append(Paragraph(f"Hospitalizations: {report_data.hospitalizations or patient.hospitalizations or 'None'}", field_style))
    
    # Psychiatric History
    story.append(Paragraph("PSYCHIATRIC HISTORY", heading_style))
    story.append(Paragraph(f"Previous Diagnoses: {report_data.previous_diagnoses or patient.previous_psychiatric_diagnoses or 'None'}", field_style))
    story.append(Paragraph(f"Previous Treatment: {report_data.previous_treatment or patient.previous_psychiatric_treatment or 'None'}", field_style))
    story.append(Paragraph(f"Previous Hospitalizations: {report_data.previous_hospitalizations or patient.previous_psychiatric_hospitalizations or 'None'}", field_style))
    story.append(Paragraph(f"Suicide/Self-Harm History: {report_data.suicide_self_harm_history or patient.suicide_self_harm_history or 'None'}", field_style))
    story.append(Paragraph(f"Substance Use History: {report_data.substance_use_history or patient.substance_use_history or 'None'}", field_style))
    
    # Family History
    story.append(Paragraph("FAMILY HISTORY", heading_style))
    story.append(Paragraph(f"Psychiatric Illness in Family: {report_data.psychiatric_illness_family or patient.psychiatric_illness_family or 'None'}", field_style))
    story.append(Paragraph(f"Medical Illness in Family: {report_data.medical_illness_family or patient.medical_illness_family or 'None'}", field_style))
    story.append(Paragraph(f"Family Dynamics: {report_data.family_dynamics or patient.family_dynamics or 'N/A'}", field_style))
    story.append(Paragraph(f"Significant Family Events: {report_data.significant_family_events or patient.significant_family_events or 'None'}", field_style))
    
    # Social History
    story.append(Paragraph("SOCIAL HISTORY", heading_style))
    story.append(Paragraph(f"Childhood/Developmental: {report_data.childhood_developmental or patient.childhood_developmental_history or 'N/A'}", field_style))
    story.append(Paragraph(f"Educational History: {report_data.educational_history or patient.educational_history or 'N/A'}", field_style))
    story.append(Paragraph(f"Occupational History: {report_data.occupational_history or patient.occupational_history or 'N/A'}", field_style))
    story.append(Paragraph(f"Relationship History: {report_data.relationship_history or patient.relationship_history or 'N/A'}", field_style))
    story.append(Paragraph(f"Social Support System: {report_data.social_support or patient.social_support_system or 'N/A'}", field_style))
    story.append(Paragraph(f"Living Situation: {report_data.living_situation or patient.living_situation or 'N/A'}", field_style))
    story.append(Paragraph(f"Cultural/Religious Background: {report_data.cultural_religious or patient.cultural_religious_background or 'N/A'}", field_style))
    
    # Helper function to get value with proper fallback
    def get_pdf_value(edited_val, patient_attr, default='N/A'):
        """Get value from edited data, then patient data, then default"""
        if edited_val and edited_val not in ['', None, 'N/A', 'None']:
            return edited_val
        val = getattr(patient, patient_attr, None) if hasattr(patient, patient_attr) else None
        if val and val not in ['', None, 'N/A', 'None']:
            return val
        return default
    
    # Chief Complaints
    story.append(Spacer(1, 5))
    story.append(Paragraph("CHIEF COMPLAINTS", heading_style))
    story.append(Paragraph(f"Primary Complaint: {get_pdf_value(report_data.chief_complaint, 'chief_complaint', 'Under assessment')}", field_style))
    story.append(Paragraph(f"Description: {get_pdf_value(report_data.chief_complaint_description, 'chief_complaint_description', 'Initial assessment in progress')}", field_style))
    story.append(Spacer(1, 10))
    
    # Course of Illness
    story.append(Paragraph("COURSE OF ILLNESS", heading_style))
    story.append(Paragraph(f"Onset: {get_pdf_value(report_data.illness_onset, 'illness_onset', 'Gradual')}", field_style))
    story.append(Paragraph(f"Progression: {get_pdf_value(report_data.illness_progression, 'illness_progression', 'Stable')}", field_style))
    story.append(Paragraph(f"Previous Episodes: {get_pdf_value(report_data.previous_episodes, 'previous_episodes', 'None reported')}", field_style))
    story.append(Paragraph(f"Triggers: {get_pdf_value(report_data.triggers, 'triggers', 'Under evaluation')}", field_style))
    story.append(Paragraph(f"Impact on Functioning: {get_pdf_value(report_data.impact_on_functioning, 'impact_on_functioning', 'Moderate')}", field_style))
    story.append(Spacer(1, 10))
    
    # Mental Status Examination
    story.append(Paragraph("BASELINE ASSESSMENT - MENTAL STATUS EXAMINATION", heading_style))
    story.append(Paragraph(f"Appearance: {get_pdf_value(report_data.mse_appearance, 'mse_appearance', 'Appropriate')}", field_style))
    story.append(Paragraph(f"Behavior: {get_pdf_value(report_data.mse_behavior, 'mse_behavior', 'Cooperative')}", field_style))
    story.append(Paragraph(f"Speech: {get_pdf_value(report_data.mse_speech, 'mse_speech', 'Normal')}", field_style))
    story.append(Paragraph(f"Mood: {get_pdf_value(report_data.mse_mood, 'mse_mood', 'Euthymic')}", field_style))
    story.append(Paragraph(f"Affect: {get_pdf_value(report_data.mse_affect, 'mse_affect', 'Appropriate')}", field_style))
    story.append(Paragraph(f"Thought Process: {get_pdf_value(report_data.mse_thought_process, 'mse_thought_process', 'Linear')}", field_style))
    story.append(Paragraph(f"Thought Content: {get_pdf_value(report_data.mse_thought_content, 'mse_thought_content', 'Normal')}", field_style))
    story.append(Paragraph(f"Perception: {get_pdf_value(report_data.mse_perception, 'mse_perception', 'Intact')}", field_style))
    story.append(Paragraph(f"Cognition: {get_pdf_value(report_data.mse_cognition, 'mse_cognition', 'Intact')}", field_style))
    story.append(Paragraph(f"Insight: {get_pdf_value(report_data.mse_insight, 'mse_insight', 'Fair')}", field_style))
    story.append(Paragraph(f"Judgment: {get_pdf_value(report_data.mse_judgment, 'mse_judgment', 'Fair')}", field_style))
    
    # Helper function to convert markdown-style formatting to PDF HTML and add spacing after sections
    import re
    def format_summary_for_pdf(text: str) -> str:
        """Convert markdown-style formatting to ReportLab HTML and add spacing after sections"""
        if not text:
            return text
        
        # First escape ampersands (must be done first)
        text = text.replace('&', '&amp;')
        
        # Temporarily replace our HTML tags with placeholders
        placeholders = []
        def save_tag(match):
            placeholders.append(match.group(0))
            return f"__TAG_{len(placeholders)-1}__"
        
        # Convert markdown to HTML first
        # Convert **Section:** content to bold section with line break after
        # This captures content until the next **Section:** or end of text
        text = re.sub(r'\*\*([^*]+):\*\*\s*((?:(?!\*\*[^*]+:\*\*).)+)', 
                     lambda m: f'<b>{m.group(1)}:</b> {m.group(2).strip()}<br/><br/>', 
                     text, flags=re.DOTALL)
        
        # Convert remaining **text** to bold
        text = re.sub(r'\*\*([^*]+)\*\*', r'<b>\1</b>', text)
        
        # Convert {{RED:text}} to red colored text
        text = re.sub(r'\{\{RED:([^}]+)\}\}', r'<font color="red"><b>\1</b></font>', text)
        
        # Save all HTML tags
        text = re.sub(r'<[^>]+>', save_tag, text)
        
        # Escape remaining < and >
        text = text.replace('<', '&lt;').replace('>', '&gt;')
        
        # Restore HTML tags
        for i, tag in enumerate(placeholders):
            text = text.replace(f"__TAG_{i}__", tag)
        
        return text
    
    # Get all sessions
    sessions_for_display = report_data.session_summaries if report_data.session_summaries else []
    if not sessions_for_display:
        # Get from database
        db_sessions = db.query(SessionModel).filter(
            SessionModel.patient_id == patient_id
        ).order_by(SessionModel.session_date.desc()).all()
        if db_sessions:
            sessions_for_display = [{'session_number': s.session_number, 
                                    'session_date': s.session_date.strftime('%Y-%m-%d') if s.session_date else 'N/A',
                                    'summary': s.notes or ''} for s in db_sessions]
    
    # Latest Session Summary (only if there are multiple sessions)
    if len(sessions_for_display) > 1:
        latest = sessions_for_display[-1] if report_data.session_summaries else sessions_for_display[0]
        story.append(Spacer(1, 10))
        story.append(Paragraph("LATEST SESSION SUMMARY", heading_style))
        story.append(Paragraph(f"<b>Session #{latest.get('session_number', 'N/A')} | Date: {latest.get('session_date', 'N/A')}</b>", subheading_style))
        story.append(Spacer(1, 8))
        
        latest_summary = latest.get('summary', '')
        if latest_summary:
            formatted_latest = format_summary_for_pdf(latest_summary)
            try:
                story.append(Paragraph(formatted_latest, field_style))
            except:
                clean_text = re.sub(r'<[^>]+>', '', formatted_latest)
                story.append(Paragraph(clean_text, field_style))
        story.append(Spacer(1, 15))
    
    # Session Recording Summaries (All Sessions)
    story.append(Spacer(1, 10))
    story.append(Paragraph("SESSION RECORDING SUMMARIES", heading_style))
    story.append(Spacer(1, 10))
    
    # Create a style for formatted session content
    session_content_style = ParagraphStyle('SessionContent', parent=styles['Normal'], fontSize=10, spaceAfter=6, leftIndent=20, leading=14)
    
    if sessions_for_display:
        # Display all sessions
        for idx, session_data in enumerate(sessions_for_display):
            session_num = session_data.get('session_number', 'N/A')
            session_date = session_data.get('session_date', 'N/A')
            
            # Add separator line between sessions
            if idx > 0:
                story.append(Spacer(1, 10))
                story.append(Paragraph("─" * 80, normal_style))
                story.append(Spacer(1, 10))
            
            story.append(Paragraph(f"<b>Session #{session_num} | Date: {session_date}</b>", subheading_style))
            story.append(Spacer(1, 8))
            
            summary = session_data.get('summary', '')
            if summary:
                # Format with spacing after each section
                formatted_summary = format_summary_for_pdf(summary)
                try:
                    story.append(Paragraph(formatted_summary, session_content_style))
                except:
                    # Fallback if formatting fails
                    clean_text = re.sub(r'<[^>]+>', '', formatted_summary)
                    story.append(Paragraph(clean_text, field_style))
            story.append(Spacer(1, 12))
    else:
        story.append(Paragraph("No sessions recorded yet.", normal_style))
    
    # Therapist signature section
    story.append(Spacer(1, 30))
    story.append(Paragraph("_" * 50, normal_style))
    story.append(Paragraph(f"Therapist Name: {current_therapist.full_name}", normal_style))
    story.append(Paragraph(f"Date: {datetime.now().strftime('%Y-%m-%d')}", normal_style))
    
    # Build PDF
    doc.build(story)
    buffer.seek(0)
    
    return StreamingResponse(
        buffer,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=patient_{patient.patient_id}_report.pdf"}
    )


@router.get("/{patient_id}/export-pdf")
async def export_patient_pdf(
    patient_id: int,
    current_therapist: Therapist = Depends(get_current_therapist),
    db: Session = Depends(get_db)
):
    """Export patient report as PDF (without edits - uses stored data)"""
    # Create empty request to use the POST endpoint logic
    empty_request = ExportReportRequest()
    return await export_patient_pdf_with_edits(patient_id, empty_request, current_therapist, db)
