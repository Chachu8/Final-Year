"""Service for managing lecturers."""

from typing import List, Optional
from sqlalchemy.orm import Session
from app.domain.models.lecturer import Lecturer

class LecturerService:
    @staticmethod
    def get_all(db: Session) -> List[Lecturer]:
        """Retrieve all lecturers."""
        return db.query(Lecturer).all()

    @staticmethod
    def get_by_id(db: Session, lecturer_id: str) -> Optional[Lecturer]:
        """Retrieve a lecturer by ID."""
        return db.query(Lecturer).filter(Lecturer.id == lecturer_id).first()

    @staticmethod
    def create(db: Session, name: str, email: str, department: str, max_hours: int) -> Lecturer:
        """Create a new lecturer."""
        new_lecturer = Lecturer(
            name=name,
            email=email,
            department=department,
            max_hours_per_day=max_hours
        )
        db.add(new_lecturer)
        db.commit()
        db.refresh(new_lecturer)
        return new_lecturer

    @staticmethod
    def get_by_email(db: Session, email: str) -> Optional[Lecturer]:
        """Retrieve a lecturer by email."""
        return db.query(Lecturer).filter(Lecturer.email == email).first()

    @staticmethod
    def update(db: Session, email: str, name: str, department: str, max_hours: int) -> Optional[Lecturer]:
        """Update an existing lecturer."""
        lecturer = db.query(Lecturer).filter(Lecturer.email == email).first()
        if lecturer:
            lecturer.name = name
            lecturer.department = department
            lecturer.max_hours_per_day = max_hours
            db.commit()
            db.refresh(lecturer)
            return lecturer
        return None

    @staticmethod
    def delete(db: Session, lecturer_id: str) -> bool:
        """Delete a lecturer by ID."""
        lecturer = db.query(Lecturer).filter(Lecturer.id == lecturer_id).first()
        if lecturer:
            db.delete(lecturer)
            db.commit()
            return True
        return False
