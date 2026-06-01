# PostgreSQL and pgAdmin Setup

This guide shows how to run `Mock-Test` with PostgreSQL and inspect everything in pgAdmin.

## 1. Install PostgreSQL and pgAdmin

- Install PostgreSQL on your machine.
- Install pgAdmin if it did not come with your PostgreSQL installation.
- Remember the password you set for the `postgres` user.

## 2. Create a database in pgAdmin

1. Open pgAdmin.
2. Expand `Servers`.
3. Open your local PostgreSQL server.
4. Right-click `Databases`.
5. Click `Create` -> `Database...`.
6. Enter `mock_test` as the database name.
7. Keep the owner as `postgres` unless you created another database user.
8. Click `Save`.

## 3. Set environment variables in PowerShell

Open PowerShell in the project folder and run:

```powershell
.\venv\Scripts\Activate.ps1
$env:POSTGRES_HOST="127.0.0.1"
$env:POSTGRES_PORT="5432"
$env:POSTGRES_DB="mock_test"
$env:POSTGRES_USER="postgres"
$env:POSTGRES_PASSWORD="your_postgres_password"
$env:SECRET_KEY="change-this-in-production"
```

If you prefer one full connection string instead, use:

```powershell
$env:DATABASE_URL="postgresql+psycopg2://postgres:your_postgres_password@127.0.0.1:5432/mock_test"
```

## 4. Install dependencies

```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## 5. Create tables with migrations

If you did not create the database manually in pgAdmin, create it now from the project:

```powershell
python -m flask --app run.py create-db
```

Then apply migrations:

```powershell
python -m flask --app run.py init-db
```

This will:

- apply the checked-in Alembic migrations
- create all tables
- create the default admin account if it does not exist

## 6. Run the Flask app

```powershell
python run.py
```

Open [http://127.0.0.1:5000](http://127.0.0.1:5000)

Default admin login:

- Username: `admin`
- Password: `Admin@123`

## 7. View tables in pgAdmin

In pgAdmin:

1. Expand `Servers`.
2. Expand your PostgreSQL server.
3. Expand `Databases`.
4. Expand `mock_test`.
5. Expand `Schemas`.
6. Expand `public`.
7. Expand `Tables`.

You should see:

- `alembic_version`
- `users`
- `mock_tests`
- `questions`
- `attempts`
- `results`

## 8. View table data in pgAdmin

To inspect rows:

1. Right-click a table such as `users`.
2. Click `View/Edit Data`.
3. Choose `All Rows`.

Repeat for:

- `mock_tests`
- `questions`
- `attempts`
- `results`

## 9. Useful SQL queries in pgAdmin Query Tool

Open the `Query Tool` and run:

```sql
SELECT table_name
FROM information_schema.tables
WHERE table_schema = 'public'
ORDER BY table_name;
```

```sql
SELECT id, username, email, role, is_approved
FROM users
ORDER BY id;
```

```sql
SELECT id, title, total_questions, time_limit_minutes, is_active
FROM mock_tests
ORDER BY id;
```

```sql
SELECT id, mock_test_id, question_order, correct_answer
FROM questions
ORDER BY id;
```

```sql
SELECT id, user_id, mock_test_id, status, started_at, submitted_at
FROM attempts
ORDER BY id;
```

```sql
SELECT id, user_id, mock_test_id, obtained_marks, percentage
FROM results
ORDER BY id;
```

## 10. Reset the schema during development

If you want to clear the current PostgreSQL database and rebuild all tables:

```powershell
python -m flask --app run.py reset-db
```

## 11. After making model changes

When you change models, run:

```powershell
python -m flask --app run.py db migrate -m "Describe your schema change"
python -m flask --app run.py db upgrade
```

Refresh pgAdmin and check the updated tables.
