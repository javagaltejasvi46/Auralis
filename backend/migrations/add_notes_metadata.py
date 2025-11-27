"""
Database Migration: Add Notes Metadata Columns
Adds AI-generated notes tracking to sessions table
"""
from sqlalchemy import create_engine, Column, Boolean, DateTime, Text
from sqlalchemy.sql import text
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

DATABASE_URL = "sqlite:///./auralis.db"


def migrate_up():
    """Add notes metadata columns"""
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
    
    print("🔄 Running migration: Add notes metadata columns")
    
    with engine.connect() as conn:
        try:
            # Add notes_is_ai_generated column
            conn.execute(text("""
                ALTER TABLE sessions 
                ADD COLUMN notes_is_ai_generated BOOLEAN DEFAULT 0
            """))
            print("✅ Added notes_is_ai_generated column")
            
            # Add notes_edited_from_ai column
            conn.execute(text("""
                ALTER TABLE sessions 
                ADD COLUMN notes_edited_from_ai BOOLEAN DEFAULT 0
            """))
            print("✅ Added notes_edited_from_ai column")
            
            # Add notes_generated_at column
            conn.execute(text("""
                ALTER TABLE sessions 
                ADD COLUMN notes_generated_at DATETIME
            """))
            print("✅ Added notes_generated_at column")
            
            # Add notes_last_edited_at column
            conn.execute(text("""
                ALTER TABLE sessions 
                ADD COLUMN notes_last_edited_at DATETIME
            """))
            print("✅ Added notes_last_edited_at column")
            
            conn.commit()
            print("✅ Migration completed successfully")
            
        except Exception as e:
            print(f"❌ Migration failed: {e}")
            conn.rollback()
            raise


def migrate_down():
    """Remove notes metadata columns (rollback)"""
    print("⚠️  SQLite does not support DROP COLUMN")
    print("⚠️  To rollback, restore database from backup")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "down":
        migrate_down()
    else:
        migrate_up()
