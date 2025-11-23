# 🔀 Local Worktree Merge Workflow (No Remote Repository)

**This file describes how to merge worktree changes when there is NO remote GitHub repository.**

## 📋 When This Applies

Use this workflow when:
- Project has no GitHub repository configured
- Task is in "Pull Request" status
- Need to merge worktree changes to main branch locally
- User requests task completion with `/merge` command

## 🚨 CRITICAL: Check for Remote Repository First

```bash
# Check if remote repository exists
git remote -v

# If empty output → NO REMOTE (use this guide)
# If shows origin → HAS REMOTE (use standard PR workflow)
```

## 📝 Pre-Merge Checklist

Before merging worktree changes:

1. **Verify Task Status**
   - Task MUST be in "Pull Request" or "Code Review" status
   - Never merge from "In Progress" or "Testing" status

2. **Check Worktree State**
   ```bash
   cd worktrees/task-{id}
   git status
   git log --oneline -5
   ```

3. **Ensure All Changes Committed**
   ```bash
   # In worktree directory
   git add .
   git commit -m "Final changes before merge"
   ```

## 🔀 Local Merge Process

### Step 1: Prepare for Merge

```bash
# Save current directory
TASK_ID={id}
WORKTREE_DIR="worktrees/task-${TASK_ID}"
BRANCH_NAME="feature/task-${TASK_ID}"

# Ensure we're in project root
cd /path/to/project

# Fetch latest changes (even without remote, good practice)
git fetch --all 2>/dev/null || echo "No remote to fetch from"
```

### Step 2: Switch to Main Branch

```bash
# Switch to main branch
git checkout main

# Ensure main is clean
git status

# If there are uncommitted changes on main, stash them
git stash push -m "Stashing before merge of task-${TASK_ID}"
```

### Step 3: Merge Worktree Branch

```bash
# Merge the feature branch
git merge ${BRANCH_NAME} --no-ff -m "Merge task #${TASK_ID}: [Task Title]

- Implementation completed in worktree
- Code review passed
- Tests passed
- Ready for production

Task ID: ${TASK_ID}
Branch: ${BRANCH_NAME}"

# Check merge status
if [ $? -eq 0 ]; then
    echo "✅ Merge successful"
else
    echo "❌ Merge conflict detected - manual resolution required"
    # Handle conflicts if any
fi
```

### Step 4: Verify Merge

```bash
# Verify merge completed
git log --oneline -5

# Check that changes are included
git diff HEAD~1 HEAD --stat

# Ensure no uncommitted changes
git status
```

## 🧹 Post-Merge Cleanup

### Step 1: Remove Worktree

```bash
# Remove worktree (safe method)
git worktree remove ${WORKTREE_DIR}

# If above fails due to uncommitted changes
git worktree remove ${WORKTREE_DIR} --force

# Verify removal
git worktree list
```

### Step 2: Delete Feature Branch

```bash
# Delete the merged branch
git branch -d ${BRANCH_NAME}

# If branch wasn't fully merged (use with caution)
# git branch -D ${BRANCH_NAME}

# Verify branch deleted
git branch -a | grep ${BRANCH_NAME}
```

### Step 3: Update Task Status

```bash
# Mark task as Done
mcp__claudetask__update_status --task_id=${TASK_ID} --status="Done" \
  --comment="Merged locally to main branch"

# Save final stage result
mcp__claudetask__append_stage_result \
  --task_id=${TASK_ID} \
  --status="Done" \
  --summary="Task completed and merged locally" \
  --details="Branch ${BRANCH_NAME} merged to main
Worktree removed
No remote repository - local merge only"
```

### Step 4: Clean Git References

```bash
# Prune worktree references
git worktree prune

# Clean up any stale references
git gc --auto

# Verify clean state
git status
git worktree list
```

## ⚠️ Handling Merge Conflicts

If merge conflicts occur:

### Option 1: Resolve in Main Branch

```bash
# If conflicts during merge
git status

# Edit conflicted files
# Look for <<<<<<< HEAD markers

# After resolving
git add .
git commit -m "Resolved merge conflicts for task #${TASK_ID}"
```

### Option 2: Abort and Try Different Strategy

```bash
# Abort the merge
git merge --abort

# Try different merge strategy
git merge ${BRANCH_NAME} --strategy=ours  # Keep main version
# OR
git merge ${BRANCH_NAME} --strategy=theirs  # Keep worktree version
```

### Option 3: Manual Cherry-Pick

```bash
# Abort merge
git merge --abort

# Cherry-pick specific commits
git log ${BRANCH_NAME} --oneline
git cherry-pick COMMIT_HASH
```

## 🔄 Alternative: Rebase Workflow

For cleaner history without merge commits:

```bash
# In worktree
cd ${WORKTREE_DIR}
git rebase main

# If conflicts, resolve them then:
git rebase --continue

# Switch to main and fast-forward
cd /path/to/project
git checkout main
git merge ${BRANCH_NAME} --ff-only
```

## 📊 Complete Example

```bash
#!/bin/bash
# Complete local merge workflow for task #42

TASK_ID=42
WORKTREE_DIR="worktrees/task-${TASK_ID}"
BRANCH_NAME="feature/task-${TASK_ID}"

# 1. Prepare
cd /path/to/project
git checkout main
git status

# 2. Merge
git merge ${BRANCH_NAME} --no-ff -m "Merge task #${TASK_ID}: Implement new feature"

# 3. Verify
if [ $? -eq 0 ]; then
    echo "✅ Merge successful"

    # 4. Cleanup
    git worktree remove ${WORKTREE_DIR}
    git branch -d ${BRANCH_NAME}
    git worktree prune

    # 5. Update task
    echo "Task #${TASK_ID} merged and cleaned up"
else
    echo "❌ Merge failed - manual intervention required"
fi
```

## 🚨 Common Issues and Solutions

### Issue: Worktree has uncommitted changes

```bash
# Option 1: Commit changes first
cd ${WORKTREE_DIR}
git add .
git commit -m "Final changes"

# Option 2: Force remove (loses changes!)
git worktree remove ${WORKTREE_DIR} --force
```

### Issue: Branch won't delete

```bash
# Check if branch is fully merged
git branch --merged | grep ${BRANCH_NAME}

# If not shown, force delete
git branch -D ${BRANCH_NAME}
```

### Issue: Worktree directory still exists

```bash
# Manual cleanup
rm -rf ${WORKTREE_DIR}
git worktree prune
```

## ✅ Success Criteria

Merge is successful when:
1. Changes from worktree are in main branch
2. Worktree is removed
3. Feature branch is deleted
4. Task status is "Done"
5. No uncommitted changes remain
6. `git worktree list` shows worktree removed
7. `git branch` doesn't show feature branch

## 📚 Related Documentation

- [Status Transitions](status-transitions.md) - Task status workflow
- [Resource Cleanup](resource-cleanup.md) - Complete cleanup process
- [Git Workflow](git-workflow.md) - Git best practices

## 🎯 Quick Reference Commands

```bash
# Check remote status
git remote -v

# Merge locally
git checkout main
git merge feature/task-{id} --no-ff

# Cleanup
git worktree remove worktrees/task-{id}
git branch -d feature/task-{id}
git worktree prune

# Verify
git worktree list
git branch
git status
```

**Remember**: Local merges are permanent. Always verify changes before merging!