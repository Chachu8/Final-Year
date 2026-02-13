"""Course model for academic courses."""

import uuid
from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.orm import relationship

from .base import Base, TimestampMixin


class Course(Base, TimestampMixin):
    """Academic course entity.
    
    Represents a course that needs to be scheduled in the timetable.
    
    Attributes:
        id: Unique identifier
        code: Course code (e.g., "CSC301")
        title: Course title
        level: Student level (100, 200, 300, 400)
        credit_hours: Number of credit hours
        lecturer_id: Foreign key to assigned lecturer
        department: Department offering the course
        enrollment: Expected number of students
    """
    
    __tablename__ = "courses"
    
    id = Column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4())
    )
    code = Column(
        String(20),
        unique=True,
        nullable=False,
        index=True,
        comment="Course code (e.g., CSC301)"
    )
    title = Column(
        String(200),
        nullable=False,
        comment="Course title"
    )
    level = Column(
        Integer,
        nullable=False,
        comment="Student level (100, 200, 300, 400)"
    )
    credit_hours = Column(
        Integer,
        nullable=False,
        default=3,
        comment="Number of credit hours"
    )
    lecturer_id = Column(
        String(36),
        ForeignKey("lecturers.id"),
        nullable=True,
        comment="Assigned lecturer ID"
    )
    department = Column(
        String(100),
        nullable=False,
        comment="Department offering the course"
    )
    enrollment = Column(
        Integer,
        nullable=True,
        comment="Expected number of students"
    )
    semester = Column(
        Integer,
        nullable=False,
        default=1,
        comment="Semester (1 or 2)"
    )
    # duration and frequency removed - configured dynamically at generation time
    
    # Relationships
    lecturer = relationship("Lecturer", back_populates="courses")
    timetable_entries = relationship("TimetableEntry", back_populates="course", cascade="all, delete-orphan")
    
    def __repr__(self) -> str:
        return f"<Course(code='{self.code}', title='{self.title}')>"
