# ClaudeTask Framework - Task Development Guide

## Overview
You are working with ClaudeTask, an automated task management system. Tasks are managed through a Kanban board and you develop them using git worktrees. Your role is to analyze, implement, test, and review tasks automatically.

## MCP Integration
Access task management through MCP commands:
- `mcp_get_next_task` - Get highest priority task
- `mcp_analyze_task <id>` - Analyze implementation requirements
- `mcp_update_status <id> <status>` - Update task status
- `mcp_create_worktree <id>` - Create isolated workspace
- `mcp_create_pr <id>` - Create pull request

## Task Workflow

### 1. Analysis Phase (Backlog → Analysis → Ready)
When analyzing a task:
1. Get task details via MCP
2. Scan the codebase for relevant files
3. Identify:
   - Files to modify
   - Entry points
   - Dependencies
   - Potential risks
   - Edge cases
4. Create implementation plan
5. Save analysis and move to Ready

### 2. Development Phase (Ready → In Progress)
When implementing:
1. Create git worktree for isolation
2. Create feature/bug branch
3. Implement changes following the plan
4. Write/update tests
5. Commit with descriptive messages
6. Update status to Testing

### 3. Testing Phase (In Progress → Testing)
Verify implementation:
1. Run unit tests
2. Run integration tests
3. Test edge cases
4. Verify no regressions
5. If all pass, move to Code Review

### 4. Review Phase (Testing → Code Review → Done)
Complete the task:
1. Self-review the code
2. Check code quality
3. Create GitHub PR
4. If approved, merge to main
5. Clean up worktree
6. Mark as Done

## Best Practices

### Code Quality
- Follow project conventions
- Write clean, maintainable code
- Add appropriate tests
- Update documentation
- Use meaningful commit messages

### Git Workflow
- One task = one branch
- Branch naming: `feature/task-{id}-{short-name}` or `bugfix/task-{id}-{short-name}`
- Small, atomic commits
- Squash commits before merge if needed

### Task Scope
- Stay within task boundaries
- Don't fix unrelated issues
- Document any discovered problems as new tasks
- Complete one task before starting another

### Communication
- Update task analysis with findings
- Log important decisions
- Document workarounds
- Note any blockers

## Error Handling
- If blocked, update task with blocker details
- Create new tasks for discovered issues
- Don't leave tasks in limbo
- Always clean up worktrees

## Priority Guidelines
1. High priority bugs first
2. Then high priority features
3. Medium priority tasks
4. Low priority when idle

## Commands Reference

### Task Management
```bash
# Get next task
mcp run get_next_task

# Analyze task
mcp run analyze_task --task-id=123

# Update status
mcp run update_status --task-id=123 --status="In Progress"
```

### Git Operations
```bash
# Create worktree
git worktree add -b feature/task-123 ../worktrees/task-123

# Clean up worktree
git worktree remove ../worktrees/task-123
```

### Testing
```bash
# Run tests
npm test           # Frontend
pytest            # Backend
```

## Task Types

### Feature Tasks
- New functionality
- Follow TDD when possible
- Include tests
- Update documentation

### Bug Tasks
- Fix first, then refactor
- Add regression tests
- Document root cause
- Verify fix doesn't break other features

## Status Definitions
- **Backlog**: New, unanalyzed task
- **Analysis**: Being analyzed by Claude
- **Ready**: Analyzed, ready for development
- **In Progress**: Active development
- **Testing**: Running tests
- **Code Review**: Reviewing code
- **Done**: Merged to main

## Important Notes
- Always work in worktrees, never in main workspace
- One task at a time
- Complete full workflow for each task
- Clean up resources after completion
- Update task status in real-time