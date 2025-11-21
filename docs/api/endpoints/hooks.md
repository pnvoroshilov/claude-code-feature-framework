# Hooks API Endpoints

Complete API reference for managing Claude Code hooks - automated shell commands triggered at workflow events.

## Base URL

```
/api/projects/{project_id}/hooks
```

## Overview

The Hooks API enables management of both default (framework-provided) and custom (user-created) hooks. Hooks are automated shell commands that execute at specific workflow trigger points.

## Data Models

### Hook Object

```typescript
interface Hook {
  id: number;
  name: string;
  description: string;
  category: 'logging' | 'formatting' | 'notifications' | 'security' | 'version-control';
  hook_config: object;  // JSON configuration
  setup_instructions?: string;
  dependencies?: string;  // Comma-separated list
  is_enabled: boolean;
  is_favorite: boolean;
  is_custom: boolean;
  created_by?: string;
  created_at: string;
  updated_at: string;
  status?: 'active' | 'creating' | 'failed';
}
```

### HooksResponse Object

```typescript
interface HooksResponse {
  enabled: Hook[];           // Currently enabled hooks
  available_default: Hook[]; // Framework hooks not yet enabled
  custom: Hook[];            // User-created hooks
  favorites: Hook[];         // Starred hooks (cross-project)
}
```

## Endpoints

### 1. Get Project Hooks

Retrieve all hooks for a project, categorized by status.

**Endpoint:**
```
GET /api/projects/{project_id}/hooks/
```

**Response:**
```json
{
  "enabled": [
    {
      "id": 1,
      "name": "post-merge-documentation",
      "description": "Update documentation after merging to main",
      "category": "version-control",
      "hook_config": {
        "PostToolUse": [{
          "matcher": "tool==='Bash' && args.command.includes('git push')",
          "hooks": [{
            "type": "ExecuteCommand",
            "command": "/update-documentation"
          }]
        }]
      },
      "is_enabled": true,
      "is_favorite": false,
      "is_custom": false
    }
  ],
  "available_default": [...],
  "custom": [...],
  "favorites": [...]
}
```

**Status Codes:**
- `200 OK`: Success
- `404 Not Found`: Project not found
- `500 Internal Server Error`: Server error

---

### 2. Enable Hook

Enable a hook by merging its configuration into project's `.claude/settings.json`.

**Endpoint:**
```
POST /api/projects/{project_id}/hooks/enable/{hook_id}
```

**Process:**
1. Validate hook exists in `default_hooks` or `custom_hooks` table
2. Merge hook configuration into `.claude/settings.json`
3. Insert record into `project_hooks` junction table
4. Return enabled hook details

**Response:**
```json
{
  "id": 1,
  "name": "post-merge-documentation",
  "is_enabled": true,
  "message": "Hook enabled successfully"
}
```

**Status Codes:**
- `200 OK`: Hook enabled successfully
- `400 Bad Request`: Hook already enabled or invalid
- `404 Not Found`: Hook not found
- `500 Internal Server Error`: Failed to update settings.json

---

### 3. Disable Hook

Disable a hook by removing it from project's `.claude/settings.json`.

**Endpoint:**
```
POST /api/projects/{project_id}/hooks/disable/{hook_id}
```

**Process:**
1. Remove record from `project_hooks` junction table
2. Remove hook configuration from `.claude/settings.json`
3. Keep record in `custom_hooks` if it's a custom hook (don't delete)

**Response:**
```json
{
  "success": true,
  "message": "Hook disabled successfully"
}
```

**Status Codes:**
- `200 OK`: Hook disabled successfully
- `404 Not Found`: Hook not found or not enabled
- `500 Internal Server Error`: Failed to update settings.json

---

### 4. Enable All Hooks

Enable all available hooks (both default and custom) for a project.

**Endpoint:**
```
POST /api/projects/{project_id}/hooks/enable-all
```

**Process:**
1. Get all available default hooks
2. Get all custom hooks
3. Enable each hook that isn't already enabled
4. Return count of newly enabled hooks

**Response:**
```json
{
  "success": true,
  "enabled_count": 5,
  "errors": []  // Optional: list of failed hooks
}
```

**Status Codes:**
- `200 OK`: Operation completed (check enabled_count)
- `500 Internal Server Error`: Operation failed

**Example with Errors:**
```json
{
  "success": true,
  "enabled_count": 3,
  "errors": [
    "Failed to enable post-commit-lint: Missing dependencies",
    "Failed to enable security-scan: Script file not found"
  ]
}
```

---

### 5. Disable All Hooks

Disable all currently enabled hooks for a project.

**Endpoint:**
```
POST /api/projects/{project_id}/hooks/disable-all
```

**Process:**
1. Get all enabled hooks
2. Disable each enabled hook
3. Return count of disabled hooks

**Response:**
```json
{
  "success": true,
  "disabled_count": 5,
  "errors": []  // Optional: list of failed hooks
}
```

**Status Codes:**
- `200 OK`: Operation completed (check disabled_count)
- `500 Internal Server Error`: Operation failed

---

### 6. Create Custom Hook

Create a new custom hook using Claude Code CLI.

**Endpoint:**
```
POST /api/projects/{project_id}/hooks/create
```

**Request Body:**
```json
{
  "name": "my-custom-hook",
  "description": "Custom hook for my workflow",
  "category": "version-control",
  "hook_config": {
    "PostToolUse": [{
      "matcher": "tool==='Bash' && args.command.includes('git commit')",
      "hooks": [{
        "type": "ExecuteCommand",
        "command": "npm run lint"
      }]
    }]
  },
  "setup_instructions": "Install npm dependencies first",
  "dependencies": "npm, git"
}
```

**Process:**
1. Validate hook name uniqueness
2. Insert record into `custom_hooks` (status: "creating")
3. Launch background task for Claude Code CLI interaction
4. Return hook record (status will update when complete)

**Response:**
```json
{
  "id": 10,
  "name": "my-custom-hook",
  "status": "creating",
  "is_custom": true
}
```

**Status Codes:**
- `200 OK`: Hook creation initiated
- `400 Bad Request`: Invalid request body or duplicate name
- `500 Internal Server Error`: Failed to create hook

---

### 7. Update Hook

Update an existing hook's metadata and configuration.

**Endpoint:**
```
PUT /api/projects/{project_id}/hooks/{hook_id}
```

**Request Body:**
```json
{
  "description": "Updated description",
  "category": "formatting",
  "hook_config": {...},
  "setup_instructions": "Updated instructions",
  "dependencies": "jq, curl"
}
```

**Process:**
1. Verify hook exists
2. Update hook metadata in database
3. If hook is enabled, update `.claude/settings.json` with new config
4. Return updated hook details

**Response:**
```json
{
  "id": 10,
  "name": "my-custom-hook",
  "description": "Updated description",
  "updated_at": "2025-11-21T10:30:00Z"
}
```

**Restrictions:**
- Cannot edit hook name (immutable identifier)
- Cannot edit default hooks (only custom hooks)

**Status Codes:**
- `200 OK`: Hook updated successfully
- `400 Bad Request`: Invalid update data
- `404 Not Found`: Hook not found
- `500 Internal Server Error`: Failed to update hook

---

### 8. Delete Custom Hook

Permanently delete a custom hook.

**Endpoint:**
```
DELETE /api/projects/{project_id}/hooks/{hook_id}
```

**Process:**
1. Verify hook is custom (not default)
2. Remove from `project_hooks` junction table
3. Remove hook from `.claude/settings.json`
4. Delete record from `custom_hooks` table

**Response:**
```json
{
  "success": true,
  "message": "Custom hook deleted successfully"
}
```

**Status Codes:**
- `200 OK`: Hook deleted successfully
- `400 Bad Request`: Cannot delete default hook
- `404 Not Found`: Hook not found
- `500 Internal Server Error`: Failed to delete hook

---

### 9. Get Default Hooks Catalog

Retrieve all default hooks provided by the framework.

**Endpoint:**
```
GET /api/projects/{project_id}/hooks/defaults
```

**Response:**
```json
[
  {
    "id": 1,
    "name": "post-merge-documentation",
    "description": "Update documentation after merging",
    "category": "version-control",
    "is_custom": false
  },
  ...
]
```

**Status Codes:**
- `200 OK`: Success
- `500 Internal Server Error`: Server error

---

### 10. Save to Favorites

Mark a hook as favorite for quick access.

**Endpoint:**
```
POST /api/projects/{project_id}/hooks/favorites/save
```

**Query Parameters:**
- `hook_id` (required): Hook ID
- `hook_type` (required): `default` or `custom`

**Process:**
1. Validate hook exists
2. Set `is_favorite = True`
3. Hook appears in Favorites tab

**Note:** Favorites are cross-project - they show for all projects.

**Response:**
```json
{
  "id": 1,
  "is_favorite": true,
  "message": "Added to favorites"
}
```

**Status Codes:**
- `200 OK`: Success
- `400 Bad Request`: Invalid hook type or already favorite
- `500 Internal Server Error`: Server error

---

### 11. Remove from Favorites

Remove favorite status from a hook.

**Endpoint:**
```
POST /api/projects/{project_id}/hooks/favorites/remove
```

**Query Parameters:**
- `hook_id` (required): Hook ID
- `hook_type` (required): `default` or `custom`

**Response:**
```json
{
  "success": true,
  "message": "Removed from favorites successfully"
}
```

**Status Codes:**
- `200 OK`: Success
- `400 Bad Request`: Invalid hook type or not favorited
- `500 Internal Server Error`: Server error

---

## Hook Configuration Structure

### Supported Events

Hooks can trigger on the following events:

1. **PreToolUse**: Before Claude executes a tool
2. **PostToolUse**: After tool execution completes
3. **PreUserPromptSubmit**: Before user submits input
4. **PostUserPromptSubmit**: After user input submitted

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

### Hook Action Types

#### 1. ExecuteCommand

Run a shell command:

```json
{
  "type": "ExecuteCommand",
  "command": "npm run lint"
}
```

#### 2. Notification

Show user notification:

```json
{
  "type": "Notification",
  "message": "Code formatting applied"
}
```

#### 3. Custom Script

Execute a custom script file:

```json
{
  "type": "Custom",
  "script_file": "post-push-docs.sh"
}
```

### Complete Example

```json
{
  "PostToolUse": [
    {
      "matcher": "tool==='Bash' && args.command.includes('git push') && args.command.includes('main')",
      "hooks": [
        {
          "type": "Custom",
          "script_file": "post-push-docs.sh"
        },
        {
          "type": "Notification",
          "message": "Documentation update triggered"
        }
      ]
    }
  ]
}
```

## Common Use Cases

### 1. Post-Merge Documentation

Automatically update documentation after pushing to main:

```json
{
  "name": "post-merge-documentation",
  "category": "version-control",
  "hook_config": {
    "PostToolUse": [{
      "matcher": "tool==='Bash' && args.command.includes('git push')",
      "hooks": [{
        "type": "ExecuteCommand",
        "command": "/update-documentation"
      }]
    }]
  },
  "dependencies": "jq, curl, git"
}
```

### 2. Code Formatting on Save

Auto-format Python files after writing:

```json
{
  "name": "auto-format-python",
  "category": "formatting",
  "hook_config": {
    "PostToolUse": [{
      "matcher": "tool==='Write' && args.file_path.endsWith('.py')",
      "hooks": [{
        "type": "ExecuteCommand",
        "command": "black ${file_path}"
      }]
    }]
  },
  "dependencies": "black"
}
```

### 3. Test Execution on Test File Changes

Run tests automatically when test files are modified:

```json
{
  "name": "auto-run-tests",
  "category": "testing",
  "hook_config": {
    "PostToolUse": [{
      "matcher": "tool==='Write' && args.file_path.includes('/tests/')",
      "hooks": [{
        "type": "ExecuteCommand",
        "command": "pytest ${file_path}"
      }]
    }]
  },
  "dependencies": "pytest"
}
```

## Error Handling

### Common Error Responses

**400 Bad Request:**
```json
{
  "detail": "Hook name already exists"
}
```

**404 Not Found:**
```json
{
  "detail": "Hook not found"
}
```

**500 Internal Server Error:**
```json
{
  "detail": "Failed to enable hook: Permission denied writing to .claude/settings.json"
}
```

## Best Practices

### 1. Hook Configuration

- Use specific matchers to avoid unintended triggers
- Test hook configuration before enabling
- Document dependencies clearly
- Keep hook commands idempotent

### 2. Error Recovery

- Handle errors gracefully in hook scripts
- Use `set -e` for bash scripts to fail fast
- Log hook execution for debugging
- Provide clear error messages

### 3. Performance

- Avoid long-running commands in hooks
- Use background tasks for heavy operations
- Implement timeouts for external commands
- Cache results when possible

### 4. Security

- Validate all user input in hook commands
- Avoid exposing sensitive data in hook configs
- Use secure methods for credential management
- Restrict file system access appropriately

## Related Documentation

- [Hooks System Architecture](../../architecture/hooks-system.md)
- [Hooks Component](../../components/Hooks.md)
- [Database Migrations](../../deployment/database-migrations.md)

---

**Last Updated:** 2025-11-21
**API Version:** 2.0
**Status:** Active
