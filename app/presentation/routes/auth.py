"""Authentication routes.

Handles login, logout, and protected route access.
"""

from fasthtml.common import *
from starlette.requests import Request
from starlette.responses import RedirectResponse

from app.domain.services.auth import AuthService
from faststrap import (
    Container, Card, Input, Button, 
    Alert, Icon
)


def auth_routes(app):
    """Register authentication routes."""
    
    @app.get("/login")
    def login_page(request: Request):
        return Div(
            Container(
                Card(
                    Div(
                        # Logo
                        Div(
                            "TS",
                            cls="bg-primary text-white rounded d-flex align-items-center justify-content-center fw-bold mx-auto mb-3",
                            style="width: 50px; height: 50px; font-size: 1.5rem;"
                        ),
                        H4("Timetable Scheduler", cls="text-center fw-bold mb-1"),
                        P("Sign in to your account", cls="text-center text-muted small mb-4"),
                        
                        # Back Home Button
                        A(
                            Icon("arrow-left", cls="me-2"),
                            "Back to Home",
                            href="/",
                            cls="btn btn-outline-secondary btn-sm w-100 mb-3"
                        ),
                        
                        Form(
                            Div(
                                Label("User Name", cls="form-label small fw-bold text-muted"),
                                Input(type="text", name="username", placeholder="Username", required=True, cls="form-control bg-light border-0 py-2"),
                                cls="mb-3"
                            ),
                            Div(
                                Label("Password", cls="form-label small fw-bold text-muted"),
                                Input(type="password", name="password", placeholder="••••••••", required=True, cls="form-control bg-light border-0 py-2"),
                                cls="mb-4"
                            ),
                            Button(
                                "Sign In", 
                                type="submit", 
                                variant="primary", 
                                cls="w-100 py-2 fw-medium shadow-sm"
                            ),
                            method="post",
                            action="/login"
                        ),
                        
                        footer=Div(
                            P("Demo: Use any email and password (6+ chars)", cls="text-muted small text-center mb-0"),
                            cls="bg-transparent border-0 pt-3"
                        ),
                        cls="p-4"
                    ),
                    cls="shadow border-0 rounded-4",
                    style="max-width: 400px; width: 100%;"
                ),
                cls="min-vh-100 d-flex align-items-center justify-content-center"
            ),
            style="background-color: #ECF0F1; min-height: 100vh;"
        )

    @app.post("/login")
    async def login_submit(username: str, password: str, request: Request):
        db = request.state.db
        auth_service = AuthService(db)
        
        user = auth_service.authenticate_user(username, password)
        
        if not user:
            # For simplicity, we redirect back to login (FastHTML/HTMX can do better, but keeping it simple)
            return RedirectResponse(url="/login?error=invalid", status_code=303)
            
        # Create user session
        access_token, token_data = auth_service.create_user_tokens(user)
        
        resp = RedirectResponse(url="/dashboard", status_code=303)
        resp.set_cookie(
            key="access_token",
            value=access_token,
            httponly=True,
            samesite="lax",
            secure=False
        )
        return resp

    @app.get("/logout")
    def logout():
        resp = RedirectResponse(url="/login", status_code=303)
        resp.delete_cookie("access_token")
        return resp

 