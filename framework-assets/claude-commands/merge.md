---
allowed-tools: [Bash, Read, Write, Edit, Glob, Grep, Task, Skill]
argument-hint: [task-id]
description: Complete a task by merging PR, cleaning worktree, and stopping session
---

# /merge Command - Complete Task and Merge PR

Complete Task {{TASK_ID}} by merging its branch to main and cleaning up.

## MANDATORY: RAG-First Search Policy

**Before ANY merge operations, ALWAYS use RAG search to understand context:**

```bash
# 1. Search for git workflow documentation
mcp__claudetask__search_documentation --query="git workflow merge strategy" --top_k=10

# 2. Search for any merge-related patterns
mcp__claudetask__search_codebase --query="git merge conflict resolution" --top_k=10

# 3. Search for CI/CD or post-merge hooks
mcp__claudetask__search_codebase --query="post-merge hook CI deployment" --top_k=10
```

**Why RAG First for Merge?**
- Understand project's git workflow
- Find post-merge procedures
- Identify CI/CD requirements
- Discover cleanup patterns

---

## EXECUTION: Delegate to pr-merge-agent with merge-skill

**IMPORTANT: This command delegates work to a specialized agent with merge expertise!**

### Step 1: Get Task Details
```bash
mcp__claudetask__get_task --task_id={{TASK_ID}}
```

Extract:
- `git_branch` - branch name to merge
- `worktree_path` - path to cleanup (if exists)
- `project_id` - for project path lookup

### Step 2: RAG Context Gathering (MANDATORY)

**Before delegating, gather merge context:**

```bash
# Search for project's git workflow
mcp__claudetask__search_documentation --query="git branching strategy merge" --top_k=10

# Search for post-merge procedures
mcp__claudetask__search_documentation --query="deployment release procedures" --top_k=10

# Find any custom merge scripts
mcp__claudetask__search_codebase --query="merge script hook post-merge" --top_k=10
```

### Step 3: Delegate to PR Merge Agent

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

  **MANDATORY: Use Skill tool to load merge-skill BEFORE any git operations!**

  ```
  Skill("merge-skill")
  ```

  The merge-skill provides:
  - Merge strategies (fast-forward, 3-way, squash)
  - Conflict resolution techniques
  - Recovery operations if something goes wrong
  - Best practices for safe merging

  ## MANDATORY: RAG Search Before Merge

  Before any git operations, search for context:
  - mcp__claudetask__search_documentation --query="git merge workflow" --top_k=10
  - mcp__claudetask__search_codebase --query="post-merge cleanup script" --top_k=10

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

### Step 4: Update Task Status (after agent completes successfully)

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

### Step 5: Trigger Codebase Reindexing (MANDATORY)

**After merge, update RAG index with new code:**

```bash
# Reindex codebase to include merged changes
mcp__claudetask__reindex_codebase

# Reindex documentation if docs were changed
mcp__claudetask__reindex_documentation
```

---

## Important Notes:

**Mode-Dependent Behavior**:

**AUTO Mode (manual_mode = false):**
- This command is executed AUTOMATICALLY after code review passes
- NO user action required - orchestrator triggers via `/PR`

**Manual Mode (manual_mode = true):**
- User explicitly triggers this command after manual review

---

## RAG Search Patterns for Merge

```bash
# Git workflow patterns
mcp__claudetask__search_documentation --query="git workflow branching strategy" --top_k=10
mcp__claudetask__search_codebase --query="git hook pre-commit post-merge" --top_k=10

# CI/CD patterns
mcp__claudetask__search_documentation --query="CI CD deployment pipeline" --top_k=10
mcp__claudetask__search_codebase --query="deployment script release" --top_k=10

# Cleanup patterns
mcp__claudetask__search_codebase --query="cleanup worktree branch delete" --top_k=10

# Post-merge procedures
mcp__claudetask__search_documentation --query="release notes changelog" --top_k=10
```

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
Task #{{TASK_ID}} Completed Successfully!

- Merged to main: OK
- Pushed to remote: OK
- Feature branch deleted: OK
- Remote branch deleted: OK
- Worktree cleaned: OK
- Task status: Done
- Session stopped: OK
- Codebase reindexed: OK

Merge commit: <hash>
The implementation is now in main and pushed to origin.
```

---

## Post-Merge RAG Reindexing

**CRITICAL:** After merging, the RAG index should be updated to include new code:

```bash
# Incremental reindex (faster, only changes)
mcp__claudetask__reindex_codebase

# If documentation was updated
mcp__claudetask__reindex_documentation
```

This ensures future RAG searches include the newly merged code.

---

## Why This Architecture?

1. **RAG-First** - Search for context before merge operations
2. **Skill-based expertise** - merge-skill provides professional git workflows
3. **Agent isolation** - pr-merge-agent handles git operations independently
4. **Conflict resolution** - Expert guidance for handling merge conflicts
5. **Recovery** - Knows how to abort and recover from failed merges
6. **Reliability** - Agent has full git access and credentials
7. **Index Update** - RAG reindexing after merge keeps search current
