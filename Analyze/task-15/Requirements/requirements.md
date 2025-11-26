# Requirements Document: Task #15 - Session Task Details Fix

**Version**: 1.0
**Date**: 2025-11-26
**Complexity**: MODERATE
**Project**: Claude Code Feature Framework

## Executive Summary

The Task Sessions detail view in the Sessions page (`TaskSessionsView.tsx`) currently fails to display session messages despite showing sessions as active. The root cause is a data source mismatch: the UI fetches from the database (`claude_sessions.messages` field), but messages are actually stored in Claude Code's native JSONL files (`~/.claude/projects/*/session-id.jsonl`). This document outlines requirements to resolve this issue.

## Problem Statement

**Current Behavior**:
- TaskSessionsView fetches sessions via `/api/projects/{project_id}/sessions`
- Backend returns session records from `claude_sessions` table
- `messages` field in database is NULL or empty
- UI displays "No messages yet" even for active sessions with conversation history

**Expected Behavior**:
- Session detail dialog shows actual conversation messages
- Messages display user and Claude responses with proper formatting
- Active sessions show real-time or recent messages
- Completed sessions show full conversation history

**Root Cause**:
Messages are persisted to JSONL files by Claude Code CLI but never synced to the database. The `ClaudeSession` model has a `messages` JSON field that remains unpopulated.

## User Stories

### US-1: View Session Messages
**As a** developer
**I want to** view conversation messages when opening a task session detail dialog
**So that** I can understand what work was done in that session

**Acceptance Criteria**:
- Clicking "View Details" on a session opens dialog with messages
- Messages tab displays user and Claude messages with timestamps
- Messages show proper formatting (text, tool use, tool results)
- Both active and completed sessions show their messages
- Empty sessions display "No messages yet" appropriately

### US-2: Monitor Active Session Progress
**As a** project manager
**I want to** see recent messages from active sessions
**So that** I can monitor ongoing work without interrupting the developer

**Acceptance Criteria**:
- Active sessions show at least the last 10-20 messages
- Messages update when dialog is refreshed
- Status indicator shows session is actively running
- Tool usage and commands are visible in messages

### US-3: Review Completed Session History
**As a** team member
**I want to** review the complete conversation history of completed sessions
**So that** I can learn from past implementations and decisions

**Acceptance Criteria**:
- Completed sessions show full message history
- Messages include all user prompts and Claude responses
- Tool invocations and results are visible
- Session statistics reflect actual message count

## Functional Requirements

### FR-1: Message Data Source Selection
**Priority**: HIGH

The system must choose one of two approaches:

**Option A: Read from JSONL Files (Recommended)**
- Backend reads messages directly from `~/.claude/projects/{project}/session-{id}.jsonl`
- No database schema changes required
- Consistent with `ClaudeCodeSessionsView` approach
- Real-time access to messages as they're created

**Option B: Sync Messages to Database**
- Periodically sync JSONL messages to `claude_sessions.messages` field
- Requires background job or trigger mechanism
- Adds complexity but improves query performance
- May have sync lag for active sessions

**Decision Criteria**:
- Consistency with existing patterns (ClaudeCodeSessionsView uses JSONL)
- Maintenance overhead (sync jobs require monitoring)
- Performance considerations (JSONL read vs database query)
- Real-time requirements (active session messages)

### FR-2: Backend API Enhancement
**Priority**: HIGH

Modify `/api/projects/{project_id}/sessions` endpoint:

**Current Implementation**:
```python
# Returns session.messages from database (NULL/empty)
session_dict["messages"] = session.messages
```

**Required Enhancement**:
```python
# Read messages from JSONL file if available
if session.working_dir and session.id:
    jsonl_path = f"{session.working_dir}/.claude/sessions/{session.id}.jsonl"
    if os.path.exists(jsonl_path):
        messages = parse_jsonl_messages(jsonl_path)
        session_dict["messages"] = messages
    else:
        session_dict["messages"] = []
```

**Additional Requirements**:
- Support optional `include_messages=true` query parameter (performance)
- Limit message count for large sessions (e.g., last 100 messages)
- Handle JSONL parse errors gracefully
- Log missing or corrupted JSONL files

### FR-3: Frontend Message Display
**Priority**: MEDIUM

TaskSessionsView already has message rendering logic (similar to ClaudeCodeSessionsView):

**Required Verification**:
- Confirm message format compatibility with Claude API structure
- Ensure tool_use and tool_result blocks render correctly
- Verify proper styling for user vs Claude messages
- Test with various message content types (text, arrays, objects)

**Enhancement Opportunities**:
- Add message filtering (show only user messages, only errors, etc.)
- Implement message search within session
- Add export functionality for session transcript

### FR-4: Session Statistics Update
**Priority**: LOW

Update message count and statistics to reflect actual messages:

**Current Issue**:
- Session statistics may show incorrect message counts
- Tool usage counts may be outdated

**Required**:
- Recalculate message count from JSONL when displaying session
- Update tool usage statistics based on actual messages
- Display session duration accurately

## Non-Functional Requirements

### NFR-1: Performance
- JSONL parsing for 100 messages: < 200ms
- Session detail dialog load time: < 1 second
- Pagination for sessions with 1000+ messages
- Lazy loading for message content (load on tab switch)

### NFR-2: Compatibility
- Maintain backward compatibility with existing database schema
- Support sessions created before and after fix
- Handle missing JSONL files gracefully (old sessions)
- Work with both development and production environments

### NFR-3: Reliability
- Graceful degradation if JSONL file is missing
- Error handling for corrupted JSONL files
- Logging for debugging message loading issues
- Retry mechanism for file read errors

### NFR-4: Maintainability
- Reuse existing JSONL parsing code from `claude_sessions_reader.py`
- Follow existing patterns from `ClaudeCodeSessionsView`
- Document message source decision in code comments
- Add unit tests for JSONL parsing edge cases

## Business Rules

### BR-1: Message Source Priority
1. If JSONL file exists and is readable → use JSONL messages
2. If JSONL missing but database has messages → use database messages (legacy)
3. If both missing → display "No messages yet"

### BR-2: Message Access Control
- Sessions are project-scoped (no cross-project access)
- Users can view all sessions within their project
- No message content filtering or redaction required (local tool)

### BR-3: Active Session Behavior
- Active sessions show messages up to current point
- Messages update when user manually refreshes dialog
- No real-time WebSocket updates required (manual refresh acceptable)

### BR-4: Session File Location Resolution
- Use `session.working_dir` as base path
- JSONL files located at: `{working_dir}/.claude/sessions/{session_id}.jsonl`
- Handle path variations (absolute vs relative paths)
- Validate paths to prevent directory traversal

## Definition of Done (DoD)

### Implementation Complete
- [ ] Backend reads messages from JSONL files OR syncs them to database
- [ ] `/api/projects/{project_id}/sessions` returns populated messages
- [ ] TaskSessionsView dialog displays messages correctly
- [ ] Message formatting matches Claude API structure

### Quality Verified
- [ ] Unit tests for JSONL parsing and edge cases
- [ ] Integration test: create session, verify messages appear
- [ ] Manual testing: open detail dialog, verify messages display
- [ ] Error scenarios tested (missing file, corrupted JSONL, empty session)

### Documentation Updated
- [ ] Code comments explain message source decision
- [ ] API documentation updated for endpoint changes
- [ ] Component documentation reflects new behavior
- [ ] Known limitations documented (if any)

### User Experience Validated
- [ ] Active sessions show recent messages
- [ ] Completed sessions show full history
- [ ] Empty sessions show appropriate message
- [ ] Tool use/results display correctly
- [ ] Performance acceptable for large sessions

## Out of Scope

The following items are explicitly NOT included in this task:

- Real-time WebSocket updates for active session messages
- Message editing or deletion functionality
- Advanced message filtering or search
- Export session transcript to file
- Message content redaction or privacy controls
- Database schema migration to store all messages
- Automatic background sync jobs
- Session replay or step-through debugging

## Dependencies

### Internal Dependencies
- `claudetask/backend/app/services/claude_sessions_reader.py` - JSONL parsing
- `claudetask/frontend/src/pages/ClaudeSessions.tsx` - Reference implementation
- `claudetask/backend/app/models.py` - ClaudeSession model
- `claudetask/backend/app/main.py` - API endpoint implementation

### External Dependencies
- Claude Code CLI JSONL file format (must remain stable)
- File system access to project `.claude/sessions/` directory
- JSONL file permissions (must be readable)

### Assumptions
- Claude Code continues writing messages to JSONL files
- JSONL file format remains backward compatible
- Session working_dir paths are correctly stored in database
- File system has adequate performance for JSONL reads

## Success Metrics

### Primary Metrics
- **Message Display Rate**: 100% of sessions with JSONL files show messages
- **Load Performance**: Session detail opens in < 1 second
- **Error Rate**: < 1% of session detail views fail to load

### Secondary Metrics
- **User Satisfaction**: Developers can review session history effectively
- **Support Requests**: Reduction in "can't see messages" support tickets
- **Code Quality**: Reuses existing patterns, maintains consistency

## Risk Assessment

### Technical Risks
| Risk | Probability | Impact | Mitigation |
|------|------------|--------|------------|
| JSONL format change | Low | High | Version check, fallback to database |
| Large file parsing slow | Medium | Medium | Implement pagination, limit messages |
| File not found | High | Low | Graceful fallback, clear error message |
| Path traversal security | Low | High | Strict path validation, project scope check |

### Implementation Risks
| Risk | Probability | Impact | Mitigation |
|------|------------|--------|------------|
| Breaking existing functionality | Low | High | Comprehensive testing, careful refactoring |
| Performance degradation | Medium | Medium | Load testing, optimization if needed |
| Inconsistent message format | Medium | Medium | Robust parsing, handle multiple formats |

## Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2025-11-26 | Requirements Analyst | Initial document |
