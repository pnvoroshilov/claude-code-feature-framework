# Requirements: Sessions Tab Consolidation

## Overview

Consolidate the two separate session pages ("Claude Sessions" and "Claude Code Sessions") into a unified "Sessions" page with internal sub-navigation, focusing on Claude Code sessions while simplifying the overall UX.

## User Stories

### US-01: Unified Sessions Page
**As a** user
**I want** to access both task sessions and Claude Code sessions from a single page
**So that** I have a centralized location for all session management

**Acceptance Criteria:**
- Single "Sessions" page accessible from main navigation
- Internal tab/sub-menu navigation to switch between session types
- URL routing maintains current view (e.g., `/sessions/claude-code`, `/sessions/tasks`)
- Smooth transitions between sub-views with no page reload

### US-02: Claude Code Sessions Priority
**As a** developer
**I want** Claude Code sessions to be the default/primary view
**So that** I can quickly access my most frequently used session type

**Acceptance Criteria:**
- Claude Code Sessions tab is the default view when navigating to /sessions
- More prominent placement in navigation hierarchy
- Primary action buttons focus on Claude Code session features
- Task Sessions remain accessible but are secondary

### US-03: Simplified Active Process Display
**As a** user
**I want** active process monitoring to be less prominent or hidden
**So that** I can focus on session content without visual clutter

**Acceptance Criteria:**
- Active Claude Code processes (CPU, memory, kill buttons) are hidden by default
- Optional "Show System Processes" toggle or collapsible section
- Process information only shown when explicitly requested
- Clean, minimal interface focused on session content

### US-04: Improved Session Navigation UX
**As a** user
**I want** an intuitive and clean interface for browsing sessions
**So that** I can find and access session information efficiently

**Acceptance Criteria:**
- Clear visual hierarchy between session types
- Consistent card-based layout across both views
- Search/filter functionality works across both session types
- Responsive design for mobile and desktop
- Loading states are smooth and non-intrusive

## Functional Requirements

### FR-01: Page Structure
- Single React component page at `/sessions`
- Material-UI Tabs component for sub-navigation
- Two tabs: "Claude Code Sessions" (default) and "Task Sessions"
- Shared header with unified refresh and action buttons
- Persistent state when switching between tabs

### FR-02: Data Management
- Maintain separate API calls for each session type
- Cache session data to avoid unnecessary re-fetching when switching tabs
- Auto-refresh capability with manual refresh button
- Real-time updates for active sessions (optional, configurable)

### FR-03: Active Process Control
- Active process monitoring moved to collapsible "System Processes" section
- Section collapsed by default
- Only shows Claude Code-related processes
- Kill session functionality retained but less prominent
- Process list updates every 5 seconds when expanded

### FR-04: Search and Filter
- Unified search bar that searches within active tab
- Filter options contextual to current tab:
  - Claude Code tab: Recent, Large, With Errors, Tool-Heavy
  - Task Sessions tab: Active, Completed, With Errors
- Search persists when switching tabs
- Clear filters button

## Non-Functional Requirements

### NFR-01: Performance
- Initial page load under 2 seconds
- Tab switching instantaneous (<100ms)
- No re-render of inactive tab content
- Lazy loading for session details

### NFR-02: Usability
- Keyboard navigation between tabs (arrow keys)
- Breadcrumb shows current view
- Color-coded session types (Claude Code: purple, Task: blue)
- Consistent spacing and alignment

### NFR-03: Compatibility
- Works in Chrome, Firefox, Safari, Edge (latest 2 versions)
- Responsive layout for screens 320px to 4K
- Maintains existing API compatibility
- No breaking changes to backend

### NFR-04: Accessibility
- ARIA labels for tabs and sections
- Keyboard-only navigation supported
- Screen reader compatible
- Color contrast meets WCAG AA standards

## Business Rules

### BR-01: Default View
- Claude Code Sessions tab is always the default landing view
- User's last active tab is NOT remembered (always defaults to Claude Code)

### BR-02: Process Visibility
- Active processes hidden by default to reduce clutter
- Process monitoring only available on Task Sessions tab
- Maximum 50 processes shown at once

### BR-03: Session Type Separation
- Task Sessions show embedded ClaudeTask database sessions
- Claude Code Sessions show native .jsonl file sessions
- No cross-contamination of data between types

## Definition of Done (DoD)

1. **Code Complete**
   - Single unified Sessions page component created
   - Both session types integrated with tab navigation
   - Active process section is collapsible and hidden by default
   - Search and filter work within each tab

2. **UI/UX**
   - Claude Code Sessions is the default view
   - Clean, minimal interface with reduced visual noise
   - Consistent styling between both tabs
   - Smooth transitions and animations

3. **Testing**
   - Manual testing confirms tab switching works
   - Search/filter functionality verified in both tabs
   - Process monitoring collapse/expand works
   - Responsive layout tested on mobile and desktop

4. **Documentation**
   - Component documentation updated in docs/components/
   - API endpoints remain unchanged and documented
   - User guide updated to reflect new unified interface

5. **Quality**
   - No console errors or warnings
   - TypeScript types are correct
   - Code follows existing patterns
   - Performance meets NFR-01 requirements

6. **Deployment Ready**
   - No breaking changes to existing functionality
   - All existing session features remain accessible
   - Backward compatible with current API
   - Ready for code review and PR

## Dependencies

- Existing ClaudeSessions.tsx component
- Existing ClaudeCodeSessions.tsx component
- Backend API endpoints (no changes required):
  - `/api/claude-sessions/projects`
  - `/api/claude-sessions/sessions/{session_id}`
  - `/api/claude-sessions/active-sessions`
- Material-UI Tabs component
- React Router for URL routing

## Assumptions

- Backend APIs remain unchanged
- Session data structures remain the same
- User authentication/authorization is unchanged
- Existing session features will be preserved
- No new API endpoints required

## Out of Scope

- Real-time WebSocket updates for sessions
- Session export functionality
- Advanced analytics dashboard
- Session comparison tools
- Collaborative session sharing
- Migration of existing session data structures
