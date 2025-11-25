# Project Modes Documentation

This document describes the two operational modes available in the ClaudeTask Framework and their implications for development workflow.

## Overview

The framework supports two distinct operational modes:
1. **SIMPLE Mode** - Streamlined workflow for rapid development
2. **DEVELOPMENT Mode** - Full development lifecycle with quality gates

The mode is configured at project creation and explicitly displayed at the top of `CLAUDE.md`, determining:
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
- Solo developer projects
- Rapid prototyping phase
- Internal tools with low risk
- Learning and experimentation
- Small projects (< 5 tasks simultaneously)

### Configuration in CLAUDE.md
When a project is created in SIMPLE mode, the generated `CLAUDE.md` contains:

```markdown
# 🎯 PROJECT MODE: SIMPLE

**This project is configured in SIMPLE mode.**

## Task Workflow (3 Columns)
- **Backlog**: Tasks waiting to be started
- **In Progress**: Tasks currently being worked on
- **Done**: Completed tasks

## What this means:
- ✅ **NO Git workflow** - Direct work, no branches, no PRs
- ✅ **NO complex statuses** - Just Backlog → In Progress → Done
- ✅ **Simplified task management** - Focus on getting work done
- ✅ **No worktrees, no version control complexity**

## Your approach:
1. Follow simple Backlog → In Progress → Done flow
2. Work directly in main branch
3. No worktrees, no test environments
4. Mark done only when user explicitly requests
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

**Current Project Status**: This project is configured in DEVELOPMENT mode.

### Worktree Toggle Feature

DEVELOPMENT mode supports **optional Git worktrees** via a toggle switch:

- **Worktrees Enabled (Default)**: Each task gets isolated workspace in `worktrees/task-{id}/`
- **Worktrees Disabled**: Work directly in main branch or manual feature branches

**Why Toggle Worktrees?**
- Some repositories don't support worktrees (Git LFS, submodules)
- Solo developers may prefer simpler workflow
- Gradual adoption of worktree workflow
- Flexibility for different project needs

**How to Toggle:**
1. Open project in ClaudeTask UI
2. Go to TaskBoard page
3. Look for worktree toggle switch next to project mode indicator (only visible in DEVELOPMENT mode)
4. Toggle on/off as needed
5. CLAUDE.md is automatically regenerated with appropriate instructions

**Technical Implementation:**
- Database field: `project_settings.worktree_enabled` (BOOLEAN, default: true)
- UI component: `ProjectModeToggle.tsx` with Switch control
- Backend: Automatic CLAUDE.md regeneration on toggle via `claude_config_generator.py`
- WebSocket: Real-time broadcast of setting changes

### Configuration in CLAUDE.md
When a project is created in DEVELOPMENT mode, the generated `CLAUDE.md` contains:

```markdown
# 🎯 PROJECT MODE: DEVELOPMENT

**This project is configured in DEVELOPMENT mode.**

## Task Workflow (6 Columns)
- **Backlog**: New tasks waiting to be analyzed
- **Analysis**: Understanding requirements and planning
- **In Progress**: Active development with Git worktrees
- **Testing**: Running tests and validation
- **Code Review**: Peer review of changes and PR management
- **Done**: Completed and merged

## What this means:
- ✅ **Full Git workflow** - Branches, worktrees, PRs
- ✅ **Complete development lifecycle** - From analysis to deployment
- ✅ **Version control** - Proper branching and merge strategy
- ✅ **Quality gates** - Testing and code review required
- ✅ **Worktrees**: Enabled - isolated task workspaces

## Your approach:
1. Follow the complete task workflow through all statuses
2. Create worktrees for each task
3. Use proper branching strategy
4. Create PRs and wait for review
5. Ensure tests pass before moving forward
```

When **worktrees are disabled**, the mode section changes to:

```markdown
## Task Workflow (6 Columns)
- **In Progress**: Active development without worktrees

## What this means:
- ❌ **Worktrees**: Disabled - work directly in main branch

## Your approach:
2. Work in main branch or feature branches (worktrees disabled)
```

### Task Workflow (6 Columns)
```
Backlog → Analysis → In Progress → Testing → Code Review → Done
```

**Important Change (2025-11-26):** The workflow has been simplified from 7 to 6 columns. The separate "PR" status has been merged into "Code Review". Pull request creation and management now occur during the Code Review phase.

### Characteristics
- **Full Git Workflow**: Feature branches, worktrees (optional), pull requests
- **Complete Development Lifecycle**: From analysis to deployment
- **Version Control**: Proper branching and merge strategy
- **Quality Gates**: Testing and code review required before merge
- **Worktree Management**: Isolated development environments per task (can be toggled on/off)

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
- Active development in task worktree (if worktrees enabled) or main branch (if disabled)
- Feature branch created (if worktrees enabled)
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
- **PR creation** during this phase (if not already created)
- Awaiting merge approval
- CI/CD checks (if configured)
- **Manual merge** by user or team lead after review approval

#### 6. Done
- Merged to main branch
- Worktree cleaned up (if worktrees enabled)
- Resources released
- Task archived

### When to Use DEVELOPMENT Mode
- Production applications
- Team development (2+ developers)
- Quality-critical projects
- Customer-facing applications
- Projects requiring code review
- Regulatory compliance requirements
- Long-term maintenance projects

### Workflow Example
```
1. User creates task → Backlog
2. Coordinator delegates to analysts → Analysis
   - Business analyst creates requirements
   - Systems analyst creates technical spec
   - Auto-transition to In Progress
3. Coordinator sets up worktree → In Progress (if worktrees enabled)
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
   - PR created with changes summary
   - Awaits user merge approval
6. User merges PR → Done
   - Coordinator cleans up worktree (if worktrees enabled)
   - Releases resources
   - Task archived
```

## Mode Comparison

| Feature | SIMPLE Mode | DEVELOPMENT Mode |
|---------|-------------|------------------|
| **Statuses** | 3 (Backlog, In Progress, Done) | 6 (Full lifecycle) |
| **Git Workflow** | None (direct to main) | Feature branches + PRs |
| **Worktrees** | No | Optional (toggle on/off) |
| **Analysis Phase** | No | Yes (automatic delegation) |
| **Testing Phase** | No | Yes (manual testing) |
| **Code Review** | No | Yes (includes PR management) |
| **Pull Requests** | No | Yes (created during Code Review) |
| **Quality Gates** | None | Testing + Review |
| **Team Size** | 1 developer | 1+ developers |
| **Best For** | Prototypes, internal tools | Production, team projects |
| **Mode Selection** | At project creation | At project creation |
| **Mode Visibility** | Explicit in CLAUDE.md | Explicit in CLAUDE.md |

## Project Creation and Mode Selection

### Mode Selection During Setup

As of 2025-11-20, project mode is **selected during project creation** in the Project Setup page:

**Project Setup UI:**
```tsx
<FormControl component="fieldset">
  <FormLabel>Project Mode</FormLabel>
  <RadioGroup value={projectData.project_mode || 'simple'}>
    <FormControlLabel
      value="simple"
      label="Simple Mode - 3 columns: Backlog → In Progress → Done. Direct work, no branches or PRs."
    />
    <FormControlLabel
      value="development"
      label="Development Mode - Full workflow with Git integration, worktrees, testing, code review, and PRs."
    />
  </RadioGroup>
</FormControl>
```

**Default Mode**: `simple` (selected by default for new projects)

**Mode Persistence**:
- Mode is stored in `projects.project_mode` database field
- Cannot be changed after project creation (immutable)
- CLAUDE.md explicitly displays the selected mode at the top

### CLAUDE.md Mode Indicator

The `claude_config_generator.py` service automatically inserts an explicit mode indicator at the top of every generated CLAUDE.md:

```python
# Insert explicit project mode indicator at the top
mode_upper = project_mode.upper()
mode_indicator = f"""
# 🎯 PROJECT MODE: {mode_upper}

**This project is configured in {mode_upper} mode.**

## Task Workflow ({'3 Columns' if project_mode == 'simple' else '6 Columns'})
"""
```

This ensures Claude Code always knows which mode the project is operating in.

## Switching Between Modes

### Important: Mode is Immutable After Creation

**As of 2025-11-20, project mode CANNOT be changed after project creation.**

The mode selection is:
- Made during project setup
- Stored in database
- Explicitly displayed in CLAUDE.md
- Immutable throughout project lifecycle

**Why Immutable?**
- Prevents confusion from mid-project workflow changes
- Ensures consistent task management approach
- Avoids complications with existing tasks in different statuses
- Simplifies CLAUDE.md generation logic

**If You Need Different Mode:**
1. Create a new project with desired mode
2. Migrate tasks manually if needed
3. Archive old project

### Legacy: SIMPLE → DEVELOPMENT (Historical Reference)

**Historical process (no longer supported):**

**When to Switch**:
- Project grows beyond solo development
- Need code review and quality gates
- Preparing for production deployment
- Adding team members

**How to Switch** (legacy):
1. Edit `CLAUDE.md` at project root
2. Change mode header from SIMPLE to DEVELOPMENT
3. Update task workflow section
4. Commit changes
5. Existing tasks can continue in current status
6. New tasks will follow DEVELOPMENT workflow

**Migration Considerations**:
- Existing In Progress tasks: Move to Analysis or Testing as appropriate
- No worktrees exist: Enable worktree toggle and create worktrees for active tasks
- Alternatively: Keep worktrees disabled and work in main branch
- Update team on new workflow

### Legacy: DEVELOPMENT → SIMPLE (Historical Reference)

**Historical process (no longer supported):**

**When to Switch**:
- Moving to solo development
- Internal prototype or POC
- Need faster iteration
- Reducing process overhead

**How to Switch** (legacy):
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

## Mode Configuration in Code

### Backend: claude_config_generator.py

The CLAUDE.md generation service handles mode-specific configuration:

```python
def generate_claude_md(
    project_name: str,
    project_path: str,
    tech_stack: List[str],
    custom_instructions: str = "",
    project_mode: str = "simple",
    worktree_enabled: bool = True
) -> str:
    # Insert explicit project mode indicator
    mode_upper = project_mode.upper()
    mode_indicator = f"""
# 🎯 PROJECT MODE: {mode_upper}

**This project is configured in {mode_upper} mode.**
"""

    if project_mode == "simple":
        mode_indicator += """
## Task Workflow (3 Columns)
- **Backlog**: Tasks waiting to be started
- **In Progress**: Tasks currently being worked on
- **Done**: Completed tasks

## What this means:
- ✅ **NO Git workflow** - Direct work, no branches, no PRs
- ✅ **NO complex statuses** - Just Backlog → In Progress → Done
"""
    else:  # development mode
        worktree_text = "with Git worktrees" if worktree_enabled else "without worktrees"
        mode_indicator += f"""
## Task Workflow (6 Columns)
- **In Progress**: Active development {worktree_text}

## What this means:
- {"✅" if worktree_enabled else "❌"} **Worktrees**: {"Enabled" if worktree_enabled else "Disabled"}
"""

    # Insert mode indicator after first heading
    lines = template_content.split('\n')
    template_content = lines[0] + '\n' + mode_indicator + '\n'.join(lines[1:])

    return template_content
```

### Frontend: ProjectSetup.tsx

Project mode selection in UI:

```tsx
const [projectData, setProjectData] = useState({
  project_name: '',
  github_repo: '',
  force_reinitialize: false,
  project_mode: 'simple',  // Default to simple mode
});

// Radio group for mode selection
<FormControl component="fieldset">
  <FormLabel>Project Mode</FormLabel>
  <RadioGroup
    value={projectData.project_mode || 'simple'}
    onChange={(e) => setProjectData({
      ...projectData,
      project_mode: e.target.value as 'simple' | 'development'
    })}
  >
    <FormControlLabel value="simple" label="Simple Mode" />
    <FormControlLabel value="development" label="Development Mode" />
  </RadioGroup>
</FormControl>
```

### Database Schema

```sql
-- projects table
CREATE TABLE projects (
  id TEXT PRIMARY KEY,
  name TEXT NOT NULL,
  project_mode TEXT DEFAULT 'simple',  -- 'simple' or 'development'
  ...
);

-- project_settings table
CREATE TABLE project_settings (
  id INTEGER PRIMARY KEY,
  project_id TEXT UNIQUE NOT NULL,
  worktree_enabled BOOLEAN DEFAULT 1 NOT NULL,  -- Only relevant in development mode
  ...
);
```

## CLAUDE.md Regeneration

### Regeneration Script

A migration script is available to regenerate CLAUDE.md for existing projects:

**Location**: `claudetask/backend/migrations/regenerate_claude_md.py`

**Usage**:
```bash
python migrations/regenerate_claude_md.py <project_id>
```

**What It Does**:
1. Reads project configuration from database (mode, worktree_enabled, custom_instructions)
2. Generates fresh CLAUDE.md content using `claude_config_generator.py`
3. Creates backup of existing CLAUDE.md (→ CLAUDE.md.backup)
4. Writes new CLAUDE.md with explicit mode indicator
5. Updates `projects.claude_config` field in database

**When to Use**:
- After changing worktree_enabled setting via UI
- To add explicit mode indicator to legacy projects
- To sync CLAUDE.md with database configuration
- After framework updates that change CLAUDE.md template

**Example Output**:
```
Project: My Project
Path: /path/to/project
Mode: development
Worktree enabled: True
✓ CLAUDE.md regenerated successfully
✓ Backup saved to CLAUDE.md.backup
✓ Database updated
```

### Automatic Regeneration

CLAUDE.md is automatically regenerated in these scenarios:

1. **Project Creation**: Fresh CLAUDE.md generated with selected mode
2. **Worktree Toggle**: When user toggles worktree switch in UI (DEVELOPMENT mode only)
3. **Framework Update**: When framework files are synced to project
4. **Settings Update**: When project settings are modified via API

The regeneration always:
- Preserves custom instructions
- Respects current project mode
- Includes worktree setting (for DEVELOPMENT mode)
- Creates backup before overwriting
- Updates database `claude_config` field

## Best Practices

### SIMPLE Mode Best Practices
1. **Keep Tasks Small**: Focus on small, manageable tasks
2. **Commit Frequently**: Regular commits to main branch
3. **Test Locally**: Manual testing before marking done
4. **Document as You Go**: Update docs with code changes
5. **Quick Iterations**: Embrace rapid development cycle

### DEVELOPMENT Mode Best Practices
1. **Complete Analysis**: Don't skip analysis phase
2. **Use Worktrees** (if enabled): One worktree per task for isolation
3. **Write Tests**: Include tests with implementation
4. **Request Review**: Always get code review before merge
5. **Test Thoroughly**: Manual testing before code review
6. **Clean PRs**: Keep PRs focused and well-documented
7. **Clean Up**: Always clean up worktrees after merge (if worktrees enabled)

### Worktree Toggle Best Practices
- **Enable worktrees** for parallel development on multiple tasks
- **Disable worktrees** if repository has Git LFS or submodule issues
- **Disable worktrees** for solo development with simple workflow
- **Enable worktrees** when onboarding new team members (prevents conflicts)
- Toggle can be changed at any time without data loss

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

- [CLAUDE.md Template](../../framework-assets/claude-configs/CLAUDE.md) - Base template for CLAUDE.md generation
- [Task Workflow Documentation](../claudetask/workflow.md) - Detailed workflow guide (to be created)
- [Git Worktree Guide](../claudetask/worktree-guide.md) - Worktree management (to be created)
- [ProjectModeToggle Component](../components/ProjectModeToggle.md) - UI component for worktree toggle
- [Database Migrations](../deployment/database-migrations.md) - Migration 005 (worktree toggle)

## Troubleshooting

### Mode Indicator Not Appearing in CLAUDE.md
**Symptom**: CLAUDE.md doesn't show "🎯 PROJECT MODE: ..." at the top

**Solution**:
```bash
# Regenerate CLAUDE.md for project
python migrations/regenerate_claude_md.py <project_id>

# Or update via UI (toggle worktree setting twice to trigger regeneration)
```

### Worktree Toggle Not Visible
**Symptom**: Switch doesn't appear in DEVELOPMENT mode

**Possible Causes**:
1. Project mode is SIMPLE (toggle only in DEVELOPMENT)
2. Migration 005 not run (worktree_enabled column missing)

**Solution**: See [ProjectModeToggle Component Troubleshooting](../components/ProjectModeToggle.md#troubleshooting)

### CLAUDE.md Out of Sync with Database
**Symptom**: CLAUDE.md shows different mode or worktree setting than database

**Solution**:
```bash
# Check database values
sqlite3 claudetask/backend/claudetask.db << EOF
SELECT p.name, p.project_mode, ps.worktree_enabled
FROM projects p
JOIN project_settings ps ON p.id = ps.project_id;
EOF

# Regenerate CLAUDE.md
python migrations/regenerate_claude_md.py <project_id>
```

---

**Current Project Mode**: DEVELOPMENT
**Worktree Setting**: Enabled
**Workflow Columns**: 6 (PR merged into Code Review as of 2025-11-26)
**Last Updated**: 2025-11-26
**Mode Selection**: At project creation (immutable)
**Mode Visibility**: Explicit indicator in CLAUDE.md
