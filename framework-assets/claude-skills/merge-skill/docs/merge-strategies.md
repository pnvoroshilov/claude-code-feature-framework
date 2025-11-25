# Merge Strategies - Detailed Guide

## Overview

Git provides multiple merge strategies, each suited for different scenarios. Choosing the right strategy affects your project's history, collaboration workflow, and maintenance.

## Strategy Comparison

merge_strategy_comparison[4]{strategy,history_type,use_case,command}:
Fast-forward,Linear - no merge commit,Branch is ahead of target,git merge --ff-only
3-way merge,Branched - creates merge commit,Preserve full history,git merge --no-ff
Squash merge,Linear - single commit,Clean history desired,git merge --squash
Rebase merge,Linear - rewrites commits,Perfect linear history,git rebase && merge

## Fast-forward Merge

### When to Use
- Feature branch is ahead of main with no divergence
- Main branch hasn't received any commits since branch creation
- Want simplest possible merge with no extra commits

### How It Works
```
BEFORE:
main:    A---B
              \
feature:       C---D

AFTER (fast-forward):
main:    A---B---C---D
```

### Commands
```bash
# Ensure fast-forward is possible
git checkout main
git pull origin main

# Attempt fast-forward merge
git merge --ff-only feature/quick-fix

# If it fails, branch has diverged - use different strategy
```

### Pros and Cons

fast_forward_pros_cons[6]{aspect,pro_or_con}:
History simplicity,Pro - cleanest possible history
No merge commits,Pro - linear timeline
Branch visibility,Con - loses information about feature branch existence
Force linear,Con - fails if branches diverged
Collaboration,Con - not suitable for shared branches
Rollback difficulty,Con - harder to revert entire feature at once

## 3-Way Merge (Merge Commit)

### When to Use
- Branches have diverged (both have new commits)
- Want to preserve complete history
- Working with team on shared branches
- Need clear boundary between features

### How It Works
```
BEFORE:
main:    A---B---E---F
              \
feature:       C---D

AFTER (3-way merge):
main:    A---B---E---F---M
              \         /
feature:       C---D----
```

### Commands
```bash
# Force creation of merge commit even if fast-forward possible
git checkout main
git merge --no-ff feature/new-dashboard

# Git automatically creates merge commit
# Or resolve conflicts if needed
```

### Pros and Cons

three_way_pros_cons[6]{aspect,pro_or_con}:
History preservation,Pro - complete feature branch history visible
Feature boundaries,Pro - clear merge commits mark feature completion
Rollback ease,Pro - revert merge commit to undo entire feature
Graph complexity,Con - branching history can be complex
Merge commits,Con - extra commits in history
Bisect difficulty,Con - git bisect more complex with branches

## Squash Merge

### When to Use
- Want clean, linear history
- Feature branch has messy commit history
- Individual commits not important
- Deploying to production requires clean history

### How It Works
```
BEFORE:
main:    A---B
              \
feature:       C---D---E (messy commits)

AFTER (squash merge):
main:    A---B---S (S contains all changes from C, D, E)
```

### Commands
```bash
git checkout main
git merge --squash feature/refactor-auth

# This stages all changes but doesn't commit
# Now create a single, well-crafted commit
git commit -m "feat: refactor authentication system

- Implement OAuth2 flow
- Add JWT token management
- Improve session handling

Closes #123"
```

### Pros and Cons

squash_merge_pros_cons[6]{aspect,pro_or_con}:
Clean history,Pro - one commit per feature
Linear timeline,Pro - easy to follow git log
Clear commits,Pro - well-written commit messages
Feature detail lost,Con - individual commit history erased
Collaboration issues,Con - contributors lose attribution for individual commits
Bisect benefit,Pro - easier to bisect with fewer commits

## Rebase Merge

### When to Use
- Want perfectly linear history
- Feature branch is yours alone (not shared)
- Can rewrite history safely
- Team prefers linear history

### How It Works
```
BEFORE:
main:    A---B---E---F
              \
feature:       C---D

AFTER (rebase):
main:    A---B---E---F
feature:               C'---D' (rebased commits)

THEN (merge):
main:    A---B---E---F---C'---D' (fast-forward merge)
```

### Commands
```bash
# Step 1: Rebase feature branch onto main
git checkout feature/api-update
git rebase main

# Resolve any conflicts during rebase
# Git replays each commit one by one

# Step 2: Fast-forward merge
git checkout main
git merge feature/api-update  # This will be fast-forward
```

### Pros and Cons

rebase_merge_pros_cons[6]{aspect,pro_or_con}:
Perfect linear history,Pro - cleanest possible timeline
No merge commits,Pro - eliminates merge commit noise
Conflict resolution,Con - may need to resolve conflicts multiple times
Shared branches,Con - NEVER rebase shared branches dangerous
Force push required,Con - need git push --force after rebase
History rewriting,Con - changes commit hashes breaks references

### Rebase Warning

**NEVER rebase branches that have been pushed and shared with others!**

```bash
# DANGEROUS - DO NOT DO THIS if branch is shared:
git checkout shared-feature
git rebase main  # This rewrites history
git push --force  # This breaks everyone's local branches

# SAFE - Only rebase private branches:
git checkout my-private-feature
git rebase main
git push --force-with-lease  # Safer than --force
```

## Strategy Selection Guide

### Decision Matrix

project_type_to_strategy[5]{project_type,recommended_strategy,reason}:
Open source public,3-way merge,Preserves contributor history and attribution
Enterprise team,Squash merge,Clean history easier code review
Solo developer,Rebase merge,Perfect linear history full control
Continuous deployment,Squash merge,One commit per feature easier rollback
Large refactoring,3-way merge,Preserves context of changes over time

### Decision Questions

```
Q1: Is the feature branch shared with others?
    YES → Use 3-way merge (--no-ff)
    NO  → Continue to Q2

Q2: Do you need to preserve individual commit history?
    YES → Use 3-way merge (--no-ff)
    NO  → Continue to Q3

Q3: Is perfectly linear history important?
    YES → Use rebase merge or squash merge
    NO  → Continue to Q4

Q4: Has main branch changed since feature branch creation?
    YES → Use 3-way merge (--no-ff) or rebase merge
    NO  → Use fast-forward merge (--ff-only)

Q5: Are commits in feature branch messy/WIP?
    YES → Use squash merge
    NO  → Use 3-way merge (--no-ff)
```

## Examples by Scenario

### Scenario 1: Quick Hotfix (Fast-forward)

```bash
# Create hotfix branch
git checkout -b hotfix/security-patch main

# Make fix
echo "fixed" > security-fix.txt
git add security-fix.txt
git commit -m "fix: patch security vulnerability CVE-2024-001"

# Merge back (fast-forward)
git checkout main
git merge --ff-only hotfix/security-patch
# Result: A---B---C (C is the hotfix commit, no merge commit)

# Clean up
git branch -d hotfix/security-patch
```

### Scenario 2: Feature with Full History (3-way)

```bash
# Feature branch with multiple commits
git checkout -b feature/user-dashboard main

# Work happens...
git commit -m "feat: add dashboard layout"
git commit -m "feat: add charts component"
git commit -m "feat: add user stats widget"

# Merge preserving history
git checkout main
git merge --no-ff feature/user-dashboard

# Result: Creates merge commit that ties all three commits together
# History shows:
# - Individual feature commits
# - Merge commit marking feature completion
```

### Scenario 3: Messy Feature (Squash)

```bash
# Feature branch with WIP commits
git checkout -b feature/refactor-api main

# Messy work...
git commit -m "wip"
git commit -m "fix typo"
git commit -m "oops forgot file"
git commit -m "actually done now"

# Squash into single clean commit
git checkout main
git merge --squash feature/refactor-api
git commit -m "refactor: modernize API endpoints

- Convert to REST best practices
- Add proper error handling
- Improve response formats

Closes #456"

# Result: Clean single commit, messy history discarded
```

### Scenario 4: Perfect Linear History (Rebase)

```bash
# Keep feature branch current with main
git checkout feature/new-auth
git fetch origin
git rebase origin/main  # Replay feature commits on top of main

# Resolve any conflicts
# Each commit is replayed individually

# Once rebased, fast-forward merge
git checkout main
git merge feature/new-auth  # Fast-forward, no merge commit

# Result: A---B---C---D---E---F (perfectly linear)
```

## Branch Protection and Strategy Enforcement

### GitHub Branch Protection

```yaml
# .github/workflows/branch-protection.yml
# Enforce merge strategy via GitHub Actions

on:
  pull_request:
    types: [opened, synchronize]

jobs:
  enforce-squash:
    runs-on: ubuntu-latest
    steps:
      - name: Check PR merge method
        run: |
          # Enforce squash merge only
          if [ "${{ github.event.pull_request.merge_method }}" != "squash" ]; then
            echo "Error: Only squash merge allowed"
            exit 1
          fi
```

### Git Configuration

```bash
# Prevent accidental fast-forward merges
git config merge.ff false  # Always create merge commit

# Or enforce fast-forward only
git config merge.ff only   # Fail if fast-forward not possible

# Default to no fast-forward
git config --global merge.ff false
```

## Advanced: Octopus Merge

Merge multiple branches at once (rarely needed):

```bash
# Merge multiple feature branches simultaneously
git checkout main
git merge feature-a feature-b feature-c

# Creates single merge commit with multiple parents
# Only works if no conflicts between branches
```

## Summary

Choose your merge strategy based on:
- **Team workflow** - Shared branches need 3-way merge
- **History preferences** - Linear vs branched
- **Commit quality** - Clean commits use as-is, messy use squash
- **Rollback needs** - Easy revert needs merge commits
- **Project standards** - Follow team conventions

Default recommendation: **3-way merge (--no-ff)** for most teams, as it preserves history and enables easy rollback.
