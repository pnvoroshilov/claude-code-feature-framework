---
description: Start development phase after analysis complete (UC-02)
---

# Start Development Phase - UC-02 Workflow

When you run this command with a task ID, the system will execute the UC-02 workflow.

## MANDATORY: RAG-First Search Policy

**Before ANY development work, ALWAYS use RAG search to understand context:**

```bash
# 1. Search codebase for patterns related to this feature
mcp__claudetask__search_codebase --query="<feature keywords from requirements>" --top_k=20

# 2. Search documentation for architectural guidance
mcp__claudetask__search_documentation --query="<component/module area>" --top_k=10

# 3. Find similar tasks for implementation patterns
mcp__claudetask__find_similar_tasks --task_description="<task description>" --top_k=5
```

**Why RAG First?**
- Discover existing patterns to follow
- Find related code that must be updated
- Understand architectural constraints
- Learn from past implementations

---

## UC-02: Review and Select Development Path

**Step 1: Review Analysis Documents with RAG Context**

```bash
# First, gather RAG context
mcp__claudetask__search_codebase --query="<main feature area>" --top_k=20
mcp__claudetask__search_documentation --query="architecture design patterns" --top_k=10
```

Then review:
- Read `worktrees/task-{id}/Analyze/requirements.md` (from Requirements Analyst)
- Read `worktrees/task-{id}/Analyze/architecture.md` (from System Architect)
- Check for any PR testing or review errors

**Step 2: Intelligent Agent Selection**
- Determine which agent(s) will participate in development
- Decide if tasks can be split into bounded contexts
- Plan parallel development if applicable

**Step 3: Launch Development Agents with RAG Instructions**

Delegate to appropriate specialized agents, **always including RAG search instructions**:

**For Frontend Work (frontend-developer agent):**
```
Task(
  subagent_type="frontend-developer",
  prompt="""
  Implement frontend for Task #{task_id}:

  **MANDATORY: RAG Search First!**
  Before writing ANY code, run:
  - mcp__claudetask__search_codebase --query="React component <feature> UI" --top_k=20
  - mcp__claudetask__search_documentation --query="frontend patterns components" --top_k=10

  Requirements: [from Analyze/requirements.md]
  Architecture: [from Analyze/architecture.md]
  Worktree: worktrees/task-{id}/

  Use RAG results to:
  1. Follow existing component patterns
  2. Reuse existing utilities and hooks
  3. Match project styling conventions
  """
)
```

**For Backend Work (python-api-expert agent):**
```
Task(
  subagent_type="python-api-expert",
  prompt="""
  Implement backend API for Task #{task_id}:

  **MANDATORY: RAG Search First!**
  Before writing ANY code, run:
  - mcp__claudetask__search_codebase --query="FastAPI router endpoint <feature>" --top_k=20
  - mcp__claudetask__search_codebase --query="MongoDB repository service <domain>" --top_k=20
  - mcp__claudetask__search_documentation --query="API design database schema" --top_k=10

  Requirements: [from Analyze/requirements.md]
  Architecture: [from Analyze/architecture.md]
  Worktree: worktrees/task-{id}/

  Use RAG results to:
  1. Follow existing API patterns
  2. Match repository/service layer patterns
  3. Use consistent error handling
  """
)
```

**For Fullstack Features:**
- Both agents work in parallel in isolated worktree context
- Each agent must use RAG before implementation

**Step 4: Monitor and Validate**
- Track agent progress and completion
- Validate Definition of Done (DoD) completeness
- Call additional agents if gaps exist

**Step 5: Create Pull Request**
- Automatically create PR when development complete
- Transition task to "Testing" status

**Step 6: Proceed to Testing**
- After PR created, move to "Testing" status
- NOTE: In AUTO mode (manual_mode = false), orchestrator will automatically
  execute `/test {task_id}` command. In MANUAL mode, wait for user action.

---

## Usage

```bash
/start-develop [task-id]
```

## Example

```bash
/start-develop 42
```

This will:
1. Load task #42 details from ClaudeTask backend
2. **RAG Search** - Find related code and documentation
3. Review `worktrees/task-42/Analyze/` folder documents
4. Select appropriate development agent(s)
5. Delegate implementation work **with RAG instructions**
6. Monitor for completion
7. Create PR automatically
8. Transition to Testing status
9. In AUTO mode: Orchestrator executes `/test {task_id}` automatically

---

## Required Preconditions

- Task must be in "In Progress" status
- Analysis phase must be complete
- `worktrees/task-{id}/Analyze/requirements.md` must exist
- `worktrees/task-{id}/Analyze/architecture.md` must exist
- Worktree must be created and ready

---

## RAG Search Patterns for Development

```bash
# Backend patterns
mcp__claudetask__search_codebase --query="FastAPI endpoint router CRUD" --top_k=20
mcp__claudetask__search_codebase --query="MongoDB repository async CRUD" --top_k=20
mcp__claudetask__search_codebase --query="Pydantic schema validation model" --top_k=20

# Frontend patterns
mcp__claudetask__search_codebase --query="React useState useEffect hook" --top_k=20
mcp__claudetask__search_codebase --query="MUI Material-UI component styling" --top_k=20
mcp__claudetask__search_codebase --query="axios API call error handling" --top_k=20

# Cross-cutting concerns
mcp__claudetask__search_codebase --query="authentication authorization middleware" --top_k=20
mcp__claudetask__search_codebase --query="error handling exception logging" --top_k=20

# Documentation
mcp__claudetask__search_documentation --query="API design guidelines" --top_k=10
mcp__claudetask__search_documentation --query="database schema migrations" --top_k=10
```

---

## Status Flow

```
Analysis → In Progress → /start-develop → Implementation → Testing → Code Review → Done
```

---

## Notes

- This implements UC-02 from `Workflow/new_workflow_usecases.md`
- **RAG search is MANDATORY** before any development
- Supports parallel development for bounded contexts
- Automatically handles DoD validation
- Creates PR before moving to Testing (new workflow)
- Analysis folder is `Analyze/` (NOT "Analyse")
