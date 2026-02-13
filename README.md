# Automated Timetable Scheduling System

A web-based automated timetable scheduling system built with FastHTML and Faststrap.

## Features

- 🎯 **Automated Scheduling**: CSP-based algorithm for conflict-free timetable generation
- 👥 **Role-Based Access**: Admin, Department Head, and Lecturer roles
- 📊 **Dashboard**: Statistics and quick actions
- ✏️ **Manual Editing**: Drag-and-drop timetable adjustments
- 📄 **PDF Export**: Download and print timetables
- 📥 **Bulk Import**: CSV/Excel import for courses and data

## Tech Stack

- **Backend & Frontend**: FastHTML (unified full-stack framework)
- **UI Components**: Faststrap (Bootstrap 5 in Python)
- **Database**: PostgreSQL (production) / SQLite (development)
- **Authentication**: JWT tokens with bcrypt password hashing
- **Scheduling**: Constraint Satisfaction Problem (CSP) algorithm

## Setup

### Prerequisites

- Python 3.10+
- PostgreSQL (for production) or SQLite (for development)

### Installation

1. **Clone the repository**
   ```bash
   cd Final-Year
   ```

2. **Create virtual environment**
   ```bash
   python -m venv .venv
   # Windows
   .venv\Scripts\activate
   # Linux/Mac
   source .venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment**
   ```bash
   # Copy .env.example to .env
   copy .env.example .env  # Windows
   cp .env.example .env    # Linux/Mac
   
   # Generate secret keys
   python -c "import secrets; print(secrets.token_hex(32))"
   
   # Update .env with your database URL and generated secret keys
   ```

5. **Initialize database**
   ```bash
   # The database will be created automatically on first run
   # For PostgreSQL, create the database first:
   # createdb timetable_db
   ```

6. **Seed sample data** (optional)
   ```bash
   python seed_db.py
   ```

## Running the Application

```bash
python main.py
```

The application will be available at `http://localhost:8000`

### Sample Login Credentials (after seeding)

- **Admin**: `admin@university.edu` / `admin123`
- **Dept Head**: `depthead@university.edu` / `dept123`
- **Lecturer**: `lecturer1@university.edu` / `lect123`

## Project Structure

```
Final-Year/
├── main.py                      # Application entry point
├── seed_db.py                   # Database seeding script
├── app/
│   ├── config.py                # Configuration settings
│   ├── domain/
│   │   └── models/              # Database models
│   ├── infrastructure/
│   │   ├── database/            # Database connection & middleware
│   │   └── security/            # JWT & password hashing
│   └── presentation/
│       ├── components/          # Reusable UI components
│       └── routes/              # Route handlers
└── requirements.txt             # Python dependencies
```

## Development Status

### ✅ Completed (Phase 1-2)
- Project structure and configuration
- Database models with relationships
- PostgreSQL/SQLite database connection
- JWT authentication utilities
- Custom Faststrap theme
- Seed data script

### 🚧 In Progress (Phase 3)
- Authentication system (login/logout)
- Dashboard and UI components

### 📋 Planned
- CRUD operations for courses, lecturers, venues
- CSP-based scheduling algorithm
- Timetable generation and viewing
- Manual editing with drag-and-drop
- PDF export functionality

## License

MIT License - see LICENSE file for details
