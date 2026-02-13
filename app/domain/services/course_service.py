"""Service for managing courses."""

from typing import List, Optional
from sqlalchemy.orm import Session
from app.domain.models.course import Course

class CourseService:
    @staticmethod
    def get_all(db: Session) -> List[Course]:
        """Retrieve all courses."""
        return db.query(Course).all()

    @staticmethod
    def get_by_id(db: Session, course_id: str) -> Optional[Course]:
        """Retrieve a course by ID."""
        return db.query(Course).filter(Course.id == course_id).first()

    @staticmethod
    def create(db: Session, code: str, title: str, credits: int, level: int, department: str, lecturer_id: Optional[str] = None) -> Course:
        """Create a new course."""
        new_course = Course(
            code=code,
            title=title,
            credit_hours=credits,
            level=level,
            department=department,
            lecturer_id=lecturer_id if lecturer_id else None
        )
        db.add(new_course)
        db.commit()
        db.refresh(new_course)
        return new_course

    @staticmethod
    def get_by_code(db: Session, code: str) -> Optional[Course]:
        """Retrieve a course by its code."""
        return db.query(Course).filter(Course.code == code).first()

    @staticmethod
    def update(db: Session, code: str, title: str, credits: int, level: int, department: str, lecturer_id: Optional[str] = None) -> Optional[Course]:
        """Update an existing course."""
        course = db.query(Course).filter(Course.code == code).first()
        if course:
            course.title = title
            course.credit_hours = credits
            course.level = level
            course.department = department
            course.lecturer_id = lecturer_id if lecturer_id else None
            db.commit()
            db.refresh(course)
            return course
        return None

    @staticmethod
    def delete(db: Session, course_id: str) -> bool:
        """Delete a course by ID."""
        course = db.query(Course).filter(Course.id == course_id).first()
        if course:
            db.delete(course)
            db.commit()
            return True
        return False
