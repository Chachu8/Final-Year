"""User authentication and authorization models.

Defines the core user entity with role-based access control.
"""

import enum
import uuid
from datetime import datetime

from sqlalchemy import Column, String, Boolean, Enum, DateTime, Integer
from sqlalchemy.orm import relationship

from .base import Base, TimestampMixin


class UserRole(enum.Enum):
    """Enumeration of user roles in the system.
    
    Defines user types with distinct permissions and access levels.
    """
    ADMIN = "admin"
    DEPT_HEAD = "dept_head"
    LECTURER = "lecturer"


class User(Base, TimestampMixin):
    """Core user authentication entity.
    
    Represents an authenticated user in the system with role-based access.
    
    Attributes:
        id: Unique identifier (UUID string format)
        username: Unique username for login
        email: User's email address (unique)
        password_hash: Bcrypt hashed password
        full_name: User's full name
        role: User's role determining permissions
        is_active: Whether account is active
        last_login_at: Timestamp of most recent login
    """
    
    __tablename__ = "users"
    
    id = Column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
        comment="Unique user identifier (UUID format)"
    )
    username = Column(
        String(50),
        unique=True,
        nullable=False,
        index=True,
        comment="Unique username for login"
    )
    email = Column(
        String(255),
        unique=True,
        nullable=False,
        index=True,
        comment="User email address (unique, case-insensitive)"
    )
    password_hash = Column(
        String(255),
        nullable=False,
        comment="Bcrypt hashed password"
    )
    full_name = Column(
        String(100),
        nullable=False,
        comment="User's full name"
    )
    role = Column(
        Enum(UserRole),
        nullable=False,
        default=UserRole.LECTURER,
        comment="User role determining permissions"
    )
    is_active = Column(
        Boolean,
        default=True,
        nullable=False,
        comment="Account active status"
    )
    last_login_at = Column(
        DateTime,
        nullable=True,
        comment="UTC timestamp of last successful login"
    )
    
    def __repr__(self) -> str:
        return f"<User(username='{self.username}', role='{self.role.value}')>"
