"""Dashboard routes.

Handles the main dashboard view after login.
"""

from fasthtml.common import *
from starlette.requests import Request
from starlette.responses import RedirectResponse
from app.domain.services.auth import AuthService
from app.presentation.components.layout import DashboardLayout
from faststrap import (
    Row, Col, Card, Icon, Badge, Button
)
from sqlalchemy import func
from app.domain.models import Course, Lecturer, Venue, Timetable
from app.domain.services.auth import AuthService

# Use standard FastHTML components for Div, H2, P etc

def dashboard_routes(app):
    """Register dashboard routes."""
    
    @app.get("/dashboard")
    def dashboard(request: Request):
        token = request.cookies.get("access_token")
        if not token:
            return RedirectResponse(url="/login", status_code=303)
            
        db = request.state.db
        user = AuthService.get_current_user_from_token(token, db)
        
        if not user:
             return RedirectResponse(url="/login", status_code=303)


        # Stats Real Data
        courses_count = db.query(func.count(Course.id)).scalar()
        lecturers_count = db.query(func.count(Lecturer.id)).scalar()
        venues_count = db.query(func.count(Venue.id)).scalar()
        timetables_count = db.query(func.count(Timetable.id)).scalar()

        stats = [
            {"label": "Total Courses", "value": str(courses_count), "icon": "journal-bookmark-fill", "color": "primary"},
            {"label": "Total Lecturers", "value": str(lecturers_count), "icon": "people-fill", "color": "info"},
            {"label": "Total Venues", "value": str(venues_count), "icon": "building", "color": "warning"},
            {"label": "Generated Timetables", "value": str(timetables_count), "icon": "calendar-check", "color": "success"},
        ]

        return DashboardLayout(
            # Page Header
            Div(
                H2("Dashboard", cls="fw-bold text-dark"),
                P("Welcome to the Timetable Scheduling System", cls="text-muted"),
                cls="mb-4"
            ),
            
            # Stats Row
            Row(
                *[
                    Col(
                        Card(
                            Div(
                                Div(
                                    P(stat["label"], cls="text-muted mb-1 small fw-bold"),
                                    H2(stat["value"], cls="mb-0 fw-bold"),
                                    cls="flex-grow-1"
                                ),
                                Div(
                                    Icon(stat["icon"], style="font-size: 1.5rem;"),
                                    cls=f"bg-{stat['color']} bg-opacity-10 text-{stat['color']} p-3 rounded-circle d-flex align-items-center justify-content-center",
                                    style="width: 50px; height: 50px;"
                                ),
                                cls="d-flex align-items-center justify-content-between"
                            ),
                            cls="shadow-sm border-0 h-100 py-2"
                        ),
                        cols=12, md=6, lg=3, cls="mb-4"
                    ) for stat in stats
                ]
            ),
            
            # Quick Actions Section
            Card(
                Div(
                    H4("Quick Actions", cls="card-title fw-bold mb-3"),
                    Div(
                        # Update buttons to links (href) using A tag for proper navigation
                        A(Icon("plus", cls="me-1"), "Add Course", href="/courses", cls="btn btn-success me-2 text-white fw-medium", style="min-width: 200px;"),
                        A(Icon("plus", cls="me-1"), "Add Lecturer", href="/lecturers", cls="btn btn-primary me-2 text-white fw-medium", style="min-width: 200px;"),
                        A(Icon("calendar-plus", cls="me-1"), "Generate Timetable", href="/timetable", cls="btn btn-success me-2 text-white fw-medium", style="min-width: 200px;"),
                        A(Icon("collection", cls="me-1"), "Manage Timetables", href="/timetables", cls="btn btn-info text-white fw-medium", style="min-width: 200px;"),
                        cls="d-flex flex-wrap gap-2"
                    )
                ),
                cls="shadow-sm border-0 mb-4 p-4"
            ),
            
            # Alert Section - Dynamic based on real conflicts
            *_build_dashboard_alerts(db),
            
            current_user=user,
            active_page="dashboard"
        )

def _build_dashboard_alerts(db):
    """Build dashboard alert section based on real conflicts."""
    from app.domain.models import TimetableEntry, TimeSlot
    from sqlalchemy import and_
    
    # Check for conflicts in the latest published timetable
    latest_timetable = db.query(Timetable).filter(
        Timetable.status == "Published"
    ).order_by(Timetable.created_at.desc()).first()
    
    if not latest_timetable:
        # No timetable yet - show info alert
        return [
            Div(
                Div(
                    Icon("info-circle-fill", cls="me-2 text-info"),
                    Span("No Timetable Generated Yet", cls="fw-bold text-info"),
                    cls="mb-2 d-flex align-items-center"
                ),
                P("Generate your first timetable to get started.", cls="mb-3 small"),
                A("Generate Now", href="/timetable", cls="btn btn-info btn-sm px-3"),
                cls="alert alert-info border-info border-opacity-25 bg-info bg-opacity-10 rounded-3 p-4"
            )
        ]
    
    # Check for venue conflicts (same venue, same time slot)
    conflicts = []
    entries = db.query(TimetableEntry).filter(
        TimetableEntry.timetable_id == latest_timetable.id,
        TimetableEntry.venue_id.isnot(None)
    ).all()
    
    # Group by venue and time slot
    venue_time_map = {}
    for entry in entries:
        key = (entry.venue_id, entry.timeslot_id, entry.timeslot.day.value)
        if key not in venue_time_map:
            venue_time_map[key] = []
        venue_time_map[key].append(entry)
    
    # Find conflicts
    for key, entries_list in venue_time_map.items():
        if len(entries_list) > 1:
            venue = entries_list[0].venue
            time_slot = entries_list[0].timeslot
            day = time_slot.day.value
            courses = ", ".join([e.course.code for e in entries_list])
            conflicts.append(f"Venue conflict: {venue.name} double-booked on {day} {time_slot.start_time.strftime('%H:%M')}-{time_slot.end_time.strftime('%H:%M')} ({courses})")
    
    # Check for unassigned venues
    unassigned_count = db.query(func.count(TimetableEntry.id)).filter(
        TimetableEntry.timetable_id == latest_timetable.id,
        TimetableEntry.venue_id.is_(None)
    ).scalar()
    
    if conflicts:
        # Show danger alert with conflicts
        return [
            Div(
                Div(
                    Icon("exclamation-triangle-fill", cls="me-2 text-danger"),
                    Span("Scheduling Conflicts Detected", cls="fw-bold text-danger"),
                    cls="mb-2 d-flex align-items-center"
                ),
                Ul(
                    *[Li(conflict, cls="text-danger small") for conflict in conflicts[:5]],  # Show max 5
                    cls="mb-3 ps-3"
                ),
                A("View Timetable", href="/timetable/view", cls="btn btn-outline-danger btn-sm px-3"),
                cls="alert alert-danger border-danger border-opacity-25 bg-danger bg-opacity-10 rounded-3 p-4"
            )
        ]
    elif unassigned_count > 0:
        # Show warning for unassigned venues
        return [
            Div(
                Div(
                    Icon("exclamation-circle-fill", cls="me-2 text-warning"),
                    Span(f"{unassigned_count} Courses Need Venue Assignment", cls="fw-bold text-warning"),
                    cls="mb-2 d-flex align-items-center"
                ),
                P("Some courses don't have assigned venues yet. Manually assign them in the timetable view.", cls="mb-3 small"),
                A("Assign Venues", href="/timetable/view", cls="btn btn-outline-warning btn-sm px-3"),
                cls="alert alert-warning border-warning border-opacity-25 bg-warning bg-opacity-10 rounded-3 p-4"
            )
        ]
    else:
        # All good - show success alert
        return [
            Div(
                Div(
                    Icon("check-circle-fill", cls="me-2 text-success"),
                    Span("No Scheduling Issues", cls="fw-bold text-success"),
                    cls="mb-2 d-flex align-items-center"
                ),
                P("Your timetable is conflict-free and all venues are assigned!", cls="mb-0 small"),
                cls="alert alert-success border-success border-opacity-25 bg-success bg-opacity-10 rounded-3 p-4"
            )
        ]
