# Hooks and .claude/settings.json - Technical Documentation

## Overview

Claude Code hooks are stored and configured in `.claude/settings.json` at the project level. This document explains how hooks are managed in the ClaudeTask Framework.

## Storage Architecture

### Location
```
project-root/
├── .claude/
│   └── settings.json   ← Hooks are stored HERE
```

### Format in settings.json
```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "echo \"$(date) - $(echo '$TOOL_INPUT' | jq -r '.command')\" >> ~/.claude/bash.log"
          }
        ]
      }
    ],
    "PreToolUse": [
      {
        "matcher": "Edit",
        "hooks": [
          {
            "type": "command",
            "command": "FILE=$(echo '$TOOL_INPUT' | jq -r '.file_path'); if [[ $FILE == *.env* ]]; then exit 1; fi"
          }
        ]
      }
    ]
  }
}
```

## How Hooks Are Applied

### 1. Enabling a Default Hook (via UI)

**User Action**: Enable "Bash Command Logger" hook in UI

**Backend Flow**:
1. User clicks "Enable" toggle in Hooks page
2. Frontend calls: `POST /api/projects/{project_id}/hooks/enable/{hook_id}`
3. Backend `hook_service.enable_hook()`:
   - Fetches hook configuration from `DefaultHook` table
   - Calls `hook_file_service.apply_hook_to_settings()`
   - Merges hook config into `.claude/settings.json`
   - Creates `ProjectHook` record in database
4. Hook is now active!

**Code Flow**:
```python
# hook_service.py
async def enable_hook(self, project_id: str, hook_id: int):
    # Get hook from database
    hook = await self.db.execute(select(DefaultHook).where(...))

    # Apply to settings.json ← KEY STEP
    success = await self.file_service.apply_hook_to_settings(
        project_path=project.path,
        hook_name=hook.name,
        hook_config=hook.hook_config  # This merges into settings.json
    )

    # Record in database
    project_hook = ProjectHook(...)
    self.db.add(project_hook)
```

**settings.json Before**:
```json
{
  "other_settings": "..."
}
```

**settings.json After**:
```json
{
  "other_settings": "...",
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Bash",
        "hooks": [...]
      }
    ]
  }
}
```

### 2. Creating a Custom Hook (via UI or /create-hook)

**User Action**: Create custom "My Logger" hook via UI

**Backend Flow**:
1. User fills form and clicks "Create Custom Hook"
2. Frontend calls: `POST /api/projects/{project_id}/hooks/create`
3. Backend `hook_service.create_custom_hook()`:
   - Creates `CustomHook` record with status="creating"
   - Launches background task
4. Background task `execute_hook_creation_cli()`:
   - Starts Claude CLI session
   - Executes `/create-hook "My Logger" "Description"`
   - hook-creator agent creates JSON file
   - **Automatically applies to settings.json** ← NEW FIX
   - Updates hook status to "active"
   - Creates `ProjectHook` record

**Code Flow**:
```python
# hook_service.py
async def execute_hook_creation_cli(self, ...):
    # Create hook via CLI
    result = await self.creation_service.create_hook_via_claude_cli(...)

    if result["success"]:
        # Get hook config
        hook_config = result.get("hook_config", {})

        # 🔴 CRITICAL: Apply to settings.json
        settings_applied = await self.file_service.apply_hook_to_settings(
            project_path=project.path,
            hook_name=hook_name,
            hook_config=hook_config  # ← This saves to settings.json
        )

        # Enable hook
        project_hook = ProjectHook(...)
```

### 3. Disabling a Hook

**User Action**: Disable hook via UI

**Backend Flow**:
1. User toggles "Disable" in UI
2. Frontend calls: `POST /api/projects/{project_id}/hooks/disable/{hook_id}`
3. Backend `hook_service.disable_hook()`:
   - Calls `hook_file_service.remove_hook_from_settings()`
   - Removes hook config from `.claude/settings.json`
   - Deletes `ProjectHook` record from database
4. Hook is now inactive!

**settings.json Before**:
```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Bash",
        "hooks": [...]
      }
    ]
  }
}
```

**settings.json After**:
```json
{
  "hooks": {}
}
```

## File Service Implementation

### apply_hook_to_settings()
Located in: `claudetask/backend/app/services/hook_file_service.py`

```python
async def apply_hook_to_settings(
    self,
    project_path: str,
    hook_name: str,
    hook_config: Dict[str, Any]
) -> bool:
    """
    Merges hook configuration into .claude/settings.json

    Process:
    1. Read existing settings.json (or create if doesn't exist)
    2. Initialize hooks section if missing
    3. Merge hook config into hooks section by event type
    4. Avoid duplicates (check matcher)
    5. Write back to settings.json
    """
    settings_path = os.path.join(project_path, ".claude", "settings.json")

    # Read existing settings
    settings = {}
    if os.path.exists(settings_path):
        async with aiofiles.open(settings_path, 'r') as f:
            settings = json.loads(await f.read())

    # Initialize hooks section
    if "hooks" not in settings:
        settings["hooks"] = {}

    # Merge hook config
    for event_type, event_hooks in hook_config.items():
        if event_type not in settings["hooks"]:
            settings["hooks"][event_type] = []

        # Add hooks (avoid duplicates)
        for hook_matcher in event_hooks:
            if hook_matcher not in settings["hooks"][event_type]:
                settings["hooks"][event_type].append(hook_matcher)

    # Write back
    async with aiofiles.open(settings_path, 'w') as f:
        await f.write(json.dumps(settings, indent=2))

    return True
```

### remove_hook_from_settings()
```python
async def remove_hook_from_settings(
    self,
    project_path: str,
    hook_name: str
) -> bool:
    """
    Removes hook configuration from .claude/settings.json

    Note: This removes ALL hooks with matching name
    In production, you might want to track specific matchers
    """
    # Similar to apply, but removes instead of adding
```

## Database vs settings.json

### Why Both?

**Database (`DefaultHook`, `CustomHook`, `ProjectHook`)**:
- **Purpose**: Catalog and management
- **Stores**: Hook metadata (name, description, category, dependencies)
- **Tracks**: Which hooks are enabled for which projects
- **UI**: Powers the Hooks management page

**settings.json**:
- **Purpose**: Runtime configuration for Claude Code
- **Stores**: Actual hook behavior (events, matchers, commands)
- **Used by**: Claude Code runtime to execute hooks
- **Format**: Official Claude Code hooks specification

### Data Flow

```
┌─────────────┐
│  Database   │  Hook metadata and relationships
│  (SQLite)   │  - DefaultHook: Framework hooks catalog
│             │  - CustomHook: User-created hooks
│             │  - ProjectHook: Which hooks enabled where
└──────┬──────┘
       │
       │ enable_hook() / create_custom_hook()
       ↓
┌─────────────────────┐
│  hook_file_service  │  Applies hook to settings
│                     │
└──────┬──────────────┘
       │
       │ apply_hook_to_settings()
       ↓
┌─────────────────────────┐
│  .claude/settings.json  │  Runtime configuration
│                         │  - Actual hook commands
│  "hooks": {             │  - Event types
│    "PostToolUse": [...] │  - Matchers
│  }                      │  - Shell commands
└─────────────────────────┘
       │
       │ Claude Code reads and executes
       ↓
┌─────────────┐
│ Claude Code │  Executes hooks at runtime
│  Runtime    │
└─────────────┘
```

## Best Practices

### 1. Always Use the Service Layer
```python
# ✅ CORRECT
await hook_service.enable_hook(project_id, hook_id)
# This ensures database AND settings.json are updated

# ❌ WRONG
# Manually editing settings.json without updating database
```

### 2. Validate Hook Configuration
```python
# Before applying to settings.json
hook_config = {
    "PostToolUse": [
        {
            "matcher": "Bash",
            "hooks": [{"type": "command", "command": "..."}]
        }
    ]
}
# Must follow Claude Code hooks specification!
```

### 3. Handle Multiple Hooks Gracefully
```python
# apply_hook_to_settings() merges, doesn't replace
# This allows multiple hooks to coexist in same event type
```

### 4. Security
```python
# Always sanitize shell commands
# Never execute unsanitized user input
command = self.sanitize_hook_input(user_command)
```

## Troubleshooting

### Hook Not Working?

**Check 1**: Is hook in settings.json?
```bash
cat project/.claude/settings.json | jq '.hooks'
```

**Check 2**: Is ProjectHook record in database?
```sql
SELECT * FROM project_hooks WHERE project_id = '...' AND hook_id = ...;
```

**Check 3**: Is hook configuration valid?
- Must follow Claude Code hooks specification
- Event names must match: PostToolUse, PreToolUse, etc.
- Matcher must match tool name or use "*"

### Hook Not Appearing in UI?

**Check 1**: Is DefaultHook/CustomHook in database?
```sql
SELECT * FROM default_hooks;
SELECT * FROM custom_hooks;
```

**Check 2**: Was seed_default_hooks() executed?
```python
# Check startup logs
# Should see: "Seeded X default hooks"
```

## Testing

### Manual Test: Enable Hook
```bash
# 1. Start backend
cd claudetask/backend && source venv/bin/activate && uvicorn app.main:app

# 2. Enable hook via API
curl -X POST http://localhost:3333/api/projects/{project_id}/hooks/enable/1

# 3. Check settings.json
cat project/.claude/settings.json

# 4. Trigger hook (e.g., run bash command if bash logger enabled)
```

### Manual Test: Create Custom Hook
```bash
# 1. Via UI: Create custom hook with config
# 2. Check settings.json was updated
# 3. Trigger hook event
```

## Summary

✅ Hooks are stored in `.claude/settings.json` for Claude Code runtime
✅ Database tracks hook metadata and relationships
✅ `hook_file_service.apply_hook_to_settings()` merges configs into settings.json
✅ When enabling a hook, config is automatically applied
✅ When creating a custom hook, config is automatically applied after creation
✅ When disabling a hook, config is removed from settings.json

---

**All hooks operations properly update `.claude/settings.json` in the project!** 🎉
