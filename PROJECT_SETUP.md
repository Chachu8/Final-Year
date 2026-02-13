# Project Setup Guide

This guide provides step-by-step instructions to set up the **Automated Timetable Scheduling System** on your local machine.

---

## 1. Prerequisites

Before starting, ensure you have the following installed:

- **Python 3.10+**: [Download here](https://www.python.org/downloads/)
- **Git**: [Download here](https://git-scm.com/downloads)
- **PostgreSQL**: [Download here](https://www.postgresql.org/download/)

---

## 2. Clone the Project

Open your terminal (PowerShell or Command Prompt) and run:

```bash
git clone https://github.com/Final-Year/Final-Year.git
cd Final-Year
```

---

## 3. Python and Environment Setup

### Create a Virtual Environment

It's recommended to use a virtual environment to manage dependencies:

```bash
# Windows
python -m venv venv
.\venv\Scripts\activate
```

### Install Dependencies

Install all required packages including Faststrap:

```bash
pip install -r requirements.txt
```

### Install & Confirm Faststrap

Faststrap is a core component of this project. Install it explicitly to ensure it's available:

```bash
# Install Faststrap
pip install faststrap

# Confirm installation
faststrap version
```

---

## 4. Configuration Setup

### Environment Variables

1. Copy the example environment file:

   ```bash
   cp .env.example .env
   ```

2. Open `.env` in your text editor and update:
   - `DATABASE_URL`: Set your PostgreSQL password.
   - Example: `postgresql://postgres:YOUR_PASSWORD@localhost:5432/timetable_db`

---

## 5. PostgreSQL Database Setup

### Step 1: Start PostgreSQL Service

Ensure PostgreSQL is running on your machine:

```bash
# Check status
Get-Service postgresql*

# Start service (if not running)
Start-Service postgresql-x64-16 # replace 16 with your version
```

### Step 2: Create Database

```bash
psql -U postgres -c "CREATE DATABASE timetable_db;"
```

### Step 3: Test Connection

Run the diagnostic script to confirm connection:

```bash
python test_db.py
```

### Step 4: Initialize Tables

```bash
python init_db.py
```

### Step 5: Seed Sample Data

```bash
python seed_db.py
```

---

## 6. Running the Project

Once the database is confirmed to be working fine, run the application:

```bash
python main.py
```

The application will be available at: **<http://localhost:8000>**

---

## Summary of Management Files

| File | Purpose |
| :--- | :--- |
| `test_db.py` | Test PostgreSQL connection and show diagnostics |
| `init_db.py` | Create all database tables |
| `seed_db.py` | Populate database with sample data |
| `reset_database.py` | Drops all tables and re-initializes (CAUTION) |

---

## Verification Checklist

- [x] Python 3.10+ installed
- [x] Virtual environment active
- [x] `faststrap version` returns a version number
- [x] `.env` file contains correct database credentials
- [x] `python test_db.py` returns `[SUCCESS]`
- [x] `python main.py` starts the server without errors
