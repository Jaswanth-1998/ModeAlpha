# Git Workflow Handbook (Office + Home + Testing + Production)

This workflow uses:

* `main` → production/live deployed code
* `development` → active development
* `testing` → UAT/testing branch

Goal:

* `main` always stable
* New work goes to `development`
* Testing happens in `testing`
* Only tested code goes to `main`
* Old deployed code stays live until merge to `main`

---

# 1. Create Repository

## Create local project

```bash
mkdir myproject
cd myproject
```

---

# 2. Initialize Git

```bash
git init
```

---

# 3. Add Files

```bash
git add .
```

---

# 4. First Commit

```bash
git commit -m "Initial project setup"
```

---

# 5. Add GitHub Repository

Create repository in [GitHub](https://github.com?utm_source=chatgpt.com)

Example:

```bash
git remote add origin https://github.com/username/myproject.git
```

---

# 6. Rename Default Branch to Main

```bash
git branch -M main
```

---

# 7. Push Main Branch

```bash
git push -u origin main
```

---

# 8. Create Development Branch

```bash
git checkout -b development
```

Push it:

```bash
git push -u origin development
```

---

# 9. Create Testing Branch

```bash
git checkout -b testing
```

Push it:

```bash
git push -u origin testing
```

---

# Final Branch Structure

```text
main         -> Production/live
development  -> Developer work
testing      -> UAT testing
```

---

# DAILY WORKFLOW

# 10. Start Working in Development

Always switch to development branch before coding.

```bash
git checkout development
```

---

# 11. Pull Latest Code Before Work

Very important when working from office/home.

```bash
git pull origin development
```

---

# 12. Make Changes

Edit files.

---

# 13. Check Changed Files

```bash
git status
```

---

# 14. Add Updated Files

```bash
git add .
```

OR specific file:

```bash
git add app.py
```

---

# 15. Commit Changes

```bash
git commit -m "Added login feature"
```

---

# 16. Push Development Changes

```bash
git push origin development
```

---

# TESTING FLOW

# 17. Move Development Code to Testing

Switch to testing branch:

```bash
git checkout testing
```

---

Pull latest testing code:

```bash
git pull origin testing
```

---

Merge development into testing:

```bash
git merge development
```

---

Push testing branch:

```bash
git push origin testing
```

---

# UAT / TESTING

QA/UAT team tests from `testing` branch.

Production (`main`) still uses old stable code.

Nothing changes in production yet.

---

# IF BUGS FOUND

Switch back:

```bash
git checkout development
```

Fix bugs.

Then:

```bash
git add .
git commit -m "Fixed login validation bug"
git push origin development
```

Again move to testing:

```bash
git checkout testing
git merge development
git push origin testing
```

---

# FINAL PRODUCTION DEPLOYMENT

# 18. Merge Tested Code to Main

Switch:

```bash
git checkout main
```

---

Pull latest main:

```bash
git pull origin main
```

---

Merge tested code:

```bash
git merge testing
```

---

Push main:

```bash
git push origin main
```

---

Now deploy from `main`.

---

# IMPORTANT REAL-WORLD RULE

## Production server should ONLY deploy from `main`

Never deploy from:

* development
* testing

Only:

```text
main
```

That ensures unfinished work never goes live.

---

# WHEN DEVELOPMENT HAS NEW CHANGES BUT MAIN SHOULD STAY OLD

Example:

```text
main         -> version 1 live
development  -> version 2 in progress
testing      -> testing version 2
```

Production still uses:

```text
main -> version 1
```

Because you did NOT merge to main.

So old stable code remains deployed.

---

# HOW TO CHECK OLD VERSION CODES

# View Commit History

```bash
git log --oneline
```

Example:

```text
a1b2c3 Added payment gateway
d4e5f6 Fixed login
g7h8i9 Initial commit
```

---

# View Specific Old Version

```bash
git checkout COMMIT_ID
```

Example:

```bash
git checkout d4e5f6
```

Now project becomes old version temporarily.

---

# Return Back

```bash
git checkout main
```

OR

```bash
git checkout development
```

---

# DEPLOY OLD VERSION ONLY

Example:

Production broken after latest deployment.

Find old stable commit:

```bash
git log --oneline
```

Checkout old commit:

```bash
git checkout d4e5f6
```

Deploy it.

---

# BETTER REAL-WORLD METHOD (TAGS)

# Create Stable Release Tag

```bash
git tag v1.0
```

Push tag:

```bash
git push origin v1.0
```

---

# Deploy Old Stable Version

```bash
git checkout v1.0
```

Much cleaner than commit IDs.

---

# OFFICE + HOME WORKFLOW

# OFFICE

Before work:

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

---

# HOME

Before work:

```bash
git checkout development
git pull origin development
```

Now office updates come to home laptop.

Work normally.

Then:

```bash
git add .
git commit -m "Added API integration"
git push origin development
```

---

# VERY IMPORTANT RULE

Always do:

```bash
git pull
```

before starting work in another machine.

Otherwise conflicts happen.

---

# IF CONFLICT HAPPENS

Example:

Same file edited in office and home.

Git shows conflict.

Check files:

```bash
git status
```

Open conflicted file.

You will see:

```text
<<<<<<< HEAD
home code
=======
office code
>>>>>>> branch
```

Edit manually.

Keep correct code.

Then:

```bash
git add .
git commit -m "Resolved merge conflict"
git push origin development
```

---

# COMPLETE FLOW SUMMARY

```text
Developer Work
      ↓
development
      ↓
Merge to testing
      ↓
UAT Testing
      ↓
Bug Fixes in development
      ↓
Merge again to testing
      ↓
Approved
      ↓
Merge testing → main
      ↓
Deploy main
```

---

# MOST IMPORTANT COMMANDS

## Clone Project

```bash
git clone REPO_URL
```

---

## Switch Branch

```bash
git checkout development
```

---

## Pull Latest Code

```bash
git pull origin development
```

---

## Push Code

```bash
git push origin development
```

---

## Create Branch

```bash
git checkout -b testing
```

---

## Merge Branch

```bash
git merge development
```

---

## View Branches

```bash
git branch
```

---

## View Commit History

```bash
git log --oneline
```

---

# Recommended Real-World Strategy

```text
main
  Stable production only

development
  Daily developer coding

testing
  QA/UAT validation
```

This is simple, scalable, and used in many companies.


Since you already have the project on your **office system** and want to work on the same project from your **home system**, you only need `git clone` **once on the home system**.

Repository:

```text
https://github.com/Jaswanth-1998/ModeAlpha.git
```
-----------------------------------------------------------------------------------------------------------------------------------------------

### git clone once on the home system ###

# First Time Setup on Home System

Open Terminal / Git Bash.

## 1. Go to the folder where you want the project

Example:

```bash
cd D:\Projects
```

or

```bash
cd ~/Projects
```

---

## 2. Clone the repository

```bash
git clone https://github.com/Jaswanth-1998/ModeAlpha.git
```

Output:

```text
Cloning into 'ModeAlpha'...
Receiving objects...
Resolving deltas...
```

Now a folder is created:

```text
Projects/
└── ModeAlpha/
```

---

## 3. Enter the project folder

```bash
cd ModeAlpha
```

---

## 4. Check available branches

```bash
git branch -a
```

Example output:

```text
* main
  remotes/origin/main
  remotes/origin/development
  remotes/origin/testing
```

---

## 5. Switch to development branch

If development branch already exists remotely:

```bash
git checkout development
```

If Git says branch not found:

```bash
git checkout -b development origin/development
```

Verify:

```bash
git branch
```

Output:

```text
* development
  main
```

Now you're ready to work.

---

# Daily Office Workflow

Before starting work:

```bash
cd ModeAlpha
git checkout development
git pull origin development
```

Do coding.

Then:

```bash
git add .
git commit -m "Completed feature XYZ"
git push origin development
```

---

# Daily Home Workflow

After reaching home:

```bash
cd ModeAlpha
git checkout development
git pull origin development
```

Now you get all office changes.

Do coding.

Then:

```bash
git add .
git commit -m "Modified feature XYZ"
git push origin development
```

---

# Next Day at Office

Get home changes:

```bash
cd ModeAlpha
git checkout development
git pull origin development
```

Continue working.

---

# Verify You Are On Correct Branch

Before coding:

```bash
git branch
```

Output should be:

```text
* development
```

If not:

```bash
git checkout development
```

---

# Very Important

Use `git clone` only:

* First time on home laptop
* First time on new office laptop
* First time on a new machine

After that, never clone again on the same machine.

Use:

```bash
git pull origin development
```

to get the latest changes and

```bash
git push origin development
```

to send your changes to GitHub.
