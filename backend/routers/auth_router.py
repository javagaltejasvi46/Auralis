"""
Authentication routes
"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from datetime import datetime
from models import Therapist, get_db
from auth import create_access_token, get_current_therapist

router = APIRouter(prefix="/auth", tags=["Authentication"])

class TherapistRegister(BaseModel):
    email: EmailStr
    username: str
    password: str
    full_name: str
    license_number: str
    specialization: str = None
    phone: str = None

class TherapistLogin(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str
    therapist: dict

@router.post("/register", response_model=dict)
async def register(therapist_data: TherapistRegister, db: Session = Depends(get_db)):
    """Register new therapist account"""
    
    # Check if email exists
    if db.query(Therapist).filter(Therapist.email == therapist_data.email).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Check if username exists
    if db.query(Therapist).filter(Therapist.username == therapist_data.username).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already taken"
        )
    
    # Check if license number exists
    if therapist_data.license_number:
        if db.query(Therapist).filter(Therapist.license_number == therapist_data.license_number).first():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="License number already registered"
            )
    
    # Create new therapist
    new_therapist = Therapist(
        email=therapist_data.email,
        username=therapist_data.username,
        hashed_password=Therapist.hash_password(therapist_data.password),
        full_name=therapist_data.full_name,
        license_number=therapist_data.license_number,
        specialization=therapist_data.specialization,
        phone=therapist_data.phone,
        is_verified=True  # Auto-verify for now, can add email verification later
    )
    
    db.add(new_therapist)
    db.commit()
    db.refresh(new_therapist)
    
    return {
        "success": True,
        "message": "Account created successfully",
        "therapist": new_therapist.to_dict()
    }

@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """Login therapist"""
    
    # Find therapist by username
    therapist = db.query(Therapist).filter(Therapist.username == form_data.username).first()
    
    if not therapist or not therapist.verify_password(form_data.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not therapist.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is inactive"
        )
    
    # Update last login
    therapist.last_login = datetime.utcnow()
    db.commit()
    
    # Create access token
    access_token = create_access_token(data={"sub": str(therapist.id)})
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "therapist": therapist.to_dict()
    }

@router.get("/me", response_model=dict)
async def get_current_user(current_therapist: Therapist = Depends(get_current_therapist)):
    """Get current therapist profile"""
    return {
        "success": True,
        "therapist": current_therapist.to_dict()
    }

@router.post("/logout")
async def logout():
    """Logout (client-side token removal)"""
    return {
        "success": True,
        "message": "Logged out successfully"
    }
