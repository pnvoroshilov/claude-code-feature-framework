---
name: merge-skill
description: Comprehensive Git branch merging strategies, conflict resolution techniques, and best practices for handling complex merge scenarios including renamed files, binary conflicts, and large-scale refactoring
version: 1.0.0
tags: [git, merge, conflict-resolution, version-control, workflow]
---

# Git Merge & Conflict Resolution - Comprehensive Guide

## Overview

This skill provides expert guidance for Git branch merging strategies and conflict resolution. Master professional merge workflows, understand complex conflict scenarios, and learn recovery techniques used in production environments.

## What You'll Master

merge_capabilities[10]{category,description}:
Branch Strategies,Fast-forward vs 3-way merge vs rebase vs squash strategies
Pre-merge Checks,Comprehensive validation before merging branches
Conflict Detection,Understanding conflict markers and file state analysis
Manual Resolution,Step-by-step techniques for resolving different conflict types
Tool-Assisted Resolution,Using git mergetool and diff3 conflict style
Complex Scenarios,Renamed files deleted vs modified submodule conflicts
Binary Conflicts,Handling non-text files images and compiled assets
Large Refactors,Strategies for merging major architectural changes
Recovery Techniques,Aborting merges reverting and cherry-picking
Best Practices,Team collaboration conflict prevention and documentation

## Quick Start

### Basic Merge Workflow
```bash
# Update target branch
git checkout main
git pull origin main

# Merge feature branch
git merge feature/user-auth

# If conflicts occur
git status                    # See conflicted files
git diff --check             # Check conflict markers
# Resolve conflicts in editor
git add .
git commit -m "Merge feature/user-auth into main"
```

### Pre-merge Checklist
```bash
# 1. Ensure branch is up to date
git checkout feature/my-feature
git fetch origin
git rebase origin/main       # Or: git merge origin/main

# 2. Run tests
npm test                     # Or: pytest, cargo test, etc.

# 3. Review changes
git diff main..HEAD

# 4. Check for uncommitted changes
git status

# 5. Ready to merge
git checkout main
git merge feature/my-feature
```

## Core Capabilities

### 1. Merge Strategies
- **Fast-forward merge** - Linear history with `--ff-only`
- **3-way merge** - Creates merge commit with `--no-ff`
- **Squash merge** - Combines commits with `--squash`
- **Rebase merge** - Linear history via rebase then merge
- **Strategy selection** - Choose based on project needs

### 2. Conflict Resolution
- **Understanding markers** - `<<<<<<<`, `=======`, `>>>>>>>`
- **Manual resolution** - Edit files to resolve conflicts
- **Tool-assisted** - Use `git mergetool` and visual diff tools
- **Verification** - Test and validate resolutions
- **Commit** - Mark as resolved with `git add` and commit

### 3. Complex Scenarios
- **Renamed files** - Git tracks renames through conflicts
- **Deleted vs modified** - Decide to keep or remove
- **Binary conflicts** - Use `--ours` or `--theirs`
- **Lock files** - Regenerate package-lock.json, Cargo.lock
- **Large refactoring** - Strategic conflict resolution

### 4. Recovery Operations
- **Abort merge** - `git merge --abort` to cancel
- **Undo merge** - `git reset --hard ORIG_HEAD` (if not pushed)
- **Revert merge** - `git revert -m 1 <hash>` (safe for pushed)
- **Cherry-pick** - Apply specific commits after abort
- **Reflog** - Recover lost commits with `git reflog`

## Documentation

### Core Concepts
**[docs/merge-strategies.md](docs/merge-strategies.md)** - Detailed merge strategy guide:
- Fast-forward vs 3-way vs squash vs rebase
- Decision tree for strategy selection
- Examples of each strategy
- When to use which approach
- Pros and cons comparison

**[docs/conflict-resolution.md](docs/conflict-resolution.md)** - Conflict resolution techniques:
- Understanding conflict markers
- Reading complex conflicts
- Manual resolution workflow
- Using git mergetool and diff3
- Resolution strategies by scenario

**[docs/complex-scenarios.md](docs/complex-scenarios.md)** - Handling difficult merges:
- Renamed/moved files with conflicts
- Deleted vs modified conflicts
- Binary file conflicts
- Package lock file conflicts
- Large-scale refactoring conflicts

**[docs/recovery.md](docs/recovery.md)** - Undo and recovery operations:
- Aborting merges safely
- Undoing completed merges
- Recovering from mistakes
- Using git reflog
- Cherry-picking after failed merge

**[docs/best-practices.md](docs/best-practices.md)** - Professional merge workflows:
- Team conflict prevention
- Merge commit conventions
- Branch hygiene
- Communication protocols
- Automation and CI/CD

## Examples

### Basic Examples

- **[Example 1: Simple Merge Workflow](examples/simple-merge.md)** - Complete basic merge from start to finish
- **[Example 2: Resolving Text Conflicts](examples/text-conflicts.md)** - Step-by-step conflict resolution in code files
- **[Example 3: Pre-merge Validation](examples/pre-merge-checks.md)** - Automated validation script before merging

### Advanced Examples

- **[Example 4: Binary File Conflicts](examples/binary-conflicts.md)** - Handling image and asset conflicts
- **[Example 5: Refactoring Merge](examples/refactoring-merge.md)** - Merging major code restructuring
- **[Example 6: Lock File Regeneration](examples/lock-file-conflicts.md)** - Resolving package manager lock files

## Quick Reference

### Essential Commands

essential_merge_commands[15]{command,description}:
git merge <branch>,Merge specified branch into current branch
git merge --no-ff <branch>,Force merge commit even if fast-forward possible
git merge --squash <branch>,Combine all commits into one staged change
git merge --abort,Cancel merge and return to pre-merge state
git merge --continue,Continue merge after resolving conflicts
git status,Show conflicted files during merge
git diff --check,Check for conflict markers before committing
git checkout --ours <file>,Accept current branch version for file
git checkout --theirs <file>,Accept incoming branch version for file
git log --merge,Show commits involved in current conflict
git log --oneline --graph --all,Visualize branch history and merges
git mergetool,Open visual merge tool
git rerere,Reuse recorded conflict resolutions
git reset --hard ORIG_HEAD,Undo last merge (DANGER if pushed)
git revert -m 1 <hash>,Safely revert merge commit

### Conflict Markers Anatomy

```
<<<<<<< HEAD (current branch)
const API_URL = "https://api.production.com";
=======
const API_URL = "https://api.staging.com";
>>>>>>> feature/api-update (incoming branch)
```

conflict_marker_anatomy[4]{marker,meaning}:
<<<<<<< HEAD,Start of current branch changes
=======,Separator between current and incoming
>>>>>>> branch-name,End of incoming branch changes
no markers,Areas where Git successfully auto-merged

### Strategy Selection Decision Tree

```
START: Ready to merge feature branch?
│
├─> Linear history required?
│   └─> YES → Use squash merge (--squash)
│   └─> NO → Continue
│
├─> Feature branch shared with team?
│   └─> YES → Avoid rebase, use 3-way merge (--no-ff)
│   └─> NO → Continue
│
├─> Want to preserve individual commits?
│   └─> YES → Use 3-way merge (--no-ff)
│   └─> NO → Use squash merge (--squash)
│
└─> Main branch hasn't changed since branch?
    └─> YES → Fast-forward merge (--ff-only)
    └─> NO → Use 3-way merge (--no-ff)
```

## Troubleshooting

common_merge_issues[8]{issue,solution}:
Cannot merge - uncommitted changes,Commit or stash changes: git stash && git merge
Already up to date but branches differ,Force re-merge: git merge --no-ff
Conflict markers in committed code,Search codebase: grep -r "<<<<<<< " . and fix
Lost work during merge,Check reflog: git reflog for recovery
Merge created wrong result,Revert: git revert -m 1 <merge-hash>
Cannot abort merge,Reset hard: git reset --hard HEAD (DANGER)
Merged wrong branch,Undo: git reset --hard ORIG_HEAD if not pushed
Binary file always conflicts,Use .gitattributes: *.png binary -merge

### Advanced: Git Rerere

Rerere (reuse recorded resolution) remembers conflict resolutions:

```bash
# Enable rerere globally
git config --global rerere.enabled true

# Git will now automatically apply previous resolutions
# to identical conflicts in future merges/rebases

# View recorded resolutions
git rerere status

# Clear all recorded resolutions
git rerere clear
```

## Best Practices

merge_best_practices[10]{practice,explanation}:
Keep branches small,Smaller branches = fewer conflicts easier to merge
Merge frequently,Regular merges from main prevent massive conflicts
Communicate changes,Tell team about major refactors to coordinate work
Use feature flags,Deploy incomplete features behind flags
Test before merging,Always run full test suite before merge
Review merge commits,Use git log --first-parent to review
Document complex resolutions,Add comments explaining non-obvious fixes
Use branch protection,Require PR reviews prevent direct pushes
Automate checks,CI/CD must pass before merge allowed
Clean up after merge,Delete merged feature branches

### Merge Commit Message Convention

```bash
# Good merge commit message:
git merge feature/user-auth -m "Merge: Add OAuth2 authentication

Implements GitHub and Google OAuth2 providers.
Adds user session management and token refresh.

Resolves: #123
Reviewed-by: @teammate"

# For conflict resolutions:
git commit -m "Merge: Integrate API v2 with database refactor

Conflicts resolved:
- src/api/endpoints.js: Combined route changes
- src/db/schema.js: Merged schema migrations
- package-lock.json: Regenerated

Manual testing performed on staging environment."
```

## Usage in Claude Code

This skill automatically enhances Claude Code when:

1. **Merge Conflicts Detected** - Provides step-by-step resolution guidance
2. **Pre-merge Validation** - Suggests checks before merging
3. **Strategy Selection** - Recommends appropriate merge strategy
4. **Complex Scenarios** - Handles renamed files, binary conflicts, refactorings
5. **Recovery Operations** - Guides through undo and recovery processes
6. **Best Practices** - Enforces professional merge workflows

## Getting Started

1. **Start with SKILL.md** (this file) for a complete overview
2. **Read [docs/merge-strategies.md](docs/merge-strategies.md)** to understand different approaches
3. **Review [docs/conflict-resolution.md](docs/conflict-resolution.md)** for resolution techniques
4. **Explore [examples/](examples/)** for practical, working scenarios
5. **Reference [docs/best-practices.md](docs/best-practices.md)** for team workflows

## Next Steps

After mastering merge skills:
1. Practice on test repositories before production
2. Set up merge automation with CI/CD
3. Configure git rerere for recurring conflicts
4. Establish team merge conventions
5. Document complex conflict resolutions
6. Train team on conflict prevention
7. Regular branch cleanup to avoid merge debt

---

**Ready to handle any merge scenario?** Start with simple conflicts, progress to complex scenarios, and always remember: when in doubt, `git merge --abort` and seek help!
