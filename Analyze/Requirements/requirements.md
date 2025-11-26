# Requirements: Merge Projects Section

**Task ID:** 18
**Task Title:** Объединить секцию Projects (Merge Projects Section)
**Date Created:** 2025-11-26
**Complexity:** MODERATE

## 1. Overview

Merge three separate project-related pages (Projects, Project Instructions, Project Setup) into a single unified Projects section with tab-based navigation. This consolidation improves UX by providing all project management functionality in one place and reduces navigation complexity.

## 2. User Stories

### User Story 1: Unified Project Management
**As a** ClaudeTask user
**I want** to access all project-related features in one unified section
**So that** I don't need to navigate between multiple pages to manage my projects

**Acceptance Criteria:**
- Single "Projects" menu item in sidebar (replaces 3 separate items)
- All project functionality accessible from unified page
- Tab-based navigation between project features
- URL structure preserves tab state

### User Story 2: Project List and Management
**As a** project manager
**I want** to view and manage all projects in a centralized table
**So that** I can quickly activate, edit, or delete projects

**Acceptance Criteria:**
- Projects table with all current functionality (activate, edit, delete, browse files, update framework)
- "New Project" button redirects to setup tab
- Active project indicator preserved
- GitHub repo links work correctly

### User Story 3: Project Instructions Editor
**As a** developer
**I want** to edit custom project instructions from the main Projects page
**So that** I can configure Claude's behavior without leaving the projects section

**Acceptance Criteria:**
- Accessible via tab in unified Projects section
- Project selector if multiple projects exist
- Full CRUD functionality for custom instructions
- Save confirmation and error handling

### User Story 4: Project Setup Wizard
**As a** new user
**I want** to initialize new projects from the Projects page
**So that** I can set up projects without navigating to separate setup page

**Acceptance Criteria:**
- Accessible via "Setup" tab or "New Project" button
- Complete stepper workflow preserved
- Folder picker integration works
- Success/error messaging consistent

## 3. Functional Requirements

### FR-1: Tabbed Navigation Structure
- Material-UI Tabs component with 3 tabs:
  - **Projects** (default) - project list and management
  - **Instructions** - custom instructions editor
  - **Setup** - project initialization wizard
- URL-based tab state: `/projects?tab=instructions`
- Tab state persists on navigation
- Keyboard navigation support (arrow keys)
- Mobile-responsive tab layout

### FR-2: Projects Tab (Main List)
- Complete existing ProjectManager functionality:
  - Table with columns: Name, Path, Tech Stack, GitHub, Status, Created, Actions
  - Context menu: Browse Files, Activate Project, Update Framework, Edit Project, Delete Project
  - Active project alert banner
  - Refresh button
  - "New Project" button (switches to Setup tab)
  - Edit dialog modal
  - Delete confirmation
  - Framework update notifications

### FR-3: Instructions Tab
- Complete existing ProjectInstructions functionality:
  - Project selector dropdown (if multiple projects)
  - Custom instructions textarea (multiline, 20 rows)
  - Save button with loading state
  - Success/error alerts
  - Info card explaining how instructions work
  - Database-backed storage

### FR-4: Setup Tab
- Complete existing ProjectSetup functionality:
  - 3-step stepper: Configuration → Initialize → Complete
  - Project path input with folder picker
  - Project name and GitHub repo fields
  - Project mode selection (Simple/Development)
  - Force reinitialize checkbox
  - Path examples and help text
  - Server-side folder picker integration
  - Success confirmation with file list

### FR-5: Sidebar Navigation Update
- Remove 3 separate menu items:
  - ~~Projects~~ (line 48)
  - ~~Project Instructions~~ (line 55)
  - ~~Project Setup~~ (line 56)
- Keep single "Projects" menu item (consolidated)
- Update routing in App.tsx

## 4. Non-Functional Requirements

### NFR-1: Performance
- Tab switching: < 100ms (no API calls on tab change)
- Initial page load: < 2 seconds
- API response time: < 500ms
- Smooth transitions with no UI flickering

### NFR-2: Usability
- Consistent Material-UI design language
- Clear visual hierarchy with gradient headers
- Intuitive tab labels
- Accessible via keyboard (Tab, Arrow keys, Enter)
- Mobile-responsive layout (tabs scroll horizontally on mobile)

### NFR-3: Maintainability
- Modular component structure
- Shared state management for project selection
- Reusable UI components
- TypeScript type safety
- Consistent error handling patterns

### NFR-4: Browser Compatibility
- Chrome 90+ (primary)
- Firefox 88+
- Safari 14+
- Edge 90+

## 5. Definition of Done (DoD)

### Code Implementation
- [ ] New unified Projects component created (`Projects.tsx`)
- [ ] Three existing pages integrated as tab panels
- [ ] Sidebar navigation updated (3 items → 1 item)
- [ ] Routing updated in App.tsx
- [ ] URL-based tab state implemented
- [ ] TypeScript type safety maintained
- [ ] No console errors or warnings

### Functionality
- [ ] All existing ProjectManager features work
- [ ] All existing ProjectInstructions features work
- [ ] All existing ProjectSetup features work
- [ ] Tab navigation works (click, keyboard)
- [ ] URL state preserves selected tab
- [ ] "New Project" button switches to Setup tab
- [ ] Mobile responsive layout works

### Testing
- [ ] Manual testing on all tabs completed
- [ ] Browser compatibility verified (Chrome, Firefox, Safari)
- [ ] Mobile responsive testing done
- [ ] Keyboard navigation tested
- [ ] All API integrations verified
- [ ] Error handling tested

### Documentation
- [ ] Component documentation updated
- [ ] README.md includes new Projects component
- [ ] API endpoints documented (if changed)
- [ ] User guide updated (if needed)

### Code Quality
- [ ] Code follows existing patterns
- [ ] No duplicate code
- [ ] Proper error handling
- [ ] Loading states implemented
- [ ] Accessibility attributes added (aria-*)
- [ ] Clean git history with descriptive commits

## 6. Out of Scope

The following are explicitly **not** included in this task:

- ❌ Changing existing API endpoints
- ❌ Modifying database schema
- ❌ Adding new project management features
- ❌ Redesigning UI components (keep existing styling)
- ❌ Performance optimizations beyond tab switching
- ❌ Internationalization (i18n)
- ❌ Unit/integration tests (manual testing only)
- ❌ Backend changes to projects API

## 7. Dependencies

### Internal Dependencies
- Material-UI Tabs component
- React Router v6 (URL state management)
- Existing ProjectManager, ProjectInstructions, ProjectSetup components
- Backend API: `/api/projects/*`, `/api/projects/{id}/instructions/`

### External Dependencies
- None (all dependencies already in package.json)

## 8. Success Metrics

### User Experience
- Reduce navigation clicks: 3 → 1 (66% improvement)
- Single source of truth for project management
- Faster project operations (no page reloads between features)

### Technical
- Zero regressions in existing functionality
- Maintain current API call patterns
- Same or better performance metrics

## 9. Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| State management complexity | Medium | Medium | Use URL params for tab state, avoid complex context |
| Breaking existing functionality | Low | High | Thorough testing of all features before merge |
| Mobile UX degradation | Low | Medium | Test on mobile devices, use Material-UI responsive breakpoints |
| Tab state not preserved | Medium | Low | Implement URL-based state early, test navigation |

## 10. Migration Notes

### User Impact
- **Minimal disruption**: All existing functionality preserved
- **Navigation change**: Users need to learn new tab structure (low learning curve)
- **Bookmarks**: Old URLs will redirect to new structure

### URL Migration Strategy
- Old: `/projects`, `/instructions`, `/setup`
- New: `/projects?tab=list` (default), `/projects?tab=instructions`, `/projects?tab=setup`
- Redirect rules in App.tsx for backward compatibility

## 11. References

- Existing implementation:
  - `claudetask/frontend/src/pages/ProjectManager.tsx`
  - `claudetask/frontend/src/pages/ProjectInstructions.tsx`
  - `claudetask/frontend/src/pages/ProjectSetup.tsx`
  - `claudetask/frontend/src/components/Sidebar.tsx`
  - `claudetask/frontend/src/App.tsx`

- Similar pattern: Sessions component (`Sessions.tsx`) with tab navigation for Claude Code/Task sessions

- Material-UI Tabs documentation: https://mui.com/material-ui/react-tabs/

---

**Document Status:** Final
**Reviewed By:** N/A
**Approved By:** N/A
**Last Updated:** 2025-11-26
