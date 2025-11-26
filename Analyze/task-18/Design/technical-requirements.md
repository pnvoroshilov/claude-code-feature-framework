# Technical Requirements: Merge Projects Section

## Task Overview
**Task ID**: 18
**Task Title**: Merge Projects, Project Instructions, Project Setup into one unified section with tabs
**Complexity**: MODERATE

## Summary
Consolidate three separate project-related pages (ProjectManager, ProjectInstructions, ProjectSetup) into a single unified Projects page with tabbed navigation. This follows the established pattern used in Sessions.tsx for consistent UX.

---

## What to Change

### 1. Create New Unified Component: `Projects.tsx`

**Location**: `worktrees/task-18/claudetask/frontend/src/pages/Projects.tsx`

**Purpose**: Replace three separate pages with a single tabbed interface

**Implementation Details**:
- **Tab Structure**: 3 tabs with URL-based state management
  - Tab 1: "Projects" (default) - shows project list (current ProjectManager content)
  - Tab 2: "Instructions" - shows custom instructions editor (current ProjectInstructions content)
  - Tab 3: "Setup" - shows project setup wizard (current ProjectSetup content)

- **URL Routing Pattern** (following Sessions.tsx):
  - `/projects` → redirects to `/projects/list`
  - `/projects/list` → Projects list tab
  - `/projects/instructions` → Instructions editor tab
  - `/projects/setup` → Setup wizard tab

- **State Management**:
  - Use `useLocation()` and `useNavigate()` for URL-based tab state
  - Implement `useEffect` to sync URL with active tab
  - Handle default route (`/projects` → `/projects/list`)

**Code Structure**:
```typescript
type TabValue = 'list' | 'instructions' | 'setup';

const Projects: React.FC = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const [currentTab, setCurrentTab] = useState<TabValue>('list');

  // URL-based tab state management (similar to Sessions.tsx lines 105-117)
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

  const handleTabChange = (_event: React.SyntheticEvent, newValue: TabValue) => {
    setCurrentTab(newValue);
    navigate(`/projects/${newValue}`, { replace: true });
  };

  return (
    <Container maxWidth="xl" sx={{ py: 4 }}>
      {/* Page Header */}
      <Box sx={{ mb: 4 }}>
        <Typography variant="h3" component="h1">Projects</Typography>
        <Typography variant="body1" color="text.secondary">
          Manage projects, configure instructions, and set up new projects
        </Typography>
      </Box>

      {/* Tab Navigation */}
      <Tabs value={currentTab} onChange={handleTabChange}>
        <Tab label="Projects" value="list" />
        <Tab label="Instructions" value="instructions" />
        <Tab label="Setup" value="setup" />
      </Tabs>

      {/* Tab Panels */}
      <Box role="tabpanel" hidden={currentTab !== 'list'}>
        {currentTab === 'list' && <ProjectListView />}
      </Box>
      <Box role="tabpanel" hidden={currentTab !== 'instructions'}>
        {currentTab === 'instructions' && <ProjectInstructionsView />}
      </Box>
      <Box role="tabpanel" hidden={currentTab !== 'setup'}>
        {currentTab === 'setup' && <ProjectSetupView />}
      </Box>
    </Container>
  );
};
```

### 2. Extract Component Views

**Create 3 Sub-Components** (extract existing logic):

**a) `ProjectListView.tsx`**
- **Location**: `worktrees/task-18/claudetask/frontend/src/components/projects/ProjectListView.tsx`
- **Source**: Extract from `ProjectManager.tsx` (lines 210-798)
- **Changes**:
  - Remove Container wrapper (parent handles it)
  - Remove page header (handled by parent)
  - Keep all project list logic, table, dialogs, menus

**b) `ProjectInstructionsView.tsx`**
- **Location**: `worktrees/task-18/claudetask/frontend/src/components/projects/ProjectInstructionsView.tsx`
- **Source**: Extract from `ProjectInstructions.tsx` (lines 79-378)
- **Changes**:
  - Remove Container wrapper
  - Remove page header
  - Keep editor, save functionality, alerts

**c) `ProjectSetupView.tsx`**
- **Location**: `worktrees/task-18/claudetask/frontend/src/components/projects/ProjectSetupView.tsx`
- **Source**: Extract from `ProjectSetup.tsx` (lines 45-783)
- **Changes**:
  - Remove Container wrapper
  - Remove page header and icon
  - Keep stepper, form, initialization logic

### 3. Update Routing Configuration

**File**: `worktrees/task-18/claudetask/frontend/src/App.tsx`

**Current Routes** (lines 78-92):
```typescript
<Route path="/projects" element={<ProjectManager />} />
<Route path="/instructions" element={<ProjectInstructions />} />
<Route path="/setup" element={<ProjectSetup />} />
```

**New Routes**:
```typescript
<Route path="/projects/*" element={<Projects />} />
<Route path="/projects/:projectId/files" element={<FileBrowser />} />
// Remove: /instructions and /setup routes
```

**Why**:
- `/projects/*` handles all sub-routes internally
- Keeps FileBrowser route for backward compatibility
- Instructions and Setup are now sub-tabs, not separate routes

### 4. Update Sidebar Navigation

**File**: `worktrees/task-18/claudetask/frontend/src/components/Sidebar.tsx`

**Current Menu Items** (lines 45-58):
```typescript
{ text: 'Projects', icon: <ProjectIcon />, path: '/projects' },
{ text: 'Project Instructions', icon: <InstructionsIcon />, path: '/instructions' },
{ text: 'Project Setup', icon: <SetupIcon />, path: '/setup' },
```

**New Menu Items**:
```typescript
{ text: 'Projects', icon: <ProjectIcon />, path: '/projects' },
// Remove: Project Instructions and Project Setup items
```

**Active State Logic** (update line 171-173):
```typescript
const isActive = item.path === '/projects'
  ? location.pathname.startsWith('/projects')
  : location.pathname === item.path;
```

**Why**:
- Single "Projects" menu item
- Highlights when any `/projects/*` route is active
- Matches Sessions pattern

### 5. Clean Up Old Files

**After testing, remove**:
- `claudetask/frontend/src/pages/ProjectManager.tsx`
- `claudetask/frontend/src/pages/ProjectInstructions.tsx`
- `claudetask/frontend/src/pages/ProjectSetup.tsx`

**Why**: Replaced by new unified structure

---

## Where to Make Changes

| File | Action | Lines | Description |
|------|--------|-------|-------------|
| `src/pages/Projects.tsx` | **CREATE** | - | New unified component with tabs |
| `src/components/projects/ProjectListView.tsx` | **CREATE** | - | Extract from ProjectManager |
| `src/components/projects/ProjectInstructionsView.tsx` | **CREATE** | - | Extract from ProjectInstructions |
| `src/components/projects/ProjectSetupView.tsx` | **CREATE** | - | Extract from ProjectSetup |
| `src/App.tsx` | **MODIFY** | 78-92 | Update routes: `/projects/*` |
| `src/components/Sidebar.tsx` | **MODIFY** | 45-58, 171-173 | Remove 2 menu items, update active logic |
| `src/pages/ProjectManager.tsx` | **DELETE** | - | After testing |
| `src/pages/ProjectInstructions.tsx` | **DELETE** | - | After testing |
| `src/pages/ProjectSetup.tsx` | **DELETE** | - | After testing |

---

## Why These Changes

### Business Justification
1. **Improved UX**: All project-related functionality in one place
2. **Reduced Navigation**: Fewer sidebar items, cleaner navigation
3. **Consistency**: Matches Sessions.tsx tabbed pattern
4. **Context Preservation**: Users stay in "Projects" context

### Technical Justification
1. **Established Pattern**: Follows Sessions.tsx implementation (proven pattern)
2. **URL-Based State**: Browser back/forward work correctly
3. **Code Reuse**: Existing logic moved, not rewritten
4. **Maintainability**: Related features grouped logically

### Design Decisions
1. **Why Tabs vs Separate Pages?**
   - Sessions.tsx precedent shows this works well
   - Related functionality benefits from context sharing
   - Reduces cognitive load (single "Projects" concept)

2. **Why URL-Based Tab State?**
   - Deep linking support (`/projects/setup`)
   - Browser navigation (back/forward) works
   - Shareable URLs for specific tabs

3. **Why Extract to Sub-Components?**
   - Keeps parent component clean
   - Maintains testability
   - Easier to refactor individual views

---

## Integration Points

### 1. ProjectContext
- **Used by**: ProjectInstructionsView (needs selectedProject)
- **Action**: Import and use in sub-components
- **No changes needed**: Context provider in App.tsx already wraps all routes

### 2. React Query
- **Used by**: All three views (project list, API calls)
- **Action**: Import useQuery/useMutation in sub-components
- **No changes needed**: QueryClient in App.tsx already configured

### 3. Navigation
- **Used by**: ProjectListView (navigate to file browser)
- **Action**: Import useNavigate in sub-components
- **Update**: Ensure `/projects/:projectId/files` route still works

### 4. API Services
- **Used by**: All views (getProjects, updateProject, etc.)
- **Action**: Import from `../services/api` in sub-components
- **No changes needed**: API layer unchanged

---

## Dependencies

### New Component Structure
```
Projects.tsx (parent)
├── ProjectListView.tsx (manages project list, table, dialogs)
├── ProjectInstructionsView.tsx (manages custom instructions editor)
└── ProjectSetupView.tsx (manages project initialization wizard)
```

### Shared Dependencies
- React Router: `useLocation`, `useNavigate`, `Link`
- MUI Components: `Tabs`, `Tab`, `Container`, `Box`
- React Query: `useQuery`, `useMutation`
- Project Context: `useProject`

---

## Testing Considerations

### Manual Testing Checklist
1. **Navigation**:
   - [ ] `/projects` redirects to `/projects/list`
   - [ ] Click "Projects" in sidebar → shows Projects List tab
   - [ ] Tab navigation updates URL correctly
   - [ ] Browser back/forward works with tabs

2. **Functionality**:
   - [ ] Projects List: CRUD operations work
   - [ ] Instructions: Save/load custom instructions
   - [ ] Setup: Initialize new project
   - [ ] File browser navigation still works

3. **UI/UX**:
   - [ ] Sidebar highlights "Projects" for all `/projects/*` routes
   - [ ] Tab styling matches Sessions.tsx
   - [ ] Responsive design works on mobile
   - [ ] No layout shifts when switching tabs

### Edge Cases
- Navigating directly to `/projects/setup` via URL
- Refreshing page while on a specific tab
- Using browser back after creating project in Setup tab
- Active project context when switching tabs

---

## Migration Strategy

### Phase 1: Create New Structure (No Breaking Changes)
1. Create `Projects.tsx` with tabs
2. Create 3 view components
3. Test new routes alongside old routes

### Phase 2: Update Navigation
1. Update `App.tsx` routes
2. Update `Sidebar.tsx` menu items
3. Add redirects from old routes if needed

### Phase 3: Clean Up (After Testing)
1. Remove old page components
2. Remove unused imports
3. Update documentation

---

## Performance Considerations

### Tab Content Rendering
- **Strategy**: Conditional rendering with `hidden` attribute
- **Why**: Prevents unmounting/remounting when switching tabs
- **Precedent**: Sessions.tsx lines 521-537
- **Trade-off**: All tab content in DOM, but only visible tab interactive

### Code Splitting (Optional Future Enhancement)
- Could lazy-load tab views if bundle size becomes concern
- Not necessary for initial implementation

---

## Accessibility

### Tab Navigation
- Use proper ARIA attributes: `role="tabpanel"`, `aria-labelledby`, `id`
- Follow Sessions.tsx pattern (lines 249-260)
- Ensure keyboard navigation works (Tab, Arrow keys)

### Screen Readers
- Announce tab changes
- Maintain focus management when switching tabs
- Label tabs clearly ("Projects", "Instructions", "Setup")

---

## File Size Estimates

- **Projects.tsx**: ~200 lines (parent with tabs)
- **ProjectListView.tsx**: ~600 lines (from ProjectManager)
- **ProjectInstructionsView.tsx**: ~300 lines (from ProjectInstructions)
- **ProjectSetupView.tsx**: ~400 lines (from ProjectSetup)
- **Total**: ~1500 lines across 4 new files vs 3 old files (~1800 lines)

**Net Result**: Slightly smaller, better organized code

---

## Documentation Updates Needed

### User-Facing
- Update screenshots showing new Projects section
- Document tab navigation in user guide

### Developer-Facing
- Update component architecture diagram
- Document new component structure in README
- Add ADR for this consolidation decision

---

## Success Criteria

1. ✅ All project functionality accessible from single "Projects" menu item
2. ✅ Tab navigation works with URL state
3. ✅ Browser back/forward work correctly
4. ✅ No functionality lost from consolidation
5. ✅ UI consistent with Sessions.tsx pattern
6. ✅ Sidebar reduced by 2 items
7. ✅ Deep linking works (`/projects/setup`)
8. ✅ Active project context preserved across tabs
