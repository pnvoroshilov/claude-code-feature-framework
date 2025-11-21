# 🎯 Project Modes Configuration

## Two Project Modes

ClaudeTask supports two distinct project modes with different workflows:

### DEVELOPMENT Mode (Full Workflow)

**Task Workflow (7 Columns)**:
- **Backlog**: New tasks waiting to be analyzed
- **Analysis**: Understanding requirements and planning
- **In Progress**: Active development with Git worktrees
- **Testing**: Running tests and validation
- **Code Review**: Peer review of changes
- **PR**: Pull Request created and awaiting merge
- **Done**: Completed and merged

**What this means**:
- ✅ **Full Git workflow** - Branches, worktrees, PRs
- ✅ **Complete development lifecycle** - From analysis to deployment
- ✅ **Version control** - Proper branching and merge strategy
- ✅ **Quality gates** - Testing and code review required

**Your approach**:
1. Follow the complete task workflow through all statuses
2. Create worktrees for each task
3. Use proper branching strategy
4. Create PRs and wait for review
5. Ensure tests pass before moving forward

### SIMPLE Mode (Simplified Workflow)

**Task Workflow (3 Columns)**:
- **Backlog**: Tasks waiting to be started
- **In Progress**: Tasks currently being worked on
- **Done**: Completed tasks

**What this means**:
- ✅ **NO Git workflow** - Direct work, no branches, no PRs
- ✅ **NO complex statuses** - Just Backlog → In Progress → Done
- ✅ **Simplified task management** - Focus on getting work done
- ✅ **No worktrees, no version control complexity**

**🔴 CRITICAL: SIMPLE Mode Status Rules**

**⚠️ IN SIMPLE MODE, IGNORE ALL INSTRUCTIONS ABOUT:**
- ❌ Analysis status - Skip directly to In Progress
- ❌ Testing status - Do NOT auto-transition to Testing
- ❌ Code Review status - Does not exist in SIMPLE mode
- ❌ Pull Request status - Does not exist in SIMPLE mode
- ❌ Worktrees and git branches - Work directly in main branch
- ❌ Test environment setup - No automatic test server management

**Status Transitions (SIMPLE Mode ONLY)**:
```
Backlog → In Progress → Done
```

**That's it! No other statuses exist in SIMPLE mode.**

**Status Transition Rules**:

#### 1. Backlog → In Progress
- ✅ User starts working on a task
- ✅ Task moves to "In Progress"
- ✅ NO analysis phase
- ✅ NO worktree creation
- ✅ Work directly in main branch

#### 2. In Progress → Done
- ⚠️ **ONLY when user EXPLICITLY requests**: "mark task X as done"
- ❌ **NEVER auto-transition to Done**
- ❌ **NO Testing status** in between
- ❌ **NO Code Review** in between
- ❌ **NO automatic detection of completion**

#### 3. In Progress → Stay In Progress
- ✅ If implementation detected, task STAYS "In Progress"
- ✅ NO auto-transition to Testing or any other status
- ✅ Wait for user to manually mark as Done

## How to Determine Project Mode

Check the top of CLAUDE.md for the project mode indicator:
- `# 🎯 PROJECT MODE: DEVELOPMENT` → Use DEVELOPMENT mode rules
- `# 🎯 PROJECT MODE: SIMPLE` → Use SIMPLE mode rules

**IMPORTANT**: All workflow instructions are mode-specific. Always check the project mode before following any workflow instruction.
