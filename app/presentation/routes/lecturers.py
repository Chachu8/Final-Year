"""Lecturer Management Routes."""

from fasthtml.common import *
from starlette.requests import Request
from faststrap import Container, Row, Col, Card, Button, Icon, Input, Select, Modal, ConfirmDialog

from app.presentation.components.layout import DashboardLayout
from app.presentation.components.tables import DataTable, Badge

from app.domain.services.lecturer_service import LecturerService

def lecturers_routes(app):
    """Register lecturer routes."""
    
    @app.get("/lecturers")
    def lecturers_list(request: Request):
        db = request.state.db
        lecturers_data = LecturerService.get_all(db)
        
        rows = []
        for l in lecturers_data:
            rows.append([
                l.name,
                l.email,
                Badge(l.department, "info"),
                f"{l.max_hours_per_day} hrs"
            ])
            # Note: Deleting by Name (col 0) might verify difficult if names are not unique.
            # Email is unique. Let's rely on Email?
            # DataTable id_index defaults to 0 (Name).
            # We should probably change DataTable to use Email (index 1) for ID?
            # Or just pass the ID as a hidden attribute in the name column?
            # For now, let's use Name and hope for unique names or refactor later.
            # Actually, `Lecturer` model has unique email.
        
        return DashboardLayout(
            # Header
            Div(
                H2("Lecturer Management", cls="fw-bold text-dark"),
                P("Manage teaching staff and their schedules", cls="text-muted"),
                cls="mb-4"
            ),
            
            # Toolbar
            Card(
                Row(
                    Col(
                        Div(
                            Icon("search", cls="text-muted position-absolute start-0 top-50 translate-middle-y ms-3"),
                            Input(name="search", type="text", placeholder="Search lecturers...", cls="form-control ps-5"),
                            cls="position-relative"
                        ),
                        cols=12, md=6
                    ),
                    Col(
                        Button(
                            Icon("plus", cls="me-2"), "Add Lecturer", 
                            variant="success", 
                            cls="text-white w-100",
                            data_bs_toggle="modal", 
                            data_bs_target="#addLecturerModal",
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
                columns=["Name", "Email", "Department", "Max Hours/Day"],
                rows=rows,
                id_index=1, # Use Email as ID
                edit_modal_id="editLecturerModal",
                hx_edit_url="/lecturers/edit"
            ),
            
            # Edit Lecturer Modal
            Modal(
                Div(cls="p-5 text-center", children=[
                    Div(cls="spinner-border text-primary", role="status"),
                    P("Loading...", cls="mt-2 text-muted")
                ]),
                modal_id="editLecturerModal",
                title="Edit Lecturer",
                centered=True,
                fade=True
            ),
            
            # Add Lecturer Modal
            Modal(
                Form(
                    Input(name="name", label="Full Name", placeholder="Dr. John Doe", required=True),
                    Input(name="email", label="Email Address", type="email", placeholder="john.doe@university.edu", required=True),
                    Row(
                        Col(
                            Select(
                                "department",
                                ("Science", "Science"),
                                ("Arts", "Arts"),
                                ("Engineering", "Engineering"),
                                ("Business", "Business"),
                                label="Department",
                                required=True
                            ),
                            cls="mb-3", cols=6
                        ),
                        Col(
                            Input(name="max_hours", label="Max Hours/Day", type="number", placeholder="6", required=True),
                            cls="mb-3", cols=6
                        ),
                    ),
                    Div(
                        Button("Cancel", type="button", variant="light", cls="me-2", data_bs_dismiss="modal"),
                        Button("Save Lecturer", type="submit", variant="primary"),
                        cls="text-end"
                    ),
                    action="/lecturers", method="post"
                ),
                modal_id="addLecturerModal",
                title="Add Lecturer",
                centered=True,
                fade=True
            ),

            # Delete Confirmation Modal
            ConfirmDialog(
                "Are you sure you want to delete this lecturer? This action cannot be undone.",
                confirm_text="Delete Lecturer",
                variant="danger",
                dialog_id="deleteConfirmModal",
                hx_confirm_url="/lecturers/delete",
                hx_confirm_method="delete",
            ),
             
            Script("""
                const deleteModal = document.getElementById('deleteConfirmModal')
                const confirmBtn = deleteModal.querySelector('.btn-danger')
                deleteModal.addEventListener('show.bs.modal', event => {
                    const button = event.relatedTarget
                    const id = button.getAttribute('data-delete-id')
                    confirmBtn.setAttribute('hx-delete', '/lecturers/' + id)
                    htmx.process(confirmBtn)
                })
            """),
            
            active_page="lecturers",
            current_user=request.state.user if hasattr(request.state, 'user') else None
        )

    @app.post("/lecturers")
    async def create_lecturer(
        request: Request,
        name: str = Form(...),
        email: str = Form(...),
        department: str = Form(...),
        max_hours: int = Form(...)
    ):
        db = request.state.db
        try:
            LecturerService.create(db, name, email, department, max_hours)
        except Exception as e:
            print(f"Error creating lecturer: {e}")
        return RedirectResponse(url="/lecturers", status_code=303)

    @app.get("/lecturers/edit/{email}")
    async def edit_lecturer_form(request: Request, email: str):
        db = request.state.db
        lecturer = LecturerService.get_by_email(db, email)
        
        if not lecturer:
             return Div("Lecturer not found", cls="p-4 text-danger")

        return Div(
            Div(
                H5("Edit Lecturer", cls="modal-title"),
                Button(type="button", cls="btn-close", data_bs_dismiss="modal", aria_label="Close"),
                cls="modal-header"
            ),
            Div(
                Form(
                    # Hidden input for original email
                    Input(name="original_email", type="hidden", value=lecturer.email),
                    Input(name="name", label="Full Name", value=lecturer.name, required=True),
                    Input(name="email", label="Email Address", type="email", value=lecturer.email, readonly=True),
                    Row(
                        Col(
                            Select(
                                "department",
                                ("Science", "Science", lecturer.department == "Science"),
                                ("Arts", "Arts", lecturer.department == "Arts"),
                                ("Engineering", "Engineering", lecturer.department == "Engineering"),
                                ("Business", "Business", lecturer.department == "Business"),
                                label="Department",
                                required=True
                            ),
                            cls="mb-3", cols=6
                        ),
                        Col(
                            Input(name="max_hours", label="Max Hours/Day", type="number", value=str(lecturer.max_hours_per_day), required=True),
                            cls="mb-3", cols=6
                        ),
                    ),
                    Div(
                        Button("Cancel", type="button", variant="light", cls="me-2", data_bs_dismiss="modal"),
                        Button("Save Changes", type="submit", variant="primary"),
                        cls="text-end"
                    ),
                    action=f"/lecturers/edit/{email}", method="post"
                ),
                cls="modal-body"
            ),
            cls="modal-content"
        )
    
    @app.post("/lecturers/edit/{email}")
    async def update_lecturer(
        request: Request,
        email: str,
        name: str = Form(...),
        department: str = Form(...),
        max_hours: int = Form(...)
    ):
        db = request.state.db
        LecturerService.update(db, email, name, department, max_hours)
        return RedirectResponse(url="/lecturers", status_code=303)

    @app.delete("/lecturers/{email}")
    async def delete_lecturer(request: Request, email: str):
        db = request.state.db
        from app.domain.models.lecturer import Lecturer
        lecturer = db.query(Lecturer).filter(Lecturer.email == email).first()
        if lecturer:
            db.delete(lecturer)
            db.commit()
        return Response(status_code=200, headers={"HX-Location": "/lecturers"})
