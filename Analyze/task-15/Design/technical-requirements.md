# Technical Requirements: Task #15 - Session Task Details Fix

**Version**: 1.0
**Date**: 2025-11-26
**Task**: Session Task Details
**Complexity**: MODERATE

## Executive Summary

Fix TaskSessionsView to display session messages by reading from JSONL files instead of the database. The database `messages` field is NULL/empty, but messages exist in `~/.claude/projects/{project}/*.jsonl` files. Follow the pattern used by ClaudeCodeSessionsView which already successfully reads JSONL files.

## Root Cause Analysis

**Current Flow**:
```
TaskSessionsView → GET /api/projects/{project_id}/sessions
                 → Returns session.messages from database (NULL)
                 → UI shows "No messages yet"
```

**Working Flow** (ClaudeCodeSessionsView):
```
ClaudeCodeSessionsView → Uses claude_sessions_reader.py service
                       → Reads from JSONL files directly
                       → Parses and displays messages successfully
```

**Problem**: TaskSessionsView relies on database field that is never populated. Claude Code writes messages to JSONL files only, not to the database.

## Solution: Read from JSONL Files (Option A)

**Recommended Approach**: Enhance the `/api/projects/{project_id}/sessions` endpoint to read messages from JSONL files when available.

### Why Option A?
- ✅ Consistent with existing ClaudeCodeSessionsView pattern
- ✅ No database schema changes required
- ✅ Real-time access to messages as they're created
- ✅ Reuses existing `claude_sessions_reader.py` service
- ✅ Lower maintenance overhead (no sync jobs)

## What Needs to Change

### 1. Backend API Endpoint Enhancement

**File**: `claudetask/backend/app/main.py`
**Location**: Lines 1021-1051 (function `get_project_sessions`)

**Current Implementation** (line 1043):
```python
"messages": session.messages,  # NULL/empty from database
```

**Required Change**:
```python
# Read messages from JSONL if available, fallback to database
messages = []
if session.working_dir and session.id:
    # Construct JSONL path
    project_encoded = project_id.replace('/', '-')
    claude_projects_dir = Path.home() / ".claude" / "projects" / project_encoded
    jsonl_path = claude_projects_dir / f"{session.id}.jsonl"

    if jsonl_path.exists():
        try:
            messages = parse_jsonl_messages(jsonl_path)
        except Exception as e:
            logger.warning(f"Failed to parse JSONL {jsonl_path}: {e}")
            messages = session.messages or []
    else:
        # Fallback to database messages (legacy sessions)
        messages = session.messages or []
else:
    messages = session.messages or []

session_dict["messages"] = messages
```

**New Function Required**:
```python
def parse_jsonl_messages(jsonl_path: Path) -> List[dict]:
    """
    Parse messages from Claude Code JSONL file

    Returns messages in format compatible with frontend:
    [
      {
        "role": "user" | "assistant",
        "content": string | array,
        "timestamp": ISO datetime string
      }
    ]
    """
    messages = []
    with open(jsonl_path, 'r', encoding='utf-8') as f:
        for line in f:
            try:
                entry = json.loads(line.strip())
                entry_type = entry.get("type")

                if entry_type in ["user", "assistant"]:
                    messages.append({
                        "role": entry_type,
                        "content": entry.get("content", ""),
                        "timestamp": entry.get("timestamp"),
                    })
            except json.JSONDecodeError as e:
                logger.warning(f"Skipping malformed JSON line: {e}")
                continue

    return messages
```

**Integration Points**:
- Import `Path` from `pathlib`
- Import `logger` for error logging
- Consider extracting to `claude_sessions_reader.py` service for reusability

### 2. JSONL Path Resolution Challenge

**Problem**: Database stores UUID-like `session.id`, but JSONL filename mapping is unclear.

**Investigation Required**:
1. Check if `session.id` matches JSONL filename exactly
2. Check if `session.session_id` field (line 120 in models.py) is the JSONL filename
3. Verify actual JSONL file naming convention in `~/.claude/projects/*/`

**Current Database Schema** (models.py line 119-120):
```python
id = Column(String, primary_key=True, index=True)
session_id = Column(String, nullable=True, index=True)  # Added session_id field
```

**Likely Solution**:
- Try `session.id` first for filename
- If not found, try `session.session_id`
- Log which mapping works for future reference

### 3. Frontend Verification (Minimal Changes)

**File**: `claudetask/frontend/src/components/sessions/TaskSessionsView.tsx`
**Location**: Lines 547-662 (Messages TabPanel)

**Current Code Analysis**:
- ✅ Already has message rendering logic (lines 549-660)
- ✅ Handles different content formats (string, array, object)
- ✅ Renders tool_use and tool_result blocks correctly
- ✅ Shows "No messages yet" when array is empty

**Required Change**: **NONE** - Frontend already handles message display correctly!

**Why No Frontend Changes?**:
The frontend expects `selectedSession.messages` to be an array. As long as the backend returns messages in the correct format, existing UI will work.

**Format Expected by Frontend** (inferred from lines 598-649):
```typescript
messages: Array<{
  role: 'user' | 'assistant';
  content: string | Array<{
    type: 'text' | 'tool_use' | 'tool_result';
    text?: string;
    name?: string;
    input?: any;
    content?: any;
  }>;
}>
```

### 4. Error Handling & Edge Cases

**Scenarios to Handle**:

| Scenario | Behavior | HTTP Status |
|----------|----------|-------------|
| JSONL file found and valid | Return parsed messages | 200 |
| JSONL file missing | Fallback to `session.messages` (database) | 200 |
| JSONL file corrupted | Log error, return empty array or database messages | 200 |
| Path traversal attempt | Validate paths, reject suspicious patterns | 400 |
| Project directory not found | Return empty messages | 200 |

**Logging Strategy**:
- INFO: Successful JSONL read
- WARNING: JSONL not found (expected for old sessions)
- ERROR: JSONL parse failure, path validation failure

### 5. Performance Considerations

**Current Endpoint Performance**: < 100ms (database query only)
**Target Performance**: < 500ms (including JSONL read)

**Optimization Strategy**:
- Limit messages to last 100 entries for initial load
- Add optional query parameter: `?limit=100`
- Consider caching for completed sessions (messages won't change)

**Message Limiting**:
```python
# In parse_jsonl_messages function
messages = []
for line in f:
    # ... parse line ...
    messages.append(parsed_entry)

    if len(messages) >= limit:
        break  # Stop reading after limit reached

return messages
```

## Dependencies & Integration Points

### Reuse Existing Code

**Service**: `claudetask/backend/app/services/claude_sessions_reader.py`

This service already has JSONL parsing logic for ClaudeCodeSessionsView:
- `_parse_session_file()` method (lines 107-214) - comprehensive parsing
- `get_session_details()` method (lines 216-274) - includes message extraction

**Option 1**: Extract and adapt existing parsing logic
**Option 2**: Extend `claude_sessions_reader.py` with new method for task sessions

**Recommendation**: Create a lightweight parser in `main.py` initially. If complexity grows, refactor to shared service.

### Path Construction Logic

**Key Discovery** (from `claude_sessions_reader.py`):
- Claude Code encodes project paths with dashes: `/Users/path/to/project` → `Users-path-to-project`
- Projects stored in `~/.claude/projects/{encoded-path}/`
- Session files: `{project-dir}/{session-id}.jsonl`

**Path Construction**:
```python
from pathlib import Path
import os

def get_session_jsonl_path(project_id: str, session_id: str) -> Path:
    """
    Construct path to session JSONL file

    Args:
        project_id: Project ID (may be path-like)
        session_id: Session UUID

    Returns:
        Path to JSONL file
    """
    # Encode project path (replace slashes with dashes)
    project_encoded = project_id.replace('/', '-').replace(os.sep, '-')

    # Construct full path
    claude_dir = Path.home() / ".claude" / "projects" / project_encoded
    jsonl_path = claude_dir / f"{session_id}.jsonl"

    # Security: Validate path stays within .claude directory
    try:
        resolved = jsonl_path.resolve()
        claude_base = (Path.home() / ".claude").resolve()
        if not str(resolved).startswith(str(claude_base)):
            raise ValueError("Path traversal detected")
    except Exception as e:
        logger.error(f"Invalid path construction: {e}")
        return None

    return jsonl_path
```

## Testing Strategy

### Unit Tests

**File**: `claudetask/backend/tests/test_sessions_api.py` (create if needed)

**Test Cases**:
1. **test_parse_jsonl_messages_valid_file** - Parse valid JSONL with user/assistant messages
2. **test_parse_jsonl_messages_corrupted_file** - Handle malformed JSON lines gracefully
3. **test_parse_jsonl_messages_empty_file** - Return empty array for empty file
4. **test_get_session_jsonl_path** - Verify correct path construction
5. **test_path_traversal_prevention** - Ensure security validation works

### Integration Tests

**File**: `claudetask/backend/tests/test_sessions_integration.py`

**Test Scenarios**:
1. **test_get_project_sessions_with_jsonl** - API returns messages from JSONL
2. **test_get_project_sessions_without_jsonl** - API falls back to database messages
3. **test_get_project_sessions_jsonl_error** - API handles JSONL parse errors gracefully

### Manual Testing Checklist

From `acceptance-criteria.md`:
- [ ] AC-2: Messages display for active sessions
- [ ] AC-3: Messages display for completed sessions
- [ ] AC-4: Empty sessions show appropriate message
- [ ] AC-5: Tool use and results display correctly
- [ ] AC-8: Error handling for missing JSONL files
- [ ] AC-9: Backend API returns messages

## Security Considerations

### Path Traversal Prevention

**Risk**: Malicious `project_id` or `session_id` could access arbitrary files

**Mitigation**:
```python
# Validate resolved path stays within .claude directory
resolved_path = jsonl_path.resolve()
claude_base = (Path.home() / ".claude").resolve()

if not str(resolved_path).startswith(str(claude_base)):
    raise SecurityError("Invalid path - potential traversal")
```

### Project Scope Validation

**Current Implementation**: Already validated via database query
```python
.where(ClaudeSession.project_id == project_id)
```

This ensures only sessions belonging to the requested project are returned.

## Rollout Plan

### Phase 1: Backend Enhancement
1. Add `parse_jsonl_messages()` function to `main.py`
2. Add `get_session_jsonl_path()` helper function
3. Modify `get_project_sessions()` endpoint (lines 1021-1051)
4. Add error logging for debugging

### Phase 2: Testing
1. Write unit tests for JSONL parsing
2. Write integration tests for API endpoint
3. Manual testing with real sessions
4. Verify no regression in ClaudeCodeSessionsView

### Phase 3: Validation
1. Test with active sessions (messages updating in real-time)
2. Test with completed sessions (full history)
3. Test with empty/idle sessions
4. Test with missing JSONL files (legacy sessions)
5. Performance testing with large sessions (500+ messages)

### Phase 4: Documentation
1. Update code comments explaining message source
2. Update `docs/api/endpoints/claude-sessions.md` with new behavior
3. Document JSONL path resolution logic
4. Add troubleshooting guide for message display issues

## File Summary

| File | Lines Changed | Complexity | Risk |
|------|--------------|------------|------|
| `claudetask/backend/app/main.py` | ~50-80 | MODERATE | LOW |
| `claudetask/frontend/src/components/sessions/TaskSessionsView.tsx` | 0 | NONE | NONE |

**Total Estimated Changes**: ~50-80 lines of backend code, 0 frontend changes

## Definition of Done Checklist

From `requirements.md`:

**Implementation Complete**:
- [ ] Backend reads messages from JSONL files
- [ ] `/api/projects/{project_id}/sessions` returns populated messages
- [ ] TaskSessionsView dialog displays messages correctly
- [ ] Message formatting matches Claude API structure

**Quality Verified**:
- [ ] Unit tests for JSONL parsing and edge cases
- [ ] Integration test: create session, verify messages appear
- [ ] Manual testing: open detail dialog, verify messages display
- [ ] Error scenarios tested (missing file, corrupted JSONL, empty session)

**Documentation Updated**:
- [ ] Code comments explain message source decision
- [ ] API documentation updated for endpoint changes
- [ ] Component documentation reflects new behavior
- [ ] Known limitations documented (if any)

**User Experience Validated**:
- [ ] Active sessions show recent messages
- [ ] Completed sessions show full history
- [ ] Empty sessions show appropriate message
- [ ] Tool use/results display correctly
- [ ] Performance acceptable for large sessions

## Success Metrics

- **Message Display Rate**: 100% of sessions with JSONL files show messages
- **Load Performance**: Session detail opens in < 1 second
- **Error Rate**: < 1% of session detail views fail to load
- **Code Reuse**: Leverage existing `claude_sessions_reader.py` patterns

## Risks & Mitigations

| Risk | Probability | Impact | Mitigation |
|------|------------|--------|------------|
| JSONL filename doesn't match `session.id` | MEDIUM | HIGH | Check both `id` and `session_id` fields, log findings |
| Large JSONL files slow down API | MEDIUM | MEDIUM | Implement message limiting (100 messages) |
| Path construction differs on Windows | LOW | MEDIUM | Use `os.sep` for cross-platform compatibility |
| Concurrent reads during active session | LOW | LOW | JSONL is append-only, reads are safe |

## Conclusion

This is a straightforward bug fix that requires backend-only changes. The frontend already has complete message rendering logic. By following the ClaudeCodeSessionsView pattern and reusing JSONL parsing logic, we can restore message display functionality with minimal code changes and low risk of regression.

**Estimated Effort**: 2-4 hours development + 1-2 hours testing = 1 development session
