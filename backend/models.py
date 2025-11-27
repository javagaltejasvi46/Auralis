from sqlalchemy import Column, Integer, String, DateTime, Float, Text, ForeignKey, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy import create_engine
from datetime import datetime
import hashlib
import secrets

Base = declarative_base()

class Therapist(Base):
    """Therapist/Doctor account"""
    __tablename__ = "therapists"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, nullable=False)
    license_number = Column(String, unique=True)
    specialization = Column(String)
    phone = Column(String)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime)
    
    # Relationships
    patients = relationship("Patient", back_populates="therapist", cascade="all, delete-orphan")
    
    def verify_password(self, password: str) -> bool:
        """Verify password using SHA-256 with salt"""
        try:
            salt, stored_hash = self.hashed_password.split('$', 1)
            password_hash = hashlib.sha256((salt + password).encode()).hexdigest()
            return password_hash == stored_hash
        except:
            return False
    
    @staticmethod
    def hash_password(password: str) -> str:
        """Hash password using SHA-256 with random salt"""
        salt = secrets.token_hex(16)
        password_hash = hashlib.sha256((salt + password).encode()).hexdigest()
        return f"{salt}${password_hash}"
    
    def to_dict(self):
        return {
            "id": self.id,
            "email": self.email,
            "username": self.username,
            "full_name": self.full_name,
            "license_number": self.license_number,
            "specialization": self.specialization,
            "phone": self.phone,
            "is_active": self.is_active,
            "is_verified": self.is_verified,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "patient_count": len(self.patients) if self.patients else 0
        }

class Patient(Base):
    """Patient profile"""
    __tablename__ = "patients"
    
    id = Column(Integer, primary_key=True, index=True)
    therapist_id = Column(Integer, ForeignKey("therapists.id"), nullable=False)
    patient_id = Column(String, unique=True, index=True, nullable=False)  # Custom ID
    full_name = Column(String, nullable=False)
    date_of_birth = Column(DateTime)
    gender = Column(String)
    phone = Column(String)
    email = Column(String)
    address = Column(Text)
    emergency_contact = Column(String)
    medical_history = Column(Text)
    notes = Column(Text)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    therapist = relationship("Therapist", back_populates="patients")
    sessions = relationship("Session", back_populates="patient", cascade="all, delete-orphan")
    
    def to_dict(self, include_sessions=False):
        data = {
            "id": self.id,
            "patient_id": self.patient_id,
            "full_name": self.full_name,
            "date_of_birth": self.date_of_birth.isoformat() if self.date_of_birth else None,
            "gender": self.gender,
            "phone": self.phone,
            "email": self.email,
            "address": self.address,
            "emergency_contact": self.emergency_contact,
            "medical_history": self.medical_history,
            "notes": self.notes,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "session_count": len(self.sessions) if self.sessions else 0
        }
        if include_sessions:
            data["sessions"] = [s.to_dict() for s in self.sessions]
        return data

class Session(Base):
    """Therapy session with transcription"""
    __tablename__ = "sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False)
    session_number = Column(Integer, nullable=False)
    session_date = Column(DateTime, default=datetime.utcnow)
    duration = Column(Integer)  # Duration in seconds
    language = Column(String, default="hindi")
    
    # Transcription data
    original_transcription = Column(Text)
    translated_transcription = Column(Text)
    translation_language = Column(String)
    
    # Audio file
    audio_file_path = Column(String)
    audio_file_size = Column(Integer)
    
    # Session metadata
    notes = Column(Text)
    diagnosis = Column(Text)
    treatment_plan = Column(Text)
    is_completed = Column(Boolean, default=False)
    
    # Notes metadata (for AI-generated notes tracking)
    notes_is_ai_generated = Column(Boolean, default=False)
    notes_edited_from_ai = Column(Boolean, default=False)
    notes_generated_at = Column(DateTime, nullable=True)
    notes_last_edited_at = Column(DateTime, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    patient = relationship("Patient", back_populates="sessions")
    
    def to_dict(self):
        return {
            "id": self.id,
            "patient_id": self.patient_id,
            "session_number": self.session_number,
            "session_date": self.session_date.isoformat() if self.session_date else None,
            "duration": self.duration,
            "language": self.language,
            "original_transcription": self.original_transcription,
            "translated_transcription": self.translated_transcription,
            "translation_language": self.translation_language,
            "audio_file_path": self.audio_file_path,
            "audio_file_size": self.audio_file_size,
            "notes": self.notes,
            "diagnosis": self.diagnosis,
            "treatment_plan": self.treatment_plan,
            "is_completed": self.is_completed,
            "notes_metadata": {
                "is_ai_generated": self.notes_is_ai_generated,
                "edited_from_ai": self.notes_edited_from_ai,
                "generated_at": self.notes_generated_at.isoformat() if self.notes_generated_at else None,
                "last_edited_at": self.notes_last_edited_at.isoformat() if self.notes_last_edited_at else None
            },
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }

class AudioRecord(Base):
    """Legacy audio records table"""
    __tablename__ = "audio_records"
    
    id = Column(String, primary_key=True, index=True)
    filename = Column(String, nullable=False)
    original_name = Column(String, nullable=False)
    file_path = Column(String, nullable=False)
    upload_time = Column(DateTime, default=datetime.utcnow)
    duration = Column(Float, nullable=True)
    size = Column(Integer, nullable=False)
    
    def to_dict(self):
        return {
            "id": self.id,
            "filename": self.filename,
            "original_name": self.original_name,
            "file_path": self.file_path,
            "upload_time": self.upload_time.isoformat(),
            "duration": self.duration,
            "size": self.size
        }

# Database setup
DATABASE_URL = "sqlite:///./auralis.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def create_tables():
    Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
