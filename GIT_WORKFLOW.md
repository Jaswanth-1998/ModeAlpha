# Git Workflow Handbook

This project follows a simple 3-branch workflow so production stays stable while development and testing continue safely.

## Branch Purpose

- `main` -> production / live deployed code
- `development` -> active development work
- `testing` -> QA / UAT testing branch

Goal:
- `main` should always stay stable
- all new work starts in `development`
- testing happens in `testing`
- only approved code moves to `main`

## Initial Repository Setup

### 1. Create local project folder

```bash
mkdir myproject
cd myproject
```

### 2. Initialize Git

```bash
git init
```

### 3. Add project files

```bash
git add .
```

### 4. Create first commit

```bash
git commit -m "Initial project setup"
```

### 5. Add GitHub remote

Create a repository in GitHub, then run:

```bash
git remote add origin https://github.com/username/myproject.git
```

### 6. Rename default branch to main

```bash
git branch -M main
```

### 7. Push main branch

```bash
git push -u origin main
```

### 8. Create development branch

```bash
git checkout -b development
git push -u origin development
```

### 9. Create testing branch

```bash
git checkout -b testing
git push -u origin testing
```

## Final Branch Structure

```text
main         -> Production / live
development  -> Daily developer work
testing      -> QA / UAT testing
```

## Daily Development Workflow

### 1. Move to development branch

```bash
git checkout development
```

### 2. Pull latest code before starting work

This is important when working from office, home, or another machine.

```bash
git pull origin development
```

### 3. Make code changes

Update files normally.

### 4. Check modified files

```bash
git status
```

### 5. Stage changes

```bash
git add .
```

Or add only specific files:

```bash
git add app.py
```

### 6. Commit changes

```bash
git commit -m "Added login feature"
```

### 7. Push development work

```bash
git push origin development
```

## Testing Flow

### Move development code into testing

```bash
git checkout testing
git pull origin testing
git merge development
git push origin testing
```

Now QA / UAT team can test from `testing`.

Important:
- production is still unchanged
- `main` still holds the old live stable code

## If Bugs Are Found During Testing

Go back to development:

```bash
git checkout development
```

Fix the issue, then:

```bash
git add .
git commit -m "Fixed login validation bug"
git push origin development
```

Move the fix again to testing:

```bash
git checkout testing
git merge development
git push origin testing
```

## Production Deployment Flow

Only after testing approval:

```bash
git checkout main
git pull origin main
git merge testing
git push origin main
```

Then deploy from `main`.

## Important Real-World Rule

Production server should deploy only from:

```text
main
```

Never deploy from:
- `development`
- `testing`

This ensures unfinished work never goes live.

## Example Version Flow

```text
main         -> Version 1 live
development  -> Version 2 in progress
testing      -> Version 2 under testing
```

Production still stays on Version 1 until `testing` is merged into `main`.

## Office and Home Workflow

### Office

Before starting work:

```bash
git checkout development
git pull origin development
```

After work:

```bash
git add .
git commit -m "Completed dashboard UI"
git push origin development
```

### Home

Before starting work:

```bash
git checkout development
git pull origin development
```

Now office updates are available on the home machine.

After work:

```bash
git add .
git commit -m "Added API integration"
git push origin development
```

## Very Important Rule

Before starting work on another machine, always run:

```bash
git pull origin development
```

Otherwise conflicts can happen.

## If Conflict Happens

Check status:

```bash
git status
```

Git may show conflict markers like:

```text
<<<<<<< HEAD
home code
=======
office code
>>>>>>> branch
```

Fix the file manually, then run:

```bash
git add .
git commit -m "Resolved merge conflict"
git push origin development
```

## View Old Versions

### Show commit history

```bash
git log --oneline
```

Example:

```text
a1b2c3 Added payment gateway
d4e5f6 Fixed login
g7h8i9 Initial commit
```

### Checkout old version temporarily

```bash
git checkout COMMIT_ID
```

Example:

```bash
git checkout d4e5f6
```

Return back later:

```bash
git checkout main
```

or

```bash
git checkout development
```

## Better Real-World Method: Tags

### Create release tag

```bash
git tag v1.0
git push origin v1.0
```

### Use an old stable release

```bash
git checkout v1.0
```

Tags are cleaner than remembering commit IDs.

## Complete Flow Summary

```text
Developer Work
      ?
development
      ?
Merge to testing
      ?
UAT Testing
      ?
Bug Fixes in development
      ?
Merge again to testing
      ?
Approved
      ?
Merge testing -> main
      ?
Deploy main
```

## Most Common Git Commands

### Clone project

```bash
git clone REPO_URL
```

### Switch branch

```bash
git checkout development
```

### Pull latest code

```bash
git pull origin development
```

### Push code

```bash
git push origin development
```

### Create branch

```bash
git checkout -b testing
```

### Merge branch

```bash
git merge development
```

### View branches

```bash
git branch
```

### View commit history

```bash
git log --oneline
```

## Recommended Strategy for This Project

```text
main
  Stable production only

development
  Daily developer coding

testing
  QA / UAT validation
```

This is simple, safe, and works well when you move between office, home, testing, and production environments.
