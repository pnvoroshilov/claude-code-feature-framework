# Intelligent Development Workflow

Complete guide to the intelligent development workflow with automated agents and slash commands in the Claude Code Feature Framework.

## Overview

The framework implements an intelligent, agent-driven development workflow that guides tasks from inception through deployment. This workflow combines:

- **Automated Analysis**: Business and systems analysts create requirements and architecture documentation
- **Structured Development**: Clear phases with analysis, implementation, testing, and review
- **Slash Commands**: Quick commands to trigger workflow phases
- **Specialized Agents**: Expert agents for each phase of development
- **Git Worktrees**: Isolated development environments per task

## Workflow Phases

### Phase 1: Task Creation (Backlog)

**Status**: Backlog
**Duration**: Initial task definition
**Owner**: User/Product Owner

**Activities**:
- Create task with title and description
- Set priority (High, Medium, Low)
- Set type (Feature, Bug)
- Task enters Backlog status

**No automated actions** - awaits user to start analysis.

---

### Phase 2: Analysis (Analyse)

**Status**: Analyse
**Trigger**: User initiates with `/start-feature [task-id]`
**Duration**: 5-15 minutes (automated)
**Agents**: requirements-analyst, system-architect

#### 2.1 Requirements Analysis

**Agent**: `requirements-analyst`
**Output**: `worktrees/task-{id}/Analyze/Requirements/`

Creates comprehensive business requirements including:
- **User Stories**: Clear user-focused scenarios
- **Acceptance Criteria**: Testable success conditions
- **Business Requirements**: Core business needs
- **Functional Requirements**: Specific feature behaviors
- **Non-Functional Requirements**: Performance, security, usability
- **Constraints**: Technical and business limitations
- **Success Metrics**: How to measure completion

**Example requirements.md structure**:
```markdown
# Requirements: [Task Title]

## User Stories
As a [user], I want [goal] so that [benefit]

## Acceptance Criteria
- [ ] Criterion 1: Specific, testable condition
- [ ] Criterion 2: Another measurable outcome

## Functional Requirements
- FR1: Detailed functional requirement
- FR2: Another functional requirement

## Non-Functional Requirements
- NFR1: Performance requirements
- NFR2: Security requirements
```

#### 2.2 System Architecture

**Agent**: `system-architect`
**Output**: `worktrees/task-{id}/Analyse/architecture.md`

Creates technical architecture and implementation plan:
- **System Architecture**: High-level component design
- **Technical Approach**: Implementation strategy
- **Integration Points**: APIs, services, databases
- **Data Flow**: How data moves through the system
- **Implementation Steps**: Ordered development tasks
- **Technology Stack**: Frameworks and libraries to use
- **Security Considerations**: Security requirements
- **Performance Considerations**: Optimization needs

**Example architecture.md structure**:
```markdown
# Architecture: [Task Title]

## System Components
### Frontend
- Component 1: Purpose and location
- Component 2: Purpose and location

### Backend
- Endpoint 1: Route and purpose
- Service 1: Business logic

## Implementation Steps
1. Step 1: Create base component
2. Step 2: Add business logic
3. Step 3: Integrate with API

## Technology Stack
- Frontend: React, TypeScript, Material-UI
- Backend: FastAPI, Python, SQLAlchemy
```

#### 2.3 Worktree Setup

After analysis completes, the framework automatically:
1. **Creates git worktree**: `worktrees/task-{id}/`
2. **Creates feature branch**: `feature/task-{id}`
3. **Sets up Analyse folder**: Contains requirements.md and architecture.md
4. **Updates task status**: Automatically transitions to "In Progress"

---

### Phase 3: Development (In Progress)

**Status**: In Progress
**Trigger**: Automatic after analysis complete
**Duration**: Varies by task complexity
**Owner**: User/Developer

#### 3.1 Starting Development

**Command**: `/start-develop [task-id]`

This command:
1. Verifies prerequisites (requirements.md and architecture.md exist)
2. Reads and displays analysis documents
3. Updates task status to "In Progress"
4. Provides implementation guidelines

#### 3.2 Implementation Guidelines

**Working Directory**: `worktrees/task-{id}/`
**Branch**: `feature/task-{id}`

Development workflow:
1. **Navigate to worktree**: `cd worktrees/task-{id}`
2. **Verify branch**: `git branch --show-current` (should show `feature/task-{id}`)
3. **Follow architecture.md**: Implement according to technical plan
4. **Meet requirements.md**: Satisfy all acceptance criteria
5. **Make regular commits**: Use descriptive commit messages
6. **Test as you develop**: Verify functionality works

**Commit Message Format**:
```bash
git commit -m "feat(task-{id}): Brief description

- Detail about change 1
- Detail about change 2

Refs: #{task_id}"
```

#### 3.3 Implementation Checklist

Track progress against:
- [ ] Read and understand requirements.md
- [ ] Read and understand architecture.md
- [ ] Set up required dependencies
- [ ] Implement core functionality
- [ ] Handle edge cases from requirements
- [ ] Add error handling
- [ ] Write unit tests
- [ ] Test locally
- [ ] Update documentation
- [ ] Make clean commits

#### 3.4 Automatic Detection

The coordinator agent monitors worktrees for implementation completion:
- **Detects**: Recent commits with completion keywords
- **Checks**: Implementation agent completion reports
- **Listens**: User signals that development is complete
- **Auto-transitions**: Moves task to "Tests" status when detected

---

### Phase 4: Testing (Tests)

**Status**: Tests
**Trigger**: Automatic when implementation detected OR manual with `/test [task-id]`
**Duration**: Varies by testing complexity
**Owner**: User/QA

#### 4.1 Test Environment Setup

**Command**: `/test [task-id]` (optional - auto-triggered)

Framework automatically:
1. **Finds available ports**: Checks for free backend and frontend ports
2. **Starts backend server**: `python -m uvicorn app.main:app --port [FREE_PORT]`
3. **Starts frontend server**: `PORT=[FREE_PORT] npm start`
4. **Saves testing URLs**: Persists URLs to task database using `mcp:set_testing_urls`
5. **Notifies user**: Provides direct links to test environments

**Critical**: Testing URLs MUST be saved to task database for persistent access.

#### 4.2 Manual Testing

User performs manual testing:
1. **Access test environment**: Use provided URLs
2. **Test all acceptance criteria**: From requirements.md
3. **Document test results**: In `worktrees/task-{id}/Tests/test-plan.md`
4. **Report bugs**: Add to test-plan.md if issues found
5. **Verify edge cases**: Test boundary conditions

**Test Plan Structure** (`Tests/test-plan.md`):
```markdown
# Test Plan: [Task Title]

## Test Environment
- Backend: http://localhost:[PORT]
- Frontend: http://localhost:[PORT]

## Test Cases

### TC1: [Test Case Title]
**Acceptance Criteria**: [From requirements.md]
**Steps**:
1. Step 1
2. Step 2
**Expected**: Expected result
**Actual**: Actual result
**Status**: ✅ Pass / ❌ Fail

## Testing Summary
- Total tests: X
- Passed: Y
- Failed: Z
- Status: Ready for Code Review / Needs Fixes
```

#### 4.3 Transition to Code Review

**Manual**: User updates status when testing complete
```bash
mcp:update_status [task-id] "Code Review"
```

---

### Phase 5: Code Review (Code Review)

**Status**: Code Review
**Trigger**: Manual by user after testing complete
**Duration**: Varies by code complexity
**Reviewer**: Another developer or senior engineer

#### 5.1 Review Scope

**CRITICAL**: Review ONLY task-specific changes

Reviewer should:
- Use `git diff main..HEAD` to see ONLY task changes
- Review modified files in worktree
- Focus on changes introduced by THIS task
- Do NOT review unrelated existing code

#### 5.2 Review Checklist

- [ ] **Code Quality**: Clean, maintainable, follows conventions
- [ ] **Requirements Met**: All acceptance criteria satisfied
- [ ] **Architecture Followed**: Matches architecture.md plan
- [ ] **Tests Included**: Unit tests for new code
- [ ] **Error Handling**: Proper error handling added
- [ ] **Security**: No security vulnerabilities introduced
- [ ] **Performance**: No performance regressions
- [ ] **Documentation**: Code comments and docs updated

#### 5.3 Review Process

1. **Reviewer examines code**: In `worktrees/task-{id}/`
2. **Provides feedback**: Via comments or direct discussion
3. **Developer addresses feedback**: Makes necessary changes
4. **Re-review if needed**: Iterate until approved
5. **Approval**: Reviewer approves changes

#### 5.4 After Review Complete

**Manual**: User updates status when approved
```bash
mcp:update_status [task-id] "PR"
```

---

### Phase 6: Pull Request (PR)

**Status**: PR
**Trigger**: Manual with `/PR [task-id]` command
**Duration**: Time to create PR and get approval
**Owner**: Developer (creates PR) → Team Lead (approves)

#### 6.1 Creating Pull Request

**Command**: `/PR [task-id]`

This command delegates to `pr-merge-agent` which:
1. **Gathers information**: Reads requirements.md, architecture.md, test-plan.md
2. **Creates PR description**: Comprehensive summary of changes
3. **Creates PR with gh CLI**: `gh pr create --title "..." --body "..."`
4. **Links task documentation**: References all analysis documents

#### 6.2 PR Description Template

```markdown
# [Task Title]

## 📋 Task Overview
Brief description of what this PR accomplishes

**Task ID:** #[task_id]
**Type:** Feature/Bug Fix
**Priority:** High/Medium/Low

## 🎯 Business Requirements

Summary from requirements.md:
- User story
- Key acceptance criteria

## 🏗️ Technical Implementation

Summary from architecture.md:
- Architecture approach
- Key technical decisions

## 📊 Changes Made

### Files Changed
- `file1.tsx` - Added component for feature
- `file2.py` - Implemented backend API
- `file3.md` - Updated documentation

### Components Modified
- Component 1: Description of changes
- Component 2: Description of changes

## ✅ Testing

Summary from Tests/test-plan.md:
- Test coverage
- Test results
- Manual testing completed

## 📚 Documentation

- [x] requirements.md created
- [x] architecture.md created
- [x] test-plan.md completed
- [x] Code comments added

## 🔍 Review Checklist
- [ ] Code follows project conventions
- [ ] All tests pass
- [ ] Documentation updated
- [ ] No security issues
- [ ] Performance impact assessed
```

#### 6.3 Manual Mode vs Auto Mode

**Manual Mode** (default, `manual_mode: true`):
- PR created but NOT automatically merged
- Requires human approval and manual merge
- User must merge PR via GitHub UI or `gh pr merge`

**Auto Mode** (`manual_mode: false`):
- PR created AND automatically merged after checks pass
- No human approval required
- Coordinator handles merge automatically

#### 6.4 After PR Creation

**PR Status**: Task remains in "PR" status until merged
- Wait for CI/CD checks to pass (if configured)
- Wait for human review and approval (if manual_mode)
- Do NOT auto-transition to Done

---

### Phase 7: Merge and Completion (Done)

**Status**: Done
**Trigger**: Manual with `/merge [task-id]` command AFTER PR is merged
**Duration**: Cleanup takes ~1 minute
**Owner**: Coordinator agent

#### 7.1 Merge Command

**Command**: `/merge [task-id]`

**Prerequisites**:
- PR must be merged to main branch
- Changes must be in main branch
- User has explicitly requested merge

#### 7.2 Cleanup Process

Coordinator performs complete resource cleanup:

1. **Stop Claude session**: Completes task-specific Claude session
2. **Stop terminal sessions**: Stops any embedded terminal sessions
3. **Kill test servers**: Terminates frontend and backend test processes
4. **Release ports**: Frees up occupied ports
5. **Clear testing URLs**: Removes URLs from task database
6. **Update task status**: Sets status to "Done"
7. **Optional worktree cleanup**: Removes worktree if requested

**Automated Cleanup Command**:
```bash
mcp:stop_session [task-id]
```

This single command handles all cleanup automatically.

#### 7.3 Manual Cleanup (Alternative)

If automated cleanup fails, manual steps:
```bash
# Find test processes
lsof -i :[BACKEND_PORT]
lsof -i :[FRONTEND_PORT]

# Kill processes
kill [BACKEND_PID]
kill [FRONTEND_PID]

# Remove worktree (optional)
git worktree remove --force worktrees/task-[id]
```

#### 7.4 Completion Report

Coordinator provides structured report:
```
✅ Task #[id] Completed

Cleanup Actions:
- Claude session: Completed ✓
- Terminal sessions: Stopped ✓
- Test servers: Terminated ✓
- Ports released: [BACKEND_PORT], [FRONTEND_PORT] ✓
- Testing URLs: Cleared ✓
- Worktree: [Kept/Removed] ✓

All resources cleaned up successfully.
```

---

## Slash Commands Reference

### `/start-feature [task-id]`
**Phase**: Backlog → Analysis
**Purpose**: Start task analysis with automated agents
**Actions**:
- Delegates to requirements-analyst agent
- Delegates to system-architect agent
- Creates worktree and feature branch
- Sets up Analyze/ folder with documentation
- Auto-transitions to "In Progress"

### `/start-develop [task-id]`
**Phase**: Analysis → Development
**Purpose**: Begin implementation after analysis
**Actions**:
- Verifies analysis documents exist
- Displays requirements and architecture
- Updates task status to "In Progress"
- Provides implementation guidelines

### `/test [task-id]`
**Phase**: Development → Testing
**Purpose**: Setup test environment for manual testing
**Actions**:
- Finds available ports
- Starts backend and frontend servers
- Saves testing URLs to task database
- Creates Tests/ folder with test-plan.md template
- Notifies user with test environment URLs

### `/PR [task-id]`
**Phase**: Code Review → Pull Request
**Purpose**: Create pull request for reviewed code
**Actions**:
- Gathers requirements, architecture, test plan
- Creates comprehensive PR description
- Executes `gh pr create` with proper formatting
- Links all task documentation
- Updates task status to "PR"

### `/merge [task-id]`
**Phase**: PR → Done
**Purpose**: Complete task and cleanup all resources
**Prerequisites**: PR must be merged to main
**Actions**:
- Stops Claude session
- Kills test server processes
- Releases occupied ports
- Clears testing URLs
- Updates status to "Done"
- Optional: Removes worktree

---

## Specialized Agents

### Analysis Agents

#### `requirements-analyst`
**Purpose**: Create comprehensive business requirements documentation
**Output**: `Analyze/Requirements/` (requirements.md, acceptance-criteria.md, constraints.md)
**Skills**:
- RAG-enhanced requirements analysis
- User story creation
- Acceptance criteria definition
- Business requirement analysis
- Task queue conflict checking
- Project documentation analysis

#### `system-architect`
**Purpose**: Create technical architecture documentation
**Output**: `architecture.md`
**Skills**:
- System design
- Technical specification
- Integration planning
- Implementation strategy

### Implementation Agents

Agents in framework (used by Task tool):
- `frontend-developer`: React/TypeScript UI components
- `backend-architect`: FastAPI/Python backend code
- `mobile-react-expert`: Mobile-responsive React components
- `python-api-expert`: API endpoints and services
- `devops-engineer`: Deployment and infrastructure

### Review Agents

#### `fullstack-code-reviewer`
**Purpose**: Review code quality across frontend and backend
**Scope**: ONLY task-specific changes
**Skills**:
- Code quality assessment
- Security review
- Performance analysis
- Architecture validation

#### `pr-merge-agent`
**Purpose**: Handle PR creation and merge operations
**Skills**:
- PR description generation
- Documentation gathering
- Merge coordination
- Resource cleanup

---

## Git Worktree Management

### Why Worktrees?

**Benefits**:
- **Isolation**: Each task has its own workspace
- **Parallel Development**: Work on multiple tasks simultaneously
- **Clean Separation**: No branch switching in main repo
- **Easy Cleanup**: Delete worktree when task complete

### Worktree Structure

```
project-root/
├── .git/                     # Main repository
├── worktrees/                # All task worktrees
│   ├── task-1/               # Worktree for task #1
│   │   ├── Analyse/          # Analysis documentation
│   │   │   ├── requirements.md
│   │   │   └── architecture.md
│   │   ├── Tests/            # Testing documentation
│   │   │   └── test-plan.md
│   │   ├── src/              # Source code
│   │   └── ...
│   ├── task-2/               # Worktree for task #2
│   └── ...
└── ...
```

### Worktree Commands

**Create worktree** (automated):
```bash
git worktree add worktrees/task-[id] -b feature/task-[id]
```

**List worktrees**:
```bash
git worktree list
```

**Remove worktree**:
```bash
git worktree remove --force worktrees/task-[id]
```

### Worktree Best Practices

1. **One task per worktree**: Don't mix tasks
2. **Regular commits**: Commit frequently in worktree
3. **Stay synced**: Merge main regularly to avoid conflicts
4. **Clean up after merge**: Remove worktree when task complete
5. **Use descriptive branches**: `feature/task-[id]` naming

---

## Project Mode Integration

### SIMPLE Mode

**Workflow differences**:
- ❌ NO Analysis phase (skip requirements/architecture)
- ❌ NO Worktrees (work directly in main branch)
- ❌ NO Testing phase (no test environment setup)
- ❌ NO Code Review (no review required)
- ❌ NO Pull Requests (direct commits to main)

**Workflow**: Backlog → In Progress → Done

### DEVELOPMENT Mode

**Full workflow**:
- ✅ Analysis phase with automated agents
- ✅ Worktrees for isolated development (optional toggle)
- ✅ Testing phase with test environment
- ✅ Code Review before merge (includes PR creation and management)
- ✅ Pull Requests required

**Workflow**: Backlog → Analysis → In Progress → Testing → Code Review → Done (6 columns)

**Worktree Toggle**: Can enable/disable worktrees in DEVELOPMENT mode while keeping full workflow.

**Note:** As of 2025-11-26, the workflow was simplified from 7 to 6 columns by merging PR status into Code Review.

---

## MCP Tools for Workflow

### Task Status Management

```bash
# Get task queue
mcp:get_task_queue

# Get specific task
mcp:get_task --task_id=[id]

# Update task status
mcp:update_status --task_id=[id] --status="[new-status]"
```

### Stage Results

```bash
# Save analysis results
mcp:append_stage_result --task_id=[id] --status="Analysis" \
  --summary="Analysis complete" \
  --details="Requirements and architecture created"

# Save implementation results
mcp:append_stage_result --task_id=[id] --status="In Progress" \
  --summary="Implementation complete" \
  --details="Feature implemented per architecture.md"

# Save testing results
mcp:append_stage_result --task_id=[id] --status="Testing" \
  --summary="Testing complete" \
  --details="All tests passed, ready for review"
```

### Testing URLs

```bash
# Save testing URLs (CRITICAL - MANDATORY)
mcp:set_testing_urls --task_id=[id] \
  --urls='{"frontend": "http://localhost:[PORT]", "backend": "http://localhost:[PORT]"}'

# Get testing URLs
mcp:get_task --task_id=[id]
# Returns task with testing_urls field
```

### Session Management

```bash
# Stop Claude session and cleanup resources
mcp:stop_session [task-id]
```

---

## Workflow Monitoring

### Coordinator Responsibilities

The coordinator agent continuously:
1. **Monitors task queue**: Checks for new tasks
2. **Detects status changes**: Watches for transitions
3. **Auto-transitions**: Moves tasks through workflow
4. **Delegates to agents**: Assigns work to specialists
5. **Manages resources**: Starts/stops test environments
6. **Updates task state**: Saves progress and results

### Auto-Transitions

**Automatic** (no user action required):
- Analysis → In Progress (after analysis complete)
- In Progress → Testing (when implementation detected)

**Manual** (requires user action):
- Backlog → Analysis (user runs `/start-feature`)
- Testing → Code Review (user confirms tests pass)
- Code Review → PR (user runs `/PR`)
- PR → Done (user runs `/merge` after PR merged)

### Implementation Detection

Coordinator monitors for:
- **Recent commits**: Commits in worktree with completion keywords
- **Agent reports**: Implementation agent completion notifications
- **User signals**: User indicates development finished
- **File changes**: Significant code changes detected

When detected, coordinator:
1. Auto-transitions task to "Testing"
2. Saves implementation summary to stage_results
3. Prepares test environment
4. Saves testing URLs to task database
5. Notifies user test environment is ready

---

## Troubleshooting

### Analysis Not Starting

**Symptom**: `/start-feature` command doesn't trigger agents

**Solutions**:
- Verify task is in "Backlog" status
- Check agent files exist in `framework-assets/claude-agents/`
- Verify MCP server is running
- Check coordinator logs for errors

### Worktree Creation Failed

**Symptom**: Worktree not created for task

**Solutions**:
- Check `worktrees/` directory exists
- Verify git repository is initialized
- Ensure no conflicting worktrees exist
- Check disk space available

### Test Environment Not Starting

**Symptom**: Test servers don't start or URLs not saved

**Solutions**:
- Check ports are not already occupied: `lsof -i :[PORT]`
- Verify backend and frontend can start manually
- Check testing URLs were saved with `mcp:set_testing_urls`
- Review coordinator logs for port conflicts

### PR Creation Failed

**Symptom**: `/PR` command fails to create pull request

**Solutions**:
- Verify `gh` CLI is installed and authenticated
- Check requirements.md and architecture.md exist
- Ensure all changes are committed
- Verify git remote is configured

### Cleanup Not Working

**Symptom**: Resources not cleaned up after `/merge`

**Solutions**:
- Manually kill processes: `kill [PID]`
- Manually remove worktree: `git worktree remove --force worktrees/task-[id]`
- Check for zombie processes: `ps aux | grep task-[id]`
- Verify cleanup was triggered with task_id

---

## Best Practices

### For Analysis Phase
1. **Review generated docs**: Always read requirements.md and architecture.md
2. **Refine if needed**: Edit documents if analysis missed details
3. **Ask questions**: Clarify requirements before implementation
4. **Keep docs updated**: Update if implementation differs

### For Development Phase
1. **Follow architecture**: Stick to the technical plan
2. **Test as you go**: Don't wait until the end
3. **Make small commits**: Frequent, descriptive commits
4. **Stay in worktree**: Don't switch branches in main repo
5. **Document changes**: Add comments and update docs

### For Testing Phase
1. **Test all criteria**: Check every acceptance criterion
2. **Document thoroughly**: Record all test results
3. **Report bugs clearly**: Detailed bug descriptions in test-plan.md
4. **Test edge cases**: Don't just test happy path
5. **Keep URLs saved**: Always save testing URLs to task database

### For Code Review Phase
1. **Review only task changes**: Use `git diff main..HEAD`
2. **Check against requirements**: Verify all criteria met
3. **Be thorough**: Don't rush the review
4. **Provide constructive feedback**: Specific, actionable comments
5. **Approve when ready**: Don't approve with outstanding issues

### For PR Phase
1. **Write clear descriptions**: Comprehensive PR summaries
2. **Link documentation**: Reference requirements and architecture
3. **Wait for checks**: Let CI/CD complete
4. **Address feedback**: Respond to all review comments
5. **Clean merge**: Ensure no conflicts with main

### For Completion Phase
1. **Verify PR merged**: Check main branch has changes
2. **Run cleanup**: Always use `/merge` command
3. **Confirm resources freed**: Check processes terminated
4. **Archive task**: Move to "Done" status
5. **Document learnings**: Note any issues for future tasks

---

## Related Documentation

- [Project Modes](./project-modes.md) - SIMPLE vs DEVELOPMENT mode details
- [MCP Tools Reference](../api/mcp-tools.md) - Complete MCP tool documentation
- [Slash Commands](../../framework-assets/claude-commands/README.md) - All available commands
- [Specialized Agents](../../framework-assets/claude-agents/README.md) - Agent capabilities

---

**Last Updated**: 2025-11-21
**Version**: 1.0.0
**Workflow Status**: Active in DEVELOPMENT mode
