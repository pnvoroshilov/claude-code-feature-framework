# Design Documentation: Merge Projects Section (Task #18)

## Overview

This directory contains the complete technical design and architecture documentation for consolidating three separate project-related pages into a unified tabbed interface.

**Task Complexity**: MODERATE

---

## Documentation Files

### 1. [technical-requirements.md](./technical-requirements.md)
**What/Where/Why to change**

**Key Sections**:
- **What to Change**: 9 specific file changes detailed
- **Where**: Exact file paths and line numbers
- **Why**: Business and technical justification
- **Integration Points**: ProjectContext, React Query, Navigation, API Services
- **Testing Checklist**: Manual testing scenarios and edge cases
- **Success Criteria**: 8 measurable outcomes

**Quick Reference**:
- Create 1 new parent component: `Projects.tsx`
- Extract 3 view components: `ProjectListView.tsx`, `ProjectInstructionsView.tsx`, `ProjectSetupView.tsx`
- Update routing in `App.tsx`
- Update sidebar in `Sidebar.tsx`
- Delete 3 old page components after testing

**Page Count**: ~8 pages (concise)

---

### 2. [architecture-decisions.md](./architecture-decisions.md)
**Architecture Decision Records (ADRs)**

**5 Key ADRs**:
1. **ADR-001**: Consolidate into Tabbed Interface
   - **Decision**: Merge 3 pages into 1 with tabs
   - **Rationale**: Pattern consistency, improved UX, reduced navigation friction

2. **ADR-002**: URL-Based Tab State Management
   - **Decision**: Use path segments (`/projects/setup`) not query params
   - **Rationale**: Deep linking, browser navigation, consistency with Sessions.tsx

3. **ADR-003**: Extract Views as Separate Components
   - **Decision**: Create 3 sub-components instead of inline content
   - **Rationale**: Maintainability, testability, clear separation of concerns

4. **ADR-004**: Conditional Rendering vs Lazy Loading
   - **Decision**: Use conditional rendering with `hidden` attribute
   - **Rationale**: Fast tab switching, state preservation, consistency with Sessions

5. **ADR-005**: Sidebar Consolidation
   - **Decision**: Single "Projects" menu item instead of 3
   - **Rationale**: Reduced clutter, clearer navigation, matches Sessions pattern

**Each ADR includes**:
- Context and problem statement
- Decision and rationale
- Consequences (positive/negative/neutral)
- Alternatives considered
- Implementation notes

**Page Count**: ~6 pages

---

### 3. [conflict-analysis.md](./conflict-analysis.md)
**Conflict analysis with other active tasks**

**Overall Risk**: **LOW**

**Key Sections**:
- **Active Tasks Review**: Potential conflict areas
- **File-Level Analysis**: High/medium/low risk files
- **Concurrent Task Scenarios**: 4 common conflict scenarios with resolutions
- **Git Merge Conflict Hotspots**: Predicted conflicts in App.tsx and Sidebar.tsx
- **Coordination Recommendations**: Before/during/after implementation checklist
- **Rollback Strategy**: 3 rollback options if issues occur
- **Testing Strategy**: Pre-merge and post-merge testing

**Risk Assessment**:
| Category | Risk Level |
|----------|-----------|
| File Conflicts | LOW |
| Routing Conflicts | MEDIUM |
| Sidebar Conflicts | MEDIUM |
| API Conflicts | NONE |
| State Conflicts | LOW |

**Recommendation**: ✅ **PROCEED WITH IMPLEMENTATION**

**Page Count**: ~4 pages

---

## Quick Start Guide

### For Developers Implementing This Task

1. **Read First**: `technical-requirements.md` (understand what to build)
2. **Review Decisions**: `architecture-decisions.md` (understand why these choices)
3. **Check Conflicts**: `conflict-analysis.md` (coordinate with team)
4. **Follow Reference**: Look at `Sessions.tsx` for implementation pattern

### Implementation Order

```
Phase 1: Create New Structure (No Breaking Changes)
├── 1. Create Projects.tsx with tabs
├── 2. Create ProjectListView.tsx (extract from ProjectManager)
├── 3. Create ProjectInstructionsView.tsx (extract from ProjectInstructions)
└── 4. Create ProjectSetupView.tsx (extract from ProjectSetup)

Phase 2: Update Navigation
├── 1. Update App.tsx routes
├── 2. Update Sidebar.tsx menu items
└── 3. Add redirects for old routes

Phase 3: Clean Up (After Testing)
├── 1. Remove old page components
├── 2. Remove unused imports
└── 3. Update documentation
```

### Key Files to Reference

**Pattern Reference**:
- `claudetask/frontend/src/pages/Sessions.tsx` (lines 92-537)
  - URL-based tab state management
  - Tab navigation and styling
  - Conditional rendering pattern

**Component Structure**:
```
Projects.tsx (parent)
├── Tab Navigation (MUI Tabs)
├── URL State Management (useLocation/useNavigate)
└── Tab Panels
    ├── ProjectListView (project list, CRUD)
    ├── ProjectInstructionsView (instructions editor)
    └── ProjectSetupView (initialization wizard)
```

---

## Design Highlights

### Pattern Consistency
- ✅ Follows Sessions.tsx tabbed navigation pattern
- ✅ URL-based state management for deep linking
- ✅ Consistent MUI styling and theming
- ✅ Proper ARIA attributes for accessibility

### Code Organization
- ✅ Parent component: ~200 lines (focused on navigation)
- ✅ View components: 300-600 lines each (single responsibility)
- ✅ Total: ~1500 lines across 4 files (vs 1800 in 3 old files)
- ✅ Better separation of concerns

### User Experience
- ✅ Single "Projects" concept (not 3 separate pages)
- ✅ All project functionality in one place
- ✅ Sidebar reduced from 8 to 6 items
- ✅ Browser back/forward work correctly
- ✅ Shareable URLs to specific tabs

### Technical Benefits
- ✅ Deep linking support (`/projects/setup`)
- ✅ State preservation across tabs
- ✅ No functionality lost
- ✅ Easy to test and maintain
- ✅ Future-proof for enhancements

---

## Validation Checklist

### Before Implementation
- [ ] Read all 3 design documents
- [ ] Review Sessions.tsx reference implementation
- [ ] Check for active branches touching affected files
- [ ] Announce in team channel about planned changes

### During Implementation
- [ ] Create feature branch: `feature/task-18-merge-projects`
- [ ] Follow technical-requirements.md step-by-step
- [ ] Reference Sessions.tsx for patterns
- [ ] Commit incrementally (routes, sidebar, components)
- [ ] Open draft PR early for visibility

### Before Merge
- [ ] All manual tests pass (see technical-requirements.md)
- [ ] No console errors or warnings
- [ ] Routing works (old routes redirect correctly)
- [ ] Sidebar highlights correctly
- [ ] Tab navigation smooth and responsive
- [ ] Code review approved
- [ ] Conflicts resolved with main branch

### After Merge
- [ ] Monitor for routing errors
- [ ] Check user feedback
- [ ] Update user documentation
- [ ] Close task in task board

---

## Success Criteria (from technical-requirements.md)

1. ✅ All project functionality accessible from single "Projects" menu item
2. ✅ Tab navigation works with URL state
3. ✅ Browser back/forward work correctly
4. ✅ No functionality lost from consolidation
5. ✅ UI consistent with Sessions.tsx pattern
6. ✅ Sidebar reduced by 2 items
7. ✅ Deep linking works (`/projects/setup`)
8. ✅ Active project context preserved across tabs

---

## Key Metrics

| Metric | Before | After | Improvement |
|--------|--------|-------|-------------|
| Sidebar Items | 8 | 6 | -25% |
| Page Components | 3 | 1 | Consolidated |
| Navigation Clicks | 2-3 | 1-2 | Reduced |
| Code Lines | 1800 | 1500 | -16% |
| Component Files | 3 | 4 | Better organized |

---

## Questions?

**For Technical Details**: See `technical-requirements.md`
**For Design Rationale**: See `architecture-decisions.md`
**For Conflict Coordination**: See `conflict-analysis.md`

**Implementation Reference**: `claudetask/frontend/src/pages/Sessions.tsx`

**Team Communication**: Announce in channel before starting, coordinate routing/sidebar changes

---

## Document Metadata

- **Created**: 2025-01-26
- **Task ID**: 18
- **Complexity**: MODERATE
- **Estimated Effort**: 2-3 days
- **Risk Level**: LOW
- **Recommendation**: PROCEED
- **Total Documentation**: ~18 pages across 3 files
