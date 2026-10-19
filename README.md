# Attendance Management System

A beginner-friendly college DBMS project using HTML, CSS, JavaScript, Python Flask and MySQL. SQL queries are written explicitly in Python using `mysql-connector-python`; no ORM is used.

## Features

- Dashboard totals for students, subjects and attendance records
- Add, view and update students
- Add and view subjects
- Mark, view and update attendance
- Search attendance by roll number
- Calculate attendance percentage per subject
- Primary keys, foreign keys, unique constraints and joined SELECT queries
- Basic input validation and error messages

## Project structure

```text
AttendanceManagementSystem/
├── app.py
├── templates/
│   └── index.html
├── static/
│   ├── style.css
│   └── script.js
├── database/
│   └── database.sql
├── requirements.txt
├── Procfile
├── .env.example
├── .gitignore
└── README.md
```

## Run locally in VS Code

### 1. Requirements
Install Python 3.10+ and MySQL Server. MySQL Workbench is useful for viewing/testing the database.

### 2. Create a virtual environment (recommended)

Windows PowerShell:
```powershell
py -m venv .venv
.venv\\Scripts\\Activate.ps1
```

macOS/Linux:
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure MySQL
The default local settings are `localhost`, user `root`, blank password, and database `attendance_db`. If your MySQL account has a password, set the environment variables before running the app.

Windows PowerShell example:
```powershell
$env:DB_HOST="localhost"
$env:DB_USER="root"
$env:DB_PASSWORD="your_mysql_password"
$env:DB_NAME="attendance_db"
$env:DB_PORT="3306"
```

macOS/Linux example:
```bash
export DB_HOST=localhost
export DB_USER=root
export DB_PASSWORD='your_mysql_password'
export DB_NAME=attendance_db
export DB_PORT=3306
```

The app creates the database and tables on startup, so the MySQL account needs permission to create a database and tables. Alternatively, run `database/database.sql` in MySQL Workbench first. Keep the app's DB settings consistent with your MySQL setup.

### 5. Start the application
```bash
python app.py
```
Open http://127.0.0.1:5000 in your browser.

## Verify in MySQL Workbench

```sql
USE attendance_db;
SHOW TABLES;
SELECT * FROM Student;
SELECT * FROM Subject;
SELECT * FROM Attendance;
```

## Push to GitHub

Create an empty repository on GitHub. In the terminal, from this project folder:

```bash
git init
git add .
git commit -m "Add Attendance Management System"
git branch -M main
git remote add origin https://github.com/YOUR-USERNAME/YOUR-REPOSITORY.git
git push -u origin main
```

Replace the URL with your own repository URL. Do not commit your actual MySQL password or other secrets.

## Deployment notes

This application needs a **reachable MySQL server**. A local MySQL server on your laptop is not reachable by a hosted app once deployed. Create/provision a MySQL database accessible to your hosting service, then set these environment variables in the hosting dashboard:

- `DB_HOST`
- `DB_PORT`
- `DB_NAME`
- `DB_USER`
- `DB_PASSWORD`

The included `Procfile` is for hosts that support Procfile-based Python web apps. Some hosts may require a platform-specific start command such as `gunicorn app:app`; install Gunicorn if the platform uses it (`pip install gunicorn`, then add `gunicorn` to `requirements.txt`). Check your chosen host's current Python and MySQL support before deploying. Never put database credentials in public GitHub files.

## DBMS concepts to explain

- **Primary key (PK):** uniquely identifies each row.
- **Foreign key (FK):** links Attendance to Student and Subject.
- **INSERT:** adds a student, subject or attendance record.
- **SELECT:** displays rows and creates joined attendance reports.
- **UPDATE:** edits student details or attendance.
- **JOIN:** combines related data from the three tables.
- **Attendance percentage:** `(present classes / total classes) * 100`.
