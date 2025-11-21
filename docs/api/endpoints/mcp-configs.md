# MCP Configs API Endpoints

## Overview

The MCP Configs API manages Model Context Protocol (MCP) server configurations. MCP configs enable Claude Code to interact with external tools and services. Configurations can be default framework configs or custom project-specific configs.

## Base URL

```
http://localhost:3333/api/projects/{project_id}/mcp-configs
```

## Endpoints

### GET `/api/projects/{project_id}/mcp-configs`

Get all MCP configs for a project (enabled, available defaults, and custom).

**Response:**
```json
{
  "enabled": [
    {
      "id": 1,
      "name": "filesystem",
      "description": "File system access for reading and writing files",
      "config_json": {
        "mcpServers": {
          "filesystem": {
            "command": "npx",
            "args": ["-y", "@modelcontextprotocol/server-filesystem", "/path/to/project"]
          }
        }
      },
      "is_custom": false,
      "enabled_at": "2025-11-21T10:00:00Z"
    }
  ],
  "available_default": [
    {
      "id": 2,
      "name": "github",
      "description": "GitHub API integration for repository operations",
      "config_json": {
        "mcpServers": {
          "github": {
            "command": "npx",
            "args": ["-y", "@modelcontextprotocol/server-github"],
            "env": {
              "GITHUB_TOKEN": "<insert-github-personal-access-token>"
            }
          }
        }
      },
      "is_custom": false
    }
  ],
  "custom": [
    {
      "id": 10,
      "name": "custom-api",
      "description": "Custom REST API integration",
      "config_json": {
        "mcpServers": {
          "custom-api": {
            "command": "node",
            "args": ["./custom-mcp-server.js"],
            "env": {
              "API_KEY": "secret"
            }
          }
        }
      },
      "is_custom": true,
      "created_at": "2025-11-21T09:00:00Z"
    }
  ]
}
```

### POST `/api/projects/{project_id}/mcp-configs/enable/{mcp_config_id}`

Enable an MCP config by writing it from database to project's `.mcp.json`.

**Query Parameters:**
- `mcp_config_type` (optional): `"default"` or `"custom"`, defaults to `"default"`

**Process:**
1. Checks if imported config exists in database (uses imported if available)
2. Otherwise uses default/custom MCP config from database
3. Writes MCP config from database to `.mcp.json`
4. Inserts record into `project_mcp_configs` junction table
5. Returns enabled MCP config details

**Note:** Database is the source of truth; `.mcp.json` is the output file.

**Request:**
```http
POST /api/projects/my-project/mcp-configs/enable/1?mcp_config_type=default
```

**Response:**
```json
{
  "id": 1,
  "name": "filesystem",
  "description": "File system access for reading and writing files",
  "config_json": {
    "mcpServers": {
      "filesystem": {
        "command": "npx",
        "args": ["-y", "@modelcontextprotocol/server-filesystem", "/path/to/project"]
      }
    }
  },
  "enabled_at": "2025-11-21T10:00:00Z"
}
```

**Error Responses:**
- `400` - MCP config already enabled or invalid type
- `404` - MCP config not found
- `500` - File system error

### POST `/api/projects/{project_id}/mcp-configs/disable/{mcp_config_id}`

Disable an MCP config by removing it from project's `.mcp.json`.

**Process:**
1. Removes record from `project_mcp_configs` junction table
2. Removes MCP config from `.mcp.json` file
3. Keeps record in database (doesn't delete custom configs)

**Request:**
```http
POST /api/projects/my-project/mcp-configs/disable/1
```

**Response:**
```json
{
  "success": true,
  "message": "MCP config disabled successfully"
}
```

**Error Responses:**
- `404` - MCP config not found or not enabled
- `500` - File system or database error

### POST `/api/projects/{project_id}/mcp-configs/enable-all`

Enable all available MCP configs (both default and custom) for a project.

**Process:**
1. Gets all available default MCP configs
2. Gets all custom MCP configs
3. Enables each config that isn't already enabled
4. Returns count of newly enabled configs

**Request:**
```http
POST /api/projects/my-project/mcp-configs/enable-all
```

**Response:**
```json
{
  "success": true,
  "enabled_count": 5,
  "errors": []
}
```

**Response with Errors:**
```json
{
  "success": true,
  "enabled_count": 3,
  "errors": [
    "Failed to enable github: Missing GITHUB_TOKEN environment variable",
    "Failed to enable custom-api: Invalid JSON configuration"
  ]
}
```

**Status Codes:**
- `200 OK` - Operation completed (check enabled_count and errors)
- `500 Internal Server Error` - Operation failed completely

### POST `/api/projects/{project_id}/mcp-configs/disable-all`

Disable all currently enabled MCP configs for a project.

**Process:**
1. Gets all enabled MCP configs
2. Disables each enabled config
3. Returns count of disabled configs

**Request:**
```http
POST /api/projects/my-project/mcp-configs/disable-all
```

**Response:**
```json
{
  "success": true,
  "disabled_count": 5,
  "errors": []
}
```

**Response with Errors:**
```json
{
  "success": true,
  "disabled_count": 4,
  "errors": [
    "Failed to disable filesystem: .mcp.json is locked by another process"
  ]
}
```

**Status Codes:**
- `200 OK` - Operation completed (check disabled_count and errors)
- `500 Internal Server Error` - Operation failed completely

### POST `/api/projects/{project_id}/mcp-configs`

Create a custom MCP config.

**Request Body:**
```json
{
  "name": "custom-api",
  "description": "Custom REST API integration",
  "config_json": {
    "mcpServers": {
      "custom-api": {
        "command": "node",
        "args": ["./custom-mcp-server.js"],
        "env": {
          "API_KEY": "secret"
        }
      }
    }
  }
}
```

**Process:**
1. Validates MCP config JSON structure
2. Inserts record into `custom_mcp_configs` table
3. Returns created config

**Response:**
```json
{
  "id": 10,
  "name": "custom-api",
  "description": "Custom REST API integration",
  "config_json": {
    "mcpServers": {
      "custom-api": {
        "command": "node",
        "args": ["./custom-mcp-server.js"],
        "env": {
          "API_KEY": "secret"
        }
      }
    }
  },
  "is_custom": true,
  "created_at": "2025-11-21T10:00:00Z"
}
```

**Error Responses:**
- `400` - Invalid JSON or duplicate name
- `500` - Database error

### PUT `/api/projects/{project_id}/mcp-configs/{mcp_config_id}`

Update a custom MCP config.

**Request Body:**
```json
{
  "name": "custom-api-updated",
  "description": "Updated description",
  "config_json": {
    "mcpServers": {
      "custom-api-updated": {
        "command": "node",
        "args": ["./updated-server.js"]
      }
    }
  }
}
```

**Process:**
1. Validates config is custom (cannot update default configs)
2. Updates record in `custom_mcp_configs` table
3. If enabled, updates `.mcp.json` as well

**Response:**
```json
{
  "id": 10,
  "name": "custom-api-updated",
  "description": "Updated description",
  "config_json": {
    "mcpServers": {
      "custom-api-updated": {
        "command": "node",
        "args": ["./updated-server.js"]
      }
    }
  },
  "updated_at": "2025-11-21T10:05:00Z"
}
```

**Error Responses:**
- `400` - Invalid JSON or cannot update default config
- `404` - MCP config not found
- `500` - Database or file system error

### DELETE `/api/projects/{project_id}/mcp-configs/{mcp_config_id}`

Delete a custom MCP config.

**Process:**
1. Verifies config is custom (cannot delete default configs)
2. Disables config if enabled (removes from `.mcp.json`)
3. Deletes record from `custom_mcp_configs` table

**Request:**
```http
DELETE /api/projects/my-project/mcp-configs/10
```

**Response:**
```json
{
  "success": true,
  "message": "Custom MCP config deleted successfully"
}
```

**Error Responses:**
- `400` - Cannot delete default config
- `404` - MCP config not found
- `500` - Database or file system error

### POST `/api/projects/{project_id}/mcp-configs/import`

Import MCP configs from existing `.mcp.json` file.

**Process:**
1. Reads project's `.mcp.json` file
2. Parses JSON and extracts MCP server configurations
3. Creates records in `imported_mcp_configs` table
4. Marks configs as enabled in `project_mcp_configs`

**Request:**
```http
POST /api/projects/my-project/mcp-configs/import
```

**Response:**
```json
{
  "success": true,
  "imported_count": 3,
  "configs": [
    {
      "id": 20,
      "name": "filesystem",
      "description": "Imported from .mcp.json"
    },
    {
      "id": 21,
      "name": "github",
      "description": "Imported from .mcp.json"
    },
    {
      "id": 22,
      "name": "custom-server",
      "description": "Imported from .mcp.json"
    }
  ]
}
```

**Error Responses:**
- `404` - .mcp.json not found
- `400` - Invalid JSON format
- `500` - Database or file system error

## MCP Config Structure

### Standard MCP Config JSON Format

```json
{
  "mcpServers": {
    "server-name": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-package"],
      "env": {
        "ENV_VAR": "value"
      }
    }
  }
}
```

### Common MCP Servers

#### Filesystem Server
```json
{
  "mcpServers": {
    "filesystem": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "/path/to/project"]
    }
  }
}
```

#### GitHub Server
```json
{
  "mcpServers": {
    "github": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": {
        "GITHUB_TOKEN": "<github-token>"
      }
    }
  }
}
```

#### PostgreSQL Server
```json
{
  "mcpServers": {
    "postgres": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-postgres", "postgresql://localhost/mydb"]
    }
  }
}
```

#### Custom Server
```json
{
  "mcpServers": {
    "custom": {
      "command": "node",
      "args": ["./path/to/custom-server.js"],
      "env": {
        "API_KEY": "secret",
        "API_URL": "https://api.example.com"
      }
    }
  }
}
```

## MCP Config Storage

### Default Configs
- **Source:** Framework-defined MCP server configurations
- **Database:** `default_mcp_configs` table
- **Active (when enabled):** Written to `{project}/.mcp.json`

### Custom Configs
- **Database:** `custom_mcp_configs` table
- **Active (when enabled):** Written to `{project}/.mcp.json`

### Imported Configs
- **Source:** Existing `{project}/.mcp.json` file
- **Database:** `imported_mcp_configs` table
- **Priority:** Imported configs take precedence over defaults

## MCP Config Lifecycle

```
[Create Custom Config]
        ↓
    Insert into custom_mcp_configs
        ↓
[Enable Config]
        ↓
    Write to .mcp.json
        ↓
    Insert into project_mcp_configs
        ↓
    Claude Code can use MCP tools
        ↓
[Disable Config]
        ↓
    Remove from .mcp.json
        ↓
    Remove from project_mcp_configs
```

## Error Handling

All endpoints return standard error responses:

```json
{
  "detail": "Error message describing what went wrong"
}
```

**Common HTTP Status Codes:**
- `200` - Success
- `400` - Bad request (validation error)
- `404` - Resource not found
- `500` - Internal server error

## Usage Examples

### Enable a default MCP config
```bash
curl -X POST "http://localhost:3333/api/projects/my-project/mcp-configs/enable/1?mcp_config_type=default"
```

### Enable a custom MCP config
```bash
curl -X POST "http://localhost:3333/api/projects/my-project/mcp-configs/enable/10?mcp_config_type=custom"
```

### Create a custom MCP config
```bash
curl -X POST "http://localhost:3333/api/projects/my-project/mcp-configs" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "custom-api",
    "description": "Custom REST API integration",
    "config_json": {
      "mcpServers": {
        "custom-api": {
          "command": "node",
          "args": ["./custom-server.js"],
          "env": {
            "API_KEY": "secret"
          }
        }
      }
    }
  }'
```

### Enable all MCP configs
```bash
curl -X POST "http://localhost:3333/api/projects/my-project/mcp-configs/enable-all"
```

### Disable all MCP configs
```bash
curl -X POST "http://localhost:3333/api/projects/my-project/mcp-configs/disable-all"
```

### Import existing .mcp.json
```bash
curl -X POST "http://localhost:3333/api/projects/my-project/mcp-configs/import"
```

### Update custom MCP config
```bash
curl -X PUT "http://localhost:3333/api/projects/my-project/mcp-configs/10" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "custom-api-v2",
    "description": "Updated API integration",
    "config_json": {
      "mcpServers": {
        "custom-api-v2": {
          "command": "node",
          "args": ["./v2-server.js"]
        }
      }
    }
  }'
```

## Integration with Claude Code

MCP configs enable Claude Code to:
- Access file systems
- Interact with databases
- Make API calls
- Execute custom tools
- Integrate with external services

**Usage in Claude Code:**
1. Enable MCP configs for project
2. Configs are written to `.mcp.json`
3. Claude Code CLI reads `.mcp.json` on startup
4. MCP tools become available to Claude
5. Claude can use tools in conversations

**Example MCP Tool Usage:**
```
Claude: I'll use the filesystem tool to read the config file.
[Uses @modelcontextprotocol/server-filesystem]

Claude: Let me check your GitHub repository.
[Uses @modelcontextprotocol/server-github]
```

## Security Considerations

**Environment Variables:**
- Store sensitive data (API keys, tokens) in environment variables
- Never commit `.mcp.json` with secrets to version control
- Use `.env` files and reference in MCP config:
  ```json
  {
    "env": {
      "API_KEY": "${API_KEY}"
    }
  }
  ```

**Command Execution:**
- MCP servers execute arbitrary commands
- Only enable trusted MCP configs
- Validate custom MCP configs before enabling
- Review command and args before activation

**File Access:**
- Filesystem MCP servers have access to specified directories
- Use least-privilege principle (limit access scope)
- Never grant root or home directory access

## Troubleshooting

**MCP Config Not Working:**
1. Check `.mcp.json` syntax is valid JSON
2. Verify MCP server package is installed
3. Check environment variables are set
4. Review Claude Code logs for MCP errors
5. Test MCP server independently

**Import Failed:**
1. Ensure `.mcp.json` exists in project root
2. Validate JSON syntax
3. Check file permissions
4. Review error message for specifics

**Enable Failed:**
1. Check if config already enabled
2. Verify `.mcp.json` is writable
3. Ensure no conflicting server names
4. Review database constraints
