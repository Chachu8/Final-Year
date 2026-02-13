"""Test PostgreSQL connection.

This script tests the database connection and prints diagnostic information.
"""

import sys
from sqlalchemy import create_engine, text
from app.config import get_settings

settings = get_settings()

def test_connection():
    """Test database connection."""
    print(f"[INFO] Environment: {settings.environment}")
    print(f"[INFO] Database URL: {settings.db_url}")
    print(f"[INFO] Attempting connection...")
    
    try:
        # Create engine
        engine = create_engine(settings.db_url, echo=True)
        
        # Test connection
        with engine.connect() as conn:
            result = conn.execute(text("SELECT version()"))
            version = result.fetchone()[0]
            print(f"\n[SUCCESS] Connected to PostgreSQL!")
            print(f"[INFO] PostgreSQL version: {version}")
            
            # Check if tables exist
            result = conn.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
                ORDER BY table_name
            """))
            tables = [row[0] for row in result.fetchall()]
            
            if tables:
                print(f"\n[INFO] Existing tables ({len(tables)}):")
                for table in tables:
                    print(f"  - {table}")
            else:
                print("\n[INFO] No tables found. Run 'python init_db.py' to create them.")
                
        return True
        
    except Exception as e:
        print(f"\n[ERROR] Connection failed!")
        print(f"[ERROR] {type(e).__name__}: {e}")
        print("\n[DEBUG] Troubleshooting:")
        print("  1. Check PostgreSQL is running: pg_ctl status")
        print("  2. Verify database exists: psql -l")
        print("  3. Test credentials: psql -U postgres -d timetable_db")
        print("  4. Check .env file has correct DATABASE_URL")
        return False


if __name__ == "__main__":
    success = test_connection()
    sys.exit(0 if success else 1)
