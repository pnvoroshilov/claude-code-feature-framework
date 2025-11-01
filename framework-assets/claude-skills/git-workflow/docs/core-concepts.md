# Core Concepts - Git Workflow Fundamentals

## Table of Contents

- [Distributed Version Control Model](#distributed-version-control-model)
- [The Three States](#the-three-states)
- [Git Object Model](#git-object-model)
- [Commits and History](#commits-and-history)
- [Branches and References](#branches-and-references)
- [Remote Repositories](#remote-repositories)
- [HEAD and Detached HEAD](#head-and-detached-head)
- [Merge Base and Common Ancestors](#merge-base-and-common-ancestors)
- [Tracking Branches](#tracking-branches)
- [The Index (Staging Area)](#the-index-staging-area)
- [Refs and Reflog](#refs-and-reflog)
- [Git Workflow Models](#git-workflow-models)

## Distributed Version Control Model

### What It Is

Git is a **distributed version control system (DVCS)**, meaning every developer has a complete copy of the entire repository history on their local machine. Unlike centralized version control systems (CVS, SVN), there is no single "master" repository that everyone must connect to.

### Why It Matters

This distributed nature provides several critical advantages:
- **Work offline** - Full version control capabilities without network connection
- **Fast operations** - Most operations are local and instantaneous
- **Redundancy** - Every clone is a full backup of the repository
- **Flexible workflows** - Teams can structure workflows to match their needs
- **Branching and merging** - Extremely lightweight and fast

### How It Works

When you clone a repository, Git downloads the entire history:
```bash
# Clone includes all commits, branches, and tags
git clone https://github.com/user/repo.git

# You now have:
# - Complete commit history
# - All branches (local copies)
# - Full repository metadata
# - Ability to work completely offline
```

Each developer's repository is equal in status. The "origin" remote is just a convention - there's nothing technically special about it. This enables workflows like:
- Multiple remote repositories
- Peer-to-peer collaboration
- Hierarchical team structures
- Fork-based workflows

### Examples

**Multiple remotes for different purposes:**
```bash
# Add company remote
git remote add company git@company-gitlab.com:team/project.git

# Add personal fork
git remote add fork git@github.com:myusername/project.git

# Push to different remotes
git push company main          # Company's main branch
git push fork feature-branch   # Your experimental work
```

**Working offline:**
```bash
# All of these work without internet:
git log                        # View history
git checkout -b feature        # Create branch
git commit -m "Add feature"    # Commit changes
git rebase main               # Rebase your work

# Only push requires network:
git push origin feature        # Upload to remote
```

### Related Concepts
- [Remote Repositories](#remote-repositories)
- [Tracking Branches](#tracking-branches)

---

## The Three States

### What It Is

Git manages files in three distinct states:
1. **Modified** - File changed but not staged
2. **Staged** - File marked for inclusion in next commit
3. **Committed** - Data safely stored in local repository

These states correspond to three main sections of a Git project:
- **Working Directory** - Where you edit files
- **Staging Area (Index)** - Where you prepare commits
- **Repository (.git directory)** - Where commits are permanently stored

### Why It Matters

Understanding the three states is fundamental to Git workflow because:
- **Precise control** - Choose exactly what goes into each commit
- **Atomic commits** - Group related changes logically
- **Review before commit** - Inspect staged changes before committing
- **Partial staging** - Commit portions of files independently

### How It Works

The typical flow through these states:
```bash
# 1. MODIFIED: Edit a file
echo "new feature" >> feature.txt
git status  # Shows: modified: feature.txt

# 2. STAGED: Add to staging area
git add feature.txt
git status  # Shows: Changes to be committed

# 3. COMMITTED: Commit to repository
git commit -m "feat: add new feature"
git status  # Shows: nothing to commit, working tree clean
```

### Examples

**Working with multiple states:**
```bash
# Modify three files
echo "fix bug" >> bugfix.js
echo "new feature" >> feature.js
echo "update docs" >> README.md

# Check status - all modified
git status
# modified: bugfix.js
# modified: feature.js
# modified: README.md

# Stage only bug fix and feature
git add bugfix.js feature.js

# Commit bug fix and feature (docs stay modified)
git commit -m "fix: resolve bug and add feature"

# Docs remain in working directory (modified)
# Can commit separately later
git add README.md
git commit -m "docs: update README"
```

**Unstaging files:**
```bash
# Stage files
git add file1.txt file2.txt

# Changed your mind about file2
git reset HEAD file2.txt  # Unstage file2, keeps modifications

# file1 is staged, file2 is modified but not staged
```

**Viewing differences between states:**
```bash
# See unstaged changes (working dir vs staging)
git diff

# See staged changes (staging vs last commit)
git diff --staged

# See all changes (working dir vs last commit)
git diff HEAD
```

### Common Mistakes
- **Committing too much** - Always review `git diff --staged` before committing
- **Forgetting to stage** - Changes must be staged before committing
- **Confusing states** - Use `git status` frequently to understand current state

### Related Concepts
- [The Index (Staging Area)](#the-index-staging-area)
- [Commits and History](#commits-and-history)

---

## Git Object Model

### What It Is

Git stores all data as **objects** in a content-addressable filesystem. There are four types of objects:
1. **Blob** - Stores file content
2. **Tree** - Stores directory structure and file names
3. **Commit** - Points to a tree and contains metadata
4. **Tag** - Points to a commit with additional metadata

Each object is identified by a SHA-1 hash of its content.

### Why It Matters

Understanding Git's object model helps you:
- **Understand how Git stores data** - Files are stored once, referenced many times
- **Reason about repository size** - Why large files are problematic
- **Understand commit relationships** - How commits link together
- **Debug issues** - When things go wrong, you can inspect objects directly
- **Optimize repositories** - Know what takes up space

### How It Works

Every commit points to a tree representing the entire project state at that moment:

```
Commit (c7f8a9)
  ├── tree (a3b5c8)
  │   ├── blob (file1.txt) - d4e6f2
  │   ├── blob (file2.js)  - b8c9d1
  │   └── tree (src/)
  │       ├── blob (index.js) - a1b2c3
  │       └── blob (util.js)  - e5f6g7
  ├── parent (b4d6e8)
  ├── author "John Doe"
  ├── committer "John Doe"
  └── message "feat: add new feature"
```

### Examples

**Inspecting objects:**
```bash
# View commit object
git cat-file -p HEAD
# tree a3b5c8...
# parent b4d6e8...
# author John Doe <john@example.com> 1634567890 +0000
# committer John Doe <john@example.com> 1634567890 +0000
#
# feat: add new feature

# View tree object
git cat-file -p a3b5c8
# 100644 blob d4e6f2... file1.txt
# 100644 blob b8c9d1... file2.js
# 040000 tree f8g9h1... src

# View blob object (file content)
git cat-file -p d4e6f2
# Hello, World!
```

**Content addressability means:**
```bash
# Same content = same hash
echo "test" > file1.txt
echo "test" > file2.txt

# Both files share the same blob object
git add file1.txt file2.txt
git ls-files -s
# 100644 9daeafb9864cf43055ae93beb0afd6c7d144bfa4 0 file1.txt
# 100644 9daeafb9864cf43055ae93beb0afd6c7d144bfa4 0 file2.txt
#        ^^^ Same hash - stored once!
```

**Why commits are immutable:**
```bash
# Commit hash depends on:
# - Tree hash (all file contents)
# - Parent commit hash
# - Author/committer info
# - Timestamp
# - Commit message

# Changing ANY of these creates a NEW commit with different hash
# This is why rewriting history creates new commits
```

### Related Concepts
- [Commits and History](#commits-and-history)
- [Refs and Reflog](#refs-and-reflog)

---

## Commits and History

### What It Is

A **commit** is a snapshot of your project at a specific point in time. It includes:
- Complete snapshot of all tracked files
- Reference to parent commit(s)
- Author and committer information
- Timestamp
- Commit message describing changes

Commits form a **directed acyclic graph (DAG)** - each commit points to its parent(s), creating a history.

### Why It Matters

Commits are the fundamental unit of Git history:
- **Track changes over time** - See how project evolved
- **Identify what changed** - Know exactly what each commit did
- **Enable collaboration** - Share specific units of work
- **Allow rollback** - Return to any previous state
- **Support branching** - Diverge and converge development paths

### How It Works

**Linear history (single branch):**
```
A---B---C---D  (main)
```

**Branching history:**
```
A---B---C---F---G  (main)
     \
      D---E  (feature)
```

**Merged history:**
```
A---B---C---F---G---H  (main)
     \             /
      D-----------E  (feature - merged)
```

### Examples

**Creating meaningful commits:**
```bash
# Bad: Too broad
git add .
git commit -m "updates"

# Good: Specific, atomic change
git add src/auth/login.ts tests/auth.test.ts
git commit -m "feat(auth): implement JWT token validation

- Add JWT verification middleware
- Validate token expiration
- Add unit tests for token validation
- Update auth documentation

Closes #123"
```

**Viewing commit history:**
```bash
# Simple log
git log

# One line per commit
git log --oneline

# With graph visualization
git log --graph --oneline --all

# With file changes
git log --stat

# Specific file history
git log -- src/auth.js

# Commits by specific author
git log --author="John Doe"

# Commits in date range
git log --since="2 weeks ago"
```

**Commit anatomy:**
```bash
git show HEAD
# commit c7f8a9b2d3e4f5g6h7i8j9k0l1m2n3o4p5q6r7s8
# Author: John Doe <john@example.com>
# Date:   Mon Oct 18 10:30:00 2024 -0400
#
#     feat(auth): implement JWT token validation
#
#     - Add JWT verification middleware
#     - Validate token expiration
#     - Add unit tests for token validation
#
#     Closes #123
#
# diff --git a/src/auth.js b/src/auth.js
# [... file changes ...]
```

**Amending the last commit:**
```bash
# Oops, forgot to add a file
git add forgotten-file.js
git commit --amend --no-edit

# Fix commit message
git commit --amend -m "feat(auth): implement JWT validation with tests"
```

### Best Practices

**Atomic commits:**
Each commit should:
- Contain one logical change
- Be independently buildable
- Have a clear, single purpose
- Include related tests

**Commit message structure:**
```
<type>(<scope>): <subject>

<body>

<footer>
```

Example:
```
feat(dashboard): add real-time analytics widget

- Implement WebSocket connection for live data
- Add animated chart component
- Create data transformation utilities
- Add error handling for connection failures

Closes #456
Reviewed-by: Jane Smith
```

### Common Mistakes
- **Too many changes in one commit** - Makes review and revert difficult
- **Vague commit messages** - Future developers won't understand why
- **Breaking commits** - Each commit should leave project in working state
- **Missing context** - Commit message should explain "why", not just "what"

### Related Concepts
- [Git Object Model](#git-object-model)
- [Branches and References](#branches-and-references)

---

## Branches and References

### What It Is

A **branch** is simply a lightweight movable pointer to a commit. Creating a branch creates a new pointer - it doesn't copy files or commits. The default branch is typically called `main` or `master`.

**References (refs)** are human-readable names for commits:
- `refs/heads/*` - Local branches
- `refs/remotes/*` - Remote-tracking branches
- `refs/tags/*` - Tags

### Why It Matters

Branches enable:
- **Parallel development** - Multiple features simultaneously
- **Experimentation** - Try ideas without affecting main code
- **Organization** - Separate concerns (features, bugs, releases)
- **Collaboration** - Multiple developers working independently
- **Risk-free changes** - Easy to create, merge, or delete

### How It Works

```bash
# Branch is just a file containing a commit hash
cat .git/refs/heads/main
# c7f8a9b2d3e4f5g6h7i8j9k0l1m2n3o4p5q6r7s8

# Creating a branch just creates a new file
git branch feature
# Creates .git/refs/heads/feature with same hash
```

**Branch visualization:**
```
Before creating feature branch:
A---B---C  (main)
        ↑
      HEAD

After "git checkout -b feature":
A---B---C  (main, feature)
        ↑
      HEAD (feature)

After committing to feature:
A---B---C  (main)
        \
         D  (feature)
            ↑
          HEAD
```

### Examples

**Basic branch operations:**
```bash
# Create new branch
git branch feature/new-dashboard

# Create and switch to new branch
git checkout -b feature/user-auth

# Or using modern syntax
git switch -c feature/user-auth

# List all branches
git branch              # Local branches
git branch -r           # Remote branches
git branch -a           # All branches

# Rename branch
git branch -m old-name new-name

# Delete branch
git branch -d feature-branch        # Safe delete (only if merged)
git branch -D feature-branch        # Force delete
```

**Branch naming conventions:**
```bash
# Feature branches
feature/user-authentication
feature/dashboard-widget
feat/payment-integration

# Bug fix branches
bugfix/login-error
fix/memory-leak
hotfix/production-crash

# Release branches
release/v1.2.0
release/2024-Q1

# Experimental branches
experiment/new-architecture
spike/performance-test
```

**Tracking relationships:**
```bash
# See which remote branch a local branch tracks
git branch -vv

# Set upstream branch
git branch --set-upstream-to=origin/feature

# Push and set upstream in one command
git push -u origin feature

# Pull from tracked branch
git pull  # Fetches and merges from upstream
```

**Branch comparison:**
```bash
# See commits in feature not in main
git log main..feature

# See commits in main not in feature
git log feature..main

# See commits in either but not both
git log main...feature

# See file differences between branches
git diff main..feature

# List files that differ
git diff --name-only main..feature
```

### Best Practices

**Short-lived branches:**
- Keep feature branches alive for days/weeks, not months
- Merge or close branches promptly
- Rebase regularly to stay current with main

**Clear naming:**
- Use consistent prefixes (feature/, bugfix/, hotfix/)
- Include issue number when applicable (feature/123-user-auth)
- Make purpose obvious from name

**Branch protection:**
```bash
# On GitHub/GitLab, protect main branch:
# - Require PR before merging
# - Require status checks to pass
# - Require review approvals
# - Prevent force push
# - Prevent deletion
```

### Common Mistakes
- **Long-lived branches** - Get out of sync with main, difficult to merge
- **Committing to main directly** - Bypasses review process
- **Too many active branches** - Hard to track and maintain
- **Not deleting merged branches** - Clutters repository

### Related Concepts
- [HEAD and Detached HEAD](#head-and-detached-head)
- [Remote Repositories](#remote-repositories)
- [Tracking Branches](#tracking-branches)

---

## Remote Repositories

### What It Is

A **remote repository** is a version of your project hosted elsewhere (GitHub, GitLab, Bitbucket, or even another directory on your machine). You can have multiple remotes, each with a name (typically "origin" for the main remote).

### Why It Matters

Remotes enable:
- **Collaboration** - Share code with team
- **Backup** - Repository stored in multiple locations
- **CI/CD integration** - Automated testing and deployment
- **Code review** - Pull request workflows
- **Access control** - Manage who can read/write

### How It Works

```bash
# View remotes
git remote -v
# origin  git@github.com:user/repo.git (fetch)
# origin  git@github.com:user/repo.git (push)

# Remotes have URLs and are bidirectional
# - fetch URL: where you pull from
# - push URL: where you push to (usually same)
```

### Examples

**Adding and managing remotes:**
```bash
# Add remote
git remote add origin git@github.com:user/repo.git

# Add additional remotes
git remote add upstream git@github.com:original/repo.git
git remote add backup git@backup-server.com:user/repo.git

# Change remote URL
git remote set-url origin git@gitlab.com:user/repo.git

# Rename remote
git remote rename origin github

# Remove remote
git remote remove backup

# View detailed remote info
git remote show origin
```

**Fetching and pulling:**
```bash
# Fetch updates all remote tracking branches
git fetch origin
# origin/main updated
# origin/feature updated

# Fetch all remotes
git fetch --all

# Fetch and prune deleted branches
git fetch --prune

# Pull = fetch + merge
git pull origin main

# Pull with rebase instead of merge
git pull --rebase origin main
```

**Pushing:**
```bash
# Push branch to remote
git push origin feature

# Push and set upstream
git push -u origin feature

# Push all branches
git push --all origin

# Push tags
git push --tags

# Force push (dangerous!)
git push --force origin feature

# Safer force push (only if no one else pushed)
git push --force-with-lease origin feature

# Delete remote branch
git push origin --delete feature
```

**Working with forks:**
```bash
# Common fork workflow setup
git clone git@github.com:yourname/repo.git
cd repo

# Add upstream (original repository)
git remote add upstream git@github.com:original/repo.git

# Fetch upstream changes
git fetch upstream

# Merge upstream into your fork
git checkout main
git merge upstream/main

# Push to your fork
git push origin main
```

### Best Practices

**Regular synchronization:**
```bash
# Daily workflow
git fetch origin          # See what's new
git pull --rebase         # Update your branch
git push origin feature   # Share your work
```

**Safe force pushing:**
```bash
# NEVER force push to shared branches (main, develop)
# OK to force push to personal feature branches

# Use --force-with-lease to prevent overwriting others' work
git push --force-with-lease origin feature
```

**Multiple remotes strategy:**
```bash
# Company GitLab (internal)
git remote add company git@company-gitlab.com:team/project.git

# Personal GitHub (external)
git remote add github git@github.com:username/project.git

# Push to different remotes as needed
git push company main      # Internal deployment
git push github public     # Public release
```

### Common Mistakes
- **Force pushing shared branches** - Destroys teammates' work
- **Not fetching regularly** - Get out of sync with team
- **Pushing to wrong remote** - Check remote before pushing
- **Forgetting upstream** - Lose connection to original repository

### Related Concepts
- [Tracking Branches](#tracking-branches)
- [Distributed Version Control Model](#distributed-version-control-model)

---

## HEAD and Detached HEAD

### What It Is

**HEAD** is a special reference that points to the current branch or commit. It represents "where you are" in the repository.

**Detached HEAD** occurs when HEAD points directly to a commit instead of a branch. You're no longer "on" a branch.

### Why It Matters

Understanding HEAD helps you:
- **Know your current position** in the repository
- **Understand what commits will update** when you commit
- **Avoid losing work** in detached HEAD state
- **Navigate repository history** safely

### How It Works

**Normal state (HEAD points to branch):**
```bash
cat .git/HEAD
# ref: refs/heads/main

# HEAD → main → commit C
#
# A---B---C  (main)
#         ↑
#        HEAD
```

**Detached HEAD (HEAD points to commit):**
```bash
cat .git/HEAD
# c7f8a9b2d3e4f5g6h7i8j9k0l1m2n3o4p5q6r7s8

# HEAD → commit B directly
#
# A---B---C  (main)
#     ↑
#    HEAD
```

### Examples

**Entering detached HEAD state:**
```bash
# Checkout specific commit
git checkout c7f8a9

# Checkout tag
git checkout v1.0.0

# Checkout remote branch without creating local branch
git checkout origin/main

# Git warns you:
# Note: switching to 'c7f8a9'.
# You are in 'detached HEAD' state...
```

**Working in detached HEAD:**
```bash
# You're in detached HEAD on old commit
git log --oneline
# c7f8a9 (HEAD) old commit
# a1b2c3 older commit

# Make changes and commit
echo "test" > test.txt
git add test.txt
git commit -m "test commit"

# New commit created but not on any branch!
#
# A---B---C  (main)
#     \
#      D  (HEAD - orphaned!)
```

**Saving work from detached HEAD:**
```bash
# Option 1: Create branch at current position
git checkout -b feature/from-detached
# Now your commit is on feature/from-detached branch

# Option 2: Note the commit hash
git log --oneline -1
# d4e6f8 (HEAD) test commit

# Return to main and cherry-pick
git checkout main
git cherry-pick d4e6f8
```

**Abandoning work from detached HEAD:**
```bash
# Just checkout a branch - commits will be garbage collected
git checkout main
# Warning: you are leaving 1 commit behind, not connected to any branches

# If you need it later, find it in reflog
git reflog
# c7f8a9 HEAD@{0}: checkout: moving to main
# d4e6f8 HEAD@{1}: commit: test commit
```

### Best Practices

**Avoid working in detached HEAD:**
- If you need to make changes to old code, create a branch first
- Detached HEAD is for exploration, not development

**Safe exploration:**
```bash
# Want to look at old code? Use detached HEAD for viewing
git checkout v1.0.0
# Look around, run tests
git log
git diff v1.1.0

# Return to branch when done
git checkout main
```

**Creating branch before committing:**
```bash
# You realize you're in detached HEAD and want to commit
# Create branch FIRST
git checkout -b fix/old-bug

# Now you can commit safely
git commit -m "fix: resolve bug in old version"
```

### Common Mistakes
- **Committing in detached HEAD** - Commits not on any branch, easy to lose
- **Not understanding the warning** - Git tells you, but it's easy to ignore
- **Forgetting commit hash** - Hard to recover work later

### Related Concepts
- [Branches and References](#branches-and-references)
- [Refs and Reflog](#refs-and-reflog)

---

## Merge Base and Common Ancestors

### What It Is

The **merge base** is the most recent common ancestor of two branches. It's the commit where the branches diverged.

**Common ancestor** is any commit that is reachable from both branches.

### Why It Matters

Understanding merge base helps with:
- **Three-way merges** - Git finds the merge base to determine what changed in each branch
- **Rebase operations** - Rebase replays commits since the merge base
- **Conflict understanding** - Conflicts occur when both branches modified the same lines since merge base
- **Comparing branches** - See what each branch added since divergence

### How It Works

**Simple case:**
```
A---B---C  (main)
     \
      D---E  (feature)
```
Merge base of main and feature is commit B (where they diverged).

**Complex case with multiple merges:**
```
A---B---C---F---G  (main)
     \         /
      D-------E  (feature)
```
Even after merges, merge base is the most recent common ancestor.

### Examples

**Finding merge base:**
```bash
# Find merge base of two branches
git merge-base main feature
# b4d6e8a1c2f3g4h5i6j7k8l9m0n1o2p3q4r5s6t7

# View the merge base commit
git show $(git merge-base main feature)

# Compare branch to merge base
git diff $(git merge-base main feature)..feature
# Shows what feature added since diverging from main
```

**Three-way merge visualization:**
```bash
# Before merge:
#
#      [Merge Base]
#      /          \
#   [Main]      [Feature]
#
# Git compares:
# 1. Merge base → Main (what main changed)
# 2. Merge base → Feature (what feature changed)
# 3. Combines both sets of changes

# If both branches modified same lines = conflict
```

**Using merge base for comparison:**
```bash
# See all commits in feature not in main
git log $(git merge-base main feature)..feature

# See commits in main not in feature
git log $(git merge-base main feature)..main

# Compare files changed since divergence
git diff $(git merge-base main feature)..feature -- src/

# Use triple dot syntax (shorthand for merge base)
git log main...feature
git diff main...feature
```

**Rebasing changes merge base:**
```bash
# Before rebase:
#
# A---B---C---F  (main)
#      \
#       D---E  (feature)
# Merge base: B

# After "git rebase main" on feature:
#
# A---B---C---F  (main)
#              \
#               D'---E'  (feature)
# Merge base: F (updated!)
```

### Best Practices

**Use triple-dot syntax:**
```bash
# These are equivalent:
git diff $(git merge-base main feature)..feature
git diff main...feature  # Easier!

git log $(git merge-base main feature)..feature
git log main...feature  # Easier!
```

**Understanding conflicts:**
```bash
# When merge conflicts occur:
# 1. Find merge base
git merge-base HEAD MERGE_HEAD

# 2. View what changed in each branch
git diff $(git merge-base HEAD MERGE_HEAD)..HEAD
git diff $(git merge-base HEAD MERGE_HEAD)..MERGE_HEAD

# 3. Understand why conflict happened
# Both branches modified same lines since merge base
```

### Related Concepts
- [Commits and History](#commits-and-history)
- [Branches and References](#branches-and-references)

---

## Tracking Branches

### What It Is

A **tracking branch** (or upstream branch) is a local branch that has a direct relationship with a remote branch. When you push/pull without specifying a branch, Git uses the tracking relationship.

### Why It Matters

Tracking branches enable:
- **Simplified push/pull** - No need to specify remote and branch
- **Status information** - See if you're ahead/behind remote
- **Branch synchronization** - Keep local and remote in sync
- **Convenient workflows** - Less typing, fewer errors

### How It Works

```bash
# Tracking relationship stored in .git/config
[branch "main"]
    remote = origin
    merge = refs/heads/main

# Now these commands work without arguments:
git push   # Pushes to origin/main
git pull   # Pulls from origin/main
```

### Examples

**Setting up tracking:**
```bash
# Method 1: Clone sets up tracking automatically
git clone git@github.com:user/repo.git
# main branch tracks origin/main automatically

# Method 2: Push with -u sets up tracking
git checkout -b feature
git push -u origin feature
# Local feature now tracks origin/feature

# Method 3: Set tracking explicitly
git branch --set-upstream-to=origin/feature feature

# Method 4: Checkout remote branch creates tracking
git checkout feature
# If remote origin/feature exists, creates local feature that tracks it
```

**Viewing tracking information:**
```bash
# See tracking branches with status
git branch -vv
# * feature  c7f8a9 [origin/feature: ahead 2] Latest commit
#   main     b4d6e8 [origin/main] Synced with remote
#   hotfix   a1b2c3 [origin/hotfix: behind 1] Old commit

# See remote branches
git branch -r
# origin/HEAD -> origin/main
# origin/feature
# origin/main

# See detailed tracking info
git remote show origin
```

**Using tracking branches:**
```bash
# With tracking set up:
git pull              # Pulls from tracking branch
git push              # Pushes to tracking branch
git status            # Shows ahead/behind status

# Without tracking:
git pull origin feature    # Must specify
git push origin feature    # Must specify
git status                 # No remote status
```

**Ahead/behind status:**
```bash
git status
# On branch feature
# Your branch is ahead of 'origin/feature' by 2 commits.
#   (use "git push" to publish your local commits)

# After making commits locally, you're "ahead"
# After someone else pushes, you're "behind"
# After diverging, you're "ahead and behind"

# See commits you're ahead by
git log origin/feature..HEAD

# See commits you're behind by
git log HEAD..origin/feature
```

### Best Practices

**Always use -u for first push:**
```bash
# Creates branch and sets tracking in one command
git push -u origin feature

# Now all future operations are simple
git push
git pull
git status  # Shows sync status
```

**Keep tracking branches in sync:**
```bash
# Daily workflow
git fetch               # Update remote tracking info
git status              # See if behind
git pull --rebase       # Update local branch
```

**Clean up tracking for deleted remotes:**
```bash
# Remove remote tracking branches for deleted remotes
git fetch --prune

# Or configure to always prune
git config --global fetch.prune true
```

### Common Mistakes
- **Not setting upstream** - Have to specify remote/branch every time
- **Forgetting to fetch** - Status info becomes stale
- **Force pushing** - Can break tracking for others

### Related Concepts
- [Remote Repositories](#remote-repositories)
- [Branches and References](#branches-and-references)

---

## The Index (Staging Area)

### What It Is

The **index** (also called staging area or cache) is an intermediate area between your working directory and repository. It holds the snapshot that will become your next commit.

### Why It Matters

The index provides:
- **Selective commits** - Choose exactly what goes into each commit
- **Atomic commits** - Group related changes logically
- **Review opportunity** - Inspect changes before committing
- **Partial staging** - Stage portions of files

### How It Works

The index is stored in `.git/index` and tracks:
- File names and paths
- File content hashes (blob objects)
- File metadata (permissions, timestamps)

When you `git add`, file content is:
1. Hashed and stored as blob object in `.git/objects/`
2. Recorded in index with file path

### Examples

**Selective staging:**
```bash
# Stage specific files
git add src/feature.js tests/feature.test.js

# Stage specific directories
git add src/components/

# Stage all modified files
git add -u

# Stage all files (new and modified)
git add .

# Stage interactively
git add -i

# Stage patches of files
git add -p
```

**Interactive staging (patch mode):**
```bash
git add -p feature.js

# Git shows each change:
# @@ -10,3 +10,7 @@ function calculate() {
# +  // Add validation
# +  if (!input) return 0;
#    return input * 2;
#  }
#
# Stage this hunk [y,n,q,a,d,/,s,e,?]?

# Options:
# y - stage this hunk
# n - don't stage
# s - split into smaller hunks
# e - manually edit hunk
# q - quit
```

**Viewing index state:**
```bash
# See what's staged
git diff --staged
git diff --cached  # Same thing

# See what's not staged
git diff

# See index contents
git ls-files -s
# 100644 d4e6f2... 0    src/feature.js
# 100644 b8c9d1... 0    tests/feature.test.js
```

**Unstaging:**
```bash
# Unstage specific file (keep changes)
git reset HEAD feature.js

# Unstage all files (keep changes)
git reset HEAD

# Unstage and discard changes (dangerous!)
git checkout HEAD feature.js
```

### Best Practices

**Review before committing:**
```bash
# Always check what you're committing
git diff --staged

# Or use git's built-in review
git commit --verbose  # Shows diff in commit message editor
```

**Use patch mode for precision:**
```bash
# When file has multiple unrelated changes
git add -p feature.js

# Stage only the bug fix, leave refactoring for separate commit
```

**Stage related changes together:**
```bash
# Good: Related changes in one commit
git add src/auth.js tests/auth.test.js docs/auth.md
git commit -m "feat(auth): add JWT validation"

# Bad: Unrelated changes in one commit
git add .
git commit -m "various changes"
```

### Related Concepts
- [The Three States](#the-three-states)
- [Commits and History](#commits-and-history)

---

## Refs and Reflog

### What It Is

**Refs** (references) are human-readable names for commits:
- Local branches: `refs/heads/*`
- Remote branches: `refs/remotes/*`
- Tags: `refs/tags/*`

**Reflog** is Git's safety net - it records when refs (like HEAD) were updated, creating a local history of where you've been.

### Why It Matters

- **Recovery** - Reflog helps recover "lost" commits
- **Debugging** - See what you did and when
- **Undo mistakes** - Return to previous state
- **Navigation** - Reference historical positions

### How It Works

Every time HEAD moves, Git records it in the reflog:
```bash
# View reflog
git reflog
# c7f8a9 HEAD@{0}: commit: feat: add feature
# b4d6e8 HEAD@{1}: checkout: moving from main to feature
# a1b2c3 HEAD@{2}: pull: Fast-forward
```

### Examples

**Using reflog for recovery:**
```bash
# Oh no! Accidentally reset hard
git reset --hard HEAD~3
# Lost 3 commits!

# Check reflog
git reflog
# a1b2c3 HEAD@{0}: reset: moving to HEAD~3
# b4d6e8 HEAD@{1}: commit: feat: lost commit 1
# c7f8a9 HEAD@{2}: commit: feat: lost commit 2
# d1e2f3 HEAD@{3}: commit: feat: lost commit 3

# Recover by resetting to before the mistake
git reset --hard HEAD@{3}
# Back to d1e2f3, all commits recovered!
```

**Reflog references:**
```bash
# Reference by position
HEAD@{0}   # Current HEAD
HEAD@{1}   # Previous HEAD position
HEAD@{2}   # Two positions ago

# Reference by time
HEAD@{5.minutes.ago}
HEAD@{yesterday}
HEAD@{2.weeks.ago}

# Use in commands
git diff HEAD@{yesterday}
git show HEAD@{2}
git reset --hard HEAD@{5.minutes.ago}
```

**Branch reflogs:**
```bash
# Each branch has its own reflog
git reflog show feature
# Shows history of feature branch

git reflog show origin/main
# Shows history of remote branch updates
```

**Finding lost commits:**
```bash
# After deleting a branch, commits still in reflog
git reflog --all
# Shows reflog for all refs

# Find commit by message
git reflog | grep "important commit"

# Recover deleted branch
git branch recovered-branch <commit-hash-from-reflog>
```

### Best Practices

**Use reflog for "oh no" moments:**
```bash
# Common recovery scenarios:
# 1. Accidental reset
git reset --hard HEAD@{1}

# 2. Accidental branch delete
git reflog
git branch recovered-branch <commit-hash>

# 3. Lost commits after rebase
git reflog
git cherry-pick <commit-hash>

# 4. Undo merge
git reset --hard HEAD@{1}
```

**Reflog expiration:**
```bash
# Reflog entries expire eventually (default 90 days)
# Adjust expiration
git config --global gc.reflogExpire "never"
git config --global gc.reflogExpireUnreachable "never"

# Manually clean reflog
git reflog expire --expire=30.days --all
git gc --prune=now
```

### Common Mistakes
- **Panicking when commits seem lost** - Check reflog first!
- **Not knowing reflog exists** - It's your safety net
- **Waiting too long to recover** - Reflog expires eventually

### Related Concepts
- [HEAD and Detached HEAD](#head-and-detached-head)
- [Branches and References](#branches-and-references)

---

## Git Workflow Models

### What It Is

**Git workflow models** are standardized branching and merging strategies that teams adopt for consistent collaboration. Common models include:
- **GitFlow** - Structured with multiple long-lived branches
- **GitHub Flow** - Simple, branch-based workflow
- **Trunk-Based Development** - Minimal branching, frequent integration

### Why It Matters

Adopting a workflow model provides:
- **Consistency** - Everyone follows same process
- **Predictability** - Clear expectations for branches
- **Organization** - Structured release process
- **Scalability** - Works for teams of any size

### How They Work

**GitFlow:**
```
main (production)
  └── develop (integration)
       ├── feature/* (new features)
       ├── release/* (prep for release)
       └── hotfix/* (production fixes)
```

**GitHub Flow:**
```
main (production)
  └── feature/* (any changes)
```

**Trunk-Based:**
```
main (trunk)
  └── short-lived feature branches (hours/days)
```

### Examples

See [docs/patterns.md](patterns.md) for detailed workflow implementations.

### Related Concepts
- [Branches and References](#branches-and-references)
- [Best Practices](best-practices.md)

---

## Summary

Understanding these core concepts provides the foundation for mastering Git workflows:

1. **Distributed Model** - Every clone is a full repository
2. **Three States** - Modified, staged, committed
3. **Object Model** - Blobs, trees, commits, tags
4. **Commits** - Snapshots forming a DAG
5. **Branches** - Lightweight pointers to commits
6. **Remotes** - Repository copies elsewhere
7. **HEAD** - Current position in repository
8. **Merge Base** - Common ancestor of branches
9. **Tracking** - Branch relationships with remotes
10. **Index** - Staging area for commits
11. **Reflog** - Safety net for recovery
12. **Workflow Models** - Team collaboration patterns

Master these concepts and you'll understand not just *how* to use Git commands, but *why* they work the way they do.

**Next Steps:**
- Read [best-practices.md](best-practices.md) for professional Git standards
- Explore [patterns.md](patterns.md) for workflow implementations
- Try [examples/](../examples/) for hands-on practice
