"""Venue Management Routes."""

from fasthtml.common import *
from starlette.requests import Request
from faststrap import Container, Row, Col, Card, Button, Icon, Input, Select, Modal, ConfirmDialog

from app.presentation.components.layout import DashboardLayout
from app.presentation.components.tables import DataTable, Badge

from app.domain.services.venue_service import VenueService

def venues_routes(app):
    """Register venue routes."""
    
    @app.get("/venues")
    def venues_list(request: Request):
        db = request.state.db
        venues_data = VenueService.get_all(db)
        
        rows = []
        for v in venues_data:
            badge_color = "primary"
            if v.type.value == "lab":
                badge_color = "info"
            elif v.type.value == "classroom":
                badge_color = "secondary"
                
            rows.append([
                v.name,
                f"{v.capacity} seats",
                Badge(v.type.value.replace("_", " ").title(), badge_color)
            ])
            # Use Name as ID (index 0)
        
        return DashboardLayout(
            # Header
            Div(
                H2("Venue Management", cls="fw-bold text-dark"),
                P("Manage classrooms, labs, and lecture halls", cls="text-muted"),
                cls="mb-4"
            ),
            
            # Toolbar
            Card(
                Row(
                    Col(
                        Div(
                            Icon("search", cls="text-muted position-absolute start-0 top-50 translate-middle-y ms-3"),
                            Input(name="search", type="text", placeholder="Search venues...", cls="form-control ps-5"),
                            cls="position-relative"
                        ),
                        cols=12, md=6
                    ),
                    Col(
                        Button(
                            Icon("plus", cls="me-2"), "Add Venue", 
                            variant="success", 
                            cls="text-white w-100",
                            data_bs_toggle="modal", 
                            data_bs_target="#addVenueModal",
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
                columns=["Venue Name", "Capacity", "Type"],
                rows=rows,
                id_index=0, # Use Name as ID
                edit_modal_id="editVenueModal",
                hx_edit_url="/venues/edit"
            ),
            
            # Edit Venue Modal
            Modal(
                Div(cls="p-5 text-center", children=[
                    Div(cls="spinner-border text-primary", role="status"),
                    P("Loading...", cls="mt-2 text-muted")
                ]),
                modal_id="editVenueModal",
                title="Edit Venue",
                centered=True,
                fade=True
            ),
            
            # Add Venue Modal
            Modal(
                Form(
                    Input(name="name", label="Venue Name", placeholder="e.g. Lecture Hall A", required=True),
                    Row(
                        Col(
                            Input(name="capacity", label="Capacity", type="number", placeholder="50", required=True),
                            cls="mb-3", cols=6
                        ),
                        Col(
                            Select(
                                "type",
                                ("Lecture Hall", "Lecture Hall"),
                                ("Lab", "Lab"),
                                ("Classroom", "Classroom"),
                                label="Type",
                                required=True
                            ),
                            cls="mb-3", cols=6
                        ),
                    ),
                    Div(
                        Button("Cancel", type="button", variant="light", cls="me-2", data_bs_dismiss="modal"),
                        Button("Save Venue", type="submit", variant="primary"),
                        cls="text-end"
                    ),
                    action="/venues", method="post"
                ),
                modal_id="addVenueModal",
                title="Add Venue",
                centered=True,
                fade=True
            ),

            # Delete Confirmation Modal
            ConfirmDialog(
                "Are you sure you want to delete this venue? This action cannot be undone.",
                confirm_text="Delete Venue",
                variant="danger",
                dialog_id="deleteConfirmModal",
                hx_confirm_url="/venues/delete",
                hx_confirm_method="delete",
            ),
             
            Script("""
                const deleteModal = document.getElementById('deleteConfirmModal')
                const confirmBtn = deleteModal.querySelector('.btn-danger')
                deleteModal.addEventListener('show.bs.modal', event => {
                    const button = event.relatedTarget
                    const id = button.getAttribute('data-delete-id')
                    confirmBtn.setAttribute('hx-delete', '/venues/' + id)
                    htmx.process(confirmBtn)
                })
            """),
            
            active_page="venues",
            current_user=request.state.user if hasattr(request.state, 'user') else None
        )

    @app.post("/venues")
    async def create_venue(
        request: Request,
        name: str = Form(...),
        capacity: int = Form(...),
        type: str = Form(...)
    ):
        db = request.state.db
        try:
            VenueService.create(db, name, capacity, type)
        except Exception as e:
            print(f"Error creating venue: {e}")
        return RedirectResponse(url="/venues", status_code=303)

    @app.get("/venues/edit/{name}")
    async def edit_venue_form(request: Request, name: str):
        db = request.state.db
        venue = VenueService.get_by_name(db, name)
        
        if not venue:
             return Div("Venue not found", cls="p-4 text-danger")
        
        # Determine selected type
        current_type = venue.type.value # e.g. "lecture_hall"
        # Map back to display Label if needed, or just select based on value logic
        # Our Enum values are lowercase with underscores
             
        return Div(
            Div(
                H5("Edit Venue", cls="modal-title"),
                Button(type="button", cls="btn-close", data_bs_dismiss="modal", aria_label="Close"),
                cls="modal-header"
            ),
            Div(
                Form(
                    # Hidden input for original name
                    Input(name="original_name", type="hidden", value=venue.name),
                    Input(name="name", label="Venue Name", value=venue.name, readonly=True),
                    Row(
                        Col(
                            Input(name="capacity", label="Capacity", type="number", value=str(venue.capacity), required=True),
                            cls="mb-3", cols=6
                        ),
                        Col(
                            Select(
                                "type",
                                ("Lecture Hall", "Lecture Hall", current_type == "lecture_hall"),
                                ("Lab", "Lab", current_type == "lab"),
                                ("Classroom", "Classroom", current_type == "classroom"),
                                label="Type",
                                required=True
                            ),
                            cls="mb-3", cols=6
                        ),
                    ),
                    Div(
                        Button("Cancel", type="button", variant="light", cls="me-2", data_bs_dismiss="modal"),
                        Button("Save Changes", type="submit", variant="primary"),
                        cls="text-end"
                    ),
                    action=f"/venues/edit/{name}", method="post"
                ),
                cls="modal-body"
            ),
            cls="modal-content"
        )

    @app.post("/venues/edit/{name}")
    async def update_venue(
        request: Request,
        name: str,
        capacity: int = Form(...),
        type: str = Form(...)
    ):
        db = request.state.db
        VenueService.update(db, name, capacity, type)
        return RedirectResponse(url="/venues", status_code=303)

    @app.delete("/venues/{name}")
    async def delete_venue(request: Request, name: str):
        db = request.state.db
        from app.domain.models.venue import Venue
        venue = db.query(Venue).filter(Venue.name == name).first()
        if venue:
            db.delete(venue)
            db.commit()
        return Response(status_code=200, headers={"HX-Location": "/venues"})
