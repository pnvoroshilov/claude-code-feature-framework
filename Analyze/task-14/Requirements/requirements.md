# Requirements Document: Session UI Improvements

**Task ID**: 14
**Task Title**: Сессии (Sessions UI Improvements)
**Type**: Feature Enhancement
**Priority**: Medium
**Date**: 2025-11-26

---

## 1. Overview

This task addresses four specific improvements to the Sessions UI in the ClaudeTask framework to enhance usability, performance, and presentation of session data.

### Context

The Sessions page (`/sessions`) provides a unified interface for monitoring Claude Code sessions and task-based sessions. It displays:
- Two tabs: "Claude Code Sessions" and "Task Sessions"
- System Process Monitor (collapsible accordion)
- Session lists with detailed analytics
- Session details dialogs with messages, tools, and timeline tabs

**Current Issues**:
1. Process monitor shows ALL Claude subprocesses (including system processes)
2. No pagination for Claude sessions list (performance issues with large datasets)
3. Session detail dialog has unnecessary tabs before showing messages
4. Empty lines appear in session messages (display bug)

---

## 2. User Stories

### US-1: Filter Project-Launched Processes

**As a** developer monitoring active sessions
**I want to** see only Claude processes launched from projects (not system subprocesses)
**So that** I can focus on relevant processes without clutter

**Acceptance Criteria**:
- Only processes launched via project tasks/embedded sessions appear in monitor
- System subprocesses (child processes, helper processes) are excluded
- Process filtering is based on command pattern or process metadata
- Empty state shows "No active project sessions" when all processes are filtered

---

### US-2: Add Pagination to Claude Sessions

**As a** user reviewing session history
**I want to** navigate sessions with pagination controls
**So that** the interface remains responsive with large session counts

**Acceptance Criteria**:
- Sessions display 20 items per page by default
- Pagination controls show: [Previous] [1] [2] [3] ... [Next]
- Page number displays current/total (e.g., "Page 2 of 15")
- Pagination state persists during filtering/searching
- User can optionally change page size (10, 20, 50, 100 items)

---

### US-3: Simplify Session View - Direct Message Display

**As a** user reviewing session details
**I want to** see messages immediately when clicking a session
**So that** I can quickly review conversations without extra navigation

**Acceptance Criteria**:
- Clicking a session opens dialog directly to Messages view (no tabs)
- Message list appears immediately without additional clicks
- Optional: Add compact header with session metadata (ID, timestamp, count)
- Remove or hide Info/Tools/Timeline tabs by default
- Advanced details (tools, timeline) accessible via collapsed sections or secondary navigation

---

### US-4: Fix Empty Lines in Session Messages

**As a** user reading session messages
**I want to** see clean message formatting without empty lines
**So that** messages are readable and professional

**Acceptance Criteria**:
- Empty lines between messages are removed
- Blank content blocks are filtered out during rendering
- Proper spacing between user and assistant messages (1-2 lines max)
- Tool use/result blocks maintain internal formatting but remove excess spacing
- Message bubbles have consistent padding and margins

---

## 3. Functional Requirements

### FR-1: Process Filtering Logic

**Description**: Filter active Claude processes to show only project-launched sessions

**Requirements**:
- **FR-1.1**: Backend API (`/api/claude-sessions/active-sessions`) adds filtering parameter
- **FR-1.2**: Process filtering distinguishes project processes from system subprocesses
- **FR-1.3**: Filter criteria: command pattern matching (e.g., contains task_id or project_path)
- **FR-1.4**: Frontend receives only filtered processes from API
- **FR-1.5**: Empty state message when no project processes are active

**Related Files**:
- `claudetask/backend/app/api/claude_sessions.py` (endpoint)
- `claudetask/frontend/src/pages/Sessions.tsx` (process monitor)

---

### FR-2: Session Pagination

**Description**: Implement pagination for Claude sessions list

**Requirements**:
- **FR-2.1**: Backend supports pagination parameters: `page`, `page_size`, `offset`
- **FR-2.2**: Backend returns pagination metadata: `total_sessions`, `total_pages`, `current_page`
- **FR-2.3**: Frontend displays pagination controls (MUI Pagination component)
- **FR-2.4**: Default page size: 20 sessions
- **FR-2.5**: Page size options: 10, 20, 50, 100 (dropdown or button group)
- **FR-2.6**: Pagination state preserved during search/filter operations
- **FR-2.7**: URL query params reflect current page (`?page=2&size=20`)

**Related Files**:
- `claudetask/backend/app/api/claude_sessions.py` (sessions endpoint)
- `claudetask/frontend/src/components/sessions/ClaudeCodeSessionsView.tsx` (session list)
- `claudetask/frontend/src/pages/ClaudeCodeSessions.tsx` (session list)

---

### FR-3: Direct Message Display

**Description**: Simplify session detail view to show messages first

**Requirements**:
- **FR-3.1**: Remove tab navigation from session detail dialog
- **FR-3.2**: Display message list immediately on dialog open
- **FR-3.3**: Add compact header with session metadata (ID, timestamps, message count)
- **FR-3.4**: Optional: Collapse advanced details (Tools, Timeline, Errors) into accordion sections
- **FR-3.5**: Message list takes full dialog height (minus header)
- **FR-3.6**: Maintain existing message formatting (user/assistant bubbles, tool displays)

**Related Files**:
- `claudetask/frontend/src/components/sessions/ClaudeCodeSessionsView.tsx` (detail dialog)
- `claudetask/frontend/src/pages/ClaudeCodeSessions.tsx` (detail dialog)

---

### FR-4: Empty Line Removal

**Description**: Fix message rendering to remove empty lines

**Requirements**:
- **FR-4.1**: Filter out empty content blocks before rendering
- **FR-4.2**: Trim whitespace from message content
- **FR-4.3**: Remove consecutive newlines (replace `\n\n+` with single `\n`)
- **FR-4.4**: Ensure consistent spacing between message bubbles (e.g., `marginBottom: 1.5`)
- **FR-4.5**: Tool use/result blocks maintain internal formatting (preserve code structure)
- **FR-4.6**: Apply fixes to all message display components (ClaudeCodeSessionsView, ClaudeSessions)

**Related Files**:
- `claudetask/frontend/src/components/sessions/ClaudeCodeSessionsView.tsx`
- `claudetask/frontend/src/pages/ClaudeCodeSessions.tsx`
- `claudetask/frontend/src/pages/ClaudeSessions.tsx`

---

## 4. Definition of Done (DoD)

### Development Complete
- [ ] All 4 functional requirements implemented
- [ ] Process filtering logic correctly identifies project vs system processes
- [ ] Pagination controls display and function correctly
- [ ] Session detail dialog opens directly to messages view
- [ ] Empty lines removed from message rendering
- [ ] Code follows existing project patterns and conventions
- [ ] No console errors or warnings

### Testing Complete
- [ ] Manual testing confirms process filter shows only project sessions
- [ ] Pagination tested with small (<20), medium (20-100), and large (>100) session counts
- [ ] Session detail dialog verified across multiple sessions
- [ ] Message formatting tested with various content types (text, tools, errors)
- [ ] Empty line fix verified across all message display components
- [ ] Responsive design tested on desktop, tablet, mobile viewports

### Documentation Updated
- [ ] Update `docs/components/Sessions.md` with new filtering behavior
- [ ] Update `docs/components/ClaudeCodeSessions.md` with pagination details
- [ ] Update `docs/components/ClaudeSessions.md` with simplified view
- [ ] Add API documentation for new pagination parameters
- [ ] Update user-facing help text if applicable

### Code Review Ready
- [ ] Pull request created with clear description
- [ ] All changes committed to feature branch
- [ ] Conflicts resolved with main branch
- [ ] Screenshots/video demo of UI changes attached to PR

---

## 5. Non-Functional Requirements

### Performance
- Pagination improves load time for large session lists (target: <500ms)
- Process filtering reduces API response size (target: <100KB)
- Message rendering optimizations prevent UI lag with long conversations

### Usability
- Pagination controls are intuitive and accessible
- Direct message view reduces clicks by 1-2 per session review
- Clean message formatting improves readability

### Compatibility
- Works with existing ClaudeCodeSessionsView and ClaudeSessions components
- Maintains backward compatibility with session data format
- Responsive design on all supported viewports (desktop, tablet, mobile)

### Maintainability
- Filtering logic reusable across components
- Pagination logic follows Material-UI patterns
- Message formatting extracted to reusable helper functions

---

## 6. Out of Scope

The following are explicitly **NOT** part of this task:

- Changing session data storage format or backend database schema
- Adding new session metadata fields
- Implementing WebSocket real-time updates
- Adding export/import functionality
- Changing overall Sessions page layout or navigation structure
- Adding authentication or access control to sessions
- Performance optimizations beyond pagination (e.g., virtual scrolling)

---

## 7. Success Metrics

### Quantitative
- Process monitor shows 50-80% fewer processes (excluding system subprocesses)
- Session load time reduced by 60% for projects with >100 sessions
- User clicks to view messages reduced from 3 to 1

### Qualitative
- Developers report cleaner process list
- Users find session review faster and more intuitive
- Message readability improved (no distracting empty lines)

---

## 8. Related Tasks and Dependencies

### Active Task Overlap
- **Task #15** (Session Task Details): May affect same components - coordinate to avoid conflicts

### Dependencies
- Material-UI v5 (Pagination component)
- Existing session API endpoints
- Claude session file parser

### Blocked By
- None (all prerequisites met)

---

## 9. Implementation Notes

### Process Filtering Approach
Consider filtering by:
1. Command pattern (contains `--task-id`, `--project-path`)
2. Parent process check (only top-level Claude processes)
3. Environment variables (project-specific vars)

### Pagination Strategy
- Backend: Use SQLAlchemy `.limit()` and `.offset()` for database queries
- Frontend: Material-UI `<Pagination>` component with state management

### Message Simplification
- Remove Tabs component, replace with single scrollable message list
- Collapse advanced details into `<Accordion>` sections at bottom

### Empty Line Fix
```typescript
// Example filtering logic
const cleanContent = (content: string) => {
  return content
    .trim()
    .replace(/\n{3,}/g, '\n\n') // Max 2 consecutive newlines
    .replace(/^\s*\n/gm, ''); // Remove empty lines at start
};
```

---

**End of Requirements Document**
