"""Domain models package.

Exports all database models for easy importing.
"""

from .base import Base, TimestampMixin
from .user import User, UserRole
from .course import Course
from .lecturer import Lecturer
from .venue import Venue, VenueType
from .timeslot import TimeSlot, DayOfWeek
from .timetable import TimetableEntry, Timetable, TimetableStatus

__all__ = [
    "Base",
    "TimestampMixin",
    "User",
    "UserRole",
    "Course",
    "Lecturer",
    "Venue",
    "VenueType",
    "TimeSlot",
    "DayOfWeek",
    "TimetableEntry",
]
