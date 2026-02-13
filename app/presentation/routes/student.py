from fasthtml.common import *
from faststrap import *
from app.domain.models import Course, Timetable, TimetableStatus
from app.domain.services.timetable_service import TimetableService
from app.presentation.components.timetable_view import TimetableGrid
from app.presentation.routes.timetable import DashboardLayout # Re-use or custom layout? 
# Use a custom Student Layout without Sidebar for cleaner look, or re-use DashboardNavbar?
# Let's define a simple layout here or reuse LandingLayout style but with filtering.

def StudentLayout(*content, **kwargs):
    return Div(
        # Navbar
        Nav(
            Container(
                A(
                    Img(src="/assets/logo.png", alt="Unilorin Logo", style="height: 40px; margin-right: 10px;"),
                    "Unilorin Timetable", 
                    cls="navbar-brand fw-bold text-white d-flex align-items-center", 
                    href="/"
                ),
                Div(
                    A(
                        Icon("arrow-left", cls="me-2"),
                        "Back Home",
                        href="/",
                        cls="btn btn-sm btn-outline-light me-3"
                    ),
                    # A("Help", href="#", cls="nav-link text-white-50 small me-3"),
                    cls="d-flex align-items-center"
                ),
                cls="d-flex justify-content-between align-items-center"
            ),
            cls="navbar navbar-expand-lg navbar-dark bg-primary shadow-sm py-2"
        ),
        # Main Content
        Container(
            *content,
            cls="py-4"
        ),
        style="background-color: #f8f9fa; min-height: 100vh;"
    )

def student_routes(app):
    @app.get("/student")
    def student_portal(request: Request):
        return StudentLayout(
            # Header
            Div(
                Div(
                    P("Home > Timetables", cls="small text-muted mb-1"),
                    H2("Student Timetables", cls="fw-bold text-dark"),
                    P("View and download your class schedules", cls="text-muted"),
                ),
                cls="mb-4"
            ),
            
            # Main Filter & Grid Container
            Div(
                hx_get="/student/timetables",
                hx_trigger="load",
                id="student-timetable-container"
            )
        )

    @app.get("/student/timetables")
    def student_timetables_partial(request: Request, department: str = "All", level: str = "All", query: str = ""):
        db = request.state.db
        
        # Get Latest Published Timetable
        timetable = db.query(Timetable).filter(Timetable.status == TimetableStatus.PUBLISHED).order_by(Timetable.created_at.desc()).first()
        
        if not timetable:
             return Div(
                 Div(
                     Icon("calendar-x", style="font-size: 3rem;", cls="text-muted mb-3"),
                     H4("No Timetable Published", cls="fw-bold"),
                     P("Please check back later.", cls="text-muted"),
                     cls="text-center py-5"
                 ),
                 cls="card shadow-sm border-0"
             )

        # Get Data for Grid
        # We reuse the Service but filter by Published ID
        data = TimetableService.get_timetable_grid(db, str(timetable.id), department, level)
        
        # Apply Text Search Filter (Service doesn't support text search on grid yet easily, so we rely on Dept/Level mostly)
        # If query exists, we might filter 'entries' manually in the grid data, but TimetableGrid expects structured data.
        # For prototype, we stick to Dept/Level filters as they are most effective for timetables.
        
        # Filter Options
        depts = [r[0] for r in db.query(Course.department).distinct().order_by(Course.department).all()]
        levels = [str(r[0]) for r in db.query(Course.level).distinct().order_by(Course.level).all()]

        return Div(
            # Filter Bar
            Card(
                Div(
                    Row(
                        Col(
                            Div(
                                Label("Department", cls="form-label small fw-bold text-muted"),
                                Select(
                                    "department",
                                    ("All", "All Departments", department == "All"),
                                    *[(d, d, department == d) for d in depts],
                                    cls="form-select",
                                    hx_get="/student/timetables",
                                    hx_target="#student-timetable-container",
                                    hx_include="[name='level'], [name='query']"
                                ),
                            ),
                            cols=12, md=4, cls="mb-3 mb-md-0"
                        ),
                        Col(
                            Div(
                                Label("Level", cls="form-label small fw-bold text-muted"),
                                Select(
                                    "level",
                                    ("All", "All Levels", level == "All"),
                                    *[(l, l, level == l) for l in levels],
                                    cls="form-select",
                                    hx_get="/student/timetables",
                                    hx_target="#student-timetable-container",
                                    hx_include="[name='department'], [name='query']"
                                ),
                            ),
                            cols=12, md=3, cls="mb-3 mb-md-0"
                        ),
                        # Col(
                        #      Div(
                        #         Label("Search", cls="form-label small fw-bold text-muted"),
                        #         Div(
                        #             Icon("search", cls="position-absolute top-50 start-0 translate-middle-y ms-3 text-muted"),
                        #             Input(
                        #                 type="search", 
                        #                 name="query", 
                        #                 value=query,
                        #                 placeholder="Search courses...", 
                        #                 cls="form-control ps-5",
                        #                 # hx_get="/student/timetables",
                        #                 # hx_trigger="keyup changed delay:500ms",
                        #                 # hx_target="#student-timetable-container",
                        #                 # hx_include="[name='department'], [name='level']"
                        #                 # Disabled text search for now as it requires complex grid filtering logic
                        #                 disabled=True
                        #             ),
                        #             cls="position-relative"
                        #         ),
                        #     ),
                        #     cols=12, md=5
                        # ),
                        cls="g-1",
                        cols=1,
                        cols_md=2,
                        cols_lg=2,
                    ),
                    cls="p-1"
                ),

                cls="shadow-sm border-0 mb-4 p-2"
            ),
            
            # Active Timetable Info & Download
            Div(
                 Div(
                     Badge("Active Timetable", bg="light", text="success", cls="border border-success me-2"),
                     Span(f"Session: {timetable.academic_session} | Semester {timetable.semester}", cls="text-muted small"),
                 ),
                 A(
                     Icon("file-pdf", cls="me-2"),
                     "Download PDF",
                     href=f"/timetable/export-pdf?timetable_id={timetable.id}&department={department}&level={level}",
                     cls="btn btn-sm btn-primary",
                     target="_blank"
                 ),
                 cls="mb-3 d-flex justify-content-between align-items-center flex-wrap gap-3"
            ),

            # Grid
            TimetableGrid(data, readonly=True)
        )
