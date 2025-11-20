---
allowed-tools: [Bash, Read, Write, Edit, MultiEdit, Glob, Grep]
argument-hint: [task-id]
description: Start development phase for a task after analysis is complete. Begin implementation in task worktree.
---

# Start Development Phase

I'll start the development phase for this task, transitioning from analysis to implementation.

## Prerequisites

Before starting development:
- ✅ Task must be in "Analyse" status or have completed analysis
- ✅ requirements.md must exist in Analyse/ folder
- ✅ architecture.md must exist in Analyse/ folder
- ✅ Task worktree must be created

## Getting Task Information

First, let me get the task details:

```bash
# Get task information
mcp:get_task <task_id>
```

## Verification Steps

### Step 1: Check Analysis Documents

I'll verify that both analysis documents exist:

```bash
# Check for requirements.md
ls worktrees/task-<id>/Analyse/requirements.md

# Check for architecture.md
ls worktrees/task-<id>/Analyse/architecture.md
```

### Step 2: Read Analysis Documents

I'll read both documents to understand the requirements and architecture:

```bash
# Read requirements
cat worktrees/task-<id>/Analyse/requirements.md

# Read architecture
cat worktrees/task-<id>/Analyse/architecture.md
```

### Step 3: Update Task Status to "In Progress"

Move the task from "Analyse" to "In Progress":

```bash
mcp:update_status <task_id> "In Progress"
```

## Development Workflow

### Working in Task Worktree

All development work should be done in the task's isolated worktree:

```bash
# Navigate to task worktree
cd worktrees/task-<id>

# Verify you're on the correct branch
git branch --show-current
# Should show: feature/task-<id>
```

### Implementation Guidelines

1. **Follow Architecture**:
   - Implement according to architecture.md specifications
   - Use the technology stack and patterns defined
   - Follow the implementation steps outlined

2. **Meet Requirements**:
   - Satisfy all acceptance criteria from requirements.md
   - Implement all functional requirements
   - Consider edge cases and constraints

3. **Code Quality**:
   - Follow project coding conventions
   - Write clean, maintainable code
   - Add appropriate error handling
   - Include code comments where needed

4. **Testing as You Go**:
   - Write unit tests for new code
   - Test edge cases
   - Verify functionality works as expected

### Making Commits

Make regular, descriptive commits:

```bash
# Stage your changes
git add <files>

# Commit with descriptive message
git commit -m "feat(task-<id>): <description>

- Detail about change 1
- Detail about change 2

Refs: #<task_id>"

# Push to remote (if needed)
git push origin feature/task-<id>
```

## Implementation Checklist

As you develop, track progress against these items:

- [ ] Read and understand requirements.md
- [ ] Read and understand architecture.md
- [ ] Set up any required dependencies
- [ ] Implement core functionality
- [ ] Handle edge cases from requirements
- [ ] Add error handling
- [ ] Write unit tests
- [ ] Test locally
- [ ] Update documentation (if needed)
- [ ] Make clean, descriptive commits

## Completion

When implementation is complete:

1. **Verify all requirements met**:
   - Review acceptance criteria in requirements.md
   - Check that all functional requirements implemented
   - Test edge cases

2. **Prepare for testing**:
   - Ensure code is committed
   - Push changes to remote branch
   - Ready for transition to "Tests" status

3. **Move to Tests status**:
   ```bash
   # When ready for testing phase
   mcp:update_status <task_id> "Tests"
   ```

## Tips

- **Stay focused**: Work only on this task in the worktree
- **Refer to docs**: Keep requirements.md and architecture.md open
- **Test frequently**: Don't wait until the end to test
- **Ask for help**: If blocked, update task status to "Blocked" with details
- **Document changes**: Update architecture.md if implementation differs from plan

## Next Steps

After completing development:
1. Use `/test` command to enter testing phase
2. Perform manual testing and document results
3. Move to code review when tests pass
4. Use `/PR` command to create pull request

Let me begin by getting the task information and verifying analysis documents...
