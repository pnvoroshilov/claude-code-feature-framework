# Acceptance Criteria: Merge Projects Section

**Task ID:** 18
**Last Updated:** 2025-11-26

## Overview

Detailed acceptance criteria for merging Projects, Project Instructions, and Project Setup into a unified tabbed interface.

---

## User Story 1: Unified Project Management

### Scenario 1.1: User navigates to Projects from sidebar
**GIVEN** user is on any page in ClaudeTask
**WHEN** user clicks "Projects" in sidebar
**THEN**
- Projects page loads with default "Projects" tab active
- URL is `/projects` or `/projects?tab=list`
- Sidebar shows "Projects" as active/selected
- No separate "Project Instructions" or "Project Setup" menu items visible

### Scenario 1.2: User switches between tabs
**GIVEN** user is on Projects page
**WHEN** user clicks "Instructions" tab
**THEN**
- Instructions tab content displays
- URL updates to `/projects?tab=instructions`
- Tab indicator moves to "Instructions"
- Previous tab content is hidden (not destroyed)
- No page reload occurs

### Scenario 1.3: User accesses Projects via direct URL
**GIVEN** user has URL `/projects?tab=setup`
**WHEN** user navigates to URL
**THEN**
- Projects page loads with "Setup" tab active
- Tab state reflects URL parameter
- Other tabs are accessible via tab navigation

### Scenario 1.4: Tab state persists on navigation
**GIVEN** user is on `/projects?tab=instructions`
**WHEN** user navigates away and returns via browser back button
**THEN**
- Instructions tab is still active
- Tab state is preserved from URL
- No default tab reset occurs

---

## User Story 2: Project List and Management

### Scenario 2.1: Projects table displays correctly
**GIVEN** user has 3 projects in database
**WHEN** user views Projects tab
**THEN**
- Table shows all 3 projects
- Columns displayed: Name, Path, Tech Stack, GitHub, Status, Created, Actions
- Active project shows "Active" chip (green)
- Inactive projects show "Inactive" chip (gray)
- Each row has context menu (3-dot icon)

### Scenario 2.2: User activates a project
**GIVEN** user has inactive project "MyApp"
**WHEN** user clicks context menu → "Activate Project"
**THEN**
- Project status changes to "Active"
- Active project alert banner updates
- Other projects become inactive
- API call: `POST /api/projects/{id}/activate`
- UI updates without page reload

### Scenario 2.3: User edits project details
**GIVEN** user selects "Edit Project" from context menu
**WHEN** edit dialog opens
**THEN**
- Dialog shows project name and GitHub repo fields
- Current values pre-filled
- Path and tech stack shown as read-only info
- Save button disabled until changes made

**AND WHEN** user changes name and clicks "Save"
**THEN**
- API call: `PUT /api/projects/{id}` with updated data
- Dialog closes on success
- Table updates with new name
- Success feedback shown (optional)

### Scenario 2.4: User deletes a project
**GIVEN** user selects "Delete Project" from context menu
**WHEN** confirmation dialog appears
**THEN**
- Confirmation message: "Are you sure you want to delete '{name}'?"
- User can cancel or confirm

**AND WHEN** user confirms deletion
**THEN**
- API call: `DELETE /api/projects/{id}`
- Project removed from table
- If deleted project was active, no active project remains
- Error alert shown if deletion fails

### Scenario 2.5: User updates framework files
**GIVEN** user selects "Update Framework" from context menu
**WHEN** update initiates
**THEN**
- Loading indicator shown
- API call: `POST /api/projects/{id}/update-framework`
- Success alert shows updated files list
- Alert auto-dismisses after 5 seconds

### Scenario 2.6: User clicks "New Project" button
**GIVEN** user is on Projects tab
**WHEN** user clicks "New Project" button
**THEN**
- Tab switches to "Setup" tab
- URL updates to `/projects?tab=setup`
- Setup wizard displays step 1 (Configuration)

### Scenario 2.7: User browses project files
**GIVEN** user clicks context menu → "Browse Files"
**WHEN** file browser loads
**THEN**
- Navigates to `/projects/{id}/files`
- File browser component loads
- Project context preserved

---

## User Story 3: Project Instructions Editor

### Scenario 3.1: User accesses instructions tab
**GIVEN** user has active project selected
**WHEN** user clicks "Instructions" tab
**THEN**
- Instructions editor loads
- Active project name shown in header
- Custom instructions loaded from database
- Save button visible and enabled

### Scenario 3.2: User edits custom instructions
**GIVEN** user is on Instructions tab
**WHEN** user types in textarea
**THEN**
- Changes reflected in real-time
- No auto-save occurs
- Save button remains enabled
- Unsaved changes warning (optional)

### Scenario 3.3: User saves instructions
**GIVEN** user has modified instructions
**WHEN** user clicks "Save Instructions"
**THEN**
- Save button shows loading state ("Saving...")
- API call: `PUT /api/projects/{id}/instructions/`
- Success alert: "Instructions saved successfully!"
- Alert auto-dismisses after 3 seconds
- Save button returns to normal state

### Scenario 3.4: User saves with API error
**GIVEN** backend is unreachable
**WHEN** user clicks "Save Instructions"
**THEN**
- Error alert shown: "Failed to save instructions: {error detail}"
- Instructions remain in editor (not lost)
- User can retry save
- Alert dismissible by user

### Scenario 3.5: No active project selected
**GIVEN** no project is active
**WHEN** user clicks "Instructions" tab
**THEN**
- Info alert: "Please select a project to edit instructions."
- Editor is disabled or hidden
- Suggestion to activate project shown

---

## User Story 4: Project Setup Wizard

### Scenario 4.1: User starts new project setup
**GIVEN** user is on Setup tab
**WHEN** tab loads
**THEN**
- Stepper shows 3 steps: "Project Configuration", "Initialize", "Setup Complete"
- Step 1 "Project Configuration" is active
- Form fields visible: Project Path, Project Name, GitHub Repo, Project Mode
- "Initialize Project" button enabled when path and name filled

### Scenario 4.2: User enters project path manually
**GIVEN** user is on Configuration step
**WHEN** user types `/Users/john/projects/my-app`
**THEN**
- Project name auto-fills to "my-app" (if empty)
- Path validation occurs (optional)
- "Initialize Project" button becomes enabled

### Scenario 4.3: User uses folder picker
**GIVEN** user clicks "Browse" button
**WHEN** system folder picker opens
**THEN**
- User can navigate file system
- Selected folder path populates "Project Path" field
- Project name auto-fills from folder name
- Picker closes on selection or cancel

### Scenario 4.4: User selects project mode
**GIVEN** user is on Configuration step
**WHEN** user selects "Development Mode" radio button
**THEN**
- Mode description shown: "Full workflow with Git integration..."
- Form state updates with selected mode
- Mode will be sent to API on initialization

### Scenario 4.5: User initializes project
**GIVEN** user has filled required fields
**WHEN** user clicks "Initialize Project"
**THEN**
- Stepper advances to step 2 "Initialize"
- Loading indicator shows "Initializing Project..."
- API call: `POST /api/projects/initialize`
- On success, stepper advances to step 3 "Setup Complete"

### Scenario 4.6: Initialization succeeds
**GIVEN** API returns success
**WHEN** step 3 loads
**THEN**
- Success icon (green checkmark) displayed
- "Project Initialized Successfully!" message
- Configuration details shown (Project ID, MCP Configured)
- Files created list displayed
- "Initialize Another Project" button available

### Scenario 4.7: Initialization fails
**GIVEN** API returns error (e.g., path already exists)
**WHEN** initialization completes
**THEN**
- Error alert shown: "Initialization failed: {error detail}"
- User remains on step 2
- Can modify form and retry
- Error dismissible

### Scenario 4.8: Force reinitialize option
**GIVEN** project already exists at path
**WHEN** user checks "Force reinitialize" and submits
**THEN**
- API call includes `force_reinitialize: true`
- Existing configuration removed
- New configuration created
- Warning about data loss (optional)

---

## Cross-Cutting Acceptance Criteria

### Navigation

**AC-N1:** Sidebar shows single "Projects" menu item (not 3 separate items)
**AC-N2:** Clicking "Projects" in sidebar navigates to `/projects`
**AC-N3:** URL parameter `?tab={name}` controls active tab
**AC-N4:** Tab state survives page refresh (from URL)
**AC-N5:** Browser back/forward navigation works correctly

### Responsive Design

**AC-R1:** On mobile (< 960px), tabs scroll horizontally
**AC-R2:** All tab content responsive and readable on mobile
**AC-R3:** Tables have horizontal scroll if needed
**AC-R4:** Forms stack vertically on narrow screens

### Accessibility

**AC-A1:** Tabs navigable via keyboard (Tab, Arrow keys, Enter)
**AC-A2:** ARIA labels present: `role="tabpanel"`, `aria-labelledby`
**AC-A3:** Focus indicators visible on tab elements
**AC-A4:** Screen reader announces tab changes

### Error Handling

**AC-E1:** All API errors show user-friendly messages
**AC-E2:** Network errors handled gracefully (no crash)
**AC-E3:** Loading states shown during async operations
**AC-E4:** Error alerts dismissible by user
**AC-E5:** Failed operations can be retried

### Performance

**AC-P1:** Tab switching < 100ms (no network calls)
**AC-P2:** Initial page load < 2 seconds
**AC-P3:** No UI flicker during tab changes
**AC-P4:** Smooth transitions between tabs

### Data Integrity

**AC-D1:** No data loss on tab switching
**AC-D2:** Unsaved changes warning (optional)
**AC-D3:** API calls match existing endpoints
**AC-D4:** Database operations atomic and consistent

---

## Edge Cases

### EC-1: No projects exist
**GIVEN** database has zero projects
**WHEN** user views Projects tab
**THEN**
- Empty state shown: "No projects found"
- "Create Project" button visible
- Suggests navigating to Setup tab

### EC-2: Very long project path
**GIVEN** project path is > 100 characters
**WHEN** displayed in table
**THEN**
- Path truncated with ellipsis
- Tooltip shows full path on hover
- No layout breaking

### EC-3: Network offline during save
**GIVEN** user is offline
**WHEN** user saves instructions
**THEN**
- Error alert: "Network error. Please check connection."
- Data preserved in form
- User can retry when online

### EC-4: Concurrent project activation
**GIVEN** two users activate different projects simultaneously
**WHEN** both requests complete
**THEN**
- Last request wins (expected behavior)
- UI updates for both users
- No database corruption

### EC-5: Special characters in project name
**GIVEN** project name includes `<script>alert('xss')</script>`
**WHEN** project displayed in table
**THEN**
- Name rendered as text (not executed)
- XSS protection in place
- Special chars properly escaped

---

## Testing Checklist

### Manual Testing
- [ ] Navigate to Projects via sidebar
- [ ] Switch between all 3 tabs
- [ ] Verify URL updates with tab changes
- [ ] Test browser back/forward with tabs
- [ ] Activate a project from table
- [ ] Edit project details
- [ ] Delete a project
- [ ] Update framework files
- [ ] Browse files from context menu
- [ ] Save custom instructions
- [ ] Initialize new project via Setup
- [ ] Test folder picker (Browse button)
- [ ] Test force reinitialize option
- [ ] Verify mobile responsive layout
- [ ] Test keyboard navigation (Tab, Arrow keys)
- [ ] Test all error scenarios (API failures)
- [ ] Verify loading states show correctly
- [ ] Check accessibility with screen reader

### Browser Compatibility
- [ ] Chrome (latest)
- [ ] Firefox (latest)
- [ ] Safari (latest)
- [ ] Edge (latest)
- [ ] Mobile Safari (iOS)
- [ ] Mobile Chrome (Android)

---

**Document Status:** Final
**Total Scenarios:** 35+
**Critical Paths:** 4 (Navigation, Projects Table, Instructions, Setup)
**Edge Cases:** 5
**Last Updated:** 2025-11-26
