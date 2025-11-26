# Constraints: Merge Projects Section

**Task ID:** 18
**Last Updated:** 2025-11-26

## 1. Technical Constraints

### TC-1: Technology Stack (MANDATORY)
**Constraint:** Must use existing technology stack without introducing new dependencies

**Details:**
- React 18.x
- TypeScript
- Material-UI (MUI) v5
- React Router v6
- Existing API client patterns

**Rationale:** Maintain consistency with existing codebase and avoid dependency bloat

**Impact:** Cannot use alternative UI libraries or routing solutions

---

### TC-2: Existing API Contracts (MANDATORY)
**Constraint:** Cannot modify existing backend API endpoints

**Protected Endpoints:**
- `GET /api/projects` - List all projects
- `POST /api/projects/{id}/activate` - Activate project
- `PUT /api/projects/{id}` - Update project
- `DELETE /api/projects/{id}` - Delete project
- `GET /api/projects/{id}/instructions/` - Get instructions
- `PUT /api/projects/{id}/instructions/` - Update instructions
- `POST /api/projects/initialize` - Initialize project
- `POST /api/projects/{id}/update-framework` - Update framework

**Rationale:** Backend changes are out of scope; other features depend on these endpoints

**Impact:** Frontend must work with existing API structure and response formats

---

### TC-3: Component Reuse (RECOMMENDED)
**Constraint:** Maximize reuse of existing component code from ProjectManager, ProjectInstructions, ProjectSetup

**Details:**
- Extract existing logic into reusable components
- Preserve existing styling and UX patterns
- Avoid code duplication

**Rationale:** Faster implementation, less bug surface area, easier maintenance

**Impact:** May need refactoring for composition, but core logic stays same

---

### TC-4: URL Structure (MANDATORY)
**Constraint:** URL structure must support tab-based navigation and be bookmarkable

**Required Pattern:**
- `/projects` - Default to Projects tab
- `/projects?tab=list` - Projects tab (explicit)
- `/projects?tab=instructions` - Instructions tab
- `/projects?tab=setup` - Setup tab

**Backward Compatibility (RECOMMENDED):**
- `/instructions` → redirect to `/projects?tab=instructions`
- `/setup` → redirect to `/projects?tab=setup`

**Rationale:** SEO, bookmarkability, browser history navigation

**Impact:** Routing logic must handle query parameters and redirects

---

### TC-5: Browser Support (MANDATORY)
**Constraint:** Must work on modern browsers with ES6+ support

**Minimum Versions:**
- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

**Not Required:**
- Internet Explorer (deprecated)
- Opera Mini
- Very old mobile browsers

**Rationale:** Modern browser features required (fetch, async/await, ES6 modules)

**Impact:** Can use modern JavaScript/CSS features without polyfills for old browsers

---

## 2. Design Constraints

### DC-1: Material-UI Design System (MANDATORY)
**Constraint:** All UI components must use Material-UI components and styling

**Required:**
- MUI Tabs for tab navigation
- MUI theme system for colors
- MUI typography and spacing
- MUI icons
- `sx` prop for styling (no inline CSS)

**Prohibited:**
- Custom CSS classes (unless absolutely necessary)
- Inline styles (except for dynamic values)
- Third-party UI libraries

**Rationale:** Consistency with existing app design and theming

**Impact:** Must adapt designs to MUI capabilities and patterns

---

### DC-2: Existing Visual Language (MANDATORY)
**Constraint:** Must maintain existing visual design patterns and branding

**Preserve:**
- Gradient headers (primary color gradient for page titles)
- Card-based layouts with shadows
- Color palette (primary blue, success green, error red)
- Icon usage patterns
- Spacing and typography hierarchy

**Rationale:** Consistent user experience across app

**Impact:** Cannot introduce new visual styles or redesign existing components

---

### DC-3: Responsive Design (MANDATORY)
**Constraint:** Must be fully responsive on mobile, tablet, and desktop

**Breakpoints (MUI default):**
- xs: 0px (mobile)
- sm: 600px (tablet)
- md: 960px (desktop)
- lg: 1280px (large desktop)
- xl: 1920px (extra large)

**Requirements:**
- Mobile-first approach
- No horizontal scroll on narrow screens
- Touch-friendly targets (min 44x44px)
- Tabs scroll horizontally on mobile

**Rationale:** Users access app from various devices

**Impact:** Need responsive layouts, breakpoint testing required

---

### DC-4: Accessibility Standards (RECOMMENDED)
**Constraint:** Should meet WCAG 2.1 Level AA standards

**Requirements:**
- Keyboard navigation support
- ARIA labels for screen readers
- Sufficient color contrast (4.5:1 minimum)
- Focus indicators visible
- Tab order logical

**Rationale:** Accessibility best practices and potential legal requirements

**Impact:** Extra attributes and testing needed for accessibility

---

## 3. Performance Constraints

### PC-1: Page Load Time (TARGET)
**Constraint:** Initial page load should complete in < 2 seconds on average connection

**Metrics:**
- First Contentful Paint (FCP) < 1.5s
- Time to Interactive (TTI) < 2.5s
- Largest Contentful Paint (LCP) < 2.5s

**Rationale:** User experience and engagement

**Impact:** May need code splitting, lazy loading, or optimizations

---

### PC-2: Tab Switching Performance (MANDATORY)
**Constraint:** Tab switching must feel instant (< 100ms)

**Requirements:**
- No API calls on tab switch (load data once)
- No full component remount on tab change
- Smooth transitions with no flicker

**Rationale:** Perceived performance critical for tabbed UIs

**Impact:** Need smart state management, potentially keep all tabs mounted

---

### PC-3: API Response Time (INFORMATIONAL)
**Constraint:** Backend API response times are outside our control

**Known Limitations:**
- Project list: ~200-500ms
- Initialize project: ~1-3s (creates files)
- Update framework: ~2-5s (updates multiple files)

**Mitigation:**
- Show loading indicators
- Provide user feedback
- Allow cancellation (if possible)

**Rationale:** Backend performance is separate concern

**Impact:** Must design for async operations with loading states

---

## 4. Security Constraints

### SC-1: Path Traversal Protection (MANDATORY)
**Constraint:** All file paths must be validated to prevent directory traversal attacks

**Requirements:**
- Validate project paths don't contain `..`, absolute paths outside allowed dirs
- Server-side validation for all path inputs
- Sanitize user input before API calls

**Rationale:** Security vulnerability if user can access arbitrary file system

**Impact:** Path validation logic required, error handling for invalid paths

---

### SC-2: XSS Prevention (MANDATORY)
**Constraint:** All user-generated content must be escaped to prevent XSS

**Requirements:**
- React's built-in XSS protection (dangerouslySetInnerHTML avoided)
- Sanitize project names, instructions before display
- No `eval()` or `innerHTML` usage

**Rationale:** Common web security vulnerability

**Impact:** React handles most XSS prevention, but be cautious with dynamic content

---

### SC-3: CSRF Protection (INFORMATIONAL)
**Constraint:** Backend must implement CSRF protection for state-changing operations

**Details:**
- POST/PUT/DELETE requests should include CSRF token
- Backend validates token

**Rationale:** Prevent cross-site request forgery attacks

**Impact:** Frontend may need to include CSRF token in headers (check existing API client)

---

## 5. Data Constraints

### DC-1: Project Data Structure (MANDATORY)
**Constraint:** Must work with existing project data model from backend

**Project Schema:**
```typescript
interface Project {
  id: string;
  name: string;
  path: string;
  tech_stack: string[];
  github_repo?: string;
  is_active: boolean;
  created_at: string;
  project_mode?: 'simple' | 'development';
}
```

**Rationale:** Database schema is fixed, cannot change

**Impact:** Frontend must adapt to this structure

---

### DC-2: Custom Instructions Format (MANDATORY)
**Constraint:** Custom instructions stored as plain text in database

**Details:**
- No rich text formatting (plain text only)
- Max length: TBD (check backend validation)
- Stored per project (not global)

**Rationale:** Simple text storage, no markdown parsing on backend

**Impact:** Textarea input sufficient, no rich text editor needed

---

## 6. Business Constraints

### BC-1: No Breaking Changes (MANDATORY)
**Constraint:** Existing functionality must continue to work exactly as before

**Requirements:**
- All features from ProjectManager preserved
- All features from ProjectInstructions preserved
- All features from ProjectSetup preserved
- No behavior changes (only UI reorganization)

**Rationale:** Users rely on existing workflows

**Impact:** Comprehensive regression testing required

---

### BC-2: User Training (MINIMAL)
**Constraint:** Changes should be intuitive enough to require minimal user training

**Requirements:**
- Tabs clearly labeled
- No major workflow changes
- Similar patterns to existing app (e.g., Sessions page tabs)

**Rationale:** Users shouldn't need documentation to understand change

**Impact:** Familiar tab pattern, clear labels, consistent UX

---

## 7. Time and Resource Constraints

### RC-1: Implementation Timeline (INFORMATIONAL)
**Constraint:** Task should be completed in reasonable timeframe

**Estimated Effort:**
- Component creation: 2-4 hours
- Integration and testing: 2-3 hours
- Bug fixes and polish: 1-2 hours
- **Total: 5-9 hours** (1-2 days for single developer)

**Rationale:** Moderate complexity task with clear requirements

**Impact:** Prioritize core functionality, defer nice-to-haves if needed

---

### RC-2: Testing Resources (MANUAL)
**Constraint:** Testing will be manual (no automated tests required)

**Requirements:**
- Manual browser testing (Chrome, Firefox, Safari)
- Mobile responsive testing (physical devices or DevTools)
- Functional testing of all features
- No unit tests or E2E tests required for this task

**Rationale:** Framework doesn't currently have extensive test suite

**Impact:** Thorough manual testing checklist needed

---

## 8. Dependencies and Integration Constraints

### IC-1: React Router Dependency (MANDATORY)
**Constraint:** Must use React Router v6 for navigation and URL state

**Details:**
- Use `useSearchParams()` for tab state
- Use `<Navigate>` for redirects
- Follow existing routing patterns in App.tsx

**Rationale:** Existing routing infrastructure

**Impact:** Tab state management via URL query params

---

### IC-2: API Client Pattern (MANDATORY)
**Constraint:** Must use existing API client in `services/api.ts`

**Existing Functions:**
- `getProjects()`
- `updateProject(id, data)`
- `deleteProject(id)`
- `activateProject(id)`
- `updateFramework(id)`
- `initializeProject(data)`

**Rationale:** Centralized API client for consistency and maintainability

**Impact:** Use existing functions, add new ones if needed (within api.ts pattern)

---

### IC-3: ProjectContext Dependency (RECOMMENDED)
**Constraint:** Consider using existing ProjectContext for shared state

**Details:**
- `ProjectProvider` already wraps app
- `useProject()` hook provides selected project state
- May reduce prop drilling

**Rationale:** Avoid duplicate state management

**Impact:** Review existing context usage before implementing new state

---

## 9. Known Limitations

### KL-1: No Real-Time Updates
**Limitation:** Changes in one browser tab/window won't reflect in others without manual refresh

**Details:**
- No WebSocket or polling for real-time sync
- User must refresh to see changes from other sessions

**Rationale:** Out of scope for this task

**Impact:** Document behavior, consider future enhancement

---

### KL-2: No Offline Support
**Limitation:** App requires network connection to function

**Details:**
- No service worker or offline cache
- API calls fail if offline
- No optimistic UI updates

**Rationale:** Out of scope for this task

**Impact:** Show clear error messages when offline

---

### KL-3: No Undo/Redo
**Limitation:** Destructive operations (delete project) cannot be undone

**Details:**
- No undo stack or history
- Confirmations are only safeguard

**Rationale:** Complex feature, out of scope

**Impact:** Ensure confirmation dialogs are clear

---

## 10. Assumptions

### A-1: Backend Stability
**Assumption:** Backend APIs are stable and won't change during implementation

**Risk:** Low (backend is mature)

**Mitigation:** Communicate with backend team if API changes needed

---

### A-2: Browser Compatibility
**Assumption:** Users are on modern browsers (90%+ market share)

**Risk:** Low (old browsers rare in development tools space)

**Mitigation:** Document minimum browser requirements

---

### A-3: Single Active Project
**Assumption:** Only one project can be active at a time (existing behavior)

**Risk:** None (current limitation)

**Mitigation:** N/A

---

### A-4: No Custom Instructions Validation
**Assumption:** Custom instructions are free-form text with minimal validation

**Risk:** Low (backend may have max length, but no strict format)

**Mitigation:** Handle server validation errors gracefully

---

## Summary Matrix

| Category | Constraint | Priority | Impact |
|----------|-----------|----------|--------|
| Technical | Existing Tech Stack | MANDATORY | High - Must use React, MUI, TypeScript |
| Technical | API Contracts | MANDATORY | High - Cannot change backend |
| Design | Material-UI Design | MANDATORY | High - Consistent UI |
| Design | Responsive Design | MANDATORY | High - Mobile support required |
| Performance | Tab Switch Speed | MANDATORY | Medium - UX critical |
| Security | Path Validation | MANDATORY | High - Security risk |
| Security | XSS Prevention | MANDATORY | High - Security risk |
| Business | No Breaking Changes | MANDATORY | High - User workflows preserved |
| Integration | React Router v6 | MANDATORY | Medium - URL state management |
| Limitation | No Real-Time Sync | KNOWN | Low - Document only |

---

**Total Constraints:** 24 (10 MANDATORY, 3 RECOMMENDED, 4 INFORMATIONAL, 4 KNOWN LIMITATIONS, 3 ASSUMPTIONS)

**Critical Path Blockers:** None identified

**Document Status:** Final
**Last Updated:** 2025-11-26
