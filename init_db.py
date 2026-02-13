"""Initialize database tables.

This script creates all database tables in PostgreSQL.
Run this before seeding data.
"""

from app.infrastructure.database import init_db
from app.config import get_settings

settings = get_settings()

def main():
    """Initialize database tables."""
    print(f"[DB] Connecting to: {settings.db_url}")
    print("[DB] Creating tables...")
    
    try:
        init_db()
        print("[SUCCESS] All tables created successfully!")
        print("[INFO] Tables created:")
        print("  - users")
        print("  - courses")
        print("  - lecturers")
        print("  - venues")
        print("  - timeslots")
        print("  - timetable_entries")
        print("\n[NEXT] Run 'python seed_db.py' to populate with sample data")
    except Exception as e:
        print(f"[ERROR] Failed to create tables: {e}")
        raise


if __name__ == "__main__":
    main()
