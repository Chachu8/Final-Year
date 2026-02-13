from fasthtml.common import *
from faststrap import *
from app.domain.models import Timetable, Course, TimetableEntry

def CourseCard(entry: TimetableEntry, readonly: bool = False):
    """Render a course card for the grid."""
    # Check if venue is assigned
    if entry.venue is None:
        # Unassigned course - use secondary color
        color = "secondary"
        venue_display = Div(
            Icon("exclamation-triangle-fill", cls="process-icon me-1"),
            Span("Unassigned", cls="small fst-italic"),
            cls="d-flex align-items-center mb-1"
        )
    else:
        # Assigned course - normal color mapping
        colors = ["primary", "success", "info", "warning", "danger", "dark"]
        color = colors[hash(entry.course.department) % len(colors)]
        venue_display = Div(
            Icon("geo-alt-fill", cls="process-icon me-1"),
            Span(entry.venue.name, cls="small"),
            cls="d-flex align-items-center mb-1"
        )
    
    # Lock Icon/Lecturer
    extras = []
    if entry.is_locked and not readonly:
        extras.append(Icon("lock-fill", cls="position-absolute top-0 end-0 m-2 small"))
    
    # Read-only specific: Show lecturer
    if readonly and entry.course.lecturer:
        extras.append(
             Div(
                Icon("person-fill", cls="me-1", style="font-size: 0.75rem;"),
                Span(entry.course.lecturer.name, cls="small"), # Full name for clarity
                cls="d-flex align-items-center mt-1",
                style="font-size: 0.8rem; opacity: 0.9;"
            )
        )
        
    card_content = Div(
        Div(
            Div(
                H2(entry.course.code, cls="h6 fw-bold mb-1"),
                venue_display,
                cls="d-flex justify-content-between align-items-center"
            ),
            Badge(entry.course.department, bg="white", text=color, cls="border"),
            *extras,
            cls="card-body p-2 position-relative"
        ),
        cls=f"card bg-{color} text-white shadow-sm mb-1 {'clickable-card' if not readonly else ''}",
        style=f"transition: transform 0.2s; {'cursor: pointer;' if not readonly else ''}"
    )

    
    # Build card with proper HTMX attributes if not readonly
    if not readonly:
        return Div(
            Div(
                Div(
                    H2(entry.course.code, cls="h6 fw-bold mb-1"),
                    venue_display,
                    cls="d-flex justify-content-between align-items-center"
                ),
                Badge(entry.course.department, bg="white", text=color, cls="border"),
                *extras,
                cls="card-body p-2 position-relative"
            ),
            cls=f"card bg-{color} text-white shadow-sm mb-1 clickable-card",
            style="transition: transform 0.2s; cursor: pointer;",
            data_bs_toggle="modal",
            data_bs_target="#editEntryModal",
            hx_get=f"/timetable/entry/{entry.id}",
            hx_target="#edit-entry-content"
        )
    else:
        return card_content

def TimetableGrid(data: dict, readonly: bool = False):
    """Render the main timetable grid table."""
    grid_rows = []
    for time_slot in data['times']:
        cells = [TCell(time_slot, cls="align-middle fw-bold bg-light")]
        for day in data['days']:
            entries = data['grid'].get(time_slot, {}).get(day, [])
            if entries:
                content = Div(*[CourseCard(e, readonly=readonly) for e in entries])
            else:
                content = "" # Empty cell
            cells.append(TCell(content, cls="align-middle"))
        grid_rows.append(TRow(*cells))
        
    return Card(
        Div(
            Table(
                THead(
                    TRow(
                        TCell("Time", cls="bg-light"),
                        *[TCell(day, cls="text-center bg-light") for day in data['days']]
                    )
                ),
                TBody(
                    *grid_rows
                ),
                cls="table table-bordered table-hover mb-0"
            ),
            cls="table-responsive"
        ),
        cls="shadow-sm border-0"
    )
