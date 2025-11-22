---
description: Start development phase after analysis complete (UC-02)
---

# Start Development Phase - UC-02 Workflow

When you run this command with a task ID, the system will execute the UC-02 workflow:

## UC-02: Review and Select Development Path

**Step 1: Review Analysis Documents**
- Read `/Analyze/requirements.md` (from Requirements Analyst)
- Read `/Analyze/architecture.md` (from System Architect)
- Check for any PR testing or review errors

**Step 2: Intelligent Agent Selection**
- Determine which agent(s) will participate in development
- Decide if tasks can be split into bounded contexts
- Plan parallel development if applicable

**Step 3: Launch Development Agents**
- Delegate to appropriate specialized agents:
  - `frontend-developer` for UI/frontend work
  - `python-api-expert` for backend API work
  - Both agents in parallel for fullstack features
- Each agent works in isolated worktree context

**Step 4: Monitor and Validate**
- Track agent progress and completion
- Validate Definition of Done (DoD) completeness
- Call additional agents if gaps exist

**Step 5: Create Pull Request**
- Automatically create PR when development complete
- Transition task to "PR" status

**Step 6: Proceed to Testing**
- After PR created, move to "Testing" status
- NOTE: In AUTO mode (manual_mode = false), orchestrator will automatically
  execute `/test {task_id}` command. In MANUAL mode, wait for user action.

## Usage

```bash
/start-develop [task-id]
```

## Example

```bash
/start-develop 42
```

This will:
1. ✅ Load task #42 details from ClaudeTask backend
2. ✅ Review `/Analyze` folder documents
3. ✅ Select appropriate development agent(s)
4. ✅ Delegate implementation work
5. ✅ Monitor for completion
6. ✅ Create PR automatically
7. ✅ Transition to Testing status
8. ✅ In AUTO mode: Orchestrator executes `/test {task_id}` automatically

## Required Preconditions

- Task must be in "In Progress" status
- Analysis phase must be complete
- `/Analyze/requirements.md` must exist
- `/Analyze/architecture.md` must exist
- Worktree must be created and ready

## Status Flow

```
Analysis → In Progress → /start-develop → Implementation → PR → Testing → Code Review → Done
```

## Notes

- This implements UC-02 from `Workflow/new_workflow_usecases.md`
- Supports parallel development for bounded contexts
- Automatically handles DoD validation
- Creates PR before moving to Testing (new workflow)
