# Acceptance Criteria: Task #15 - Session Task Details Fix

**Version**: 1.0
**Date**: 2025-11-26
**Task**: Session Task Details
**Complexity**: MODERATE

## Overview

This document defines specific, testable acceptance criteria for resolving the Session Task Details message display issue. Each criterion must be verified before the task can be marked as complete.

## Feature-Level Acceptance Criteria

### AC-1: Session Detail Dialog Opens Successfully
**Given** a task session exists in the database
**When** user clicks the "View Details" icon/button on the session
**Then** the session detail dialog opens within 1 second
**And** all tabs (Overview, Messages, Tools Used, Terminal Output) are accessible

**Verification Steps**:
1. Navigate to Sessions page → Task Sessions tab
2. Locate any session in the list
3. Click the history/details icon
4. Verify dialog opens promptly
5. Click through all tabs to ensure no errors

**Pass Criteria**: Dialog opens without errors, all tabs render

---

### AC-2: Messages Display for Active Sessions
**Given** an active Claude Code session exists with conversation history
**When** user opens the session detail dialog and navigates to Messages tab
**Then** the messages tab displays at least the recent messages from the session
**And** both user prompts and Claude responses are visible
**And** messages are formatted correctly with proper styling

**Verification Steps**:
1. Start a Claude Code session via `/start-develop {task_id}`
2. Have a conversation with at least 5 exchanges
3. Open Sessions page → Task Sessions
4. Find the active session in the list
5. Open detail dialog → Messages tab
6. Verify messages appear with:
   - User messages (blue theme, 👤 avatar)
   - Claude messages (green theme, 🤖 avatar)
   - Proper timestamps
   - Tool use blocks (if any)
   - Tool result blocks (if any)

**Pass Criteria**: All messages visible, correctly formatted, no "No messages yet" error

---

### AC-3: Messages Display for Completed Sessions
**Given** a completed Claude Code session with conversation history
**When** user opens the session detail dialog and navigates to Messages tab
**Then** the full conversation history is displayed
**And** all messages are readable and properly formatted
**And** session statistics reflect actual message count

**Verification Steps**:
1. Complete an existing session via `/PR {task_id}` or `/merge {task_id}`
2. Open Sessions page → Task Sessions
3. Find the completed session
4. Open detail dialog → Messages tab
5. Verify full conversation history appears
6. Check Overview tab: message count matches actual count

**Pass Criteria**: Complete history visible, statistics accurate

---

### AC-4: Empty Sessions Show Appropriate Message
**Given** a session has been created but no conversation has occurred
**When** user opens the session detail dialog and navigates to Messages tab
**Then** the UI displays "No messages yet" or similar appropriate message
**And** no errors appear in browser console

**Verification Steps**:
1. Create a new task session in "idle" status (not yet launched)
2. Open detail dialog → Messages tab
3. Verify empty state message displays
4. Check browser console for errors (should be none)

**Pass Criteria**: Appropriate empty state, no errors

---

### AC-5: Tool Use and Results Display Correctly
**Given** a session contains messages with tool invocations
**When** user views these messages in the Messages tab
**Then** tool use blocks are highlighted and formatted distinctly
**And** tool result blocks show output clearly
**And** JSON content is properly formatted and readable

**Verification Steps**:
1. Find or create a session where Claude used tools (Read, Write, Bash, etc.)
2. Open detail dialog → Messages tab
3. Locate messages with tool_use blocks
4. Verify:
   - Tool name displayed (e.g., "🔧 Tool: Read")
   - Tool input JSON formatted (indented, readable)
   - Tool result content displayed
   - Scrollable if result is long (max 400px height)
5. Check styling matches ClaudeCodeSessionsView reference

**Pass Criteria**: Tool blocks distinct, readable, properly styled

---

### AC-6: Message Content Parsing Handles Multiple Formats
**Given** messages may have different content structures (string, array, object)
**When** the UI renders these messages
**Then** all formats display correctly without errors
**And** no "undefined" or "[object Object]" appears

**Test Cases**:
- Simple string content: `"Hello, Claude"`
- Array content: `[{type: "text", text: "Hello"}]`
- Object with text property: `{text: "Hello"}`
- Mixed content with tool_use and text blocks
- Empty or null content

**Verification Steps**:
1. Review JSONL file for various content formats
2. Open session detail dialog
3. Scroll through all messages
4. Verify each format renders appropriately
5. Check for console errors

**Pass Criteria**: All formats render, no errors or garbled text

---

### AC-7: Large Sessions Perform Acceptably
**Given** a session contains 100+ messages
**When** user opens the session detail dialog
**Then** the dialog loads within 2 seconds
**And** scrolling through messages is smooth (no lag)
**And** memory usage remains reasonable

**Verification Steps**:
1. Identify or create a session with 100+ messages
2. Open detail dialog and measure load time
3. Navigate to Messages tab
4. Scroll through entire list
5. Monitor browser DevTools Performance tab
6. Check memory usage in DevTools Memory tab

**Pass Criteria**: Load < 2s, smooth scrolling, no memory leaks

---

### AC-8: Error Handling for Missing JSONL Files
**Given** a session record exists in database but JSONL file is missing
**When** user opens the session detail dialog
**Then** the UI displays a friendly message like "Messages unavailable"
**And** no server errors or crashes occur
**And** other session details (Overview, Tools Used) still display

**Verification Steps**:
1. Identify a session in database
2. Rename or move the corresponding `.jsonl` file
3. Open detail dialog
4. Verify graceful degradation:
   - Overview tab still works
   - Messages tab shows "unavailable" message
   - No HTTP 500 errors
   - No frontend crashes
5. Restore JSONL file afterward

**Pass Criteria**: Graceful fallback, no crashes, informative message

---

### AC-9: Backend API Returns Messages
**Given** a valid session ID and project ID
**When** frontend calls `GET /api/projects/{project_id}/sessions`
**Then** the response includes a populated `messages` array for sessions with JSONL files
**And** the API responds within 500ms for typical sessions

**Verification Steps**:
1. Open browser DevTools → Network tab
2. Navigate to Sessions page → Task Sessions
3. Observe API call to `/api/projects/{project_id}/sessions`
4. Verify response JSON includes:
   ```json
   {
     "messages": [
       {"role": "user", "content": "..."},
       {"role": "assistant", "content": "..."}
     ]
   }
   ```
5. Check response time < 500ms

**Pass Criteria**: API returns messages, acceptable performance

---

### AC-10: Session Statistics Update
**Given** messages are now loaded from JSONL files
**When** user views session Overview tab
**Then** message count reflects actual number of messages
**And** tool usage statistics are accurate
**And** session duration is correctly calculated

**Verification Steps**:
1. Open a session detail dialog
2. Count messages manually in Messages tab
3. Navigate to Overview tab
4. Verify:
   - "Total Messages" matches count
   - "Tools Used" count matches actual tool invocations
   - Session duration is reasonable
5. Compare with JSONL file directly if needed

**Pass Criteria**: Statistics accurate, reflect actual session content

---

## API-Level Acceptance Criteria

### AC-API-1: Endpoint Enhancement
**Endpoint**: `GET /api/projects/{project_id}/sessions`

**Request**:
```http
GET /api/projects/abc-123/sessions HTTP/1.1
```

**Expected Response**:
```json
[
  {
    "id": "session-001",
    "task_id": 15,
    "task_title": "Session Task Details",
    "status": "active",
    "working_dir": "/path/to/project",
    "messages": [
      {
        "role": "user",
        "timestamp": "2025-11-26T10:30:00Z",
        "content": "Start working on task"
      },
      {
        "role": "assistant",
        "timestamp": "2025-11-26T10:30:05Z",
        "content": [
          {"type": "text", "text": "I'll help with that task."},
          {"type": "tool_use", "name": "Read", "input": {...}}
        ]
      }
    ],
    "created_at": "2025-11-26T10:29:00Z"
  }
]
```

**Acceptance**:
- ✅ Response includes `messages` array
- ✅ Messages have `role`, `content`, `timestamp`
- ✅ Content supports string and array formats
- ✅ HTTP 200 status code
- ✅ Response time < 500ms

---

### AC-API-2: JSONL Parsing Logic
**Backend Code**: `claudetask/backend/app/main.py` (or service layer)

**Expected Behavior**:
```python
# Pseudo-code
def get_session_messages(session):
    jsonl_path = f"{session.working_dir}/.claude/sessions/{session.id}.jsonl"

    if os.path.exists(jsonl_path):
        messages = parse_jsonl(jsonl_path)
        return messages
    elif session.messages:  # Fallback to database
        return session.messages
    else:
        return []  # Empty session
```

**Acceptance**:
- ✅ Reads from correct JSONL path
- ✅ Falls back to database if JSONL missing
- ✅ Returns empty array if both missing
- ✅ Handles parse errors gracefully
- ✅ Logs errors appropriately

---

### AC-API-3: Error Handling
**Scenarios**:
1. **JSONL file not found**
   - Expected: Return `messages: []`, log warning
   - HTTP Status: 200 (not an error condition)

2. **JSONL file corrupted/invalid JSON**
   - Expected: Log error, return `messages: []`
   - HTTP Status: 200 (graceful degradation)

3. **Path traversal attempt**
   - Expected: Reject request, validate paths
   - HTTP Status: 400 Bad Request

4. **Project not found**
   - Expected: Standard project not found error
   - HTTP Status: 404 Not Found

**Acceptance**: All error scenarios handled without crashes

---

## Frontend-Level Acceptance Criteria

### AC-UI-1: Message Rendering Logic
**Component**: `TaskSessionsView.tsx`

**Expected Behavior**:
```typescript
// Messages tab content
{selectedSession.messages?.length ? (
  selectedSession.messages.map((msg, idx) => (
    <MessageBubble key={idx} message={msg} />
  ))
) : (
  <Typography>No messages yet</Typography>
)}
```

**Acceptance**:
- ✅ Renders messages when available
- ✅ Shows empty state when no messages
- ✅ Handles null/undefined messages array
- ✅ Applies correct styling per message role
- ✅ Parses content structure correctly

---

### AC-UI-2: Content Type Handling
**Test Matrix**:

| Content Type | Input | Expected Output |
|--------------|-------|-----------------|
| String | `"Hello"` | Plain text: "Hello" |
| Text Block | `{type:"text", text:"Hello"}` | Plain text: "Hello" |
| Tool Use | `{type:"tool_use", name:"Read", input:{...}}` | Highlighted box with tool name and input |
| Tool Result | `{type:"tool_result", content:"Success"}` | Green box with result content |
| Array | `[{type:"text", text:"Hi"}, {type:"tool_use",...}]` | Multiple blocks stacked |
| Object | `{text: "Hello"}` | Plain text: "Hello" |
| Null/Empty | `null` or `""` | "(empty)" or skip |

**Acceptance**: All content types render correctly per matrix

---

### AC-UI-3: Styling Consistency
**Reference**: `ClaudeCodeSessionsView.tsx` (existing implementation)

**Requirements**:
- User messages: Blue theme (`theme.palette.primary.main`)
- Claude messages: Green theme (`theme.palette.success.main`)
- Tool use blocks: Info theme (`theme.palette.info.main`)
- Tool results: Success theme, max height 400px, scrollable
- Font: Monospace for code/tool content
- Spacing: Consistent padding and margins

**Acceptance**: Matches reference implementation styling

---

## Integration Test Scenarios

### Scenario 1: New Session Workflow
1. Create new task
2. Run `/start-develop {task_id}`
3. Have conversation with Claude (5+ exchanges)
4. Use at least 2 different tools (Read, Write)
5. Open Sessions page → Task Sessions
6. Verify session appears in list
7. Open detail dialog
8. **Verify**: Messages display correctly, tools highlighted

**Pass**: End-to-end workflow works seamlessly

---

### Scenario 2: Session Completion
1. Start with active session (from Scenario 1)
2. Run `/PR {task_id}` to complete task
3. Session status changes to "completed"
4. Refresh Sessions page
5. Open completed session detail dialog
6. **Verify**: Full message history preserved, all data intact

**Pass**: Completion doesn't lose message data

---

### Scenario 3: Multiple Concurrent Sessions
1. Create 3 different tasks
2. Start sessions for all 3 tasks
3. Interleave conversations across sessions
4. Open Sessions page
5. Verify all 3 sessions listed
6. Open detail dialogs for each
7. **Verify**: Messages don't mix between sessions, each shows correct data

**Pass**: Session isolation maintained

---

### Scenario 4: Legacy Session Compatibility
1. Identify old session (created before this fix)
2. Verify JSONL file may be missing
3. Open detail dialog
4. **Verify**: UI doesn't crash, shows "unavailable" gracefully
5. Overview and other tabs still functional

**Pass**: Backward compatibility maintained

---

## Performance Acceptance Criteria

### Perf-1: API Response Time
| Session Size | Target Response Time |
|--------------|---------------------|
| 10 messages | < 100ms |
| 50 messages | < 250ms |
| 100 messages | < 500ms |
| 500 messages | < 2000ms |

**Measurement**: Chrome DevTools Network tab, average of 5 requests

---

### Perf-2: Frontend Rendering
| Session Size | Target Render Time |
|--------------|-------------------|
| 10 messages | < 50ms |
| 50 messages | < 150ms |
| 100 messages | < 300ms |
| 500 messages | < 1000ms |

**Measurement**: Chrome DevTools Performance profiler, React Profiler

---

### Perf-3: Memory Usage
- Initial load: < 10MB increase
- After viewing 10 sessions: < 50MB increase
- No memory leaks (heap stable after closing dialogs)

**Measurement**: Chrome DevTools Memory profiler

---

## Security Acceptance Criteria

### Sec-1: Path Validation
**Given** malicious user attempts path traversal
**When** API receives request with `..` or absolute paths
**Then** request is rejected or sanitized
**And** only project-scoped files are accessible

**Test Cases**:
- `/../../../etc/passwd` → Rejected
- Absolute path outside project → Rejected
- Relative path within project → Allowed

---

### Sec-2: Project Scope Enforcement
**Given** multiple projects exist
**When** user requests sessions for project A
**Then** only project A sessions are returned
**And** project B sessions are never exposed

**Test**: Cross-project access attempt returns empty or 403

---

## Accessibility Acceptance Criteria

### A11y-1: Keyboard Navigation
- ✅ Tab key navigates through dialog tabs
- ✅ Enter key opens session details
- ✅ Escape key closes dialog
- ✅ Arrow keys scroll messages

---

### A11y-2: Screen Reader Support
- ✅ ARIA labels present on all interactive elements
- ✅ Message roles announced ("User message", "Claude response")
- ✅ Empty state announced clearly
- ✅ Tool use/results described meaningfully

---

## Documentation Acceptance Criteria

### Doc-1: Code Comments
- ✅ Message source decision documented in code
- ✅ JSONL path construction explained
- ✅ Fallback logic commented
- ✅ Error handling rationale noted

---

### Doc-2: API Documentation
- ✅ Endpoint updated in `docs/api/endpoints/claude-sessions.md`
- ✅ Response format includes messages structure
- ✅ Examples show new message format

---

### Doc-3: Component Documentation
- ✅ `docs/components/Sessions.md` reflects new behavior
- ✅ TaskSessionsView behavior documented
- ✅ Known limitations listed

---

## Definition of Done Checklist

- [ ] All Feature-Level AC (AC-1 through AC-10) pass
- [ ] All API-Level AC (AC-API-1 through AC-API-3) pass
- [ ] All Frontend-Level AC (AC-UI-1 through AC-UI-3) pass
- [ ] All Integration Scenarios (1-4) pass
- [ ] Performance criteria met (Perf-1, Perf-2, Perf-3)
- [ ] Security criteria met (Sec-1, Sec-2)
- [ ] Accessibility criteria met (A11y-1, A11y-2)
- [ ] Documentation updated (Doc-1, Doc-2, Doc-3)
- [ ] Code reviewed and approved
- [ ] Manual testing completed by QA or peer
- [ ] No new console errors or warnings
- [ ] Backward compatibility verified

---

## Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2025-11-26 | Requirements Analyst | Initial acceptance criteria |
