# Slash Commands Reference

Complete reference for all available slash commands in the Claude Code Feature Framework.

## Overview

Slash commands provide quick access to workflow automation features. They trigger specialized agents and automate common development tasks.

## Command Categories

- **Workflow Commands**: Control task progression through development lifecycle
- **Analysis Commands**: Generate requirements and architecture documentation
- **Testing Commands**: Setup and manage test environments
- **Review Commands**: Create PRs and manage code reviews
- **Git Commands**: Version control and commit/push operations (NEW)
- **Documentation Commands**: Automated documentation updates
- **Skill Commands**: Manage Claude Code skills
- **Hook Commands**: Configure automated workflow hooks
- **Utility Commands**: General utilities and helpers

---

## Workflow Commands

### `/start-feature [task-id]`

**Phase**: Backlog → Analysis
**Purpose**: Start analysis phase for a new feature
**Mode**: DEVELOPMENT only

**What it does**:
1. Delegates to `requirements-analyst` agent
2. Creates `worktrees/task-{id}/Analyze/Requirements/` (3 files)
3. Delegates to `system-architect` agent
4. Creates `worktrees/task-{id}/Analyze/Design/` (4 files)
5. Creates git worktree at `worktrees/task-{id}/`
6. Creates feature branch `feature/task-{id}`
7. Auto-transitions task to "In Progress" status

**Prerequisites**:
- Task must be in "Backlog" status
- Project must be in DEVELOPMENT mode

**Example Usage**:
```
/start-feature 42
```

**Expected Output**:
```
✅ Analysis Started for Task #42

Requirements Writer Agent:
- Creating business requirements...
- Analyzing user needs...
✓ requirements.md created

System Architect Agent:
- Designing system architecture...
- Planning implementation...
✓ architecture.md created

Worktree Setup:
✓ Created worktree at worktrees/task-42
✓ Created branch feature/task-42
✓ Analysis documents ready

Task #42 moved to "In Progress"
Ready for development!
```

**Related Documentation**:
- [Intelligent Workflow](../architecture/intelligent-workflow.md#phase-2-analysis)
- [Requirements Analyst Agent](../../framework-assets/claude-agents/requirements-analyst.md)
- [System Architect Agent](../../framework-assets/claude-agents/system-architect.md)

---

### `/start-develop [task-id]`

**Phase**: Analysis → Development
**Purpose**: Begin implementation after analysis complete
**Mode**: DEVELOPMENT only

**What it does**:
1. Verifies `requirements.md` exists in Analyse/ folder
2. Verifies `architecture.md` exists in Analyse/ folder
3. Reads and displays both documents
4. Updates task status to "In Progress" (if not already)
5. Provides implementation guidelines

**Prerequisites**:
- Task must be in "Analyse" status or have completed analysis
- `requirements.md` must exist
- `architecture.md` must exist
- Task worktree must be created

**Example Usage**:
```
/start-develop 42
```

**Expected Output**:
```
✅ Starting Development Phase for Task #42

Analysis Documents Found:
✓ requirements.md
✓ architecture.md

Requirements Summary:
- User Story: As a user, I want to continue a task...
- Acceptance Criteria:
  - [ ] Button appears on task cards
  - [ ] Clicking button navigates to task session
  - [ ] Button shows correct state

Architecture Summary:
- Frontend: Add ContinueButton component to TaskCard
- Backend: No changes required
- Integration: Use existing session API

Implementation Checklist:
- [ ] Read and understand requirements.md
- [ ] Read and understand architecture.md
- [ ] Implement core functionality
- [ ] Write tests
- [ ] Make clean commits

Working Directory: worktrees/task-42
Branch: feature/task-42

Ready to implement!
```

**Related Documentation**:
- [Intelligent Workflow](../architecture/intelligent-workflow.md#phase-3-development)
- [Development Guidelines](../architecture/intelligent-workflow.md#32-implementation-guidelines)

---

### `/test [task-id]`

**Phase**: In Progress → Testing
**Purpose**: Setup test environment for manual testing
**Mode**: DEVELOPMENT only

**What it does**:
1. Finds available ports for backend and frontend
2. Starts backend test server: `uvicorn app.main:app --port [FREE_PORT]`
3. Starts frontend test server: `PORT=[FREE_PORT] npm start`
4. Saves testing URLs to task database using `mcp:set_testing_urls`
5. Creates `Tests/` folder in worktree
6. Creates `test-plan.md` template
7. Updates task status to "Tests"
8. Notifies user with test environment URLs

**Prerequisites**:
- Task must be in "In Progress" status
- Implementation must be complete
- Code must be committed

**Example Usage**:
```
/test 42
```

**Expected Output**:
```
✅ Test Environment Ready for Task #42

Starting Test Servers:
✓ Backend: http://localhost:4000
✓ Frontend: http://localhost:3001
✓ Testing URLs saved to task database

Test Plan Template:
✓ Created Tests/test-plan.md

Task #42 moved to "Tests" status

Manual Testing Instructions:
1. Access frontend: http://localhost:3001
2. Test all acceptance criteria from requirements.md
3. Document results in Tests/test-plan.md
4. Report any bugs found

When testing complete, move to "Code Review"
```

**Important**: Testing URLs are MANDATORY and must be saved to task database.

**Related Documentation**:
- [Intelligent Workflow](../architecture/intelligent-workflow.md#phase-4-testing)
- [Testing Phase Guidelines](../architecture/intelligent-workflow.md#42-manual-testing)

---

### `/PR [task-id]`

**Phase**: Code Review → Pull Request
**Purpose**: Create pull request for reviewed code
**Mode**: DEVELOPMENT only

**What it does**:
1. Verifies prerequisites (analysis docs, test plan)
2. Reads requirements.md, architecture.md, test-plan.md
3. Gets list of changed files
4. Gets commit history
5. Delegates to `pr-merge-agent`
6. Creates comprehensive PR description
7. Executes `gh pr create` with proper formatting
8. Updates task status to "PR"
9. Returns PR URL

**Prerequisites**:
- Task must be in "Code Review" or "Tests" status
- All tests passed
- requirements.md exists
- architecture.md exists
- All code committed and pushed

**Example Usage**:
```
/PR 42
```

**Expected Output**:
```
✅ Creating Pull Request for Task #42

Gathering PR Information:
✓ requirements.md read
✓ architecture.md read
✓ test-plan.md read
✓ Changed files: 5
✓ Commits: 8

PR Merge Agent:
- Creating comprehensive PR description...
- Linking task documentation...
- Creating PR with gh CLI...

✅ Pull Request Created!

PR URL: https://github.com/user/repo/pull/123
Title: feat(task-42): Add continue button to task cards

Task #42 moved to "PR" status

Next Steps:
- Wait for CI/CD checks
- Wait for code review approval (if manual_mode)
- Merge PR manually or use /merge command
```

**Related Documentation**:
- [Intelligent Workflow](../architecture/intelligent-workflow.md#phase-6-pull-request)
- [PR Merge Agent](../../framework-assets/claude-agents/pr-merge-agent.md)

---

### `/merge [task-id]`

**Phase**: PR → Done
**Purpose**: Complete task and cleanup all resources
**Mode**: DEVELOPMENT only

**What it does**:
1. Verifies PR is merged to main branch
2. Stops Claude Code session for task
3. Terminates embedded terminal sessions
4. Kills all test server processes
5. Releases occupied ports
6. Clears testing URLs from task database
7. Updates task status to "Done"
8. Optional: Removes task worktree

**Prerequisites**:
- Task must be in "PR" status
- PR must be merged to main branch
- User has explicitly requested merge

**Example Usage**:
```
/merge 42
```

**Expected Output**:
```
✅ Merging Task #42

Verification:
✓ PR is merged to main
✓ Changes are in main branch

Cleanup Process:
✓ Claude session completed
✓ Terminal sessions stopped
✓ Backend server (PID 12345) terminated
✓ Frontend server (PID 12346) terminated
✓ Ports released: 4000, 3001
✓ Testing URLs cleared

Task #42 moved to "Done"

✅ Task Completed Successfully!

All resources cleaned up.
Worktree kept at: worktrees/task-42
(Remove manually with: git worktree remove --force worktrees/task-42)
```

**Related Documentation**:
- [Intelligent Workflow](../architecture/intelligent-workflow.md#phase-7-merge-and-completion)
- [Resource Cleanup](../architecture/intelligent-workflow.md#72-cleanup-process)

---

## Git Commands

### `/git-push`

**Purpose**: Commit all changes and push to origin remote
**Category**: Version Control
**Allowed Tools**: Bash, Read, Glob, Grep

**What it does**:
1. Checks current git status and recent commit style
2. Stages all modified and untracked files (`git add -A`)
3. Analyzes changes to generate appropriate commit message
4. Creates commit with conventional format (feat/fix/docs/etc)
5. Pushes changes to origin remote
6. Verifies successful push

**Prerequisites**:
- Git repository initialized
- Remote named `origin` configured
- User has push permissions to remote

**Example Usage**:
```
/git-push
```

**Expected Output**:
```
Analyzing changes...
📋 Modified files: 3
📄 New files: 1

Creating commit...
✅ Changes committed and pushed!

📝 Commit: a1b2c3d
📌 Message: feat: Add Sessions page with unified tab interface
🌿 Branch: main
📁 Files changed: 4
🚀 Pushed to: origin/main
```

**Commit Message Format**:
The command automatically generates conventional commit messages:
- `feat:` - New feature or functionality
- `fix:` - Bug fix
- `docs:` - Documentation only
- `style:` - Formatting, no code change
- `refactor:` - Code restructuring
- `test:` - Adding tests
- `chore:` - Maintenance tasks

**Security Checks**:
Before committing, the command verifies:
- No secrets or credentials in changes (.env, API keys, passwords)
- No sensitive files being committed
- .gitignore is properly configured

If sensitive files are detected, **commit is aborted** and user is alerted.

**Error Handling**:

**No changes to commit**:
```
ℹ️ No changes to commit. Working tree is clean.
```

**Remote has new commits (push rejected)**:
```bash
# Automatically attempts rebase and retry:
git pull --rebase origin <branch>
git push
```

**Permission denied**:
```
❌ Push failed: Permission denied
Please check repository access and authentication.
```

**Related Documentation**:
- [Git Workflow Command](../../framework-assets/claude-commands/git-push.md)
- [Git Best Practices](../skills/git-workflow.md)

---

## Documentation Commands

### `/update-documentation [scope]`

**Purpose**: Update project documentation automatically
**Trigger**: Post-merge hook or manual

**What it does**:
1. Analyzes recent git changes
2. Identifies affected documentation areas
3. Delegates to `documentation-updater-agent`
4. Updates/creates/deletes documentation files
5. Commits changes with `[skip-hook]` tag
6. Pushes to origin

**Scopes**:
- `all` (default): Update all documentation
- `api`: Update only API documentation
- `components`: Update only component docs
- `architecture`: Update only architecture docs
- `deployment`: Update only deployment docs

**Example Usage**:
```
/update-documentation all
/update-documentation api
/update-documentation components
```

**Expected Output**:
```
✅ Documentation Update Complete

Analyzed Changes:
- 5 files modified in last commit
- 2 new components added
- 1 API endpoint changed

Updated Files:
✓ docs/api/endpoints/settings.md
✓ docs/components/ContinueButton.md

Created Files:
✓ docs/architecture/intelligent-workflow.md

Deleted Files:
✓ docs/components/OldComponent.md (component removed)

✅ Committed and pushed documentation updates
```

**Related Documentation**:
- [Documentation Updater Agent](../../framework-assets/claude-agents/documentation-updater-agent.md)
- [Documentation System](../README.md#documentation-maintenance)

---

## Skill Commands

### `/create-skill [skill-name]`

**Purpose**: Create a new custom skill for Claude Code

**What it does**:
1. Creates skill file in project `.claude/skills/` directory
2. Adds skill metadata and template
3. Registers skill in project skills database
4. Enables skill for project

**Example Usage**:
```
/create-skill my-custom-skill
```

**Expected Output**:
```
✅ Custom Skill Created

Skill: my-custom-skill
Location: .claude/skills/my-custom-skill.md
Status: Enabled

Edit the skill file to add:
- Description
- Instructions
- Example usage
- Knowledge base

Skill is now available to Claude Code in this project.
```

**Related Documentation**:
- [Skills System](../skills/README.md)
- [Creating Custom Skills](../skills/README.md#creating-custom-skills)

---

### `/edit-skill [skill-name]`

**Purpose**: Edit an existing custom skill

**What it does**:
1. Opens skill file in editor
2. Allows modification of skill content
3. Validates skill format
4. Saves and reloads skill

**Example Usage**:
```
/edit-skill my-custom-skill
```

---

## Hook Commands

### `/create-hook [hook-name]`

**Purpose**: Create a new custom hook for automation

**What it does**:
1. Creates hook script in `.claude/hooks/` directory
2. Makes script executable
3. Registers hook in project hooks database
4. Enables hook for project

**Example Usage**:
```
/create-hook pre-commit-validation
```

**Expected Output**:
```
✅ Custom Hook Created

Hook: pre-commit-validation
Location: .claude/hooks/pre-commit-validation.sh
Event: PreToolUse (configure in UI)
Status: Enabled

Edit the hook script to add automation logic.
Configure hook event and filters in Hooks UI.
```

**Related Documentation**:
- [Hooks System](../architecture/hooks-system.md)
- [Creating Custom Hooks](../architecture/hooks-system.md#creating-hooks)

---

### `/edit-hook [hook-name]`

**Purpose**: Edit an existing custom hook

**What it does**:
1. Opens hook script in editor
2. Allows modification of hook logic
3. Validates script syntax
4. Saves and reloads hook

**Example Usage**:
```
/edit-hook pre-commit-validation
```

---

## Command Usage Best Practices

### 1. Workflow Commands

**Follow the sequence**:
```
/start-feature → Development → /test → Review → /PR → /merge
```

**Don't skip phases**: Each phase builds on the previous one.

**Wait for completion**: Let automated agents finish before proceeding.

### 2. Testing Commands

**Always save URLs**: Testing URLs must be saved to task database.

**Document results**: Fill out test-plan.md thoroughly.

**Report bugs**: Note all issues found during testing.

### 3. PR Commands

**Verify prerequisites**: Ensure all documents exist before creating PR.

**Review PR description**: Check that PR accurately describes changes.

**Wait for checks**: Let CI/CD complete before merging.

### 4. Documentation Commands

**Run after merges**: Keep documentation current after changes.

**Use specific scopes**: Target only affected documentation areas.

**Review changes**: Verify auto-generated docs are accurate.

### 5. Skill and Hook Commands

**Test thoroughly**: Test custom skills and hooks before relying on them.

**Document usage**: Add clear instructions in skill/hook files.

**Version control**: Commit custom skills and hooks to repository.

---

## Command Aliases

Some commands have shorter aliases:

| Full Command | Alias | Description |
|--------------|-------|-------------|
| `/start-feature` | `/sf` | Start feature analysis |
| `/start-develop` | `/sd` | Start development |
| `/test` | `/t` | Setup test environment |
| `/PR` | `/pr` | Create pull request |
| `/merge` | `/m` | Merge and cleanup |
| `/update-documentation` | `/doc` | Update docs |

**Example**:
```
/sf 42    # Same as /start-feature 42
/sd 42    # Same as /start-develop 42
/t 42     # Same as /test 42
```

---

## Troubleshooting Commands

### Command Not Found

**Symptom**: Slash command doesn't execute

**Solutions**:
- Verify command exists in `framework-assets/claude-commands/`
- Check command file has correct frontmatter
- Ensure project is in correct mode (SIMPLE vs DEVELOPMENT)
- Check Claude Code session is active

### Command Fails Silently

**Symptom**: Command runs but produces no output

**Solutions**:
- Check backend logs for errors
- Verify MCP server is running
- Check task status prerequisites
- Verify all required files exist

### Agent Delegation Fails

**Symptom**: Command starts but agent doesn't respond

**Solutions**:
- Verify agent file exists in `framework-assets/claude-agents/`
- Check agent has correct tools in frontmatter
- Verify agent has access to required context
- Check for agent execution errors in logs

---

## Custom Commands

### Creating Custom Commands

1. Create command file: `.claude/commands/my-command.md`
2. Add frontmatter:
```markdown
---
allowed-tools: [Bash, Read, Write]
argument-hint: [args]
description: My custom command description
---

# My Custom Command

Command implementation goes here...
```

3. Save file and reload Claude Code session
4. Command available as `/my-command`

### Command File Structure

```markdown
---
allowed-tools: [list of tools]
argument-hint: [argument hints]
description: Brief description
---

# Command Name

## What it does
Description of command functionality

## Prerequisites
What must be true before running

## Usage
How to use the command

## Example
Example command execution
```

---

## Related Documentation

- [Intelligent Workflow](../architecture/intelligent-workflow.md) - Complete workflow guide
- [Project Modes](../architecture/project-modes.md) - SIMPLE vs DEVELOPMENT modes
- [MCP Tools](../api/mcp-tools.md) - MCP tool reference
- [Specialized Agents](../../framework-assets/claude-agents/README.md) - Agent capabilities

---

**Last Updated**: 2025-11-21
**Command Version**: 1.0.0
**Total Commands**: 10 built-in + unlimited custom
