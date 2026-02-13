"""Consolidated database seeding script.

Usage:
    python seed_database.py --mode simple    # Basic test data
    python seed_database.py --mode realistic # Full multi-department data
"""

import argparse
import random
from datetime import time
from app.infrastructure.database import get_db, init_db
from app.domain.models import (
    User, UserRole,
    Course,
    Lecturer,
    Venue, VenueType,
    TimeSlot, DayOfWeek
)
from app.infrastructure.security import hash_password


def seed_users_simple():
    """Create basic test users."""
    return [
        User(
            username="admin",
            email="admin@university.edu",
            password_hash=hash_password("admin123"),
            full_name="System Administrator",
            role=UserRole.ADMIN,
            is_active=True
        ),
        User(
            username="depthead",
            email="depthead@university.edu",
            password_hash=hash_password("dept123"),
            full_name="Dr. Department Head",
            role=UserRole.DEPT_HEAD,
            is_active=True
        ),
    ]


def seed_users_realistic():
    """Create admin and department head users."""
    return [
        User(
            username="admin",
            email="admin@unilorin.edu.ng",
            password_hash=hash_password("admin123"),
            full_name="System Administrator",
            role=UserRole.ADMIN,
            is_active=True
        ),
        User(
            username="dean",
            email="dean@unilorin.edu.ng",
            password_hash=hash_password("dean123"),
            full_name="Dean of Faculty",
            role=UserRole.DEPT_HEAD,
            is_active=True
        ),
    ]


def seed_lecturers_simple():
    """Create sample lecturers for testing."""
    return [
        Lecturer(
            name="Dr. Alice Johnson",
            email="alice.johnson@university.edu",
            department="Computer Science",
            max_hours_per_day=6
        ),
        Lecturer(
            name="Prof. Bob Williams",
            email="bob.williams@university.edu",
            department="Computer Science",
            max_hours_per_day=5
        ),
        Lecturer(
            name="Dr. Carol Brown",
            email="carol.brown@university.edu",
            department="Computer Science",
            max_hours_per_day=6
        ),
        Lecturer(
            name="Dr. David Miller",
            email="david.miller@university.edu",
            department="Mathematics",
            max_hours_per_day=6
        ),
    ]


def seed_lecturers_realistic(departments):
    """Create lecturers for each department (~5 per department)."""
    lecturers = []
    first_names = ["John", "Jane", "Alice", "Bob", "Charlie", "David", "Eve", "Frank", "Grace", "Hank"]
    last_names = ["Smith", "Doe", "Johnson", "Williams", "Brown", "Jones", "Miller", "Davis", "Garcia", "Rodriguez"]
    
    for dept in departments:
        for _ in range(5):
            first = random.choice(first_names)
            last = random.choice(last_names)
            name = f"Dr. {first} {last}"
            lecturers.append(Lecturer(
                name=name,
                email=f"{last.lower()}{random.randint(1,99)}@unilorin.edu.ng",
                department=dept,
                max_hours_per_day=6
            ))
    
    return lecturers


def seed_venues_simple():
    """Create sample venues for testing."""
    return [
        Venue(name="LT1", capacity=200, type=VenueType.LECTURE_HALL),
        Venue(name="LT2", capacity=150, type=VenueType.LECTURE_HALL),
        Venue(name="Lab A", capacity=40, type=VenueType.LAB),
        Venue(name="Lab B", capacity=40, type=VenueType.LAB),
        Venue(name="Room 101", capacity=50, type=VenueType.CLASSROOM),
        Venue(name="Room 102", capacity=50, type=VenueType.CLASSROOM),
        Venue(name="Room 201", capacity=60, type=VenueType.CLASSROOM),
    ]


def seed_venues_realistic():
    """Create realistic venues - 6 lecture halls only."""
    venues = []
    
    # 1 Large Lecture Theater
    venues.append(Venue(name="LT", capacity=300, type=VenueType.LECTURE_HALL))
    
    # 5 Lecture Rooms
    for i in range(1, 6):
        venues.append(Venue(name=f"LR {i}", capacity=150, type=VenueType.CLASSROOM))
    
    return venues


def seed_timeslots():
    """Create timeslots (Monday-Friday, 8AM-6PM, 1-hour slots)."""
    timeslots = []
    days = [DayOfWeek.MONDAY, DayOfWeek.TUESDAY, DayOfWeek.WEDNESDAY, 
            DayOfWeek.THURSDAY, DayOfWeek.FRIDAY]
    
    for day in days:
        for hour in range(8, 18):  # 8:00 to 17:00
            timeslots.append(
                TimeSlot(
                    day=day,
                    start_time=time(hour, 0),
                    end_time=time(hour + 1, 0)
                )
            )
    
    return timeslots


def seed_courses_simple(lecturers):
    """Create sample courses for testing."""
    return [
        # 100 Level
        Course(
            code="CSC101",
            title="Introduction to Computer Science",
            level=100,
            credit_hours=3,
            lecturer_id=lecturers[0].id,
            department="Computer Science",
            enrollment=120,
            semester=1
        ),
        Course(
            code="MTH101",
            title="General Mathematics I",
            level=100,
            credit_hours=3,
            lecturer_id=lecturers[3].id,
            department="Mathematics",
            enrollment=150,
            semester=1
        ),
        # 200 Level
        Course(
            code="CSC201",
            title="Data Structures and Algorithms",
            level=200,
            credit_hours=4,
            lecturer_id=lecturers[1].id,
            department="Computer Science",
            enrollment=80,
            semester=1
        ),
        Course(
            code="CSC202",
            title="Object-Oriented Programming",
            level=200,
            credit_hours=3,
            lecturer_id=lecturers[0].id,
            department="Computer Science",
            enrollment=75,
            semester=2
        ),
        # 300 Level
        Course(
            code="CSC301",
            title="Database Management Systems",
            level=300,
            credit_hours=4,
            lecturer_id=lecturers[2].id,
            department="Computer Science",
            enrollment=60,
            semester=1
        ),
        Course(
            code="CSC302",
            title="Operating Systems",
            level=300,
            credit_hours=3,
            lecturer_id=lecturers[1].id,
            department="Computer Science",
            enrollment=55,
            semester=2
        ),
        # 400 Level
        Course(
            code="CSC401",
            title="Artificial Intelligence",
            level=400,
            credit_hours=4,
            lecturer_id=lecturers[2].id,
            department="Computer Science",
            enrollment=40,
            semester=1
        ),
        Course(
            code="CSC402",
            title="Software Engineering",
            level=400,
            credit_hours=3,
            lecturer_id=lecturers[0].id,
            department="Computer Science",
            enrollment=45,
            semester=2
        ),
    ]


def seed_courses_realistic(lecturers, departments):
    """Generate ~150 courses for 5 departments."""
    dept_codes = {
        "Computer Science": "CSC",
        "Library Info Sci": "LIS",
        "Mass Comm": "MAC",
        "Info Tech": "IFT",
        "Telecom Sci": "TCS"
    }
    
    levels = [100, 200, 300, 400]
    courses = []
    
    for dept_name, code_prefix in dept_codes.items():
        dept_lecturers = [l for l in lecturers if l.department == dept_name]
        
        for level in levels:
            # Create 7-8 courses per department per level
            num_courses = random.randint(7, 8)
            
            for i in range(1, num_courses + 1):
                course_code = f"{code_prefix}{level}{i:02d}"
                semester = random.choice([1, 2])
                enrollment = 150 if level == 100 else 100 if level == 200 else 60
                
                course = Course(
                    code=course_code,
                    title=f"Intro to {dept_name} {level}-{i}" if level == 100 else f"Advanced {dept_name} {level}-{i}",
                    level=level,
                    credit_hours=3,
                    lecturer_id=random.choice(dept_lecturers).id if dept_lecturers else None,
                    department=dept_name,
                    enrollment=enrollment,
                    semester=semester
                )
                courses.append(course)
    
    return courses


def seed_simple(db):
    """Seed database with simple test data."""
    print("\n[*] Seeding database with SIMPLE test data...")
    
    # Check if data exists
    existing_users = db.query(User).count()
    if existing_users > 0:
        print("[WARN] Database already contains data. Skipping seed.")
        print("       Use reset_database.py to clear existing data first.")
        return
    
    # Seed users
    print("[+] Creating users...")
    users = seed_users_simple()
    db.add_all(users)
    db.flush()
    
    # Seed lecturers
    print("[+] Creating lecturers...")
    lecturers = seed_lecturers_simple()
    db.add_all(lecturers)
    db.flush()
    
    # Seed venues
    print("[+] Creating venues...")
    venues = seed_venues_simple()
    db.add_all(venues)
    db.flush()
    
    # Seed timeslots
    print("[+] Creating timeslots...")
    timeslots = seed_timeslots()
    db.add_all(timeslots)
    db.flush()
    
    # Seed courses
    print("[+] Creating courses...")
    courses = seed_courses_simple(lecturers)
    db.add_all(courses)
    db.flush()
    
    print("\n[SUCCESS] Database seeded successfully!")
    print(f"  - {len(users)} users")
    print(f"  - {len(lecturers)} lecturers")
    print(f"  - {len(venues)} venues")
    print(f"  - {len(timeslots)} timeslots")
    print(f"  - {len(courses)} courses")
    
    print("\n[INFO] Login credentials:")
    print("  Admin: admin / admin123")
    print("  Dept Head: depthead / dept123")


def seed_realistic(db):
    """Seed database with realistic multi-department data."""
    print("\n[*] Seeding database with REALISTIC data...")
    
    # Check if data exists
    existing_users = db.query(User).count()
    if existing_users > 0:
        print("[WARN] Database already contains data. Skipping seed.")
        print("       Use reset_database.py to clear existing data first.")
        return
    
    departments = ["Computer Science", "Library Info Sci", "Mass Comm", "Info Tech", "Telecom Sci"]
    
    # Seed users
    print("[+] Creating users...")
    users = seed_users_realistic()
    db.add_all(users)
    db.flush()
    
    # Seed lecturers
    print("[+] Creating lecturers...")
    lecturers = seed_lecturers_realistic(departments)
    db.add_all(lecturers)
    db.flush()
    
    # Seed venues
    print("[+] Creating venues...")
    venues = seed_venues_realistic()
    db.add_all(venues)
    db.flush()
    
    # Seed timeslots
    print("[+] Creating timeslots...")
    timeslots = seed_timeslots()
    db.add_all(timeslots)
    db.flush()
    
    # Seed courses
    print("[+] Creating courses...")
    courses = seed_courses_realistic(lecturers, departments)
    db.add_all(courses)
    db.flush()
    
    print("\n[SUCCESS] Database seeded successfully!")
    print(f"  - {len(users)} users")
    print(f"  - {len(lecturers)} lecturers ({len(departments)} departments)")
    print(f"  - {len(venues)} venues")
    print(f"  - {len(timeslots)} timeslots")
    print(f"  - {len(courses)} courses")
    
    print("\n[INFO] Login credentials:")
    print("  Admin: admin / admin123")
    print("  Dean: dean / dean123")


def main():
    """Main function to seed the database."""
    parser = argparse.ArgumentParser(description="Seed the timetable database")
    parser.add_argument(
        "--mode",
        choices=["simple", "realistic"],
        default="simple",
        help="Seeding mode: simple (test data) or realistic (full dataset)"
    )
    
    args = parser.parse_args()
    
    # Initialize database
    init_db()
    
    with get_db() as db:
        if args.mode == "simple":
            seed_simple(db)
        else:
            seed_realistic(db)


if __name__ == "__main__":
    main()
