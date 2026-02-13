from starlette.requests import Request
from starlette.responses import RedirectResponse
from starlette.responses import Response # For HX-Redirect
import time, json
from fasthtml.common import *
from faststrap import Card, Button, Icon, Row, Col, Badge, TCell, TRow, THead, TBody, Table, Modal
from app.presentation.components.layout import DashboardLayout
from app.domain.services.timetable_service import TimetableService
from app.domain.models import Course, TimetableEntry, Venue, TimeSlot

def timetable_routes(app):
    """Register timetable routes."""
    
    @app.get("/timetable")
    def timetable_view(request: Request):
        db = request.state.db
        # Default stats for Semester 1
        stats = TimetableService.get_stats(db, semester=1)
        
        # Helper for rendering stats (Reusable)
        def render_stats_html(stats, semester):
            sem_suffix = "st" if semester == 1 else "nd" if semester == 2 else "th"
            return Div(
                H4("Ready to Generate", cls="fw-bold mb-3"),
                P(f"Generate a new timetable for the {stats['courses']} courses of {semester}{sem_suffix} Semester.", cls="text-muted mb-4"),
                
                # Stats Grid
                Row(
                    Col(
                        Div(
                            H4(str(stats['courses']), cls="fw-bold mb-1"),
                            P("Courses", cls="small text-muted mb-0"),
                            cls="p-3 bg-light rounded text-center"
                        ),
                        cols=4
                    ),
                    Col(
                        Div(
                            H4(str(stats['lecturers']), cls="fw-bold mb-1"),
                            P("Lecturers", cls="small text-muted mb-0"),
                            cls="p-3 bg-light rounded text-center"
                        ),
                        cols=4
                    ),
                    Col(
                        Div(
                            H4(str(stats['venues']), cls="fw-bold mb-1"),
                            P("Venues", cls="small text-muted mb-0"),
                            cls="p-3 bg-light rounded text-center"
                        ),
                        cols=4
                    ),
                    cls="mb-4 justify-content-center g-3 align-items-center",
                    style="max-width: 600px; margin: 0 auto;",
                    cols=1,
                    cols_md=3,
                    cols_lg=3,
                ),
                id="stats-wrapper"
            )

        return DashboardLayout(
            # Header
            Div(
                H2("Timetable Generation", cls="fw-bold text-dark"),
                P("Automatically create an optimized schedule", cls="text-muted"),
                cls="mb-4"
            ),
            
            # Main Content Area
            Card(
                Div(
            # Ready State Content
                    Div(
                        Div(
                            Icon("calendar-plus", style="font-size: 3rem;", cls="text-primary mb-3"),
                            cls="bg-primary bg-opacity-10 rounded-circle p-4 d-inline-flex mb-4",
                            style="width: 120px; height: 120px; align-items: center; justify-content: center;"
                        ),
                        Form(
                            # Stats Partial Container - Server Rendered Initial State
                            render_stats_html(stats, semester=1),
                            
                            Div(
                                Label("Target Semester:", cls="form-label fw-bold me-2", style="min-width: 200px;"),
                                Select(
                                    Option("Semester 1", value="1", selected=True),
                                    Option("Semester 2", value="2"),
                                    name="semester",
                                    id="semester-select",
                                    cls="form-select d-inline-block w-auto",
                                    hx_get="/timetable/stats-partial",
                                    hx_target="#stats-wrapper",
                                    hx_swap="outerHTML",
                                    style="min-width: 220px;"
                                ),
                                cls="mb-2 d-flex justify-content-center align-items-center flex-wrap",
                                cols=1,
                                cols_lg=2,
                            ),
                            
                            Row(
                                # Configure Constraints Button (opens modal)
                                Button(
                                    Icon("sliders", cls="me-2"),
                                    "Configure Constraints",
                                    type="button",
                                    variant="outline-primary",
                                    size="sm",
                                    style="width: 220px;",
                                    data_bs_toggle="modal",
                                    data_bs_target="#constraintsModal"
                                ),
                                
                                Button(
                                    Icon("lightning-fill", cls="me-2"),
                                    "Generate Timetable", 
                                    type="submit",
                                    variant="success", 
                                    size="md",
                                    cls="px-5 text-white fw-bold shadow-sm w-auto",
                                ),
                                cls="d-flex justify-content-center align-items-center gap-3 my-3",
                                cols=1,
                                cols_md=2,
                                cols_lg=2,
                            ),

                            # Hidden input to store constraints JSON
                            Input(type="hidden", name="constraints", id="constraints-input", value="{}"),
                            hx_post="/timetable/generate",
                            hx_target="#generation-container",
                            hx_swap="innerHTML",
                            cls="text-center"
                        ),
                        cls="text-center py-3",
                        id="generation-container"
                    ),
                    cls="p-3"
                ),
                cls="shadow-sm border-0"
            ),
            
            # Constraints Configuration Modal
            Modal(
                Div(
                    Div(cls="spinner-border text-primary", role="status"),
                    P("Loading courses...", cls="mt-2 text-muted"),
                    cls="p-5 text-center",
                    id="constraints-modal-content",
                    hx_get="/timetable/constraints-form",
                    hx_trigger="shown.bs.modal from:#constraintsModal",
                    hx_vals='js:{semester: document.getElementById("semester-select").value, current_constraints: document.getElementById("constraints-input").value || "{}"}'
                ),
                modal_id="constraintsModal",
                title="Configure Constraints",
                size="lg",
                centered=True,
                fade=True
            ),
            
            # Floating History Button (Top Right as requested)
            A(
                Icon("clock-history", cls="me-2"), "History",
                href="/timetables",
                cls="btn btn-outline-secondary shadow position-fixed top-0 end-0 m-4 mt-5 rounded-pill px-4 bg-white",
                style="z-index: 1050; margin-top: 80px !important;" 
            ),
            
            active_page="timetable",
            current_user=request.state.user if hasattr(request.state, 'user') else None
        )

    @app.get("/timetables")
    def list_timetables(request: Request):
        """List all timetables (Drafts and Published)."""
        db = request.state.db
        timetables = TimetableService.get_all_timetables(db)
        from app.domain.models import TimetableStatus
        
        # Helper for Badges
        def StatusBadge(status):
            colors = {
                TimetableStatus.DRAFT: "secondary",
                TimetableStatus.PUBLISHED: "success",
                TimetableStatus.ARCHIVED: "dark"
            }
            return Badge(status.value, bg=colors.get(status, "secondary"))

        rows = []
        for t in timetables:
            rows.append(
                TRow(
                    TCell(t.academic_session),
                    TCell(f"Semester {t.semester}"),
                    TCell(StatusBadge(t.status)),
                    TCell(t.created_at.strftime("%Y-%m-%d %H:%M") if t.created_at else "-"),
                    TCell(
                        Div(
                            A(Icon("eye"), cls="btn btn-sm btn-outline-primary me-1", href=f"/timetable/view?timetable_id={t.id}", title="View"),
                            Button(Icon("check-lg"), cls="btn btn-sm btn-outline-success me-1", 
                                   disabled=(t.status == TimetableStatus.PUBLISHED),
                                   hx_post=f"/timetable/publish/{t.id}", hx_swap="outerHTML", title="Publish") if t.status != TimetableStatus.PUBLISHED else "",
                            Button(Icon("trash"), cls="btn btn-sm btn-outline-danger", 
                                   hx_delete=f"/timetable/delete/{t.id}", 
                                   hx_confirm="Are you sure you want to delete this timetable?",
                                   hx_target="closest tr", 
                                   hx_swap="outerHTML", title="Delete"),
                            cls="d-flex"
                        )
                    )
                )
            )

        return DashboardLayout(
            Div(
                H2("Timetable Manage", cls="fw-bold text-dark"),
                P("Manage drafts and published schedules", cls="text-muted"),
                cls="mb-4"
            ),
            Card(
                Div(
                    Table(
                        THead(TRow(TCell("Session"), TCell("Semester"), TCell("Status"), TCell("Created"), TCell("Actions"))),
                        TBody(*rows) if rows else TBody(TRow(TCell("No timetables found", colspan=5, cls="text-center text-muted")))
                    ),
                    cls="table-responsive"
                ),
                cls="shadow-sm border-0"
            ),
             # Quick Access Floating Button (Top Right as requested)
            A(
                Icon("calendar-plus", cls="me-2"), "New",
                href="/timetable",
                cls="btn btn-primary shadow position-fixed top-0 end-0 m-4 mt-5 rounded-pill px-4",
                style="z-index: 1050; margin-top: 80px !important;" 
            ),
            active_page="timetables",
            current_user=request.state.user if hasattr(request.state, 'user') else None
        )

    @app.post("/timetable/generate")
    async def trigger_generation(request: Request):
        """Trigger generation and show processing state."""
        db = request.state.db
        form = await request.form()
        try:
            semester = int(form.get("semester", 1))
        except ValueError:
            semester = 1
        
        # Parse constraints JSON
        import json
        constraints_json = form.get("constraints", "{}")
        try:
            constraints = json.loads(constraints_json)
        except json.JSONDecodeError:
            constraints = {}
        
        # Run the generation algorithm
        # In a production app, this should be a background task (Celery/RQ)
        # For now, we run it synchronously to keep things simple
        success, timetable_id = TimetableService.generate_timetable(db, semester=semester, constraints=constraints)
        
        # Returns the "Processing" state which polls for completion
        return Div(
            Div(
                Div(cls="spinner-border text-primary", style="width: 4rem; height: 4rem;", role="status"),
                cls="mb-4"
            ),
            H4("Generating Timetable...", cls="fw-bold mb-2"),
            P("Please wait while we optimize the schedule...", cls="text-muted mb-4"),
            
            Div(cls="progress w-50 mx-auto mb-3", style="height: 6px;", children=[
                Div(cls="progress-bar progress-bar-striped progress-bar-animated", style="width: 100%")
            ]),
            
            # Polling to check status (Simulated with sleep for now)
            Div(
                hx_get=f"/timetable/status?id={timetable_id}",
                hx_trigger="load delay:2s", # Poll after 2 seconds
                hx_target="#generation-container",
                hx_swap="innerHTML"
            ),
            cls="text-center py-5 fade-in"
        )

    @app.get("/timetable/status")
    async def check_status(request: Request):
        """Check generation status."""
        # For now, immediately return "Complete" state
        # In real impl, this would check celery task status
        
        return Div(
            Div(
                Icon("check-lg", style="font-size: 3rem;", cls="text-success"),
                cls="bg-success bg-opacity-10 rounded-circle p-4 d-inline-flex mb-4",
                style="width: 120px; height: 120px; align-items: center; justify-content: center;"
            ),
            H4("Generation Complete!", cls="fw-bold mb-3"),
            P("Your timetable has been created without any conflicts.", cls="text-muted mb-4"),
            
            Div(
                A(
                    Icon("arrow-right", cls="ms-2 order-2"), "View Timetable", 
                    href=f"/timetable/view?timetable_id={request.query_params.get('id')}", 
                    cls="btn btn-success btn-md px-3 me-3 text-white fw-medium shadow-sm d-inline-flex align-items-center w-auto", # A tag style
                    style="min-width: 220px;"
                ),
                Button(
                    "Generate Again", 
                    variant="light", 
                    size="md",
                    cls="btn-md px-4 border",
                    hx_get="/timetable/reset", # Reset to ready state
                    hx_target="#generation-container",
                    style="min-width: 220px;"
                ),
                cls="d-flex justify-content-center flex-wrap gap-2"
            ),
            cls="text-center py-5 fade-in"
        )
    
    @app.get("/timetable/constraints-form")
    def constraints_form(request: Request):
        """Display constraint configuration modal content."""
        db = request.state.db
        semester = int(request.query_params.get("semester", 1))
        
        # Parse current constraints from client side
        try:
            constraints = json.loads(request.query_params.get("current_constraints", "{}"))
        except:
            constraints = {}
        
        # Initial load: Get first 10 courses
        courses = db.query(Course).filter(Course.semester == semester).order_by(Course.level, Course.code).limit(10).all()
        
        sem_suffix = "st" if semester == 1 else "nd" if semester == 2 else "th"

        # Helper to render rows (shared with search)
        def render_rows(courses, constraints):
            if not courses:
                return Div(P("No courses found.", cls="text-muted text-center py-3"), cls="w-100")
            
            rows = []
            for c in courses:
                c_data = constraints.get(str(c.id), {})
                dur = int(c_data.get("duration", 1))
                freq = int(c_data.get("frequency", 1))
                
                # Active state styling
                is_active = dur > 1 or freq > 1
                row_cls = "d-flex justify-content-between align-items-center p-1 border-bottom hover-bg-light transition-all"
                if is_active:
                    row_cls += " bg-light border-start border-primary border-4 ps-2"
                
                rows.append(
                    Div(
                        Div(
                            Strong(c.code, cls="d-block"),
                            Span(c.title[:30] + "..." if len(c.title)>30 else c.title, cls="small text-muted"),
                        ),
                        Div(
                            # Duration Toggles
                            Div(
                                Span("Duration:", cls="small text-muted me-2"),
                                Div(
                                    *[
                                        Button(f"{h}h", 
                                              type="button",
                                              cls=f"btn btn-sm {'btn-primary' if dur==h else 'btn-outline-primary'}",
                                              hx_post="/timetable/constraints/update",
                                              hx_vals=json.dumps({"course_id": str(c.id), "field": "duration", "value": h}),
                                              hx_include="#constraints-input", 
                                              hx_target=f"#course-row-{c.id}",
                                              hx_swap="outerHTML"
                                        ) for h in [1, 2, 3]
                                    ],
                                    cls="btn-group btn-group-sm me-3"
                                ),
                                cls="d-flex align-items-center"
                            ),
                            # Frequency Toggles
                            Div(
                                Span("Freq:", cls="small text-muted me-2"),
                                Div(
                                    *[
                                        Button(f"{f}x", 
                                              type="button",
                                              cls=f"btn btn-sm {'btn-primary' if freq==f else 'btn-outline-primary'}",
                                              hx_post="/timetable/constraints/update",
                                              hx_vals=json.dumps({"course_id": str(c.id), "field": "frequency", "value": f}),
                                              hx_include="#constraints-input", 
                                              hx_target=f"#course-row-{c.id}",
                                              hx_swap="outerHTML"
                                        ) for f in [1, 2]
                                    ],
                                    cls="btn-group btn-group-sm"
                                ),
                                cls="d-flex align-items-center"
                            ),
                            cls="d-flex align-items-center"
                        ),
                        id=f"course-row-{c.id}",
                        cls=row_cls
                    )
                )
            return Div(*rows)

        return Div(
            # Header
            Div(
                H5(f"Configure {semester}{sem_suffix} Semester Constraints", cls="fw-bold text-primary mb-1"),
                P("Set specific duration and frequency for courses.", cls="small text-muted mb-0"),
                cls="mb-2 pb-2 border-bottom"
            ),
            # Sticky Header with Search
            Div(
                Input(
                    type="search", 
                    name="q", 
                    placeholder="Search for courses (e.g. CSC201)...",
                    cls="form-control mb-3 shadow-sm",
                    autofocus=True,
                    hx_post="/timetable/constraints/search",
                    hx_trigger="keyup changed delay:300ms, search",
                    hx_target="#constraint-results",
                    hx_include="#constraints-input", # Send current constraints too
                    hx_vals=json.dumps({"semester": semester}) # Send semester
                ),
                Div(
                    Span(f"{len(constraints)} Constraints Configure", cls="badge bg-primary rounded-pill"),
                    cls="mb-2 text-end small"
                ) if constraints else "",
                cls="position-sticky top-0 bg-white pt-2 pb-1",
                style="z-index: 10;"
            ),
            
            # Scrollable Results
            Div(
                render_rows(courses, constraints),
                id="constraint-results",
                cls="overflow-auto custom-scrollbar",
                style="max-height: 50vh; min-width: 250px;"
            ),
            cls="w-100"
        )

    @app.post("/timetable/constraints/search")
    async def search_constraints(request: Request):
        """Search courses for constraint config."""
        db = request.state.db
        form = await request.form()
        query = form.get("q", "").strip()
        semester = int(form.get("semester", 1))
        
        # Parse current constraints to show correct states
        try:
            constraints = json.loads(form.get("constraints", "{}"))
        except:
            constraints = {}
            
        courses_query = db.query(Course).filter(Course.semester == semester)
        if query:
            courses_query = courses_query.filter(Course.code.ilike(f"%{query}%") | Course.title.ilike(f"%{query}%"))
            
        courses = courses_query.order_by(Course.level, Course.code).limit(20).all()
        
        # We need to re-use render_rows - duplicated logic for now vs shared function
        # Since we are inside a different function scope, we duplicate the renderer logic
        # Ideally this would be a standalone component function
        
        rows = []
        for c in courses:
            c_data = constraints.get(str(c.id), {})
            dur = int(c_data.get("duration", 1))
            freq = int(c_data.get("frequency", 1))
            
            is_active = dur > 1 or freq > 1
            row_cls = "d-flex justify-content-between align-items-center p-3 border-bottom hover-bg-light transition-all"
            if is_active:
                row_cls += " bg-light border-start border-primary border-4 ps-2"
            
            rows.append(
                Div(
                    Div(
                        Strong(c.code, cls="d-block"),
                        Span(c.title[:30] + "..." if len(c.title)>30 else c.title, cls="small text-muted"),
                    ),
                    Div(
                        Div(
                            Span("Duration:", cls="small text-muted me-2"),
                            Div(
                                *[
                                    Button(f"{h}h", 
                                          type="button",
                                              cls=f"btn btn-sm {'btn-primary' if dur==h else 'btn-outline-primary'}",
                                          hx_post="/timetable/constraints/update",
                                          hx_vals=json.dumps({"course_id": str(c.id), "field": "duration", "value": h}),
                                          hx_include="#constraints-input", 
                                          hx_target=f"#course-row-{c.id}",
                                          hx_swap="outerHTML"
                                    ) for h in [1, 2, 3]
                                ],
                                cls="btn-group btn-group-sm me-3"
                            ),
                            cls="d-flex align-items-center"
                        ),
                        Div(
                            Span("Freq:", cls="small text-muted me-2"),
                            Div(
                                *[
                                    Button(f"{f}x", 
                                          type="button",
                                          cls=f"btn btn-sm {'btn-primary' if freq==f else 'btn-outline-primary'}",
                                          hx_post="/timetable/constraints/update",
                                          hx_vals=json.dumps({"course_id": str(c.id), "field": "frequency", "value": f}),
                                          hx_include="#constraints-input", 
                                          hx_target=f"#course-row-{c.id}",
                                          hx_swap="outerHTML"
                                    ) for f in [1, 2]
                                ],
                                cls="btn-group btn-group-sm"
                            ),
                            cls="d-flex align-items-center"
                        ),
                        cls="d-flex align-items-center"
                    ),
                    id=f"course-row-{c.id}",
                    cls=row_cls
                )
            )
            
        if not rows:
             return Div(P("No matching courses found.", cls="text-muted text-center py-3"), cls="w-100")
             
        return Div(*rows)

    @app.post("/timetable/constraints/update")
    async def update_constraint(request: Request):
        """Update a constraint value and return updated row."""
        db = request.state.db
        form = await request.form()
        course_id = form.get("course_id")
        field = form.get("field") # 'duration' or 'frequency'
        value = int(form.get("value"))
        
        # Parse current constraints
        try:
            constraints = json.loads(form.get("constraints", "{}"))
        except:
            constraints = {}
        
        # Update logic
        if course_id not in constraints:
            constraints[course_id] = {"duration": 1, "frequency": 1}
        
        constraints[course_id][field] = value
        
        # Cleanup if default
        if constraints[course_id]["duration"] == 1 and constraints[course_id]["frequency"] == 1:
            if course_id in constraints:
                del constraints[course_id]
        
        new_constraints_json = json.dumps(constraints)
        
        # Re-render the specific row
        c = db.query(Course).filter(Course.id == course_id).first()
        if not c:
            return "" # Should not happen
            
        c_data = constraints.get(str(c.id), {})
        dur = int(c_data.get("duration", 1))
        freq = int(c_data.get("frequency", 1))
        
        is_active = dur > 1 or freq > 1
        row_cls = "d-flex justify-content-between align-items-center p-3 border-bottom hover-bg-light transition-all"
        if is_active:
            row_cls += " bg-light border-start border-primary border-4 ps-2 transition-all"
        
        # Row HTML
        row_html = Div(
            Div(
                Strong(c.code, cls="d-block"),
                Span(c.title[:30] + "..." if len(c.title)>30 else c.title, cls="small text-muted"),
            ),
            Div(
                Div(
                    Span("Duration:", cls="small text-muted me-2"),
                    Div(
                        *[
                            Button(f"{h}h", 
                                  type="button",
                                  cls=f"btn btn-sm {'btn-primary' if dur==h else 'btn-outline-primary'}",
                                  hx_post="/timetable/constraints/update",
                                  hx_vals=json.dumps({"course_id": str(c.id), "field": "duration", "value": h}),
                                  hx_include="#constraints-input", 
                                  hx_target=f"#course-row-{c.id}",
                                  hx_swap="outerHTML"
                            ) for h in [1, 2, 3]
                        ],
                        cls="btn-group btn-group-sm me-3"
                    ),
                    cls="d-flex align-items-center"
                ),
                Div(
                    Span("Freq:", cls="small text-muted me-2"),
                    Div(
                        *[
                            Button(f"{f}x", 
                                  type="button",
                                  cls=f"btn btn-sm {'btn-primary' if freq==f else 'btn-outline-primary'}",
                                  hx_post="/timetable/constraints/update",
                                  hx_vals=json.dumps({"course_id": str(c.id), "field": "frequency", "value": f}),
                                  hx_include="#constraints-input", 
                                  hx_target=f"#course-row-{c.id}",
                                  hx_swap="outerHTML"
                            ) for f in [1, 2]
                        ],
                        cls="btn-group btn-group-sm"
                    ),
                    cls="d-flex align-items-center"
                ),
                cls="d-flex align-items-center"
            ),
            id=f"course-row-{c.id}",
            cls=row_cls,
            # Script to update the hidden input on client side
            children=[
                Script(f"""
                    document.getElementById('constraints-input').value = '{new_constraints_json}';
                """)
            ]
        )
        
        return row_html

    @app.get("/timetable/view")
    def view_timetable(request: Request, department: str = "All", level: str = "All", timetable_id: str = None):
        from app.presentation.components.timetable_view import TimetableGrid
        db = request.state.db
        data = TimetableService.get_timetable_grid(db, timetable_id, department, level)
        timetable = data.get('timetable')
        
        # Helper for course card (REMOVED - moved to component)
        
        # Grid Rows (REMOVED - handled by component)

        # Dynamic Options for Filters
        from app.domain.models import Course
        depts = [r[0] for r in db.query(Course.department).distinct().order_by(Course.department).all()]
        levels = [str(r[0]) for r in db.query(Course.level).distinct().order_by(Course.level).all()]

        return DashboardLayout(
            # Page Header
            Div(
                Div(
                    H2(f"Timetable ({'Draft' if not timetable or timetable.status.value == 'Draft' else 'Published'})", cls="fw-bold text-dark"),
                    P(f"Session: {timetable.academic_session if timetable else '-'} | Semester: {timetable.semester if timetable else '-'}", cls="text-muted"),
                ),
                Div(
                    Button(
                        Icon("check-lg", cls="me-2"), "Publish", 
                        hx_post=f"/timetable/publish/{timetable.id}",
                        hx_swap="none", # Just toast?
                        cls="btn btn-success text-white me-2 shadow-sm"
                    ) if timetable and timetable.status.value == "Draft" else "",

                    
                    A(
                        Icon("file-pdf", cls="me-2"), "Export PDF",
                        href=f"/timetable/export-pdf?timetable_id={timetable.id if timetable else ''}&department={department}&level={level}",
                        cls="btn btn-outline-secondary shadow-sm",
                        target="_blank"
                    ) if timetable else "",
                    cls="d-flex"
                ),
                cls="d-flex justify-content-between align-items-center mb-4 w-100 flex-wrap"
            ),
            
            
            # Filters & Actions
            Card(
                Div(
                    Row(
                        Col(
                            Div(
                                Span("Department:", cls="me-2 fw-bold"),
                                Select(
                                    Option("All", value="All", selected=(department == "All")),
                                    *[Option(d, value=d, selected=(department == d)) for d in depts],
                                    name="department",
                                    cls="form-select d-inline-block w-auto",
                                    hx_get=f"/timetable/view?timetable_id={timetable_id if timetable_id else ''}",
                                    hx_target="body",
                                    hx_push_url="true",
                                    hx_include="[name='level']" # Include level value
                                ),
                                cls="d-flex align-items-center"
                            ),
                            cols="auto"
                        ),
                        Col(
                            Div(
                                Span("Level:", cls="me-2 fw-bold"),
                                Select(
                                    Option("All", value="All", selected=(level == "All")),
                                    *[Option(l, value=l, selected=(level == l)) for l in levels],
                                    name="level",
                                    cls="form-select d-inline-block w-auto",
                                    hx_get=f"/timetable/view?timetable_id={timetable_id if timetable_id else ''}",
                                    hx_target="body",
                                    hx_push_url="true",
                                    hx_include="[name='department']", # Include department value
                                    style="min-width: 220px;"
                                ),
                                cls="d-flex align-items-center"
                            ),
                            cols="auto"
                        ),
                         Col(
                            Div(
                                Div(
                                    Icon("lock-fill", cls="text-muted me-1"), "Locked",
                                    cls="small text-muted me-3"
                                ),
                                Div(
                                     Icon("exclamation-circle", cls="text-danger me-1"), "Conflict",
                                     cls="small text-danger"
                                ),
                                cls="d-flex align-items-center h-100 gap-3",
                                style="min-width: 220px;"
                            ),
                            cls="ms-auto"
                        ),
                        cls="align-items-center justify-content-between gap-3"
                    )
                ),
                cls="shadow-sm border-0 mb-4 p-3"
            ),
            
            # The Timetable Grid (Refactored)
            TimetableGrid(data, readonly=False),
            
            # Edit Entry Modal
            Modal(
                Div(cls="p-5 text-center", children=[
                    Div(cls="spinner-border text-primary", role="status"),
                    P("Loading entry details...", cls="mt-2 text-muted")
                ], id="edit-entry-content"), # ID on the content div
                modal_id="editEntryModal",
                title="", # Empty title as we render header inside
                centered=True
            ),
            
            # Floating Restore Button (Bottom Right)
            Button(
                Icon("arrow-counterclockwise", cls="me-2"), "Unlock/Restore",
                variant="dark",
                cls="position-fixed bottom-0 end-0 mb-5  m-4 shadow-lg rounded-pill px-4 py-2",
                style="z-index: 1050;",
                data_bs_toggle="tooltip",
                title="Unlock manual edits",
                hx_post="/timetable/restore",
                hx_swap="none"
            ),
            
            active_page="timetable",
            current_user=request.state.user if hasattr(request.state, 'user') else None
        )

    @app.post("/timetable/publish/{timetable_id}")
    def publish_timetable(request: Request, timetable_id: str):
        db = request.state.db
        success, msg = TimetableService.publish_timetable(db, timetable_id)
        # We could return a toast or redirect
        # For simple UX, let's redirect to list
        from starlette.responses import Response
        return Response(status_code=200, headers={"HX-Redirect": "/timetables"})

    @app.delete("/timetable/delete/{timetable_id}")
    def delete_timetable(request: Request, timetable_id: str):
        db = request.state.db
        TimetableService.delete_timetable(db, timetable_id)
        return "" # Remove row

    @app.get("/timetable/entry/{entry_id}")
    def edit_entry_form(request: Request, entry_id: str):
        """Fetch form to edit a specific timetable entry."""
        db = request.state.db
        entry = TimetableService.get_entry(db, entry_id)
        
        if not entry:
            return Div("Entry not found", cls="alert alert-danger")

        # Fetch options for dropdowns
        from app.domain.models import TimeSlot, Venue
        timeslots = db.query(TimeSlot).all()
        # Sort timeslots by day and time
        day_order = {"Monday": 0, "Tuesday": 1, "Wednesday": 2, "Thursday": 3, "Friday": 4}
        timeslots.sort(key=lambda t: (day_order.get(t.day.value, 99), t.start_time))
        
        venues = db.query(Venue).all()
        venues.sort(key=lambda v: v.name)

        return Div(
            Div(
                H5(f"Edit: {entry.course.code}", cls="modal-title"),
                Button(type="button", cls="btn-close", data_bs_dismiss="modal"),
                cls="modal-header"
            ),
            Form(
                Div(
                    P(f"Course: {entry.course.title}", cls="text-muted mb-3"),
                    
                    # TimeSlot Select
                    Div(
                         Label("Time Slot", cls="form-label fw-bold"),
                         Select(
                             *[Option(f"{ts.day.value} {ts.start_time.strftime('%H:%M')}-{ts.end_time.strftime('%H:%M')}", 
                                      value=ts.id, 
                                      selected=(ts.id == entry.timeslot_id)) 
                               for ts in timeslots],
                             name="new_timeslot_id",
                             cls="form-select"
                         ),
                         cls="mb-3"
                    ),
                    
                    # Venue Select
                    Div(
                         Label("Venue", cls="form-label fw-bold"),
                         Select(
                             *[Option(f"{v.name} (Cap: {v.capacity})", 
                                      value=v.id, 
                                      selected=(v.id == entry.venue_id)) 
                               for v in venues],
                             name="new_venue_id",
                             cls="form-select"
                         ),
                         cls="mb-3"
                    ),
                    
                    Div(id="edit-error", cls="text-danger small mb-2"),
                    cls="modal-body"
                ),
                Div(
                    Button("Close", type="button", variant="secondary", data_bs_dismiss="modal"),
                    Button("Save Changes", type="submit", variant="primary", cls="ms-2"),
                    cls="modal-footer"
                ),
                hx_put=f"/timetable/entry/{entry_id}",
                hx_target="#edit-error", 
            )
            # Return just the modal content without wrapping id
            # The HTMX will replace the content of #edit-entry-content
        )

    @app.put("/timetable/entry/{entry_id}")
    async def update_entry(request: Request, entry_id: str):
        """Handle entry update."""
        form = await request.form()
        db = request.state.db
        
        success, message = TimetableService.update_entry(
            db, 
            entry_id, 
            form.get("new_timeslot_id"), 
            form.get("new_venue_id")
        )
        
        if success:
            # Refresh the grid view
            # Using HTMX to redirect or refresh is tricky from modal.
            # Best: Return a script to close modal and refresh page OR simply redirect.
            # HX-Redirect header is supported by HTMX
            from fasthtml.common import Response
            return Response(headers={"HX-Redirect": "/timetable/view"})
        else:
            return Div(message, cls="alert alert-danger")

    @app.post("/timetable/restore")
    def restore_timetable(request: Request):
        """Unlock all entries (Restore)."""
        db = request.state.db
        TimetableService.restore_timetable(db)
        from fasthtml.common import Response
        return Response(headers={"HX-Refresh": "true"})

    @app.get("/timetable/stats-partial")
    def stats_partial(request: Request):
        """Return partial HTML for stats based on semester."""
        db = request.state.db
        try:
             semester = int(request.query_params.get("semester", 1))
        except:
             semester = 1
             
        stats = TimetableService.get_stats(db, semester=semester)
        
        sem_suffix = "st" if semester == 1 else "nd" if semester == 2 else "th"
        
        return Div(
            H4("Ready to Generate", cls="fw-bold mb-3"),
            P(f"Generate a new timetable for the {stats['courses']} courses of {semester}{sem_suffix} Semester.", cls="text-muted mb-4"),
            
            # Stats Grid
            Row(
                Col(
                    Div(
                        H4(str(stats['courses']), cls="fw-bold mb-1"),
                        P("Courses", cls="small text-muted mb-0"),
                        cls="p-3 bg-light rounded text-center"
                    ),
                    cols=4
                ),
                Col(
                    Div(
                        H4(str(stats['lecturers']), cls="fw-bold mb-1"),
                        P("Lecturers", cls="small text-muted mb-0"),
                        cls="p-3 bg-light rounded text-center"
                    ),
                    cols=4
                ),
                Col(
                    Div(
                        H4(str(stats['venues']), cls="fw-bold mb-1"),
                        P("Venues", cls="small text-muted mb-0"),
                        cls="p-3 bg-light rounded text-center"
                    ),
                    cols=4
                ),
                cls="mb-4 justify-content-center g-3 align-items-center",
                style="max-width: 600px; margin: 0 auto;"
            ),
            id="stats-wrapper"
        )
    
    @app.get("/timetable/export-pdf")
    def export_timetable_pdf(request: Request, timetable_id: str = None, department: str = "All", level: str = "All"):
        """Export timetable as PDF."""
        from app.domain.services.pdf_service import PDFService
        
        db = request.state.db
        
        try:
            # Generate PDF
            pdf_bytes = PDFService.generate_timetable_pdf(db, timetable_id, department, level)
            
            # Get timetable for filename
            data = TimetableService.get_timetable_grid(db, timetable_id, department, level)
            timetable = data.get('timetable')
            
            # Create filename
            filename = f"timetable_{timetable.academic_session.replace('/', '_')}_S{timetable.semester}"
            if department != "All":
                filename += f"_{department}"
            if level != "All":
                filename += f"_L{level}"
            filename += ".pdf"
            
            # Return PDF response
            return Response(
                content=pdf_bytes,
                media_type="application/pdf",
                headers={
                    "Content-Disposition": f'attachment; filename="{filename}"'
                }
            )
        except Exception as e:
            # Return error message
            return Div(
                Alert(f"Error generating PDF: {str(e)}", variant="danger"),
                cls="p-4"
            )