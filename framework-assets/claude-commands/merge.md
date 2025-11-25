---
allowed-tools: [Bash, Read, Write, Edit, Glob, Grep, Task, Skill]
argument-hint: [task-id]
description: Complete a task by merging PR, cleaning worktree, and stopping session
---

# /merge Command - Complete Task and Merge PR

Complete Task {{TASK_ID}} by merging its branch to main and cleaning up.

## EXECUTION: Delegate to pr-merge-agent with merge-skill

**⚠️ IMPORTANT: This command delegates work to a specialized agent with merge expertise!**

### Step 1: Get Task Details
```bash
mcp__claudetask__get_task --task_id={{TASK_ID}}
```

Extract:
- `git_branch` - branch name to merge
- `worktree_path` - path to cleanup (if exists)
- `project_id` - for project path lookup

### Step 2: Delegate to PR Merge Agent

Use the Task tool to spawn `pr-merge-agent`:

```
Task(
  subagent_type="pr-merge-agent",
  prompt="""
  Complete merge for Task #{{TASK_ID}}:

  **Branch to merge:** <branch_name>
  **Project path:** <project_path>
  **Worktree path:** <worktree_path or "none">

  ## FIRST: Load merge-skill for expert guidance

  **⚠️ MANDATORY: Use Skill tool to load merge-skill BEFORE any git operations!**

  ```
  Skill("merge-skill")
  ```

  The merge-skill provides:
  - Merge strategies (fast-forward, 3-way, squash)
  - Conflict resolution techniques
  - Recovery operations if something goes wrong
  - Best practices for safe merging

  ## Then execute tasks (in order):

  1. **Pre-merge validation:**
     - cd to project path
     - git fetch origin
     - Check branch exists: git branch --list <branch_name>
     - Check for conflicts: git diff main...<branch_name>

  2. **Execute merge (following merge-skill best practices):**
     - git checkout main
     - git pull origin main
     - git merge <branch_name> --no-ff -m "Merge task #{{TASK_ID}}: <branch_name>"

  3. **Handle conflicts (if any):**
     - Use merge-skill conflict resolution techniques
     - Document resolved conflicts in commit message
     - If unresolvable, abort and report

  4. **Push to remote (CRITICAL!):**
     - git push origin main
     - Verify: git status should show "up to date with origin/main"
     - If push fails, retry up to 3 times

  5. **Cleanup:**
     - Delete local branch: git branch -d <branch_name>
     - Delete remote branch: git push origin --delete <branch_name>
     - Remove worktree if exists: git worktree remove <worktree_path> --force
     - Prune worktrees: git worktree prune

  6. **Report results:**
     - Merge commit hash
     - Push status (success/failure)
     - Conflicts resolved (if any)
     - Cleanup status
  """
)
```

### Step 3: Update Task Status (after agent completes successfully)

```bash
# Save stage result
mcp__claudetask__append_stage_result --task_id={{TASK_ID}} --status="Done" \
  --summary="Merged to main and pushed to remote" \
  --details="Branch merged, pushed, and cleaned up by pr-merge-agent with merge-skill"

# Update status to Done
mcp__claudetask__update_status --task_id={{TASK_ID}} --status="Done" \
  --comment="PR merged, branch deleted, worktree cleaned"

# Stop session and cleanup resources
mcp__claudetask__stop_session --task_id={{TASK_ID}}
```

---

## Important Notes:

⚠️ **Mode-Dependent Behavior**:

**AUTO Mode (manual_mode = false):**
- This command is executed AUTOMATICALLY after code review passes
- NO user action required - orchestrator triggers via `/PR`

**Manual Mode (manual_mode = true):**
- User explicitly triggers this command after manual review

---

## merge-skill Capabilities

The pr-merge-agent uses merge-skill which provides:

| Capability | Description |
|------------|-------------|
| **Merge Strategies** | Fast-forward, 3-way, squash, rebase |
| **Conflict Resolution** | Manual and tool-assisted techniques |
| **Complex Scenarios** | Renamed files, binary conflicts, refactoring |
| **Recovery** | Abort, revert, reflog recovery |
| **Best Practices** | Team workflows, commit conventions |

---

## Error Handling (agent should handle using merge-skill):

### Merge Conflicts
- Use merge-skill conflict resolution techniques
- Document resolution in commit message
- If unresolvable, `git merge --abort` and report

### Push Failure
- Retry push up to 3 times
- Check remote status with `git remote -v`
- If still fails, report credential/permission issue

### Branch Not Found
- Report error and stop - don't proceed

---

## Completion Report

After successful completion, report:
```
✅ Task #{{TASK_ID}} Completed Successfully!

- Merged to main: ✓
- Pushed to remote: ✓
- Feature branch deleted: ✓
- Remote branch deleted: ✓
- Worktree cleaned: ✓
- Task status: Done ✓
- Session stopped: ✓

Merge commit: <hash>
The implementation is now in main and pushed to origin.
```

---

## Why This Architecture?

1. **Skill-based expertise** - merge-skill provides professional git workflows
2. **Agent isolation** - pr-merge-agent handles git operations independently
3. **Conflict resolution** - Expert guidance for handling merge conflicts
4. **Recovery** - Knows how to abort and recover from failed merges
5. **Reliability** - Agent has full git access and credentials
