# Architecture Decision Records: Projects Section Consolidation

## ADR-001: Consolidate Project Pages into Tabbed Interface

**Status**: Proposed
**Date**: 2025-01-26
**Deciders**: Development Team

### Context
Currently, project-related functionality is split across three separate pages:
1. Projects (`/projects`) - Project list and management
2. Project Instructions (`/instructions`) - Custom instructions editor
3. Project Setup (`/setup`) - New project initialization

This creates navigation friction and conceptual fragmentation. Users must navigate between different sidebar items to complete project-related workflows.

### Decision
Consolidate all three pages into a single "Projects" section with tabbed navigation, following the established pattern from Sessions.tsx.

### Rationale

#### Pattern Consistency
- **Sessions.tsx precedent**: Already uses tabbed interface successfully (Claude Code Sessions + Task Sessions)
- **Proven UX**: Users are familiar with this pattern in the application
- **Code reuse**: Can follow established implementation patterns

#### User Experience Benefits
1. **Single Mental Model**: "Projects" is one concept, not three
2. **Context Preservation**: Stay in "Projects" context while accessing related features
3. **Reduced Navigation**: Fewer sidebar items (6 items vs 8 items)
4. **Workflow Efficiency**: Create project → Set instructions → Manage projects without leaving section

#### Technical Benefits
1. **URL-Based State**: Tabs sync with browser URL for deep linking
2. **Browser Navigation**: Back/forward buttons work correctly
3. **Component Reuse**: Extract existing logic into composable views
4. **Maintainability**: Related code grouped together

### Consequences

#### Positive
- **Cleaner Sidebar**: Reduced visual clutter (2 fewer menu items)
- **Better Organization**: Related functionality co-located
- **Consistent UX**: Matches Sessions pattern users already understand
- **Shareable URLs**: Can link directly to specific tabs (e.g., `/projects/setup`)

#### Negative
- **Initial Complexity**: More complex parent component than separate pages
- **Bundle Size**: All tab content loaded together (mitigated by conditional rendering)
- **Migration Effort**: Need to extract and refactor existing components

#### Neutral
- **Different Navigation**: Users navigate via tabs instead of sidebar (but more intuitive)
- **URL Structure Change**: Old routes need redirects or deprecation

### Alternatives Considered

#### Alternative 1: Keep Separate Pages
**Rejected** because:
- Doesn't solve navigation friction
- Misses opportunity for consistency with Sessions pattern
- Doesn't improve user workflow efficiency

#### Alternative 2: Single Page Without Tabs
**Rejected** because:
- Would be too long and overwhelming
- Loses deep linking capability
- Harder to maintain focused views

#### Alternative 3: Accordion Instead of Tabs
**Rejected** because:
- Doesn't match Sessions.tsx pattern
- Less common UX pattern for navigation
- Harder to bookmark specific sections

### Implementation Notes
- Follow Sessions.tsx implementation as reference (lines 92-537)
- Use URL-based tab state management
- Extract existing page logic into view components
- Maintain backward compatibility for FileBrowser route

---

## ADR-002: URL-Based Tab State Management

**Status**: Proposed
**Date**: 2025-01-26

### Context
When implementing tabbed navigation, state can be managed in multiple ways:
1. React state only (no URL changes)
2. Query parameters (`/projects?tab=setup`)
3. URL path segments (`/projects/setup`)

### Decision
Use URL path segments for tab state (`/projects/list`, `/projects/instructions`, `/projects/setup`).

### Rationale

#### Consistency with Sessions
- Sessions.tsx uses path segments (`/sessions/claude-code`, `/sessions/tasks`)
- Users already familiar with this pattern
- Creates consistent mental model across application

#### Technical Advantages
1. **Deep Linking**: Share direct links to specific tabs
2. **Browser Navigation**: Back/forward buttons work intuitively
3. **Bookmarking**: Users can bookmark specific tabs
4. **Analytics**: Easier to track which tabs are used most
5. **SEO-Friendly**: Better URL structure (if public-facing in future)

#### User Experience
- **Clear URL**: User knows exactly where they are
- **Predictable**: Matches web standards and user expectations
- **Shareable**: Can send link to colleague: "Check the setup tab"

### Consequences

#### Positive
- All benefits of deep linking and browser navigation
- Consistent with existing Sessions implementation
- Future-proof for potential public documentation

#### Negative
- Slightly more complex routing logic
- Need to handle default redirect (`/projects` → `/projects/list`)

#### Implementation
```typescript
// URL-based state management pattern
useEffect(() => {
  const path = location.pathname;
  if (path === '/projects' || path === '/projects/') {
    navigate('/projects/list', { replace: true });
    setCurrentTab('list');
  } else if (path.includes('/list')) {
    setCurrentTab('list');
  } else if (path.includes('/instructions')) {
    setCurrentTab('instructions');
  } else if (path.includes('/setup')) {
    setCurrentTab('setup');
  }
}, [location.pathname, navigate]);
```

### Alternatives Considered

#### Alternative 1: Query Parameters (`?tab=setup`)
**Rejected** because:
- Inconsistent with Sessions.tsx pattern
- Less clean URLs
- Harder to construct redirect rules

#### Alternative 2: React State Only
**Rejected** because:
- No deep linking capability
- Browser back/forward don't work
- Can't bookmark specific tabs

---

## ADR-003: Extract Views as Separate Components

**Status**: Proposed
**Date**: 2025-01-26

### Context
When consolidating pages into tabs, we can either:
1. Inline all content directly in parent component
2. Extract each tab's content into separate view components

### Decision
Extract each tab into separate view components:
- `ProjectListView.tsx`
- `ProjectInstructionsView.tsx`
- `ProjectSetupView.tsx`

### Rationale

#### Maintainability
- **Single Responsibility**: Each view handles one concern
- **Easier Testing**: Can test views independently
- **Cleaner Parent**: Parent component focuses on tab navigation logic
- **Reduced Complexity**: Each file stays under 600 lines

#### Code Organization
- **Clear Boundaries**: Tab content clearly separated
- **Reusability**: Views could be reused elsewhere if needed (e.g., modals)
- **Parallel Development**: Multiple developers can work on different tabs

#### Performance
- **Code Splitting**: Could lazy-load tabs in future if needed
- **Conditional Rendering**: Only active tab interactive, others hidden
- **Maintainable Bundle**: Easier to analyze and optimize individual views

### Consequences

#### Positive
- Better code organization and separation of concerns
- Easier to maintain and test individual views
- Parent component stays clean and focused
- Team members can work on different tabs without conflicts

#### Negative
- More files to manage (4 instead of 1)
- Slightly more import overhead
- Need to pass props/context to child components

#### Implementation Structure
```
src/
├── pages/
│   └── Projects.tsx (parent with tabs, ~200 lines)
└── components/
    └── projects/
        ├── ProjectListView.tsx (~600 lines)
        ├── ProjectInstructionsView.tsx (~300 lines)
        └── ProjectSetupView.tsx (~400 lines)
```

### Alternatives Considered

#### Alternative 1: Inline Everything in Projects.tsx
**Rejected** because:
- Would create 1500+ line file
- Hard to maintain and test
- Violates single responsibility principle

#### Alternative 2: Keep Original Page Structure with Wrapper
**Rejected** because:
- Doesn't improve organization
- Duplicates routing logic
- Misses opportunity to extract reusable views

---

## ADR-004: Conditional Rendering vs Lazy Loading

**Status**: Proposed
**Date**: 2025-01-26

### Context
Tab content can be rendered in different ways:
1. **Conditional Rendering**: All tabs in DOM, use `hidden` attribute
2. **Mount/Unmount**: Only render active tab, unmount others
3. **Lazy Loading**: Use React.lazy() to load tabs on demand

### Decision
Use conditional rendering with `hidden` attribute (following Sessions.tsx pattern).

### Rationale

#### Consistency
- Sessions.tsx uses this approach (lines 521-537)
- Proven to work well in production
- Maintains consistency across codebase

#### User Experience
- **Fast Tab Switching**: No loading delay when changing tabs
- **State Preservation**: Form data, scroll position preserved
- **Smooth Transitions**: No flicker or layout shift

#### Simplicity
- Straightforward implementation
- No need for suspense boundaries
- Easier to debug and maintain

#### Performance Trade-offs
- **Bundle Size**: All tabs loaded initially (~1500 lines total)
  - Not significant compared to other pages
  - Projects section is core functionality
- **Initial Load**: Slightly slower first load
  - Acceptable for admin/management interface
  - Users typically stay in Projects section once there
- **Runtime Performance**: All tabs in DOM
  - Modern browsers handle this well
  - Only visible tab receives interactions

### Consequences

#### Positive
- Fast tab switching (no re-rendering)
- State preservation across tabs
- Simpler implementation
- Consistent with Sessions.tsx

#### Negative
- All tab content in initial bundle
- All tab components mount on first render
- Slightly larger initial memory footprint

#### When to Reconsider
Consider lazy loading if:
- Bundle size becomes concern (> 500KB for Projects section)
- Tab content becomes significantly more complex
- Performance metrics show slow initial load

### Implementation
```typescript
<Box role="tabpanel" hidden={currentTab !== 'list'}>
  {currentTab === 'list' && <ProjectListView />}
</Box>
<Box role="tabpanel" hidden={currentTab !== 'instructions'}>
  {currentTab === 'instructions' && <ProjectInstructionsView />}
</Box>
```

### Alternatives Considered

#### Alternative 1: Lazy Loading with React.lazy()
**Rejected for now** because:
- Adds unnecessary complexity
- Bundle size not currently a concern
- Would introduce loading states between tabs
- Could always add later if needed

#### Alternative 2: Mount/Unmount Pattern
**Rejected** because:
- Loses form state when switching tabs
- Causes unnecessary re-renders
- Slower tab switching experience

---

## ADR-005: Sidebar Consolidation

**Status**: Proposed
**Date**: 2025-01-26

### Context
Current sidebar has 3 project-related menu items:
- Projects
- Project Instructions
- Project Setup

After consolidation, need to decide how to represent this in sidebar.

### Decision
Keep single "Projects" menu item, remove "Project Instructions" and "Project Setup" from sidebar.

### Rationale

#### Reduced Cognitive Load
- **Fewer Items**: Sidebar goes from 8 to 6 main items
- **Clearer Organization**: Related features grouped under one concept
- **Simpler Mental Model**: "Projects" encompasses all project functionality

#### Navigation Efficiency
- **Fewer Clicks**: Users go to "Projects" then choose tab (vs hunting for right sidebar item)
- **Context Awareness**: Tab bar shows all options at once
- **Better Discoverability**: Users see all project features when they visit Projects section

#### Consistency
- **Matches Sessions**: Sessions has 2 tabs but single sidebar item
- **Standard Pattern**: Most admin UIs group related features under sections with tabs

### Consequences

#### Positive
- Cleaner, less cluttered sidebar
- More intuitive navigation (one place for all project tasks)
- Consistent with Sessions pattern

#### Negative
- Users must know to look in "Projects" for instructions/setup
- Can't navigate directly to Setup from sidebar (must go through Projects first)

#### Migration Considerations
- Some users might look for "Project Setup" in sidebar
- Could add tooltip on "Projects" item: "Manage projects, instructions, and setup"
- Monitor user feedback and adjust if needed

### Implementation
```typescript
// Before: 3 menu items
{ text: 'Projects', icon: <ProjectIcon />, path: '/projects' },
{ text: 'Project Instructions', icon: <InstructionsIcon />, path: '/instructions' },
{ text: 'Project Setup', icon: <SetupIcon />, path: '/setup' },

// After: 1 menu item
{ text: 'Projects', icon: <ProjectIcon />, path: '/projects' },
```

### Active State Logic
```typescript
const isActive = item.path === '/projects'
  ? location.pathname.startsWith('/projects')
  : location.pathname === item.path;
```

This ensures "Projects" highlights for `/projects/list`, `/projects/instructions`, `/projects/setup`.

---

## Summary of Architectural Decisions

| ADR | Decision | Rationale | Impact |
|-----|----------|-----------|--------|
| ADR-001 | Consolidate into tabs | Pattern consistency, improved UX | Major refactor, better organization |
| ADR-002 | URL-based tab state | Deep linking, browser navigation | More complex routing, better UX |
| ADR-003 | Extract view components | Maintainability, testability | More files, cleaner code |
| ADR-004 | Conditional rendering | Fast switching, state preservation | Larger initial bundle, smoother UX |
| ADR-005 | Single sidebar item | Reduced clutter, clearer navigation | Fewer sidebar items, potential discoverability issue |

## Risks and Mitigations

| Risk | Probability | Impact | Mitigation |
|------|------------|--------|------------|
| Users can't find setup/instructions | Low | Medium | Add tooltips, update documentation |
| Bundle size too large | Low | Low | Monitor metrics, add lazy loading if needed |
| URL routing bugs | Medium | High | Thorough testing, follow Sessions.tsx pattern exactly |
| State management complexity | Low | Medium | Use proven pattern from Sessions.tsx |
| Breaking existing workflows | Medium | High | Maintain backward compatibility, add redirects |

## Future Enhancements

1. **Lazy Loading**: If bundle size becomes concern, lazy load tab views
2. **Tab Badges**: Show counts (e.g., "3 projects", "Setup incomplete")
3. **Keyboard Shortcuts**: Ctrl+1/2/3 to switch between tabs
4. **Tab Persistence**: Remember last visited tab per user
5. **Mobile Optimization**: Swipe gesture to change tabs on touch devices
