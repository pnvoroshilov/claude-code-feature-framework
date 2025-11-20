# Database Migrations Guide

Complete guide to ClaudeTask database migrations, including migration history, execution procedures, and troubleshooting.

## Overview

ClaudeTask uses SQLite database migrations to evolve the schema over time. All migrations are idempotent and can be safely re-run.

## Migration Directory Structure

```
claudetask/backend/migrations/
├── README.md                              # Migration documentation
├── README_HOOK_SYNC.md                    # Hook synchronization workflow guide
├── 001_initial_schema.sql                 # SQL: Initial tables
├── 002_add_skills_subagents.sql           # SQL: Skills and subagents
├── 003_add_hooks_tables.sql               # SQL: Hooks support
├── 004_add_script_file_to_hooks.sql       # SQL: Hook script files
├── 005_add_worktree_enabled.sql           # SQL: Worktree toggle support
├── 006_add_cascade_delete.sql             # SQL: CASCADE DELETE constraints
├── 007_fix_post_merge_hook_config.sql     # SQL: Hook config sync
├── migrate_add_hooks_tables.py            # Python: Run migrations 001-003
├── migrate_add_script_file_to_hooks.py    # Python: Run migration 004
├── migrate_add_worktree_enabled.py        # Python: Run migration 005
├── migrate_add_cascade_delete.py          # Python: Run migration 006
├── migrate_fix_post_merge_hook_config.py  # Python: Run migration 007
├── resync_all_hooks_from_json.py          # Python: Universal hook sync tool
└── rebuild_project_hooks_settings.py      # Python: Rebuild project settings
```

## Migration History

### 001: Initial Schema

**Created:** Project inception
**Purpose:** Core tables for projects, tasks, and task history

**Tables:**
- `projects` - Project metadata and configuration
- `tasks` - Task management with status tracking
- `task_history` - Audit log for task status changes
- `project_settings` - Project-specific settings
- `agents` - Agent configurations

**Key Features:**
- Task status enumeration (Backlog, Analysis, In Progress, Testing, Code Review, PR, Done, Blocked)
- Project mode support (simple, development)
- Custom instructions per project
- Task priority and type management

### 002: Add Skills and Subagents Tables

**Created:** Skills system implementation
**Purpose:** Support for skills marketplace and subagent management

**Tables:**
- `default_skills` - Framework-provided skills
- `custom_skills` - User-created project-specific skills
- `project_skills` - Junction table (many-to-many)
- `default_subagents` - Framework-provided subagents
- `custom_subagents` - User-created subagents
- `project_subagents` - Junction table (many-to-many)
- `agent_skill_recommendations` - Recommended skills per agent

**Key Features:**
- Skills categorization (development, testing, productivity)
- Subagent type management for Task tool integration
- Favorite marking for quick access
- Skill metadata and status tracking

### 003: Add Hooks Tables

**Created:** Hooks system implementation
**Purpose:** Support for Claude Code hooks marketplace

**Tables:**
- `default_hooks` - Framework-provided hooks
- `custom_hooks` - User-created project-specific hooks
- `project_hooks` - Junction table (many-to-many)

**Key Features:**
- Hook configuration JSON storage
- Category-based organization
- Setup instructions and dependencies
- Favorite marking
- Default hooks loaded from `framework-assets/claude-hooks/*.json`

**Initial Default Hooks:**
- Bash Command Logger
- Auto Code Formatter
- Desktop Notifications
- File Protection
- Git Auto Commit
- Post-Merge Documentation Update

### 004: Add script_file to Hooks Tables

**Created:** 2025-11-16
**Purpose:** Separate hook configuration from shell script implementation

**Changes:**
```sql
ALTER TABLE default_hooks ADD COLUMN script_file VARCHAR(100);
ALTER TABLE custom_hooks ADD COLUMN script_file VARCHAR(100);
```

**Key Features:**
- Optional script file reference (e.g., `post-push-docs.sh`)
- Cleaner separation of config vs. implementation
- Better maintainability for complex hooks
- Automatic script copying and chmod +x on enable

**Updated Hooks:**
- Post-Merge Documentation Update v2.0.0
  - Now uses `post-push-docs.sh` script file
  - URL encoding support for paths with spaces
  - Backend API integration
  - Enhanced recursion prevention

**Why This Change:**

**Before (v1.0.0):**
```json
{
  "hook_config": {
    "PostToolUse": [{
      "hooks": [{
        "command": "bash -c 'if echo \"$HOOK_INPUT\" | grep -q \"git push\"; then ...; fi'"
      }]
    }]
  }
}
```

**After (v2.0.0):**
```json
{
  "script_file": "post-push-docs.sh",
  "hook_config": {
    "PostToolUse": [{
      "hooks": [{
        "command": ".claude/hooks/post-push-docs.sh"
      }]
    }]
  }
}
```

**Benefits:**
- 120+ line shell script in separate file
- Proper syntax highlighting and editing
- Version control for script changes
- Easier testing and debugging

### 005: Add worktree_enabled to ProjectSettings

**Created:** 2025-11-20
**Purpose:** Enable/disable Git worktrees per project in DEVELOPMENT mode

**Changes:**
```sql
ALTER TABLE project_settings ADD COLUMN worktree_enabled BOOLEAN DEFAULT 1 NOT NULL;
UPDATE project_settings SET worktree_enabled = 1 WHERE worktree_enabled IS NULL;
```

**Key Features:**
- Toggle worktree functionality per project
- Default: enabled (value = 1/true)
- UI toggle in ProjectModeToggle component
- Dynamic CLAUDE.md generation based on setting
- WebSocket broadcast for real-time updates

**Use Cases:**

**Worktrees Enabled (Default):**
- Isolated workspace per task
- Parallel development on multiple tasks
- No interference between tasks
- Automatic cleanup after merge

**Worktrees Disabled:**
- Work directly in main branch
- Simpler workflow for solo developers
- Useful when repository doesn't support worktrees
- Reduced complexity for small projects

**Frontend Integration:**
```tsx
// ProjectModeToggle.tsx
const [worktreeEnabled, setWorktreeEnabled] = useState<boolean>(true);

// Toggle worktree setting
const handleWorktreeToggle = async (event) => {
  await updateProjectSettings(projectId, {
    worktree_enabled: event.target.checked
  });
  // Triggers CLAUDE.md regeneration
};
```

**Backend Integration:**
```python
# When worktree_enabled changes, regenerate CLAUDE.md
if worktree_changed:
    await ProjectService.regenerate_claude_md(db, project_id)

# Broadcast via WebSocket
await task_websocket_manager.broadcast_message({
    "type": "project_settings_updated",
    "project_id": project_id,
    "settings": {"worktree_enabled": settings.worktree_enabled}
})
```

**CLAUDE.md Generation:**
- If `worktree_enabled = true`: Full worktree instructions included
- If `worktree_enabled = false`: Worktree warnings and alternative workflow

**Why This Change:**
- Some repositories may not support git worktrees (submodules, Git LFS issues)
- Solo developers may prefer simpler workflow without worktrees
- Provides flexibility while maintaining DEVELOPMENT mode workflow
- Allows gradual adoption of worktree workflow

### 006: Add CASCADE DELETE to Foreign Keys

**Created:** 2025-11-20
**Purpose:** Fix project deletion to properly cascade delete all related records

**Changes:**
Recreate all tables with foreign keys referencing `projects.id` to include `ON DELETE CASCADE`:

**Affected Tables:**
- `tasks` - Task records
- `agents` - Agent configurations
- `project_settings` - Project-specific settings
- `custom_skills` - Project custom skills
- `custom_subagents` - Project custom subagents
- `project_skills` - Project-skill junction
- `project_mcp_configs` - Project MCP config junction
- `custom_mcp_configs` - Custom MCP configurations
- `custom_hooks` - Custom hook definitions
- `project_hooks` - Project-hook junction
- `project_subagents` - Project-subagent junction
- `claude_sessions` - Claude Code session records

**Key Features:**
- Automatic cascade deletion of all related records when project is deleted
- Orphaned record cleanup during migration
- No manual cleanup required in application code
- Referential integrity maintained

**Migration Process:**
1. Disable foreign key constraints temporarily
2. Clean up existing orphaned records
3. For each table with project_id FK:
   - Backup data to temporary table
   - Drop original table
   - Recreate table with CASCADE DELETE
   - Restore data from backup
   - Drop temporary table
4. Re-enable foreign key constraints
5. Verify CASCADE DELETE works

**Before Migration:**
```sql
-- Manual cleanup required in application code
DELETE FROM tasks WHERE project_id = ?;
DELETE FROM agents WHERE project_id = ?;
DELETE FROM project_settings WHERE project_id = ?;
-- ... 9 more manual deletes ...
DELETE FROM projects WHERE id = ?;
```

**After Migration:**
```sql
-- Single delete cascades to all related records
DELETE FROM projects WHERE id = ?;
-- All related records automatically deleted!
```

**Why This Change:**
- **Problem:** Deleting a project required manual cleanup of 12+ related tables
- **Risk:** Orphaned records if any delete fails
- **Complexity:** Application code had to manage cascade logic
- **Solution:** Database-level CASCADE DELETE ensures automatic cleanup
- **Benefit:** Safer, simpler, more reliable project deletion

**Testing Verification:**
```sql
-- Create test project with related records
INSERT INTO projects (id, name, path) VALUES ('test-project', 'Test', '/path');
INSERT INTO tasks (id, project_id, title) VALUES (1, 'test-project', 'Task 1');
INSERT INTO agents (id, project_id, name) VALUES (1, 'test-project', 'Agent 1');

-- Delete project (should cascade)
DELETE FROM projects WHERE id = 'test-project';

-- Verify cascade worked
SELECT COUNT(*) FROM tasks WHERE project_id = 'test-project';     -- Should be 0
SELECT COUNT(*) FROM agents WHERE project_id = 'test-project';    -- Should be 0
```

**Project Initialization Timeout:**

Related improvement: Increased project initialization timeout from 10s to 30s to accommodate the directory trust initialization step, which launches a Claude session and waits for user acceptance of the trust prompt.

### 007: Fix Post-Merge Hook Configuration ⭐ LATEST

**Created:** 2025-11-20
**Purpose:** Fix Post-Merge Documentation hook to use script reference instead of inline command

**Changes:**
Updates the `hook_config` JSON in `default_hooks` table for the Post-Merge Documentation Update hook.

**Before (v1.0.0 - Inline Command):**
```json
{
  "PostToolUse": [{
    "matcher": "Bash",
    "hooks": [{
      "type": "command",
      "command": "LOGFILE=\".claude/logs/hooks/post-merge-doc-$(date +%Y%m%d).log\"; mkdir -p .claude/logs/hooks; echo \"[$(date)] Hook triggered\" >> \"$LOGFILE\"; ..."
    }]
  }]
}
```

**After (v2.0.0 - Script Reference):**
```json
{
  "PostToolUse": [{
    "matcher": "Bash",
    "hooks": [{
      "type": "command",
      "command": ".claude/hooks/post-push-docs.sh"
    }]
  }]
}
```

**Key Features:**
- Updates database hook configuration to reference external script
- Ensures consistency between database and JSON source files
- Enables cleaner hook configuration management
- Supports framework hook synchronization tools

**Root Cause:**
- Database was seeded with old version of hook JSON files containing inline commands
- JSON files in `framework-assets/claude-hooks/` were updated with script references
- Database hooks were not re-synced, causing mismatch
- When users enabled hooks via UI, they got old inline format from database

**Migration Process:**
```python
correct_hook_config = {
    "PostToolUse": [{
        "matcher": "Bash",
        "hooks": [{
            "type": "command",
            "command": ".claude/hooks/post-push-docs.sh"
        }]
    }]
}

cursor.execute("""
    UPDATE default_hooks
    SET hook_config = ?
    WHERE name = 'Post-Merge Documentation Update'
""", (json.dumps(correct_hook_config),))
```

**Why This Change:**
- **Problem:** Projects showing hooks with inline bash commands in `.claude/settings.json`
- **Issue:** Database contained old format, JSON files had new format
- **Impact:** Users enabling hooks got outdated inline format
- **Solution:** Update database to match current JSON source files
- **Benefit:** Consistent hook format across all projects

**Related Tools:**
- `resync_all_hooks_from_json.py` - Universal hook synchronization from JSON files
- `rebuild_project_hooks_settings.py` - Rebuild project settings from updated database
- See `migrations/README_HOOK_SYNC.md` for complete workflow

**Verification:**
```bash
# Check database hook config
sqlite3 data/claudetask.db "SELECT hook_config FROM default_hooks WHERE name = 'Post-Merge Documentation Update';"

# Should show: {"PostToolUse":[{"matcher":"Bash","hooks":[{"type":"command","command":".claude/hooks/post-push-docs.sh"}]}]}

# Check project settings
cat /path/to/project/.claude/settings.json | jq '.hooks.PostToolUse[0].hooks[0].command'

# Should show: ".claude/hooks/post-push-docs.sh"
```

## Running Migrations

### Fresh Database Installation

Run all migrations from scratch:

```bash
# Navigate to project root
cd /path/to/Claude\ Code\ Feature\ Framework

# Run complete migration (001-003)
python claudetask/backend/migrations/migrate_add_hooks_tables.py

# Run migration 004 (script_file support)
python claudetask/backend/migrations/migrate_add_script_file_to_hooks.py

# Run migration 005 (worktree_enabled support)
python claudetask/backend/migrations/migrate_add_worktree_enabled.py

# Run migration 006 (CASCADE DELETE support)
python claudetask/backend/migrations/migrate_add_cascade_delete.py

# Run migration 007 (Fix post-merge hook config)
python claudetask/backend/migrations/migrate_fix_post_merge_hook_config.py

# Alternative: Resync all hooks from JSON (recommended)
python claudetask/backend/migrations/resync_all_hooks_from_json.py
```

### Incremental Migration (Existing Database)

If you already have a database with migrations 001-006:

```bash
# Fix post-merge hook configuration
python claudetask/backend/migrations/migrate_fix_post_merge_hook_config.py

# Or resync all hooks from JSON source (recommended)
python claudetask/backend/migrations/resync_all_hooks_from_json.py
```

If you already have a database with migrations 001-005:

```bash
# Add CASCADE DELETE to foreign keys
python claudetask/backend/migrations/migrate_add_cascade_delete.py

# Fix post-merge hook configuration
python claudetask/backend/migrations/migrate_fix_post_merge_hook_config.py
```

If you already have a database with migrations 001-004:

```bash
# Add worktree_enabled column to project_settings
python claudetask/backend/migrations/migrate_add_worktree_enabled.py

# Add CASCADE DELETE to foreign keys
python claudetask/backend/migrations/migrate_add_cascade_delete.py
```

If you have a database with migrations 001-003:

```bash
# Add script_file column to hooks tables
python claudetask/backend/migrations/migrate_add_script_file_to_hooks.py

# Add worktree_enabled column to project_settings
python claudetask/backend/migrations/migrate_add_worktree_enabled.py

# Add CASCADE DELETE to foreign keys
python claudetask/backend/migrations/migrate_add_cascade_delete.py

# Fix post-merge hook configuration
python claudetask/backend/migrations/migrate_fix_post_merge_hook_config.py
```

### Migration 005 Only

For databases that need worktree_enabled support:

```bash
python claudetask/backend/migrations/migrate_add_worktree_enabled.py
```

This script:
1. Adds `worktree_enabled BOOLEAN DEFAULT 1 NOT NULL` to `project_settings` table
2. Updates existing records to set `worktree_enabled = 1` (enabled by default)
3. Handles "duplicate column" errors gracefully (idempotent)

### Migration 006 Only

For databases that need CASCADE DELETE constraints:

```bash
python claudetask/backend/migrations/migrate_add_cascade_delete.py
```

This script:
1. Creates backup of all tables with project_id foreign keys
2. Recreates tables with `ON DELETE CASCADE` constraint
3. Restores all data from backups
4. Cleans up orphaned records (records referencing non-existent projects)
5. Verifies CASCADE DELETE functionality

**Important Notes:**
- This migration recreates multiple tables - backup your database first!
- Migration may take 1-2 minutes for large databases
- All data is preserved during table recreation
- Orphaned records are automatically cleaned up

### Migration 007 Only

For databases that need hook configuration sync:

```bash
# Option 1: Fix only Post-Merge hook (specific fix)
python claudetask/backend/migrations/migrate_fix_post_merge_hook_config.py

# Option 2: Resync all hooks from JSON source (recommended)
python claudetask/backend/migrations/resync_all_hooks_from_json.py
```

**migrate_fix_post_merge_hook_config.py:**
- Updates only the Post-Merge Documentation Update hook
- Changes inline command to script reference
- Idempotent and safe to re-run

**resync_all_hooks_from_json.py** (Recommended):
- Reads ALL hook JSON files from `framework-assets/claude-hooks/`
- Updates ALL hooks in database with current JSON data
- Syncs: hook_config, script_file, description, setup_instructions, dependencies
- Ensures database matches JSON source files
- Use after updating any hook JSON file

After re-syncing hooks in database, update affected projects:

```bash
# Rebuild .claude/settings.json for a specific project
python claudetask/backend/migrations/rebuild_project_hooks_settings.py <project_id>

# Find project IDs
sqlite3 data/claudetask.db "SELECT id, name FROM projects;"
```

### Migration 004 Only

For databases that already have hooks tables but need script_file support:

```bash
python claudetask/backend/migrations/migrate_add_script_file_to_hooks.py
```

This script:
1. Adds `script_file VARCHAR(100)` to `default_hooks` table
2. Adds `script_file VARCHAR(100)` to `custom_hooks` table
3. Handles "duplicate column" errors gracefully (idempotent)

## Migration Scripts

### migrate_add_hooks_tables.py

Complete migration script that runs 001-003:

```python
def migrate():
    """Run all migrations up to and including hooks tables"""
    conn = get_db_connection()

    # 001: Initial schema
    with open('001_initial_schema.sql', 'r') as f:
        conn.executescript(f.read())

    # 002: Skills and subagents
    with open('002_add_skills_subagents.sql', 'r') as f:
        conn.executescript(f.read())

    # 003: Hooks tables
    with open('003_add_hooks_tables.sql', 'r') as f:
        conn.executescript(f.read())

    # Load default hooks from framework-assets
    load_default_hooks(conn)

    conn.commit()
```

### migrate_add_script_file_to_hooks.py

Migration 004 implementation:

```python
def migrate():
    """Add script_file column to hooks tables"""
    conn = get_db_connection()

    # Add column to default_hooks (idempotent)
    try:
        conn.execute("""
            ALTER TABLE default_hooks
            ADD COLUMN script_file VARCHAR(100)
        """)
        print("✓ Added script_file to default_hooks")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e):
            print("⊙ script_file already exists in default_hooks")
        else:
            raise

    # Add column to custom_hooks (idempotent)
    try:
        conn.execute("""
            ALTER TABLE custom_hooks
            ADD COLUMN script_file VARCHAR(100)
        """)
        print("✓ Added script_file to custom_hooks")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e):
            print("⊙ script_file already exists in custom_hooks")
        else:
            raise

    conn.commit()
    print("\n✓ Migration 004 complete")
```

### migrate_fix_post_merge_hook_config.py

Migration 007: Fix Post-Merge hook configuration to use script reference:

```python
def fix_hook_config():
    """Update Post-Merge Documentation hook_config to use script reference"""
    conn = get_db_connection()

    correct_hook_config = {
        "PostToolUse": [{
            "matcher": "Bash",
            "hooks": [{
                "type": "command",
                "command": ".claude/hooks/post-push-docs.sh"
            }]
        }]
    }

    # Update the hook_config JSON
    cursor.execute("""
        UPDATE default_hooks
        SET hook_config = ?
        WHERE name = 'Post-Merge Documentation Update'
    """, (json.dumps(correct_hook_config),))

    conn.commit()
    print("✓ Post-Merge Documentation Update hook_config fixed")
```

**Key Features:**
- Updates database hook_config to match JSON source files
- Changes from inline bash command to script reference
- Ensures consistency across framework

### resync_all_hooks_from_json.py

Universal hook synchronization tool (recommended for hook updates):

```python
def resync_hooks():
    """Resync all hooks from JSON files in framework-assets"""
    conn = get_db_connection()
    hooks_dir = "framework-assets/claude-hooks"

    for json_file in os.listdir(hooks_dir):
        if not json_file.endswith(".json"):
            continue

        # Read JSON hook definition
        with open(os.path.join(hooks_dir, json_file), "r") as f:
            hook_data = json.load(f)

        # Update or insert hook in database
        conn.execute("""
            UPDATE default_hooks
            SET
                hook_config = ?,
                script_file = ?,
                description = ?,
                setup_instructions = ?,
                dependencies = ?
            WHERE file_name = ?
        """, (
            json.dumps(hook_data["hook_config"]),
            hook_data.get("script_file"),
            hook_data["description"],
            hook_data.get("setup_instructions"),
            json.dumps(hook_data.get("dependencies", [])),
            json_file
        ))

    conn.commit()
    print(f"✓ Resynced {len(hooks)} hooks from JSON source")
```

**When to Use:**
- After updating any hook JSON file in framework-assets
- To ensure database matches current hook definitions
- After framework updates with new hook versions
- Periodic maintenance to keep hooks synchronized

### rebuild_project_hooks_settings.py

Rebuild project settings.json from database hooks:

```python
def rebuild_settings(project_id: str):
    """Rebuild .claude/settings.json from enabled hooks in database"""
    conn = get_db_connection()

    # Get project path
    project = conn.execute(
        "SELECT path FROM projects WHERE id = ?",
        (project_id,)
    ).fetchone()

    # Get all enabled hooks for project
    enabled_hooks = conn.execute("""
        SELECT h.hook_config
        FROM project_hooks ph
        JOIN default_hooks h ON ph.hook_id = h.id
        WHERE ph.project_id = ? AND ph.hook_type = 'default'
    """, (project_id,)).fetchall()

    # Merge all hook configs into settings.json
    merged_config = merge_hook_configs([h[0] for h in enabled_hooks])

    # Write to .claude/settings.json
    settings_file = os.path.join(project_path, ".claude/settings.json")
    with open(settings_file, "w") as f:
        json.dump({"hooks": merged_config}, f, indent=2)

    print(f"✓ Rebuilt settings.json for project {project_id}")
```

**When to Use:**
- After running resync_all_hooks_from_json.py
- When project has wrong hook format in settings.json
- After manually editing database hooks
- To propagate hook updates to existing projects

## Hook Script File Workflow

### 1. Framework Storage

Default hooks and their scripts live in framework assets:

```
framework-assets/claude-hooks/
├── post-merge-documentation.json  # Hook configuration
└── post-push-docs.sh              # Shell script (v2.0.0)
```

### 2. Database Storage

When hooks are loaded into database:

```sql
INSERT INTO default_hooks (
    name,
    file_name,
    script_file,              -- NEW: post-push-docs.sh
    hook_config,
    ...
) VALUES (
    'Post-Merge Documentation Update',
    'post-merge-documentation.json',
    'post-push-docs.sh',      -- References separate script
    '{ "PostToolUse": [...] }',
    ...
);
```

### 3. Project Installation

When user enables a hook with script_file:

```python
# hook_file_service.py
def copy_hook_to_project(project_path, hook):
    if hook.script_file:
        # Copy script from framework to project
        src = f"framework-assets/claude-hooks/{hook.script_file}"
        dst = f"{project_path}/.claude/hooks/{hook.script_file}"

        shutil.copy(src, dst)
        os.chmod(dst, 0o755)  # Make executable
```

Result in project:
```
project/
└── .claude/
    ├── hooks/
    │   └── post-push-docs.sh  # Copied, executable
    └── settings.json          # References script in hook_config
```

### 4. Hook Execution

When Claude Code triggers the hook:

```
PostToolUse Event (Bash)
      ↓
Read .claude/settings.json
      ↓
Execute: .claude/hooks/post-push-docs.sh
      ↓
Script receives JSON via stdin
      ↓
Script performs actions
```

## Idempotent Migration Design

All migrations are designed to be safely re-run:

```python
# Pattern 1: Try-except for ALTER TABLE
try:
    conn.execute("ALTER TABLE table ADD COLUMN column_name TYPE")
except sqlite3.OperationalError as e:
    if "duplicate column" in str(e):
        pass  # Already migrated
    else:
        raise

# Pattern 2: CREATE TABLE IF NOT EXISTS
conn.execute("""
    CREATE TABLE IF NOT EXISTS table_name (
        id INTEGER PRIMARY KEY,
        ...
    )
""")

# Pattern 3: Conditional INSERT
conn.execute("""
    INSERT INTO table (name, ...)
    SELECT 'value', ...
    WHERE NOT EXISTS (SELECT 1 FROM table WHERE name = 'value')
""")
```

## Troubleshooting

### Migration Fails: "table already exists"

**Symptom:**
```
sqlite3.OperationalError: table default_hooks already exists
```

**Cause:** Database already has this migration applied

**Solution:** This is normal for idempotent migrations. The error is caught and ignored.

**Verification:**
```bash
sqlite3 claudetask/backend/claudetask.db ".schema default_hooks"
```

### Migration Fails: "duplicate column name: script_file"

**Symptom:**
```
sqlite3.OperationalError: duplicate column name: script_file
```

**Cause:** Migration 004 already applied

**Solution:** This is expected behavior. Migration script catches and ignores this error.

**Verification:**
```bash
sqlite3 claudetask/backend/claudetask.db "PRAGMA table_info(default_hooks);"
```

Look for:
```
8|script_file|VARCHAR(100)|0||0
```

### Hook Script Not Copied to Project

**Symptom:** Hook enabled but `.claude/hooks/script.sh` doesn't exist

**Possible Causes:**
1. Migration 004 not run (script_file column missing)
2. Script file missing from framework-assets
3. Hook service not updated to copy script files

**Solution:**
```bash
# 1. Check migration status
sqlite3 claudetask/backend/claudetask.db "PRAGMA table_info(default_hooks);" | grep script_file

# 2. Check framework assets
ls -la framework-assets/claude-hooks/post-push-docs.sh

# 3. Re-enable hook (will copy script)
# Go to UI > Hooks > Disable > Enable
```

### Script Not Executable

**Symptom:** Hook triggers but script fails with "Permission denied"

**Cause:** Script not made executable during copy

**Solution:**
```bash
chmod +x .claude/hooks/post-push-docs.sh
```

**Prevention:** Backend service should automatically `chmod +x`:
```python
os.chmod(script_path, 0o755)
```

### Database Locked Error

**Symptom:**
```
sqlite3.OperationalError: database is locked
```

**Cause:** Another process has the database open

**Solution:**
```bash
# Stop backend server
# Stop any active Claude sessions
# Run migration
# Restart services
```

## Database Schema Inspection

Useful commands for inspecting migration state:

```bash
# Connect to database
sqlite3 claudetask/backend/claudetask.db

# List all tables
.tables

# Show table schema
.schema default_hooks

# Show column info
PRAGMA table_info(default_hooks);

# Count hooks
SELECT COUNT(*) FROM default_hooks;

# Check for script_file values
SELECT name, script_file FROM default_hooks WHERE script_file IS NOT NULL;

# Show Post-Merge hook details
SELECT * FROM default_hooks WHERE name = 'Post-Merge Documentation Update';
```

## Best Practices

### 1. Always Backup Before Migration

```bash
cp claudetask/backend/claudetask.db claudetask/backend/claudetask.db.backup
```

### 2. Test Migrations on Copy

```bash
# Test on database copy
cp claudetask.db test.db
# Run migration against test.db
# Verify results
# Then run on production database
```

### 3. Version Control SQL Files

Keep all `.sql` migration files in git:
```
migrations/
├── 001_initial_schema.sql
├── 002_add_skills_subagents.sql
├── 003_add_hooks_tables.sql
└── 004_add_script_file_to_hooks.sql
```

### 4. Document Migration Intent

Each migration should have:
- Clear purpose statement
- List of changes
- Reason for changes
- Backward compatibility notes

### 5. Make Migrations Idempotent

Always design migrations to be safely re-run:
- Use `IF NOT EXISTS` for CREATE
- Catch `duplicate column` errors for ALTER
- Use conditional INSERT with NOT EXISTS

## Migration Checklist

Before running a migration:

- [ ] Backup database
- [ ] Review migration SQL/Python code
- [ ] Check migration history (which migrations already applied)
- [ ] Verify migration is idempotent
- [ ] Test on database copy first
- [ ] Stop backend server (prevent lock)
- [ ] Run migration
- [ ] Verify schema changes
- [ ] Test functionality
- [ ] Restart backend server

## Future Migrations

When adding new migrations:

1. **Create SQL file**: `00X_description.sql`
2. **Create Python script**: `migrate_description.py`
3. **Update README.md**: Document migration purpose
4. **Add to migration history**: This document
5. **Test idempotency**: Ensure safe re-run
6. **Update schema docs**: Reflect new tables/columns

## See Also

- [Hooks System Architecture](../architecture/hooks-system.md) - Complete hooks system documentation
- [Hook Synchronization Guide](../../claudetask/backend/migrations/README_HOOK_SYNC.md) - Hook config sync workflow
- [Framework Updates](../architecture/framework-updates.md) - Framework file synchronization
- [Database Models](../../claudetask/backend/app/models.py) - SQLAlchemy model definitions
- [Migration README](../../claudetask/backend/migrations/README.md) - Migration overview
