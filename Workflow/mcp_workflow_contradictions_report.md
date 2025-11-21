# MCP Tools vs New Workflow - Contradictions Analysis Report

**Analysis Date**: 2025-11-21
**Analyzed Files**:
- `Workflow/new_workflow_usecases.md` (New Use Case Model)
- `claudetask/mcp_server/claudetask_mcp_bridge.py` (MCP Tool Implementations)
- `.claudetask/instructions/*.md` (Current Instructions)
- `CLAUDE.md` (Main Orchestrator Configuration)

---

## 🔴 CRITICAL CONTRADICTIONS

### 1. **UC-01 Analysis Phase: Wrong Agent Delegation Instructions**

**Use Case Requirement (UC-01, Steps 4-7)**:
```
4. Claude Code gets Task description + initial requirements
   and sends it to Requirements Writer Agent
5. Requirements Writer Agent:
   - Asks additional questions if needed
   - Rewrites requirements in format: User Story + Use Cases
   - Adds DoD
   - Saves documents to /Analyze/Requirements
6. Claude code invokes System Architect Agent
7. System Architect Agent:
   - Analyzes requirements + DoD
   - Analyze other active tasks
   - Studies code base, documentation, architecture
   - Creates Technical Requirements
   - Writes test cases (UI & Backend)
   - Saves documentation in /Analyze/Design
```

**Current MCP Implementation** (`_get_next_steps_for_status`, lines 896-970):
```python
elif status == "Analysis":
    return """📍 NEXT STEPS (Status: Analysis):
⚠️ MANDATORY DUAL DELEGATION - ALWAYS DELEGATE TO BOTH:

1. FIRST delegate to Business Analyst:
   mcp:delegate_to_agent <task_id> business-analyst "Analyze business requirements"

2. THEN delegate to Systems Analyst:
   mcp:delegate_to_agent <task_id> systems-analyst "Analyze technical requirements"
```

**Instruction File** (`.claudetask/instructions/analysis-phase.md`, lines 46-118):
```markdown
### 🔴 STEP 2: Delegate to Business Analyst
Task tool with business-analyst:
"Analyze business requirements and user needs for this task."

### 🔴 STEP 4: Delegate to Systems Analyst
Task tool with systems-analyst:
"Analyze technical requirements and system design for this task."
```

**❌ CONTRADICTION**:
- **Use Case**: Requires `Requirements Writer Agent` and `System Architect Agent`
- **MCP Implementation**: Uses `business-analyst` and `systems-analyst`
- **Agent Mapping Mismatch**: These are different agents with different capabilities

**✅ EXPECTED BEHAVIOR**:
- Should delegate to `requirements-analyst` (or `requirements-writer`) and `system-architect`
- Agent selection should match the use case terminology
- Agent capabilities should align with UC-01 requirements

---

### 2. **UC-02: Missing "/start-develop" Command Implementation**

**Use Case Requirement (UC-02, Step 1)**:
```
1. System starts terminal session with Claude Code
   and sends command "/start-develop" to Claude
2. Claude reviews /Analyze folder and monitors whether PR has testing or review errors
3. Claude decides:
   - Which agent(s) will participate in development
   - Whether tasks can be split into bounded contexts to be developed in parallel
```

**Current Implementation**:
- ❌ No `/start-develop` command exists in slash commands
- ❌ No automatic review of `/Analyze` folder on development start
- ❌ No automatic decision logic for agent selection
- ❌ No parallel development support in workflow

**Available Commands** (from project structure):
- `/start-feature [task-id]` - Starts analysis phase
- `/test` - Testing command
- `/PR` - Code review command
- `/merge [task-id]` - Complete and merge task

**✅ EXPECTED BEHAVIOR**:
- Add `/start-develop [task-id]` command
- Implement automatic `/Analyze` folder review
- Add agent selection logic based on task analysis
- Support parallel development for bounded contexts

---

### 3. **UC-02: Wrong PR Creation Sequence**

**Use Case Requirement (UC-02, Steps 6-7)**:
```
6. Claude creates Pull Request
7. Claude calls MCP ClaudeTask to change Task status to "Testing"
```

**Current MCP Implementation** (`_get_next_steps_for_status`, lines 937-950):
```python
elif status == "In Progress":
    return """📍 NEXT STEPS (Status: In Progress):
1. Monitor development progress
2. When complete, move to: mcp:update_status <task_id> "Testing"
3. Or if blocked: mcp:update_status <task_id> "Blocked" """

elif status == "Code Review":
    return """📍 NEXT STEPS (Status: Code Review):
1. Complete code review with appropriate agent
2. After review complete → Update to Pull Request: mcp:update_status <task_id> "PR"
3. Then create PR ONLY (no merge): mcp:complete_task <task_id> true
⚠️ DO NOT merge to main, DO NOT run tests"""
```

**Current Instruction** (`.claudetask/instructions/status-transitions.md`, lines 127-140):
```markdown
### Code Review → Pull Request

**After code review complete**:
# Update to Pull Request status
mcp:update_status {id} "Pull Request"

# Create PR (see pr-merge-phase.md for details)

- ✅ After code review complete → Update to "Pull Request"
- ✅ **CREATE PR ONLY** (no merge, no testing)
```

**❌ CONTRADICTION**:
- **Use Case**: PR created AFTER development, BEFORE testing
- **Current Flow**: `In Progress → Testing → Code Review → PR → Done`
- **Sequence Mismatch**: Testing happens before PR creation, not after

**✅ EXPECTED BEHAVIOR (per UC-02)**:
```
In Progress → Development Complete → Create PR → Testing → Code Review → Done
```

---

### 4. **UC-04 Testing: Wrong Agent Usage**

**Use Case Requirement (UC-04, Variant A - Automated Testing)**:
```
2. Claude gets all information about the Task and context, checks
3. Claude Determine which tests must run (UI, backend)
4. Claude Invokes subagents to execute tests automatically
5. Testing agent (web or backend):
   - Get /Analyze docs and analyze them
   - Check test plan
   - check DoD
   - Write tests in /Tests folder
   - run test on new environment
11. Create report in /Tests/Report
```

**Current Implementation** (`_get_next_steps_for_status`, lines 944-950):
```python
elif status == "Testing":
    return """📍 NEXT STEPS (Status: Testing):
🔴 FULL STOP - MANUAL TESTING ONLY
1. Prepare test environment (ensure app is running)
2. Provide URLs/endpoints for user to test manually
3. Document what needs to be tested
4. ⚠️ NO AUTO PROGRESSION - Wait for user
5. ONLY user can update status after manual testing
Note: NEVER automatically move to Code Review"""
```

**Instruction File** (`.claudetask/instructions/testing-workflow.md`):
```markdown
### 🔴 MANDATORY: Manual Testing Only
- ✅ Setup test environment (find ports, start servers)
- ✅ Save testing URLs with mcp__claudetask__set_testing_urls
- ❌ DO NOT delegate to testing agents
- ❌ Wait for user manual testing
```

**❌ CONTRADICTION**:
- **Use Case Variant A**: Requires AUTOMATED testing with testing agents
- **Current Implementation**: ONLY manual testing, explicitly forbids testing agents
- **Missing Feature**: No support for automated test execution

**✅ EXPECTED BEHAVIOR**:
- Support BOTH manual (Variant B) and automated (Variant A) testing
- Add project setting: `manual_testing_mode` (true/false)
- Implement automated testing flow with testing agents for Variant A

---

### 5. **UC-05 Code Review: Missing Auto-Merge Capability**

**Use Case Requirement (UC-05, Variant A - Auto Review Mode)**:
```
6. Claude checks for Manual mode and then (if disabled) calls "PR-merge-agent"
7. "PR-merge-agent" Subagent:
   - Auto-merge PR into origin main
   - Auto-resolve merge conflicts using merge strategy
8. Claude move task to "Done" status
```

**Current Implementation** (`_get_next_steps_for_status`, lines 953-960):
```python
elif status == "PR":
    return """📍 NEXT STEPS (Status: Pull Request):
🔴 FULL STOP - NO AUTO ACTIONS
1. PR has been created (not merged)
2. Awaiting user to handle merge
3. NO automatic actions allowed
4. User will manually merge and update status
⚠️ DO NOT attempt any automatic actions"""
```

**Critical Restrictions** (`.claudetask/instructions/critical-restrictions.md`):
```markdown
⛔ NEVER mark tasks as "Done" without explicit user request
⛔ NEVER transition from "Code Review" to "Done"
```

**❌ CONTRADICTION**:
- **Use Case Variant A**: Requires AUTO-MERGE when manual mode is disabled
- **Current Implementation**: ALWAYS manual merge, NO auto actions
- **Missing Agent**: No `PR-merge-agent` implementation
- **Missing Logic**: No manual mode detection

**✅ EXPECTED BEHAVIOR**:
- Add project setting: `manual_review_mode` (true/false)
- Implement `PR-merge-agent` for automated merges
- Support merge conflict resolution strategies
- Auto-transition to Done when manual mode is OFF

---

### 6. **UC-01: Wrong Session Start Command**

**Use Case Requirement (UC-01, Step 2)**:
```
2. System starts terminal session with Claude code
   and sends command /start-feature with task id
```

**Available Command**:
```bash
/start-feature [task-id]: Start working on a task from the ClaudeTask board.
Gets task status and follows MCP instructions.
```

**✅ CORRECT**: This is actually implemented correctly

**However**, missing in use case description:
- No mention of worktree initialization in UC-01 preconditions
- Backend auto-creates worktree, but UC-01 doesn't specify this

---

### 7. **UC-04 Testing: Wrong Command Name**

**Use Case Requirement (UC-04, Variant A, Step 1)**:
```
1. System starts terminal session with Claude Code
   and sends command "/test" to Claude
```

**Available Commands**:
- ✅ `/test` command exists
- ❌ But current implementation doesn't match UC-04 requirements

**Current `/test` Behavior** (needs verification):
- Should trigger automated testing agents (per UC-04 Variant A)
- Current implementation forces manual testing only

---

## ⚠️ MODERATE CONTRADICTIONS

### 8. **Analysis Folder Naming Inconsistency**

**Use Case Documents**:
- UC-01 uses `/Analyze/Requirements` and `/Analyze/Design`

**Current Implementation**:
- Uses `worktrees/task-{id}/Analyse/` (British spelling)
- Saves to `requirements.md` and `architecture.md`

**❌ MINOR INCONSISTENCY**:
- Folder name: `Analyze` (US) vs `Analyse` (UK)
- Document location: UC uses `/Analyze/Design` vs current uses `/Analyse/architecture.md`

---

### 9. **UC-03: Wrong Development Agent Names**

**Use Case Requirement (UC-03, Actor)**:
```
Actors: Development Agents
```

**Current Agent Mappings** (`claudetask_mcp_bridge.py`, lines 63-185):
```python
agent_mappings = {
    "Feature": {
        "Analysis": "business-analyst",
        "Ready": "requirements-analyst",
        "In Progress": {
            "frontend": "frontend-developer",
            "backend": "python-api-expert",
            "fullstack": ["frontend-developer", "python-api-expert"]
        }
    }
}
```

**✅ PARTIAL MATCH**:
- Agents exist: `frontend-developer`, `python-api-expert`
- Use case is generic ("Development Agents"), so this is acceptable

---

### 10. **Missing Project Settings for Mode Detection**

**Use Cases Require**:
- Manual mode detection (UC-04 Variant A vs B)
- Manual review mode (UC-05 Variant A vs B)

**Current Project Settings** (`_get_project_settings`, lines 3034-3075):
```python
async def _get_project_settings(self, project_id: int):
    # Returns: project_mode, worktree_enabled, etc.
```

**❌ MISSING SETTINGS**:
- `manual_testing_mode` (true/false) - for UC-04
- `manual_review_mode` (true/false) - for UC-05
- No conditional logic based on these settings

---

## 📊 SUMMARY OF CONTRADICTIONS

| # | Issue | Severity | Use Case | Current Behavior | Required Action |
|---|-------|----------|----------|------------------|-----------------|
| 1 | Wrong agent names in Analysis | 🔴 CRITICAL | UC-01 | `business-analyst`, `systems-analyst` | Use `requirements-analyst`, `system-architect` |
| 2 | Missing `/start-develop` command | 🔴 CRITICAL | UC-02 | Not implemented | Create `/start-develop` slash command |
| 3 | Wrong PR creation sequence | 🔴 CRITICAL | UC-02 | Testing before PR | Change to: PR → Testing → Review |
| 4 | No automated testing support | 🔴 CRITICAL | UC-04 Variant A | Only manual testing | Add automated testing agents |
| 5 | No auto-merge capability | 🔴 CRITICAL | UC-05 Variant A | Always manual merge | Implement `PR-merge-agent` |
| 6 | Missing manual mode settings | ⚠️ MODERATE | UC-04, UC-05 | No mode detection | Add `manual_testing_mode`, `manual_review_mode` |
| 7 | Folder naming inconsistency | ⚠️ MINOR | UC-01 | `Analyse` vs `Analyze` | Standardize spelling |

---

## 🔧 RECOMMENDED FIXES

### Priority 1: Critical Agent and Flow Fixes

#### Fix 1.1: Update Agent Names in MCP Bridge
**File**: `claudetask/mcp_server/claudetask_mcp_bridge.py`

**Lines 63-185**: Update agent_mappings
```python
agent_mappings = {
    "Feature": {
        "Analysis": "requirements-analyst",  # Was: business-analyst
        "Ready": "system-architect",          # Was: systems-analyst
        # ... rest unchanged
    }
}
```

**Lines 896-970**: Update `_get_next_steps_for_status`
```python
elif status == "Analysis":
    return """📍 NEXT STEPS (Status: Analysis):
⚠️ MANDATORY DUAL DELEGATION - ALWAYS DELEGATE TO BOTH:

1. FIRST delegate to Requirements Analyst:
   mcp:delegate_to_agent <task_id> requirements-analyst "Analyze requirements"

2. THEN delegate to System Architect:
   mcp:delegate_to_agent <task_id> system-architect "Design architecture"
```

#### Fix 1.2: Update Status Flow (PR Before Testing)
**File**: `claudetask/mcp_server/claudetask_mcp_bridge.py`

**Lines 187-203**: Update status_flow
```python
# OLD:
status_flow = ["Backlog", "Analysis", "Ready", "In Progress", "Testing", "Code Review", "PR", "Done"]

# NEW (per UC-02):
status_flow = ["Backlog", "Analysis", "In Progress", "PR", "Testing", "Code Review", "Done"]
```

**Update all related methods**:
- `_get_next_steps_for_status`
- `_get_status_progression_instructions`
- `_update_status`

#### Fix 1.3: Add Manual Mode Settings
**File**: `claudetask/backend/app/models/project.py`

Add new fields:
```python
class Project(Base):
    # ... existing fields
    manual_testing_mode: bool = Column(Boolean, default=True)
    manual_review_mode: bool = Column(Boolean, default=True)
```

**Migration**: Create alembic migration for new fields

#### Fix 1.4: Implement Automated Testing (Variant A)
**File**: `claudetask/mcp_server/claudetask_mcp_bridge.py`

Update `_get_next_steps_for_status` testing section:
```python
elif status == "Testing":
    # Get project settings
    project_settings = await self._get_project_settings(self.project_id)

    if project_settings.get("manual_testing_mode", True):
        return """📍 MANUAL TESTING MODE:
        1. Prepare test environment
        2. Provide URLs to user
        3. Wait for user testing"""
    else:
        return """📍 AUTOMATED TESTING MODE:
        1. Invoke web-tester agent for UI tests
        2. Invoke backend testing agent for API tests
        3. Generate test report in /Tests/Report
        4. Auto-progress to Code Review if all pass"""
```

#### Fix 1.5: Implement PR-Merge Agent (Variant A)
**File**: `claudetask/backend/app/services/pr_merge_service.py` (NEW)

Create new service:
```python
class PRMergeService:
    async def auto_merge_pr(self, task_id: int):
        """Auto-merge PR using GitHub API"""
        # 1. Check for merge conflicts
        # 2. Resolve using merge strategy
        # 3. Merge to main
        # 4. Update task status to Done
```

Add to MCP bridge:
```python
elif status == "Code Review":
    project_settings = await self._get_project_settings(self.project_id)

    if not project_settings.get("manual_review_mode", True):
        # Automated mode
        return """📍 AUTO-MERGE MODE:
        1. Complete code review
        2. Auto-merge PR to main
        3. Auto-transition to Done"""
```

---

### Priority 2: Add Missing Commands

#### Fix 2.1: Create `/start-develop` Slash Command
**File**: `.claude/commands/start-develop.md` (NEW)

```markdown
---
description: Start development phase after analysis complete
---

# Start Development Phase

When you run this command with a task ID, the system will:
1. Review /Analyze folder documents
2. Determine required agents (frontend, backend, fullstack)
3. Check for bounded context separation
4. Start parallel development if applicable
5. Delegate to appropriate development agents

Usage: /start-develop [task-id]
```

**Backend Implementation**: Add to slash command processor

---

### Priority 3: Update Instructions

#### Fix 3.1: Update Analysis Phase Instructions
**File**: `.claudetask/instructions/analysis-phase.md`

**Lines 46-118**: Update agent names
```markdown
### 🔴 STEP 2: Delegate to Requirements Analyst
Task tool with requirements-analyst:
"Analyze business requirements and create user stories"

### 🔴 STEP 4: Delegate to System Architect
Task tool with system-architect:
"Design system architecture and technical approach"
```

#### Fix 3.2: Update Status Transitions
**File**: `.claudetask/instructions/status-transitions.md`

**Lines 7-9**: Update status flow
```markdown
## Status Flow with Agent Delegation (DEVELOPMENT MODE)

Backlog → Analysis → In Progress → Pull Request → Testing → Code Review → Done
```

Update all sections to reflect new flow.

#### Fix 3.3: Add Testing Mode Instructions
**File**: `.claudetask/instructions/testing-workflow.md`

Add section for automated testing:
```markdown
## Testing Mode Detection

### Manual Mode (Default)
[Current instructions]

### Automated Mode (When manual_testing_mode = false)
1. Invoke web-tester agent for UI testing
2. Invoke backend testing agent for API testing
3. Generate test reports
4. Auto-progress based on results
```

---

### Priority 4: Standardization

#### Fix 4.1: Folder Naming
**Decision needed**: Use `Analyze` (US) or `Analyse` (UK) consistently

**Recommendation**: Use `Analyze` (US) to match use case documentation

**Files to update**:
- Backend worktree creation logic
- All instruction files
- Documentation

---

## 🎯 VALIDATION CHECKLIST

After implementing fixes, verify:

- [ ] UC-01: Analysis delegates to correct agents (`requirements-analyst`, `system-architect`)
- [ ] UC-02: `/start-develop` command exists and works
- [ ] UC-02: Status flow is `In Progress → PR → Testing → Code Review → Done`
- [ ] UC-04 Variant A: Automated testing works when `manual_testing_mode = false`
- [ ] UC-04 Variant B: Manual testing works when `manual_testing_mode = true`
- [ ] UC-05 Variant A: Auto-merge works when `manual_review_mode = false`
- [ ] UC-05 Variant B: Manual merge works when `manual_review_mode = true`
- [ ] All instruction files updated with correct flow and agents
- [ ] MCP commands reflect new workflow
- [ ] Project settings include mode flags

---

## 📝 NOTES

1. **Breaking Changes**: Changing status flow will require database migration and existing workflow updates
2. **Agent Verification**: Ensure `requirements-analyst` and `system-architect` agents exist and are configured
3. **Testing**: All changes should be tested in development environment before production
4. **Documentation**: Update all user-facing documentation to reflect new workflow
5. **Backward Compatibility**: Consider migration path for projects using old workflow

---

**Report Generated**: 2025-11-21
**Analysis Tool**: Claude Code with Serena MCP symbolic analysis
**Recommendation**: Implement Priority 1 fixes immediately to align with use case model
