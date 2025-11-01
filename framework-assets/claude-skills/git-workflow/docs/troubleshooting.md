# Troubleshooting Git Issues

## Table of Contents

- [Merge Conflicts](#merge-conflicts)
- [Lost Commits](#lost-commits)
- [Undoing Changes](#undoing-changes)
- [Fixing Commit Mistakes](#fixing-commit-mistakes)
- [Detached HEAD State](#detached-HEAD-state)
- [Remote Synchronization Issues](#remote-synchronization-issues)
- [Large Files and Repository Size](#large-files-and-repository-size)
- [Permission and Authentication Issues](#permission-and-authentication-issues)

## Merge Conflicts

### Problem: Merge Conflicts During Pull

**Symptoms:**
```bash
$ git pull origin main
CONFLICT (content): Merge conflict in src/app.js
Automatic merge failed; fix conflicts and then commit the result.
```

**Solution:**

```bash
# 1. Check conflict status
git status
# Shows conflicted files

# 2. Open conflicted file
# Look for conflict markers:
<<<<<<< HEAD
your changes
=======
their changes
>>>>>>> origin/main

# 3. Resolve manually
# Edit file to keep desired changes
# Remove conflict markers

# 4. Mark as resolved
git add src/app.js

# 5. Complete merge
git commit

# Alternative: Use merge tool
git mergetool
```

**Prevention:**
- Pull frequently to stay synced
- Commit before pulling
- Use smaller, focused commits
- Communicate with team about overlapping work

---

## Lost Commits

### Problem: Can't Find Commits After Reset

**Symptoms:**
```bash
$ git reset --hard HEAD~5
# Oh no! Where did my commits go?
```

**Solution:**

```bash
# 1. Check reflog
git reflog
# abc123 HEAD@{0}: reset: moving to HEAD~5
# def456 HEAD@{1}: commit: my important work

# 2. Recover lost commits
git reset --hard HEAD@{1}
# OR create branch to preserve
git branch recovered-work HEAD@{1}

# 3. Verify recovery
git log
```

**Alternative: Find by commit message:**
```bash
# Search all reachable and unreachable commits
git fsck --lost-found
git log --all --oneline | grep "important work"
```

### Problem: Deleted Branch with Unmerged Work

**Symptoms:**
```bash
$ git branch -D feature-branch
Deleted branch feature-branch (was abc123).
# Oops, that had important work!
```

**Solution:**

```bash
# 1. Find branch tip in reflog
git reflog | grep "feature-branch"
# abc123 HEAD@{5}: commit: feature work

# 2. Recreate branch
git checkout -b feature-branch abc123

# 3. Verify
git log
```

---

## Undoing Changes

### Problem: Need to Undo Last Commit

**Keep changes (soft reset):**
```bash
# Undo commit, keep changes staged
git reset --soft HEAD~1

# OR undo commit, keep changes unstaged
git reset HEAD~1

# Changes still in working directory
```

**Discard changes (hard reset):**
```bash
# Undo commit and discard all changes
git reset --hard HEAD~1

# WARNING: This permanently deletes changes
```

**Create reverse commit (revert):**
```bash
# Safer for shared branches
git revert HEAD

# Creates new commit that undoes changes
# Preserves history
```

### Problem: Undo Changes to Specific File

**Discard unstaged changes:**
```bash
# Revert file to last commit
git checkout -- src/app.js

# OR with newer syntax
git restore src/app.js
```

**Unstage file:**
```bash
# Remove from staging, keep changes
git reset HEAD src/app.js

# OR with newer syntax
git restore --staged src/app.js
```

**Revert file to specific commit:**
```bash
# Restore file from specific commit
git checkout abc123 -- src/app.js
git commit -m "revert: restore app.js from abc123"
```

---

## Fixing Commit Mistakes

### Problem: Wrong Commit Message

**Last commit:**
```bash
# Fix most recent commit message
git commit --amend -m "correct message"
```

**Older commit:**
```bash
# Use interactive rebase
git rebase -i HEAD~3

# Mark commit with 'reword'
reword abc123 old message

# Git opens editor to change message
```

### Problem: Forgot to Add Files to Commit

```bash
# Add forgotten files
git add forgotten-file.js

# Amend last commit
git commit --amend --no-edit

# Files now included in last commit
```

### Problem: Committed to Wrong Branch

**Move commits to correct branch:**
```bash
# Currently on wrong-branch with 3 commits to move
git log --oneline -3
# abc123 commit 3
# def456 commit 2  
# ghi789 commit 1

# Create/checkout correct branch
git checkout -b correct-branch HEAD~3

# Cherry-pick commits
git cherry-pick ghi789 def456 abc123

# Go back and reset wrong branch
git checkout wrong-branch
git reset --hard HEAD~3
```

### Problem: Committed Sensitive Data

**Remove from last commit:**
```bash
# Remove file
git rm --cached secrets.env

# Amend commit
git commit --amend --no-edit

# Force push if already pushed
git push --force-with-lease
```

**Remove from history:**
```bash
# Use git-filter-repo (recommended)
git filter-repo --path secrets.env --invert-paths

# Or BFG Repo-Cleaner
bfg --delete-files secrets.env

# Force push all branches
git push --force --all

# IMPORTANT: Rotate compromised secrets!
```

---

## Detached HEAD State

### Problem: In Detached HEAD State

**Symptoms:**
```bash
$ git checkout abc123
Note: switching to 'abc123'.
You are in 'detached HEAD' state...

$ git status
HEAD detached at abc123
```

**Solution (without saving work):**
```bash
# Just return to a branch
git checkout main
```

**Solution (save work):**
```bash
# Create branch at current position
git checkout -b new-branch-name

# OR create branch without checking out
git branch recovery-branch
git checkout main
```

**Prevention:**
- Always work on branches, not specific commits
- Use branches for any development work

---

## Remote Synchronization Issues

### Problem: Diverged Branches

**Symptoms:**
```bash
$ git pull
fatal: Need to specify how to reconcile divergent branches.
```

**Solution 1: Merge (default):**
```bash
git pull --no-rebase
# Creates merge commit
```

**Solution 2: Rebase (cleaner):**
```bash
git pull --rebase
# Replays your commits on top of remote
```

**Configure default behavior:**
```bash
# Set pull to always rebase
git config --global pull.rebase true

# OR set to always merge
git config --global pull.rebase false
```

### Problem: Push Rejected

**Symptoms:**
```bash
$ git push
! [rejected] main -> main (fetch first)
error: failed to push some refs
```

**Solution:**
```bash
# Someone else pushed, fetch their changes
git fetch origin

# Option 1: Merge their changes
git merge origin/main
git push

# Option 2: Rebase on their changes
git rebase origin/main
git push

# Option 3: Pull (fetch + merge/rebase)
git pull
git push
```

### Problem: Can't Push, Need Force Push

**Symptoms:**
```bash
$ git push
! [rejected] feature -> feature (non-fast-forward)
```

**Safe force push:**
```bash
# Use --force-with-lease (safer)
git push --force-with-lease origin feature

# Only succeeds if no one else pushed
# Protects against overwriting others' work
```

**Unsafe force push (avoid):**
```bash
# Overwrites remote regardless
git push --force origin feature
# Only use if you're certain no one else has pushed
```

---

## Large Files and Repository Size

### Problem: Repository Too Large

**Check size:**
```bash
# See repository size
git count-objects -vH
```

**Solution 1: Find large files:**
```bash
# Find largest files in history
git rev-list --objects --all \
  | git cat-file --batch-check='%(objecttype) %(objectname) %(objectsize) %(rest)' \
  | awk '/^blob/ {print substr($0,6)}' \
  | sort --numeric-sort --key=2 \
  | tail -20
```

**Solution 2: Remove large files:**
```bash
# Use git-filter-repo
git filter-repo --path large-file.zip --invert-paths

# Or BFG Repo-Cleaner
bfg --strip-blobs-bigger-than 50M
```

**Solution 3: Use Git LFS:**
```bash
# Install Git LFS
git lfs install

# Track large files
git lfs track "*.psd"
git lfs track "*.mp4"

# Add .gitattributes
git add .gitattributes

# Large files now stored in LFS
```

### Problem: Accidentally Committed Large File

```bash
# Remove from last commit
git rm --cached large-file.zip
git commit --amend --no-edit

# If already pushed
git push --force-with-lease
```

---

## Permission and Authentication Issues

### Problem: Permission Denied (SSH)

**Symptoms:**
```bash
$ git push
Permission denied (publickey).
fatal: Could not read from remote repository.
```

**Solution:**
```bash
# 1. Check SSH key
ssh -T git@github.com

# 2. Generate new SSH key if needed
ssh-keygen -t ed25519 -C "your.email@example.com"

# 3. Add to SSH agent
eval "$(ssh-agent -s)"
ssh-add ~/.ssh/id_ed25519

# 4. Add public key to GitHub
cat ~/.ssh/id_ed25519.pub
# Copy and add to GitHub Settings → SSH Keys
```

### Problem: Authentication Failed (HTTPS)

**Solution:**
```bash
# Use SSH instead of HTTPS
git remote set-url origin git@github.com:user/repo.git

# OR configure credential helper
git config --global credential.helper cache

# OR use personal access token
# GitHub Settings → Developer settings → Personal access tokens
# Use token as password when prompted
```

### Problem: Wrong Permissions on Files

```bash
# Fix repository permissions
chmod -R u+rwX,go+rX,go-w .git

# Fix file permissions
find . -type f -exec chmod 644 {} \;
find . -type d -exec chmod 755 {} \;
```

---

## Additional Common Issues

### Problem: Slow Git Operations

**Solutions:**
```bash
# Run garbage collection
git gc --aggressive --prune=now

# Repack repository
git repack -ad

# Enable filesystem monitor (Git 2.36+)
git config core.fsmonitor true
```

### Problem: Line Ending Issues

**Configure line endings:**
```bash
# Windows (CRLF)
git config --global core.autocrlf true

# Mac/Linux (LF)
git config --global core.autocrlf input

# Normalize existing files
git add --renormalize .
git commit -m "chore: normalize line endings"
```

### Problem: Git Commands Hang

```bash
# Check for large files being processed
# Kill hung Git process
ps aux | grep git
kill <PID>

# Clean up lock files
rm .git/index.lock
rm .git/refs/heads/*.lock
```

---

## Quick Reference: Common Fixes

| Problem | Quick Fix |
|---------|-----------|
| Undo last commit | `git reset --soft HEAD~1` |
| Discard local changes | `git checkout -- <file>` |
| Unstage file | `git reset HEAD <file>` |
| Fix last commit message | `git commit --amend` |
| Recover deleted branch | `git reflog` → `git branch <name> <sha>` |
| Exit detached HEAD | `git checkout main` |
| Update from remote | `git pull --rebase` |
| Safe force push | `git push --force-with-lease` |
| Find lost commits | `git reflog` |
| Remove large file | `git filter-repo --path <file> --invert-paths` |

---

## Getting Help

**Git documentation:**
```bash
# Command help
git help <command>
git <command> --help

# Man page
man git-<command>

# Quick reference
git <command> -h
```

**Git configuration:**
```bash
# View all config
git config --list

# View specific config
git config user.name
git config remote.origin.url
```

**Debug mode:**
```bash
# Verbose output
git <command> -v

# Trace all Git commands
GIT_TRACE=1 git <command>

# Trace Git operations
GIT_TRACE_PERFORMANCE=1 git <command>
```

---

## Prevention Strategies

**Daily habits:**
- Commit frequently with clear messages
- Pull before starting work
- Push at end of day
- Use branches for all work
- Review changes before committing

**Safety nets:**
- Enable branch protection
- Use pre-commit hooks
- Regular backups
- Keep main branch stable
- Use feature flags

**Team communication:**
- Discuss before force pushing
- Announce large refactorings
- Share merge conflict solutions
- Document team Git workflow

---

## When to Ask for Help

Ask for help if:
- Lost important work (reflog doesn't help)
- Repository corruption
- Unable to push/pull after multiple attempts
- Need to rewrite published history safely
- Team-wide Git issues

**Resources:**
- Git documentation: git-scm.com
- Stack Overflow: stackoverflow.com/questions/tagged/git
- GitHub Community: github.community
- Team lead or senior developer

Remember: Most Git problems are recoverable. Take a deep breath, check reflog, and work through it systematically.
