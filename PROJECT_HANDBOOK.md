# ModeAlpha Project Handbook

This handbook explains the structure of the ModeAlpha project, what each important file and folder does, how migrations work, what `commands.py`, `extensions.py`, and `instance` are used for, which folders are optional or recommended, and how to debug Flask projects when errors happen.

Use this as a reference both for understanding this project and for building future Flask projects manually without AI assistance.

---

## 1. What This Project Is

ModeAlpha is a Flask web application with:
- Flask app factory pattern
- Blueprints
- function-based routes
- layered architecture
- PostgreSQL with SQLAlchemy ORM
- Flask-Migrate / Alembic migrations
- Jinja2 templates
- Bootstrap UI
- session-based authentication
- admin and user roles

The main code flow is:

```text
Browser Request
-> Route
-> Controller
-> Service
-> Model / Database
-> Controller response
-> Template or JSON response
```

That separation is one of the most important ideas to learn from this project.

---

## 2. Root Folder Structure

Current root structure:

```text
ModeAlpha/
├── .venv/
├── app/
├── migrations/
├── COMMIT_MESSAGE_GUIDE.md
├── COMMIT_MESSAGE_TEMPLATES.md
├── FUTURE_UPDATE_WORKFLOW.md
├── GIT_WORKFLOW.md
├── POSTGRESQL_SETUP.md
├── QUICK_START.md
├── README.md
├── requirements.txt
├── run.py
└── __pycache__/
```

### Root file purpose

#### `.venv/`
Python virtual environment.

Used for:
- installing project-specific packages
- avoiding conflicts with other Python projects

Status:
- not mandatory for Python itself
- strongly recommended for every real project

#### `app/`
Main application source code.

Status:
- mandatory for this project structure

#### `migrations/`
Database migration files managed by Flask-Migrate / Alembic.

Status:
- not mandatory for Flask itself
- strongly recommended for real database projects
- practically required if you want safe schema updates

#### `README.md`
Main project overview and setup guide.

#### `requirements.txt`
List of Python packages used by the project.

#### `run.py`
Small project entry point that starts the Flask app.

#### `__pycache__/`
Python-generated cache folder.

Status:
- optional
- auto-generated
- should not be committed normally

---

## 3. `run.py`

File:
- `run.py`

Current content:
- imports `create_app()` from `app`
- creates the app object
- runs Flask in debug mode when executed directly

Why it exists:
- gives a simple starting point to launch the app
- used by `python run.py`
- also useful for Flask CLI commands via `--app run.py`

Typical role in future projects:
- simple launcher file
- often very small

Status:
- recommended
- not strictly mandatory if you use another startup pattern, but common and useful

---

## 4. `app/` Folder Overview

This is the most important folder.

```text
app/
├── __init__.py
├── commands.py
├── extensions.py
├── config/
├── controllers/
├── instance/
├── middleware/
├── models/
├── routes/
├── services/
├── static/
├── templates/
└── utils/
```

---

## 5. `app/__init__.py`

This file builds the Flask app.

### What it does

- creates the Flask app object
- loads configuration from `app/config/settings.py`
- ensures required directories exist
- initializes extensions (`db`, `migrate`)
- imports models so SQLAlchemy metadata is available
- registers custom CLI commands from `commands.py`
- registers a `before_request` hook to load the logged-in user
- injects `current_user` into templates
- sets no-cache headers for authenticated pages
- registers all Blueprints

### Why it matters

This is the central application bootstrap file.

If this file is broken:
- the app will not start correctly
- routes may not register
- database extensions may not initialize
- commands may not work

### Status

- mandatory for this app factory structure
- strongly recommended for scalable Flask apps

---

## 6. `app/extensions.py`

File:
- `app/extensions.py`

Current purpose:
- stores shared extension objects in one place

Current content:
- `db = SQLAlchemy()`
- `migrate = Migrate()`

### Why this file is useful

Instead of creating SQLAlchemy or Migrate directly inside many files, you create them once here and initialize them later inside `create_app()`.

That gives:
- clean separation
- easier testing
- no circular import mess
- reusable app factory pattern

### How it works

Step 1:
- define uninitialized extension objects in `extensions.py`

Step 2:
- inside `app/__init__.py`, call:
  - `db.init_app(app)`
  - `migrate.init_app(app, db, ...)`

This pattern is standard Flask practice.

### Is it mandatory?

- not mandatory for tiny apps
- strongly recommended for any app with multiple files

### Future usage

If you add more shared extensions later, they can also live here, for example:
- `login_manager`
- `mail`
- `bcrypt`
- `cache`
- `socketio`

---

## 7. `app/commands.py`

This file defines custom Flask CLI commands.

### Current commands

- `create-db`
- `init-db`
- `seed-admin`
- `reset-db`

### What each command does

#### `create-db`
Creates the PostgreSQL database if it does not already exist.

Use when:
- setting up the project on a new machine
- setting up a new server
- creating the PostgreSQL database for the first time

#### `init-db`
Runs migrations and ensures the default admin account exists.

Use when:
- first-time project setup
- after creating a fresh database

#### `seed-admin`
Creates the default admin user if it is missing.

Use when:
- admin account does not exist
- you want to ensure the admin record is available

#### `reset-db`
Drops existing tables and rebuilds the database from migrations.

Use when:
- local development database is broken
- schema has become inconsistent locally
- you need a clean rebuild during development

### Why `commands.py` is useful

Benefits:
- setup becomes repeatable
- no need to run manual SQL every time
- easier onboarding for new developers
- safer and cleaner than putting setup logic inside routes
- works well with PostgreSQL + Flask-Migrate

### Is it mandatory?

- not mandatory for Flask itself
- very useful for real projects
- strongly recommended in this project

### How it is connected

`app/__init__.py` calls:

```python
register_commands(app)
```

That registers the commands with Flask CLI.

### Example usage

```powershell
python -m flask --app run.py create-db
python -m flask --app run.py init-db
python -m flask --app run.py seed-admin
python -m flask --app run.py reset-db
```

---

## 8. `app/config/`

Files:
- `app/config/__init__.py`
- `app/config/settings.py`

### `settings.py`

This is the main configuration file.

### What it does

- builds the database URL
- defines base config values
- defines development and production config classes
- stores paths like `INSTANCE_DIR` and `UPLOAD_DIR`
- sets session timeout settings
- sets default admin values
- ensures important local directories exist

### Important values in this file

- `SECRET_KEY`
- `SQLALCHEMY_DATABASE_URI`
- `POSTGRES_MAINTENANCE_DB`
- `INSTANCE_DIR`
- `UPLOAD_DIR`
- `SESSION_TIMEOUT_MINUTES`
- `PERMANENT_SESSION_LIFETIME`
- `DEFAULT_ADMIN_USERNAME`
- `DEFAULT_ADMIN_EMAIL`
- `DEFAULT_ADMIN_PASSWORD`
- `DEFAULT_ADMIN_MOBILE`

### Why it matters

If you want to change:
- DB connection
- upload location
- session timeout
- admin defaults
- debug mode

this is one of the first files to check.

### Status

- mandatory for this structure
- some form of settings/config file is strongly recommended in every scalable project

---

## 9. `app/routes/`

Files:
- `admin_routes.py`
- `api_routes.py`
- `auth_routes.py`
- `main_routes.py`
- `test_routes.py`
- `user_routes.py`
- `__init__.py`

### Purpose of the routes layer

Routes map URLs to controller functions.

Example idea:

```text
/admin/tests -> admin_routes.py -> admin_controller.test_list()
```

### File-by-file purpose

#### `main_routes.py`
Public pages like home/landing page.

#### `auth_routes.py`
Authentication routes such as:
- register
- login
- profile
- logout

#### `admin_routes.py`
Admin panel routes such as:
- dashboard
- pending users
- tests
- reports
- settings

#### `user_routes.py`
User dashboard and result routes.

#### `test_routes.py`
Mock test engine routes:
- start test
- view question page
- move through test
- submit flow

#### `api_routes.py`
AJAX / JSON routes for browser-side actions.
Examples:
- approve/reject users
- save answers
- submit attempts
- dashboard metrics

### Why routes should stay thin

Routes should:
- receive request
- call controller
- return response

Routes should not contain heavy business logic.

### Status

- mandatory in this architecture
- Blueprints are strongly recommended for medium and large apps

---

## 10. `app/controllers/`

Files:
- `admin_controller.py`
- `api_controller.py`
- `auth_controller.py`
- `main_controller.py`
- `test_controller.py`
- `user_controller.py`
- `__init__.py`

### Purpose of controllers

Controllers handle request/response logic.

Typical controller responsibilities:
- read form data
- call services
- handle exceptions
- flash messages
- redirect to another page
- return `render_template()` or `jsonify()`

### File-by-file purpose

#### `main_controller.py`
Controls public/non-auth homepage rendering.

#### `auth_controller.py`
Handles:
- registration
- login
- logout
- profile updates

#### `admin_controller.py`
Handles admin pages:
- dashboard
- test CRUD pages
- report pages
- settings pages
- upload question page

#### `user_controller.py`
Handles user pages:
- dashboard
- test list
- results

#### `test_controller.py`
Handles test-taking page flow.

#### `api_controller.py`
Handles AJAX / JSON responses.

### Why controllers are useful

Without controllers, routes become very large.

Controllers give a clean middle layer between:
- URL routing
- business/service logic

### Status

- optional in tiny apps
- strongly recommended in structured apps

---

## 11. `app/services/`

Files:
- `admin_service.py`
- `auth_service.py`
- `docx_service.py`
- `mock_test_service.py`
- `report_service.py`
- `__init__.py`

### Purpose of services

Services contain business logic.

This is one of the most important architecture ideas in the project.

### File-by-file purpose

#### `auth_service.py`
Authentication and profile business rules.
Examples:
- register user
- validate duplicate email/mobile/username
- login validation
- password hashing
- profile update
- session helper usage

#### `admin_service.py`
Admin business rules.
Examples:
- get admin dashboard metrics
- approve/reject users
- create/update/delete tests
- import questions
- manage user state in settings

#### `docx_service.py`
Word document parsing logic.
Examples:
- read `.docx`
- extract questions/options/answers
- support answer-per-question and final-answer-key formats

#### `mock_test_service.py`
Mock test engine business rules.
Examples:
- create attempts
- save answers
- track navigation status
- pause/resume
- submit tests
- calculate result values

#### `report_service.py`
Report and analytics business rules.
Examples:
- user-wise report data
- test-wise report data
- approved users report
- detailed drill-down rows

### Why services matter

Benefits:
- business logic stays reusable
- easier testing
- thinner controllers
- easier future maintenance
- easier debugging because logic is not spread everywhere

### Status

- optional in tiny apps
- strongly recommended for real-world apps

---

## 12. `app/models/`

Files:
- `attempt.py`
- `mock_test.py`
- `question.py`
- `result.py`
- `user.py`
- `__init__.py`

### Purpose of models

Models define database tables and relationships.

### File-by-file purpose

#### `user.py`
Stores user/admin account data.
Examples:
- username
- email
- mobile number
- DOB
- password hash
- role
- approval status
- active status
- delete flag

#### `mock_test.py`
Stores mock test master details.
Examples:
- title
- description
- time limit
- marks per question
- negative marking settings
- total questions
- active/delete flags

#### `question.py`
Stores each test question and answer.
Examples:
- question text
- option A/B/C/D
- correct answer
- question order

#### `attempt.py`
Stores a user’s in-progress or submitted attempt.
Examples:
- selected answers JSON
- status
- timer tracking
- pause/resume tracking
- visited questions

#### `result.py`
Stores final computed result after test submission.
Examples:
- total questions
- correct/wrong/unanswered count
- obtained marks
- total marks
- percentage

### What models should contain

Models should mainly contain:
- columns
- relationships
- small representation helpers

Avoid putting heavy business logic directly in models.

### Status

- mandatory if using SQLAlchemy ORM

---

## 13. `app/middleware/`

Files:
- `auth_middleware.py`
- `__init__.py`

### Purpose

This folder contains request-access control helpers.

### `auth_middleware.py`
Current responsibilities:
- load logged-in user into `g.current_user`
- session timeout handling
- deleted/deactivated account check
- `login_required`
- `admin_required`
- `approved_user_required`
- redirect or JSON unauthorized/forbidden responses

### Why middleware/decorators matter

These checks are reused across many routes.
Without decorators, the same access-check code would be repeated everywhere.

### Status

- optional as a separate folder
- highly recommended if your app has reusable access rules

---

## 14. `app/utils/`

Files:
- `helpers.py`
- `pagination.py`
- `seed.py`
- `__init__.py`

### Purpose

Reusable helper functions that do not belong directly to one controller or one service.

### File-by-file purpose

#### `helpers.py`
General helper functions such as:
- normalize email/mobile
- parse bool/int/float
- JSON helpers
- timer helper functions

#### `pagination.py`
Pagination helper functions.

Current design:
- function-based, not class-based

Used for:
- page number extraction
- paginating data lists
- building page links

#### `seed.py`
Seed helper functions.

Used for:
- creating the default admin record

### Status

- optional folder
- recommended for shared helper logic

---

## 15. `app/templates/`

Main template files:
- `base.html`
- `auth_base.html`
- `home.html`

Subfolders:
- `admin/`
- `auth/`
- `mock_tests/`
- `partials/`
- `user/`

### Purpose

Jinja2 HTML templates used to render pages.

### Main template files

#### `base.html`
Main layout for authenticated pages.
Includes common layout pieces such as:
- sidebar
- navbar
- flash messages
- script/style includes

#### `auth_base.html`
Layout for login/register style pages.

#### `home.html`
Public landing page.

### `partials/`
Reusable HTML fragments.

Files include:
- `flash_messages.html`
- `navbar.html`
- `pagination.html`
- `question_palette.html`
- `sidebar.html`

Why partials are useful:
- avoid repeating markup
- easier design updates
- easier maintenance

### `admin/`
Admin page templates.

Files include:
- `dashboard.html`
- `pending_users.html`
- `reports.html`
- `settings.html`
- `test_form.html`
- `test_list.html`
- `test_report_detail.html`
- `upload_questions.html`
- `user_report_detail.html`

### `auth/`
Authentication templates.

Files include:
- `login.html`
- `register.html`
- `profile.html`

### `user/`
User templates.

Files include:
- `dashboard.html`
- `results.html`
- `result_detail.html`
- `test_list.html`

### `mock_tests/`
Templates related to test-taking flow.

Files include:
- `question.html`

### Are templates mandatory?

- yes, if server-side rendering is used
- no, if you build a pure API-only backend

---

## 16. `app/static/`

Subfolders:
- `css/`
- `js/`

### `css/style.css`
Main stylesheet.

Used for:
- project layout
- sidebar/navbar look
- cards
- buttons
- palette colors
- responsive styling

### `js/main.js`
General frontend behavior.
Examples:
- flash alert handling
- confirmation helpers
- general UI interactions

### `js/admin.js`
Admin-specific browser logic.
Examples:
- approve/reject AJAX actions
- admin metric refresh

### `js/test_engine.js`
Test page logic.
Examples:
- timer
- autosave answers
- submit via AJAX
- question navigation updates

### Status

- mandatory if your UI depends on custom CSS/JS
- static folder itself is standard and recommended in Flask

---

## 17. `app/instance/`

Current contents include:
- uploaded `.docx` files
- SQLite backup files from earlier development
- local runtime files

### Important clarification

This project now uses PostgreSQL by default, but the `instance` folder is still useful for:
- uploaded question documents
- local runtime files
- machine-specific writable storage

### Why Flask instance folder exists

Flask treats `instance` as a writable, environment-specific folder.

Typical use cases:
- SQLite DB file
- uploads
- secret local config
- cache/temp files

### In this project

`settings.py` defines:
- `INSTANCE_DIR = APP_DIR / "instance"`
- `UPLOAD_DIR = INSTANCE_DIR / "uploads"`

Then `ensure_directories()` creates them.

### Is `instance` mandatory?

- not mandatory for Flask itself
- useful if you need writable local project storage
- recommended here because uploads are used

### Can it be removed?

Yes, if:
- uploads are moved elsewhere
- no local writable runtime files are needed
- PostgreSQL is used for DB

### Should `__init__.py` be inside `instance`?

Not really required.
It is meaningful mainly for Python packages.
For an instance/runtime folder, it is optional and usually unnecessary.

---

## 18. `migrations/` Folder

This folder is used by Alembic through Flask-Migrate.

Current important files:
- `migrations/alembic.ini`
- `migrations/env.py`
- `migrations/script.py.mako`
- `migrations/README`
- `migrations/versions/*.py`

### What migration means

A migration is a step-by-step database schema change record.

Examples:
- create users table
- add new column
- remove unique constraint
- add soft delete fields

Instead of manually changing the DB each time, migration files record those changes.

---

## 19. How Migrations Work in This Project

### The main idea

1. You change SQLAlchemy model code
2. Flask-Migrate compares models with current DB state
3. It generates a new migration version file
4. You apply that version file to the database

### Important migration files

#### `migrations/env.py`
This is the Alembic execution environment.

What it does:
- connects migrations to the current Flask app
- reads DB engine from Flask-SQLAlchemy
- loads metadata from SQLAlchemy models
- configures online/offline migration execution
- skips empty autogenerate migrations

Think of `env.py` as the bridge between:
- Flask app
- SQLAlchemy models
- Alembic migration engine

#### `migrations/script.py.mako`
Template Alembic uses when creating a new migration file.

#### `migrations/versions/`
This is the most important subfolder.
Each `.py` file here represents one schema version step.

Current version files:
- `20260522_180500_initial_schema.py`
- `20260525_191500_add_pause_tracking_to_attempts.py`
- `20260525_214500_add_soft_delete_flags_and_user_status.py`
- `20260526_103000_add_visited_questions_to_attempts.py`
- `20260601_141500_drop_hard_user_unique_constraints.py`

---

## 20. How a Migration Version File Works

Example structure inside a version file:

```python
revision = "20260601_141500"
down_revision = "20260526_103000"


def upgrade():
    ...


def downgrade():
    ...
```

### Meaning of each part

#### `revision`
Unique ID of this migration file.

#### `down_revision`
The previous migration that must come before this one.

This creates a chain like:

```text
initial_schema -> pause_tracking -> soft_delete -> visited_questions -> drop_unique_constraints
```

#### `upgrade()`
What to do when moving forward.

Examples:
- create table
- add column
- drop constraint

#### `downgrade()`
What to do when rolling back.

Examples:
- drop column
- recreate constraint
- remove table

---

## 21. How Version Files Are Used by the Project

Very important point:

The application code does **not** import migration version files directly during normal page requests.

Instead:
- Alembic reads them when you run migration commands
- it decides which version files must run
- it applies their `upgrade()` or `downgrade()` functions

So the version files are used by:
- `flask db upgrade`
- `flask db downgrade`
- `init-db`
- `reset-db`

They are **not** used by:
- normal Flask route execution
- templates
- controllers
- services during regular page requests

The database stores the currently applied migration version in the `alembic_version` table.

---

## 22. Step-by-Step: How to Add a New Database Change

Example: suppose you want to add a new column `last_login_at` to the `users` table.

### Step 1. Update the model

Edit:
- `app/models/user.py`

Add the new SQLAlchemy column.

### Step 2. Activate environment

```powershell
.\.venv\Scripts\Activate.ps1
```

### Step 3. Generate migration file

```powershell
python -m flask --app run.py db migrate -m "Add last_login_at to users"
```

This creates a new file inside:
- `migrations/versions/`

### Step 4. Review the generated migration file

Open the new file and check:
- is the new column correct?
- is the type correct?
- is nullable/default behavior correct?

### Step 5. Apply the migration

```powershell
python -m flask --app run.py db upgrade
```

### Step 6. Verify in pgAdmin

Check the table structure.

### Step 7. Test in the app

Run the app and test related screens.

---

## 23. Step-by-Step: How to View Current Migration Version

### Method 1: Flask command

```powershell
python -m flask --app run.py db current
```

### Method 2: Show migration history

```powershell
python -m flask --app run.py db history
```

### Method 3: Check database table

In PostgreSQL / pgAdmin:
- open table `alembic_version`
- read the current version number

---

## 24. Step-by-Step: How to Change Version

The phrase “change version” can mean 4 different things.

### Case A: Move database to latest version

Use:

```powershell
python -m flask --app run.py db upgrade
```

This applies all pending migration files in order.

### Case B: Move database back one version

Use:

```powershell
python -m flask --app run.py db downgrade -1
```

Or downgrade to a specific revision:

```powershell
python -m flask --app run.py db downgrade 20260526_103000
```

### Case C: Create a new version file

Use:

```powershell
python -m flask --app run.py db migrate -m "Describe schema change"
```

This is the normal and safest way.

### Case D: Manually edit a version file

Possible, but only if you understand what you are doing.

Safe rule:
- you may edit the `upgrade()` / `downgrade()` logic if the migration is new and not yet shared widely
- do not casually change `revision` IDs or `down_revision` values unless you know the whole migration chain impact

### If you really change a `revision` or `down_revision`

Then you must ensure:
- this migration’s ID is still unique
- any child migration that points to it has the correct `down_revision`
- migration history remains one valid chain

This is why manual revision-ID changes are usually **not recommended**.

Better practice:
- create a new migration file instead of renaming old ones

---

## 25. Step-by-Step: How to Use Migration Files Safely

### Recommended workflow

1. change model code
2. create migration
3. review migration file
4. apply migration
5. verify in pgAdmin
6. test application
7. commit model + migration together

### Never do this casually

- do not manually edit the `alembic_version` table unless you really know why
- do not delete old migration files randomly
- do not rename migration files after they are already shared in a team
- do not skip reviewing autogenerated migration files

---

## 26. Root Cause Understanding: Why Migrations Exist

Without migrations:
- each developer must manually update DB tables
- production DB schema can drift away from code
- rollback becomes hard
- deployment becomes risky

With migrations:
- schema updates are versioned
- team members stay in sync
- deployment is repeatable
- DB changes are trackable in Git

---

## 27. Optional vs Mandatory Folders

### Usually mandatory for this project style

- `app/`
- `app/__init__.py`
- `app/routes/`
- `app/models/`
- `app/templates/`
- `requirements.txt`
- `run.py`

### Strongly recommended

- `.venv/`
- `migrations/`
- `app/config/`
- `app/controllers/`
- `app/services/`
- `app/utils/`
- `app/middleware/`
- `app/static/`
- `app/extensions.py`
- `app/commands.py`

### Optional depending on project type

- `app/instance/`
- `migrations/` if you truly do not need schema versioning
- `controllers/` layer in very tiny apps
- `services/` layer in very tiny apps
- `static/` if it is API-only
- `templates/` if frontend is separate

### Auto-generated / should not be treated as real source folders

- `__pycache__/`

---

## 28. How to Start a New Project Manually Using This Pattern

If you want to build another project yourself, this is a good manual sequence.

### Step 1. Create project folder

```powershell
mkdir MyNewProject
cd MyNewProject
```

### Step 2. Create virtual environment

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### Step 3. Install starter packages

```powershell
pip install flask flask-sqlalchemy flask-migrate psycopg2-binary python-docx
```

### Step 4. Create folder structure

```text
app/
  config/
  routes/
  controllers/
  services/
  models/
  middleware/
  utils/
  templates/
  static/
  instance/
```

### Step 5. Create these core files first

- `run.py`
- `app/__init__.py`
- `app/extensions.py`
- `app/config/settings.py`
- first model file
- first route file

### Step 6. Start with one small feature end-to-end

Example:
- home page
- user registration
- login page

Build using this flow:

```text
route -> controller -> service -> model/template
```

### Step 7. Add migrations early

```powershell
python -m flask --app run.py db init
python -m flask --app run.py db migrate -m "Initial schema"
python -m flask --app run.py db upgrade
```

### Step 8. Add commands and helpers later

Once the app grows:
- add `commands.py`
- add `middleware/`
- add `utils/`
- add `services/`

---

## 29. Debugging Handbook for Flask Projects

This section is for learning how to debug projects manually.

### Golden rule

Read errors from:
- the bottom of the traceback upward
- the first line of the error message carefully
- the file path shown in the traceback

Many beginners read the traceback top-down and get confused.

### Simple debugging workflow

1. reproduce the issue
2. read the exact error message
3. identify the file where the real app code failed
4. identify which layer failed
5. inspect input data and assumptions
6. fix one cause at a time
7. test again

---

## 30. How to Identify Which Layer Has the Problem

### If error is in `routes/`
Likely:
- wrong endpoint setup
- wrong methods list
- wrong function call

### If error is in `controllers/`
Likely:
- form/request handling problem
- wrong redirect
- missing argument
- unhandled exception from service

### If error is in `services/`
Likely:
- business logic bug
- query bug
- duplicate validation issue
- data conversion issue
- parser logic issue

### If error is in `models/`
Likely:
- wrong column type
- relationship problem
- migration mismatch

### If error is in `templates/`
Likely:
- Jinja syntax error
- variable missing
- bad file encoding
- wrong loop or condition name

### If error is in `migrations/`
Likely:
- schema mismatch
- bad generated migration
- wrong downgrade/upgrade logic

---

## 31. Common Error Types and How to Debug Them

### 1. ImportError / ModuleNotFoundError

Check:
- is the package installed?
- is the virtual environment active?
- is the import path correct?

### 2. Template errors

Check:
- template file name
- Jinja syntax
- variables passed from controller
- file encoding

### 3. Database errors

Check:
- DB connection settings
- table/column exists?
- did you run migrations?
- is model different from database?

### 4. SQLAlchemy errors

Check:
- query filters
- relationship names
- column names
- session commit logic

### 5. Migration errors

Check:
- current DB revision
- model changes
- autogenerated migration correctness
- dependency chain via `down_revision`

### 6. Authentication / session errors

Check:
- session values
- decorators
- `g.current_user`
- session timeout behavior

### 7. AJAX / API errors

Check:
- browser network tab
- JSON response body
- HTTP status code
- route URL
- method type (`GET` vs `POST`)

### 8. File upload/parser errors

Check:
- actual file content
- file extension
- path being saved
- parser assumptions
- encoding problems in templates or logs

---

## 32. Practical Debugging Techniques

### Technique 1: Read traceback carefully

Look for the first project file path such as:
- `app/services/...`
- `app/controllers/...`
- `app/templates/...`

That is usually where to start.

### Technique 2: Add temporary print statements

Examples:
- request form values
- DB query result
- selected variable state
- parser lines

Use only temporarily, then remove them.

### Technique 3: Flash or JSON debug messages

For web flows:
- flash useful messages on form errors
- return detailed JSON during development for AJAX routes

### Technique 4: Use browser DevTools

Check:
- Console tab for JS errors
- Network tab for AJAX response errors
- status codes like `400`, `401`, `403`, `500`

### Technique 5: Verify database in pgAdmin

After model or report issues:
- inspect actual rows
- check constraints
- confirm column values

### Technique 6: Compare route -> controller -> service flow

If a page breaks, ask:
- did the route reach the controller?
- did the controller call the service?
- did the service return expected data?
- did the template receive the right variable names?

### Technique 7: Use breakpoints / debugger

In VS Code you can:
- open Run and Debug
- create a Python debug configuration
- place breakpoints
- step through line by line

This is one of the best ways to learn manually.

---

## 33. Flask-Specific Debugging Tips

### Run in debug mode during development

`run.py` currently uses:

```python
app.run(debug=True)
```

That helps by:
- reloading on code changes
- showing detailed error pages

Do not use debug mode on production.

### Use Flask CLI commands

Helpful commands:

```powershell
python -m flask --app run.py routes
python -m flask --app run.py db current
python -m flask --app run.py db history
python -m flask --app run.py shell
```

These help you inspect:
- registered routes
- migration status
- DB access from Python shell

### Use SQL logging temporarily

If needed, you can temporarily set SQLAlchemy echo behavior in config to inspect generated SQL.

---

## 34. How to Debug This Project Specifically

### If login fails unexpectedly

Check:
- `auth_routes.py`
- `auth_controller.py`
- `auth_service.py`
- `auth_middleware.py`
- `users` table values in pgAdmin

### If admin/user page redirects incorrectly

Check:
- decorators in `auth_middleware.py`
- session values
- `g.current_user.role`

### If report counts look wrong

Check:
- `report_service.py`
- delete flags
- attempt/result rows in DB

### If test submission behaves wrongly

Check:
- `test_controller.py`
- `mock_test_service.py`
- `attempts` and `results` tables

### If Word import fails

Check:
- `docx_service.py`
- real extracted lines from the document
- option format
- answer-key format

### If upload page crashes before upload

Check:
- template encoding
- Jinja syntax
- `upload_questions.html`

### If settings actions fail

Check:
- template button data URLs
- `admin.js`
- `api_routes.py`
- `api_controller.py`
- `admin_service.py`

---

## 35. Recommended Learning Path From This Project

If you want to learn enough to build a project manually, study in this order:

1. `run.py`
2. `app/__init__.py`
3. `app/config/settings.py`
4. `app/extensions.py`
5. one route file
6. one controller file
7. one service file
8. one model file
9. one template file
10. `auth_middleware.py`
11. `commands.py`
12. `migrations/env.py`
13. one migration file

### Best end-to-end learning example

Study this feature path:

```text
Login page
-> auth_routes.py
-> auth_controller.py
-> auth_service.py
-> user model
-> auth templates
-> middleware session handling
```

Then study this one:

```text
Upload questions
-> admin_routes.py
-> admin_controller.py
-> admin_service.py
-> docx_service.py
-> questions model
-> upload_questions.html
```

Then study this one:

```text
Take test
-> test_routes.py
-> test_controller.py
-> mock_test_service.py
-> attempt/result models
-> question.html
-> test_engine.js
```

---

## 36. What You Should Copy Into Future Projects

Recommended to reuse:
- app factory pattern
- `extensions.py`
- `config/settings.py`
- Blueprints
- route -> controller -> service -> model structure
- Flask-Migrate
- `commands.py`
- middleware decorators
- partial templates
- reusable utils/helpers

Not always necessary for every tiny project:
- very deep folder separation
- many docs files
- custom commands if the app is extremely small
- instance folder if there are no uploads or local runtime files

---

## 37. Final Practical Advice

### For manual development

Do this every time:
- build one feature end-to-end
- keep files small
- do not mix route logic and business logic
- keep DB changes in migrations
- test after each small change
- commit model + migration + logic together

### For debugging

Remember this pattern:

```text
Where did it fail?
What layer failed?
What input caused it?
What assumption was wrong?
What is the smallest safe fix?
```

### For migrations

Remember this rule:

```text
Change model -> generate migration -> review migration -> upgrade database -> verify -> test
```

This one habit will save you from many future database issues.

---

## 38. Quick Command Reference

### Run project

```powershell
.\.venv\Scripts\Activate.ps1
python run.py
```

### Create database

```powershell
python -m flask --app run.py create-db
```

### Initialize database

```powershell
python -m flask --app run.py init-db
```

### Create migration

```powershell
python -m flask --app run.py db migrate -m "Describe schema change"
```

### Apply migration

```powershell
python -m flask --app run.py db upgrade
```

### Roll back one migration

```powershell
python -m flask --app run.py db downgrade -1
```

### Show current revision

```powershell
python -m flask --app run.py db current
```

### Show revision history

```powershell
python -m flask --app run.py db history
```

### Reset database

```powershell
python -m flask --app run.py reset-db
```

### Show routes

```powershell
python -m flask --app run.py routes
```

---

## 39. Closing Note

If you understand these 5 things well, you can build many Flask projects manually:

1. app factory pattern
2. route -> controller -> service -> model separation
3. template and static file structure
4. migrations and schema versioning
5. step-by-step debugging habits

This project is a good learning template because it is not just a working app, it also demonstrates how to organize a codebase so it stays maintainable as features grow.

---

## 40. Update Example: Re-Test and Attempt-Wise Reporting

Date:
- 09 July 2026

This is a practical example of how a real feature update was done without adding a new table.

### What changed

- completed tests can now be taken again using `Re-Test`
- reports now show labels like `1st Attempt`, `2nd Attempt`
- test-wise summary keeps `No. of Users Attended` as unique users only
- user-wise summary counts repeated attempts
- each question can now be marked with `Leave as Un-Answer`
- `Final Submit` appears only after every question is answered or explicitly marked unanswered

### Which files were mainly involved

- `app/services/mock_test_service.py`
- `app/services/report_service.py`
- `app/controllers/test_controller.py`
- `app/controllers/api_controller.py`
- `app/utils/helpers.py`
- `app/static/js/test_engine.js`
- `app/templates/mock_tests/question.html`
- `app/templates/partials/question_palette.html`
- `app/templates/user/test_list.html`
- `app/templates/user/results.html`
- `app/templates/user/result_detail.html`
- `app/templates/admin/reports.html`
- `app/templates/admin/test_report_detail.html`
- `app/templates/admin/user_report_detail.html`

### Why no migration was needed

No schema change was required because:
- submitted attempt history already existed in `results`
- active and paused attempts already existed in `attempts`
- question selections were already stored in `attempts.answers_json`

The update only changed how the existing data is interpreted and displayed.

### What to learn from this

Not every feature needs a database migration.

If the existing schema already stores enough information, you can:
- update service logic
- update controller messages
- update templates
- update JavaScript behavior

and keep the database structure unchanged.
