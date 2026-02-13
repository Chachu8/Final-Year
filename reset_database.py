"""Interactive database reset utility.

This script provides selective table reset functionality with safety prompts.
Use with caution - this performs destructive operations!

Usage:
    python reset_database.py
"""

from app.infrastructure.database import get_db, init_db
from app.infrastructure.database.connection import engine
from app.domain.models.base import Base
from app.domain.models import (
    User, Course, Lecturer, Venue, TimeSlot, Timetable, TimetableEntry
)
from sqlalchemy import MetaData


def print_menu():
    """Display the reset menu."""
    print("\n" + "="*60)
    print("  DATABASE RESET UTILITY")
    print("="*60)
    print("\n[WARNING] This tool performs DESTRUCTIVE operations!")
    print("          All data in selected tables will be PERMANENTLY DELETED.\n")
    print("Select reset option:")
    print("  1. Reset ALL tables (complete database wipe)")
    print("  2. Reset Timetables only (preserve courses, lecturers, venues)")
    print("  3. Reset Courses only")
    print("  4. Reset Lecturers only")
    print("  5. Reset Venues only")
    print("  6. Reset TimeSlots only")
    print("  7. Reset Users only")
    print("  8. Custom selection (choose multiple tables)")
    print("  0. Exit (cancel)")
    print("="*60)


def confirm_action(message):
    """Prompt user for confirmation."""
    response = input(f"\n{message} (yes/no): ").strip().lower()
    return response in ['yes', 'y']


def reset_all_tables():
    """Drop and recreate all tables."""
    print("\n[*] Resetting ALL tables...")
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    print("[SUCCESS] All tables reset successfully!")


def reset_specific_tables(table_models):
    """Reset specific tables by deleting all rows."""
    print(f"\n[*] Resetting {len(table_models)} table(s)...")
    
    with get_db() as db:
        for model in table_models:
            table_name = model.__tablename__
            print(f"  [-] Clearing {table_name}...")
            db.query(model).delete()
        
        db.commit()
    
    print("[SUCCESS] Selected tables reset successfully!")


def get_custom_selection():
    """Allow user to select multiple tables."""
    tables = {
        '1': ('Users', User),
        '2': ('Courses', Course),
        '3': ('Lecturers', Lecturer),
        '4': ('Venues', Venue),
        '5': ('TimeSlots', TimeSlot),
        '6': ('Timetables', Timetable),
        '7': ('TimetableEntries', TimetableEntry),
    }
    
    print("\nSelect tables to reset (comma-separated, e.g., 1,2,3):")
    for key, (name, _) in tables.items():
        print(f"  {key}. {name}")
    
    selection = input("\nYour selection: ").strip()
    
    selected_models = []
    for num in selection.split(','):
        num = num.strip()
        if num in tables:
            name, model = tables[num]
            selected_models.append(model)
            print(f"  [+] Selected: {name}")
    
    return selected_models


def main():
    """Main interactive menu."""
    # Initialize database connection
    init_db()
    
    while True:
        print_menu()
        choice = input("\nEnter your choice: ").strip()
        
        if choice == '0':
            print("\n[*] Exiting without changes.")
            break
        
        elif choice == '1':
            # Reset all tables
            if confirm_action("⚠️  Reset ALL tables? This will delete EVERYTHING!"):
                reset_all_tables()
                break
            else:
                print("[*] Cancelled.")
        
        elif choice == '2':
            # Reset timetables only
            if confirm_action("Reset Timetables and TimetableEntries?"):
                reset_specific_tables([Timetable, TimetableEntry])
                break
            else:
                print("[*] Cancelled.")
        
        elif choice == '3':
            # Reset courses
            if confirm_action("Reset Courses? (This may affect timetables)"):
                reset_specific_tables([Course])
                break
            else:
                print("[*] Cancelled.")
        
        elif choice == '4':
            # Reset lecturers
            if confirm_action("Reset Lecturers? (This may affect courses)"):
                reset_specific_tables([Lecturer])
                break
            else:
                print("[*] Cancelled.")
        
        elif choice == '5':
            # Reset venues
            if confirm_action("Reset Venues? (This may affect timetables)"):
                reset_specific_tables([Venue])
                break
            else:
                print("[*] Cancelled.")
        
        elif choice == '6':
            # Reset timeslots
            if confirm_action("Reset TimeSlots? (This may affect timetables)"):
                reset_specific_tables([TimeSlot])
                break
            else:
                print("[*] Cancelled.")
        
        elif choice == '7':
            # Reset users
            if confirm_action("Reset Users? (You'll need to re-seed users to login)"):
                reset_specific_tables([User])
                break
            else:
                print("[*] Cancelled.")
        
        elif choice == '8':
            # Custom selection
            selected = get_custom_selection()
            if selected:
                table_names = ', '.join([m.__tablename__ for m in selected])
                if confirm_action(f"Reset these tables: {table_names}?"):
                    reset_specific_tables(selected)
                    break
                else:
                    print("[*] Cancelled.")
            else:
                print("[ERROR] No valid tables selected.")
        
        else:
            print("[ERROR] Invalid choice. Please try again.")
    
    print("\n[*] Done.\n")


if __name__ == "__main__":
    main()
