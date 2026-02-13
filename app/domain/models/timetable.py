"""Timetable entry model for scheduled classes."""

import uuid
import enum
from sqlalchemy import Column, String, Boolean, ForeignKey, Integer, Enum
from sqlalchemy.orm import relationship

from .base import Base, TimestampMixin


class TimetableStatus(str, enum.Enum):
    """Status of a timetable."""
    DRAFT = "Draft"
    PUBLISHED = "Published"
    ARCHIVED = "Archived"


class Timetable(Base, TimestampMixin):
    """Timetable parent entity.
    
    Represents a full generated schedule for a specific session/semester.
    """
    __tablename__ = "timetables"
    
    id = Column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4())
    )
    academic_session = Column(
        String(20),
        nullable=False,
        default="2024/2025", # Default for now
        comment="Academic Session e.g. 2024/2025"
    )
    semester = Column(
        Integer,
        nullable=False,
        comment="Semester 1 or 2"
    )
    status = Column(
        Enum(TimetableStatus),
        default=TimetableStatus.DRAFT,
        nullable=False
    )
    is_active = Column(
        Boolean,
        default=False,
        comment="Whether this is the currently active timetable for the semester"
    )
    
    # Relationships
    entries = relationship("TimetableEntry", back_populates="timetable", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Timetable(session='{self.academic_session}', sem={self.semester}, status='{self.status}')>"


class TimetableEntry(Base, TimestampMixin):
    """Timetable entry entity.
    
    Represents a scheduled class session linking course, timeslot, and venue.
    """
    
    __tablename__ = "timetable_entries"
    
    id = Column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4())
    )
    timetable_id = Column(
        String(36),
        ForeignKey("timetables.id", ondelete="CASCADE"),
        nullable=False,
        comment="Parent timetable"
    )
    course_id = Column(
        String(36),
        ForeignKey("courses.id", ondelete="CASCADE"),
        nullable=False,
        comment="Course being taught"
    )
    timeslot_id = Column(
        String(36),
        ForeignKey("timeslots.id", ondelete="CASCADE"),
        nullable=False,
        comment="Time slot for the class"
    )
    venue_id = Column(
        String(36),
        ForeignKey("venues.id", ondelete="CASCADE"),
        nullable=True,
        comment="Venue where class is held (nullable for unassigned)"
    )
    is_locked = Column(
        Boolean,
        default=False,
        nullable=False,
        comment="Locked entries won't be changed by auto-generation"
    )
    
    # Relationships
    timetable = relationship("Timetable", back_populates="entries")
    course = relationship("Course", back_populates="timetable_entries")
    timeslot = relationship("TimeSlot", back_populates="timetable_entries")
    venue = relationship("Venue", back_populates="timetable_entries")
    
    def __repr__(self) -> str:
        return f"<TimetableEntry(course='{self.course_id}', venue='{self.venue_id}')>"
