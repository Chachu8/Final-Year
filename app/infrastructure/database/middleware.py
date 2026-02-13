"""Database middleware for FastHTML request handling.

Provides database session management via middleware.
"""

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

from .connection import SessionLocal


class DBSessionMiddleware(BaseHTTPMiddleware):
    """Middleware to provide database session for each request.
    
    Automatically creates a database session for each request and
    attaches it to request.state.db. Session is committed on success
    and rolled back on error.
    """
    
    async def dispatch(self, request: Request, call_next):
        """Process request with database session."""
        db = SessionLocal()
        request.state.db = db
        
        try:
            response = await call_next(request)
            db.commit()
            return response
        except Exception:
            db.rollback()
            raise
        finally:
            db.close()
