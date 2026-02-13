"""Authentication Service.

Handles user authentication logic including login, logout, and token management.
"""

from typing import Optional, Dict, Any, Tuple
from sqlalchemy.orm import Session
from datetime import timedelta

from app.domain.models.user import User
from app.infrastructure.security.password import verify_password
from app.infrastructure.security.jwt import create_access_token, verify_token
from app.config import get_settings

settings = get_settings()


class AuthService:
    """Service for handling authentication operations."""
    
    def __init__(self, db: Session):
        self.db = db
        
    def authenticate_user(self, username: str, password: str) -> Optional[User]:
        """Authenticate a user by username and password.
        
        Args:
            username: User's username
            password: User's plain text password
            
        Returns:
            User instance if credentials are valid, None otherwise
        """
        user = self.db.query(User).filter(User.username == username).first()
        if not user:
            return None
        
        # Verify password (assuming hash is stored, mock verify for now if needed)
        # Note: In a real system, verify_password uses bcrypt
        if not verify_password(password, user.password_hash):
            return None
            
        return user
        
    def create_user_tokens(self, user: User) -> Tuple[str, Dict[str, Any]]:
        """Create access token for user.
        
        Args:
            user: Authenticated user instance
            
        Returns:
            Tuple of (access_token, token_payload)
        """
        token_data = {
            "sub": user.id,
            "username": user.username,
            "role": user.role.value,
            "full_name": user.full_name
        }
        
        access_token = create_access_token(
            data=token_data,
            expires_delta=timedelta(hours=settings.jwt_expiration_hours)
        )
        
        return access_token, token_data
    
    @staticmethod
    def get_current_user_from_token(token: str, db: Session) -> Optional[User]:
        """Retrieve user from JWT token.
        
        Args:
            token: JWT token string
            db: Database session
            
        Returns:
            User instance if token is valid and user exists, None otherwise
        """
        payload = verify_token(token)
        if not payload:
            return None
            
        user_id = payload.get("sub")
        if not user_id:
            return None
            
        return db.query(User).filter(User.id == user_id).first()
