# Acceptance Criteria: Session UI Improvements

**Task ID**: 14
**Date**: 2025-11-26

---

## Feature 1: Filter Project-Launched Processes

### AC-1.1: Process List Shows Only Project Sessions

**Given** the Sessions page Process Monitor is expanded
**When** the system fetches active Claude sessions
**Then** only processes launched from project tasks/embedded sessions are displayed
**And** system subprocesses (child processes, helper utilities) are excluded

**Test Steps**:
1. Navigate to `/sessions`
2. Expand "System Processes" accordion
3. Verify processes shown have project context (task_id, project_path)
4. Open terminal, run `ps aux | grep claude` to see all processes
5. Confirm UI shows subset of processes (only project-launched)

---

### AC-1.2: Filter Logic Uses Command Pattern

**Given** backend receives request for active sessions
**When** filtering processes from system process list
**Then** filter includes processes whose command contains project indicators:
- `--task-id` flag
- `--project-path` flag
- Embedded session launch pattern
**And** excludes processes without these indicators

**Test Steps**:
1. Start Claude session via TaskBoard ("Start Session" button)
2. Check process list includes new session
3. Start standalone Claude Code session (unrelated to project)
4. Verify standalone session NOT shown in process monitor
5. Check API response: `GET /api/claude-sessions/active-sessions`
6. Confirm response contains only filtered processes

---

### AC-1.3: Empty State When No Project Processes

**Given** no project-related Claude processes are running
**When** user expands Process Monitor
**Then** display message: "No active project sessions"
**And** do not show empty table or error state

**Test Steps**:
1. Stop all project Claude sessions
2. Expand Process Monitor
3. Verify "No active project sessions" message appears
4. Start a project session
5. Verify process appears and empty state disappears

---

### AC-1.4: Process Cards Display Correct Information

**Given** Process Monitor shows project sessions
**When** rendering process cards
**Then** each card displays:
- PID
- CPU usage (%)
- Memory usage (%)
- Project name or task ID
- Working directory
- Terminate button

**Test Steps**:
1. Launch 2-3 project sessions
2. Expand Process Monitor
3. Verify each card shows complete information
4. Compare PID/CPU/Memory with system `ps aux | grep claude`
5. Confirm values match system metrics

---

## Feature 2: Add Pagination to Claude Sessions

### AC-2.1: Sessions Display 20 Per Page by Default

**Given** a project has >20 Claude sessions
**When** user views session list
**Then** exactly 20 sessions appear on page 1
**And** pagination controls are visible at bottom

**Test Steps**:
1. Select project with 50+ sessions
2. Count sessions displayed on page 1
3. Verify count equals 20
4. Scroll to bottom
5. Verify pagination controls present

---

### AC-2.2: Pagination Controls Function Correctly

**Given** session list has multiple pages
**When** user clicks pagination controls
**Then** correct page loads with corresponding sessions

**Test Steps**:
1. Navigate to session list (50+ sessions)
2. Click "Next" button → Page 2 loads
3. Click page number "3" → Page 3 loads
4. Click "Previous" → Page 2 loads
5. Verify URL updates: `?page=2&size=20`
6. Refresh browser → Page 2 still displayed

---

### AC-2.3: Page Size Options Available

**Given** user wants to change page size
**When** user selects page size option (10, 20, 50, 100)
**Then** session list updates to show selected number of items
**And** pagination controls recalculate total pages

**Test Steps**:
1. View session list (default 20 per page)
2. Change page size to 50
3. Verify 50 sessions now displayed
4. Verify pagination shows fewer total pages
5. Change to 10 per page
6. Verify 10 sessions displayed, more pages available

---

### AC-2.4: Pagination Metadata Displayed

**Given** session list is paginated
**When** viewing any page
**Then** display "Page X of Y" or "Showing 21-40 of 150 sessions"
**And** metadata is accurate

**Test Steps**:
1. Navigate to session list with 75 sessions
2. Verify page 1 shows "Page 1 of 4" (20 per page)
3. Go to page 2
4. Verify "Page 2 of 4" or "Showing 21-40 of 75"
5. Check last page shows remaining sessions

---

### AC-2.5: Pagination Persists During Filtering

**Given** user is on page 2 of session list
**When** user applies search filter or tab filter
**Then** pagination resets to page 1 with filtered results
**And** pagination recalculates total pages for filtered set

**Test Steps**:
1. Navigate to page 3 of session list
2. Enter search query "error"
3. Verify results reset to page 1
4. Verify pagination shows pages for filtered results
5. Clear filter
6. Verify pagination returns to original state (page 1)

---

### AC-2.6: Backend Returns Pagination Metadata

**Given** frontend requests paginated sessions
**When** backend API endpoint called with `page` and `page_size` params
**Then** response includes:
```json
{
  "sessions": [...],
  "pagination": {
    "total_sessions": 150,
    "total_pages": 8,
    "current_page": 2,
    "page_size": 20
  }
}
```

**Test Steps**:
1. Open browser DevTools Network tab
2. Load session list
3. Inspect API response: `GET /api/claude-sessions/projects/{name}/sessions?page=1&page_size=20`
4. Verify response includes `pagination` object
5. Verify values are accurate

---

## Feature 3: Simplify Session View - Direct Message Display

### AC-3.1: Session Detail Opens Directly to Messages

**Given** user clicks on a session card
**When** session detail dialog opens
**Then** message list is immediately visible (no tabs to click)
**And** messages are fully loaded and scrollable

**Test Steps**:
1. Click any session card
2. Verify dialog opens
3. Verify messages appear immediately (no loading state)
4. Verify no tab navigation required
5. Scroll through messages
6. Close and reopen dialog → Same behavior

---

### AC-3.2: Compact Header Shows Session Metadata

**Given** session detail dialog is open
**When** viewing message list
**Then** compact header displays:
- Session ID
- Created timestamp
- Last activity timestamp
- Total message count

**Test Steps**:
1. Open session detail dialog
2. Verify header shows session ID (e.g., "Session: abc-123-def")
3. Verify timestamps displayed (e.g., "Created: Nov 26, 2025 10:30 AM")
4. Verify message count (e.g., "42 messages")
5. Confirm header is compact (single line or minimal height)

---

### AC-3.3: Advanced Details Collapsed by Default

**Given** session detail dialog is open
**When** user views messages
**Then** Tools, Timeline, and Errors sections are collapsed
**And** user can expand them via accordion or button

**Test Steps**:
1. Open session detail dialog
2. Verify Tools section not visible by default
3. Verify Timeline section not visible
4. Locate expand/collapse control (accordion or button)
5. Click to expand Tools → Tools section appears
6. Click to collapse → Tools section hides
7. Repeat for Timeline and Errors sections

---

### AC-3.4: Message List Takes Full Dialog Height

**Given** session detail dialog is open
**When** viewing messages
**Then** message list occupies maximum available vertical space
**And** scrollbar appears when content exceeds viewport

**Test Steps**:
1. Open session with 50+ messages
2. Verify message list fills dialog height
3. Verify scrollbar appears on right side
4. Scroll to bottom → Last message visible
5. Resize browser window
6. Verify message list adjusts height responsively

---

### AC-3.5: Message Formatting Maintained

**Given** session detail dialog shows messages
**When** viewing user and assistant messages
**Then** existing formatting is preserved:
- User messages: Blue theme, left-aligned
- Assistant messages: Green theme, left-aligned
- Tool use blocks: Info theme with syntax highlighting
- Tool result blocks: Success theme, scrollable

**Test Steps**:
1. Open session with varied message types
2. Verify user message has blue border and background
3. Verify Claude message has green styling
4. Check tool use block shows tool name and input
5. Check tool result block shows output
6. Confirm all visual styling matches original design

---

## Feature 4: Fix Empty Lines in Session Messages

### AC-4.1: Empty Lines Between Messages Removed

**Given** session detail dialog displays messages
**When** rendering message list
**Then** no empty lines appear between consecutive messages
**And** spacing between messages is exactly 1.5rem (or consistent value)

**Test Steps**:
1. Open session detail dialog
2. Inspect spacing between user message and Claude response
3. Verify no blank lines (extra `<br>`, `<div>`, or padding)
4. Measure gap between message bubbles (should be ~1.5rem)
5. Check DevTools Elements tab for unnecessary elements

---

### AC-4.2: Blank Content Blocks Filtered

**Given** message contains empty content blocks (e.g., `content: [""]`)
**When** rendering message
**Then** empty blocks are not rendered
**And** only content with actual text/data appears

**Test Steps**:
1. Find session with message containing empty blocks (inspect API response)
2. Open session detail
3. Verify empty blocks do not create blank spaces
4. Compare rendered message with API data
5. Confirm filtering logic removes `""` or `null` content

---

### AC-4.3: Whitespace Trimmed from Content

**Given** message content has leading/trailing whitespace
**When** rendering message text
**Then** whitespace is trimmed
**And** content starts cleanly without extra padding

**Test Steps**:
1. Inspect API response for message with `content: "  Hello world  "`
2. Open session detail
3. Verify rendered message shows "Hello world" (no leading/trailing spaces)
4. Check multiple messages
5. Confirm trimming applied consistently

---

### AC-4.4: Consecutive Newlines Reduced

**Given** message content contains multiple newlines (`\n\n\n`)
**When** rendering message
**Then** consecutive newlines reduced to maximum of 2 (`\n\n`)
**And** content maintains paragraph structure

**Test Steps**:
1. Find message with multiple consecutive newlines
2. Open session detail
3. Verify no large gaps within message content
4. Check paragraph breaks appear natural (max 1 blank line)
5. Confirm code blocks maintain internal formatting

---

### AC-4.5: Tool Blocks Maintain Internal Formatting

**Given** message contains tool use or tool result blocks
**When** rendering tool blocks
**Then** internal code/data formatting is preserved
**And** syntax highlighting (if applicable) remains intact
**And** scrollable areas work correctly

**Test Steps**:
1. Open session with tool use blocks (e.g., Bash commands)
2. Verify code indentation preserved
3. Check JSON formatting in tool inputs
4. Verify tool result output maintains structure
5. Test scrolling in long tool results

---

### AC-4.6: Fix Applied to All Components

**Given** multiple components display session messages
**When** rendering messages in:
- ClaudeCodeSessionsView
- ClaudeCodeSessions page
- ClaudeSessions page
**Then** empty line fix is applied consistently across all components

**Test Steps**:
1. Navigate to `/sessions/claude-code` tab
2. Open session detail → Verify no empty lines
3. Navigate to `/claude-sessions` page
4. Open session → Verify no empty lines
5. Check ClaudeCodeSessionsView (if separate route)
6. Confirm fix applied uniformly

---

### AC-4.7: Message Bubble Spacing Consistent

**Given** session detail displays messages
**When** viewing message bubbles
**Then** each bubble has consistent padding and margins:
- Internal padding: 1.5-2rem
- Bottom margin: 1.5rem
- No extra spacing around bubbles

**Test Steps**:
1. Open session detail
2. Inspect message bubble in DevTools
3. Verify `padding: 2rem` (or theme spacing)
4. Verify `marginBottom: 1.5rem`
5. Check spacing is identical for user and Claude messages

---

## Cross-Feature Testing

### CFT-1: All Features Work Together

**Given** all 4 features are implemented
**When** user navigates Sessions page
**Then**:
- Process monitor shows only project processes
- Session list displays 20 per page with pagination
- Clicking session opens directly to clean message view
- Messages have no empty lines

**Test Steps**:
1. Navigate to `/sessions`
2. Expand Process Monitor → Verify filtered processes
3. Select project with 50+ sessions
4. Verify pagination controls present
5. Click page 2 → Verify 20 sessions load
6. Click session → Verify direct message view
7. Verify messages are clean (no empty lines)

---

### CFT-2: Responsive Design Maintained

**Given** all UI changes implemented
**When** viewing on different screen sizes
**Then** all features work responsively:
- Process cards stack on mobile
- Pagination controls wrap on small screens
- Message dialog scales correctly
- Message bubbles remain readable

**Test Steps**:
1. Test on desktop (1920x1080)
2. Test on tablet (768x1024)
3. Test on mobile (375x667)
4. Verify all features function correctly
5. Check touch interactions on mobile

---

### CFT-3: Performance Acceptable

**Given** large session dataset (100+ sessions)
**When** user interacts with UI
**Then** performance remains acceptable:
- Page load <500ms
- Pagination change <200ms
- Session detail open <300ms
- No UI lag or freezing

**Test Steps**:
1. Load project with 100+ sessions
2. Use browser Performance tab
3. Measure page load time
4. Click pagination → Measure render time
5. Open session detail → Measure time to interactive
6. Verify all interactions feel smooth

---

**End of Acceptance Criteria**
