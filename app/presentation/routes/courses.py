"""Course Management Routes."""

from fasthtml.common import *
from starlette.requests import Request
from faststrap import Container, Row, Col, Card, Button, Icon, Input, Select, Modal, ConfirmDialog

from app.presentation.components.layout import DashboardLayout
from app.presentation.components.tables import DataTable, Badge

from app.domain.services.course_service import CourseService
from app.domain.services.lecturer_service import LecturerService

def courses_routes(app):
    """Register course routes."""
    
    @app.get("/courses")
    def courses_list(request: Request):
        db = request.state.db
        courses_data = CourseService.get_all(db)
        lecturers_data = LecturerService.get_all(db)
        
        # Transform data for table
        rows = []
        for c in courses_data:
            lecturer_name = c.lecturer.name if c.lecturer else "Unassigned"
            rows.append([
                c.code, 
                c.title, 
                Badge(f"Level {c.level}", "secondary"), 
                str(c.credit_hours), 
                lecturer_name, 
                Badge(c.department, "info"),
            ])
            
        # Prepare lecturer options for matching Select
        lecturer_options = [("", "Select Lecturer...")]
        for l in lecturers_data:
            lecturer_options.append((l.id, l.name))
        
        return DashboardLayout(
            # Header
            Div(
                H2("Course Management", cls="fw-bold text-dark"),
                P("Manage courses and their assignments", cls="text-muted"),
                cls="mb-4"
            ),
            
            # Toolbar
            Card(
                Row(
                    Col(
                        Div(
                            Icon("search", cls="text-muted position-absolute start-0 top-50 translate-middle-y ms-3"),
                            Input(name="search", type="text", placeholder="Search courses...", cls="form-control ps-5"),
                            cls="position-relative"
                        ),
                        cols=12, md=6
                    ),
                    Col(
                        Button(
                            Icon("plus", cls="me-2"), "Add Course", 
                            variant="success", 
                            cls="text-white w-100",
                            data_bs_toggle="modal", 
                            data_bs_target="#addCourseModal",
                            style="max-width: 200px;"
                        ),
                        cols=12, md=6, cls="text-md-end mt-3 mt-md-0"
                    ),
                    cls="align-items-center",
                    cols=1,
                    cols_md=2,
                    cols_lg=2,
                ),
                cls="border-0 shadow-sm p-3 mb-4"
            ),
            
            # Data Table
            DataTable(
                columns=["Course Code", "Title", "Level", "Credits", "Lecturer", "Department"],
                rows=rows,
                id_index=0, # Using Course Code as ID
                edit_modal_id="editCourseModal",
                hx_edit_url="/courses/edit"
            ),
            
            # Edit Course Modal (Shell)
            Modal(
                Div(cls="p-5 text-center", children=[
                    Div(cls="spinner-border text-primary", role="status"),
                    P("Loading...", cls="mt-2 text-muted")
                ]),
                modal_id="editCourseModal",
                title="Edit Course", # Will be overwritten by HTMX response
                size="lg",
                centered=True,
                fade=True
            ),
            
            # Add Course Modal
            Modal(
                Form(
                    Row(
                        Col(
                            # Input component handles label
                            Input(name="code", label="Course Code", placeholder="e.g. CS101", required=True),
                            cls="mb-3", cols=6
                        ),
                        Col(
                            Input(name="credits", label="Credit Hours", type="number", placeholder="3", required=True),
                            cls="mb-3", cols=6
                        ),
                    ),
                    Input(name="title", label="Course Title", placeholder="Introduction to Computer Science", required=True),
                    Row(
                        Col(
                            Select(
                                "level",
                                ("100", "Level 100"),
                                ("200", "Level 200"),
                                ("300", "Level 300"),
                                ("400", "Level 400"),
                                label="Level",
                                required=True
                            ),
                            cls="mb-3", cols=6
                        ),
                        Col(
                            Select(
                                "department",
                                ("Science", "Science"),
                                ("Arts", "Arts"),
                                ("Engineering", "Engineering"),
                                label="Department",
                                required=True
                            ),
                            cls="mb-3", cols=6
                        ),
                    ),
                    Select(
                        "lecturer_id",
                        *lecturer_options,
                        label="Lecturer"
                    ),
                    Div(
                        Button("Cancel", type="button", variant="light", cls="me-2", data_bs_dismiss="modal"),
                        Button("Save Course", type="submit", variant="primary"),
                        cls="text-end"
                    ),
                    action="/courses", method="post"
                ),
                modal_id="addCourseModal",
                title="Add Course",
                size="lg",
                centered=True,
                fade=True
            ),

            # Delete Confirmation Modal
            ConfirmDialog(
                "Are you sure you want to delete this course? This action cannot be undone.",
                confirm_text="Delete Course",
                variant="danger",
                dialog_id="deleteConfirmModal",
                hx_confirm_url="/courses/delete", # Fallback
                hx_confirm_method="delete",
            ),
            
            Script("""
                const deleteModal = document.getElementById('deleteConfirmModal')
                const confirmBtn = deleteModal.querySelector('.btn-danger')
                deleteModal.addEventListener('show.bs.modal', event => {
                    const button = event.relatedTarget
                    const id = button.getAttribute('data-delete-id')
                    // Update HTMX url
                    confirmBtn.setAttribute('hx-delete', '/courses/' + id)
                    // We need to process the element to bind the new htmx info if needed,
                    // but changing attribute often works if htmx triggers on click.
                    htmx.process(confirmBtn)
                })
            """),
            
            active_page="courses",
            current_user=request.state.user if hasattr(request.state, 'user') else None
        )

    @app.post("/courses")
    async def create_course(
        request: Request,
        code: str = Form(...),
        title: str = Form(...),
        credits: int = Form(...),
        level: int = Form(...),
        department: str = Form(...),
        lecturer_id: Optional[str] = Form(None)
    ):
        db = request.state.db
        try:
            CourseService.create(db, code, title, credits, level, department, lecturer_id)
        except Exception as e:
            # Handle duplicate code or other errors
            print(f"Error creating course: {e}")
        
        return RedirectResponse(url="/courses", status_code=303)

    @app.get("/courses/edit/{code}")
    async def edit_course_form(request: Request, code: str):
        db = request.state.db
        course = CourseService.get_by_code(db, code)
        lecturers_data = LecturerService.get_all(db)
        
        if not course:
             return Div("Course not found", cls="p-4 text-danger")

        lecturer_options = [("", "Select Lecturer...")]
        for l in lecturers_data:
            lecturer_options.append((l.id, l.name, str(l.id) == str(course.lecturer_id) if course.lecturer_id else False))

        return Div(
            Div(
                H5("Edit Course", cls="modal-title"),
                Button(type="button", cls="btn-close", data_bs_dismiss="modal", aria_label="Close"),
                cls="modal-header"
            ),
            Div(
                Form(
                    # Hidden input for original code to identify record
                    Input(name="original_code", type="hidden", value=course.code),
                    Row(
                        Col(
                            # Code might be editable or read-only. Let's make it read-only for simplicity as it's the ID.
                            Input(name="code", label="Course Code", value=course.code, readonly=True),
                            cls="mb-3", cols=6
                        ),
                        Col(
                            Input(name="credits", label="Credit Hours", type="number", value=str(course.credit_hours), required=True),
                            cls="mb-3", cols=6
                        ),
                    ),
                    Input(name="title", label="Course Title", value=course.title, required=True),
                    Row(
                        Col(
                            Select(
                                "level",
                                ("100", "Level 100", course.level == 100),
                                ("200", "Level 200", course.level == 200),
                                ("300", "Level 300", course.level == 300),
                                ("400", "Level 400", course.level == 400),
                                label="Level",
                                required=True
                            ),
                            cls="mb-3", cols=6
                        ),
                        Col(
                            Select(
                                "department",
                                ("Science", "Science", course.department == "Science"),
                                ("Arts", "Arts", course.department == "Arts"),
                                ("Engineering", "Engineering", course.department == "Engineering"),
                                label="Department",
                                required=True
                            ),
                            cls="mb-3", cols=6
                        ),
                    ),
                    Select(
                        "lecturer_id",
                        *lecturer_options,
                        label="Lecturer"
                    ),
                    Div(
                        Button("Cancel", type="button", variant="light", cls="me-2", data_bs_dismiss="modal"),
                        Button("Save Changes", type="submit", variant="primary"),
                        cls="text-end"
                    ),
                    action=f"/courses/edit/{code}", method="post"
                ),
                cls="modal-body"
            ),
            cls="modal-content" # Return only modal content to replace existing content
        )

    @app.post("/courses/edit/{code}")
    async def update_course(
        request: Request,
        code: str,
        title: str = Form(...),
        credits: int = Form(...),
        level: int = Form(...),
        department: str = Form(...),
        lecturer_id: Optional[str] = Form(None)
    ):
        db = request.state.db
        CourseService.update(db, code, title, credits, level, department, lecturer_id)
        return RedirectResponse(url="/courses", status_code=303)

    @app.delete("/courses/{code}")
    async def delete_course(request: Request, code: str):
        db = request.state.db
        from app.domain.models.course import Course
        course = db.query(Course).filter(Course.code == code).first()
        if course:
            db.delete(course)
            db.commit()
        
        return Response(status_code=200, headers={"HX-Location": "/courses"})
