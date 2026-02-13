Automated Timetable Scheduling System
Complete Architecture & Design Specification
1. Technology Stack
This system is built entirely with Python frameworks using a monolithic full-stack architecture:
•	FastHTML: Full-stack framework handling routing, business logic, database connections, and HTML rendering
•	Faststrap: Bootstrap components as Python functions for consistent UI
•	HTMX: Dynamic updates without page reloads (built into FastHTML)
•	SQLite/PostgreSQL: Database layer
•	CSP Solver: Constraint Satisfaction Problem algorithm for scheduling
2. Project Structure
timetable_system/
├── main.py                    # Application entry point
├── config.py                  # Configuration settings
├── models/                    # Database models
│   ├── user.py
│   ├── course.py
│   ├── lecturer.py
│   ├── venue.py
│   ├── timeslot.py
│   └── timetable.py
├── routes/                    # Route handlers
│   ├── auth.py               # Login/logout
│   ├── dashboard.py          # Dashboard
│   ├── courses.py            # Course CRUD
│   ├── lecturers.py          # Lecturer CRUD
│   ├── venues.py             # Venue CRUD
│   └── timetable.py          # Timetable generation & editing
├── scheduler/                 # Scheduling engine
│   ├── csp_solver.py         # CSP algorithm
│   ├── constraints.py        # Scheduling constraints
│   └── generator.py          # Timetable generator
├── components/                # Reusable UI components
│   ├── navbar.py
│   ├── sidebar.py
│   ├── forms.py
│   └── tables.py
├── utils/                     # Helper functions
│   ├── validators.py
│   └── pdf_generator.py
├── static/css/custom.css      # Custom styles
└── database/timetable.db      # SQLite database
3. Database Schema
User Table
id (PK), username, email, password_hash, role (admin/dept_head/lecturer), created_at
Course Table
id (PK), code, title, level, credit_hours, lecturer_id (FK), department
Lecturer Table
id (PK), name, email, department, max_hours_per_day
Venue Table
id (PK), name, capacity, type (lecture_hall/lab/classroom)
TimeSlot Table
id (PK), day (Mon-Fri), start_time, end_time
TimetableEntry Table
id (PK), course_id (FK), timeslot_id (FK), venue_id (FK), is_locked (Boolean for manual override)
4. Design System - Color Palette
•	Primary Dark (#2C3E50): Navbar, headers, primary buttons
•	Primary Blue (#3498DB): Links, active states, call-to-action
•	Success Green (#27AE60): Success messages, generate button
•	Danger Red (#E74C3C): Errors, conflict indicators, delete actions
•	Warning Orange (#F39C12): Warnings, pending actions
•	Light Gray (#ECF0F1): Backgrounds, table alternating rows
•	White (#FFFFFF): Content background, cards
5. Navigation & Routing
•	/ → Landing page (redirects to /login if not authenticated)
•	/login → User authentication
•	/dashboard → Main dashboard with statistics
•	/courses → Course management (CRUD)
•	/lecturers → Lecturer management
•	/venues → Venue/room management
•	/timetable → View and edit generated timetable
•	/timetable/generate → Trigger timetable generation
•	/timetable/export → Export as PDF
6. Key Features & UI Components
Dashboard
•	Statistics cards (total courses, lecturers, venues, generated timetables)
•	Quick action buttons
•	Recent activity feed
•	Conflict alerts (if any)
Course Management
•	Data table with search and filter
•	Add/Edit modal forms
•	Delete confirmation dialogs
•	Bulk import from CSV/Excel
Timetable Generation
•	Generate button with loading spinner
•	Progress indicator during generation
•	Conflict report if generation fails
•	Success message with link to view timetable
Timetable View & Editing
•	Weekly grid layout (days as columns, time slots as rows)
•	Color-coded course blocks
•	Drag-and-drop functionality for manual adjustments
•	Click to edit entry details
•	Lock icon for protected entries
•	Real-time conflict highlighting
•	Filter by department/level
7. Scheduling Algorithm Specifications
Algorithm Type
Constraint Satisfaction Problem (CSP) with backtracking algorithm
Hard Constraints (Must Be Satisfied)
•	No lecturer can teach two courses simultaneously
•	No venue can host two courses at the same time
•	No student level can have overlapping courses
•	Courses must fit within available time slots
•	Venue capacity must accommodate course enrollment
Soft Constraints (Optimization Goals)
•	Distribute courses evenly across the week
•	Minimize gaps in student schedules
•	Respect lecturer preferences (if specified)
•	Avoid Friday afternoon slots when possible
Implementation Steps
•	Load all courses, lecturers, venues, and time slots from database
•	Initialize empty timetable structure
•	Sort courses by constraints (most constrained first)
•	For each course, find valid time slot and venue
•	Check all hard constraints
•	If no valid assignment, backtrack and try different slot
•	Optimize for soft constraints
•	Save generated timetable to database
8. Manual Override System
The system allows administrators to manually adjust auto-generated timetables:
•	Drag-and-drop entries to different time slots
•	Click to edit course, lecturer, or venue assignment
•	Lock entries to prevent regeneration from overwriting
•	Real-time conflict detection during manual edits
•	Undo/redo functionality
•	Save changes or revert to auto-generated version
9. Typography & Spacing Guidelines
Typography
•	Font Family: Inter or System UI
•	H1: 24px, bold
•	H2: 20px, bold
•	H3: 18px, bold
•	Body: 16px, regular
•	Small/Labels: 14px
Spacing
•	Container Max Width: 1200px
•	Card Padding: 24px
•	Section Spacing: 48px
•	Border Radius: 8px
•	Grid System: Bootstrap 5 (12 columns)
