# MCP Configuration Normalization Fix

## Problem Description

When adding MCP servers from mcp.so search, configurations sometimes arrive with an incorrect double-wrapped structure that causes errors.

### Incorrect Format (Double-Wrapped)
```json
{
  "mcpServers": {
    "context7": {
      "command": "bunx",
      "args": [
        "-y",
        "@upstash/context7-mcp",
        "--api-key",
        "ctx7sk-7fe85543-cda6-4afe-8f6b-976ef346269b"
      ]
    }
  }
}
```

### Correct Format (Expected)
```json
{
  "command": "bunx",
  "args": [
    "-y",
    "@upstash/context7-mcp",
    "--api-key",
    "ctx7sk-7fe85543-cda6-4afe-8f6b-976ef346269b"
  ]
}
```

## Root Cause

The issue occurred because:
1. mcp.so sometimes returns configuration with outer `mcpServers` wrapper
2. Our system expects only the inner server configuration
3. No normalization was performed before saving/validating configs

This resulted in errors when trying to use the configuration, as Claude Code expects the inner format only.

## Solution Implemented

### 1. Added Normalization Function

Created `_normalize_mcp_config()` method in both:
- `MCPSearchService` (claudetask/backend/app/services/mcp_search_service.py)
- `MCPConfigService` (claudetask/backend/app/services/mcp_config_service.py)

**Function Logic:**
```python
def _normalize_mcp_config(self, config_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Normalize MCP config by removing double-wrapped mcpServers structure

    Handles two cases:
    1. Correct format: {"command": "...", "args": [...]}
    2. Double-wrapped format: {"mcpServers": {"server_name": {...}}}

    Returns: Normalized config with only the inner server configuration
    """
    if not config_data:
        return config_data

    # Check if config has outer mcpServers wrapper
    if "mcpServers" in config_data:
        # Extract the first server config from mcpServers
        mcp_servers = config_data["mcpServers"]
        if isinstance(mcp_servers, dict) and len(mcp_servers) > 0:
            first_server_key = next(iter(mcp_servers))
            return mcp_servers[first_server_key]

    # Config is already in correct format
    return config_data
```

### 2. Integration Points

#### MCPSearchService.get_server_config()
```python
# Normalize config before returning
normalized_config = self._normalize_mcp_config(config) if config else None

return {
    "description": description,
    "config": normalized_config,  # Uses normalized config
    "github_url": github_url,
    "avatar_url": avatar_url
}
```

#### MCPConfigService.create_custom_mcp_config()
```python
# Normalize config before validation
normalized_config = self._normalize_mcp_config(config_create.config)

# Validate normalized config
if not self.file_service.validate_mcp_config_json(normalized_config):
    raise ValueError(f"Invalid MCP config JSON")

# Save normalized config to database
custom_mcp_config = CustomMCPConfig(
    # ...
    config=normalized_config,  # Uses normalized config
    # ...
)
```

## Testing

Created comprehensive unit tests to verify normalization:

### Test Cases
1. **Correct format unchanged**: Verifies that properly formatted configs are not modified
2. **Double-wrapped normalized**: Verifies that double-wrapped configs are properly unwrapped
3. **Empty configs handled**: Verifies that None and empty dicts are handled safely
4. **Multiple servers**: Verifies that first server is extracted when multiple servers present

### Test Results
```
✅ Test 1 passed: Correct format unchanged
✅ Test 2 passed: Double-wrapped format normalized correctly
✅ Test 3 passed: Empty configs handled correctly
✅ Test 4 passed: First server extracted from multiple servers

🎉 All tests passed!
```

## Benefits

1. **Automatic Correction**: Configs from mcp.so are automatically normalized
2. **User-Friendly**: Users don't need to manually fix configs
3. **Backwards Compatible**: Correctly formatted configs remain unchanged
4. **Consistent Format**: All configs are stored in consistent format in database
5. **Error Prevention**: Prevents validation and execution errors from malformed configs

## Files Modified

1. **claudetask/backend/app/services/mcp_search_service.py**
   - Added `_normalize_mcp_config()` method (lines 15-42)
   - Updated `get_server_config()` to use normalization (lines 332-333)

2. **claudetask/backend/app/services/mcp_config_service.py**
   - Added `_normalize_mcp_config()` method (lines 521-551)
   - Updated `create_custom_mcp_config()` to normalize before validation (lines 387-392)
   - Updated config storage to use normalized config (line 413)

## Usage

### For Users
No changes required! The normalization happens automatically when:
- Importing MCP configs from mcp.so
- Creating custom MCP configs manually
- Enabling/disabling MCP configs

### For Developers
If adding new MCP config handling code, use the normalization helper:

```python
# In MCPSearchService or MCPConfigService
normalized = self._normalize_mcp_config(raw_config)
# Now normalized contains correctly formatted config
```

## Future Improvements

1. **Validation Enhancement**: Add more comprehensive config validation
2. **Error Messages**: Provide clearer error messages about config format issues
3. **Migration Script**: Create script to normalize existing configs in database
4. **Documentation**: Update user docs about MCP config format requirements

## Related Issues

This fix resolves the issue where:
- Context7 MCP showed as "Enabled" but couldn't be disabled
- Error: "MCP config not enabled for project" when trying to manage configs
- Conflicts between global and project-level MCP configurations

## Version

**Fix Version**: 2024-01-12
**Framework Version**: Claude Code Feature Framework v1.x
**Backend Version**: FastAPI Backend v1.x
