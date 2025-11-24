# Local Worktree Merge Guide

This guide explains how to merge task changes from git worktrees to your main branch when working without a remote GitHub repository.

## When to Use This Guide

Use this workflow when:
- Your project has no remote GitHub repository configured
- Task is in "Pull Request" status and ready to merge
- You need to merge worktree changes to main branch locally
- User requests task completion with `/merge` or `/done` command

## Prerequisites Check

Before starting, verify you're working without a remote:

```bash
# Check for remote repository
git remote -v

# Expected output: empty (no remotes)
# If you see 'origin' URLs, use the standard GitHub PR workflow instead
```

## Pre-Merge Checklist

### 1. Verify Task Status

Task must be in one of these statuses:
- "Pull Request" (preferred)
- "Code Review" (acceptable)

Never merge from:
- "In Progress"
- "Testing"
- "Analysis"

### 2. Check Worktree State

```bash
# Navigate to worktree
cd worktrees/task-{id}

# Check for uncommitted changes
git status

# View recent commits
git log --oneline -5

# Ensure branch is up to date
git fetch --all 2>/dev/null || echo "No remote to fetch"
```

### 3. Commit All Changes

```bash
# In worktree directory
git add .
git commit -m "Final changes before merge [skip-hook]"

# Verify clean state
git status
```

## Merge Process

### Step 1: Prepare Environment

```bash
# Set variables
TASK_ID=42
WORKTREE_DIR="worktrees/task-${TASK_ID}"
BRANCH_NAME="feature/task-${TASK_ID}"
PROJECT_ROOT="/path/to/your/project"

# Return to project root
cd ${PROJECT_ROOT}
```

### Step 2: Switch to Main Branch

```bash
# Checkout main
git checkout main

# Verify main is clean
git status

# If there are uncommitted changes, stash them
git stash push -m "Stashing before merge of task-${TASK_ID}"
```

### Step 3: Perform Merge

```bash
# Merge with no-fast-forward (creates merge commit)
git merge ${BRANCH_NAME} --no-ff -m "Merge task #${TASK_ID}: [Task Title]

Implementation details:
- Feature completed in isolated worktree
- Code review passed
- Tests verified
- Ready for production

Task ID: ${TASK_ID}
Branch: ${BRANCH_NAME}
Worktree: ${WORKTREE_DIR}

[skip-hook]"

# Check merge status
if [ $? -eq 0 ]; then
    echo "✅ Merge successful"
else
    echo "❌ Merge conflict detected"
fi
```

### Step 4: Verify Merge

```bash
# View merge commit
git log --oneline -5

# Check changes included
git diff HEAD~1 HEAD --stat

# Ensure no uncommitted changes
git status
```

## Post-Merge Cleanup

### Step 1: Remove Worktree

```bash
# Safe removal (fails if uncommitted changes)
git worktree remove ${WORKTREE_DIR}

# Force removal if needed (CAUTION: loses uncommitted changes)
git worktree remove ${WORKTREE_DIR} --force

# Verify removal
git worktree list
```

### Step 2: Delete Feature Branch

```bash
# Delete merged branch
git branch -d ${BRANCH_NAME}

# Force delete if not fully merged (use with caution)
# git branch -D ${BRANCH_NAME}

# Verify deletion
git branch -a | grep ${BRANCH_NAME}
```

### Step 3: Update Task Status

```bash
# Mark task as Done
mcp__claudetask__update_status \
  --task_id=${TASK_ID} \
  --status="Done" \
  --comment="Merged locally to main branch"

# Save stage result
mcp__claudetask__append_stage_result \
  --task_id=${TASK_ID} \
  --status="Done" \
  --summary="Task completed and merged" \
  --details="Branch ${BRANCH_NAME} merged to main
Worktree removed from ${WORKTREE_DIR}
Local merge only (no remote repository)"
```

### Step 4: Clean Git References

```bash
# Prune worktree references
git worktree prune

# Garbage collection
git gc --auto

# Final verification
git status
git worktree list
git branch
```

## Handling Merge Conflicts

### Option 1: Resolve Manually

```bash
# View conflicted files
git status

# Edit files with conflicts
# Look for <<<<<<< HEAD markers and resolve

# After resolving
git add .
git commit -m "Resolved merge conflicts for task #${TASK_ID} [skip-hook]"
```

### Option 2: Use Merge Strategy

```bash
# Abort current merge
git merge --abort

# Try with strategy
git merge ${BRANCH_NAME} --strategy=ours   # Keep main version
# OR
git merge ${BRANCH_NAME} --strategy=theirs # Keep worktree version
```

### Option 3: Cherry-Pick Commits

```bash
# Abort merge
git merge --abort

# View commits to pick
git log ${BRANCH_NAME} --oneline

# Cherry-pick specific commits
git cherry-pick COMMIT_HASH
```

## Alternative: Rebase Workflow

For cleaner history without merge commits:

```bash
# Step 1: Rebase worktree onto main
cd ${WORKTREE_DIR}
git rebase main

# Step 2: Resolve conflicts if any
# Edit conflicted files
git add .
git rebase --continue

# Step 3: Fast-forward merge in main
cd ${PROJECT_ROOT}
git checkout main
git merge ${BRANCH_NAME} --ff-only
```

## Complete Example Script

```bash
#!/bin/bash
# Local merge workflow for task completion

# Configuration
TASK_ID=42
PROJECT_ROOT="/path/to/project"
WORKTREE_DIR="${PROJECT_ROOT}/worktrees/task-${TASK_ID}"
BRANCH_NAME="feature/task-${TASK_ID}"

# Navigate to project
cd ${PROJECT_ROOT}

# Verify no remote
if git remote -v | grep -q origin; then
    echo "❌ Remote repository detected. Use GitHub PR workflow instead."
    exit 1
fi

# Switch to main
git checkout main

# Check for uncommitted changes
if ! git diff-index --quiet HEAD --; then
    echo "⚠️  Uncommitted changes on main. Stashing..."
    git stash push -m "Auto-stash before merge task-${TASK_ID}"
fi

# Perform merge
echo "Merging ${BRANCH_NAME} into main..."
git merge ${BRANCH_NAME} --no-ff -m "Merge task #${TASK_ID}

Local worktree merge - no remote repository
Automated merge via ClaudeTask framework

[skip-hook]"

# Check merge result
if [ $? -eq 0 ]; then
    echo "✅ Merge successful"

    # Cleanup
    echo "Cleaning up worktree..."
    git worktree remove ${WORKTREE_DIR} 2>/dev/null || \
        git worktree remove ${WORKTREE_DIR} --force

    echo "Deleting branch..."
    git branch -d ${BRANCH_NAME}

    echo "Pruning references..."
    git worktree prune

    # Verify
    echo ""
    echo "Verification:"
    echo "Worktrees: $(git worktree list | wc -l) active"
    echo "Status: $(git status --short | wc -l) changes"

    echo ""
    echo "✅ Task #${TASK_ID} merged successfully"
    echo "Next: Update task status to 'Done' in ClaudeTask UI"
else
    echo "❌ Merge failed - manual intervention required"
    echo "Run 'git status' to see conflicts"
    exit 1
fi
```

## Common Issues and Solutions

### Issue: Worktree Has Uncommitted Changes

**Problem**: Can't remove worktree due to uncommitted changes

**Solution 1 - Commit changes**:
```bash
cd ${WORKTREE_DIR}
git add .
git commit -m "Final changes [skip-hook]"
```

**Solution 2 - Force remove** (CAUTION: loses changes):
```bash
git worktree remove ${WORKTREE_DIR} --force
```

### Issue: Branch Won't Delete

**Problem**: `git branch -d` fails with "not fully merged" error

**Diagnosis**:
```bash
# Check if branch is merged
git branch --merged | grep ${BRANCH_NAME}

# View unmerged commits
git log main..${BRANCH_NAME} --oneline
```

**Solution**:
```bash
# Force delete (CAUTION: only if you're sure)
git branch -D ${BRANCH_NAME}
```

### Issue: Worktree Directory Still Exists

**Problem**: Directory exists after `git worktree remove`

**Solution**:
```bash
# Manual cleanup
rm -rf ${WORKTREE_DIR}

# Prune git references
git worktree prune

# Verify
git worktree list
```

### Issue: Merge Commits Not Showing in Log

**Problem**: Merge commit doesn't appear in `git log`

**Diagnosis**:
```bash
# View all merge commits
git log --merges --oneline

# View specific merge
git log --graph --oneline --all
```

**Solution**: This is normal if using fast-forward merge. Use `--no-ff` flag to always create merge commit.

## Success Criteria

Merge is complete when all of these are true:

1. Changes from worktree are in main branch
   ```bash
   git log --oneline -5
   ```

2. Worktree is removed
   ```bash
   git worktree list  # Should not show task worktree
   ```

3. Feature branch is deleted
   ```bash
   git branch  # Should not show feature branch
   ```

4. Task status is "Done" in ClaudeTask UI

5. No uncommitted changes remain
   ```bash
   git status  # Should show "working tree clean"
   ```

6. Main branch has all expected changes
   ```bash
   git diff HEAD~1 HEAD --stat
   ```

## Best Practices

### DO:
- ✅ Always use `--no-ff` flag for merge commits
- ✅ Include `[skip-hook]` in commit messages to prevent hook recursion
- ✅ Verify worktree state before merging
- ✅ Test merged changes on main branch
- ✅ Update task status immediately after merge

### DON'T:
- ❌ Merge from "In Progress" or "Testing" status
- ❌ Force delete branches without verification
- ❌ Skip verification steps
- ❌ Leave worktrees hanging around
- ❌ Forget to update task status

## Quick Reference Commands

```bash
# Verify no remote
git remote -v

# Merge workflow
git checkout main
git merge feature/task-{id} --no-ff -m "Merge task #{id} [skip-hook]"

# Cleanup
git worktree remove worktrees/task-{id}
git branch -d feature/task-{id}
git worktree prune

# Verification
git worktree list
git branch
git status
git log --oneline -5
```

## Related Documentation

- [Status Transitions](../architecture/status-transitions.md) - Task workflow
- [Resource Cleanup](../architecture/resource-cleanup.md) - Complete cleanup process
- [Git Worktree Guide](git-worktree-guide.md) - Worktree basics
- [Testing Workflow](../architecture/testing-workflow.md) - Testing before merge

## Comparison: Local vs Remote Merge

### Local Merge (This Guide)
- No pull request creation
- Direct merge to main
- No GitHub/GitLab integration
- Immediate merge after verification
- Cleanup happens locally

### Remote Merge (GitHub PR)
- Pull request created
- Code review via GitHub
- CI/CD pipeline integration
- Merge via web interface
- Remote tracks changes

Choose local merge for:
- Personal projects without hosting
- Quick iterations
- Offline development
- Private projects

Choose remote merge for:
- Team collaboration
- Code review requirements
- CI/CD automation
- Public open-source projects

## Summary

Local worktree merging provides a clean workflow for projects without remote repositories:
- Isolated development in worktrees
- Safe merge process with verification
- Automatic cleanup of temporary branches
- Full git history preservation

The key is to verify task readiness, perform clean merge, and thoroughly clean up afterwards. Always use `[skip-hook]` tag in commit messages to prevent infinite hook recursion.
