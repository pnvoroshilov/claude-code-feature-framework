# SIMPLE Mode Status Management Updates

## 📋 Summary

Updated CLAUDE.md to properly handle SIMPLE mode project configuration with correct status transition rules.

## 🎯 Problem

The framework CLAUDE.md contained instructions for DEVELOPMENT mode with complex status workflow (Backlog → Analysis → In Progress → Testing → Code Review → PR → Done), but this project is configured in **SIMPLE mode** with only 3 statuses:
- Backlog
- In Progress
- Done

This caused issues where:
- ❌ Tasks were auto-transitioning to non-existent statuses (Testing, Code Review)
- ❌ Coordinator was trying to setup test environments
- ❌ Worktrees were being created unnecessarily
- ❌ Git branches were being managed when not needed

## ✅ Solution

Added mode-specific instructions at the **TOP** of CLAUDE.md that clearly define SIMPLE mode behavior:

### Key Changes:

#### 1. **Added SIMPLE Mode Status Rules Section (Lines 19-79)**
```
## 🔴 CRITICAL: SIMPLE Mode Status Rules

**⚠️ IN SIMPLE MODE, IGNORE ALL INSTRUCTIONS ABOUT:**
- ❌ Analysis status - Skip directly to In Progress
- ❌ Testing status - Do NOT auto-transition to Testing
- ❌ Code Review status - Does not exist in SIMPLE mode
- ❌ Pull Request status - Does not exist in SIMPLE mode
- ❌ Worktrees and git branches - Work directly in main branch
- ❌ Test environment setup - No automatic test server management
```

#### 2. **Clear Status Flow for SIMPLE Mode**
```
Backlog → In Progress → Done
```

**Status Transition Rules:**
- ✅ Backlog → In Progress: When user starts working
- ✅ In Progress → Done: **ONLY when user explicitly requests** "mark task X as done"
- ❌ NO auto-transitions based on implementation detection
- ❌ NO Testing status in between
- ❌ NO worktree or branch management

#### 3. **Updated Status Management Section (Lines 878-897)**
Added mode-specific conditional logic:
```
**🔴 IF PROJECT MODE = SIMPLE (check top of this file):**

SIMPLE Mode Status Flow:
Backlog → In Progress → Done

RULES:
- ❌ NO Analysis, Testing, Code Review, PR statuses
- ❌ NO auto-transitions except user starting task
- ❌ NO worktrees, branches, test environments
- ✅ ONLY transition to Done when user explicitly requests
- ✅ Work directly in main branch

**Stop reading here if in SIMPLE mode. The rest is for DEVELOPMENT mode only.**
```

#### 4. **Updated Agent Delegation Section (Lines 346-351)**
Added warning that delegation rules apply to DEVELOPMENT MODE only:
```
**⚠️ IMPORTANT: These delegation rules apply to DEVELOPMENT MODE ONLY.**
**In SIMPLE mode, skip Analysis phase and delegation - see SIMPLE Mode rules at top of file.**
```

## 🎯 What Coordinator Should Do in SIMPLE Mode

### When Monitoring Tasks:
1. ✅ Check task queue for new Backlog tasks
2. ✅ Provide assistance when user requests help
3. ❌ NEVER auto-transition statuses (except Backlog → In Progress when user starts)
4. ✅ Wait for explicit "mark as done" command

### When User Works on Task:
1. ✅ Provide assistance as requested
2. ❌ Do NOT setup test environments
3. ❌ Do NOT create worktrees
4. ❌ Do NOT manage git branches
5. ✅ Work directly in main branch

### When Implementation Complete:
1. ❌ Do NOT auto-transition to Testing
2. ❌ Do NOT auto-transition to Done
3. ✅ Task STAYS "In Progress"
4. ✅ Wait for user command: "mark task X as done"

## 📝 Files Modified

### 1. `/CLAUDE.md` (Framework Instructions)
- **Lines 19-79**: Added SIMPLE Mode Status Rules section
- **Lines 878-897**: Updated Status Management with mode-specific flows
- **Lines 346-351**: Added DEVELOPMENT mode warnings to delegation section

## 🧪 Testing Checklist

- [ ] Coordinator reads SIMPLE mode instructions at top
- [ ] No auto-transition to Testing status
- [ ] No worktree creation in SIMPLE mode
- [ ] No test environment setup
- [ ] Tasks stay "In Progress" until user marks as Done
- [ ] No Analysis phase in SIMPLE mode

## 🚀 Usage

When coordinator starts, it will:
1. Read CLAUDE.md and see PROJECT MODE: SIMPLE at the top
2. Follow SIMPLE mode status rules (lines 19-79)
3. Ignore all DEVELOPMENT mode instructions (which are clearly marked)
4. Use simple workflow: Backlog → In Progress → Done

## 📚 Documentation

The SIMPLE mode instructions are now:
- ✅ **Prominent** - At the very top of CLAUDE.md
- ✅ **Clear** - Explicit list of what to ignore
- ✅ **Complete** - Full status transition rules
- ✅ **Conditional** - Development mode sections clearly marked

## ⚠️ Important Notes

1. **Mode Detection**: Coordinator must read the PROJECT MODE at top of CLAUDE.md
2. **Explicit Commands**: In SIMPLE mode, ONLY explicit user commands trigger status changes
3. **No Automation**: No automatic status transitions based on implementation detection
4. **Simple Workflow**: Work directly in main branch, no git complexity

---

**Date**: 2025-11-13
**Author**: Claude Code
**Status**: Completed ✅
