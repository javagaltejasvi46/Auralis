"""
Populate database with fake Indian customer data
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, Therapist, Patient, Session
from datetime import datetime, timedelta
import random

# Database setup
DATABASE_URL = "sqlite:///./auralis.db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def create_fake_data():
    # Create tables
    Base.metadata.create_all(bind=engine)
    print("✅ Database tables created")
    
    db = SessionLocal()
    
    try:
        # Check if therapist exists
        therapist = db.query(Therapist).filter(Therapist.username == "tejasvijavagal").first()
        
        if not therapist:
            # Create therapist
            therapist = Therapist(
                username="tejasvijavagal",
                email="tejasvij@auralis.com",
                full_name="Tejasvij Javagal",
                license_number="9865073549863",
                specialization="Clinical Psychology",
                phone="+91-9876543210",
                is_active=True
            )
            therapist.hashed_password = Therapist.hash_password("password123")
            db.add(therapist)
            db.commit()
            db.refresh(therapist)
            print(f"✅ Created therapist: {therapist.full_name}")
        else:
            print(f"✅ Using existing therapist: {therapist.full_name}")
        
        # Indian names and details
        indian_patients = [
            {
                "name": "Arjun Sharma", "phone": "+91-9876543211", "email": "arjun.sharma@email.com",
                "address": "MG Road, Bangalore, Karnataka 560001", "gender": "Male",
                "occupation": "Software Engineer", "education": "B.Tech Computer Science"
            },
            {
                "name": "Priya Patel", "phone": "+91-9876543212", "email": "priya.patel@email.com", 
                "address": "Andheri West, Mumbai, Maharashtra 400058", "gender": "Female",
                "occupation": "Marketing Manager", "education": "MBA Marketing"
            },
            {
                "name": "Rajesh Kumar", "phone": "+91-9876543213", "email": "rajesh.kumar@email.com",
                "address": "Connaught Place, New Delhi 110001", "gender": "Male", 
                "occupation": "Business Analyst", "education": "M.Com"
            },
            {
                "name": "Sneha Reddy", "phone": "+91-9876543214", "email": "sneha.reddy@email.com",
                "address": "Banjara Hills, Hyderabad, Telangana 500034", "gender": "Female",
                "occupation": "Doctor", "education": "MBBS"
            },
            {
                "name": "Vikram Singh", "phone": "+91-9876543215", "email": "vikram.singh@email.com",
                "address": "Civil Lines, Jaipur, Rajasthan 302006", "gender": "Male",
                "occupation": "Teacher", "education": "M.Ed"
            },
            {
                "name": "Kavya Nair", "phone": "+91-9876543216", "email": "kavya.nair@email.com",
                "address": "Marine Drive, Kochi, Kerala 682031", "gender": "Female",
                "occupation": "Graphic Designer", "education": "B.Des"
            },
            {
                "name": "Aditya Gupta", "phone": "+91-9876543217", "email": "aditya.gupta@email.com",
                "address": "Park Street, Kolkata, West Bengal 700016", "gender": "Male",
                "occupation": "Financial Advisor", "education": "CA"
            },
            {
                "name": "Meera Iyer", "phone": "+91-9876543218", "email": "meera.iyer@email.com",
                "address": "T. Nagar, Chennai, Tamil Nadu 600017", "gender": "Female",
                "occupation": "HR Manager", "education": "MBA HR"
            },
            {
                "name": "Rohit Joshi", "phone": "+91-9876543219", "email": "rohit.joshi@email.com",
                "address": "FC Road, Pune, Maharashtra 411005", "gender": "Male",
                "occupation": "Data Scientist", "education": "M.Tech AI/ML"
            },
            {
                "name": "Ananya Menon", "phone": "+91-9876543220", "email": "ananya.menon@email.com",
                "address": "Koramangala, Bangalore, Karnataka 560034", "gender": "Female",
                "occupation": "Product Manager", "education": "B.Tech + MBA"
            }
        ]
        
        # Sample therapy session transcripts
        session_transcripts = [
            {
                "transcript": "Therapist: How are you feeling today?\nPatient: I've been feeling quite anxious lately. Work has been very stressful.\nTherapist: Can you tell me more about what's causing the stress at work?\nPatient: My manager has been very demanding and I feel like I can't meet the expectations.\nTherapist: That sounds challenging. How are you coping with these feelings?",
                "notes": "Patient reports work-related anxiety. Discussed coping strategies and stress management techniques."
            },
            {
                "transcript": "Therapist: Good morning. How has your week been?\nPatient: Better than last week. I tried the breathing exercises you suggested.\nTherapist: That's great to hear. Did you find them helpful?\nPatient: Yes, especially during stressful moments at work. I felt more in control.\nTherapist: Excellent progress. Let's continue building on these techniques.",
                "notes": "Patient showing improvement with breathing exercises. Positive response to stress management techniques."
            },
            {
                "transcript": "Therapist: I notice you seem more relaxed today. How are things going?\nPatient: Much better. I had a conversation with my manager about workload.\nTherapist: How did that go?\nPatient: Surprisingly well. We worked out a more manageable schedule.\nTherapist: That's wonderful. How do you feel about advocating for yourself?",
                "notes": "Significant improvement. Patient successfully communicated with manager. Building confidence in self-advocacy."
            }
        ]
        
        # Create patients and sessions
        for i, patient_data in enumerate(indian_patients):
            # Create patient
            patient = Patient(
                therapist_id=therapist.id,
                patient_id=f"PAT{1000 + i}",
                full_name=patient_data["name"],
                phone=patient_data["phone"],
                email=patient_data["email"],
                address=patient_data["address"],
                gender=patient_data["gender"],
                age=random.randint(25, 55),
                occupation=patient_data["occupation"],
                education=patient_data["education"],
                date_of_birth=datetime.now() - timedelta(days=random.randint(9000, 18000)),
                emergency_contact=f"Emergency contact for {patient_data['name']}",
                medical_history="No significant medical history",
                notes=f"Initial assessment completed for {patient_data['name']}",
                is_active=True,
                created_at=datetime.now() - timedelta(days=random.randint(30, 90))
            )
            
            db.add(patient)
            db.commit()
            db.refresh(patient)
            
            print(f"✅ Created patient: {patient.full_name} (ID: {patient.patient_id})")
            
            # Create 3 sessions for each patient
            for j in range(3):
                session_data = session_transcripts[j]
                session_date = datetime.now() - timedelta(days=random.randint(1, 30))
                
                session = Session(
                    patient_id=patient.id,
                    session_number=j + 1,
                    session_date=session_date,
                    duration=random.randint(2700, 3600),  # 45-60 minutes in seconds
                    original_transcription=session_data["transcript"],
                    notes=session_data["notes"],
                    language="english",
                    is_completed=True
                )
                
                db.add(session)
                
            db.commit()
            print(f"  ✅ Created 3 sessions for {patient.full_name}")
        
        print(f"\n🎉 Successfully created:")
        print(f"   - 1 Therapist: {therapist.full_name}")
        print(f"   - 10 Patients with Indian names and details")
        print(f"   - 30 Therapy sessions (3 per patient)")
        print(f"\n🔑 Login credentials:")
        print(f"   Username: tejasvijavagal")
        print(f"   Password: password123")
        
    except Exception as e:
        print(f"❌ Error creating fake data: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    create_fake_data()