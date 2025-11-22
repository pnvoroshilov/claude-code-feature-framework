# Fixing MCP 404 Errors

## Problem

You see this error in Claude terminal sessions:

```
❌ Failed to get project settings: Client error '404 Not Found' for url
   'http://localhost:3333/api/projects/ff9cc152-3f38-49ab-bec0-0e7cbf8459a'
```

## Root Cause

The MCP server was using a hardcoded project ID that doesn't match your actual project ID in the database.

## Solution (Automatic)

The framework now **auto-detects** the correct project ID by querying the backend API with your project path.

### Quick Fix

**Simply restart Claude Code** - the new auto-detection will work automatically!

### Verification

After restarting, check the terminal logs for:

```
Auto-detected project ID: c2f3e0e2-f7cb-43d1-a5a4-f491662b801d
Starting ClaudeTask MCP STDIO server for project c2f3e0e2-f7cb-43d1-a5a4-f491662b801d
```

## Manual Update (if needed)

If you need to manually update the database configuration:

```bash
# Run the update script
./scripts/update-mcp-config.sh

# Then restart Claude Code
```

## What Changed?

Before:
- MCP config had hardcoded `CLAUDETASK_PROJECT_ID`
- Every project used the same (wrong) ID
- Changing project IDs broke MCP functionality
- Framework updates re-wrote hardcoded ID back into config

After:
- MCP server queries backend API to find project by path
- Correct project ID is automatically detected
- Works for all projects without hardcoding
- Framework updates no longer inject hardcoded ID
- MCP enable/disable preserves auto-detection

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
