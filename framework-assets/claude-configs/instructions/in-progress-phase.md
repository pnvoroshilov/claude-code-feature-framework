# 🚀 In Progress Phase - Implementation Workflow

**Phase Status:** "In Progress"
**Use Cases:** UC-02 (Review and Select Development Path), UC-03 (Development)
**Trigger:** User presses "In Progress" button after Analysis approval

---

## 📋 Phase Overview

The "In Progress" phase is the **implementation stage** where code development happens based on approved requirements and technical design from the Analysis phase.

### Key Characteristics:
- ✅ Implementation of features/fixes according to `/Analyze` documentation
- ✅ Autonomous development coordination by Claude orchestrator
- ✅ Parallel development when bounded contexts allow
- ✅ Continuous DoD validation
- ✅ Automatic PR creation when implementation complete
- ⛔ NO test environment setup (happens only at Testing status)

---

## 🎯 UC-02: Review and Select Development Path

### Trigger
System starts terminal session with Claude Code and sends command `/start-develop`

### Orchestrator Responsibilities

#### 1. Review Analysis Artifacts
```bash
# Claude reviews /Analyze folder contents
Read worktrees/task-{id}/Analyze/Requirements/*.md
Read worktrees/task-{id}/Analyze/Design/*.md
```

**Extract:**
- User stories and use cases
- Technical requirements (what/where/why)
- Architecture decisions
- Definition of Done (DoD)
- Test cases (UI & Backend)

#### 2. Monitor PR Status
Check if previous PR (if exists) has:
- ❌ Testing errors → Address before proceeding
- ❌ Review comments → Address before proceeding
- ✅ Clean status → Proceed with development

#### 3. Decide Development Strategy

**Decision Factors:**
- **Single Context Task**: One domain (frontend OR backend)
  - Delegate to single specialist agent
  - Example: UI-only change → `frontend-developer`

- **Multi-Context Task**: Multiple domains (frontend AND backend)
  - Check if contexts are **bounded** (independent)
  - If bounded → Launch parallel sub-agents
  - If dependent → Sequential delegation

**Bounded Context Detection:**
```
BOUNDED (Parallel):
- Frontend: UI components in /frontend
- Backend: API endpoints in /backend
- No shared files
→ Develop in parallel

DEPENDENT (Sequential):
- Frontend needs new API endpoint
- Backend must be implemented first
→ Backend first, then Frontend
```

#### 4. Agent Selection
📖 **Reference:** [agent-selection-guide.md](agent-selection-guide.md)

**Implementation Agents:**
- `frontend-developer` - React/TypeScript/Material-UI
- `backend-architect` - FastAPI/Python/SQLAlchemy
- `python-api-expert` - FastAPI backend specialist
- `mobile-react-expert` - Mobile-first React development
- other language and framework agent experts (depends on requirements and techstack)

**Selection Rules:**
- ✅ Match task domain to agent expertise
- ✅ Check file extensions (.tsx → frontend, .py → backend)
- ✅ Technology stack alignment
- ❌ NEVER cross-assign (frontend task to backend agent)

#### 5. Launch Development Agents

**Single Agent Delegation:**
```bash
# For single-domain tasks
Task tool with subagent_type='frontend-developer'
Prompt: "Implement feature based on /Analyze/Requirements and /Analyze/Design docs.
        Worktree: worktrees/task-{id}
        Ensure DoD compliance."
```

**Parallel Agent Delegation:**
```bash
# For bounded multi-domain tasks
# Send SINGLE message with MULTIPLE Task tool calls

Task tool with subagent_type='backend-architect'
Prompt: "Implement backend API according to /Analyze/Design/technical-requirements.md
        Focus on: [backend specific requirements]
        Worktree: worktrees/task-{id}"

Task tool with subagent_type='frontend-developer'
Prompt: "Implement frontend UI according to /Analyze/Requirements/user-stories.md
        Focus on: [frontend specific requirements]
        Worktree: worktrees/task-{id}"
```

**⚠️ IMPORTANT:** Use single message with multiple tool calls for parallel execution!

#### 6. Monitor Agent Completion

**Wait for all agents to complete:**
- Track each agent's progress
- Collect completion reports
- Identify any blockers

**If Agent Reports Blocker:**
```bash
# Update task with blocker details
mcp__claudetask__append_stage_result --task_id={id} --status="In Progress" \
  --summary="Development blocked: {blocker_reason}" \
  --details="{detailed_blocker_info}"

# Delegate blocker resolution if needed
# Example: Missing requirements → requirements-analyst
```

#### 7. Validate DoD Completeness

**After all agents complete:**
```
FOR EACH DoD criterion:
  Check if implemented in code
  IF gap exists:
    - Identify responsible agent
    - Delegate gap closure
    - Wait for completion
```

**DoD Validation Checklist:**
- [ ] All functional requirements implemented
- [ ] All acceptance criteria met
- [ ] Code follows project standards
- [ ] No breaking changes (unless intended)
- [ ] Documentation updated (if required)

#### 8. Create Pull Request

**When DoD fully satisfied:**
```bash
# Commit all changes
git add .
git commit -m "Implement feature: {task_title}

{summary_of_changes}

Closes #{task_id}"

# Push to remote
git push origin task-{id}-{branch_name}

# Create PR via gh CLI
gh pr create --title "{task_title}" --body "$(cat <<'EOF'
## Summary
{bullet_points_of_changes}

## DoD Status
{checklist_of_completed_DoD_items}

## Related Task
Task #{task_id}

🤖 Generated with [Claude Code](https://claude.com/claude-code)
EOF
)"
```

#### 9. Update Task Status

**After PR created:**
```bash
# Save implementation results
mcp__claudetask__append_stage_result --task_id={id} --status="In Progress" \
  --summary="Implementation complete - PR created" \
  --details="PR: {pr_url}
All DoD criteria met:
{list_of_completed_DoD}

Agents involved:
{list_of_agents_and_their_work}

Ready for testing"

# Update to Testing status
mcp:update_status {id} "Testing"
```

### Postconditions (UC-02)
- ✅ PR created
- ✅ Code developed according to `/Analyze` specs
- ✅ All DoD criteria met
- ✅ Task transitioned to "Testing" status

---

## 🔧 UC-03: Development (Agent Execution)

### Agent Entry Point
Development agent receives:
- Task ID
- Worktree path: `worktrees/task-{id}`
- Instruction to read `/Analyze` documents
- DoD criteria to satisfy

### Agent Workflow

#### 1. Read Analysis Documents
```bash
# Requirements
Read worktrees/task-{id}/Analyze/Requirements/user-stories.md
Read worktrees/task-{id}/Analyze/Requirements/use-cases.md
Read worktrees/task-{id}/Analyze/Requirements/dod.md

# Design
Read worktrees/task-{id}/Analyze/Design/technical-requirements.md
Read worktrees/task-{id}/Analyze/Design/architecture-decisions.md
Read worktrees/task-{id}/Analyze/Design/conflict-analysis.md
```

#### 2. Use Restricted Context

**Context Boundaries:**
- ✅ Read `/Analyze` documents for **what to change**
- ✅ Use RAG tools to find **where to change**
- ✅ Study existing code patterns
- ❌ DO NOT create new architecture (already defined in /Analyze)
- ❌ DO NOT change requirements (already approved)

**RAG Tool Usage:**
```bash
# Find existing patterns
mcp__claudetask__search_codebase(
  query="existing implementation of similar feature",
  top_k=30
)

# Learn from past tasks
mcp__claudetask__find_similar_tasks(
  task_description="similar feature implementation",
  top_k=15
)
```

#### 3. Implement Code Changes

**Implementation Principles:**
- ✅ Follow technical requirements exactly
- ✅ Match existing code style and patterns
- ✅ Maintain architectural consistency
- ✅ Add appropriate error handling
- ✅ Include inline comments for complex logic
- ❌ NO over-engineering
- ❌ NO unnecessary abstractions

**File Operations:**
- Use `Read` to understand existing code
- Use `Edit` for targeted changes
- Use `Write` only for new files (if required by design)
- Use `MultiEdit` for batch changes across files

#### 4. Validate Against DoD

**Before completing:**
```
FOR EACH DoD criterion:
  Self-check implementation
  IF not satisfied:
    Continue implementation
  IF satisfied:
    Document completion
```

#### 5. Report Completion

**Success Report:**
```
Implementation Complete

Changes Made:
- {file_path}: {description_of_changes}
- {file_path}: {description_of_changes}

DoD Status:
✅ {criterion_1}
✅ {criterion_2}
✅ {criterion_3}

Ready for orchestrator review.
```

**Blocker Report (if applicable):**
```
Implementation Blocked

Blocker: {blocker_description}
Reason: {why_blocked}
Needed: {what_is_needed_to_unblock}

Recommendation: {suggested_resolution}
```

### Postconditions (UC-03)
- ✅ Code modifications prepared
- ✅ DoD criteria satisfied (or blockers reported)
- ✅ Changes committed to task branch

---

## 🔄 Orchestrator Continuous Monitoring

### When Checking "In Progress" Tasks

**Active Monitoring Pattern:**
```bash
# Get task queue
mcp:get_task_queue

# For each "In Progress" task:
FOR EACH task WHERE status = "In Progress":

  # Check for implementation completion signals

  1. Check worktree for recent commits:
     git log worktrees/task-{id} --since="last check" --oneline

  2. Look for completion keywords in commits:
     - "complete"
     - "finish"
     - "implement"
     - "add feature"
     - "fix bug"

  3. Check if implementation agents reported completion

  4. Listen for user signals that development is complete

  # IF COMPLETION DETECTED:
  IF completion_signal_found:

    # Validate DoD compliance
    review_dod_status()

    IF all_dod_satisfied:
      # Create PR
      create_pull_request()

      # Save stage result
      mcp__claudetask__append_stage_result --task_id={id} \
        --status="In Progress" \
        --summary="Implementation complete - PR created" \
        --details="{pr_details and dod_status}"

      # Transition to Testing
      mcp:update_status {id} "Testing"

    ELSE:
      # Identify gaps and delegate
      delegate_dod_gap_resolution()
```

### Implementation Completion Signals

**Commit-based Detection:**
- Commits with messages: "feat:", "fix:", "implement", "complete"
- Multiple commits within short timeframe
- Commit messages reference DoD criteria

**Agent-based Detection:**
- Agent completion reports
- Agent final messages indicating "ready for review"
- Agent DoD validation confirmations

**User-based Detection:**
- User message: "implementation complete"
- User message: "ready for testing"
- User explicitly moves task to Testing status

---

## 🚨 Critical Rules for In Progress Phase

### ⛔ RESTRICTIONS

**When task ENTERS "In Progress" status:**
1. ❌ **DO NOT** setup test environment
2. ❌ **DO NOT** start frontend/backend servers
3. ❌ **DO NOT** prepare test URLs
4. ❌ **DO NOT** find available ports
5. ✅ **ONLY** save stage result and report to user

**Why:** Test environment setup happens ONLY when task moves to "Testing" status!

### ✅ ALLOWED ACTIVITIES

**During "In Progress" status:**
1. ✅ Review `/Analyze` documentation
2. ✅ Select and delegate to implementation agents
3. ✅ Monitor agent progress
4. ✅ Validate DoD compliance
5. ✅ Create pull request when implementation complete
6. ✅ Auto-transition to "Testing" when PR created

### 📝 Stage Results - MANDATORY

**When transitioning TO "In Progress":**
```bash
mcp__claudetask__append_stage_result --task_id={id} --status="In Progress" \
  --summary="Development phase started" \
  --details="Worktree: worktrees/task-{id}
Branch: task-{id}-{branch_name}
Analysis artifacts reviewed from /Analyze
Ready for implementation"
```

**When transitioning FROM "In Progress" to "Testing":**
```bash
mcp__claudetask__append_stage_result --task_id={id} --status="In Progress" \
  --summary="Implementation complete - PR created" \
  --details="PR: {pr_url}
PR Title: {pr_title}

Changes Summary:
- {frontend_changes}
- {backend_changes}

DoD Status:
✅ {dod_criterion_1}
✅ {dod_criterion_2}
✅ {dod_criterion_3}

Agents Involved:
- {agent_1}: {their_work}
- {agent_2}: {their_work}

Ready for testing phase"
```

---

## 📊 Status Transitions

### Entering In Progress

**From:** Analysis
**Trigger:** User presses "In Progress" button
**Action:** `/start-develop` command sent to Claude

**Orchestrator Actions:**
1. ✅ Save stage result
2. ✅ Verify worktree exists
3. ✅ Read `/Analyze` documentation
4. ✅ Select development strategy
5. ✅ Delegate to implementation agents
6. ⛔ STOP - Do NOT setup test environment

### Exiting In Progress

**To:** Testing
**Trigger:** Implementation complete (PR created)
**Auto-transition:** YES

**Orchestrator Actions:**
1. ✅ Detect implementation completion
2. ✅ Validate DoD compliance
3. ✅ Create pull request
4. ✅ Save stage result with PR details
5. ✅ Update status to "Testing"
6. ➡️ Continue to Testing phase (see [testing-workflow.md](testing-workflow.md))

**To:** Blocked (if blocker encountered)
**Trigger:** Agent reports blocker or critical issue
**Auto-transition:** NO (requires orchestrator decision)

---

## 🎯 Success Criteria

**In Progress phase is successful when:**

✅ **Development Complete:**
- [ ] All code changes implemented per technical requirements
- [ ] Code follows project standards and patterns
- [ ] No breaking changes (unless approved in design)

✅ **DoD Satisfied:**
- [ ] All DoD criteria from requirements met
- [ ] Acceptance criteria validated
- [ ] No gaps in implementation

✅ **PR Created:**
- [ ] PR title follows convention
- [ ] PR description includes summary and DoD status
- [ ] PR linked to task
- [ ] PR pushed to remote branch

✅ **Documentation Updated:**
- [ ] Inline code comments added (where needed)
- [ ] Architecture docs updated (if changes made)
- [ ] API documentation updated (if endpoints changed)

✅ **Ready for Testing:**
- [ ] Stage result saved with implementation summary
- [ ] Task status updated to "Testing"
- [ ] Orchestrator proceeds to Testing phase

---

## 🔗 Related Documentation

- 📖 [Analysis Phase](analysis-phase.md) - Previous phase (creates /Analyze docs)
- 📖 [Status Transitions](status-transitions.md) - Status flow rules
- 📖 [Agent Selection Guide](agent-selection-guide.md) - Choosing implementation agents
- 📖 [Testing Workflow](testing-workflow.md) - Next phase (test environment setup)
- 📖 [RAG Usage](rag-usage.md) - How agents use RAG tools
- 📖 [MCP Commands](mcp-commands.md) - Command reference

---

## 📋 Quick Reference

**Orchestrator Entry Point:**
```
Command: /start-develop
Status: "In Progress"
Goal: Coordinate implementation, create PR, move to Testing
```

**Key Activities:**
1. Review `/Analyze` documentation
2. Select development strategy (single/parallel)
3. Delegate to implementation agents
4. Monitor agent progress
5. Validate DoD compliance
6. Create pull request
7. Transition to Testing

**Critical Reminders:**
- ⛔ NO test environment setup during In Progress
- ✅ Test environment setup ONLY at Testing status
- ✅ Always save stage results
- ✅ Auto-transition to Testing when PR created
- ✅ Use parallel agents for bounded contexts
- ✅ Validate DoD before completing phase

---

**Last Updated:** 2025-11-21
**Related Use Cases:** UC-02 (Review and Select Development Path), UC-03 (Development)
**Status:** Active - Primary implementation phase documentation
