# Commit Message Guide

This guide helps the team write clear, professional, and trackable Git commit messages for ModeAlpha.

## Recommended Format

Use this format for almost all commits:

```bash
git commit -m "type(scope): short clear summary"
```

Examples:

```bash
git commit -m "feat(auth): add profile password update flow"
git commit -m "fix(reports): correct test-wise attendance summary"
git commit -m "docs(setup): add PostgreSQL and Git workflow guides"
```

## Why This Format Is Recommended

Benefits:
- easy to read in Git history
- easy to search later
- easy to understand business impact
- useful for office, home, testing, and production tracking
- looks professional in team and corporate environments

## Commit Message Structure

### `type`

This shows what kind of change was made.

Recommended types:
- `feat` -> new feature
- `fix` -> bug fix
- `refactor` -> code cleanup without business behavior change
- `docs` -> documentation updates
- `style` -> formatting or UI polish without logic change
- `test` -> test case changes
- `chore` -> maintenance, setup, dependency, config work
- `perf` -> performance improvement

### `scope`

This tells which module or area changed.

Examples:
- `auth`
- `admin`
- `reports`
- `test-engine`
- `database`
- `ui`
- `docs`
- `settings`
- `profile`
- `pagination`
- `imports`
- `session`

### `summary`

This is a short sentence describing the main result.

Good examples:
- `add user approval workflow`
- `fix profile password validation`
- `improve report pagination behavior`

## Corporate Writing Rules

Use these rules for better commit messages:
- keep the message short and meaningful
- write what changed, not how hard it was
- use present tense / command style
- focus on business outcome or module impact
- avoid vague words like `changes done`, `updated`, `work completed`
- avoid very long one-line summaries when the change covers many modules

## Best Practice for Large Changes

If many features or fixes are included in one commit, use a subject line and a body.

Example:

```bash
git commit -m "feat: enhance test workflow, admin reporting, and platform setup" -m "Added pause and resume support, question navigation status colors, soft delete handling, paginated reports, admin settings controls, and updated setup guides for PostgreSQL and future maintenance."
```

This is the best option when one commit contains a whole bunch of related work.

## Recommended Types for This Project

### `feat`

Use for:
- new pages
- new admin tools
- new report sections
- new database-driven features
- new test engine behavior

Examples:
- `feat(admin): add user settings management screen`
- `feat(test-engine): add pause and resume support`

### `fix`

Use for:
- incorrect calculations
- broken login flow
- wrong report counts
- session issues
- UI actions not saving correctly

Examples:
- `fix(auth): resolve profile password update issue`
- `fix(reports): include all attended tests in summary`

### `refactor`

Use for:
- reorganizing services
- moving logic out of routes
- cleaning helper methods
- improving code structure without changing features

Examples:
- `refactor(pagination): convert helper to function-based implementation`
- `refactor(admin): move report logic into service layer`

### `docs`

Use for:
- README changes
- setup instructions
- Git workflow docs
- deployment or DB update notes

Examples:
- `docs(setup): refresh project setup and PostgreSQL instructions`
- `docs(git): add branching and deployment workflow handbook`

### `chore`

Use for:
- dependency updates
- folder cleanup
- environment adjustments
- utility command updates

Examples:
- `chore(database): add CLI commands for database setup`
- `chore(project): remove duplicate virtual environment folder guidance`

## Good and Bad Examples

### Good

```text
feat(reports): add detailed user-wise performance view
fix(session): expire inactive login sessions automatically
docs(workflow): add future database update procedure
refactor(auth): simplify login and approval checks
```

### Bad

```text
changes done
updated project
work completed
new code
final changes
bug fixed
```

These are too vague and become difficult to track later.

## Suggested Scope Names for ModeAlpha

Use these scopes consistently:
- `auth`
- `admin`
- `user`
- `reports`
- `test-engine`
- `database`
- `migrations`
- `imports`
- `profile`
- `session`
- `settings`
- `ui`
- `docs`
- `setup`
- `pagination`

## Examples for Common Real Project Changes

### Authentication

```bash
git commit -m "feat(auth): add password change support in profile"
```

### Admin reporting

```bash
git commit -m "feat(reports): add detailed test-wise and user-wise reports"
```

### Database changes

```bash
git commit -m "feat(database): add soft delete and active status fields"
```

### UI improvements

```bash
git commit -m "style(ui): improve button sizing and flash message behavior"
```

### Setup changes

```bash
git commit -m "docs(setup): add quick start and future update guides"
```

## Suggested Format for Big Release Commits

When one commit contains many linked changes, use:

```bash
git commit -m "feat: improve admin module, test engine, and project workflow" -m "Added report enhancements, pause and resume support, question status colors, soft delete handling, admin settings controls, and updated project documentation for setup, Git workflow, and future database changes."
```

## Quick Checklist Before Commit

Before writing a commit message, ask:
- what is the main business result?
- which module changed most?
- is this a feature, fix, docs change, or cleanup?
- can another developer understand this message after 2 months?

## Recommended Team Rule

Use:

```text
type(scope): summary
```

For larger changes, use:

```text
subject + body
```

This keeps the project history neat, searchable, and professional.
