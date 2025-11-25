# Hooks System Architecture

The ClaudeTask Framework includes a sophisticated hooks system that allows deterministic control over Claude Code's behavior through shell commands executed at specific workflow points.

## Overview

Hooks are shell commands that execute automatically at specific points in Claude Code's workflow, providing:
- **Deterministic behavior**: Actions always happen, not dependent on AI choices
- **Automation**: Trigger documentation updates, formatting, notifications, etc.
- **Integration**: Connect Claude Code with external tools and APIs
- **Customization**: Tailor Claude's behavior to project needs

## Database Schema

### Hooks Tables

The hooks system uses three main tables:

#### 1. `default_hooks`

Framework-provided hooks stored in the database.

```sql
CREATE TABLE default_hooks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(100) NOT NULL UNIQUE,
    description TEXT NOT NULL,
    category VARCHAR(50) NOT NULL,
    file_name VARCHAR(100) NOT NULL,
    script_file VARCHAR(100),  -- Optional separate script file
    hook_config JSON NOT NULL,
    setup_instructions TEXT,
    dependencies JSON,
    is_active BOOLEAN DEFAULT TRUE,
    is_favorite BOOLEAN DEFAULT FALSE,
    created_at DATETIME,
    updated_at DATETIME
);
```

**Key Fields:**
- `name`: Unique hook identifier (e.g., "Post-Merge Documentation Update")
- `category`: Hook category (logging, formatting, version-control, memory, etc.)
- `file_name`: JSON configuration filename (e.g., "post-merge-documentation.json")
- `script_file`: **NEW in v004** - Optional separate shell script (e.g., "post-push-docs.sh")
- `hook_config`: JSON object defining hook events and commands
- `dependencies`: Required tools (jq, git, curl, etc.)

#### 2. `custom_hooks`

User-created project-specific hooks.

```sql
CREATE TABLE custom_hooks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id VARCHAR REFERENCES projects(id),
    name VARCHAR(100) NOT NULL,
    description TEXT NOT NULL,
    category VARCHAR(50) NOT NULL,
    file_name VARCHAR(100) NOT NULL,
    script_file VARCHAR(100),  -- Optional separate script file
    hook_config JSON NOT NULL,
    setup_instructions TEXT,
    dependencies JSON,
    status VARCHAR(20) DEFAULT 'active',
    error_message TEXT,
    created_by VARCHAR(100),
    is_favorite BOOLEAN DEFAULT FALSE,
    created_at DATETIME,
    updated_at DATETIME
);
```

#### 3. `project_hooks`

Junction table linking projects to enabled hooks.

```sql
CREATE TABLE project_hooks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id VARCHAR REFERENCES projects(id),
    hook_id INTEGER NOT NULL,
    hook_type VARCHAR(10) NOT NULL,  -- 'default' or 'custom'
    enabled_at DATETIME,
    enabled_by VARCHAR(100)
);
```

## Hook Categories

| Category | Purpose | Examples |
|----------|---------|----------|
| `memory` | Project memory and knowledge capture | Conversation capture, file edit tracking |
| `version-control` | Git workflow automation | Post-merge docs, RAG indexing |
| `logging` | Activity tracking and audit | Command logging, tool usage tracking |
| `formatting` | Code quality and style | Auto-formatting, linting |
| `notifications` | User alerts and updates | Desktop notifications, status updates |

## Script File Support (Migration 004)

### What Changed

Migration 004 introduced the `script_file` column to separate hook configuration from implementation:

**Before (v1.0.0):** Inline commands in hook_config
```json
{
  "hook_config": {
    "PostToolUse": [{
      "hooks": [{
        "type": "command",
        "command": "bash -c 'long inline script here...'"
      }]
    }]
  }
}
```

**After (v2.0.0):** Separate script file
```json
{
  "script_file": "post-push-docs.sh",
  "hook_config": {
    "PostToolUse": [{
      "hooks": [{
        "type": "command",
        "command": ".claude/hooks/post-push-docs.sh"
      }]
    }]
  }
}
```

### Benefits

1. **Better Organization**: Complex hooks live in separate `.sh` files
2. **Easier Maintenance**: Edit shell scripts without touching JSON
3. **Proper Permissions**: Scripts are automatically `chmod +x`
4. **Version Control**: Track script changes independently
5. **Reusability**: Share scripts across hook configurations

### Workflow

#### 1. Framework Storage
```
framework-assets/claude-hooks/
├── post-merge-documentation.json  # Hook configuration
├── post-push-docs.sh              # Shell script implementation
├── memory-capture.json            # Memory conversation capture config
├── memory-capture.sh              # Memory conversation capture script
├── memory-file-edit-capture.json  # NEW: File edit capture config
└── memory-file-edit-capture.sh    # NEW: File edit capture script
```

#### 2. Database Storage
```sql
INSERT INTO default_hooks (
    name,
    file_name,           -- post-merge-documentation.json
    script_file,         -- post-push-docs.sh
    hook_config,
    ...
)
```

#### 3. Project Installation

**IMPORTANT**: As of 2025-11-20, hooks are NOT automatically enabled during project initialization.

During project creation:
```python
# project_service.py - _create_project_structure()
# 1. Create .claude/hooks/ directory
hooks_dir = os.path.join(claude_dir, "hooks")
os.makedirs(hooks_dir, exist_ok=True)

# 2. Copy ALL hook scripts (.sh files) from framework-assets
#    Scripts are ready for use when user enables hooks via UI
for hook_file in os.listdir(hooks_source_dir):
    if hook_file.endswith(".sh"):
        source_file = os.path.join(hooks_source_dir, hook_file)
        dest_file = os.path.join(hooks_dir, hook_file)
        shutil.copy(source_file, dest_file)
        os.chmod(dest_file, 0o755)  # Make executable

# 3. Create empty .claude/settings.json
settings_data = {"hooks": {}}  # No hooks enabled by default
```

When user enables a hook via UI:
```python
# hook_file_service.py
def copy_hook_to_project(project_path, hook):
    """
    1. Script already exists in .claude/hooks/ (copied during initialization)
    2. Merge hook_config into .claude/settings.json
    3. Hook becomes active
    """
    # Script is already present and executable
    # Just merge hook configuration into settings.json
```

#### 4. Settings Files

**`.claude/settings.json`** - Hook configurations (user-controlled):
```json
{
  "hooks": {
    "PostToolUse": [{
      "matcher": "Bash",
      "hooks": [{
        "type": "command",
        "command": ".claude/hooks/post-push-docs.sh"
      }]
    }]
  }
}
```

**`.claude/settings.local.json`** - MCP server configuration (automatically generated):
```json
{
  "enabledMcpjsonServers": [
    "playwright",
    "claudetask",
    "serena"
  ],
  "enableAllProjectMcpServers": true
}
```

**Key Points**:
- **settings.json**: Created empty during initialization, populated when hooks are enabled
- **settings.local.json**: Automatically generated with essential MCP servers
- Both files created in `.claude/` directory during project initialization
- settings.local.json requires Claude Code restart to take effect

## Hook Configuration Format

### JSON Structure

```json
{
  "name": "Hook Name",
  "description": "What the hook does",
  "category": "category-name",
  "version": "2.0.0",
  "script_file": "optional-script.sh",
  "hook_config": {
    "EventName": [
      {
        "matcher": "ToolName",
        "hooks": [
          {
            "type": "command",
            "command": "shell command or .claude/hooks/script.sh"
          }
        ]
      }
    ]
  },
  "setup_instructions": "How to setup/configure",
  "dependencies": ["jq", "git", "curl"]
}
```

### Available Hook Events

| Event | Trigger Point | Use Cases |
|-------|---------------|-----------|
| `PreToolUse` | Before tool execution | Validation, blocking actions |
| `PostToolUse` | After tool completion | Logging, automation, notifications |
| `UserPromptSubmit` | User submits prompt | Pre-processing, context injection |
| `Notification` | Claude sends notification | Desktop alerts, logging |
| `Stop` | Claude finishes responding | Cleanup, summary |
| `SubagentStop` | Subagent task completes | Coordination, status updates |
| `PreCompact` | Before compaction | Backup, archiving |
| `SessionStart` | Session initialization | Setup, environment prep |
| `SessionEnd` | Session termination | Cleanup, reporting |

**Event Details:**

- **UserPromptSubmit**: Triggered when user submits a prompt to Claude
  - Receives prompt content as JSON input
  - Can inject additional context into Claude's environment
  - Use for automatic context enrichment, prompt pre-processing
  - Example: inject-docs-update hook adds documentation update instruction

### Hook Input Format

Hooks receive JSON input via stdin:

```json
{
  "tool_name": "Bash",
  "tool_input": {
    "command": "git push origin main",
    "description": "Push changes to main"
  },
  "result": {
    "stdout": "...",
    "stderr": "...",
    "exit_code": 0
  }
}
```

## Default Hooks

### 1. Memory Conversation Capture

**Purpose**: Automatically captures conversation messages to project memory

**Category**: `memory`

**Events**: `Stop` (after Claude finishes responding)

**Script**: `memory-capture.sh`

**What it does**:
- Captures conversation messages via Claude Code transcript file
- Sends messages to backend API for storage
- Enables project memory persistence across sessions
- Required for GET project_memory_context to work

**Configuration**:
```json
{
  "name": "Memory Conversation Capture",
  "category": "memory",
  "hook_config": {
    "Stop": [{
      "matcher": "*",
      "hooks": [{
        "type": "command",
        "command": ".claude/hooks/memory-capture.sh"
      }]
    }]
  }
}
```

### 2. Memory File Edit Capture (NEW)

**Purpose**: Automatically captures file edit operations (Edit, Write, MultiEdit, Update) to project memory

**Category**: `memory`

**Events**: `PostToolUse` (Edit, Write, MultiEdit, Update)

**Script**: `memory-file-edit-capture.sh`

**What it does**:
- Detects file edit operations (Edit, Write, MultiEdit, Update tools)
- Extracts file path and creates meaningful summary
- Saves to project memory via backend API
- Provides edit history and context for future sessions

**Configuration**:
```json
{
  "name": "Memory File Edit Capture",
  "category": "memory",
  "hook_config": {
    "PostToolUse": [
      {
        "matcher": "Edit",
        "hooks": [{"type": "command", "command": ".claude/hooks/memory-file-edit-capture.sh"}]
      },
      {
        "matcher": "Write",
        "hooks": [{"type": "command", "command": ".claude/hooks/memory-file-edit-capture.sh"}]
      },
      {
        "matcher": "MultiEdit",
        "hooks": [{"type": "command", "command": ".claude/hooks/memory-file-edit-capture.sh"}]
      },
      {
        "matcher": "Update",
        "hooks": [{"type": "command", "command": ".claude/hooks/memory-file-edit-capture.sh"}]
      }
    ]
  }
}
```

**Key Features**:
- Tool-specific summaries (Edit vs Write vs MultiEdit)
- Captures file paths and content previews
- Metadata includes event_type, tool_name, file_path
- Graceful failure if backend unavailable

### 3. Memory Session Summarizer

**Purpose**: Periodically updates project summary based on conversation history

**Category**: `memory`

**Events**: `Stop` (after Claude finishes responding)

**Script**: `memory-session-summarize.sh`

**What it does**:
- Checks if 30+ messages accumulated since last summary
- Triggers project summary update via backend API
- Accumulates knowledge over time
- Reduces summarization frequency (optimized from 50 to 30 messages)

### 4. Post-Merge Documentation Update

**Purpose**: Automatically updates documentation after merging to main branch

**Category**: `version-control`

**Events**: `PostToolUse` (Bash tool after git push/merge)

**Script**: `post-push-docs.sh`

**What it does**:
- Detects git push/merge to main branch
- Calls backend API to execute `/update-documentation` command
- Launches embedded Claude session with documentation updater agent
- Prevents recursion with lock files and `[skip-hook]` tag

### 5. Post-Merge RAG Indexing

**Purpose**: Indexes documentation for semantic search after git merges

**Category**: `version-control`

**Events**: `PostToolUse` (Bash tool after git push)

**Script**: `post-merge-rag-indexing.sh`

**What it does**:
- Detects git push commands (including simple `git push`)
- Triggers RAG indexing of `docs/` directory
- Enables semantic search across project documentation
- Skips if `[skip-rag]` tag in commit message

## Case Study 1: Post-Merge Documentation Hook

### Version 2.0.0 Architecture

The post-merge documentation hook demonstrates advanced hook capabilities:

#### Components

1. **Hook Configuration** (`post-merge-documentation.json`):
   - Defines PostToolUse event for Bash commands
   - References separate script file
   - Lists dependencies and setup instructions

2. **Shell Script** (`post-push-docs.sh`):
   - Parses hook input JSON with `jq`
   - Detects git push/merge to main branch
   - URL-encodes project path (handles spaces)
   - Calls backend API to execute `/update-documentation`
   - Implements recursion prevention with lock files
   - Provides comprehensive logging

#### Key Features

**URL Encoding for Paths with Spaces:**
```bash
# Problem: /Users/name/Start Up/Project
# Solution: URL encode with jq
PROJECT_DIR_ENCODED=$(printf %s "$PROJECT_ROOT" | jq -sRr @uri)
# Result: /Users/name/Start%20Up/Project
```

**Recursion Prevention:**
```bash
LOCKFILE="$LOGDIR/.hook-running"

if [ -f "$LOCKFILE" ]; then
    echo "Hook already running, skipping"
    exit 0
fi

touch "$LOCKFILE"
# ... execute hook ...
rm -f "$LOCKFILE"
```

**Skip Hook Tag:**
```bash
# Check for [skip-hook] in commit title (first line only)
COMMIT_FIRST_LINE=$(git log -1 --pretty=%s)
if echo "$COMMIT_FIRST_LINE" | grep -q '\[skip-hook\]'; then
    echo "Skipping due to [skip-hook] tag"
    exit 0
fi
```

**Backend API Integration:**
```bash
API_URL="http://localhost:3333/api/claude-sessions/execute-command"
COMMAND="/update-documentation"
PROJECT_DIR_ENCODED=$(printf %s "$PROJECT_ROOT" | jq -sRr @uri)

curl -s -X POST "$API_URL?command=${COMMAND}&project_dir=${PROJECT_DIR_ENCODED}"
```

#### Workflow Diagram

```
Git Push to Main
      ↓
PostToolUse Hook Triggered
      ↓
Parse JSON Input (jq)
      ↓
Check Lock File (prevent recursion)
      ↓
Detect Main Branch + Git Command
      ↓
Check for [skip-hook] Tag
      ↓
URL Encode Project Path
      ↓
Call Backend API
      ↓
Backend Launches Embedded Claude Session
      ↓
Execute /update-documentation Command
      ↓
Documentation Updater Agent Runs
      ↓
Commit with [skip-hook] Tag
```

## Case Study 2: Memory File Edit Capture Hook

### Architecture

The memory file edit capture hook demonstrates PostToolUse event handling for multiple tools:

#### Components

1. **Hook Configuration** (`memory-file-edit-capture.json`):
   - Defines PostToolUse events for Edit, Write, MultiEdit, Update tools
   - References separate script file
   - Category: memory
   - Required files list for installation

2. **Shell Script** (`memory-file-edit-capture.sh`):
   - Receives tool execution data via stdin
   - Filters for file edit tools (Edit, Write, MultiEdit, Update)
   - Extracts file path and creates meaningful summary
   - Calls backend API to save to project memory
   - Includes metadata (event_type, tool_name, file_path)

#### Key Features

**Multi-Tool Matching:**
```json
{
  "PostToolUse": [
    {"matcher": "Edit", "hooks": [...]},
    {"matcher": "Write", "hooks": [...]},
    {"matcher": "MultiEdit", "hooks": [...]},
    {"matcher": "Update", "hooks": [...]}
  ]
}
```

**Tool-Specific Summaries:**
```python
# Python extraction logic
if tool_name == 'Edit':
    summary = f'Edited {file_path}: replaced "{old_str}..." with "{new_str}..."'
elif tool_name == 'Write':
    summary = f'Wrote file {file_path}: {content_preview}...'
elif tool_name == 'MultiEdit':
    summary = f'Multi-edited {file_path}: {len(edits)} changes'
elif tool_name == 'Update':
    summary = f'Updated {file_path}: replaced "{old_str}..." with "{new_str}..."'
```

**Memory API Call:**
```bash
PAYLOAD="{\"message_type\": \"assistant\", \"content\": \"$ESCAPED_CONTENT\", \"metadata\": {\"event_type\": \"file_edit\", \"tool_name\": \"$TOOL_NAME\", \"file_path\": \"$FILE_PATH\"}}"

curl -s -X POST "$BACKEND_URL/api/projects/$PROJECT_ID/memory/messages" \
    -H "Content-Type: application/json" \
    -d "$PAYLOAD"
```

#### Benefits

1. **Complete Edit History**: Track all file modifications
2. **Context for Future Sessions**: Understand what files changed and why
3. **Tool Coverage**: Captures all file edit operations
4. **Graceful Failure**: Continues if backend unavailable
5. **Structured Metadata**: Event type, tool, file path for querying

## Service Layer

### Hook File Service

`backend/app/services/hook_file_service.py` handles hook installation:

```python
class HookFileService:
    def copy_hook_to_project(self, project_path: str, hook: DefaultHook):
        """
        Copy hook configuration and optional script file to project

        Steps:
        1. Create .claude/hooks/ directory
        2. If script_file exists, copy and make executable
        3. Return hook_config for settings.json merge
        """
        if hook.script_file:
            src = f"framework-assets/claude-hooks/{hook.script_file}"
            dst = f"{project_path}/.claude/hooks/{hook.script_file}"
            shutil.copy(src, dst)
            os.chmod(dst, 0o755)
```

### Hook Service

`backend/app/services/hook_service.py` manages hook database operations:

```python
class HookService:
    def enable_hook_for_project(self, project_id: str, hook_id: int, hook_type: str):
        """
        Enable a hook for a project

        1. Get hook from database
        2. Call hook_file_service to copy files
        3. Create project_hooks entry
        4. Merge hook_config into .claude/settings.json
        """
```

## Migration System

### Migration 004: Add script_file Support

```sql
-- 004_add_script_file_to_hooks.sql
ALTER TABLE default_hooks ADD COLUMN script_file VARCHAR(100);
ALTER TABLE custom_hooks ADD COLUMN script_file VARCHAR(100);
```

**Migration Script** (`migrate_add_script_file_to_hooks.py`):

```python
def migrate():
    """
    1. Add script_file column to hooks tables
    2. Update existing hooks with script references
    3. Verify script files exist in framework-assets
    """
    conn = get_db_connection()

    # Add column (idempotent)
    try:
        conn.execute("ALTER TABLE default_hooks ADD COLUMN script_file VARCHAR(100)")
    except sqlite3.OperationalError:
        pass  # Column already exists

    # Update post-merge hook
    conn.execute("""
        UPDATE default_hooks
        SET script_file = 'post-push-docs.sh'
        WHERE name = 'Post-Merge Documentation Update'
    """)

    conn.commit()
```

## Best Practices

### 1. Idempotent Migrations

Always check if changes already exist:

```python
try:
    conn.execute("ALTER TABLE ...")
except sqlite3.OperationalError as e:
    if "duplicate column name" in str(e):
        pass  # Already migrated
    else:
        raise
```

### 2. Script File Permissions

Always make hook scripts executable:

```python
import os
os.chmod(script_path, 0o755)
```

### 3. Error Handling

Provide fallback mechanisms:

```bash
if [ $API_STATUS -ne 0 ]; then
    # Create marker file for manual recovery
    echo "$(date)" > "$LOGDIR/.docs-update-pending"
fi
```

### 4. Logging

Comprehensive logging for debugging:

```bash
LOGFILE="$LOGDIR/post-merge-doc-$(date +%Y%m%d).log"
echo "[$(date)] Hook triggered" >> "$LOGFILE"
```

### 5. Recursion Prevention

Use lock files to prevent infinite loops:

```bash
LOCKFILE="$LOGDIR/.hook-running"
if [ -f "$LOCKFILE" ]; then
    exit 0
fi
touch "$LOCKFILE"
# ... work ...
rm -f "$LOCKFILE"
```

## Security Considerations

1. **Validate Input**: Always parse and validate hook input
2. **Sanitize Commands**: Avoid arbitrary command execution
3. **Check Permissions**: Verify file permissions before execution
4. **Audit Trail**: Log all hook executions
5. **Fail Safe**: Graceful failure without breaking workflow

## Troubleshooting

### Hook Not Triggering

1. Check `.claude/settings.json` for hook configuration
2. Verify script file exists and is executable
3. Check hook logs in `.claude/logs/hooks/`
4. Test hook manually: `echo '{}' | .claude/hooks/script.sh`

### Recursion Issues

1. Check for lock file: `.claude/logs/hooks/.hook-running`
2. Delete lock file if stuck: `rm .claude/logs/hooks/.hook-running`
3. Add `[skip-hook]` to commit title to bypass

### API Connection Failures

1. Verify backend is running: `curl http://localhost:3333/health`
2. Check network connectivity
3. Review API logs for errors
4. Check for marker file: `.claude/logs/hooks/.docs-update-pending`

### Path Encoding Issues

1. Test URL encoding: `printf %s "/path/with spaces" | jq -sRr @uri`
2. Verify encoded path in hook logs
3. Check API receives correct path

## Future Enhancements

1. **Hook Versioning**: Track hook versions and migrations
2. **Hook Dependencies**: Automatic dependency installation
3. **Hook Templates**: Pre-configured hooks for common scenarios
4. **Hook Analytics**: Track hook execution statistics
5. **Hook Debugging**: Interactive hook testing tool
