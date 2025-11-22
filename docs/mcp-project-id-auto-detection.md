# MCP Server Project ID Auto-Detection

## Problem

Previously, the ClaudeTask MCP server required a hardcoded `CLAUDETASK_PROJECT_ID` in the environment configuration. This caused issues when:
- Project IDs changed in the database
- Multiple projects used the same MCP configuration
- Projects were moved or recreated

Example error:
```
❌ Failed to get project settings: Client error '404 Not Found' for url
   'http://localhost:3333/api/projects/ff9cc152-3f38-49ab-bec0-0e7cbf8459a'
```

## Solution

The MCP server now **automatically detects the project ID** by querying the backend API with the project path.

### How It Works

1. MCP server starts with `CLAUDETASK_PROJECT_PATH` environment variable
2. Server queries backend API: `GET /api/projects`
3. Matches project by absolute path
4. Uses detected project ID for all API calls

### Implementation

File: `claudetask/mcp_server/native_stdio_server.py`

```python
async def get_project_id_by_path(project_path: str, backend_url: str) -> str | None:
    """Get project ID by querying backend API with project path."""
    abs_path = str(Path(project_path).resolve())

    async with httpx.AsyncClient(timeout=5.0) as client:
        response = await client.get(f"{backend_url}/api/projects")
        if response.status_code == 200:
            projects = response.json()
            for project in projects:
                if project.get("path") == abs_path:
                    return project["id"]

    return None
```

### Configuration

**Old Configuration** (hardcoded ID):
```json
{
  "env": {
    "CLAUDETASK_PROJECT_ID": "ff9cc152-3f38-49ab-bec0-0e7cbf8459a",
    "CLAUDETASK_PROJECT_PATH": ".",
    "CLAUDETASK_BACKEND_URL": "http://localhost:3333"
  }
}
```

**New Configuration** (auto-detect):
```json
{
  "env": {
    "CLAUDETASK_PROJECT_PATH": ".",
    "CLAUDETASK_BACKEND_URL": "http://localhost:3333"
  }
}
```

### Benefits

✅ **No more 404 errors** - Project ID is always correct
✅ **Project portability** - Same config works for any project
✅ **Database resilience** - Survives project recreation/migration
✅ **Backward compatible** - Still accepts explicit `CLAUDETASK_PROJECT_ID` if needed

### Fallback Behavior

If auto-detection fails:
1. Uses explicitly provided `CLAUDETASK_PROJECT_ID` (if set)
2. Uses default from environment variable
3. Logs warning and continues with configured value

### Migration

For existing projects, update the MCP configuration:

1. **Database Update:**
   ```sql
   UPDATE default_mcp_configs
   SET config = json_remove(config, '$.env.CLAUDETASK_PROJECT_ID')
   WHERE name = 'claudetask';
   ```

2. **Restart Claude Code** to reload MCP configuration

3. **Verify** auto-detection in MCP server logs:
   ```
   Auto-detected project ID: c2f3e0e2-f7cb-43d1-a5a4-f491662b801d
   ```

### Troubleshooting

**Issue:** Auto-detection not working

**Checks:**
1. Backend is running: `curl http://localhost:3333/api/projects`
2. Project exists in database with correct path
3. Check MCP server logs in stderr for detection errors

**Override:** Set explicit ID if needed:
```bash
export CLAUDETASK_PROJECT_ID="your-project-id"
```

## Related Files

- `claudetask/mcp_server/native_stdio_server.py` - Auto-detection logic
- `framework-assets/mcp-configs/.mcp.json` - Default MCP configuration
- Database: `default_mcp_configs` table - Stored MCP configurations
