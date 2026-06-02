# ModeAlpha

ModeAlpha is a production-structured Flask web application for creating, managing, and attending mock tests. It uses function-based Flask routes, layered architecture, PostgreSQL, SQLAlchemy ORM, Flask-Migrate, Jinja2 templates, Bootstrap 5, session authentication, AJAX interactions, and Word question import.

The project now includes admin and user workflows, approval-based login, pause/resume test support, question navigation status colors, paginated reports, soft-delete handling, and PostgreSQL-first setup for pgAdmin usage.

## Highlights

- Flask app factory with Blueprints
- Function-based routes only
- Layered structure: Routes -> Controllers -> Services -> Models
- PostgreSQL + SQLAlchemy ORM + Flask-Migrate
- Session-based authentication with role-based access
- Admin approval flow for new users
- Admin mock test creation, edit, Word import, and soft delete
- User test engine with one-question-per-page navigation
- Autosave answers using AJAX
- Pause and resume test attempts with remaining-time tracking
- Question palette colors:
  - Green = answered
  - Red = visited but left blank
  - No color = not visited yet
- Paginated reports and tables with 5 records per page
- Admin settings module for activate, deactivate, and soft delete of users
- Confirmation prompts and success/error alerts for important actions
- Auto-closing flash messages after 5 seconds

## Tech Stack

- Python
- Flask
- PostgreSQL
- SQLAlchemy ORM
- Flask-Migrate
- Jinja2 Templates
- Bootstrap 5
- HTML / CSS / JavaScript
- Fetch API with `jsonify()`
- Werkzeug password hashing

## Roles

### Admin

Admin can:
- Approve registered users
- Create, edit, and soft-delete mock tests
- Upload `.docx` question files
- View dashboard analytics
- View approved users report
- View user-wise marks report
- View test-wise report with detailed attendance view
- Activate, deactivate, or soft-delete user accounts from Settings

### User

User can:
- Register and wait for admin approval
- Login after approval
- Edit profile and change password
- View available tests
- Start, pause, resume, and submit tests
- Review results and performance

## Current Test Engine Behavior

- One question is shown per page
- Previous / Next / Final Submit navigation is available
- Answers are saved during navigation
- Timer counts down during active attempts
- Pause freezes the timer and allows later resume
- Final submit shows a confirmation prompt
- Question navigation box colors:
  - Answered: green
  - Visited and blank: red
  - Not visited: neutral

## Soft Delete Behavior

The project now uses soft delete instead of immediate database removal for important records.

- Tests are marked with `delete_flag = 'Y'` instead of being fully removed
- Users are marked with `delete_flag = 'Y'` instead of being fully removed
- Normal lists and reports only show active, non-deleted records
- This keeps future audit/reference data available in the database

## Default Admin Login

Default admin user is created from environment variables during database initialization.

Default fallback values:
- Username: `admin`
- Email: `admin@example.com`
- Password: `Admin@123`
- Mobile: `9999999999`

Change these in environment variables before first setup if needed.

## Environment Variables

You can configure the project using these environment variables:

- `POSTGRES_HOST`
- `POSTGRES_PORT`
- `POSTGRES_DB`
- `POSTGRES_USER`
- `POSTGRES_PASSWORD`
- `POSTGRES_MAINTENANCE_DB`
- `DATABASE_URL`
- `SECRET_KEY`
- `SESSION_TIMEOUT_MINUTES`
- `DEFAULT_ADMIN_USERNAME`
- `DEFAULT_ADMIN_EMAIL`
- `DEFAULT_ADMIN_PASSWORD`
- `DEFAULT_ADMIN_MOBILE`

If `DATABASE_URL` is not provided, the project builds a PostgreSQL connection using the `POSTGRES_*` values.

## PostgreSQL Default Connection

By default, the app uses a PostgreSQL connection in this format:

```text
postgresql+psycopg2://<POSTGRES_USER>:<POSTGRES_PASSWORD>@<POSTGRES_HOST>:<POSTGRES_PORT>/<POSTGRES_DB>
```

Example local setup:

```powershell
$env:POSTGRES_HOST="127.0.0.1"
$env:POSTGRES_PORT="5432"
$env:POSTGRES_DB="mock_test"
$env:POSTGRES_USER="postgres"
$env:POSTGRES_PASSWORD="your_postgres_password"
```

## Project Folders

### `.venv`

This is the Python virtual environment for the project.
- Recommended
- Keeps project packages isolated
- Only one environment folder is needed

### `migrations`

This folder is used by Flask-Migrate / Alembic.
- Recommended for schema tracking
- Needed for `flask db migrate` and `flask db upgrade`
- Helps safely apply future database changes

### `instance`

This folder is not mandatory, but it is good practice in Flask.
It is commonly used for:
- uploads
- runtime files
- environment-specific app data

In this project it can still be useful for uploaded question documents and local runtime storage.

## Install and Run

From the project folder:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install --upgrade pip
pip install -r requirements.txt
```

Set PostgreSQL environment variables:

```powershell
$env:POSTGRES_HOST="127.0.0.1"
$env:POSTGRES_PORT="5432"
$env:POSTGRES_DB="mock_test"
$env:POSTGRES_USER="postgres"
$env:POSTGRES_PASSWORD="your_postgres_password"
$env:POSTGRES_MAINTENANCE_DB="postgres"
$env:SECRET_KEY="change-this-secret"
$env:SESSION_TIMEOUT_MINUTES="30"
```

Create the database if needed:

```powershell
python -m flask --app run.py create-db
```

Initialize schema and seed admin:

```powershell
python -m flask --app run.py init-db
```

Run the application:

```powershell
python run.py
```

Open:

- http://127.0.0.1:5000

## Database Commands

### Create database

```powershell
python -m flask --app run.py create-db
```

### Initialize schema and default admin

```powershell
python -m flask --app run.py init-db
```

### Seed admin only

```powershell
python -m flask --app run.py seed-admin
```

### Reset database

```powershell
python -m flask --app run.py reset-db
```

### Create new migration after model changes

```powershell
python -m flask --app run.py db migrate -m "Describe your change"
```

### Apply migrations

```powershell
python -m flask --app run.py db upgrade
```

## Important Migration Note

If you pulled recent changes, run this once before using the app:

```powershell
python -m flask --app run.py db upgrade
```

Recent schema changes include support for:
- pause / resume tracking
- visited question tracking
- active user status
- delete flags for soft delete

## Supported Word Question Import Formats

The importer supports both question styles below.

### Format 1: Answer under each question

```text
1. What is the capital of India?
A. Mumbai
B. Delhi
C. Chennai
D. Kolkata
ANSWER: B
```

### Format 2: Final answer key at the end

```text
1. Question one
A. Option A
B. Option B
C. Option C
D. Option D

2. Question two
A. Option A
B. Option B
C. Option C
D. Option D

ANSWER KEY
1-2:
B, D
```

The parser also supports common variations like:
- `A.` or `A)` option formats
- answer ranges like `1-10`, `11-20`
- section headings inside Word documents

## Reports Available

### Admin Reports

- Approved Users Report
- User-wise Marks Report
- Test-wise Report
- Detailed per-user attended tests view
- Detailed per-test attended users view

All report tables now support:
- 5 records per page
- page number navigation
- range summary like `Showing 1-5 of X records`

## Admin Settings Module

The admin sidebar now includes a `Settings` menu below `Reports`.

From Settings, admin can:
- search user by username
- search user by email
- search user by mobile number
- search user by numeric user id
- activate user
- deactivate user
- soft-delete user

Approved users are active by default.

## Alerts and Confirmations

Important actions now show confirmation prompts before continuing, including actions such as:
- save
- submit
- delete
- pause test
- approve user
- activate / deactivate user
- import questions

After completion, flash alerts are shown for messages like:
- saved successfully
- updated successfully
- deleted successfully
- submitted successfully

Flash messages auto-close after 5 seconds.

## Session Behavior

- Session-based login is used
- Protected pages require login
- Admin pages require admin role
- Session timeout is controlled by `SESSION_TIMEOUT_MINUTES`
- Protected responses use no-cache headers so old pages do not remain visible after session expiry

## PostgreSQL and pgAdmin

This project is now PostgreSQL-first, so you can inspect tables directly in pgAdmin.

After running setup:
- open pgAdmin
- connect to your PostgreSQL server
- open database `mock_test`
- go to `Schemas -> public -> Tables`

You should see tables like:
- `users`
- `mock_tests`
- `questions`
- `attempts`
- `results`
- `alembic_version`

Detailed PostgreSQL setup notes are available in [POSTGRESQL_SETUP.md](POSTGRESQL_SETUP.md).

## Additional Guides

- [Project Handbook](PROJECT_HANDBOOK.md)
- [Quick Start](QUICK_START.md)
- [Git Workflow Handbook](GIT_WORKFLOW.md)
- [Future Code Update and Database Update Guide](FUTURE_UPDATE_WORKFLOW.md)
- [Commit Message Guide](COMMIT_MESSAGE_GUIDE.md)
- [Professional Commit Message Templates](COMMIT_MESSAGE_TEMPLATES.md)





