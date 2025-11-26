# File Structure Changes - Task 18

## Before (3 Separate Pages)

```
claudetask/frontend/src/
├── pages/
│   ├── ProjectManager.tsx        ← Projects list
│   ├── ProjectInstructions.tsx   ← Instructions editor
│   └── ProjectSetup.tsx          ← Setup wizard
│
├── components/
│   └── Sidebar.tsx
│
└── App.tsx

Sidebar Menu:
├── Dashboard
├── Task Board
├── Projects                 ← /projects (ProjectManager)
├── Sessions
├── Skills
├── Hooks
├── MCP Configs
├── Logs
├── Subagents
├── Project Instructions     ← /instructions (ProjectInstructions)
├── Project Setup           ← /setup (ProjectSetup)
└── Settings
```

## After (Unified Projects Section)

```
claudetask/frontend/src/
├── pages/
│   ├── Projects.tsx              ← NEW: Main component with tabs
│   │
│   ├── ProjectManager.tsx        ← KEEP (delete in PR)
│   ├── ProjectInstructions.tsx   ← KEEP (delete in PR)
│   └── ProjectSetup.tsx          ← KEEP (delete in PR)
│
├── components/
│   ├── projects/                 ← NEW: View components directory
│   │   ├── ProjectListView.tsx         ← Extracted from ProjectManager
│   │   ├── ProjectInstructionsView.tsx ← Extracted from ProjectInstructions
│   │   └── ProjectSetupView.tsx        ← Extracted from ProjectSetup
│   │
│   └── Sidebar.tsx               ← MODIFIED: Removed 2 menu items
│
└── App.tsx                       ← MODIFIED: Updated routes

Sidebar Menu:
├── Dashboard
├── Task Board
├── Projects                 ← /projects/* (Projects with tabs)
├── Sessions
├── Skills
├── Hooks
├── MCP Configs
├── Logs
├── Subagents
└── Settings
```

## URL Structure

### Before:
```
/projects           → ProjectManager.tsx
/instructions       → ProjectInstructions.tsx
/setup              → ProjectSetup.tsx
```

### After:
```
/projects           → Redirect to /projects/list
/projects/list      → Projects.tsx → ProjectListView
/projects/instructions → Projects.tsx → ProjectInstructionsView
/projects/setup     → Projects.tsx → ProjectSetupView
```

## Component Hierarchy

### Projects.tsx (Main Component)
```
<Container>
  <Header />
  <Tabs>
    <Tab value="list" />
    <Tab value="instructions" />
    <Tab value="setup" />
  </Tabs>
  
  <TabPanel value="list">
    <ProjectListView />
  </TabPanel>
  
  <TabPanel value="instructions">
    <ProjectInstructionsView />
  </TabPanel>
  
  <TabPanel value="setup">
    <ProjectSetupView />
  </TabPanel>
</Container>
```

## Data Flow

```
App.tsx
  └─ Route: /projects/*
       └─ Projects.tsx
            ├─ useLocation() ────────────┐
            ├─ useNavigate() ────────────┤
            ├─ Tab state management ─────┤
            │                            │
            ├─ Tab: "list" ──────────────┤
            │   └─ ProjectListView       │
            │        ├─ useQuery()        │
            │        ├─ useMutation()     │
            │        └─ useNavigate() ────┤
            │                            │
            ├─ Tab: "instructions" ──────┤
            │   └─ ProjectInstructionsView
            │        ├─ useProject() ────┤
            │        └─ axios.get/put ───┤
            │                            │
            └─ Tab: "setup" ─────────────┤
                └─ ProjectSetupView      │
                     ├─ useMutation()     │
                     └─ DirectoryBrowser ─┘
```

## Routing Flow

```
User Navigation Flow:

1. Click "Projects" in sidebar
   → Navigate to /projects
   → Auto-redirect to /projects/list
   → Show ProjectListView

2. Click "Instructions" tab
   → Navigate to /projects/instructions
   → Show ProjectInstructionsView
   → URL changes in browser

3. Click "Setup" tab
   → Navigate to /projects/setup
   → Show ProjectSetupView
   → URL changes in browser

4. Browser Back button
   → Navigate back in history
   → Tab updates to match URL
   → View switches automatically

5. Direct URL access (bookmark)
   → Visit /projects/setup directly
   → Tab highlights "Setup"
   → ProjectSetupView renders
```

## Code Changes Summary

### New Files (4):
1. `pages/Projects.tsx` - Main tabbed container
2. `components/projects/ProjectListView.tsx` - Projects table view
3. `components/projects/ProjectInstructionsView.tsx` - Instructions editor view
4. `components/projects/ProjectSetupView.tsx` - Setup wizard view

### Modified Files (2):
1. `App.tsx` - Routes and imports
2. `components/Sidebar.tsx` - Menu items and active logic

### Preserved Files (3):
*Will be deleted in PR after testing*
1. `pages/ProjectManager.tsx`
2. `pages/ProjectInstructions.tsx`
3. `pages/ProjectSetup.tsx`

## Size Comparison

### Before:
```
ProjectManager.tsx:      29,070 bytes
ProjectInstructions.tsx: 12,314 bytes
ProjectSetup.tsx:        30,371 bytes
Total:                   71,755 bytes
```

### After:
```
Projects.tsx:                4,401 bytes (main container)
ProjectListView.tsx:        27,146 bytes (extracted content)
ProjectInstructionsView.tsx: 10,763 bytes (extracted content)
ProjectSetupView.tsx:       28,865 bytes (extracted content)
Total:                      71,175 bytes (580 bytes saved)
```

**Savings**: 580 bytes from removing duplicate Container/Header code

## State Management

### ProjectListView:
- React Query: useQuery for projects, activeProject
- React Query: useMutation for CRUD operations
- Local state: dialogs, menus, alerts

### ProjectInstructionsView:
- useProject() context hook for selected project
- axios for API calls
- Local state: instructions, loading, saving

### ProjectSetupView:
- React Query: useMutation for initialization
- Local state: stepper, form data, browser dialog
- DirectoryBrowser component for folder selection

## Navigation Guards

### Sidebar Active State Logic:
```typescript
const isActive = 
  item.path === '/sessions'
    ? location.pathname.startsWith('/sessions')
  : item.path === '/projects'
    ? location.pathname.startsWith('/projects') && 
      !location.pathname.includes('/files')
  : location.pathname === item.path;
```

Explanation:
- Sessions: Highlight for all `/sessions/*` routes
- Projects: Highlight for `/projects/*` BUT NOT `/projects/:id/files`
- Others: Exact match only

## Tab Synchronization

### URL ↔ Tab State:
```typescript
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

This ensures:
1. URL changes update tab state
2. Tab clicks update URL
3. Browser back/forward works
4. Direct URL access works
5. Default redirect works
