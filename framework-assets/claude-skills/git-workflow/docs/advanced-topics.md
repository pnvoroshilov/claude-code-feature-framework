# Advanced Git Topics

## Table of Contents

- [Interactive Rebase Mastery](#interactive-rebase-mastery)
- [Cherry-Picking Strategies](#cherry-picking-strategies)
- [Git Bisect for Debugging](#git-bisect-for-debugging)
- [Reflog for Recovery](#reflog-for-recovery)
- [Git Worktrees](#git-worktrees)
- [Sparse Checkout](#sparse-checkout)
- [Shallow Clones](#shallow-clones)
- [Git Internals and Plumbing Commands](#git-internals-and-plumbing-commands)

## Interactive Rebase Mastery

### What It Is

Interactive rebase allows you to rewrite commit history by reordering, combining, editing, or removing commits.

### Basic Usage

```bash
# Rebase last 5 commits
git rebase -i HEAD~5

# Editor shows:
pick c7f8a9b feat: add login
pick d4e6f2a fix: typo
pick a1b2c3d feat: add logout
pick e5f6g7h wip: testing
pick f8g9h1i docs: update readme

# Change to clean up history:
pick c7f8a9b feat: add login
fixup d4e6f2a fix: typo
pick a1b2c3d feat: add logout
drop e5f6g7h wip: testing
reword f8g9h1i docs: update readme
```

### Commands Available

- **pick** - Use commit as-is
- **reword** - Edit commit message
- **edit** - Stop to amend commit
- **squash** - Meld into previous, keep both messages
- **fixup** - Meld into previous, discard this message
- **drop** - Remove commit
- **exec** - Run shell command

### Example: Squashing Commits

```bash
# Squash all feature commits into one
git rebase -i main

pick c7f8a9b feat: start feature
squash d4e6f2a feat: continue work
squash a1b2c3d feat: add tests
squash e5f6g7h feat: complete feature

# Results in one clean commit
```

### Autosquash Workflow

```bash
# Create commit that fixes earlier commit
git commit --fixup=c7f8a9b

# Later, autosquash automatically arranges fixups
git rebase -i --autosquash main

# Enable by default
git config --global rebase.autosquash true
```

---

## Cherry-Picking Strategies

### What It Is

Apply specific commits from one branch to another.

### Basic Cherry-Pick

```bash
# Apply single commit
git cherry-pick abc123

# Apply multiple commits
git cherry-pick abc123 def456

# Apply range
git cherry-pick abc123..def456

# Cherry-pick without committing
git cherry-pick -n abc123
```

### Use Case: Hotfix to Multiple Branches

```bash
# Hotfix in main
git checkout main
git commit -m "fix: critical bug"  # abc123

# Apply to release branch
git checkout release/v1.2
git cherry-pick abc123

# Apply to develop
git checkout develop
git cherry-pick abc123
```

---

## Git Bisect for Debugging

### What It Is

Binary search to find the commit that introduced a bug.

### Manual Bisect

```bash
# Start bisect
git bisect start
git bisect bad              # Current is bad
git bisect good v1.0.0      # Known good version

# Git checks out middle commit
# Test and mark:
git bisect good    # or git bisect bad

# Repeat until found
# Git identifies culprit commit
git bisect reset
```

### Automated Bisect

```bash
# Create test script
cat > test.sh << 'EOF'
#!/bin/bash
npm test
EOF

# Run automated bisect
git bisect start
git bisect bad HEAD
git bisect good v1.0.0
git bisect run ./test.sh

# Git finds bad commit automatically
```

---

## Reflog for Recovery

### What It Is

Reflog records every HEAD movement, enabling recovery from mistakes.

### Common Recovery Scenarios

**Accidental Reset:**
```bash
# Reset too far
git reset --hard HEAD~10

# Find lost commits
git reflog
# abc123 HEAD@{1}: commit: lost work

# Recover
git reset --hard HEAD@{1}
```

**Deleted Branch:**
```bash
# Branch deleted
git branch -D important-feature

# Find in reflog
git reflog | grep "important-feature"
# abc123 HEAD@{5}: commit: feature work

# Restore
git checkout -b important-feature abc123
```

**Bad Rebase:**
```bash
# Rebase went wrong
git reflog
# jkl012 HEAD@{3}: rebase: start (before rebase)

# Return to pre-rebase state
git reset --hard HEAD@{3}
```

### Time-Based Recovery

```bash
# Go back to specific time
git reset --hard HEAD@{5.minutes.ago}
git reset --hard HEAD@{yesterday}
```

---

## Git Worktrees

### What It Is

Multiple working directories for the same repository.

### Basic Usage

```bash
# Add worktree
git worktree add ../project-feature feature/new-feature

# List worktrees
git worktree list

# Remove worktree
git worktree remove ../project-feature
```

### Use Cases

**Parallel Development:**
```bash
# Working on feature, bug comes up
git worktree add ../project-hotfix -b hotfix/urgent main

cd ../project-hotfix
# Fix bug here

cd ../project
# Continue feature work
```

**Code Review:**
```bash
# Review PR without switching branches
git worktree add ../project-review pr-123

cd ../project-review
# Review code

cd ../project
# Back to your work
```

---

## Sparse Checkout

### What It Is

Checkout only specific directories from repository.

### Setup

```bash
# Clone with sparse checkout
git clone --sparse https://github.com/user/repo.git
cd repo

# Add directories
git sparse-checkout add frontend/
git sparse-checkout add shared/utils/

# Only these directories checked out
```

### Use Case: Monorepo

```bash
# Large monorepo, only need one service
git clone --sparse https://github.com/company/monorepo.git
cd monorepo
git sparse-checkout add services/auth/
git sparse-checkout add shared/

# Working tree only contains needed parts
```

---

## Shallow Clones

### What It Is

Clone only recent history, not full history.

### Creating Shallow Clones

```bash
# Clone last commit only
git clone --depth 1 https://github.com/user/repo.git

# Clone last 10 commits
git clone --depth 10 https://github.com/user/repo.git

# Clone since date
git clone --shallow-since="2024-01-01" https://github.com/user/repo.git
```

### Converting

```bash
# Deepen shallow clone
git fetch --depth=100
git fetch --unshallow  # Fetch all

# Make shallow
git fetch --depth=1
```

### CI/CD Usage

```yaml
# GitHub Actions
- uses: actions/checkout@v3
  with:
    fetch-depth: 1  # Shallow for speed
```

---

## Git Internals and Plumbing Commands

### Object Model

```bash
# View object type
git cat-file -t abc123
# commit

# View object content
git cat-file -p abc123
# tree def456
# parent ghi789
# author ...

# View tree
git cat-file -p def456
# 100644 blob a1b2c3d README.md
# 040000 tree i9j0k1l src
```

### Exploring Repository

```bash
# Show all objects
find .git/objects -type f

# Count objects
git count-objects -v

# Verify integrity
git fsck --full
```

### Manual Object Creation

```bash
# Create blob
echo "Hello" | git hash-object --stdin -w

# Write tree
git write-tree

# Create commit
echo "Initial" | git commit-tree <tree-sha>

# Update ref
git update-ref refs/heads/main <commit-sha>
```

---

## Summary

Advanced Git techniques provide:
- **Clean history** via interactive rebase
- **Selective porting** with cherry-pick
- **Efficient debugging** using bisect
- **Recovery safety** with reflog
- **Parallel work** through worktrees
- **Performance** from sparse/shallow clones
- **Deep understanding** of Git internals

Master these to become a Git expert.
