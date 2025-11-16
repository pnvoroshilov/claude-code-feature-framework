# Database Migrations

This directory contains database migration scripts for ClaudeTask.

## Migration History

### 001: Initial Schema
- Created initial database tables for projects, tasks, task history

### 002: Add Skills and Subagents Tables
- Added support for skills and subagents management
- Tables: default_skills, custom_skills, project_skills, default_subagents, custom_subagents, project_subagents

### 003: Add Hooks Tables
- Added support for Claude Code hooks management
- Tables: default_hooks, custom_hooks, project_hooks
- Loads default hooks from framework-assets/claude-hooks/*.json

### 004: Add script_file to Hooks Tables ✨ NEW
- Added script_file column to default_hooks and custom_hooks
- Enables hooks to reference separate shell script files
- Example: post-merge-documentation.json references post-push-docs.sh

## Running Migrations

### For Fresh Database (All Migrations)
```bash
# Run from project root
python claudetask/backend/migrations/migrate_add_hooks_tables.py
```

### For Existing Database (004 Only)
```bash
# Add script_file column to existing hooks tables
python claudetask/backend/migrations/migrate_add_script_file_to_hooks.py

# Update Post-Merge Documentation hook with script_file reference
python claudetask/backend/migrations/update_post_merge_hook.py
```

## Hook Script File Workflow

### 1. Framework Storage
```
framework-assets/claude-hooks/
├── post-merge-documentation.json  # Hook configuration
└── post-push-docs.sh              # Separate shell script
```

### 2. Database Storage
```sql
INSERT INTO default_hooks (
    name,
    file_name,           -- post-merge-documentation.json
    script_file,         -- post-push-docs.sh ⬅️ NEW
    hook_config,
    ...
)
```

### 3. Project Copy (On Hook Enable)
```
project/.claude/hooks/
└── post-push-docs.sh  # Copied from framework, chmod +x
```

### 4. Settings Reference
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

## Creating Hooks with Script Files

### JSON Configuration (framework-assets/claude-hooks/my-hook.json)
```json
{
  "name": "My Custom Hook",
  "description": "Description here",
  "category": "version-control",
  "script_file": "my-hook.sh",  ⬅️ Reference to separate script
  "hook_config": {
    "PostToolUse": [{
      "matcher": "Bash",
      "hooks": [{
        "type": "command",
        "command": ".claude/hooks/my-hook.sh"
      }]
    }]
  },
  "setup_instructions": "...",
  "dependencies": ["jq", "git"]
}
```

### Shell Script (framework-assets/claude-hooks/my-hook.sh)
```bash
#!/bin/bash
# Your hook implementation here
```

### Important Notes
- Script file is OPTIONAL - hooks can still use inline commands
- Script files are automatically made executable (chmod +x)
- Backend service copies script on hook enable
- Framework update syncs both JSON and script files

## Migration 004 Details

**What Changed:**
- Added `script_file VARCHAR(100)` to `default_hooks` table
- Added `script_file VARCHAR(100)` to `custom_hooks` table
- Updated Post-Merge Documentation hook to reference `post-push-docs.sh`

**Why:**
- Cleaner separation of hook config vs. implementation
- Easier to maintain complex hooks (e.g., hooks with URL encoding logic)
- Better code organization for multi-line shell scripts
- Proper file permissions (executable) for scripts

**Backward Compatible:**
- Existing hooks without script_file continue to work
- Column is nullable - not required for all hooks
- Inline commands in hook_config still supported

## Troubleshooting

### Migration Fails: "table default_hooks already exists"
✅ This is normal - migration is idempotent and skips if tables exist

### Migration Fails: "duplicate column name: script_file"
✅ This is normal - migration 004 skips if column already exists

### Hook doesn't copy script file
1. Check database: `SELECT script_file FROM default_hooks WHERE name = 'Hook Name';`
2. Check framework: Does `framework-assets/claude-hooks/SCRIPT_FILE.sh` exist?
3. Check logs: Backend service logs script copy operations

### Script file not executable
Backend service automatically runs `chmod +x` when copying scripts.
If manual copy: `chmod +x .claude/hooks/SCRIPT_FILE.sh`
