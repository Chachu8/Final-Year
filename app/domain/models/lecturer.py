"""Lecturer model for teaching staff."""

import uuid
from sqlalchemy import Column, String, Integer
from sqlalchemy.orm import relationship

from .base import Base, TimestampMixin


class Lecturer(Base, TimestampMixin):
    """Lecturer/teaching staff entity.
    
    Represents a lecturer who teaches courses.
    
    Attributes:
        id: Unique identifier
        name: Lecturer's full name
        email: Lecturer's email address
        department: Department affiliation
        max_hours_per_day: Maximum teaching hours per day
    """
    
    __tablename__ = "lecturers"
    
    id = Column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4())
    )
    name = Column(
        String(100),
        nullable=False,
        comment="Lecturer's full name"
    )
    email = Column(
        String(255),
        unique=True,
        nullable=False,
        index=True,
        comment="Lecturer's email address"
    )
    department = Column(
        String(100),
        nullable=False,
        comment="Department affiliation"
    )
    max_hours_per_day = Column(
        Integer,
        default=6,
        nullable=False,
        comment="Maximum teaching hours per day"
    )
    
    # Relationships
    courses = relationship("Course", back_populates="lecturer")
    
    def __repr__(self) -> str:
        return f"<Lecturer(name='{self.name}', department='{self.department}')>"
