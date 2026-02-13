# Automated Timetable Scheduling System

![Project Banner](screenshots/landing_page.png)

A sophisticated web-based timetable scheduling system built with FastHTML and Faststrap, designed to automate course scheduling for universities using Constraint Satisfaction Problem (CSP) algorithms.

---

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Architecture](#architecture)
- [Technology Stack](#technology-stack)
- [Algorithm](#algorithm)
- [Screenshots](#screenshots)
- [Installation](#installation) 
- [Usage](#usage)
- [Color Specifications](#color-specifications)
- [Navigation](#navigation)
- [Project Structure](#project-structure)
- [Contributing](#contributing)

---

## 🎯 Overview

The Automated Timetable Scheduling System is a comprehensive solution for academic institutions to generate conflict-free timetables automatically. It handles complex scheduling constraints including venue capacity, lecturer availability, time slot conflicts, and departmental requirements.

### Key Capabilities

- **Automated Scheduling**: Generate timetables for 150+ courses across multiple departments
- **Constraint Management**: Handle venue conflicts, lecturer availability, and prayer time blocks
- **Manual Editing**: Fine-tune generated timetables with manual adjustments
- **Version Control**: Maintain multiple timetable versions (Draft/Published)
- **Student Portal**: Public-facing portal for students to view published timetables
- **PDF Export**: Export timetables as print-ready PDF documents

---

## ✨ Features

### Core Features

1. **Intelligent Scheduling Engine**
   - CSP-based backtracking algorithm
   - Priority-based scheduling (400-level → 100-level)
   - Automatic conflict detection and resolution
   - Configurable course duration and frequency

2. **CRUD Management**
   - Courses (Code, Title, Level, Semester, Department)
   - Lecturers (Name, Email, Department, Max Hours)
   - Venues (Name, Capacity, Type)
   - Time Slots (Day, Start Time, End Time)

3. **Timetable Management**
   - Generate timetables for specific semesters
   - View color-coded grid layout
   - Edit individual entries (venue/time slot)
   - Lock/unlock manual edits
   - Publish timetables for student access

4. **Advanced Features**
   - Dynamic constraint configuration per course
   - Venue conflict detection
   - Unassigned course tracking
   - Dashboard with real-time statistics
   - Role-based access control (Admin/Dept Head)

5. **Student Portal**
   - Read-only timetable view
   - Filter by department and level
   - PDF download functionality
   - Responsive design for mobile access

---

## 🏗️ Architecture

### System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Presentation Layer                       │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   Routes     │  │  Components  │  │   Layouts    │      │
│  │ (FastHTML)   │  │ (Faststrap)  │  │  (Sidebar)   │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                      Domain Layer                            │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   Services   │  │    Models    │  │  Algorithms  │      │
│  │ (Business)   │  │ (SQLAlchemy) │  │    (CSP)     │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                   Infrastructure Layer                       │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   Database   │  │   Security   │  │     PDF      │      │
│  │ (PostgreSQL) │  │    (JWT)     │  │  (ReportLab) │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
```

### Database Schema

```mermaid
erDiagram
    User ||--o{ Course : manages
    Lecturer ||--o{ Course : teaches
    Course ||--o{ TimetableEntry : "scheduled in"
    Venue ||--o{ TimetableEntry : "hosts"
    TimeSlot ||--o{ TimetableEntry : "occurs at"
    Timetable ||--o{ TimetableEntry : contains
    
    User {
        uuid id PK
        string username
        string email
        string password_hash
        enum role
        boolean is_active
    }
    
    Course {
        uuid id PK
        string code
        string title
        int level
        int semester
        int credit_hours
        string department
        int enrollment
        uuid lecturer_id FK
    }
    
    Lecturer {
        uuid id PK
        string name
        string email
        string department
        int max_hours_per_day
    }
    
    Venue {
        uuid id PK
        string name
        int capacity
        enum type
    }
    
    TimeSlot {
        uuid id PK
        enum day
        time start_time
        time end_time
    }
    
    Timetable {
        uuid id PK
        string academic_session
        int semester
        enum status
        boolean is_active
        datetime created_at
    }
    
    TimetableEntry {
        uuid id PK
        uuid timetable_id FK
        uuid course_id FK
        uuid timeslot_id FK
        uuid venue_id FK
        string day
        boolean is_locked
    }
```

---

## 🛠️ Technology Stack

### Backend
- **FastHTML** - Modern Python web framework
- **Faststrap** - Bootstrap components for FastHTML
- **SQLAlchemy** - ORM for database operations
- **PostgreSQL** - Primary database
- **Pydantic** - Data validation
- **Python-Jose** - JWT token handling
- **Passlib** - Password hashing

### Frontend
- **HTMX** - Dynamic HTML updates
- **Bootstrap 5** - UI framework
- **Bootstrap Icons** - Icon library
- **Custom CSS** - Tailored styling

### PDF Generation
- **ReportLab** - PDF creation library

### Development Tools
- **Python 3.10+**
- **pip** - Package manager
- **Git** - Version control

---

## 🧮 Algorithm

### Constraint Satisfaction Problem (CSP) Solver

The scheduling engine uses a **backtracking algorithm** with constraint propagation to generate conflict-free timetables.

#### Constraints

1. **Hard Constraints** (Must be satisfied)
   - No venue double-booking (same venue, same time)
   - No lecturer conflicts (same lecturer, same time)
   - Venue capacity ≥ course enrollment
   - Friday 1-3 PM blocked (prayer time)

2. **Soft Constraints** (Preferential)
   - Priority scheduling: 400-level → 300 → 200 → 100
   - Consecutive time slots for multi-hour courses
   - Balanced daily distribution

#### Algorithm Flow

```python
def backtrack(course_index):
    if course_index == total_courses:
        return True  # All courses scheduled
    
    course = sorted_courses[course_index]
    
    for time_slot in available_slots:
        for day in weekdays:
            if is_valid_assignment(course, time_slot, day):
                assign(course, time_slot, day)
                
                if backtrack(course_index + 1):
                    return True
                
                unassign(course, time_slot, day)
    
    return False  # No valid assignment found
```

#### Optimization Techniques

- **Forward Checking**: Prune invalid future assignments
- **Priority Ordering**: Schedule high-priority courses first
- **Constraint Propagation**: Reduce search space early
- **Backjumping**: Skip redundant backtracking steps

---

## 📸 Screenshots

### Landing Page
![Landing Page](screenshots/landing_page.png)
*Modern landing page with carousel and call-to-action buttons*

### Login Page
![Login Page](screenshots/login_page.png)
*Clean, centered authentication interface*

### Admin Dashboard
![Dashboard](screenshots/dashboard.png)
*Real-time statistics and quick actions*

### Course Management
![Courses](screenshots/courses_page.png)
*CRUD operations for course management*

### Timetable Generation
![Generation](screenshots/generation_page.png)
*Configure constraints and generate timetables*

### Constraint Configuration
![Constraints](screenshots/constraints_modal.png)
*Dynamic constraint configuration per course*

### Timetable View
![Timetable Grid](screenshots/timetable_view.png)
*Color-coded grid with manual editing capability*

### Edit Entry Modal
![Edit Modal](screenshots/edit_entry_modal.png)
*Modify venue and time slot assignments*

### Student Portal
![Student Portal](screenshots/student_portal.png)
*Public-facing timetable view with filters*

### PDF Export
![PDF Sample](screenshots/pdf_export.png)
*Print-ready A4 landscape timetable*

### Database Reset Utility
![Reset Script](screenshots/reset_database.png)
*Interactive database management tool*

---

## 💻 Installation

### Prerequisites

Before installing, ensure you have the following:

1. **Python 3.10 or higher**
   - Download: [https://www.python.org/downloads/](https://www.python.org/downloads/)
   - During installation, check "Add Python to PATH"

2. **PostgreSQL 14 or higher**
   - Download: [https://www.postgresql.org/download/](https://www.postgresql.org/download/)
   - Remember your postgres password during installation

3. **Git** (optional, for cloning)
   - Download: [https://git-scm.com/downloads](https://git-scm.com/downloads)

### Step 1: Download the Project

**Option A: Using Git**
```bash
git clone <repository-url>
cd Final-Year
```

**Option B: Download ZIP**
1. Download the project ZIP file
2. Extract to your desired location
3. Open terminal/command prompt in the extracted folder

### Step 2: Set Up Python Environment

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate

# On macOS/Linux:
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Configure PostgreSQL Database

#### 4.1 Create Database

Open PostgreSQL command line (psql) or pgAdmin and run:

```sql
CREATE DATABASE timetable_db;
CREATE USER timetable_user WITH PASSWORD 'your_secure_password';
GRANT ALL PRIVILEGES ON DATABASE timetable_db TO timetable_user;
```

#### 4.2 Configure Environment Variables

Create a `.env` file in the project root (copy from `.env.example`):

```env
# Database Configuration
DATABASE_URL=postgresql://timetable_user:your_secure_password@localhost:5432/timetable_db

# Security
SECRET_KEY=your-secret-key-here-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Application
DEBUG=True
```

**Important**: Replace `your_secure_password` and `your-secret-key-here` with your actual values.

### Step 5: Initialize Database

```bash
# Create database tables
python init_db.py
```

You should see:
```
[*] Initializing database...
[SUCCESS] Database initialized successfully!
```

### Step 6: Seed Database

Choose one of the seeding modes:

**Option A: Simple Test Data** (8 courses, 4 lecturers)
```bash
python seed_database.py --mode simple
```

**Option B: Realistic Data** (150 courses, 5 departments, 25 lecturers)
```bash
python seed_database.py --mode realistic
```

Expected output:
```
[*] Seeding database with REALISTIC data...
[+] Creating users...
[+] Creating lecturers...
[+] Creating venues...
[+] Creating timeslots...
[+] Creating courses...

[SUCCESS] Database seeded successfully!
  - 2 users
  - 25 lecturers (5 departments)
  - 6 venues
  - 50 timeslots
  - 150 courses

[INFO] Login credentials:
  Admin: admin / admin123
  Dean: dean / dean123
```

### Step 7: Run the Application

```bash
python main.py
```

The application will start on `http://localhost:5001`

You should see:
```
INFO:     Uvicorn running on http://0.0.0.0:5001
INFO:     Application startup complete.
```

### Step 8: Access the Application

Open your browser and navigate to:
- **Landing Page**: http://localhost:5001
- **Admin Login**: http://localhost:5001/login
- **Student Portal**: http://localhost:5001/student

**Default Credentials:**
- Username: `admin`
- Password: `admin123`

---

## 📖 Usage

### Admin Workflow

1. **Login** with admin credentials
2. **Manage Data**:
   - Add/Edit/Delete Courses (`/courses`)
   - Add/Edit/Delete Lecturers (`/lecturers`)
   - Add/Edit/Delete Venues (`/venues`)
3. **Generate Timetable**:
   - Go to Timetable page (`/timetable`)
   - Select semester
   - Configure constraints (optional)
   - Click "Generate Timetable"
4. **Review & Edit**:
   - View generated timetable (`/timetable/view`)
   - Click on course cards to edit venue/time slot
   - Use "Unlock/Restore" to revert manual changes
5. **Publish**:
   - Click "Publish" to make timetable visible to students
6. **Export**:
   - Click "Export PDF" for print-ready document

### Student Workflow

1. Visit Student Portal (`/student`)
2. Select Department and Level
3. View timetable
4. Download PDF (optional)

### Database Management

#### Reset Database

Use the interactive reset utility:

```bash
python reset_database.py
```

**Options:**
1. Reset ALL tables (complete wipe)
2. Reset Timetables only
3. Reset Courses only
4. Reset Lecturers only
5. Reset Venues only
6. Reset TimeSlots only
7. Reset Users only
8. Custom selection

**Example:**
```
==============================================================
  DATABASE RESET UTILITY
==============================================================

[WARNING] This tool performs DESTRUCTIVE operations!
          All data in selected tables will be PERMANENTLY DELETED.

Select reset option:
  1. Reset ALL tables (complete database wipe)
  ...
  0. Exit (cancel)
==============================================================

Enter your choice: 2

⚠️  Reset Timetables and TimetableEntries? (yes/no): yes

[*] Resetting 2 table(s)...
  [-] Clearing timetables...
  [-] Clearing timetable_entries...
[SUCCESS] Selected tables reset successfully!
```

---

## 🎨 Color Specifications

### Primary Palette

| Color Name | Hex Code | Usage |
|------------|----------|-------|
| Primary Blue | `#0d6efd` | Primary actions, links |
| Success Green | `#198754` | Success states, confirmations |
| Danger Red | `#dc3545` | Errors, deletions, conflicts |
| Warning Yellow | `#ffc107` | Warnings, pending states |
| Info Cyan | `#0dcaf0` | Informational messages |
| Dark Gray | `#212529` | Text, headers |

### Department Colors

Departments are color-coded in the timetable grid:

| Department | Color | Hex |
|------------|-------|-----|
| Computer Science | Primary | `#0d6efd` |
| Library Info Sci | Success | `#198754` |
| Mass Comm | Info | `#0dcaf0` |
| Info Tech | Warning | `#ffc107` |
| Telecom Sci | Danger | `#dc3545` |

### Status Colors

| Status | Color | Usage |
|--------|-------|-------|
| Draft | Secondary | Unpublished timetables |
| Published | Success | Active timetables |
| Unassigned | Secondary | Courses without venues |
| Locked | Dark | Manually edited entries |

---

## 🧭 Navigation

### Admin Navigation

**Sidebar Menu:**
- 📊 Dashboard (`/dashboard`)
- 📚 Courses (`/courses`)
- 👨‍🏫 Lecturers (`/lecturers`)
- 🏛️ Venues (`/venues`)
- 📅 Generate (`/timetable`)
- 📅 Timetable (`/timetables`)
- 🔒 Logout

**Quick Actions (Dashboard):**
- Generate Timetable
- View Timetable
- Manage Courses

**Floating Actions:**
- 🔄 Unlock/Restore (Timetable View)
- 📜 Timetable History (Quick Access)

### Student Navigation

**Top Bar:**
- 🏠 Home (Landing Page)
- 📅 View Timetable

**Filters:**
- Department Dropdown
- Level Dropdown

---

## 📁 Project Structure

```
Final-Year/
├── app/
│   ├── domain/
│   │   ├── models/          # SQLAlchemy models
│   │   │   ├── __init__.py
│   │   │   ├── base.py
│   │   │   ├── user.py
│   │   │   ├── course.py
│   │   │   ├── lecturer.py
│   │   │   ├── venue.py
│   │   │   ├── timeslot.py
│   │   │   └── timetable.py
│   │   └── services/        # Business logic
│   │       ├── scheduler.py # CSP algorithm
│   │       ├── timetable_service.py
│   │       └── pdf_service.py
│   ├── infrastructure/
│   │   ├── database/        # Database connection
│   │   │   ├── __init__.py
│   │   │   └── connection.py
│   │   └── security/        # Auth & security
│   │       ├── __init__.py
│   │       ├── auth.py
│   │       └── middleware.py
│   └── presentation/
│       ├── components/      # Reusable UI components
│       │   ├── __init__.py
│       │   ├── layout.py
│       │   └── timetable_view.py
│       └── routes/          # Route handlers
│           ├── __init__.py
│           ├── auth.py
│           ├── dashboard.py
│           ├── courses.py
│           ├── lecturers.py
│           ├── venues.py
│           ├── timetable.py
│           ├── student.py
│           └── landing.py
├── screenshots/             # Project screenshots
├── .env                     # Environment variables (create from .env.example)
├── .env.example             # Environment template
├── .gitignore
├── init_db.py               # Database initialization
├── seed_database.py         # Database seeding (simple/realistic)
├── reset_database.py        # Interactive database reset
├── main.py                  # Application entry point
├── requirements.txt         # Python dependencies
├── README.md                # This file
└── pyproject.toml           # Project metadata
```

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

## 👥 Authors

- **Olorundare Micheal** - *Initial work & Main Developer*
- **Asuku David** - *Project Owner*

---

## 🙏 Acknowledgments

- FastHTML framework by Answer.AI
- Faststrap for Bootstrap components
- Bootstrap team for the UI framework
- PostgreSQL community

---

## 📞 Support

For support, email meshelleva@gmail.com or open an issue in the repository.

---

**Built with ❤️ using FastHTML and Faststrap**
