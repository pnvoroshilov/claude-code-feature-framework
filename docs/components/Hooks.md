# Hooks Component

React component for managing Claude Code hooks - shell commands that execute automatically at workflow trigger points.

## Location

`claudetask/frontend/src/pages/Hooks.tsx`

## Purpose

Provides a comprehensive interface for:
- Browsing and enabling default framework hooks
- Creating custom project-specific hooks
- Managing hook configurations and dependencies
- Toggling hook activation state
- Marking hooks as favorites for quick access

## Features

### 1. Hook Categories and Filtering

**Category System:**
- `logging` - Session logging and audit trails (Blue: #3B82F6)
- `formatting` - Code formatting and linting (Purple: #8B5CF6)
- `notifications` - Status updates and alerts (Orange: #F59E0B)
- `security` - Security scans and validation (Red: #EF4444)
- `version-control` - Git integration and automation (Green: #10B981)

**Filter Options:**
- **All**: Show all hooks (default + custom + enabled)
- **Default**: Framework-provided hooks only
- **Custom**: User-created project-specific hooks
- **Favorite**: Starred hooks for quick access
- **Enabled**: Currently active hooks only

**Search:**
- Real-time search across hook names and descriptions
- Case-insensitive matching
- Filters displayed hooks dynamically

### 2. Hook Display Cards

**Visual Design:**
- Material-UI Card components with hover effects
- Category-colored badges
- Favorite star icon (toggle on/off)
- Enable/disable switch
- Quick action buttons (View, Edit, Delete)

**Card Information:**
- Hook name and description
- Category badge with color coding
- Creator information (for custom hooks)
- Last updated timestamp
- Enable/disable toggle switch

### 3. Hook Management Actions

#### Enable/Disable Hook
```tsx
const handleEnableHook = async (hookId: number, hookType: 'default' | 'custom') => {
  await axios.post(`/api/projects/${projectId}/hooks/enable/${hookId}?hook_type=${hookType}`);
};

const handleDisableHook = async (hookId: number) => {
  await axios.post(`/api/projects/${projectId}/hooks/disable/${hookId}`);
};
```

#### Mark as Favorite
```tsx
const handleToggleFavorite = async (hookId: number, hookType: 'default' | 'custom', currentState: boolean) => {
  const endpoint = currentState ? 'unfavorite' : 'favorite';
  await axios.post(`/api/projects/${projectId}/hooks/${endpoint}/${hookId}?hook_type=${hookType}`);
};
```

#### Delete Custom Hook
```tsx
const handleDeleteHook = async (hookId: number) => {
  await axios.delete(`/api/projects/${projectId}/hooks/${hookId}`);
};
```

### 4. Create Custom Hook Dialog

**Form Fields:**
- **Name**: Hook identifier (required)
- **Description**: Hook purpose and behavior (required)
- **Category**: Dropdown selection (logging, formatting, etc.)
- **Hook Config**: JSON object defining events and commands (required)
- **Setup Instructions**: Optional installation/configuration steps
- **Dependencies**: Comma-separated list of required tools (jq, git, curl, etc.)

**Example Hook Config:**
```json
{
  "PostToolUse": [
    {
      "matcher": "tool==='Bash' && args.command.includes('git push')",
      "hooks": [
        {
          "type": "ExecuteCommand",
          "command": "/update-documentation"
        }
      ]
    }
  ]
}
```

**Validation:**
- Name and description are required
- Hook config must be valid JSON
- Dependencies validated as comma-separated strings
- Category must be from predefined list

### 5. View Hook Details Dialog

**Tabs:**
1. **Configuration**: View hook_config JSON (read-only)
2. **Dependencies**: List required tools and packages
3. **Setup Instructions**: Installation and configuration steps

**Features:**
- Syntax-highlighted JSON display
- Copy-to-clipboard functionality
- Expandable/collapsible sections
- Formatted dependency list

### 6. Edit Hook Dialog

**Editable Fields:**
- Description
- Category
- Hook Config (JSON editor)
- Setup Instructions
- Dependencies

**Restrictions:**
- Cannot edit hook name (immutable identifier)
- Default hooks cannot be edited (only custom hooks)
- JSON validation on hook_config changes

## Props

This is a page component and doesn't accept props. It uses:
- `ProjectContext` for current project selection
- Internal state management for hook data

## State Management

```tsx
const [activeFilter, setActiveFilter] = useState<FilterType>('all');
const [searchQuery, setSearchQuery] = useState('');
const [hooks, setHooks] = useState<HooksResponse>({
  enabled: [],
  available_default: [],
  custom: [],
  favorites: [],
});
const [loading, setLoading] = useState(true);
const [error, setError] = useState<string | null>(null);
const [selectedHook, setSelectedHook] = useState<Hook | null>(null);
```

## API Integration

### Endpoints Used

1. **GET /api/projects/{project_id}/hooks/**
   - Fetches all hooks (enabled, default, custom, favorites)
   - Returns structured HooksResponse object

2. **POST /api/projects/{project_id}/hooks/enable/{hook_id}**
   - Enables a hook for the project
   - Query param: `hook_type` (default or custom)

3. **POST /api/projects/{project_id}/hooks/disable/{hook_id}**
   - Disables an active hook

4. **POST /api/projects/{project_id}/hooks/favorite/{hook_id}**
   - Marks hook as favorite
   - Query param: `hook_type`

5. **POST /api/projects/{project_id}/hooks/unfavorite/{hook_id}**
   - Removes favorite status

6. **POST /api/projects/{project_id}/hooks/**
   - Creates new custom hook
   - Request body: `{ name, description, category, hook_config, setup_instructions, dependencies }`

7. **PUT /api/projects/{project_id}/hooks/{hook_id}**
   - Updates existing custom hook
   - Cannot edit default hooks

8. **DELETE /api/projects/{project_id}/hooks/{hook_id}**
   - Deletes custom hook
   - Cannot delete default hooks

## Hook Configuration Structure

### Hook Events

Hooks can trigger on various events:
- `PreToolUse`: Before Claude executes a tool
- `PostToolUse`: After tool execution completes
- `PreUserPromptSubmit`: Before user submits input
- `PostUserPromptSubmit`: After user input submitted

### Matcher Syntax

Matchers use JavaScript expressions to determine when hooks execute:

```javascript
// Git push detection
"tool==='Bash' && args.command.includes('git push')"

// File write detection
"tool==='Write' && args.file_path.endsWith('.py')"

// Specific directory operations
"tool==='Read' && args.file_path.includes('/src/components/')"
```

### Hook Types

1. **ExecuteCommand**: Run shell command
   ```json
   {
     "type": "ExecuteCommand",
     "command": "npm run lint"
   }
   ```

2. **Notification**: Show user notification
   ```json
   {
     "type": "Notification",
     "message": "Code formatting applied"
   }
   ```

3. **Custom**: Execute custom script
   ```json
   {
     "type": "Custom",
     "script_file": "post-push-docs.sh"
   }
   ```

## Common Use Cases

### 1. Automatic Documentation Updates

**Use Case**: Update documentation after merging to main branch

**Configuration:**
```json
{
  "PostToolUse": [
    {
      "matcher": "tool==='Bash' && args.command.includes('git push') && args.command.includes('main')",
      "hooks": [
        {
          "type": "ExecuteCommand",
          "command": "/update-documentation"
        }
      ]
    }
  ]
}
```

**Dependencies**: `jq`, `curl`, `git`

### 2. Code Formatting on Save

**Use Case**: Auto-format code when writing Python files

**Configuration:**
```json
{
  "PostToolUse": [
    {
      "matcher": "tool==='Write' && args.file_path.endsWith('.py')",
      "hooks": [
        {
          "type": "ExecuteCommand",
          "command": "black ${file_path}"
        }
      ]
    }
  ]
}
```

**Dependencies**: `black` (Python formatter)

### 3. Test Execution Trigger

**Use Case**: Run tests after modifying test files

**Configuration:**
```json
{
  "PostToolUse": [
    {
      "matcher": "tool==='Write' && args.file_path.includes('/tests/')",
      "hooks": [
        {
          "type": "ExecuteCommand",
          "command": "pytest ${file_path}"
        }
      ]
    }
  ]
}
```

**Dependencies**: `pytest`

## UI Improvements (v2.0)

**Recent Enhancements:**
- Unified card design with consistent spacing and shadows
- Color-coded category badges for visual categorization
- Improved search UX with real-time filtering
- Better mobile responsiveness
- Enhanced dialog layouts with proper tab navigation
- Loading states and error handling improvements
- Empty state messaging when no hooks match filters

**Design System:**
- Uses Material-UI theme colors and alpha blending
- Consistent hover effects across all interactive elements
- Professional SaaS-style card layouts
- Smooth transitions and animations

## Integration with Hooks System

The Hooks component is the primary UI for managing the hooks system architecture:

1. **Default Hooks**: Framework-provided hooks from `default_hooks` table
2. **Custom Hooks**: User-created hooks stored in `custom_hooks` table
3. **Project Association**: Links via `project_hooks` junction table

**Data Flow:**
```
User Action → Hooks Component
     ↓
API Request → Backend Router
     ↓
Hook Service → Database (default_hooks, custom_hooks, project_hooks)
     ↓
Hook File Service → .claude/settings.json (apply hook configuration)
     ↓
Response → Update UI State
```

## Error Handling

**User-Facing Errors:**
- Failed to fetch hooks
- Failed to enable/disable hook
- Failed to create/update/delete hook
- Invalid hook configuration JSON
- Missing required dependencies

**Error Display:**
- Alert banner at top of page
- Inline validation errors in dialogs
- Toast notifications for quick actions

## Performance Considerations

**Optimization Strategies:**
- Fetch hooks only when project changes
- Debounced search input (avoid excessive re-renders)
- Memoized filtered hook lists
- Lazy loading of hook details in dialogs
- Cache-busting with timestamp query params

## Accessibility

- Keyboard navigation support
- ARIA labels on all interactive elements
- Screen reader-friendly hook descriptions
- Focus management in dialogs
- Color contrast compliance (WCAG AA)

## Related Documentation

- [Hooks System Architecture](../architecture/hooks-system.md) - Technical implementation details
- [Hook File Service](../api/endpoints/hooks.md) - Backend API documentation
- [Database Migrations](../deployment/database-migrations.md) - Schema changes and migrations
