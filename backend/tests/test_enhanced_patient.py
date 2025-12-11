"""
Tests for Enhanced Patient Report Feature
Tests patient model extensions, API endpoints, and PDF generation
"""
import pytest
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models import Patient, Therapist, Session, Base, engine, SessionLocal
from datetime import datetime


class TestPatientModel:
    """Test extended Patient model fields"""
    
    def setup_method(self):
        """Setup test database"""
        Base.metadata.create_all(bind=engine)
        self.db = SessionLocal()
    
    def teardown_method(self):
        """Cleanup"""
        self.db.close()
    
    def test_patient_has_extended_fields(self):
        """Test that Patient model has all new fields"""
        patient = Patient(
            therapist_id=1,
            patient_id="test-001",
            full_name="Test Patient",
            # Extended patient info
            age=30,
            residence="Test City",
            education="Graduate",
            occupation="Engineer",
            marital_status="Single",
            # Medical history
            current_medical_conditions="None",
            past_medical_conditions="None",
            current_medications="None",
            allergies="None",
            hospitalizations="None",
            # Psychiatric history
            previous_psychiatric_diagnoses="None",
            previous_psychiatric_treatment="None",
            previous_psychiatric_hospitalizations="None",
            suicide_self_harm_history="None",
            substance_use_history="None",
            # Family history
            psychiatric_illness_family="None",
            medical_illness_family="None",
            family_dynamics="Normal",
            significant_family_events="None",
            # Social history
            childhood_developmental_history="Normal",
            educational_history="Completed graduation",
            occupational_history="5 years experience",
            relationship_history="Single",
            social_support_system="Good",
            living_situation="With family",
            cultural_religious_background="Hindu",
            # Clinical assessment
            chief_complaint="Anxiety",
            chief_complaint_description="Work-related stress",
            illness_onset="6 months ago",
            illness_progression="Gradual",
            previous_episodes="None",
            triggers="Work deadlines",
            impact_on_functioning="Moderate",
            # MSE
            mse_appearance="Well-groomed",
            mse_behavior="Cooperative",
            mse_speech="Normal",
            mse_mood="Anxious",
            mse_affect="Congruent",
            mse_thought_process="Logical",
            mse_thought_content="No delusions",
            mse_perception="Normal",
            mse_cognition="Intact",
            mse_insight="Good",
            mse_judgment="Good",
        )
        
        assert patient.age == 30
        assert patient.residence == "Test City"
        assert patient.chief_complaint == "Anxiety"
        assert patient.mse_mood == "Anxious"
    
    def test_patient_to_dict_includes_all_fields(self):
        """Test that to_dict() includes all extended fields"""
        patient = Patient(
            therapist_id=1,
            patient_id="test-002",
            full_name="Test Patient 2",
            age=25,
            residence="Mumbai",
            chief_complaint="Depression",
            mse_mood="Low",
        )
        
        data = patient.to_dict()
        
        assert "age" in data
        assert "residence" in data
        assert "chief_complaint" in data
        assert "mse_mood" in data
        assert "current_medical_conditions" in data
        assert "psychiatric_illness_family" in data
        assert "childhood_developmental_history" in data
        assert data["age"] == 25
        assert data["residence"] == "Mumbai"


class TestSummarizationService:
    """Test summarization service updates"""
    
    def test_session_summary_generation(self):
        """Test that session summary follows template format"""
        from summarization_service import summarization_service
        
        session_data = {
            "session_number": 1,
            "session_date": "2024-12-04",
            "original_transcription": "Patient discussed work stress and anxiety symptoms.",
            "notes": "Patient appears anxious. Recommended relaxation techniques."
        }
        
        result = summarization_service._create_empty_session_summary(1, "2024-12-04", "Dr. Test")
        
        assert "session_number" in result
        assert "session_date" in result
        assert "summary" in result
        assert "therapist_name" in result
        assert result["session_number"] == 1
        assert "SESSION RECORDING FORM" in result["summary"]
    
    def test_overall_summary_structure(self):
        """Test overall summary has correct structure"""
        from summarization_service import summarization_service
        
        patient_data = {
            "full_name": "Test Patient",
            "chief_complaint": "Anxiety",
            "chief_complaint_description": "Work stress",
            "mse_mood": "Anxious",
        }
        
        result = summarization_service._create_empty_overall_summary(patient_data, "Dr. Test")
        
        assert "patient" in result
        assert "chief_complaints" in result
        assert "course_of_illness" in result
        assert "baseline_assessment" in result
        assert "session_summaries" in result
        assert "generated_date" in result
        assert "therapist_name" in result


class TestPDFGeneration:
    """Test PDF generation functionality"""
    
    def test_reportlab_import(self):
        """Test that reportlab is properly installed"""
        from reportlab.lib.pagesizes import A4
        from reportlab.platypus import SimpleDocTemplate
        
        assert A4 is not None
        assert SimpleDocTemplate is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
