# Acceptance Criteria: Sessions Tab Consolidation

## US-01: Unified Sessions Page

### AC-01.1: Single Entry Point
**Given** I am on the main navigation menu
**When** I look for session management
**Then** I see a single "Sessions" navigation item (not two separate items)

### AC-01.2: Internal Navigation
**Given** I am on the Sessions page
**When** I view the page
**Then** I see two tabs: "Claude Code Sessions" and "Task Sessions"

### AC-01.3: Tab Switching
**Given** I am viewing one session type
**When** I click on the other tab
**Then** the content switches without page reload
**And** the URL updates to reflect the current tab

### AC-01.4: URL Routing
**Given** I navigate to `/sessions/claude-code`
**When** the page loads
**Then** the Claude Code Sessions tab is active
**And** Claude Code session content is displayed

**Given** I navigate to `/sessions/tasks`
**When** the page loads
**Then** the Task Sessions tab is active
**And** Task session content is displayed

### AC-01.5: Direct URL Access
**Given** I bookmark `/sessions/tasks`
**When** I visit the bookmark
**Then** the page opens directly to Task Sessions tab

---

## US-02: Claude Code Sessions Priority

### AC-02.1: Default View
**Given** I navigate to `/sessions` or `/sessions/` without specifying a tab
**When** the page loads
**Then** the Claude Code Sessions tab is active by default
**And** Claude Code sessions are displayed

### AC-02.2: Tab Order
**Given** I am on the Sessions page
**When** I view the tab navigation
**Then** "Claude Code Sessions" tab appears first (leftmost)
**And** "Task Sessions" tab appears second

### AC-02.3: Primary Actions
**Given** I am viewing Claude Code Sessions tab
**When** I look at the page header
**Then** primary action buttons (Refresh, Filters) are visible and prominent
**And** actions are optimized for Claude Code workflows

### AC-02.4: Visual Prominence
**Given** I am on the Sessions page
**When** I view the layout
**Then** Claude Code Sessions content has equal or greater visual weight
**And** statistics/cards emphasize Claude Code metrics

---

## US-03: Simplified Active Process Display

### AC-03.1: Hidden by Default
**Given** I navigate to the Sessions page (any tab)
**When** the page loads
**Then** the active process monitoring section is collapsed/hidden
**And** CPU/memory metrics are not visible

### AC-03.2: Toggle Visibility
**Given** active process section is hidden
**When** I click "Show System Processes" button or expand control
**Then** the process monitoring section expands
**And** I see active Claude processes with CPU, memory, PID

### AC-03.3: Collapse Functionality
**Given** active process section is expanded
**When** I click "Hide System Processes" or collapse control
**Then** the section collapses
**And** process information is hidden from view

### AC-03.4: Process Actions
**Given** active process section is expanded
**When** I view an active process
**Then** I can see kill/terminate button
**And** the button is styled less prominently (secondary or text button)

### AC-03.5: Only Claude Code Processes
**Given** active process section is expanded
**When** I view the process list
**Then** only Claude Code-related processes are shown
**And** other system processes are filtered out

---

## US-04: Improved Session Navigation UX

### AC-04.1: Visual Hierarchy
**Given** I am on the Sessions page
**When** I view the layout
**Then** header > tabs > content hierarchy is clear
**And** spacing and typography guide my eye naturally

### AC-04.2: Consistent Cards
**Given** I switch between tabs
**When** I view session lists
**Then** both tabs use consistent card-based layouts
**And** session cards have similar structure and styling

### AC-04.3: Search Functionality
**Given** I am on any tab
**When** I type in the search bar
**Then** sessions are filtered in real-time
**And** search only affects the current tab's sessions

### AC-04.4: Filter Options
**Given** I am on Claude Code Sessions tab
**When** I view filter options
**Then** I see: All, Recent, Large, With Errors, Tool-Heavy

**Given** I am on Task Sessions tab
**When** I view filter options
**Then** I see: All, Active, Completed, With Errors

### AC-04.5: Responsive Design
**Given** I view the page on mobile (320px-767px)
**When** I observe the layout
**Then** tabs stack vertically or use scroll
**And** session cards display in single column
**And** all functionality remains accessible

**Given** I view the page on desktop (1024px+)
**When** I observe the layout
**Then** tabs display horizontally
**And** session cards display in grid (2-3 columns)
**And** content uses available space efficiently

### AC-04.6: Loading States
**Given** session data is being fetched
**When** I view the page
**Then** I see skeleton loaders or loading indicators
**And** the page layout remains stable (no jumping)

---

## Functional Requirements Acceptance Criteria

### AC-FR-01: Page Structure

**Given** the Sessions page component exists
**When** I inspect the code
**Then** I find a single React component at `/pages/Sessions.tsx` or similar
**And** Material-UI Tabs component is used for navigation
**And** Two Tab panels exist: one for Claude Code, one for Tasks

### AC-FR-02: Data Management

**Given** I switch from Claude Code tab to Task Sessions tab
**When** I return to Claude Code tab
**Then** the previously loaded session data is still visible (cached)
**And** no unnecessary API refetch occurs
**And** data is only refreshed when I click Refresh button

### AC-FR-03: Active Process Control

**Given** active process section is expanded
**When** I view the process list
**Then** it updates every 5 seconds automatically
**And** I can manually refresh with a button

**Given** active process section is collapsed
**When** I observe the page
**Then** no automatic refresh requests occur for processes
**And** API is not polled unnecessarily

### AC-FR-04: Search and Filter

**Given** I enter search term "authentication"
**When** I am on Claude Code Sessions tab
**Then** only Claude Code sessions matching "authentication" are shown

**Given** I switch to Task Sessions tab with search active
**When** I view the Task Sessions
**Then** the same search term applies to Task Sessions
**And** results are filtered accordingly

**Given** I have filters applied
**When** I click "Clear Filters" button
**Then** all filters reset to default (All)
**And** full session list is displayed

---

## Non-Functional Requirements Acceptance Criteria

### AC-NFR-01: Performance

**Given** I navigate to `/sessions` with cold cache
**When** I measure page load time
**Then** the page is interactive within 2 seconds
**And** Claude Code sessions list appears within 1 second

**Given** I am viewing Claude Code Sessions tab
**When** I click to switch to Task Sessions tab
**Then** the transition completes in under 100ms
**And** there is no visible lag or stutter

### AC-NFR-02: Usability

**Given** I am on the Sessions page
**When** I press Tab key repeatedly
**Then** focus cycles through all interactive elements
**And** tab selection can be changed with arrow keys

**Given** I view the page breadcrumb
**When** I am on Task Sessions tab
**Then** breadcrumb shows "Sessions > Task Sessions"

**Given** I view Claude Code Sessions
**When** I observe session cards
**Then** they use purple accent color (#6366f1)

**Given** I view Task Sessions
**When** I observe session cards
**Then** they use blue accent color (theme.palette.primary.main)

### AC-NFR-03: Compatibility

**Test in each browser:**
- Chrome (latest 2 versions)
- Firefox (latest 2 versions)
- Safari (latest 2 versions)
- Edge (latest 2 versions)

**Given** I open the Sessions page in [browser]
**When** I interact with all features
**Then** everything works without errors
**And** layout displays correctly

**Given** I use screen widths: 320px, 768px, 1024px, 1920px, 3840px
**When** I view the Sessions page
**Then** the layout adapts appropriately
**And** no horizontal scrolling occurs (except content areas)
**And** all buttons and controls remain accessible

### AC-NFR-04: Accessibility

**Given** I use screen reader (NVDA, JAWS, or VoiceOver)
**When** I navigate the Sessions page
**Then** all tabs are announced correctly
**And** session cards have descriptive labels
**And** I can navigate and activate all controls

**Given** I use keyboard only (no mouse)
**When** I navigate the entire page
**Then** all features are accessible
**And** focus indicators are visible
**And** tab order is logical

**Given** I test color contrast
**When** I use a contrast checker tool
**Then** all text meets WCAG AA standards (4.5:1 for normal text)
**And** interactive elements have sufficient contrast

---

## Business Rules Acceptance Criteria

### AC-BR-01: Default View

**Given** I access `/sessions` multiple times in a session
**When** I navigate to the page
**Then** it ALWAYS defaults to Claude Code Sessions tab
**And** it does NOT remember my last active tab

### AC-BR-02: Process Visibility

**Given** active process section is expanded
**When** more than 50 processes exist
**Then** only the first 50 are displayed
**And** a message indicates "Showing 50 of X processes"

**Given** I am on Task Sessions tab
**When** I expand active processes
**Then** I see process monitoring section

**Given** I am on Claude Code Sessions tab
**When** I look for process monitoring
**Then** the option to show processes is available
**And** it shows the same data as Task Sessions tab

### AC-BR-03: Session Type Separation

**Given** I view Claude Code Sessions
**When** I inspect session data
**Then** all sessions come from .jsonl files
**And** no ClaudeTask database sessions appear

**Given** I view Task Sessions
**When** I inspect session data
**Then** all sessions come from ClaudeTask database
**And** no .jsonl file sessions appear

---

## Testing Checklist

- [ ] All user stories (US-01 to US-04) pass acceptance criteria
- [ ] All functional requirements (FR-01 to FR-04) implemented
- [ ] All non-functional requirements (NFR-01 to NFR-04) verified
- [ ] All business rules (BR-01 to BR-03) enforced
- [ ] No console errors on any tab
- [ ] No TypeScript compilation errors
- [ ] Manual testing completed on all browsers
- [ ] Responsive testing on all screen sizes
- [ ] Keyboard navigation tested
- [ ] Screen reader tested (at least one reader)
- [ ] Performance metrics captured and meet requirements
