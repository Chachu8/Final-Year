"""Base models and mixins for SQLAlchemy entities.

This module provides the foundational classes for all database models,
including timestamp tracking and base configuration.
"""

from datetime import datetime

from sqlalchemy import Column, DateTime
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy models.
    
    Provides common configuration and type hints for all database entities.
    All models should inherit from this class.
    """
    pass


class TimestampMixin:
    """Mixin to add created_at and updated_at timestamps to models.
    
    Automatically tracks when records are created and last modified.
    Both timestamps are stored in UTC to ensure consistency across timezones.
    """
    
    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
        comment="UTC timestamp when record was created"
    )
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=True,
        comment="UTC timestamp when record was last updated"
    )
