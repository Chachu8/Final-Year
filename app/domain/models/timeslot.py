"""TimeSlot model for scheduling periods."""

import uuid
import enum
from datetime import time
from sqlalchemy import Column, String, Enum, Time
from sqlalchemy.orm import relationship

from .base import Base, TimestampMixin


class DayOfWeek(enum.Enum):
    """Enumeration of days of the week."""
    MONDAY = "Monday"
    TUESDAY = "Tuesday"
    WEDNESDAY = "Wednesday"
    THURSDAY = "Thursday"
    FRIDAY = "Friday"


class TimeSlot(Base, TimestampMixin):
    """Time slot entity for scheduling.
    
    Represents a specific time period on a specific day.
    
    Attributes:
        id: Unique identifier
        day: Day of the week
        start_time: Start time of the slot
        end_time: End time of the slot
    """
    
    __tablename__ = "timeslots"
    
    id = Column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4())
    )
    day = Column(
        Enum(DayOfWeek),
        nullable=False,
        comment="Day of the week"
    )
    start_time = Column(
        Time,
        nullable=False,
        comment="Start time of the slot"
    )
    end_time = Column(
        Time,
        nullable=False,
        comment="End time of the slot"
    )
    
    # Relationships
    timetable_entries = relationship("TimetableEntry", back_populates="timeslot")
    
    def __repr__(self) -> str:
        return f"<TimeSlot({self.day.value} {self.start_time}-{self.end_time})>"
