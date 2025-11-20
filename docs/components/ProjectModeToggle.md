# ProjectModeToggle Component

Project mode selector with worktree toggle for DEVELOPMENT mode configuration.

## Overview

`ProjectModeToggle` is a compact UI component that allows users to:
1. Switch between SIMPLE and DEVELOPMENT project modes
2. Toggle Git worktree functionality in DEVELOPMENT mode
3. See real-time updates via WebSocket

**Location:** `claudetask/frontend/src/components/ProjectModeToggle.tsx`

**Status:** Active, Recently Updated (v1.1 - Worktree Toggle Added)

## Features

### Mode Toggle
- **SIMPLE Mode**: Streamlined 3-column workflow (Backlog → In Progress → Done)
- **DEVELOPMENT Mode**: Full 7-column workflow with quality gates

### Worktree Toggle (DEVELOPMENT Mode Only)
- **Enabled (Default)**: Isolated workspace per task in `worktrees/task-{id}/`
- **Disabled**: Work directly in main branch or manual feature branches
- Only visible when project mode is DEVELOPMENT
- Triggers automatic CLAUDE.md regeneration on toggle

### Real-time Updates
- WebSocket integration for instant settings synchronization
- Updates reflected across all open sessions
- No page reload required

## Component Structure

```tsx
interface ProjectModeToggleProps {
  // No props - uses ProjectContext for selected project
}

const ProjectModeToggle: React.FC = () => {
  const { selectedProject, refreshProjects } = useProject();
  const { mode: themeMode } = useThemeMode();
  const [worktreeEnabled, setWorktreeEnabled] = useState<boolean>(true);
  const [loading, setLoading] = useState<boolean>(false);

  // Load project settings on mount
  useEffect(() => {
    if (selectedProject) {
      const settings = await getProjectSettings(selectedProject.id);
      setWorktreeEnabled(settings.worktree_enabled);
    }
  }, [selectedProject]);

  // Handle mode change (SIMPLE ↔ DEVELOPMENT)
  const handleModeChange = async (newMode: string) => {
    await updateProject(selectedProject.id, {
      project_mode: newMode
    });
    await refreshProjects();
  };

  // Handle worktree toggle
  const handleWorktreeToggle = async (event) => {
    const newValue = event.target.checked;
    await updateProjectSettings(selectedProject.id, {
      worktree_enabled: newValue
    });
    setWorktreeEnabled(newValue);
    await refreshProjects(); // Triggers CLAUDE.md regeneration
  };

  return (
    <Box>
      {/* Mode Toggle Buttons */}
      <ToggleButtonGroup value={projectMode} onChange={handleModeChange}>
        <ToggleButton value="simple">
          <SimpleIcon /> SIMPLE
        </ToggleButton>
        <ToggleButton value="development">
          <DevelopmentIcon /> DEVELOPMENT
        </ToggleButton>
      </ToggleButtonGroup>

      {/* Worktree Toggle (only in DEVELOPMENT mode) */}
      {projectMode === 'development' && (
        <FormControlLabel
          control={
            <Switch
              checked={worktreeEnabled}
              onChange={handleWorktreeToggle}
              disabled={loading}
            />
          }
          label={
            <Box>
              <WorktreeIcon />
              <Typography>Worktrees</Typography>
            </Box>
          }
        />
      )}
    </Box>
  );
};
```

## State Management

### Local State
- `worktreeEnabled: boolean` - Current worktree toggle state
- `loading: boolean` - Loading indicator during API calls

### Context Dependencies
- `ProjectContext` - Selected project and refresh function
- `ThemeContext` - Current theme mode for styling

## API Integration

### Endpoints Used

#### GET `/api/projects/{id}/settings`
Get current project settings including worktree_enabled.

**Response:**
```json
{
  "id": 1,
  "project_id": "abc-123",
  "worktree_enabled": true,
  "auto_mode": false,
  "max_parallel_tasks": 3,
  "test_command": null,
  "build_command": null,
  "lint_command": null
}
```

#### PATCH `/api/projects/{id}/settings`
Update project settings.

**Request:**
```json
{
  "worktree_enabled": false
}
```

**Response:**
```json
{
  "id": 1,
  "project_id": "abc-123",
  "worktree_enabled": false,
  "auto_mode": false,
  "max_parallel_tasks": 3
}
```

**Side Effects:**
- Triggers CLAUDE.md regeneration with appropriate worktree instructions
- Broadcasts WebSocket message to all connected clients
- Updates project settings in database

#### PATCH `/api/projects/{id}`
Update project mode (SIMPLE ↔ DEVELOPMENT).

**Request:**
```json
{
  "project_mode": "development"
}
```

## Usage Example

```tsx
import ProjectModeToggle from '../components/ProjectModeToggle';

// In TaskBoard or any page with project context
const TaskBoard: React.FC = () => {
  return (
    <Box>
      <Header>
        <ProjectModeToggle />
      </Header>
      <TaskColumns />
    </Box>
  );
};
```

## Styling

### Theme Integration
Uses MUI theme with custom color scheme:

```tsx
// Mode buttons
sx={{
  bgcolor: projectMode === 'simple' ? '#10b981' : '#6366f1',
  '&:hover': {
    bgcolor: alpha(color, 0.8)
  }
}}

// Worktree toggle
sx={{
  '& .MuiSwitch-switchBase.Mui-checked': {
    color: '#6366f1',
  },
  '& .MuiSwitch-switchBase.Mui-checked + .MuiSwitch-track': {
    backgroundColor: '#6366f1',
  },
}}
```

### Responsive Behavior
- Mobile (xs): Mode buttons only, worktree label hidden
- Tablet (sm+): Full display with worktree toggle
- Desktop (lg+): All labels visible

```tsx
sx={{
  display: { xs: 'none', sm: 'flex' }, // Hide on mobile
  '& .MuiFormControlLabel-label': {
    display: { xs: 'none', lg: 'block' } // Show label on desktop
  }
}}
```

## Tooltips

### Mode Toggle Tooltips
- **SIMPLE**: "3 columns: Backlog, In Progress, Done"
- **DEVELOPMENT**: "Full workflow with Git integration"

### Worktree Toggle Tooltip
- **Enabled**: "Git worktrees enabled - Each task gets isolated workspace"
- **Disabled**: "Git worktrees disabled - Tasks work in main branch"

## Visual Design

### Color Scheme
- **SIMPLE Mode**: Green (#10b981) - Fast, simple, direct
- **DEVELOPMENT Mode**: Indigo (#6366f1) - Professional, structured
- **Worktree Toggle**: Indigo (#6366f1) when enabled

### Icons
- **SIMPLE Mode**: `Lightbulb` icon (simplicity, quick ideas)
- **DEVELOPMENT Mode**: `Code` icon (professional development)
- **Worktree Toggle**: `AccountTree` icon (branching, isolation)

## Behavior

### Mode Change Flow
```
User clicks mode button
      ↓
Update project.project_mode in database
      ↓
Refresh projects context
      ↓
Update CLAUDE.md with new mode
      ↓
UI updates with new mode
```

### Worktree Toggle Flow
```
User toggles switch
      ↓
Update project_settings.worktree_enabled
      ↓
Regenerate CLAUDE.md with worktree instructions
      ↓
Broadcast WebSocket message
      ↓
UI updates, loading indicator shown
      ↓
Refresh projects context
      ↓
Loading complete
```

## WebSocket Integration

### Message Format
```json
{
  "type": "project_settings_updated",
  "project_id": "abc-123",
  "settings": {
    "worktree_enabled": false,
    "auto_mode": false,
    "max_parallel_tasks": 3
  }
}
```

### Handling Updates
Component automatically reloads settings when WebSocket message received (through ProjectContext refresh).

## Error Handling

```tsx
const handleWorktreeToggle = async (event) => {
  const newValue = event.target.checked;
  setLoading(true);

  try {
    await updateProjectSettings(projectId, {
      worktree_enabled: newValue
    });
    setWorktreeEnabled(newValue);
    await refreshProjects();
  } catch (error) {
    console.error('Failed to update worktree setting:', error);
    // Revert toggle on error
    setWorktreeEnabled(!newValue);
  } finally {
    setLoading(false);
  }
};
```

## Accessibility

- **Keyboard Navigation**: Full keyboard support for toggle buttons and switch
- **Screen Readers**: Proper ARIA labels and descriptions
- **Focus Indicators**: Clear visual focus states
- **Tooltips**: Descriptive tooltips for all interactive elements

## Related Components

- **TaskBoard**: Main page that uses ProjectModeToggle in header
- **ProjectContext**: Provides selected project and refresh function
- **ThemeContext**: Provides theme mode for styling

## Backend Integration

### Database Schema
```sql
-- projects table
CREATE TABLE projects (
  id TEXT PRIMARY KEY,
  name TEXT NOT NULL,
  project_mode TEXT DEFAULT 'simple', -- 'simple' or 'development'
  ...
);

-- project_settings table
CREATE TABLE project_settings (
  id INTEGER PRIMARY KEY,
  project_id TEXT UNIQUE NOT NULL,
  worktree_enabled BOOLEAN DEFAULT 1 NOT NULL,
  ...
);
```

### CLAUDE.md Generation

When worktree_enabled changes, backend regenerates CLAUDE.md:

```python
# claude_config_generator.py
def generate_claude_md(
    project_mode: str,
    worktree_enabled: bool = True
):
    if project_mode == "development":
        if worktree_enabled:
            # Add full worktree instructions
            mode_section = """
## ✅ GIT WORKTREES ENABLED
- Each task gets isolated workspace
- Worktrees created at worktrees/task-{id}/
- Automatic cleanup after merge
"""
        else:
            # Add worktree warnings
            mode_section = """
## ⚠️ GIT WORKTREES DISABLED
- DO NOT use git worktree commands
- Work directly in main branch
- Use standard git branching instead
"""
    return template_content
```

## Testing

### Manual Testing Checklist
- [ ] Mode toggle switches between SIMPLE and DEVELOPMENT
- [ ] Worktree toggle only visible in DEVELOPMENT mode
- [ ] Worktree toggle hidden in SIMPLE mode
- [ ] Loading indicator shows during API call
- [ ] Error handling reverts toggle on failure
- [ ] CLAUDE.md regenerated after toggle
- [ ] WebSocket message broadcast on change
- [ ] Tooltips display correctly
- [ ] Responsive layout on mobile/desktop
- [ ] Keyboard navigation works

### API Testing
```bash
# Get project settings
curl http://localhost:3333/api/projects/{id}/settings

# Update worktree setting
curl -X PATCH http://localhost:3333/api/projects/{id}/settings \
  -H "Content-Type: application/json" \
  -d '{"worktree_enabled": false}'

# Verify CLAUDE.md regenerated
cat project-path/CLAUDE.md | grep "WORKTREES"
```

## Troubleshooting

### Worktree Toggle Not Visible
**Symptom:** Switch doesn't appear in DEVELOPMENT mode

**Possible Causes:**
1. Migration 005 not run (worktree_enabled column missing)
2. Project mode is SIMPLE (toggle only in DEVELOPMENT)
3. CSS display issue on mobile

**Solution:**
```bash
# Check migration status
sqlite3 claudetask/backend/claudetask.db \
  "PRAGMA table_info(project_settings);" | grep worktree_enabled

# Run migration if needed
python claudetask/backend/migrations/migrate_add_worktree_enabled.py
```

### Toggle Not Saving
**Symptom:** Toggle reverts after page reload

**Possible Causes:**
1. API endpoint not updating database
2. Frontend not calling correct endpoint
3. Database write failure

**Solution:**
```bash
# Check backend logs for errors
tail -f backend.log | grep "worktree_enabled"

# Verify database update
sqlite3 claudetask/backend/claudetask.db \
  "SELECT worktree_enabled FROM project_settings WHERE project_id = 'abc-123';"
```

### CLAUDE.md Not Regenerating
**Symptom:** CLAUDE.md doesn't change after toggle

**Possible Causes:**
1. Backend service not calling regenerate_claude_md()
2. File write permissions issue
3. Template error in claude_config_generator.py

**Solution:**
```bash
# Check backend logs
tail -f backend.log | grep "Regenerating CLAUDE.md"

# Manually trigger regeneration
curl -X POST http://localhost:3333/api/projects/{id}/regenerate-claude-md
```

## Future Enhancements

### Planned Features
- [ ] Bulk mode change for all projects
- [ ] Mode change confirmation dialog
- [ ] Worktree usage statistics
- [ ] Automatic mode recommendation based on project size
- [ ] Mode change history tracking

### Potential Improvements
- Add animation for mode transitions
- Show worktree count when enabled
- Display warning when changing modes with active tasks
- Add undo functionality for mode changes

## Related Documentation

- [Project Modes](../architecture/project-modes.md) - Detailed mode comparison
- [Database Migrations](../deployment/database-migrations.md) - Migration 005 details
- [ProjectContext](./ProjectContext.md) - Context provider (to be created)
- [API Endpoints](../api/endpoints/projects.md) - Project settings API (to be created)

---

**Last Updated**: 2025-11-20
**Version**: 1.1 (Worktree Toggle Added)
**Component Status**: Active, Production Ready
