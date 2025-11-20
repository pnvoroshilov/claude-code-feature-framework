# Project Modes Documentation

This document describes the two operational modes available in the ClaudeTask Framework and their implications for development workflow.

## Overview

The framework supports two distinct operational modes:
1. **SIMPLE Mode** - Streamlined workflow for rapid development
2. **DEVELOPMENT Mode** - Full development lifecycle with quality gates

The mode is configured in `CLAUDE.md` at the project root and determines:
- Task workflow statuses
- Git branching strategy
- Testing requirements
- Code review processes
- Pull request workflows

## SIMPLE Mode

**Use Case**: Rapid prototyping, solo development, quick iterations

### Task Workflow (3 Columns)
```
Backlog → In Progress → Done
```

### Characteristics
- **No Git Workflow**: Direct work on main branch, no feature branches, no PRs
- **No Complex Statuses**: Just three states - simple and clear
- **Simplified Task Management**: Focus on getting work done quickly
- **No Worktrees**: Work directly in main repository
- **No Version Control Complexity**: Commit and push directly to main

### When to Use SIMPLE Mode
- ✅ Solo developer projects
- ✅ Rapid prototyping phase
- ✅ Internal tools with low risk
- ✅ Learning and experimentation
- ✅ Small projects (< 5 tasks simultaneously)

### Configuration
```markdown
# CLAUDE.md

# 🎯 PROJECT MODE: SIMPLE

**This project is configured in SIMPLE mode.**

## Task Workflow (3 Columns)
- **Backlog**: Tasks waiting to be started
- **In Progress**: Tasks currently being worked on
- **Done**: Completed tasks
```

### Workflow Example
```
1. User creates task → Backlog
2. User starts working → In Progress
3. User completes work → commits to main
4. User manually marks task → Done
```

## DEVELOPMENT Mode

**Use Case**: Production applications, team development, quality-critical projects

**Current Status**: This project is configured in DEVELOPMENT mode as of 2025-11-20.

### Task Workflow (7 Columns)
```
Backlog → Analysis → In Progress → Testing → Code Review → PR → Done
```

### Characteristics
- **Full Git Workflow**: Feature branches, worktrees, pull requests
- **Complete Development Lifecycle**: From analysis to deployment
- **Version Control**: Proper branching and merge strategy
- **Quality Gates**: Testing and code review required before merge
- **Worktree Management**: Isolated development environments per task

### Workflow Stages

#### 1. Backlog
- Tasks waiting to be analyzed
- Priority and categorization
- Initial requirements gathering

#### 2. Analysis
- Business requirements analysis
- Technical specification creation
- Implementation planning
- Risk assessment
- **Automatic transition** to In Progress after analysis complete

#### 3. In Progress
- Active development in task worktree
- Feature branch created
- Code implementation
- Unit tests written
- **Automatic transition** to Testing when implementation detected

#### 4. Testing
- Test environment prepared automatically
- Manual testing by user
- Integration testing
- Bug fixes if needed
- **Manual transition** to Code Review after testing complete

#### 5. Code Review
- Peer review of changes
- Code quality assessment
- Security review
- Documentation review
- **Manual transition** to PR after review approved

#### 6. Pull Request (PR)
- PR created with proper description
- Awaiting merge approval
- CI/CD checks (if configured)
- **Manual merge** by user or team lead

#### 7. Done
- Merged to main branch
- Worktree cleaned up
- Resources released
- Task archived

### When to Use DEVELOPMENT Mode
- ✅ Production applications
- ✅ Team development (2+ developers)
- ✅ Quality-critical projects
- ✅ Customer-facing applications
- ✅ Projects requiring code review
- ✅ Regulatory compliance requirements
- ✅ Long-term maintenance projects

### Configuration
```markdown
# CLAUDE.md

# 🎯 PROJECT MODE: DEVELOPMENT

**This project is configured in DEVELOPMENT mode with full workflow.**

## Task Workflow (7 Columns)
- **Backlog**: New tasks waiting to be analyzed
- **Analysis**: Understanding requirements and planning
- **In Progress**: Active development with Git worktrees
- **Testing**: Running tests and validation
- **Code Review**: Peer review of changes
- **PR**: Pull Request created and awaiting merge
- **Done**: Completed and merged
```

### Workflow Example
```
1. User creates task → Backlog
2. Coordinator delegates to analysts → Analysis
   - Business analyst creates requirements
   - Systems analyst creates technical spec
   - Auto-transition to In Progress
3. Coordinator sets up worktree → In Progress
   - Creates feature branch
   - User develops in isolated environment
   - Auto-transition to Testing when complete
4. Coordinator prepares test environment → Testing
   - Starts backend and frontend servers
   - Saves testing URLs to task
   - User performs manual testing
   - User manually transitions to Code Review
5. Coordinator delegates to reviewer → Code Review
   - Code quality assessment
   - Security review
   - User manually transitions to PR
6. Coordinator creates PR → PR
   - PR description with changes summary
   - Awaits user merge approval
7. User merges PR → Done
   - Coordinator cleans up worktree
   - Releases resources
   - Task archived
```

## Mode Comparison

| Feature | SIMPLE Mode | DEVELOPMENT Mode |
|---------|-------------|------------------|
| **Statuses** | 3 (Backlog, In Progress, Done) | 7 (Full lifecycle) |
| **Git Workflow** | None (direct to main) | Feature branches + PRs |
| **Worktrees** | No | Yes (one per task) |
| **Analysis Phase** | No | Yes (automatic delegation) |
| **Testing Phase** | No | Yes (manual testing) |
| **Code Review** | No | Yes (before merge) |
| **Pull Requests** | No | Yes (required) |
| **Quality Gates** | None | Testing + Review |
| **Team Size** | 1 developer | 2+ developers |
| **Best For** | Prototypes, internal tools | Production, team projects |

## Switching Between Modes

### SIMPLE → DEVELOPMENT

**When to Switch**:
- Project grows beyond solo development
- Need code review and quality gates
- Preparing for production deployment
- Adding team members

**How to Switch**:
1. Edit `CLAUDE.md` at project root
2. Change mode header from SIMPLE to DEVELOPMENT
3. Update task workflow section
4. Commit changes
5. Existing tasks can continue in current status
6. New tasks will follow DEVELOPMENT workflow

**Migration Considerations**:
- Existing In Progress tasks: Move to Analysis or Testing as appropriate
- No worktrees exist: Create worktrees for active tasks
- Update team on new workflow

### DEVELOPMENT → SIMPLE

**When to Switch**:
- Moving to solo development
- Internal prototype or POC
- Need faster iteration
- Reducing process overhead

**How to Switch**:
1. Complete or merge all PRs
2. Clean up all worktrees
3. Edit `CLAUDE.md` at project root
4. Change mode header from DEVELOPMENT to SIMPLE
5. Update task workflow section
6. Commit changes
7. Simplify existing task statuses to Backlog/In Progress/Done

**Migration Considerations**:
- Complete in-flight PRs first
- Merge feature branches
- Clean up all worktrees
- Update team on simplified workflow

## Mode Configuration File

The project mode is defined in `CLAUDE.md` at the project root. This file is read by:
- Claude Code sessions
- Autonomous coordinator agent
- Task management system

### Key Configuration Sections

#### Mode Declaration
```markdown
# 🎯 PROJECT MODE: [SIMPLE|DEVELOPMENT]
```

#### Task Workflow
```markdown
## Task Workflow (N Columns)
- List of statuses in order
```

#### Mode Description
```markdown
## What this means:
- Key characteristics of the mode
- Workflow implications
```

#### Approach Guidelines
```markdown
## Your approach:
- How to work in this mode
- Key workflow steps
```

## Best Practices

### SIMPLE Mode Best Practices
1. **Keep Tasks Small**: Focus on small, manageable tasks
2. **Commit Frequently**: Regular commits to main branch
3. **Test Locally**: Manual testing before marking done
4. **Document as You Go**: Update docs with code changes
5. **Quick Iterations**: Embrace rapid development cycle

### DEVELOPMENT Mode Best Practices
1. **Complete Analysis**: Don't skip analysis phase
2. **Use Worktrees**: One worktree per task for isolation
3. **Write Tests**: Include tests with implementation
4. **Request Review**: Always get code review before merge
5. **Test Thoroughly**: Manual testing before code review
6. **Clean PRs**: Keep PRs focused and well-documented
7. **Clean Up**: Always clean up worktrees after merge

## Auto-Transitions

### DEVELOPMENT Mode Auto-Transitions
- **Analysis → In Progress**: Automatic after analysis complete
- **In Progress → Testing**: Automatic when implementation detected
- **All Other Transitions**: Manual by user

### SIMPLE Mode Auto-Transitions
- **Backlog → In Progress**: When user starts work (can be manual)
- **In Progress → Done**: ONLY manual by user request

## Status Update Commands

### Manual Status Updates
```bash
# Update task status manually
/update-task-status {task_id} {new_status}

# Mark task as done
"mark task {task_id} as done"
```

### Automatic Status Detection (DEVELOPMENT Mode)
- Coordinator monitors task worktrees for changes
- Detects implementation completion signals
- Auto-transitions In Progress → Testing
- Saves implementation summary
- Prepares test environment

## Related Documentation

- [CLAUDE.md](../../CLAUDE.md) - Main configuration file
- [Task Workflow Documentation](../claudetask/workflow.md) - Detailed workflow guide (to be created)
- [Git Worktree Guide](../claudetask/worktree-guide.md) - Worktree management (to be created)

---

**Current Project Mode**: DEVELOPMENT
**Last Mode Change**: 2025-11-20
**Mode Change History**:
- 2025-11-20: Switched from SIMPLE to DEVELOPMENT mode
- Previous: SIMPLE mode (initial configuration)
