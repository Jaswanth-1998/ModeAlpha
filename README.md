# Mock-Test

Mock-Test is a production-style Flask web application for managing and attending mock tests with admin approval, Word-based question import, one-question-per-page test flow, and report dashboards.

This project is now configured for PostgreSQL by default so you can inspect data easily in pgAdmin.

## Default admin login

- Username: `admin`
- Password: `Admin@123`

Change these values in environment variables before production use:

- `POSTGRES_HOST`
- `POSTGRES_PORT`
- `POSTGRES_DB`
- `POSTGRES_USER`
- `POSTGRES_PASSWORD`
- `DEFAULT_ADMIN_USERNAME`
- `DEFAULT_ADMIN_EMAIL`
- `DEFAULT_ADMIN_PASSWORD`
- `DEFAULT_ADMIN_MOBILE`
- `SECRET_KEY`

## PostgreSQL defaults

If `DATABASE_URL` is not set, the app builds this connection automatically:

```text
postgresql+psycopg2://postgres:postgres@127.0.0.1:5432/mock_test
```

Change it with environment variables or provide a full `DATABASE_URL`.

## Install and run

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
$env:POSTGRES_HOST="127.0.0.1"
$env:POSTGRES_PORT="5432"
$env:POSTGRES_DB="mock_test"
$env:POSTGRES_USER="postgres"
$env:POSTGRES_PASSWORD="postgres"
python -m flask --app run.py create-db
python -m flask --app run.py init-db
python run.py
```

## Flask-Migrate setup

```bash
python -m flask --app run.py db upgrade
python -m flask --app run.py db migrate -m "Describe schema change"
python -m flask --app run.py seed-admin
```

## Reset the current PostgreSQL schema

If you want to clear all tables in the currently configured PostgreSQL database
and rebuild them from the checked-in migrations:

```bash
python -m flask --app run.py reset-db
```

## pgAdmin setup guide

See [POSTGRESQL_SETUP.md](/C:/Users/HP/Documents/Codex/2026-05-22/create-a-complete-production-style-flask/POSTGRESQL_SETUP.md) for the full step-by-step workflow:

- create the database in pgAdmin
- or create it with the Flask `create-db` command
- set the Flask environment variables
- run migrations
- verify `users`, `mock_tests`, `questions`, `attempts`, and `results` in pgAdmin

## Supported question import format

```text
Format 1: answer after each question

1. What is the capital of France?
A. Berlin
B. Madrid
C. Paris
D. Rome
ANSWER: C
```

```text
Format 2: final answer key at the end

1. Scientific temper means?
A) Logical thinking
B) Blind belief
C) Memory
D) None

2. Rote learning means?
A) Memorization
B) Understanding
C) Logic
D) None

ANSWER KEY
1-2:
A, A
```

Notes:

- Both `A.` and `A)` style options are accepted.
- Section headings like `UNIT I`, `PART A`, or `50 IMPORTANT MCQs TEST` are ignored.
- The answer key can be given as ranges like `1-10:` followed by `A, B, C, ...`.
