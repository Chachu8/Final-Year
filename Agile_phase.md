Automated Timetable Scheduling System - Task Breakdown
Phase 1: Project Setup & Foundation
 Initialize project structure
 Set up pyproject.toml with dependencies
 Configure database connection (PostgreSQL/SQLite)
 Create base configuration files (.env.example, config.py)
 Set up custom Faststrap theme with project color palette
 Create password hashing and JWT utilities
 Create main.py application entry point
 Test database connection and create initial tables
Phase 2: Database Models & Schema
 Create User model (authentication & roles)
 Create Course model
 Create Lecturer model
 Create Venue model
 Create TimeSlot model
 Create TimetableEntry model
 Set up database middleware
 Create seed data script for testing
 Test all model relationships
Phase 3: Authentication System
 Create AuthService for login/logout
 Implement login route and form
 Implement logout functionality
 Create JWT token management
 Add role-based access control decorators
 Create authentication middleware
Phase 4: Core UI Redesign (Lovable AI Spec)
 Create DashboardLayout (Sidebar + Navbar)
 Create Sidebar component with navigation links
 Create Top Navbar with user profile
 Redesign Login Page (Clean, centered, academic aesthetic)
 Redesign Dashboard (Stats cards, Quick actions, Alerts)
 Implement responsive behavior (Offcanvas sidebar)
Phase 5: CRUD Operations (UI Prototype Complete)
 Implement Course Management UI (List, Add Modal, Delete Modal)
 Implement Lecturer Management UI (List, Add Modal, Delete Modal)
 Implement Venue Management UI (List, Add Modal, Delete Modal)
 Create Reusable Table Component (Faststrap)
 Connect UI to Database (Real CRUD)
 Implement Edit/Delete Logic (Backend & UI)
 Add Form Validation
Phase 6: Scheduling Engine (Complete)
 Design CSP solver architecture
 Implement constraint logic (Venue, Lecturer, Group)
 Build backtracking algorithm
 Create generation service
Phase 7: Timetable Generation UI (Complete)
 Build generation trigger page
 Add progress indicators
 Display conflict reports
 Store generated timetables (Stub)
Phase 8: Timetable Viewing & Editing (Complete)
 Create TimeSlot-based Grid Layout.
 Implement color-coded Course Cards with Lock indicators.
 Implement "Edit Entry" Modal (Real form with dynamic data).
 Implement 
update_entry
 logic with conflict checking.
 Implement "Restore" functionality (Unlock manual edits).
 Implement PDF Export (Stub - Phase 9).
Phase 10: Real-World Data & Constraints (Complete)
 Schema: Add semester, duration, frequency to Course.
 Data: Update 
TimeSlot
 generation (8am-6pm, 1hr).
 Logic: Update CSP for consecutive slots & semester filtering.
 Seeding: Create script for 5 Depts, ~150 courses.
Phase 10a: Priority Scheduling & Constraints (Complete)
 Schema: Make venue_id nullable in 
TimetableEntry
.
 Data: Update to ONLY 6 lecture venues (LT + LR1-5).
 Logic: Prioritize Higher Levels (400→100).
 Logic: Leave ALL venues unassigned for manual allocation.
 Logic: Block Friday 1-3 PM (Prayer time).
 UI: Fix icon alignment.
 UI: Display "Unassigned" in timetable view.
Phase 10b: Dynamic Constraint Configuration (Complete)
 UI: Add "Configure Constraints" button on generation page.
 UI: Create HTMX form with course list and constraint inputs.
 UI: Allow adding/removing duration & frequency per course.
 Backend: Accept constraints as JSON in generation request.
 Backend: Apply constraints dynamically (override DB values).
 Backend: Default to 1 hour, 1x/week if not specified.
Phase 11: Timetable Versioning & Publishing (Complete)
 Model: Create 
Timetable
 model (session, semester, status).
 Model: Update 
TimetableEntry
 with timetable_id FK.
 Backend: Update 
generate_timetable
 to create 
Timetable
 hierarchy.
 Backend: Implement get_timetables(db) and 
publish_timetable(id)
.
 UI: Create /timetables Dashboard (Browser).
 UI: Update /timetable/view to support versioning.
 UI: Add Floating Quick Access Button.
 UI: Implement Student View (Published only).
Phase 12: Polish & Refinements (Complete)
 UI: Add dynamic "Generate for X courses" text.
 UI: Update Dashboard Stats with real DB data.
 UI: Refine Navigation (Floating History, Sidebar, Quick Actions).
Phase 13: Student Portal & Landing Page (Complete)
 Landing: Create Landing Page with Hero and Carousel.
 Landing: Implement full-screen carousel (90vh) with dark overlay.
 Landing: Add centered hero content with logo and modern CTAs.
 Portal: Create Student View /student.
 Portal: Implement live filtering (Dept/Level) via HTMX.
 Portal: Implement read-only Timetable Grid.
Phase 14: Navigation & PDF Export (Complete)
 Navigation: Add "Back Home" button to login page.
 Navigation: Add "Back Home" button to student portal.
 Display: Show full lecturer names on student timetable cards.
 PDF: Install WeasyPrint library.
 PDF: Create PDF service for HTML-to-PDF conversion.
 PDF: Implement /timetable/export-pdf route.
 PDF: Wire up existing "Export PDF" button.
 PDF: Add "Download PDF" to student portal.

Comment
Ctrl+Alt+M
