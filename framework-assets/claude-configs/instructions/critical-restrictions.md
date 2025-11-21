# 🔴🔴🔴 ABSOLUTE CRITICAL RESTRICTIONS 🔴🔴🔴

## ⛔ NEVER DELETE WORKTREES WITHOUT EXPLICIT USER REQUEST
**UNDER NO CIRCUMSTANCES should you:**
- ❌ Delete any worktree directory
- ❌ Remove any worktree with `git worktree remove`
- ❌ Clean up worktrees unless user EXPLICITLY types: "delete worktree for task X"
- ❌ Assume a worktree should be deleted

## ⛔ NEVER MARK TASKS AS "DONE" WITHOUT EXPLICIT USER REQUEST
**UNDER NO CIRCUMSTANCES should you:**
- ❌ Change any task status to "Done" automatically
- ❌ Mark tasks as complete without user EXPLICITLY typing: "mark task X as done"
- ❌ Close tasks based on assumptions
- ❌ Transition from any status to "Done" unless directly instructed

## ✅ ONLY WHEN USER EXPLICITLY REQUESTS:
User must type EXACT phrases like:
- "mark task 23 as done"
- "close task 23"
- "delete worktree for task 23"
- "remove task 23 worktree"

**ANY other phrasing = DO NOT perform these actions**

## 🔴 CODE REVIEW STATUS RESTRICTIONS
**⛔ IF TASK IS IN "CODE REVIEW" STATUS:**
- ❌ **NEVER** transition to "Done"
- ❌ **NEVER** delete worktree
- ❌ **NEVER** delete branch
- ❌ **NEVER** close the task
- ❌ **NEVER** clean up any resources
- ✅ **ONLY** allowed transition: Code Review → Pull Request (after review complete)
- ✅ **WAIT** for user's explicit instruction to proceed

**VIOLATIONS OF THESE RULES WILL RESULT IN DATA LOSS**
