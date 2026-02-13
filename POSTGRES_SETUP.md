# PostgreSQL Setup Guide

## Current Status

✅ **Configuration Updated**:
- ENVIRONMENT set to `production` in `.env`
- Database URL: `postgresql://postgres:evayoung@localhost:5432/timetable_db`
- All emojis replaced with Faststrap Icon components

❌ **PostgreSQL Connection Failed**:
The application cannot connect to PostgreSQL. This needs to be resolved before proceeding.

---

## Quick Diagnosis

Run this command to test the connection:
```bash
python test_db.py
```

This will show:
- PostgreSQL version (if connected)
- Existing tables
- Detailed error message (if connection fails)

---

## Common Issues & Solutions

### 1. PostgreSQL Service Not Running

**Check if PostgreSQL is running:**
```bash
# Windows (PowerShell)
Get-Service postgresql*

# Or check with pg_ctl
pg_ctl status -D "C:\Program Files\PostgreSQL\<version>\data"
```

**Start PostgreSQL:**
```bash
# Windows Services
Start-Service postgresql-x64-<version>

# Or use pg_ctl
pg_ctl start -D "C:\Program Files\PostgreSQL\<version>\data"
```

### 2. Database Doesn't Exist

**Check if database exists:**
```bash
psql -U postgres -l
```

**Create the database:**
```bash
psql -U postgres
CREATE DATABASE timetable_db;
\q
```

### 3. Wrong Password

If password is incorrect, update `.env`:
```bash
DATABASE_URL=postgresql://postgres:YOUR_ACTUAL_PASSWORD@localhost:5432/timetable_db
```

### 4. PostgreSQL Not on Port 5432

**Check PostgreSQL port:**
```bash
psql -U postgres -c "SHOW port;"
```

If different, update `.env`:
```bash
DATABASE_URL=postgresql://postgres:evayoung@localhost:YOUR_PORT/timetable_db
```

---

## Once PostgreSQL is Working

### Step 1: Test Connection
```bash
python test_db.py
```

Should show:
```
[SUCCESS] Connected to PostgreSQL!
[INFO] PostgreSQL version: ...
[INFO] No tables found. Run 'python init_db.py' to create them.
```

### Step 2: Create Tables
```bash
python init_db.py
```

Should create 6 tables:
- users
- courses
- lecturers
- venues
- timeslots
- timetable_entries

### Step 3: Seed Sample Data
```bash
python seed_db.py
```

Creates:
- 3 users (admin, dept head, lecturer)
- 4 lecturers
- 7 venues
- 25 timeslots
- 8 courses

### Step 4: Restart Application
```bash
# Stop current server (Ctrl+C in terminal)
python main.py
```

Should now show:
```
[*] Starting Automated Timetable Scheduling System
[DB] Database: postgresql://postgres:***@localhost:5432/timetable_db
[WEB] Server: http://0.0.0.0:8000
```

---

## Verify Everything Works

1. **Visit** http://localhost:8000
2. **Should see** home page with Faststrap icons (not emojis)
3. **Database** should be using PostgreSQL (not SQLite)

---

## Files Created for PostgreSQL

| File | Purpose |
|------|---------|
| `test_db.py` | Test PostgreSQL connection and show diagnostics |
| `init_db.py` | Create all database tables |
| `seed_db.py` | Populate database with sample data |

---

## Need Help?

If you're still having issues, please share:
1. Output of `python test_db.py`
2. PostgreSQL version: `psql --version`
3. Service status: `Get-Service postgresql*`
