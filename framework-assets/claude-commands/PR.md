---
allowed-tools: [Bash, Read, Write, Edit, Grep, Glob, Task]
argument-hint: [task-id]
description: Create pull request for a completed task, handle code review (if manual_mode), and merge to main.
---

# Create Pull Request and Merge

I'll create a pull request for this task, coordinate code review if needed, and handle the merge to main.

## Prerequisites

Before creating PR:
- ✅ Task must be in "Code Review" or "Tests" status
- ✅ All tests passed (test-plan.md shows "Ready for Code Review")
- ✅ requirements.md exists in Analyse/ folder
- ✅ architecture.md exists in Analyse/ folder
- ✅ All code committed and pushed

## Getting Task Information

First, let me get the task details and project settings:

```bash
# Get task information
mcp:get_task <task_id>

# Get project settings to check manual_mode
# This will tell us if code review is required
```

## PR Creation Workflow

### Step 1: Verify Prerequisites

I'll check that all required documents exist:

```bash
# Verify analysis documents
ls worktrees/task-<id>/Analyse/requirements.md
ls worktrees/task-<id>/Analyse/architecture.md

# Verify test plan (if exists)
ls worktrees/task-<id>/Tests/test-plan.md

# Check git status
cd worktrees/task-<id>
git status
```

### Step 2: Gather PR Information

I'll collect information for the PR description:

```bash
# Read requirements
cat worktrees/task-<id>/Analyse/requirements.md

# Read architecture
cat worktrees/task-<id>/Analyse/architecture.md

# Read test plan
cat worktrees/task-<id>/Tests/test-plan.md

# Get list of changed files
git diff --name-only main...HEAD

# Get commit history
git log main..HEAD --oneline
```

### Step 3: Delegate to PR Merge Agent

I'll use the pr-merge-agent to handle the PR creation and merge:

```bash
# Use Task tool to delegate to pr-merge-agent
Task tool with pr-merge-agent:
"Create pull request and handle merge for this task.

Task Details:
- ID: <task_id>
- Title: <task_title>
- Description: <task_description>
- Worktree: worktrees/task-<id>
- Branch: feature/task-<id>

Requirements: [Summary from requirements.md]
Architecture: [Summary from architecture.md]
Test Results: [Summary from test-plan.md]

Project Settings:
- manual_mode: <true/false>

Instructions:
1. Create comprehensive PR description
2. Create PR with gh CLI
3. If manual_mode = true:
   - Wait for code review approval
   - Coordinate review feedback
4. If manual_mode = false:
   - Skip code review
   - Proceed to merge when checks pass
5. Merge PR to main
6. Clean up worktree and branch
7. Update task status to 'Done'
8. Provide merge summary

Worktree path: worktrees/task-<id>
"
```

## What the PR Merge Agent Will Do

### If manual_mode = false (Automated):

1. **Create PR** with comprehensive description
2. **Wait for automated checks** to pass
3. **Merge PR** to main automatically
4. **Clean up resources**:
   - Delete worktree
   - Delete branch
   - Stop test servers
5. **Update task to "Done"**
6. **Provide summary**

### If manual_mode = true (Manual Review):

1. **Create PR** with comprehensive description
2. **Wait for code review**:
   - Notify that manual review is required
   - Provide PR URL for reviewer
   - Wait for approval
3. **After approval received**:
   - Merge PR to main
   - Clean up resources
   - Update task to "Done"
   - Provide summary

## PR Description Template

The PR will include:

```markdown
# [Task Title]

## 📋 Task Overview
[Brief description]

**Task ID:** #<task_id>
**Type:** Feature/Bug Fix
**Priority:** High/Medium/Low

## 🎯 Business Requirements

[From requirements.md - key user stories and acceptance criteria]

## 🏗️ Technical Implementation

[From architecture.md - architecture decisions and approach]

## 📊 Changes Made

### Files Changed
- file1.tsx - [Description]
- file2.py - [Description]

### Components Modified
- Component 1: [Changes]
- Component 2: [Changes]

## ✅ Testing

[From test-plan.md - test results]

- ✅ All acceptance criteria tested and passing
- ✅ Edge cases covered
- ✅ Performance acceptable
- ✅ No regressions found

## 📚 Documentation

- ✅ requirements.md created
- ✅ architecture.md created
- ✅ test-plan.md completed
- ✅ Code comments added

## 🔗 Related Links

- Analysis: Analyse/requirements.md, Analyse/architecture.md
- Tests: Tests/test-plan.md
```

## Code Review Process (Manual Mode Only)

If manual_mode = true:

### Waiting for Review:
```
PR Created: #<pr_number>
URL: https://github.com/user/repo/pull/<pr_number>

Status: Awaiting code review

⏳ Manual review required. Please:
1. Review the PR on GitHub
2. Check the code changes
3. Review requirements and architecture docs
4. Approve or request changes
```

### After Review Approved:
```
Code Review: ✅ Approved

Proceeding with merge...
```

### If Changes Requested:
```
Code Review: ⚠️ Changes requested

Please address the feedback and update the PR.
Task remains in "Code Review" status until approved.
```

## Merge Process

After all requirements met (tests pass, review approved if needed):

```bash
# Merge PR
gh pr merge <pr_number> --merge --delete-branch

# Return to project root
cd <project_path>

# Remove worktree
git worktree remove worktrees/task-<id>

# Update task status
mcp:update_status <task_id> "Done"
```

## Cleanup Checklist

The PR merge agent will ensure:

- [ ] PR created successfully
- [ ] All checks passing
- [ ] Code review approved (if manual_mode)
- [ ] PR merged to main
- [ ] Remote branch deleted
- [ ] Worktree removed
- [ ] Local branch cleaned up
- [ ] Task status updated to "Done"
- [ ] Test servers stopped
- [ ] Resources freed

## Success Output

After successful merge:

```
✅ PR Merged Successfully

PR #<number>: [Task #<id>] <title>
Merge commit: abc123def456
Branch deleted: feature/task-<id>
Worktree removed: worktrees/task-<id>
Task status: Done

📊 Summary:
- Files changed: 3
- Lines added: 150
- Lines removed: 20
- Tests: All passing ✅
- Documentation: Complete ✅
- Review: Approved ✅

Task #<id> completed successfully! 🎉
```

## Handling Issues

### If PR Creation Fails:
- Check that branch is pushed to remote
- Verify gh CLI is authenticated
- Ensure no PR already exists for this branch

### If Merge Fails:
- Check for merge conflicts
- Ensure all checks are passing
- Verify branch is up to date with main

### If Cleanup Fails:
- Manually remove worktree if needed
- Check for running processes in worktree
- Ensure no files are open in worktree

## Manual Intervention

If you need to manually handle the PR:

```bash
# Create PR manually
cd worktrees/task-<id>
gh pr create --title "[Task #<id>] <title>" --body "<description>"

# Merge manually
gh pr merge <pr_number> --merge --delete-branch

# Clean up manually
cd <project_path>
git worktree remove worktrees/task-<id>
mcp:update_status <task_id> "Done"
```

Let me start by getting task information and delegating to the PR merge agent...
