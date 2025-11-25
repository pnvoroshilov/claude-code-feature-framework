# Example 1: Simple Merge Workflow

## Scenario

You have a feature branch `feature/add-search` that implements search functionality. Main branch has progressed with other features. Time to merge.

## Initial State

```
main:    A---B---C---D (latest)
              \
feature:       E---F---G
```

## Step-by-Step Workflow

### 1. Update Main Branch

```bash
# Switch to main
git checkout main

# Get latest changes
git pull origin main

# Verify you're up to date
git log --oneline -5
# d1a2b3c (HEAD -> main, origin/main) Add user preferences
# c4d5e6f Update API documentation
# b7c8d9e Fix typo in README
```

### 2. Review Feature Branch

```bash
# Switch to feature branch
git checkout feature/add-search

# See what commits will be merged
git log --oneline main..HEAD
# g9h0i1j Add search tests
# f8g9h0i Implement search UI
# e7f8g9h Add search API endpoint

# Review changes
git diff main..HEAD
```

### 3. Update Feature Branch (Optional but Recommended)

```bash
# Incorporate latest main changes
git fetch origin
git rebase origin/main

# Or if you prefer merge:
# git merge origin/main

# Resolve any conflicts if they occur
# Run tests
npm test
```

### 4. Switch Back to Main and Merge

```bash
# Switch to target branch
git checkout main

# Merge feature branch
git merge feature/add-search
```

## Possible Outcomes

### Outcome 1: Clean Merge (No Conflicts)

```bash
git merge feature/add-search
# Updating d1a2b3c..g9h0i1j
# Fast-forward (or creating merge commit)
#  src/search/api.js     | 45 +++++++++
#  src/search/ui.jsx     | 67 +++++++++++
#  tests/search.test.js  | 34 ++++++
#  3 files changed, 146 insertions(+)

# Verify merge
git log --oneline --graph -10

# Push to remote
git push origin main
```

### Outcome 2: Conflicts Detected

```bash
git merge feature/add-search
# Auto-merging src/config.js
# CONFLICT (content): Merge conflict in src/config.js
# Automatic merge failed; fix conflicts and then commit the result.
```

**Resolution:**

```bash
# 1. See which files conflict
git status
# On branch main
# You have unmerged paths.
#
# Unmerged paths:
#   both modified:   src/config.js

# 2. Open and resolve conflicts
vim src/config.js

# Before (conflict):
# <<<<<<< HEAD
# const MAX_RESULTS = 50;
# =======
# const MAX_RESULTS = 100;
# >>>>>>> feature/add-search

# After (resolved):
# const MAX_RESULTS = 100;

# 3. Mark as resolved
git add src/config.js

# 4. Complete merge
git commit -m "Merge feature/add-search into main

Implemented search functionality across the application.

Conflicts resolved:
- src/config.js: Accepted higher MAX_RESULTS value (100)

Features added:
- Search API endpoint
- Search UI component
- Comprehensive search tests

Resolves: #456"

# 5. Push
git push origin main
```

### 5. Cleanup

```bash
# Delete feature branch locally
git branch -d feature/add-search

# Delete from remote
git push origin --delete feature/add-search

# Verify cleanup
git branch -a
```

## Complete Example Session

```bash
# Starting state
$ git branch
* feature/add-search
  main

# Update main
$ git checkout main
Switched to branch 'main'

$ git pull origin main
Already up to date.

# Merge feature
$ git merge feature/add-search
Merge made by the 'recursive' strategy.
 src/search/api.js     | 45 +++++++++
 src/search/ui.jsx     | 67 +++++++++++
 tests/search.test.js  | 34 ++++++
 3 files changed, 146 insertions(+)
 create mode 100644 src/search/api.js
 create mode 100644 src/search/ui.jsx
 create mode 100644 tests/search.test.js

# Verify
$ git log --oneline --graph -5
*   a1b2c3d (HEAD -> main) Merge feature/add-search into main
|\
| * g9h0i1j Add search tests
| * f8g9h0i Implement search UI
| * e7f8g9h Add search API endpoint
|/
* d1a2b3c (origin/main) Add user preferences

# Push
$ git push origin main
Counting objects: 12, done.
...
To github.com:user/project.git
   d1a2b3c..a1b2c3d  main -> main

# Cleanup
$ git branch -d feature/add-search
Deleted branch feature/add-search (was g9h0i1j).

$ git push origin --delete feature/add-search
To github.com:user/project.git
 - [deleted]         feature/add-search

# Final state
$ git branch
* main
```

## Verification Checklist

After merge, verify:

```bash
# ✓ Tests pass
npm test

# ✓ Build succeeds
npm run build

# ✓ No conflict markers
grep -r "<<<<<<< " .
grep -r "=======" .
grep -r ">>>>>>> " .

# ✓ Changes are correct
git diff origin/main..HEAD

# ✓ History is clean
git log --oneline --graph -10
```

## Common Issues and Solutions

### Issue 1: "Already up-to-date" but Branches Differ

```bash
git merge feature/add-search
# Already up-to-date.

# But you know there are changes!
git log main..feature/add-search
# g9h0i1j Add search tests
# ...commits shown...

# Solution: Force merge commit
git merge --no-ff feature/add-search
```

### Issue 2: Accidentally Merged Wrong Branch

```bash
git merge feature/wrong-branch
# Oh no!

# If not pushed yet:
git reset --hard HEAD~1

# If already pushed:
git revert -m 1 HEAD
git push origin main
```

### Issue 3: Forgot to Update Main First

```bash
git merge feature/add-search
# Merged successfully

git push origin main
# ! [rejected]        main -> main (fetch first)

# Solution: Pull with rebase
git pull --rebase origin main
git push origin main
```

## Key Takeaways

merge_workflow_tips[6]{tip,explanation}:
Update before merging,Always pull latest main first
Review before merge,Use git diff to see what's changing
Test after merge,Run full test suite
Clean commit message,Explain what was merged and why
Delete merged branches,Keep repository tidy
Verify push,Ensure changes made it to remote

## Next Steps

- [Example 2: Resolving Text Conflicts](text-conflicts.md) - Handling conflicts in code
- [Example 3: Pre-merge Validation](pre-merge-checks.md) - Automated checks
- [docs/merge-strategies.md](../docs/merge-strategies.md) - Choosing merge strategy
