"""
Database Migration: Add Extended Patient Fields
Adds comprehensive psychotherapy report fields to patients table
"""
from sqlalchemy import create_engine
from sqlalchemy.sql import text
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

DATABASE_URL = "sqlite:///./auralis.db"


def migrate_up():
    """Add extended patient fields for psychotherapy report"""
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
    
    print("🔄 Running migration: Add extended patient fields")
    
    # Define all new columns to add
    new_columns = [
        # Patient Information (Extended)
        ("age", "INTEGER"),
        ("residence", "TEXT"),
        ("education", "VARCHAR"),
        ("occupation", "VARCHAR"),
        ("marital_status", "VARCHAR"),
        ("date_of_assessment", "DATETIME"),
        
        # Medical History (Detailed)
        ("current_medical_conditions", "TEXT"),
        ("past_medical_conditions", "TEXT"),
        ("current_medications", "TEXT"),
        ("allergies", "TEXT"),
        ("hospitalizations", "TEXT"),
        
        # Psychiatric History
        ("previous_psychiatric_diagnoses", "TEXT"),
        ("previous_psychiatric_treatment", "TEXT"),
        ("previous_psychiatric_hospitalizations", "TEXT"),
        ("suicide_self_harm_history", "TEXT"),
        ("substance_use_history", "TEXT"),
        
        # Family History
        ("psychiatric_illness_family", "TEXT"),
        ("medical_illness_family", "TEXT"),
        ("family_dynamics", "TEXT"),
        ("significant_family_events", "TEXT"),
        
        # Social History
        ("childhood_developmental_history", "TEXT"),
        ("educational_history", "TEXT"),
        ("occupational_history", "TEXT"),
        ("relationship_history", "TEXT"),
        ("social_support_system", "TEXT"),
        ("living_situation", "TEXT"),
        ("cultural_religious_background", "TEXT"),
        
        # Clinical Assessment - Chief Complaints
        ("chief_complaint", "TEXT"),
        ("chief_complaint_description", "TEXT"),
        
        # Course of Illness
        ("illness_onset", "TEXT"),
        ("illness_progression", "TEXT"),
        ("previous_episodes", "TEXT"),
        ("triggers", "TEXT"),
        ("impact_on_functioning", "TEXT"),
        
        # Mental Status Examination
        ("mse_appearance", "TEXT"),
        ("mse_behavior", "TEXT"),
        ("mse_speech", "TEXT"),
        ("mse_mood", "TEXT"),
        ("mse_affect", "TEXT"),
        ("mse_thought_process", "TEXT"),
        ("mse_thought_content", "TEXT"),
        ("mse_perception", "TEXT"),
        ("mse_cognition", "TEXT"),
        ("mse_insight", "TEXT"),
        ("mse_judgment", "TEXT"),
    ]
    
    with engine.connect() as conn:
        success_count = 0
        skip_count = 0
        
        for column_name, column_type in new_columns:
            try:
                conn.execute(text(f"""
                    ALTER TABLE patients 
                    ADD COLUMN {column_name} {column_type}
                """))
                conn.commit()
                print(f"✅ Added {column_name} column")
                success_count += 1
            except Exception as e:
                if "duplicate column name" in str(e).lower():
                    print(f"⏭️  Column {column_name} already exists, skipping")
                    skip_count += 1
                else:
                    print(f"❌ Failed to add {column_name}: {e}")
        
        print(f"\n✅ Migration completed: {success_count} columns added, {skip_count} skipped")


def migrate_down():
    """Remove extended patient fields (rollback)"""
    print("⚠️  SQLite does not support DROP COLUMN")
    print("⚠️  To rollback, restore database from backup")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "down":
        migrate_down()
    else:
        migrate_up()
