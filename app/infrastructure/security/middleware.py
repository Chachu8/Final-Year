"""Authentication middleware.

Handles request authentication and user session population.
"""

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import RedirectResponse
from app.domain.services.auth import AuthService


class AuthMiddleware(BaseHTTPMiddleware):
    """Middleware to check authentication status and populate user."""
    
    async def dispatch(self, request: Request, call_next):
        # Skip auth check for public routes and static files
        public_paths = ["/", "/login", "/health", "/favicon.ico"]
        if (request.url.path in public_paths or 
            request.url.path.startswith(("/static", "/assets", "/student", "/timetable/export-pdf"))):
            return await call_next(request)
            
        token = request.cookies.get("access_token")
        if not token:
            # Redirect to login if accessing protected route
            return RedirectResponse(url="/login", status_code=303)
            
        # We need the DB session to get the user
        # Note: Usually DB middleware runs before this, so request.state.db should exist
        db = getattr(request.state, "db", None)
        
        if db:
            user = AuthService.get_current_user_from_token(token, db)
            if user:
                request.state.user = user
                return await call_next(request)
        
        # If token invalid or user not found
        return RedirectResponse(url="/login", status_code=303)
