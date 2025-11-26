# Architecture Decisions: Task #15 - Session Task Details Fix

**Version**: 1.0
**Date**: 2025-11-26
**Task**: Session Task Details
**Complexity**: MODERATE

## Overview

This document records key architectural decisions made for resolving the session message display issue. Each decision follows the Architecture Decision Record (ADR) format with context, decision, rationale, and consequences.

---

## ADR-001: Message Data Source Selection

**Status**: ✅ ACCEPTED

**Context**:

TaskSessionsView currently displays "No messages yet" for sessions that have conversation history. Two options exist for sourcing message data:

1. **Option A**: Read from JSONL files on-demand (like ClaudeCodeSessionsView)
2. **Option B**: Sync JSONL messages to database periodically via background job

**Current State**:
- Database `claude_sessions.messages` field is NULL/empty
- Claude Code writes messages to `~/.claude/projects/{project}/*.jsonl` only
- ClaudeCodeSessionsView successfully reads from JSONL files directly

**Decision**: **Use Option A - Read from JSONL files on-demand**

**Rationale**:

**Pros of Option A**:
- ✅ Consistent with existing ClaudeCodeSessionsView implementation
- ✅ No database schema changes required
- ✅ Real-time access to messages as they're created
- ✅ Zero sync lag for active sessions
- ✅ Reuses existing `claude_sessions_reader.py` service patterns
- ✅ Lower maintenance overhead (no background jobs)
- ✅ Simpler implementation (no sync state to manage)

**Cons of Option A**:
- ❌ File I/O on every API request (minor performance impact)
- ❌ Dependent on file system access and permissions
- ❌ Large JSONL files may slow down response

**Pros of Option B**:
- ✅ Faster database queries (no file I/O)
- ✅ Better for analytics and aggregation queries
- ✅ Messages available even if JSONL deleted

**Cons of Option B**:
- ❌ Requires background sync job implementation
- ❌ Sync lag for active sessions (messages not immediately available)
- ❌ Additional complexity (job scheduling, error handling, retry logic)
- ❌ Database storage overhead (duplicate data)
- ❌ Sync state management complexity
- ❌ What happens if sync fails? (stale data issues)

**Consequences**:

**Positive**:
- Simple implementation following established patterns
- Real-time message availability
- No additional infrastructure (background jobs)
- Easy to understand and debug

**Negative**:
- File I/O performance dependency (mitigated by message limiting)
- Must handle missing/corrupted JSONL files gracefully

**Mitigation Strategies**:
- Limit messages to last 100 entries for performance
- Add optional `?limit=N` query parameter
- Cache parsed messages for completed sessions (future enhancement)
- Log file access issues for monitoring

---

## ADR-002: JSONL Parsing Location

**Status**: ✅ ACCEPTED

**Context**:

JSONL parsing logic needs to be implemented. Three options:

1. **Option A**: Add parsing function directly in `main.py` endpoint
2. **Option B**: Extend existing `claude_sessions_reader.py` service
3. **Option C**: Create new dedicated service `task_sessions_reader.py`

**Decision**: **Use Option A - Parse in main.py initially**

**Rationale**:

**Why Option A for Now**:
- ✅ Simple, focused implementation (YAGNI principle)
- ✅ Task-specific parsing may differ from ClaudeCodeSessionsView needs
- ✅ Faster to implement and test
- ✅ Easier to refactor later if patterns emerge

**Why Not Option B**:
- ❌ `claude_sessions_reader.py` is designed for different use case (project-level sessions)
- ❌ Risk of breaking existing ClaudeCodeSessionsView
- ❌ Different message format requirements (API format vs analytics format)

**Why Not Option C**:
- ❌ Over-engineering for a single endpoint
- ❌ Creates unnecessary abstraction layer
- ❌ More files to maintain

**Future Consideration**:
If JSONL parsing is needed in multiple places, refactor to shared service. For now, keep it simple.

**Consequences**:

**Positive**:
- Rapid development with clear scope
- Lower risk of breaking existing functionality
- Easy to understand and maintain

**Negative**:
- Potential code duplication if more endpoints need JSONL parsing
- May need refactoring later

**Refactoring Trigger**:
If 3+ endpoints need JSONL parsing, extract to shared service.

---

## ADR-003: Message Format and Content Handling

**Status**: ✅ ACCEPTED

**Context**:

Claude API messages have varied content structures:
- Simple string: `"Hello"`
- Array of blocks: `[{type:"text", text:"Hi"}, {type:"tool_use",...}]`
- Object with text: `{text: "Hello"}`

Frontend (TaskSessionsView.tsx) already handles these formats (lines 598-649).

**Decision**: **Return messages in Claude API format, let frontend handle rendering**

**Rationale**:

**Why This Approach**:
- ✅ Frontend already has comprehensive content rendering logic
- ✅ No need to normalize or transform message format
- ✅ Preserves full message fidelity (tool_use, tool_result, etc.)
- ✅ Consistent with how ClaudeCodeSessionsView works

**Message Format Returned by Backend**:
```python
{
  "role": "user" | "assistant",
  "content": Any,  # String, array, or object
  "timestamp": "ISO datetime string"
}
```

**Consequences**:

**Positive**:
- Zero frontend changes required
- Full message content preserved
- Tool blocks display correctly (already tested in ClaudeCodeSessionsView)

**Negative**:
- Backend doesn't validate content structure (relies on frontend robustness)

**Validation Strategy**:
- Frontend is already defensive (handles null, undefined, various formats)
- If unknown format encountered, frontend falls back to JSON.stringify()

---

## ADR-004: Path Resolution Strategy

**Status**: ✅ ACCEPTED

**Context**:

JSONL files stored in `~/.claude/projects/{encoded-path}/{session-id}.jsonl`, but:
- Database has `session.id` (primary key)
- Database has `session.session_id` (separate field, may be NULL)
- Unclear which field matches JSONL filename

**Decision**: **Try both fields with fallback logic**

**Rationale**:

**Path Resolution Algorithm**:
```python
# Step 1: Construct project directory
project_encoded = project_id.replace('/', '-')
claude_dir = Path.home() / ".claude" / "projects" / project_encoded

# Step 2: Try primary key first
jsonl_path = claude_dir / f"{session.id}.jsonl"
if jsonl_path.exists():
    return jsonl_path

# Step 3: Try session_id field if available
if session.session_id:
    jsonl_path = claude_dir / f"{session.session_id}.jsonl"
    if jsonl_path.exists():
        return jsonl_path

# Step 4: No JSONL found
return None
```

**Why This Approach**:
- ✅ Handles both naming conventions
- ✅ Graceful fallback if field naming changes
- ✅ Logs which mapping worked for future optimization

**Consequences**:

**Positive**:
- Robust against field naming variations
- Easy to adapt if JSONL naming convention changes
- Clear logging helps understand actual mapping

**Negative**:
- Two file existence checks per session (minor overhead)

**Optimization**:
Once correct mapping is determined through logs, simplify to single check.

---

## ADR-005: Error Handling Philosophy

**Status**: ✅ ACCEPTED

**Context**:

Multiple error scenarios possible:
- JSONL file not found
- JSONL file corrupted (malformed JSON)
- File system permission errors
- Path traversal attempts

**Decision**: **Graceful degradation with informative logging**

**Rationale**:

**Error Handling Strategy**:

| Error Type | HTTP Status | Response | Log Level | User Impact |
|-----------|-------------|----------|-----------|-------------|
| JSONL not found | 200 | `messages: []` | WARNING | Shows "No messages yet" |
| JSONL corrupted | 200 | `messages: []` | ERROR | Shows "No messages yet" |
| Permission denied | 200 | `messages: []` | ERROR | Shows "No messages yet" |
| Path traversal | 400 | Error message | ERROR | Request rejected |

**Why Graceful Degradation**:
- ✅ Session metadata still useful without messages
- ✅ Overview tab, Tools tab still functional
- ✅ Missing messages != broken session
- ✅ Better UX than showing error modal

**Logging Philosophy**:
- INFO: Successful JSONL read
- WARNING: JSONL not found (expected for old sessions)
- ERROR: JSONL corrupted, permission denied, security violation

**Consequences**:

**Positive**:
- User can still access session information
- Clear distinction between expected (missing file) and unexpected (corruption) issues
- Debugging is straightforward via logs

**Negative**:
- User doesn't get explicit error for corrupted files (just empty state)

**Future Enhancement**:
Add session metadata flag: `"messages_available": boolean` to indicate JSONL status

---

## ADR-006: Performance Optimization Approach

**Status**: ✅ ACCEPTED

**Context**:

Some sessions may have 500+ messages (large JSONL files). Reading entire file could slow down API response.

**Decision**: **Limit messages to last 100 entries by default**

**Rationale**:

**Implementation**:
```python
def parse_jsonl_messages(jsonl_path: Path, limit: int = 100) -> List[dict]:
    """Parse last N messages from JSONL"""
    # Read file, parse, limit to last N messages
    messages = []
    for line in file:
        messages.append(parsed_line)
        if len(messages) > limit:
            messages.pop(0)  # Keep sliding window

    return messages
```

**Why 100 Messages**:
- ✅ Covers typical session conversation length
- ✅ Fast parsing (< 100ms for 100 messages)
- ✅ Reasonable API response size (< 500KB)
- ✅ User can still see recent context

**Optional Enhancement**:
Add query parameter: `?limit=N` or `?limit=all`

**Consequences**:

**Positive**:
- Consistent API performance regardless of session size
- Lower memory usage
- Faster JSON serialization

**Negative**:
- Very long sessions don't show full history initially

**Future Enhancement**:
- Add "Load More" button in frontend
- Add pagination: `?limit=100&offset=0`
- Add "Export Full Transcript" feature

---

## ADR-007: Security Validation Requirements

**Status**: ✅ ACCEPTED

**Context**:

File system access from API endpoint has security implications. Must prevent:
- Path traversal attacks (`../../etc/passwd`)
- Access to files outside `.claude` directory

**Decision**: **Strict path validation with resolved path checking**

**Rationale**:

**Validation Strategy**:
```python
def validate_session_path(jsonl_path: Path) -> bool:
    """Ensure path stays within .claude directory"""
    try:
        resolved = jsonl_path.resolve()
        claude_base = (Path.home() / ".claude").resolve()

        if not str(resolved).startswith(str(claude_base)):
            logger.error(f"Path traversal attempt: {resolved}")
            return False

        return True
    except Exception as e:
        logger.error(f"Path validation error: {e}")
        return False
```

**Why This Approach**:
- ✅ `.resolve()` normalizes path (removes `..`, symlinks)
- ✅ String prefix check ensures containment
- ✅ Logs security violations for monitoring
- ✅ Works cross-platform (Windows, Linux, macOS)

**Consequences**:

**Positive**:
- Strong security boundary
- Clear audit trail via logs
- Protection against common attacks

**Negative**:
- Slight performance overhead (path resolution)

**Trade-off**: Security > Performance (validation is fast anyway)

---

## ADR-008: Frontend Changes Decision

**Status**: ✅ ACCEPTED

**Context**:

Frontend (TaskSessionsView.tsx) already has message rendering logic similar to ClaudeCodeSessionsView.

**Decision**: **No frontend changes required**

**Rationale**:

**Current Frontend Capabilities** (lines 547-662):
- ✅ Renders messages from `selectedSession.messages` array
- ✅ Handles string, array, and object content formats
- ✅ Displays tool_use blocks with highlighting
- ✅ Displays tool_result blocks with scrolling
- ✅ Shows "No messages yet" for empty array
- ✅ Proper styling for user vs Claude messages

**Why No Changes Needed**:
Backend will return messages in the exact format frontend already expects.

**Consequences**:

**Positive**:
- Zero frontend risk
- No regression testing needed for UI
- Faster implementation
- Lower complexity

**Negative**:
- None (frontend is already feature-complete for this use case)

---

## Summary of Decisions

| ADR | Decision | Rationale | Impact |
|-----|----------|-----------|--------|
| 001 | Read from JSONL files | Consistent with existing pattern, real-time data | Backend-only changes |
| 002 | Parse in main.py | Simple, focused implementation | Easy to refactor later |
| 003 | Return Claude API format | Frontend already handles it | Zero frontend changes |
| 004 | Try both ID fields | Handles naming variations | Robust path resolution |
| 005 | Graceful degradation | Better UX for missing messages | Informative logging |
| 006 | Limit to 100 messages | Performance optimization | Future pagination option |
| 007 | Strict path validation | Security requirement | Prevents traversal |
| 008 | No frontend changes | Already feature-complete | Lower risk, faster delivery |

## Technical Debt & Future Enhancements

### Known Limitations

1. **No Pagination**: Large sessions load only last 100 messages
   - **Future**: Add "Load More" or pagination
   - **Priority**: LOW (affects edge cases only)

2. **No Real-Time Updates**: Messages don't auto-refresh for active sessions
   - **Future**: Add WebSocket updates or polling
   - **Priority**: MEDIUM (nice-to-have, not critical)

3. **No Message Search**: Can't search within session messages
   - **Future**: Add search/filter functionality
   - **Priority**: LOW (browser Ctrl+F works)

### Refactoring Opportunities

If JSONL parsing is needed in 3+ places:
- Extract to shared service: `claude_sessions_reader.py`
- Create unified JSONL parsing interface
- Add caching layer for completed sessions

### Monitoring & Observability

Add metrics:
- JSONL file read latency
- JSONL not found rate (indicates migration issues)
- JSONL parse error rate (indicates corruption)

## Conclusion

These architectural decisions prioritize:
1. **Simplicity**: Follow existing patterns, minimal changes
2. **Reliability**: Graceful error handling, security validation
3. **Performance**: Message limiting, efficient parsing
4. **Maintainability**: Clear code, good logging, future-proof design

By reading from JSONL files on-demand and reusing frontend logic, we achieve the fix with ~50-80 lines of backend code and zero frontend risk.
