# Recovery and Undo Operations

## Overview

Mistakes happen during merges. Git provides powerful recovery mechanisms to undo merges, recover lost commits, and restore previous states safely.

## Aborting an In-Progress Merge

### When to Abort

abort_merge_reasons[5]{reason,explanation}:
Too many conflicts,More conflicts than expected resolve later
Wrong branch,Realized you're merging the wrong branch
Missing information,Need to consult with team before resolving
Breaking changes,Merge would break critical functionality
Better approach needed,Realized merge strategy should be different

### How to Abort

```bash
# During conflict resolution
git status
# Unmerged paths:
#   both modified:   src/app.js

# Abort and return to pre-merge state
git merge --abort

# Verify clean state
git status
# On branch main
# nothing to commit, working tree clean

# Your branch is exactly as it was before git merge
```

### What Abort Does

```
BEFORE git merge:
main: A---B---C (HEAD)

DURING merge (with conflicts):
main: A---B---C (HEAD, working tree has conflicts)

AFTER git merge --abort:
main: A---B---C (HEAD, clean working tree)
```

## Undoing a Completed Merge

### Option 1: Reset (Before Pushing - DESTRUCTIVE)

**Warning**: Only use if merge hasn't been pushed!

```bash
# Just completed merge
git log --oneline
# abc123 (HEAD -> main) Merge branch 'feature'
# def456 Feature commit
# ghi789 Main commit

# Undo merge (moves HEAD back one commit)
git reset --hard HEAD~1

# OR reset to specific commit
git reset --hard ghi789

# Verify
git log --oneline
# ghi789 (HEAD -> main) Main commit
```

reset_options[3]{option,effect}:
--soft,Keeps changes staged ready to recommit
--mixed,Keeps changes unstaged in working directory
--hard,Discards all changes completely (DANGER)

```bash
# Keep merge changes but undo commit
git reset --soft HEAD~1
# Changes now staged, can recommit with better message

# Keep merge changes but unstage
git reset --mixed HEAD~1
# Changes in working directory, can review before staging

# Completely undo merge
git reset --hard HEAD~1
# All merge changes lost (unless in reflog)
```

### Option 2: Revert (After Pushing - SAFE)

Creates new commit that undoes the merge:

```bash
# Merge already pushed to remote
git log --oneline
# abc123 (HEAD -> main, origin/main) Merge branch 'feature'
# def456 Feature commit
# ghi789 Main commit

# Revert the merge
git revert -m 1 abc123

# -m 1 means "keep parent 1" (usually main branch)
# -m 2 would keep the feature branch

# This creates a new commit
git log --oneline
# xyz789 (HEAD -> main) Revert "Merge branch 'feature'"
# abc123 Merge branch 'feature'
# def456 Feature commit
# ghi789 Main commit

# Push the revert
git push origin main
```

### Understanding -m Option

```
Merge commit has two parents:

     A---B-------M (merge commit)
          \     /
           C---D (feature branch)

Parent 1: B (main branch)
Parent 2: D (feature branch)

git revert -m 1 M → Revert to parent 1 (B, main branch)
git revert -m 2 M → Revert to parent 2 (D, feature branch)
```

## Recovering from Mistakes

### Scenario 1: Accidentally Reset (Lost Commits)

```bash
# Oh no! Accidentally did:
git reset --hard HEAD~5
# Lost important commits!

# Don't panic - use reflog
git reflog
# abc123 HEAD@{0}: reset: moving to HEAD~5
# def456 HEAD@{1}: commit: Important feature
# ghi789 HEAD@{2}: commit: Bug fix
# ...

# Recover lost commits
git cherry-pick def456 ghi789
# Or reset to before the mistake
git reset --hard HEAD@{1}

# Verify recovery
git log --oneline
```

### Scenario 2: Merged Wrong Branch

```bash
# Oops, merged feature-old instead of feature-new
git log --oneline
# abc123 (HEAD -> main) Merge branch 'feature-old'

# If not pushed: reset
git reset --hard HEAD~1

# If pushed: revert then merge correct branch
git revert -m 1 abc123
git merge feature-new
```

### Scenario 3: Partial File Recovery

```bash
# Merged but lost important changes from a specific file
# Get file from before merge
git show HEAD~1:src/important.js > src/important.js.backup

# Compare and recover needed parts
diff src/important.js src/important.js.backup
vim src/important.js  # Restore lost sections

# Amend merge commit (if not pushed)
git add src/important.js
git commit --amend --no-edit
```

## Using Git Reflog

The reflog is your safety net - it records all HEAD movements.

### Viewing Reflog

```bash
# Show recent HEAD movements
git reflog

# More detailed view
git reflog show --date=relative

# Reflog for specific branch
git reflog show main
```

### Reflog Output Example

```
abc123 HEAD@{0}: merge feature: Merge made by the 'recursive' strategy
def456 HEAD@{1}: commit: Add user authentication
ghi789 HEAD@{2}: checkout: moving from feature to main
jkl012 HEAD@{3}: commit: Update API endpoints
mno345 HEAD@{4}: rebase finished: returning to refs/heads/feature
```

### Recovering with Reflog

recovery_scenarios[5]{scenario,solution}:
Lost after reset,git reset --hard HEAD@{before-reset}
Deleted branch,git checkout -b recovered-branch <reflog-hash>
Lost after rebase,git reset --hard ORIG_HEAD or git reflog
Accidental amend,git reset --soft HEAD@{1} then git commit
Lost stash,git fsck --unreachable | grep commit

```bash
# Example: Recover deleted branch
git branch -D feature-important
# Deleted branch feature-important (was abc123)

# Find it in reflog
git reflog | grep feature-important
# abc123 HEAD@{10}: commit: Feature commit

# Recreate branch
git branch feature-important abc123
# or
git checkout -b feature-important abc123
```

## Cherry-picking After Failed Merge

### Scenario: Merge Aborted, Want Specific Commits

```bash
# Tried to merge but aborted due to conflicts
git merge feature/complex
# ... many conflicts ...
git merge --abort

# Want only specific commits from that branch
git log feature/complex --oneline
# abc123 Add login UI
# def456 Update styles
# ghi789 Refactor database (causes conflicts)
# jkl012 Add logout

# Cherry-pick only what you need
git cherry-pick abc123  # Login UI
git cherry-pick def456  # Styles
git cherry-pick jkl012  # Logout
# Skip ghi789 (the problematic one)
```

### Interactive Cherry-pick

```bash
# Cherry-pick with option to edit
git cherry-pick --edit abc123

# Cherry-pick without committing (stage only)
git cherry-pick --no-commit abc123 def456
git commit -m "Combined changes from feature branch"

# Cherry-pick range of commits
git cherry-pick main..feature/branch
```

## Advanced Recovery: ORIG_HEAD

Git saves reference to previous HEAD in ORIG_HEAD:

```bash
# After dangerous operations, ORIG_HEAD points to previous state
git merge feature
# Lots of conflicts, completed merge, but it's broken

# Undo using ORIG_HEAD
git reset --hard ORIG_HEAD

# ORIG_HEAD is set by:
# - git merge
# - git rebase
# - git reset
# - git pull
```

## Recovering Lost Stashes

```bash
# Accidentally dropped stash
git stash drop
# Dropped refs/stash@{0}

# Find lost stash
git fsck --unreachable | grep commit
# unreachable commit abc123def456...

# View the commit
git show abc123def456

# If it's your stash, apply it
git stash apply abc123def456
# or
git cherry-pick abc123def456
```

## Emergency Recovery Commands

emergency_commands[8]{command,purpose}:
git merge --abort,Cancel merge in progress
git reset --hard ORIG_HEAD,Undo last merge/rebase
git reflog,View all HEAD movements
git fsck --lost-found,Find dangling commits
git cherry-pick <hash>,Apply specific commit
git revert -m 1 <hash>,Safely undo merge commit
git reset --soft HEAD~1,Undo commit keep changes
git clean -fd,Remove untracked files (DANGER)

## Preventing Data Loss

prevention_strategies[6]{strategy,explanation}:
Commit often,Small frequent commits easier to recover
Branch before experiments,Always branch for risky operations
Never force push to shared branches,Protects team from data loss
Use --force-with-lease,Safer than --force checks remote state
Enable rerere,Reuse conflict resolutions
Regular backups,Keep remote backup of important work

### Safe Force Push

```bash
# DANGEROUS - overwrites remote unconditionally
git push --force origin main

# SAFER - fails if remote has new commits
git push --force-with-lease origin main

# SAFEST - check remote first
git fetch origin
git log origin/main..main  # See what you're pushing
git push --force-with-lease origin main
```

## Recovery Workflow Checklist

recovery_checklist[8]{step,action}:
1. Don't panic,Take a breath most things are recoverable
2. Assess damage,What was lost? When did it happen?
3. Check reflog,git reflog to find lost commits
4. Check stashes,git stash list for saved work
5. Check branches,git branch -a for backup branches
6. Use fsck,git fsck for dangling objects
7. Recover carefully,Cherry-pick or reset as needed
8. Test recovery,Verify recovered state is correct

## When to Give Up and Ask for Help

seek_help_when[5]{situation,action}:
Reflog doesn't show lost commits,Check with team maybe they have backup
Force pushed to shared branch,Coordinate with team to recover
Repository corruption,Use git fsck repair or re-clone
Lost work older than 30 days,Reflog expires check backups
Complex rebase gone wrong,git rebase --abort ask experienced developer

## Summary

Recovery principles:
1. **Git rarely loses data** - reflog and fsck are powerful
2. **Abort early** - if merge looks wrong, abort immediately
3. **Don't force push** - especially to shared branches
4. **Use reflog** - it's your time machine
5. **Keep backups** - push regularly to remote

Remember: `git reflog` is your friend. Almost everything is recoverable if you know where to look.

## Quick Reference

```bash
# Abort current merge
git merge --abort

# Undo last commit (keep changes)
git reset --soft HEAD~1

# Undo last commit (discard changes)
git reset --hard HEAD~1

# Revert pushed merge
git revert -m 1 <merge-hash>

# Find lost commits
git reflog

# Recover lost commit
git cherry-pick <hash>

# Undo last operation
git reset --hard ORIG_HEAD

# View dangling commits
git fsck --unreachable | grep commit
```
