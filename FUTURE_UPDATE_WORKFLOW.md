# Future Code Update and Database Update Guide

This file explains how to safely continue future work in this Flask project when models, routes, services, templates, database tables, or dependencies are updated.

It also explains the purpose of `app/commands.py`, whether it is mandatory, and how to handle end-to-end setup when code changes in the future.

## 1. Purpose of `app/commands.py`

File:
- `app/commands.py`

This file contains custom Flask CLI commands for project setup and database handling.

Current commands:
- `create-db`
- `init-db`
- `seed-admin`
- `reset-db`

### Why it is useful

It keeps important setup and maintenance tasks outside normal web routes.

Benefits:
- easier project setup for new machines
- easier PostgreSQL database creation
- easier admin seeding
- easier database rebuild during testing
- keeps startup logic clean
- avoids writing manual SQL every time

### Is `commands.py` mandatory?

No, it is not mandatory for Flask itself.

Flask can run without `commands.py`.

But for this project it is strongly recommended because:
- PostgreSQL setup becomes easier
- migrations become easier to apply
- admin seeding becomes repeatable
- team members can use the same commands everywhere

So:
- mandatory for Flask: no
- practically useful for this project: yes

## 2. What Each Command Does

### `create-db`

Creates the PostgreSQL database if it does not already exist.

Use when:
- new machine setup
- new server setup
- new PostgreSQL database setup

Command:

```powershell
python -m flask --app run.py create-db
```

### `init-db`

Applies migrations and ensures the default admin account exists.

Use when:
- first project setup
- after database creation
- when a fresh environment is being prepared

Command:

```powershell
python -m flask --app run.py init-db
```

### `seed-admin`

Creates the default admin user if missing.

Use when:
- admin account is not yet created
- database exists but admin user is missing

Command:

```powershell
python -m flask --app run.py seed-admin
```

### `reset-db`

Drops current tables, runs migrations again, and recreates the admin account.

Use when:
- local database is broken
- schema is badly inconsistent in development
- you want a clean rebuild in a safe development environment

Command:

```powershell
python -m flask --app run.py reset-db
```

Important:
- do not use `reset-db` on live production unless you fully understand the data loss impact

## 3. End-to-End Setup on a New Machine

### Step 1. Open the project folder

```powershell
cd D:\Jaswanth-Personal\ModeAlpha
```

Or the current workspace folder you are using.

### Step 2. Create or activate virtual environment

If not created:

```powershell
python -m venv .venv
```

Activate:

```powershell
.\.venv\Scripts\Activate.ps1
```

### Step 3. Install dependencies

```powershell
pip install --upgrade pip
pip install -r requirements.txt
```

### Step 4. Set PostgreSQL environment values

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

### Step 5. Create database if needed

```powershell
python -m flask --app run.py create-db
```

### Step 6. Apply schema and seed admin

```powershell
python -m flask --app run.py init-db
```

### Step 7. Run the application

```powershell
python run.py
```

## 4. If You Change Only Frontend or Non-Database Code

Examples:
- templates
- CSS
- JavaScript
- routes only
- controllers only
- services only
- simple validation or UI changes

Procedure:

### 1. Pull latest code

```powershell
git pull origin development
```

### 2. Activate environment

```powershell
.\.venv\Scripts\Activate.ps1
```

### 3. Install packages if `requirements.txt` changed

```powershell
pip install -r requirements.txt
```

### 4. Run the app

```powershell
python run.py
```

No database migration is needed if models did not change.

## 5. If You Change Models or Database Structure

Examples:
- adding new table
- adding new column
- removing column
- changing relationship
- adding soft delete flag
- adding active status field
- changing default values

This requires a migration.

### Safe procedure

### 1. Pull latest code

```powershell
git pull origin development
```

### 2. Activate environment

```powershell
.\.venv\Scripts\Activate.ps1
```

### 3. Install packages if needed

```powershell
pip install -r requirements.txt
```

### 4. Update model files

Examples:
- `app/models/user.py`
- `app/models/mock_test.py`
- `app/models/question.py`
- `app/models/attempt.py`
- `app/models/result.py`

### 5. Update related business code

Usually model updates also need changes in:
- routes
- controllers
- services
- templates
- forms / validation
- reports
- AJAX responses

### 6. Create migration file

```powershell
python -m flask --app run.py db migrate -m "Describe your schema change"
```

Example:

```powershell
python -m flask --app run.py db migrate -m "Add is_active and delete_flag to users"
```

### 7. Review generated migration file

Check the new file inside:
- `migrations/versions/`

Make sure the migration matches your actual model changes.

### 8. Apply migration to database

```powershell
python -m flask --app run.py db upgrade
```

### 9. Verify in pgAdmin

Open pgAdmin and check:
- database exists
- table exists
- new column exists
- data types look correct
- constraints look correct

### 10. Run and test the app

```powershell
python run.py
```

Then test affected screens and workflows.

## 6. If Migration Is Wrong

Sometimes generated migration files are not perfect.

If needed:
- edit the generated migration manually
- then run upgrade again

If this is only local development and safe to rebuild:

```powershell
python -m flask --app run.py reset-db
```

Use this carefully because it rebuilds tables.

## 7. If Someone Else Updated the Code

When another developer updated models, routes, or services:

### 1. Pull latest branch

```powershell
git pull origin development
```

### 2. Activate environment

```powershell
.\.venv\Scripts\Activate.ps1
```

### 3. Install any new package

```powershell
pip install -r requirements.txt
```

### 4. Apply latest migrations

```powershell
python -m flask --app run.py db upgrade
```

### 5. Run application

```powershell
python run.py
```

This is the normal procedure when code changed and the database schema was also updated by someone else.

## 8. When Routes, Services, and Models Are Updated Together

That is very common in this project.

A usual sequence is:

1. update model
2. update service logic
3. update controller handling
4. update route mapping if needed
5. update templates or AJAX scripts
6. create migration if the model changed
7. apply migration
8. test from browser and pgAdmin

This project is modular, so future work is easier because logic is separated clearly:
- models -> database structure
- services -> business logic
- controllers -> request handling
- routes -> URL mapping
- templates/static -> UI

## 9. Database Table Update Procedure

This is the important end-to-end table update flow.

### Example case

Suppose you add a new column to `users` table called `last_login_at`.

### Step-by-step

1. Update `app/models/user.py`
2. Save code
3. Run:

```powershell
python -m flask --app run.py db migrate -m "Add last_login_at to users"
```

4. Review generated migration inside `migrations/versions/`
5. Apply:

```powershell
python -m flask --app run.py db upgrade
```

6. Open pgAdmin and confirm the new column exists in `users`
7. Update service/controller/template code if that field is used in UI or logic
8. Run the app and test

## 10. pgAdmin Verification Procedure

After any database-related update:

1. Open pgAdmin
2. Connect to PostgreSQL server
3. Open your database
4. Go to `Schemas -> public -> Tables`
5. Open the table
6. Check columns and data
7. If needed, run SQL in Query Tool

Example queries:

```sql
SELECT * FROM users;
```

```sql
SELECT * FROM mock_tests;
```

```sql
SELECT * FROM questions;
```

## 11. If Requirements Change in Future

If a new Python package is added:

### 1. Install it locally

```powershell
pip install package_name
```

### 2. Update requirements file

```powershell
pip freeze > requirements.txt
```

If you want a cleaner requirements file, update only the needed package lines manually instead of freezing everything.

### 3. Commit the code and requirements changes

```powershell
git add .
git commit -m "Added package_name dependency"
git push origin development
```

## 12. Recommended Safe Workflow for Future Updates

### If code only changed

```text
Pull code
Activate .venv
Install requirements if needed
Run app
Test
```

### If model/database changed

```text
Pull code
Activate .venv
Install requirements if needed
Run db upgrade
Run app
Check in pgAdmin
Test
```

### If you are the one introducing database changes

```text
Update model
Update service/controller/routes/templates
Create migration
Review migration
Run db upgrade
Test in browser
Verify in pgAdmin
Commit and push
```

## 13. Summary

### `commands.py`
- not mandatory for Flask
- very useful for this project
- simplifies database and admin setup

### If future code updates happen
- update related files carefully
- apply migrations only when models change
- run `db upgrade` after pulling schema changes
- verify database in pgAdmin

### If future database table changes happen
- change models first
- create migration
- apply migration
- verify in pgAdmin
- test end to end

This gives a repeatable and beginner-friendly workflow for maintaining the project in future.

## 14. Change Log Tutorial Entry

### 09 July 2026 - Re-Test, Attempt Labels, and Question Resolution Flow

This section explains a real update done in this project and how to repeat this style of work in future.

### Functional changes added

- completed tests now show a `Re-Test` action
- each submitted result is labeled as `1st Attempt`, `2nd Attempt`, and so on
- user result history shows attempt labels
- admin test drill-down and user drill-down reports show attempt labels
- test-wise summary now separates:
  - total attempts
  - unique users attended
- each question now supports `Leave as Un-Answer`
- `Final Submit` becomes visible only after all questions are resolved

### Files involved in this update

- `app/utils/helpers.py`
  - added reusable helpers for unanswered markers and attempt label formatting
- `app/services/mock_test_service.py`
  - updated attempt creation, resume flow, answer saving, result preparation, and final-submit validation
- `app/services/report_service.py`
  - updated attempt counting and unique-user counting logic for reports
- `app/controllers/test_controller.py`
  - updated flash message handling for normal start, resume, and re-test
- `app/controllers/api_controller.py`
  - expanded JSON response from answer autosave API
- `app/static/js/test_engine.js`
  - updated autosave, unanswered-mark handling, palette status updates, and final-submit visibility
- `app/templates/mock_tests/question.html`
  - added unanswered button and final-submit note
- `app/templates/partials/question_palette.html`
  - updated palette state metadata
- `app/templates/user/test_list.html`
  - updated start/resume/re-test/result actions
- `app/templates/user/results.html`
  - added attempt column
- `app/templates/user/result_detail.html`
  - added attempt display
- `app/templates/admin/reports.html`
  - added attempts column in test-wise report
- `app/templates/admin/test_report_detail.html`
  - added attempt details and attempts summary
- `app/templates/admin/user_report_detail.html`
  - added attempt column

### Was migration needed?

No.

Reason:
- no new column
- no new table
- no changed relationship
- no changed database constraint

So the correct procedure for this type of update is:

1. update services
2. update controllers
3. update templates and JavaScript
4. run the app
5. test in browser
6. verify report output

### If a similar future update needs a database change

Use this procedure:

1. update model files in `app/models/`
2. update related service/controller/template files
3. create migration:

```powershell
python -m flask --app run.py db migrate -m "Describe schema change"
```

4. review the new file inside `migrations/versions/`
5. apply it:

```powershell
python -m flask --app run.py db upgrade
```

6. verify in pgAdmin
7. run browser testing

### Practical lesson from this update

Before creating a migration, first ask:

- is the database structure really changing?
- or only the business logic and UI behavior are changing?

If only logic/UI changes, migration is not needed.
