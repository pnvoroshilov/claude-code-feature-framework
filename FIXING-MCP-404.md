# Fixing MCP 404 Errors

## Problem

You see this error in Claude terminal sessions:

```
❌ Failed to get project settings: Client error '404 Not Found' for url
   'http://localhost:3333/api/projects/ff9cc152-3f38-49ab-bec0-0e7cbf8459a'
```

## Root Cause

The framework was using a hardcoded default project ID (`ff9cc152-3f38-49ab-bec0-0e7cbf84594a`) for ALL projects instead of each project's actual ID from the database.

## Solution (Automatic)

The framework now **uses the correct project ID** for each project:

1. **Framework updates**: Writes current project's actual ID to `.mcp.json`
2. **MCP enable/disable**: Uses current project's ID, not hardcoded default
3. **Database configs**: Updated to use correct IDs per project

### Quick Fix

Run **framework update** for your project in the UI, or manually update with:

```bash
./scripts/update-mcp-config.sh
```

### Verification

Check your project's `.mcp.json` file:

```bash
cat /path/to/project/.mcp.json | grep CLAUDETASK_PROJECT_ID
```

Should show YOUR project's actual ID, not `ff9cc152-3f38-49ab-bec0-0e7cbf84594a`

## Manual Update (if needed)

If you need to manually update the database configuration:

```bash
# Run the update script
./scripts/update-mcp-config.sh

# Then restart Claude Code
```

## What Changed?

Before:
- Template had hardcoded default `CLAUDETASK_PROJECT_ID`
- Every project used the same (wrong) ID
- Framework updates wrote this hardcoded ID to all projects
- MCP enable/disable also used hardcoded default

After:
- Template has no hardcoded ID
- Framework updates write CURRENT project's actual ID
- MCP enable/disable uses current project's actual ID
- Each project gets its own correct ID from database
- Auto-detection fallback available if ID is missing

## Technical Details

See [docs/mcp-project-id-auto-detection.md](docs/mcp-project-id-auto-detection.md) for implementation details.

## Still Not Working?

1. **Check backend is running:**
   ```bash
   curl http://localhost:3333/api/projects
   ```

2. **Verify project exists:**
   ```bash
   sqlite3 claudetask/backend/data/claudetask.db \
     "SELECT id, name, path FROM projects WHERE name LIKE '%YourProject%';"
   ```

3. **Check project path matches:**
   - Project path in database must match absolute path of your project
   - Run `pwd` in your project directory to get absolute path

4. **Enable debug logging:**
   - Check Claude Code terminal output for MCP server logs
   - Look for "Auto-detected project ID" or error messages
