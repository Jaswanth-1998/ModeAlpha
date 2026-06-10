# Quick Start

This file is the short day-to-day guide for running and updating the project.

## Project Folder

```powershell
cd D:\Jaswanth-Personal\ModeAlpha
```

Or open the current project folder you are using.

## 1. Activate Virtual Environment

```powershell
.\.venv\Scripts\Activate.ps1
```

## 2. Install Dependencies

Run this when setting up for the first time or after `requirements.txt` changes.

```powershell
pip install -r requirements.txt
```

## 3. Set PostgreSQL Details

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

## 4. First-Time Database Setup

Create database:

```powershell
python -m flask --app run.py create-db
```

Initialize tables and default admin:

```powershell
python -m flask --app run.py init-db
```

## 5. Run the Project

```powershell
python run.py
```

Open in browser:
- http://127.0.0.1:5000

## 6. Default Admin Login

- Username: `admin`
- Password: `Admin@123`

## 7. Daily Start Commands

Use these most often:

```powershell
.\.venv\Scripts\Activate.ps1
python -m flask --app run.py db upgrade
python run.py
```

## 8. If You Pulled Latest Code

```powershell
git pull origin development
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python -m flask --app run.py db upgrade
python run.py
```

## 9. If You Changed Models / Database

Create migration:

```powershell
python -m flask --app run.py db migrate -m "Describe your schema change"
```

Apply migration:

```powershell
python -m flask --app run.py db upgrade
```

## 10. If Database Needs Clean Rebuild

```powershell
python -m flask --app run.py reset-db
```

Use this only in safe development/testing situations.

## 11. Useful Admin Commands

Create database:

```powershell
python -m flask --app run.py create-db
```

Seed admin again:

```powershell
python -m flask --app run.py seed-admin
```

## 12. Daily Git Commands

Switch to development:

```powershell
git checkout development
```

Pull latest:

```powershell
git pull origin development
```

Commit and push:

```powershell
git add .
git commit -m "Your update message"
git push origin development
```

## 13. When to Run `db upgrade`

Run this whenever:
- latest code was pulled from another machine or developer
- models changed
- migration files were added
- new columns/tables were introduced

Command:

```powershell
python -m flask --app run.py db upgrade
```

## 14. Main Reference Files

- `README.md`
- `POSTGRESQL_SETUP.md`
- `GIT_WORKFLOW.md`
- `FUTURE_UPDATE_WORKFLOW.md`

## 15. Quick Safe Workflow

```text
Pull latest code
Activate .venv
Install requirements if needed
Run db upgrade
Start app
Test in browser
Check pgAdmin if database changed
```
***
(Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned) ; (& c:\Users\HP\Documents\Codex\2026-05-22\ModeAlpha\.venv\Scripts\Activate.ps1)
***