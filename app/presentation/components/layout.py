"""Layout components for the application.

Includes the DashboardLayout with responsive sidebar and top navbar.
"""

from fasthtml.common import *
from faststrap import Container, Icon, Button
from typing import Any

# Color Palette from Spec
PRIMARY_DARK = "#2C3E50"
PRIMARY_BLUE = "#3498DB"
LIGHT_GRAY = "#ECF0F1"


def DashboardNavbar(current_user: Any) -> FT:
    """Fixed navbar for dashboard.
    
    Args:
        current_user: Current user object
        
    Returns:
        Navbar with logo and user profile
    """
    initials = "?"
    if hasattr(current_user, "full_name"):
        parts = current_user.full_name.split()
        initials = "".join([p[0].upper() for p in parts[:2]]) if parts else "?"
        
    role_label = current_user.role.value.replace("_", " ").title() if hasattr(current_user, "role") else "User"

    return Nav(
        Container(
            # Left: Brand (Mobile) - Removed Toggle Button as per user request
            Div(
                # Button removed here
                Div("TS Scheduler", cls="text-white fw-bold d-lg-none"), # Mobile brand
                cls="d-flex align-items-center"
            ),
            
            # Right: User Profile
            Div(
                Div(
                    Div(
                        initials,
                        cls="rounded-circle bg-white text-primary d-flex align-items-center justify-content-center fw-bold",
                        style="width: 35px; height: 35px; font-size: 0.9rem;"
                    ),
                    Div(
                        Div(current_user.full_name, cls="text-white fw-medium small"),
                        Div(role_label, cls="text-white-50 small", style="font-size: 0.75rem"),
                        cls="d-flex flex-column ms-2 d-none d-sm-block text-end pe-2"
                    ),
                    cls="d-flex align-items-center"
                ),
                cls="d-flex align-items-center"
            ),
            
            cls="d-flex justify-content-between align-items-center h-100",
            fluid=True
        ),
        cls="fixed-top shadow-sm",
        style=f"background-color: {PRIMARY_DARK}; height: 60px; z-index: 1030;"
    )

def Sidebar(active_page: str = "dashboard", mobile: bool = False) -> FT:
    """Sidebar navigation.
    
    Args:
        active_page: Key of the active page for highlighting
        mobile: If True, renders as plain content for inside offcanvas wrapper.
                If False, renders as fixed desktop sidebar.
        
    Returns:
        Sidebar component
    """
    nav_items = [
        {"icon": "grid-fill", "label": "Dashboard", "href": "/dashboard", "key": "dashboard"},
        {"icon": "journal-bookmark-fill", "label": "Courses", "href": "/courses", "key": "courses"},
        {"icon": "people-fill", "label": "Lecturers", "href": "/lecturers", "key": "lecturers"},
        {"icon": "building", "label": "Venues", "href": "/venues", "key": "venues"},
        {"icon": "calendar-week", "label": "Generate", "href": "/timetable", "key": "timetable"},
        {"icon": "clock-history", "label": "Timetables", "href": "/timetables", "key": "timetables"},
    ]
    
    content = [
        # Header
        Div(
            Div(
                Icon("calendar-date-fill", style="font-size: 1.5rem;"),
                cls="bg-primary text-white d-flex align-items-center justify-content-center rounded",
                style="width: 40px; height: 40px;"
            ),
            Div(
                H1("Timetable", cls="h5 mb-0 text-white fw-bold"),
                P("Scheduler System", cls="small text-white-50 mb-0"),
                cls="ms-3"
            ),
            cls="sidebar-header d-flex align-items-center px-4 py-3 mb-4 border-bottom border-white-10",
            style="height: 80px;"
        ),
        
        # Navigation
        Div(
            *[
                A(
                    Div(
                        Icon(item["icon"], cls="me-3", style="width: 20px; text-align: center;"),
                        Span(item["label"]),
                        cls="d-flex align-items-center"
                    ),
                    href=item["href"],
                    cls=f"nav-link text-white-50 py-3 px-4 d-block text-decoration-none {'active bg-primary text-white border-end border-4 border-info' if active_page == item['key'] else ''}",
                    style=f"transition: all 0.2s; {'background-color: rgba(255,255,255,0.05); color: white !important;' if active_page == item['key'] else ''}"
                )
                for item in nav_items
            ],
            cls="nav flex-column mb-auto"
        ),
        
        # Logout
        Div(
            A(
                Icon("box-arrow-right", cls="me-2"),
                "Logout",
                href="/logout",
                cls="btn btn-outline-light w-100 d-flex align-items-center justify-content-center"
            ),
            cls="p-4 mt-auto border-top border-white-20"
        ),
    ]
    
    # Common styles
    base_style = f"background-color: {PRIMARY_DARK} !important; width: 260px; d-flex flex-column h-100; z-index: 1040;"
    
    if mobile:
         # For mobile, it's just content inside the offcanvas wrapper
        return Div(
            *content,
            cls="d-flex flex-column h-100",
            style="background-color: inherit;"
        )
    else:
        # For desktop, it's a fixed sidebar
        return Div(
            *content,
            cls="bg-dark text-white d-flex flex-column h-100",
            # id="sidebar-desktop",  # Removed ID to avoid any potential conflict, usually not needed for fixed layout
            style=f"{base_style} position: fixed; top: 0; left: 0; bottom: 0; border-right: 1px solid rgba(0,0,0,0.1);"
        )


def MobileBottomNav(active_page: str = "dashboard") -> FT:
    """Mobile bottom navigation.
    
    Args:
        active_page: Key of the active page
        
    Returns:
        Bottom navigation bar for mobile screens
    """
    nav_items = [
        {"icon": "grid-fill", "label": "Dash", "href": "/dashboard", "key": "dashboard"},
        {"icon": "journal-bookmark-fill", "label": "Courses", "href": "/courses", "key": "courses"},
        {"icon": "people-fill", "label": "Staff", "href": "/lecturers", "key": "lecturers"},
        {"icon": "building", "label": "Venues", "href": "/venues", "key": "venues"},
        # 5th item is the Menu toggle button
    ]
    
    return Div(
        Div(
            *[
                A(
                    Icon(item["icon"], cls="mobile-nav-icon"),
                    Span(item["label"], cls="mobile-nav-label"),
                    href=item["href"],
                    cls=f"mobile-nav-item {'active' if active_page == item['key'] else ''}"
                )
                for item in nav_items
            ],
            # Menu button - toggles offcanvas sidebar
            A(
                Icon("list", cls="mobile-nav-icon"),
                Span("Menu", cls="mobile-nav-label"),
                cls="mobile-nav-item",
                data_bs_toggle="offcanvas",
                data_bs_target="#sidebar",
                role="button"
            ),
            cls="d-flex justify-content-around align-items-center w-100"
        ),
        cls="mobile-nav d-lg-none"
    )

def DashboardLayout(
    *content: Any,
    current_user: Any = None,
    active_page: str = "dashboard",
    **kwargs: Any
) -> FT:
    """Main dashboard layout wrapper.
    
    Args:
        *content: Content to display in main area
        current_user: Current user object
        active_page: Active page key
        
    Returns:
        Complete dashboard page structure
    """
    return Div(
        # Navbar
        DashboardNavbar(current_user),
        
        # Sidebar (Desktop - Fixed)
        Div(
            Sidebar(active_page, mobile=False),
            cls="d-none d-lg-block"
        ),
        
        # Mobile Offcanvas Sidebar Wrapper
        # This is the element targeted by data-bs-target="#sidebar"
        Div(
            # Header with Close Button for Mobile
            Div(
                 Div("Menu", cls="offcanvas-title h5 text-white"),
                 Button(
                     Icon("x-lg"), 
                     type="button", 
                     cls="btn-close btn-close-white", 
                     data_bs_dismiss="offcanvas", 
                     aria_label="Close"
                 ),
                 cls="offcanvas-header border-bottom border-white-10"
            ),
            # Sidebar Content
            Div(
                Sidebar(active_page, mobile=True),
                cls="offcanvas-body p-0"
            ),
            cls="offcanvas offcanvas-start d-lg-none",
            id="sidebar",
            tabindex="-1",
            style=f"background-color: {PRIMARY_DARK} !important; width: 260px;"
        ),
        
        # Main Content
        Div(
            Container(
                *content,
                fluid=True,
                cls="px-4 py-4"
            ),
            cls="main-content",
            style=f"margin-left: 0; margin-top: 60px; padding-bottom: 80px; min-height: 100vh; background-color: #F8F9FA;"
        ),
        
        # Bottom Navigation (Mobile Only)
        MobileBottomNav(active_page),
        
        # Style injection 
        Style("""
            /* Desktop Layout */
            @media (min-width: 992px) {
                .main-content { margin-left: 260px !important; padding-bottom: 2rem !important; }
            }
            .nav-link:hover { background-color: rgba(255,255,255,0.05); color: white !important; }
            
            /* Mobile Navigation Styles */
            .mobile-nav {
                position: fixed;
                bottom: 0;
                left: 0;
                right: 0;
                background: white;
                border-top: 1px solid #E5E7EB;
                padding: 0.5rem 0;
                z-index: 1030;
                box-shadow: 0 -2px 10px rgba(0, 0, 0, 0.1);
            }
            
            .mobile-nav-item {
                display: flex;
                flex-direction: column;
                align-items: center;
                text-decoration: none;
                color: #6B7280;
                font-size: 0.75rem;
                padding: 0.25rem 0.5rem;
                min-width: 60px;
                transition: color 0.2s;
            }
            .mobile-nav-item:hover { color: #4B5563; }
            
            .mobile-nav-item.active {
                color: #3498DB; /* Primary Blue from spec */
            }
            
            .mobile-nav-icon {
                font-size: 1.5rem;
                margin-bottom: 0.25rem;
            }
            
            .mobile-nav-label {
                font-size: 0.7rem;
                text-align: center;
                font-weight: 500;
            }
        """),
        
        **kwargs
    )
