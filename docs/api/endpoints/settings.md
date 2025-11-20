# Settings API Documentation

Complete API reference for project settings management in the Claude Code Feature Framework.

## Overview

The Settings API provides endpoints for managing project-level configuration, including project mode, worktree settings, and user preferences. The Settings page displays these configurations and allows users to modify them.

## Endpoints

### Get Project Settings

Retrieve all settings for a specific project.

**Endpoint**: `GET /api/projects/{project_id}/settings`

**Parameters**:
- `project_id` (path, required): Project UUID

**Response**:
```json
{
  "id": 1,
  "project_id": "uuid-here",
  "claude_config": "# CLAUDE.md content...",
  "auto_mode": false,
  "manual_mode": true,
  "worktree_enabled": true,
  "test_command": "pytest",
  "build_command": "npm run build",
  "lint_command": "flake8",
  "custom_settings": {}
}
```

**Response Fields**:
- `id`: Settings record ID
- `project_id`: Associated project UUID
- `claude_config`: Full CLAUDE.md configuration content
- `auto_mode`: Enable automatic task progression (default: false)
- `manual_mode`: Require manual approval for merges (default: true)
- `worktree_enabled`: Enable git worktrees in DEVELOPMENT mode (default: true)
- `test_command`: Command to run tests
- `build_command`: Command to build project
- `lint_command`: Command to run linter
- `custom_settings`: JSON object for additional settings

**Example Request**:
```bash
curl -X GET http://localhost:3333/api/projects/abc-123/settings
```

---

### Update Project Settings

Update settings for a specific project.

**Endpoint**: `PUT /api/projects/{project_id}/settings`

**Parameters**:
- `project_id` (path, required): Project UUID

**Request Body**:
```json
{
  "auto_mode": false,
  "manual_mode": true,
  "worktree_enabled": true,
  "test_command": "pytest tests/",
  "build_command": "npm run build",
  "lint_command": "flake8 src/",
  "custom_settings": {
    "notifications_enabled": true,
    "theme": "dark"
  }
}
```

**Response**:
```json
{
  "id": 1,
  "project_id": "uuid-here",
  "claude_config": "# Updated CLAUDE.md...",
  "auto_mode": false,
  "manual_mode": true,
  "worktree_enabled": true,
  "test_command": "pytest tests/",
  "build_command": "npm run build",
  "lint_command": "flake8 src/",
  "custom_settings": {
    "notifications_enabled": true,
    "theme": "dark"
  }
}
```

**Side Effects**:
- If `worktree_enabled` changes, CLAUDE.md is automatically regenerated
- WebSocket broadcast sent to all connected clients
- Project settings cache updated

**Example Request**:
```bash
curl -X PUT http://localhost:3333/api/projects/abc-123/settings \
  -H "Content-Type: application/json" \
  -d '{
    "worktree_enabled": false,
    "manual_mode": true
  }'
```

---

## Settings Fields Explained

### Project Mode

**Field**: `project_mode` (on Project model, not ProjectSettings)
**Type**: String enum
**Values**: `"simple"` | `"development"`
**Immutable**: Cannot be changed after project creation
**Default**: `"simple"`

**Description**: Determines the task workflow complexity:
- **SIMPLE**: 3-column workflow (Backlog → In Progress → Done)
- **DEVELOPMENT**: 7-column workflow (Backlog → Analysis → In Progress → Testing → Code Review → PR → Done)

**Location**: Displayed explicitly at the top of CLAUDE.md and in Settings page.

---

### Manual Mode

**Field**: `manual_mode`
**Type**: Boolean
**Default**: `true`
**Applicable**: DEVELOPMENT mode only

**Description**: Controls pull request merge behavior:
- **True** (default): PRs require manual review and approval before merge
- **False**: PRs auto-merge after checks pass (automated workflow)

**Use Cases**:
- **Manual Mode**: Team development, production code, quality gates required
- **Auto Mode**: Solo development, rapid prototyping, CI/CD automation

**Example**:
```json
{
  "manual_mode": true  // Requires human approval for PR merge
}
```

---

### Worktree Enabled

**Field**: `worktree_enabled`
**Type**: Boolean
**Default**: `true`
**Applicable**: DEVELOPMENT mode only

**Description**: Controls git worktree usage for task isolation:
- **True** (default): Each task gets isolated worktree in `worktrees/task-{id}/`
- **False**: Work directly in main branch or manual feature branches

**Benefits of Worktrees**:
- Parallel development on multiple tasks
- Clean separation between tasks
- No branch switching in main repo
- Easy cleanup after task completion

**When to Disable**:
- Repository has Git LFS issues
- Repository uses submodules
- Solo developer prefers simple workflow
- Testing worktree compatibility

**Side Effects**:
- Changing this setting triggers CLAUDE.md regeneration
- CLAUDE.md instructions update to reflect worktree availability

**Example**:
```json
{
  "worktree_enabled": false  // Work in main branch, no worktrees
}
```

---

### Auto Mode

**Field**: `auto_mode`
**Type**: Boolean
**Default**: `false`
**Applicable**: DEVELOPMENT mode only

**Description**: Enables automatic task progression:
- **False** (default): Coordinator monitors but waits for user actions
- **True**: Coordinator automatically progresses tasks through workflow

**When Enabled**:
- Tasks auto-transition between statuses
- Analysis agents triggered automatically
- Test environments setup automatically
- PRs created automatically when ready

**When Disabled** (default):
- User explicitly triggers workflow commands
- Manual control over each phase
- More predictable behavior

**Caution**: Auto mode is experimental. Most users should keep this disabled.

**Example**:
```json
{
  "auto_mode": false  // Manual workflow control
}
```

---

### Test Command

**Field**: `test_command`
**Type**: String (optional)
**Default**: `null`

**Description**: Command to run project tests.

**Examples**:
```json
{
  "test_command": "pytest"                    // Python projects
  "test_command": "npm test"                  // Node.js projects
  "test_command": "python -m pytest tests/"   // Specific test directory
}
```

---

### Build Command

**Field**: `build_command`
**Type**: String (optional)
**Default**: `null`

**Description**: Command to build the project.

**Examples**:
```json
{
  "build_command": "npm run build"           // Node.js projects
  "build_command": "python setup.py build"   // Python projects
  "build_command": "make build"              // Make-based projects
}
```

---

### Lint Command

**Field**: `lint_command`
**Type**: String (optional)
**Default**: `null`

**Description**: Command to run code linting.

**Examples**:
```json
{
  "lint_command": "flake8"                   // Python linting
  "lint_command": "eslint src/"              // JavaScript linting
  "lint_command": "pylint src/**/*.py"       // Specific files
}
```

---

### Custom Settings

**Field**: `custom_settings`
**Type**: JSON Object (optional)
**Default**: `{}`

**Description**: Flexible key-value store for additional settings.

**Use Cases**:
- Store UI preferences (theme, density, etc.)
- Store notification settings
- Store custom workflow preferences
- Store integration tokens (encrypted)

**Example**:
```json
{
  "custom_settings": {
    "notifications_enabled": true,
    "theme": "dark",
    "auto_save": true,
    "editor_font_size": 14,
    "show_welcome_modal": false
  }
}
```

---

## Frontend Integration

### Settings Component

**Location**: `frontend/src/pages/Settings.tsx`

The Settings page displays and allows editing of:

1. **General Settings** (localStorage):
   - Project name
   - Auto-save preference
   - Confirm actions

2. **Appearance Settings** (localStorage):
   - Theme (light/dark/system)
   - Density (comfortable/compact)
   - Animations enabled

3. **Notification Settings** (localStorage):
   - Task updates
   - Agent status
   - Error notifications
   - Sound enabled

4. **Project Settings** (localStorage):
   - Default priority
   - Auto-assign tasks
   - Branch naming convention

5. **Backend Project Settings** (database):
   - Project mode (read-only)
   - Manual mode toggle
   - Worktree enabled toggle
   - Test/Build/Lint commands

### Loading Settings

```typescript
// Load from backend
const loadBackendSettings = async () => {
  if (!selectedProject?.id) return;

  setLoadingSettings(true);
  try {
    const settings = await getProjectSettings(selectedProject.id);
    setBackendSettings(settings);
  } catch (error) {
    console.error('Failed to load backend settings:', error);
  } finally {
    setLoadingSettings(false);
  }
};

useEffect(() => {
  loadBackendSettings();
}, [selectedProject]);
```

### Updating Settings

```typescript
// Update backend settings
const handleSaveBackendSettings = async () => {
  if (!selectedProject?.id || !backendSettings) return;

  try {
    const updated = await updateProjectSettings(
      selectedProject.id,
      backendSettings
    );
    setBackendSettings(updated);
    setSaveSuccess(true);
  } catch (error) {
    setSaveError('Failed to save backend settings');
  }
};
```

### Settings API Service

**Location**: `frontend/src/services/api.ts`

```typescript
export interface ProjectSettings {
  id: number;
  project_id: string;
  claude_config: string;
  auto_mode: boolean;
  manual_mode: boolean;
  worktree_enabled: boolean;
  test_command?: string;
  build_command?: string;
  lint_command?: string;
  custom_settings?: Record<string, any>;
}

export const getProjectSettings = async (
  projectId: string
): Promise<ProjectSettings> => {
  const response = await axios.get(
    `${API_BASE_URL}/projects/${projectId}/settings`
  );
  return response.data;
};

export const updateProjectSettings = async (
  projectId: string,
  settings: Partial<ProjectSettings>
): Promise<ProjectSettings> => {
  const response = await axios.put(
    `${API_BASE_URL}/projects/${projectId}/settings`,
    settings
  );
  return response.data;
};
```

---

## CLAUDE.md Regeneration

### When Settings Change

When certain settings are updated, CLAUDE.md is automatically regenerated to reflect the changes:

**Triggers**:
- `worktree_enabled` changed
- Framework files updated
- Manual regeneration requested

**Process**:
1. Read current project configuration from database
2. Generate new CLAUDE.md using `claude_config_generator.py`
3. Create backup: `CLAUDE.md.backup`
4. Write new CLAUDE.md with updated instructions
5. Update `projects.claude_config` field in database
6. Broadcast change via WebSocket

**Example Regeneration**:
```python
from app.services.claude_config_generator import generate_claude_md

# Generate new config
new_config = generate_claude_md(
    project_name=project.name,
    project_path=project.path,
    tech_stack=project.tech_stack,
    custom_instructions=project.custom_instructions,
    project_mode=project.project_mode,
    worktree_enabled=settings.worktree_enabled
)

# Backup and write
backup_path = project_path / "CLAUDE.md.backup"
claude_md_path = project_path / "CLAUDE.md"
claude_md_path.rename(backup_path)
claude_md_path.write_text(new_config)

# Update database
project.claude_config = new_config
await db.commit()
```

---

## WebSocket Updates

### Settings Change Broadcast

When settings are updated, a WebSocket message is broadcast to all connected clients:

**Event**: `project_settings_updated`

**Payload**:
```json
{
  "event": "project_settings_updated",
  "project_id": "uuid-here",
  "settings": {
    "worktree_enabled": false,
    "manual_mode": true,
    "auto_mode": false
  },
  "timestamp": "2025-11-21T10:00:00Z"
}
```

**Frontend Handling**:
```typescript
// Listen for settings updates
websocket.on('project_settings_updated', (data) => {
  if (data.project_id === selectedProject?.id) {
    // Reload settings
    loadBackendSettings();
    // Show notification
    showNotification('Settings updated');
  }
});
```

---

## Database Schema

### ProjectSettings Table

```sql
CREATE TABLE project_settings (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  project_id TEXT UNIQUE NOT NULL,
  claude_config TEXT,
  auto_mode BOOLEAN DEFAULT 0 NOT NULL,
  manual_mode BOOLEAN DEFAULT 1 NOT NULL,
  worktree_enabled BOOLEAN DEFAULT 1 NOT NULL,
  test_command TEXT,
  build_command TEXT,
  lint_command TEXT,
  custom_settings JSON,
  FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
);
```

**Relationships**:
- One-to-one with `projects` table
- CASCADE DELETE when project deleted

---

## MCP Tool Access

### Get Project Settings via MCP

Claude Code agents can access project settings via MCP:

```bash
# Get project settings
mcp:get_project_settings

# Returns project configuration including:
# - project_mode (simple/development)
# - worktree_enabled (true/false)
# - manual_mode (true/false)
# - custom_instructions
```

**Response**:
```json
{
  "project_id": "uuid-here",
  "project_name": "My Project",
  "project_mode": "development",
  "worktree_enabled": true,
  "manual_mode": true,
  "custom_instructions": "Custom project instructions..."
}
```

**Use Case**: Agents check project settings to determine workflow behavior.

---

## Migration History

### Migration 005: Worktree Toggle

**File**: `005_add_worktree_toggle.sql`

**Changes**:
- Added `worktree_enabled` column to `project_settings`
- Default value: `true` (enabled)
- Only relevant in DEVELOPMENT mode

**Purpose**: Allow projects to disable worktrees while keeping DEVELOPMENT workflow.

---

## Best Practices

### Settings Management

1. **Read project mode first**: Check if settings apply to current mode
2. **Validate before save**: Ensure settings are compatible
3. **Provide feedback**: Show success/error messages after updates
4. **Handle errors gracefully**: Don't break UI on settings load failure
5. **Cache settings**: Avoid unnecessary API calls

### Worktree Toggle

1. **Test compatibility**: Try enabling worktrees to check repository support
2. **Gradual adoption**: Start with disabled, enable when comfortable
3. **Document decision**: Note why worktrees are enabled/disabled
4. **Communicate with team**: Ensure team understands worktree workflow
5. **Clean up after disable**: Remove existing worktrees if disabling

### Manual Mode

1. **Use manual mode for production**: Require human review for critical code
2. **Use auto mode for prototypes**: Speed up solo development
3. **Consider team size**: Manual mode essential for teams
4. **Configure CI/CD**: Auto mode works best with automated checks
5. **Document workflow**: Team should know merge process

---

## Troubleshooting

### Settings Not Loading

**Symptom**: Settings page shows "Loading..." indefinitely

**Solutions**:
- Check backend API is running: `curl http://localhost:3333/health`
- Verify project ID is valid
- Check browser console for errors
- Verify database has `project_settings` record for project

### Worktree Toggle Not Visible

**Symptom**: Worktree toggle doesn't appear in Settings

**Causes**:
- Project mode is SIMPLE (toggle only in DEVELOPMENT)
- Migration 005 not run (column missing)
- Settings not loaded from backend

**Solutions**:
- Check project mode: Should be "development"
- Run migration: `alembic upgrade head`
- Reload settings: Refresh page

### CLAUDE.md Not Regenerating

**Symptom**: Changing worktree_enabled doesn't update CLAUDE.md

**Solutions**:
- Check backend logs for errors
- Verify `claude_config_generator.py` service exists
- Manually regenerate: `python migrations/regenerate_claude_md.py [project_id]`
- Check file permissions on CLAUDE.md

### Settings Changes Not Persisting

**Symptom**: Settings revert after page reload

**Causes**:
- API request failing silently
- Database write error
- Frontend not saving to backend (only localStorage)

**Solutions**:
- Check network tab for failed requests
- Verify backend logs for errors
- Ensure using `updateProjectSettings()` API call, not just localStorage
- Check database for updated values

---

## Related Documentation

- [Project Modes](../../architecture/project-modes.md) - SIMPLE vs DEVELOPMENT mode
- [CLAUDE.md Regeneration](../../architecture/project-modes.md#claudemd-regeneration) - Automatic config updates
- [ProjectModeToggle Component](../../components/ProjectModeToggle.md) - UI component for worktree toggle
- [Database Migrations](../../deployment/database-migrations.md) - Migration 005 details

---

**Last Updated**: 2025-11-21
**API Version**: 1.0.0
**Backend**: FastAPI + SQLAlchemy
**Frontend**: React + Material-UI
