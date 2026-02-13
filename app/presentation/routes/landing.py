from fasthtml.common import *
from faststrap import *
from app.presentation.components.layout import DashboardLayout

# Define a simple Landing Layout (No sidebar, just Navbar)
def LandingLayout(*content, **kwargs):
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
                    A("Student Portal", href="/student", cls="btn btn-outline-light me-2"),
                    A("Admin Login", href="/login", cls="btn btn-light"),
                    cls="d-flex"
                ),
                cls="d-flex justify-content-between align-items-center"
            ),
            cls="navbar navbar-expand-lg navbar-dark bg-primary shadow-sm py-3"
        ),
        # Main Content (No height offset needed for full-screen carousel)
        Div(
            *content,
            style="background-color: #f8f9fa;"
        ),
        **kwargs
    )

def landing_routes(app):
    @app.get("/")
    def landing_page():
        # Full-screen Carousel with Dark Overlay and Centered Content
        carousel_images = [
            "/assets/unilorin1.jpg",
            "/assets/unilorin2.png",
            "/assets/unilorin3.jpg",
            "/assets/unilorin4.jpg",
            "/assets/unilorin5.jpg",
            "/assets/unilorin6.png",
            "/assets/unilorin7.jpg",
        ]
        
        carousel_items = []
        for i, img_src in enumerate(carousel_images):
            carousel_items.append(
                CarouselItem(
                    Img(
                        src=img_src, 
                        cls="d-block w-100", 
                        alt=f"Unilorin Campus {i+1}",
                        style="height: 90vh; object-fit: cover; filter: brightness(0.7);"
                    ),
                    active=(i == 0)
                )
            )

        # Carousel Component (Full Screen Background)
        carousel_section = Div(
            Carousel(
                *carousel_items,
                controls=True,
                indicators=True,
                ride="carousel",
                interval=4000,
                fade=True,
                cls="position-absolute top-0 start-0 w-100",
                style="height: 90vh; z-index: 1;"
            ),
            # Dark Overlay
            Div(
                cls="position-absolute top-0 start-0 w-100 h-100",
                style="background: linear-gradient(rgba(0,0,0,0.4), rgba(0,0,0,0.6)); z-index: 2; height: 90vh;"
            ),
            # Centered Hero Content
            Div(
                Div(
                    # Logo
                    Img(
                        src="/assets/logo.png", 
                        alt="University of Ilorin Logo",
                        cls="mb-4",
                        style="height: 120px; filter: drop-shadow(0 4px 6px rgba(0,0,0,0.3));"
                    ),
                    # Main Heading
                    H1(
                        "University of Ilorin",
                        cls="display-3 fw-bold text-white mb-3",
                        style="text-shadow: 2px 2px 8px rgba(0,0,0,0.5);"
                    ),
                    # Tagline
                    P(
                        "Better by Far",
                        cls="lead text-white mb-2 fw-light",
                        style="font-size: 1.5rem; text-shadow: 1px 1px 4px rgba(0,0,0,0.5);"
                    ),
                    # Subtitle
                    P(
                        "Automated Timetable Scheduling System",
                        cls="text-white-50 mb-5",
                        style="font-size: 1.1rem; text-shadow: 1px 1px 4px rgba(0,0,0,0.5);"
                    ),
                    # CTA Buttons
                    Div(
                        A(
                            Icon("calendar-check", cls="me-2"),
                            "View Timetables", 
                            href="/student", 
                            cls="btn btn-light btn-md px-5 py-3 me-3 fw-bold shadow-lg",
                            style="border-radius: 50px;"
                        ),
                        A(
                            Icon("box-arrow-in-right", cls="me-2"),
                            "Admin Portal", 
                            href="/login", 
                            cls="btn btn-outline-light btn-md px-5 py-3 fw-bold",
                            style="border-radius: 50px; border-width: 2px;"
                        ),
                        cls="d-flex justify-content-center flex-wrap gap-3"
                    ),
                    cls="text-center"
                ),
                cls="position-absolute top-50 start-50 translate-middle w-100",
                style="z-index: 3; max-width: 900px; padding: 0 20px;"
            ),
            cls="position-relative",
            style="height: 90vh; overflow: hidden;"
        )
        
        # Features Section
        features = Container(
            Row(
                Col(
                    Card(
                        Div(
                            Icon("calendar-check", style="font-size: 2.5rem;", cls="text-primary mb-3"),
                            H4("Conflict Free", cls="fw-bold mb-2"),
                            P("Optimized schedules with zero clashes for students and lecturers.", cls="text-muted small"),
                            cls="text-center p-4"
                        ),
                        cls="h-100 border-0 shadow-sm hover-card"
                    ),
                    cls="mb-4", cols=12, md=4
                ),
                Col(
                    Card(
                        Div(
                            Icon("phone", style="font-size: 2.5rem;", cls="text-success mb-3"),
                            H4("Mobile Accessible", cls="fw-bold mb-2"),
                            P("Access your timetable anywhere, anytime on any device.", cls="text-muted small"),
                            cls="text-center p-4"
                        ),
                        cls="h-100 border-0 shadow-sm hover-card"
                    ),
                    cls="mb-4", cols=12, md=4
                ),
                Col(
                    Card(
                        Div(
                            Icon("shield-check", style="font-size: 2.5rem;", cls="text-info mb-3"),
                            H4("Admin Control", cls="fw-bold mb-2"),
                            P("Secure portal for department heads to manage course constraints.", cls="text-muted small"),
                            cls="text-center p-4"
                        ),
                        cls="h-100 border-0 shadow-sm hover-card"
                    ),
                    cls="mb-4", cols=12, md=4
                ),
            ),
            cls="py-5"
        )
        
        # Footer
        footer = Div(
             Container(
                 P("© 2026 University of Ilorin. All Rights Reserved.", cls="mb-0 small")
             ),
             cls="bg-dark text-white-50 py-4 text-center mt-auto"
        )

        return LandingLayout(
            carousel_section,
            features,
            footer
        )
