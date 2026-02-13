"""Venue model for classrooms and lecture halls."""

import uuid
import enum
from sqlalchemy import Column, String, Integer, Enum
from sqlalchemy.orm import relationship

from .base import Base, TimestampMixin


class VenueType(enum.Enum):
    """Enumeration of venue types."""
    LECTURE_HALL = "lecture_hall"
    LAB = "lab"
    CLASSROOM = "classroom"


class Venue(Base, TimestampMixin):
    """Venue/room entity for classes.
    
    Represents a physical location where classes can be held.
    
    Attributes:
        id: Unique identifier
        name: Venue name (e.g., "LT1", "Lab A")
        capacity: Maximum number of students
        type: Type of venue (lecture hall, lab, classroom)
    """
    
    __tablename__ = "venues"
    
    id = Column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4())
    )
    name = Column(
        String(100),
        unique=True,
        nullable=False,
        index=True,
        comment="Venue name (e.g., LT1, Lab A)"
    )
    capacity = Column(
        Integer,
        nullable=False,
        comment="Maximum number of students"
    )
    type = Column(
        Enum(VenueType),
        nullable=False,
        default=VenueType.CLASSROOM,
        comment="Type of venue"
    )
    
    # Relationships
    timetable_entries = relationship("TimetableEntry", back_populates="venue")
    
    def __repr__(self) -> str:
        return f"<Venue(name='{self.name}', capacity={self.capacity})>"
