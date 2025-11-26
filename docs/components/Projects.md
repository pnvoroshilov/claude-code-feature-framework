# Projects Component

Unified tab interface for comprehensive project management in the ClaudeTask Framework.

**Status**: Production Ready (v1.0)
**Location**: `claudetask/frontend/src/pages/Projects.tsx`
**Last Updated**: 2025-11-26

## Overview

The Projects component provides a unified interface for managing all aspects of ClaudeTask projects through an intuitive tabbed layout. It consolidates project list management, configuration instructions, and project setup into a single cohesive interface.

## Architecture

### Component Structure

```
Projects.tsx (Main Container)
├── ProjectListView.tsx (Projects Tab)
├── ProjectInstructionsView.tsx (Instructions Tab)
└── ProjectSetupView.tsx (Setup Tab)
```

### Tab Navigation

The component uses URL-based tab state management with three main sections:

1. **Projects** (`/projects/list`) - Project list and management
2. **Instructions** (`/projects/instructions`) - Project configuration
3. **Setup** (`/projects/setup`) - New project initialization

## Features

### Tabbed Interface
- URL-based tab navigation with clean routing
- Persistent tab state across page refreshes
- Smooth tab transitions with Material-UI Tabs component
- Dynamic accent colors matching theme
- Mobile-responsive scrollable tabs

### Projects Tab (ProjectListView)

**Features**:
- Project list with comprehensive metadata display
- Search and filter capabilities
- Project activation/deactivation
- Framework update functionality
- Project editing (name, GitHub repo)
- Project deletion with confirmation
- Active project indicator
- Quick navigation to file browser

**Display Information**:
- Project name with icon
- Full file system path (with tooltip)
- Technology stack badges (auto-detected)
- GitHub repository link (if configured)
- Active/Inactive status chip
- Creation date
- Context menu for actions

**Actions**:
- Browse Files - Navigate to project file browser
- Activate Project - Set as active project
- Update Framework - Sync framework files
- Edit Project - Modify project settings
- Delete Project - Remove project with confirmation

### Instructions Tab (ProjectInstructionsView)

**Features**:
- View and edit project CLAUDE.md configuration
- Syntax highlighting for markdown
- Live preview of changes
- Version control for configuration changes
- Template selection for quick setup

### Setup Tab (ProjectSetupView)

**Features**:
- Initialize new ClaudeTask projects
- Project path selection with directory browser
- Technology stack auto-detection
- GitHub repository configuration
- Framework file installation
- CLAUDE.md generation
- Database migration execution

## Props

```typescript
// No props - self-contained page component
```

## State Management

### Local State

```typescript
const [currentTab, setCurrentTab] = useState<TabValue>('list');

type TabValue = 'list' | 'instructions' | 'setup';
```

### URL Synchronization

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

## API Integration

The component delegates API calls to sub-components:

### ProjectListView APIs
```
GET /api/projects                    # List all projects
GET /api/projects/active             # Get active project
PUT /api/projects/{id}               # Update project
DELETE /api/projects/{id}            # Delete project
POST /api/projects/{id}/activate     # Activate project
POST /api/projects/{id}/update-framework  # Update framework files
```

### ProjectInstructionsView APIs
```
GET /api/projects/{id}/instructions  # Get CLAUDE.md
PUT /api/projects/{id}/instructions  # Update CLAUDE.md
```

### ProjectSetupView APIs
```
POST /api/projects                   # Create new project
POST /api/projects/detect-tech-stack # Auto-detect technologies
POST /api/projects/init              # Initialize framework files
```

## Usage Example

```typescript
import { BrowserRouter } from 'react-router-dom';
import Projects from './pages/Projects';

function App() {
  return (
    <BrowserRouter>
      <Projects />
    </BrowserRouter>
  );
}
```

### Navigation

```typescript
// Navigate to Projects list
navigate('/projects/list');

// Navigate to Instructions
navigate('/projects/instructions');

// Navigate to Setup
navigate('/projects/setup');
```

## Styling

### Theme Integration

```typescript
const theme = useTheme();
const tabAccentColor = theme.palette.primary.main;

// Gradient header text
sx={{
  background: `linear-gradient(135deg, ${tabAccentColor}, ${alpha(tabAccentColor, 0.7)})`,
  WebkitBackgroundClip: 'text',
  WebkitTextFillColor: 'transparent',
}}

// Tab indicator
sx={{
  '& .MuiTabs-indicator': {
    backgroundColor: tabAccentColor,
    height: 3,
    borderRadius: '3px 3px 0 0',
  },
}}
```

### Responsive Design

```typescript
<Tabs
  variant="scrollable"
  scrollButtons="auto"
  sx={{
    '& .MuiTab-root': {
      minWidth: { xs: 120, md: 160 },
      fontSize: { xs: '0.875rem', md: '1rem' },
    }
  }}
>
```

## Sub-Components

### ProjectListView

**Location**: `claudetask/frontend/src/components/projects/ProjectListView.tsx`

**Key Features**:
- Table-based project display
- Context menu for project actions
- Edit project dialog with form validation
- Alert notifications for success/error states
- Framework update progress tracking
- Project activation with confirmation
- Delete with safety checks

**Project Data Structure**:
```typescript
interface Project {
  id: string;
  name: string;
  path: string;
  tech_stack: string[];
  github_repo?: string;
  is_active: boolean;
  created_at: string;
}
```

**Context Menu Actions**:
- Browse Files
- Activate Project (if not active)
- Update Framework
- Edit Project
- Delete Project (destructive, red color)

### ProjectInstructionsView

**Location**: `claudetask/frontend/src/components/projects/ProjectInstructionsView.tsx`

**Key Features**:
- Markdown editor for CLAUDE.md
- Syntax highlighting
- Live preview
- Save with validation
- Revert changes
- Template selection

### ProjectSetupView

**Location**: `claudetask/frontend/src/components/projects/ProjectSetupView.tsx`

**Key Features**:
- Multi-step wizard
- Directory picker
- Technology detection
- Configuration preview
- Progress tracking
- Error handling

## User Experience

### Navigation Flow

```
1. User visits /projects
   → Auto-redirects to /projects/list

2. User clicks "Instructions" tab
   → Updates URL to /projects/instructions
   → Loads ProjectInstructionsView

3. User clicks "New Project" button
   → Programmatically navigates to /projects/setup
   → Opens ProjectSetupView
```

### Visual Feedback

- **Tab Selection**: Indicator bar moves smoothly
- **Hover States**: Tab color changes on hover
- **Active States**: Selected tab uses accent color
- **Loading States**: Skeleton loaders during data fetch
- **Success/Error**: Alert banners for operations
- **Confirmations**: Dialogs for destructive actions

## Error Handling

```typescript
// Component-level error handling
if (error) {
  return (
    <Alert severity="error">
      Failed to load projects. Please try again.
    </Alert>
  );
}

// Sub-component error states
const [deleteError, setDeleteError] = useState<string | null>(null);

// Display error with auto-dismiss
{deleteError && (
  <Alert severity="error" onClose={() => setDeleteError(null)}>
    {deleteError}
  </Alert>
)}
```

## Accessibility

- **ARIA Labels**: All tabs have proper aria-controls and id attributes
- **Keyboard Navigation**: Full keyboard support for tab switching
- **Screen Readers**: Proper role="tabpanel" for content areas
- **Focus Management**: Maintains focus on tab change

```typescript
<Tab
  label="Projects"
  value="list"
  id="tab-list"
  aria-controls="tabpanel-list"
/>

<Box
  role="tabpanel"
  hidden={currentTab !== 'list'}
  id="tabpanel-list"
  aria-labelledby="tab-list"
>
```

## Performance

### Conditional Rendering

Only active tab content is mounted:

```typescript
{currentTab === 'list' && <ProjectListView />}
{currentTab === 'instructions' && <ProjectInstructionsView />}
{currentTab === 'setup' && <ProjectSetupView />}
```

### Lazy Loading

Sub-components are loaded only when needed, reducing initial bundle size.

### Memoization

Sub-components use React.memo where appropriate to prevent unnecessary re-renders.

## Related Components

- **[FileBrowser](./FileBrowser.md)** - Accessed from project context menu
- **[TaskBoard](./TaskBoard.md)** - Uses active project context
- **[Settings](./Settings.md)** - Project settings configuration
- **Sidebar** - Navigation to Projects page

## Future Enhancements

1. **Project Templates**: Pre-configured project types (React, FastAPI, etc.)
2. **Git Integration**: Clone from GitHub directly in setup wizard
3. **Project Search**: Full-text search across all project properties
4. **Bulk Operations**: Select multiple projects for batch actions
5. **Project Import/Export**: Backup and restore project configurations
6. **Project Analytics**: Usage statistics and metrics dashboard
7. **Favoriting**: Mark frequently used projects
8. **Recent Projects**: Quick access to recently opened projects
9. **Project Groups**: Organize projects into collections
10. **Team Sharing**: Share project configurations with team

## Troubleshooting

### Issue: Tab not switching on navigation

**Cause**: URL state not synchronized with component state

**Solution**: Check useEffect dependencies and ensure navigate is called correctly:

```typescript
useEffect(() => {
  // Ensure navigate is in dependency array
}, [location.pathname, navigate]);
```

### Issue: Sub-component not loading

**Cause**: Conditional rendering may be preventing mount

**Solution**: Verify currentTab state matches expected value:

```typescript
console.log('Current tab:', currentTab);
// Should match one of: 'list' | 'instructions' | 'setup'
```

### Issue: Tab indicator not aligned

**Cause**: Tab value mismatch with Tabs component

**Solution**: Ensure value prop matches tab values:

```typescript
<Tabs value={currentTab} onChange={handleTabChange}>
  <Tab value="list" />
  <Tab value="instructions" />
  <Tab value="setup" />
</Tabs>
```

## Testing

### Manual Testing Checklist

- [ ] Navigate to /projects auto-redirects to /projects/list
- [ ] Clicking each tab updates URL and shows correct content
- [ ] Browser back/forward buttons work correctly
- [ ] Page refresh maintains current tab
- [ ] All sub-component features work in their tabs
- [ ] Mobile layout shows scrollable tabs
- [ ] Tab indicator animates smoothly
- [ ] Keyboard navigation (arrow keys) works

### API Testing

```bash
# Test project list endpoint
curl http://localhost:3333/api/projects

# Test active project endpoint
curl http://localhost:3333/api/projects/active

# Test project update
curl -X PUT http://localhost:3333/api/projects/{id} \
  -H "Content-Type: application/json" \
  -d '{"name":"Updated Name"}'
```

## Migration Notes

### From Separate Pages to Unified Tabs

**Previous Structure**:
```
/project-manager    # Project list page
/project-instructions  # Instructions page
/project-setup      # Setup page
```

**New Structure**:
```
/projects/list          # Unified with tabs
/projects/instructions  # Unified with tabs
/projects/setup         # Unified with tabs
```

**Benefits**:
- Single consistent navigation path
- Faster navigation between related functions
- Shared context and state
- Better UX with tab persistence
- Reduced code duplication

## Development

### Adding a New Tab

1. Create new sub-component in `components/projects/`
2. Import component in Projects.tsx
3. Add new tab value to TabValue type
4. Add Tab element with proper labels and IDs
5. Add Box element with tabpanel role
6. Add URL route handler in useEffect
7. Update handleTabChange if needed

```typescript
// 1. Add to type
type TabValue = 'list' | 'instructions' | 'setup' | 'newTab';

// 2. Import component
import NewTabView from '../components/projects/NewTabView';

// 3. Add Tab
<Tab
  label="New Tab"
  value="newTab"
  id="tab-newtab"
  aria-controls="tabpanel-newtab"
/>

// 4. Add tabpanel
<Box
  role="tabpanel"
  hidden={currentTab !== 'newTab'}
  id="tabpanel-newtab"
  aria-labelledby="tab-newtab"
>
  {currentTab === 'newTab' && <NewTabView />}
</Box>

// 5. Add route handler
else if (path.includes('/newtab')) {
  setCurrentTab('newTab');
}
```

---

**Component Version**: 1.0
**Dependencies**: React 18.x, MUI v5, React Router v6
**Browser Support**: Modern browsers (Chrome, Firefox, Safari, Edge)
