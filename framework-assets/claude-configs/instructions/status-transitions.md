# 📊 Status Management and Transitions

⚠️ **This file describes DEVELOPMENT MODE workflow only. For SIMPLE mode, see [project-modes.md](project-modes.md)**

## 🤖 AUTO MODE vs MANUAL MODE

**CRITICAL: Check project settings first:**
```bash
mcp__claudetask__get_project_settings
# Check manual_mode value
```

- **`manual_mode = true`** - Follow standard instructions below
- **`manual_mode = false`** (AUTO MODE) - See [AUTO MODE Section](#auto-mode-status-transitions) for automated command execution

## Status Flow with Agent Delegation (DEVELOPMENT MODE)

```
Backlog → Analysis → In Progress → Testing → Code Review → Pull Request → Done
```

## Detailed Status Transition Rules

### 🔴 After Analysis → ALWAYS In Progress

**MANDATORY**: After analysis agent completes → Update status to "In Progress"

```bash
# Analysis complete, transition to In Progress
mcp__claudetask__append_stage_result --task_id={id} --status="Analysis" \
  --summary="Analysis complete - requirements and architecture documented" \
  --details="Requirements: [summary]
Architecture: [summary]
Ready for implementation"

# Update status to In Progress
mcp:update_status {id} "In Progress"
```

- ❌ **NEVER** skip to Ready or other statuses
- ❌ **NEVER** stay in Analysis status after analysis is done

### 🚀 After Moving to In Progress → DO NOT SETUP TEST ENVIRONMENT

**CRITICAL: When task status changes to "In Progress":**

1. ✅ Verify worktree exists:
   - Check `worktrees/task-{id}` directory
   - Ensure git branch is created

2. ✅ Save status change:
```bash
mcp__claudetask__append_stage_result --task_id={id} --status="In Progress" \
  --summary="Development phase started" \
  --details="Worktree: worktrees/task-{id}
Ready for implementation"
```

3. ✅ Report to user:
```
Task #{id} is now In Progress
Worktree: worktrees/task-{id}
Ready for development
```

4. ⛔ **STOP - DO NOT PROCEED FURTHER**
   - ❌ DO NOT setup test servers
   - ❌ DO NOT start frontend/backend
   - ❌ DO NOT prepare test environment
   - ❌ NO delegation to implementation agents
   - ❌ NO coding or development
   - ✅ Wait for user's manual development

**⚠️ IMPORTANT**: Test environments are ONLY setup when task moves to TESTING status, NOT during In Progress

### 🔴 After Implementation → MANDATORY TESTING STATUS

**⚠️ CRITICAL REQUIREMENT: After ANY code implementation:**

- ✅ **MUST** transition to "Testing" status IMMEDIATELY
- ✅ **MANDATORY** sequence: In Progress → Implementation Complete → Testing
- ❌ **NEVER** skip Testing status
- ❌ **NEVER** go directly to Code Review without Testing
- ❌ **NEVER** mark as Done without Testing

**🚨 ORCHESTRATOR MONITORING FOR IMPLEMENTATION COMPLETION:**

```
WHEN CHECKING "IN PROGRESS" TASKS:
1. For each "In Progress" task:
   - Check worktree for recent commits
   - Look for commit messages indicating completion
   - Check if implementation agents have reported completion
   - Listen for user signals that development is complete

2. IF implementation detected:
   - IMMEDIATELY update to "Testing" status
   - Save stage result with implementation summary
   - Prepare test environment

3. Continue with other tasks
```

**Implementation Completion Detection Signals**:
- New commits in task worktree
- Agent completion reports
- Key phrases in commit messages: "complete", "finish", "implement", "add feature"
- User indication that development is finished

**Implementation Complete Checklist**:
1. Code has been written/modified
2. Commits detected in task worktree
3. **AUTOMATICALLY** update status to Testing
4. Save implementation results with append_stage_result
5. **🔴🔴🔴 CRITICAL MANDATORY STEP**: Save testing URLs using `mcp__claudetask__set_testing_urls`
6. Prepare test environment for user

### 🧪 Testing Status → Prepare Environment ONLY

**When task moves from "In Progress" to "Testing":**

See detailed instructions in [testing-workflow.md](testing-workflow.md)

**Key Points**:
- ✅ Setup test environment (find ports, start servers)
- ✅ **MANDATORY**: Save testing URLs with `mcp__claudetask__set_testing_urls`
- ✅ Save stage result with URLs
- ❌ DO NOT delegate to testing agents
- ❌ Wait for user manual testing

### After Testing → Code Review

**ONLY user can update status after manual testing**:
- ❌ **NEVER** automatically move from Testing to Code Review
- ✅ User decides when testing is complete
- ✅ Prepare environment and wait

### Code Review → Pull Request

**After code review complete**:
```bash
# Update to Pull Request status
mcp:update_status {id} "Pull Request"

# Create PR (see pr-merge-phase.md for details)
```

- ✅ After code review complete → Update to "Pull Request"
- ✅ **CREATE PR ONLY** (no merge, no testing)
- ❌ **DO NOT** merge to main
- ❌ **DO NOT** run tests

### 🔴🔴🔴 CODE REVIEW STATUS RESTRICTIONS

**⛔ IF TASK IS IN "CODE REVIEW" STATUS:**
- ❌ **NEVER** transition to "Done"
- ❌ **NEVER** delete worktree
- ❌ **NEVER** delete branch
- ❌ **NEVER** close the task
- ❌ **NEVER** clean up any resources
- ✅ **ONLY** allowed transition: Code Review → Pull Request (after review complete)
- ✅ **WAIT** for user's explicit instruction to proceed

### Pull Request Status → NO AUTO ACTIONS

**⚠️ FULL STOP - No automatic actions**:
- ✅ Wait for user to handle PR merge
- ❌ **DO NOT** attempt to merge or update
- ❌ **DO NOT** transition to Done
- ❌ **DO NOT** clean up resources

### 🧹 Task Completion → CLEANUP ALL RESOURCES

**⚠️ ONLY when user EXPLICITLY requests task completion (via /merge command)**:

See detailed instructions in [resource-cleanup.md](resource-cleanup.md)

**Quick Reference**:
1. ✅ USE: `mcp:stop_session {task_id}` (automated cleanup)
2. ✅ Terminates test servers, releases ports, clears URLs
3. ✅ Save cleanup results with append_stage_result
4. ✅ Report completion to user

## Status Update Rules

1. ✅ Update status ONLY after agent completion
2. ✅ Include agent results in status updates
3. ✅ **ALWAYS save stage results** using `mcp__claudetask__append_stage_result`
4. ✅ Move to next phase based on agent output
5. ✅ Handle any blockers reported by agents

## Stage Results - MANDATORY for Every Status Change

**Every status transition MUST be accompanied by `append_stage_result`**:

```bash
mcp__claudetask__append_stage_result \
  --task_id={id} \
  --status="<current_status>" \
  --summary="<brief summary of what was done>" \
  --details="<detailed information about the phase>"
```

**Examples**:

**Analysis Complete**:
```bash
mcp__claudetask__append_stage_result --task_id=23 --status="Analysis" \
  --summary="Business and technical analysis completed" \
  --details="Requirements documented in Analyse/requirements.md
Architecture designed in Analyse/architecture.md
Ready to proceed with implementation"
```

**Testing Environment Ready**:
```bash
mcp__claudetask__append_stage_result --task_id=23 --status="Testing" \
  --summary="Testing environment prepared with URLs saved" \
  --details="Backend: http://localhost:4500
Frontend: http://localhost:3500
✅ URLs SAVED to task database
Ready for manual testing"
```

**Code Review Complete**:
```bash
mcp__claudetask__append_stage_result --task_id=23 --status="Code Review" \
  --summary="Code review completed - approved" \
  --details="Review findings: Code quality good, best practices followed
Issues found: None
Ready for PR creation"
```

## 🤖 AUTO MODE Status Transitions

**When `manual_mode = false`, the following automated transitions occur:**

### Command Execution Mapping

| Status Change | Automatic Command | Use Case Reference |
|--------------|-------------------|-------------------|
| Analysis → In Progress | `/start-develop` | UC-02 |
| In Progress → Testing | `/test {task_id}` | UC-04 |
| Testing → Code Review | `/PR {task_id}` (if tests pass) | UC-05 |
| Testing → In Progress | `/start-develop` (if tests fail) | UC-04 |
| Code Review → Pull Request | (automatic after review) | UC-05 |
| Pull Request → Done | (automatic merge if enabled) | UC-05 |

### AUTO MODE Monitoring Loop

```python
# Orchestrator continuously monitors (every 30 seconds):
WHILE TRUE:
    for task in active_tasks:
        current_status = get_task_status(task.id)

        if status_changed(task.previous_status, current_status):
            # Execute appropriate command based on transition
            handle_auto_mode_transition(task.id, current_status)

            # Save stage result for transition
            append_stage_result(task.id, current_status, "AUTO MODE transition")

            # Update tracking
            task.previous_status = current_status
```

### Testing Configuration Check

**CRITICAL for UC-04**: Check `manual_testing_mode` setting:

```bash
mcp__claudetask__get_project_settings
# Check both manual_mode and manual_testing_mode
```

- **`manual_testing_mode = false`** → Automated testing with web-tester agent
- **`manual_testing_mode = true`** → Manual testing with environment setup

### Preventing Duplicate Commands

**Track executed commands per task:**

```python
executed_commands[task_id] = set()

def execute_if_not_done(task_id, command):
    if command not in executed_commands[task_id]:
        SlashCommand(command)
        executed_commands[task_id].add(command)
        return True
    return False
```

### Handling Manual UI Updates

**If user changes status manually, orchestrator must catch up:**

```bash
# Detect manual transition
if status == "Code Review" and "/PR" not in executed_commands[task_id]:
    # Execute missed command
    SlashCommand(f"/PR {task_id}")
    append_stage_result("Executed missed /PR command after manual transition")
```

### Complete AUTO MODE Flow Example

```
1. Task in Backlog
   ↓
2. User/System triggers Analysis (UC-01)
   ↓
3. Analysis complete → Status: "In Progress"
   ↓
4. 🤖 AUTO: Execute /start-develop (UC-02)
   ↓
5. Development complete → Status: "Testing"
   ↓
6. 🤖 AUTO: Execute /test {id} (UC-04)
   ↓
7a. Tests pass → Status: "Code Review"
    ↓
    🤖 AUTO: Execute /PR {id} (UC-05)
    ↓
    Review passes → Status: "Pull Request"
    ↓
    🤖 AUTO: Merge if enabled → Status: "Done"

7b. Tests fail → Status: "In Progress"
    ↓
    🤖 AUTO: Execute /start-develop
    ↓
    (Loop back to step 4)
```

### AUTO MODE Success Criteria

✅ All transitions trigger commands within 1 minute
✅ No duplicate commands executed
✅ Stage results document every transition
✅ Manual updates detected and handled
✅ Commands match Use Case specifications

### Related Documentation

- [auto-mode-monitoring.md](auto-mode-monitoring.md) - Detailed AUTO MODE instructions
- [test-command-auto-mode.md](test-command-auto-mode.md) - Testing automation
- [Workflow/new_workflow_usecases.md](../../../Workflow/new_workflow_usecases.md) - Complete UC specifications
