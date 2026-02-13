"""Table components for the application."""

from fasthtml.common import *
from faststrap import Icon, Button, Table, THead, TBody, TRow, TCell
from typing import List, Any, Dict, Optional

def DataTable(
    columns: List[str],
    rows: List[List[Any]],
    actions: bool = True,
    edit_url: str = "#",
    delete_url: str = "#",
    id_index: int = 0,
    # Edit Action Config
    edit_modal_id: Optional[str] = None,
    hx_edit_url: Optional[str] = None,
    **kwargs
) -> FT:
    """Reusable Data Table component using Faststrap.
    
    Args:
        columns: List of column headers
        rows: List of row data
        actions: Whether to show action column
        edit_url: URL pattern for edit action (static link)
        delete_url: URL pattern for delete trigger
        id_index: Index of the column to use as ID for actions
        edit_modal_id: ID of modal to toggle for edit
        hx_edit_url: URL prefix for HTMX get request (e.g. /courses/edit)
    """
    
    # Header Row
    header_cells = [TCell(col, header=True, scope="col", cls="text-muted small fw-bold text-uppercase") for col in columns]
    if actions:
        header_cells.append(TCell("Actions", header=True, scope="col", cls="text-muted small fw-bold text-uppercase text-end"))
    
    # Body Rows
    body_rows = []
    for row in rows:
        cells = [TCell(cell, cls="align-middle") for cell in row]
        
        if actions:
            # Action Cell
            row_id = str(row[id_index]) if 0 <= id_index < len(row) else ""
            
            # Configure Edit Button
            edit_btn_attrs = {
                "variant": "link", 
                "size": "sm", 
                "cls": "text-primary p-0 me-2"
            }
            
            if hx_edit_url:
                edit_btn_attrs["hx_get"] = f"{hx_edit_url}/{row_id}"
                edit_btn_attrs["hx_target"] = f"#{edit_modal_id} .modal-content" if edit_modal_id else "#edit-modal-content"
                if edit_modal_id:
                    edit_btn_attrs["data_bs_toggle"] = "modal"
                    edit_btn_attrs["data_bs_target"] = f"#{edit_modal_id}"
            else:
                edit_btn_attrs["href"] = f"{edit_url}/{row_id}" if edit_url != "#" else "#"

            cells.append(
                TCell(
                    Div(
                        Button(Icon("pencil"), **edit_btn_attrs),
                        Button(
                            Icon("trash"), 
                            variant="link", size="sm", 
                            cls="text-danger p-0",
                            data_bs_toggle="modal",
                            data_bs_target="#deleteConfirmModal",
                            data_delete_id=row_id
                        ),
                        cls="d-flex justify-content-end"
                    ),
                    cls="align-middle"
                )
            )
        
        body_rows.append(TRow(*cells))

    # Return Faststrap Table
    return Table(
        THead(TRow(*header_cells), cls="bg-light"),
        TBody(*body_rows),
        hover=True,
        responsive=True,
        cls="bg-white rounded shadow-sm border mb-0"
    )

def Badge(text: str, variant: str = "primary", **kwargs) -> FT:
    """Faststrap badge wrapper."""
    from faststrap import Badge as FSBadge
    return FSBadge(text, variant=variant, cls="rounded-pill fw-normal", **kwargs)
