"""Main application entry point for the Timetable Scheduling System.

This module initializes the FastHTML application, sets up routes,
and configures the server.
"""

from fasthtml.common import *
from starlette.middleware import Middleware
from starlette.staticfiles import StaticFiles

from app.infrastructure.database.middleware import DBSessionMiddleware
from app.infrastructure.security.middleware import AuthMiddleware
from faststrap import add_bootstrap, mount_assets
from app.config import get_settings
from app.infrastructure.database import init_db
from app.presentation.components.shared import TIMETABLE_THEME, setup_timetable_defaults
from app.presentation.routes.auth import auth_routes
from app.presentation.routes.dashboard import dashboard_routes
from app.presentation.routes.courses import courses_routes
from app.presentation.routes.lecturers import lecturers_routes
from app.presentation.routes.venues import venues_routes
from app.presentation.routes.timetable import timetable_routes

# Get settings
settings = get_settings()

# Create FastHTML app with session support and DB/Auth middleware
app = FastHTML(
    secret_key=settings.secret_key,
    session_cookie="timetable_session",
    middleware=[
        Middleware(DBSessionMiddleware), 
        Middleware(AuthMiddleware) 
    ]
)

# Apply Faststrap theme
add_bootstrap(app, theme=TIMETABLE_THEME, mode="light")

# Setup component defaults
setup_timetable_defaults()

# Mount static files directory
mount_assets(app, "app/presentation/assets", url_path="/assets")

# Initialize database
init_db()

from app.presentation.routes.landing import landing_routes

# ... (imports)

def create_app():
    # Setup routes
    auth_routes(app)
    dashboard_routes(app)
    courses_routes(app)
    lecturers_routes(app)
    venues_routes(app)
    timetable_routes(app)
    landing_routes(app)
    
    from app.presentation.routes.student import student_routes
    student_routes(app)
    
    return app

# Call create_app to register routes immediately
create_app()

# Temporary home route removed (replaced by landing_routes)

# Health check endpoint
@app.get("/health")
def health_check():
    """Health check endpoint for monitoring."""
    return {"status": "healthy", "service": "timetable-system"}


# Run the application
if __name__ == "__main__":
    print(f"[*] Starting {settings.app_name}")
    print(f"[DB] Database: {settings.db_url}")
    print(f"[WEB] Server: http://{settings.host}:{settings.port}")
    serve(port=settings.port, host=settings.host)
