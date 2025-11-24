# 📊 Analysis Phase - UC-01 Start Analysis

⚠️ **This applies to DEVELOPMENT MODE only. SIMPLE mode skips Analysis.**

## Preconditions

- Task in "Backlog" status
- Task description available
- User presses "Start Analyse" button OR uses `/start-feature` command

## Automatic Setup (Done by Backend)

When analysis starts:
- ✅ Backend creates worktree: `worktrees/task-{id}/`
- ✅ Backend creates folders: `worktrees/task-{id}/Analyze/task-{id}/Requirements/` and `worktrees/task-{id}/Analyze/task-{id}/Design/`
- ✅ Claude Code session starts with `/start-feature {task_id}` command

**You don't create these manually - backend handles it automatically.**

**⚠️ IMPORTANT:** Analysis documents are stored in `worktrees/task-{id}/Analyze/task-{id}/` folder. The nested `task-{id}` ensures documents are versioned in git and associated with the correct task.

## Your Role as Orchestrator

You coordinate the analysis phase by delegating to specialized agents. **Do NOT do analysis yourself.**

## Analysis Workflow

### 🔴 STEP 1: Get Task Information

```bash
mcp:get_task {task_id}
```

Extract:
- Task ID
- Task description
- Initial requirements
- Any attachments or context

### 🔴 STEP 2: Delegate to Requirements Analyst Agent

**Agent:** `requirements-analyst`

**What the agent will do** (you don't need to specify this):
- Ask additional questions if needed
- Analyze requirements using RAG and docs/
- Check other active tasks for conflicts
- Create comprehensive requirements documentation
- Save documents to `worktrees/task-{id}/Analyze/task-{id}/Requirements/`

**Your delegation:**

```
Task tool with requirements-analyst:
"Analyze requirements for this task and create requirement documents.

**STEP 1: Check Other Active Tasks**
Run: mcp:get_task_queue
Identify potential requirement conflicts.

**STEP 2: Analyze Project Documentation**
Review docs/architecture/, docs/api/, docs/components/, docs/claudetask/
Extract: existing patterns, business rules, API contracts, constraints.

**STEP 3: Analyze Requirements**
Task ID: {task_id}
Task description: [paste full description]
Initial requirements: [paste any requirements provided]

Output Location: worktrees/task-{id}/Analyze/task-{id}/Requirements/
Create files: requirements.md, acceptance-criteria.md, constraints.md

The agent knows how to format requirements documents - just provide the task context."
```

### 🔴 STEP 3: Wait for Requirements Analyst Completion

**Monitor agent progress:**
- Agent may ask user additional questions via `AskUserQuestion` tool
- Agent will check other active tasks automatically
- Agent will analyze docs/ folder systematically
- Wait for agent to complete and save documents
- Verify documents exist in `worktrees/task-{id}/Analyze/task-{id}/Requirements/`

### 🔴 STEP 4: Delegate to System Architect Agent

**Agent:** `system-architect`

**What the agent will do** (you don't need to specify this):
- Analyze requirements + DoD from Requirements Analyst
- **Analyze other active tasks** (to avoid conflicts)
- Study docs/ folder and codebase systematically
- Create Technical Requirements: what to change, where, and why
- Write test cases (UI & Backend)
- Save documentation in `worktrees/task-{id}/Analyze/task-{id}/Design/`

**Your delegation:**

```
Task tool with system-architect:
"Create technical design and architecture for this task.

**STEP 1: Check Other Active Tasks**
Run: mcp:get_task_queue
Identify technical conflicts with active tasks.

**STEP 2: Study Project Documentation**
Review docs/architecture/, docs/api/, docs/components/, docs/claudetask/
Extract: architecture patterns, API contracts, component interfaces, technical constraints.

**STEP 3: Create Technical Design**
Task ID: {task_id}
Requirements location: worktrees/task-{id}/Analyze/task-{id}/Requirements/

Output Location: worktrees/task-{id}/Analyze/task-{id}/Design/
Create files: technical-requirements.md, test-cases.md, architecture-decisions.md, conflict-analysis.md

The agent knows how to create design documents and test cases - just provide the task context."
```

### 🔴 STEP 5: Wait for System Architect Completion

**Monitor agent progress:**
- Agent will analyze other active tasks automatically
- Agent will study codebase and architecture
- Wait for agent to complete and save documents
- Verify documents exist in `worktrees/task-{id}/Analyze/task-{id}/Design/`

### 🔴 STEP 6: Notify User for Review

**Inform user that analysis is complete:**

```
"Analysis phase completed for Task #{task_id}:

✅ Requirements documented in: worktrees/task-{id}/Analyze/task-{id}/Requirements/
✅ Technical design created in: worktrees/task-{id}/Analyze/task-{id}/Design/

Please review the analysis documents. If everything is ok, press 'In Progress' button to proceed with implementation."
```

### 🔴 STEP 7: Save Analysis Stage Result

```bash
mcp__claudetask__append_stage_result \
  --task_id={id} \
  --status="Analysis" \
  --summary="Requirements and technical design completed" \
  --details="Requirements Analyst Agent: Completed requirements documentation
System Architect Agent: Completed technical design and test cases

Documents created:
- worktrees/task-{id}/Analyze/task-{id}/Requirements/
- worktrees/task-{id}/Analyze/task-{id}/Design/

Ready for user review and approval."
```

### 🔴 STEP 8: Wait for User Approval

**User reviews analysis documents:**
- User checks `worktrees/task-{id}/Analyze/task-{id}/Requirements/`
- User checks `worktrees/task-{id}/Analyze/task-{id}/Design/`
- If approved: User presses **"In Progress"** button
- If changes needed: User provides feedback and you restart analysis

### 🔴 STEP 9: Transition to In Progress

When user presses "In Progress" button:

```bash
mcp:update_status {id} "In Progress"
```

```bash
mcp__claudetask__append_stage_result \
  --task_id={id} \
  --status="In Progress" \
  --summary="Analysis approved, development phase started" \
  --details="User approved analysis documents.
Ready for implementation.
Worktree: worktrees/task-{id}/"
```

**Then STOP - do not setup test environment yet.**

See [status-transitions.md](status-transitions.md) for In Progress phase.

## Postconditions

After successful analysis:
- ✅ All analysis artifacts stored in `worktrees/task-{id}/Analyze/task-{id}/`
- ✅ Requirements documented in `worktrees/task-{id}/Analyze/task-{id}/Requirements/`
- ✅ Technical design documented in `worktrees/task-{id}/Analyze/task-{id}/Design/`
- ✅ Test cases defined by System Architect
- ✅ User approved the analysis
- ✅ Task status: "In Progress"

## Analysis Quality Checklist

Before transitioning to In Progress:

- [ ] Requirements documents exist in `worktrees/task-{id}/Analyze/task-{id}/Requirements/`
- [ ] Design documents exist in `worktrees/task-{id}/Analyze/task-{id}/Design/`
- [ ] Requirements Analyst Agent completed their work
- [ ] System Architect Agent completed their work
- [ ] Both agents analyzed other active tasks
- [ ] Both agents reviewed docs/ folder
- [ ] Test cases (UI & Backend) are defined
- [ ] User reviewed and approved the analysis
- [ ] Stage result saved with `append_stage_result`
- [ ] Status updated to "In Progress"

## Common Mistakes to Avoid

❌ **DON'T**:
- Do analysis yourself (always delegate to agents)
- Create requirements documents yourself (Requirements Analyst does it)
- Create design documents yourself (System Architect does it)
- Skip user review and approval
- Move to In Progress before user approval
- Setup test environment during Analysis (wait for Testing status)
- Forget to tell agents to analyze other active tasks and docs/

✅ **DO**:
- Delegate to `requirements-analyst` agent
- Delegate to `system-architect` agent
- Let agents ask user questions if needed
- Ensure agents check task queue and docs/
- Wait for user approval before transitioning
- Save stage results at key points
- Verify all documents are created before proceeding

## Agent Responsibilities Summary

**Requirements Analyst Agent:**
- Assesses task complexity (SIMPLE/MODERATE/COMPLEX)
- Checks other active tasks for conflicts
- Analyzes docs/ folder systematically
- Asks questions if needed
- Creates requirements documentation with RAG context
- Saves to `worktrees/task-{id}/Analyze/task-{id}/Requirements/`

**System Architect Agent:**
- Assesses task complexity (SIMPLE/MODERATE/COMPLEX)
- Analyzes requirements and DoD
- **Analyzes other active tasks**
- **Studies docs/ folder**
- Studies codebase with RAG
- Creates technical requirements
- Writes test cases (UI & Backend)
- Saves to `worktrees/task-{id}/Analyze/task-{id}/Design/`

**Your responsibility:** Orchestrate and coordinate, don't do their work.
