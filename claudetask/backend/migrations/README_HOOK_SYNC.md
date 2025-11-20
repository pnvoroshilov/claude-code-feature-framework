# Hook Configuration Sync System

## Problem Statement

Projects were showing hooks with inline bash commands in `.claude/settings.json` instead of script references (e.g., `.claude/hooks/post-push-docs.sh`).

### Root Cause

1. **Database Seeding**: When the database was initially seeded, it used OLD versions of hook JSON files from `framework-assets/claude-hooks/` that contained inline commands
2. **Hook Enable Flow**: When users enable hooks via UI:
   - `hook_service.py` gets `hook_config` from database
   - `hook_file_service.py` writes `hook_config` directly to `.claude/settings.json`
   - If database has old format, settings.json gets old format
3. **JSON Files Updated But Database Not Synced**: JSON files were updated with script references, but database still had old inline commands

### Code Path

```
User clicks "Enable Hook" in UI
  ↓
hooks.py: POST /api/projects/{id}/hooks/{hook_id}/enable
  ↓
hook_service.py: enable_hook()
  ↓
hook_file_service.py: apply_hook_to_settings(hook.hook_config)  ← TAKES FROM DATABASE
  ↓
.claude/settings.json: Gets whatever is in database
```

## Solution

### 1. Fix Database Hook Configs

**Script**: `migrate_fix_post_merge_hook_config.py`
- Fixes the Post-Merge Documentation hook specifically
- Updates `hook_config` in `default_hooks` table to use script reference
```bash
python migrations/migrate_fix_post_merge_hook_config.py
```

### 2. Universal Hook Re-sync Tool

**Script**: `resync_all_hooks_from_json.py`
- Reads ALL hook JSON files from `framework-assets/claude-hooks/`
- Updates ALL hooks in `default_hooks` table with current JSON data
- Syncs: `hook_config`, `script_file`, `description`, `setup_instructions`, `dependencies`

**Usage**:
```bash
cd claudetask/backend
python migrations/resync_all_hooks_from_json.py
```

**When to use**:
- After updating any hook JSON file
- After adding new hooks
- After modifying hook configurations
- Periodic maintenance to ensure database is in sync

### 3. Per-Project Settings Rebuild

**Script**: `rebuild_project_hooks_settings.py`
- Reads enabled hooks for a project from database
- Rebuilds `.claude/settings.json` from current database hook_config
- Merges all enabled hooks into settings.json

**Usage**:
```bash
cd claudetask/backend
python migrations/rebuild_project_hooks_settings.py <project_id>
```

**When to use**:
- After re-syncing hooks (to update existing projects)
- When a project has wrong hook format in settings.json
- After manually editing database hooks

**Find project ID**:
```bash
sqlite3 data/claudetask.db "SELECT id, name, path FROM projects;"
```

## Complete Fix Workflow

### For Existing Projects with Wrong Format

1. **Re-sync database from JSON files**:
   ```bash
   python migrations/resync_all_hooks_from_json.py
   ```

2. **Find affected projects**:
   ```bash
   sqlite3 data/claudetask.db "SELECT id, name FROM projects;"
   ```

3. **Rebuild each project's settings.json**:
   ```bash
   python migrations/rebuild_project_hooks_settings.py <project_id>
   ```

### When Updating Hook JSON Files

1. **Edit JSON file** in `framework-assets/claude-hooks/`

2. **Re-sync database**:
   ```bash
   python migrations/resync_all_hooks_from_json.py
   ```

3. **Update affected projects** (two options):

   **Option A**: Rebuild automatically
   ```bash
   # For each project with this hook enabled:
   python migrations/rebuild_project_hooks_settings.py <project_id>
   ```

   **Option B**: Let users refresh via UI
   - User disables the hook
   - User re-enables the hook
   - New config from database is applied

## Verification

### Check Database Hook Config
```bash
sqlite3 data/claudetask.db "SELECT name, hook_config FROM default_hooks WHERE name = 'Post-Merge Documentation Update';"
```

Should show:
```json
{"PostToolUse":[{"matcher":"Bash","hooks":[{"type":"command","command":".claude/hooks/post-push-docs.sh"}]}]}
```

### Check Project Settings
```bash
cat /path/to/project/.claude/settings.json | jq '.hooks.PostToolUse[0].hooks[0].command'
```

Should show:
```
".claude/hooks/post-push-docs.sh"
```

NOT:
```
"LOGFILE=\".claude/logs/hooks/post-merge-doc-$(date +%Y%m%d).log\"; mkdir -p .claude/logs/hooks; ..."
```

## Prevention

### For Framework Developers

1. **Always update JSON files AND re-sync database**:
   ```bash
   # Edit framework-assets/claude-hooks/my-hook.json
   nano framework-assets/claude-hooks/my-hook.json

   # Re-sync database
   python migrations/resync_all_hooks_from_json.py
   ```

2. **Test in a fresh project**:
   ```bash
   # Create new project via UI
   # Enable the hook
   # Verify settings.json has correct format
   ```

3. **Add to CI/CD**:
   - Automated check that database matches JSON files
   - Warning if hook_config differs from JSON files

### For Project Maintainers

1. **After framework updates**:
   ```bash
   # Pull latest framework changes
   git pull origin main

   # Re-sync database
   cd claudetask/backend
   python migrations/resync_all_hooks_from_json.py

   # Rebuild your project's settings
   python migrations/rebuild_project_hooks_settings.py <your_project_id>
   ```

2. **Periodic health check**:
   ```bash
   # Compare database vs JSON files
   python migrations/resync_all_hooks_from_json.py

   # Should show 0 updates if already in sync
   ```

## Files Created

- **007_fix_post_merge_hook_config.sql**: SQL migration documentation
- **migrate_fix_post_merge_hook_config.py**: Fix specific hook (Post-Merge Documentation)
- **resync_all_hooks_from_json.py**: Universal hook sync tool (USE THIS REGULARLY)
- **rebuild_project_hooks_settings.py**: Per-project settings.json regeneration
- **README_HOOK_SYNC.md**: This documentation

## Testing Results

### TestProject Fix
- **Before**: `.claude/settings.json` had 50+ line inline bash command
- **After**: `.claude/settings.json` has `.claude/hooks/post-push-docs.sh`
- **Database**: hook_config now matches JSON file
- **Hook functionality**: Working correctly ✅

### All Hooks Synced
- File Protection ✓
- Bash Command Logger ✓
- Auto Code Formatter ✓
- Desktop Notifications ✓
- Post-Merge Documentation Update ✓ (fixed)
- Git Auto Commit ✓

## Architecture Notes

### Why This Design?

1. **Database is source of truth** for hook configs
2. **JSON files are the master templates** for database
3. **settings.json is generated** from database
4. **Separation of concerns**:
   - JSON files: Hook definitions (version controlled)
   - Database: Active hook configs (can be customized)
   - settings.json: Runtime configuration (per-project)

### Future Improvements

1. **Auto-sync on startup**: Check if JSON files are newer than database
2. **API endpoint**: Add `/api/admin/hooks/sync` to trigger re-sync
3. **Background job**: Periodically check for JSON file changes
4. **Migration system**: Track which JSON versions are in database
5. **UI indicator**: Show if hook config is outdated in UI
