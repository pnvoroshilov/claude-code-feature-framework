# MCPConfigs Component

React component for managing Model Context Protocol (MCP) server configurations that enable Claude Code to interact with external tools and services.

## Location

`claudetask/frontend/src/pages/MCPConfigs.tsx`

## Purpose

Provides a comprehensive interface for:
- Browsing and enabling default framework MCP configs
- Creating custom project-specific MCP configs
- Managing MCP server configurations (command, args, env)
- Searching MCP servers from GitHub registry
- Importing existing `.mcp.json` configurations
- Viewing MCP config JSON structures
- Toggling MCP config activation per project

## Features

### 1. MCP Config Categories

**Default Categories:**
- **Filesystem** - File system access and operations
- **Database** - PostgreSQL, SQLite, MySQL integrations
- **API** - REST API and web service integrations
- **Cloud** - AWS, Azure, Google Cloud services
- **Development** - Git, GitHub, build tools
- **AI/ML** - Machine learning and AI services
- **Custom** - User-defined MCP servers

### 2. Filter and Search

**Filter Options:**
- **All**: Show all MCP configs (default + custom + enabled)
- **Default**: Framework-provided MCP configs only
- **Custom**: User-created project-specific MCP configs
- **Favorite**: Starred MCP configs for quick access
- **Enabled**: Currently active MCP configs only

**Search:**
- Real-time search across MCP config names and descriptions
- Case-insensitive matching
- Filters displayed configs dynamically

### 3. MCP Config Display Cards

**Visual Design:**
- Material-UI Card components with professional layout
- Category badges with color coding
- Favorite star icon (toggle on/off)
- Enable/disable switch
- Quick action buttons (View JSON, Edit, Delete)

**Card Information:**
- MCP config name and description
- Category and config type (default/custom)
- Command and arguments preview
- Environment variables count
- Creator information (for custom configs)
- Enable/disable toggle switch

### 4. MCP Config Management Actions

#### Enable/Disable MCP Config
```tsx
const handleEnableConfig = async (
  configId: number,
  configType: 'default' | 'custom'
) => {
  await axios.post(
    `/api/projects/${projectId}/mcp-configs/enable/${configId}?mcp_config_type=${configType}`
  );
};

const handleDisableConfig = async (configId: number) => {
  await axios.post(`/api/projects/${projectId}/mcp-configs/disable/${configId}`);
};
```

#### Mark as Favorite
```tsx
const handleToggleFavorite = async (
  configId: number,
  configType: 'default' | 'custom',
  currentState: boolean
) => {
  const endpoint = currentState ? 'unfavorite' : 'favorite';
  await axios.post(
    `/api/projects/${projectId}/mcp-configs/${endpoint}/${configId}?mcp_config_type=${configType}`
  );
};
```

#### Import from .mcp.json
```tsx
const handleImportConfigs = async () => {
  await axios.post(`/api/projects/${projectId}/mcp-configs/import`);
};
```

### 5. Create Custom MCP Config Dialog

**Form Fields:**
- **Name**: MCP server identifier (required)
  - Auto-sanitized: lowercase, hyphens replace spaces
  - Example: "Custom API" → "custom-api"
- **Description**: MCP server purpose and capabilities (required)
- **Category**: Config category (custom, api, database, etc.)
- **JSON Configuration**: MCP server definition (required)

**MCP Config JSON Structure:**
```json
{
  "command": "npx",
  "args": ["-y", "@modelcontextprotocol/server-filesystem", "/path/to/project"],
  "env": {
    "API_KEY": "secret"
  }
}
```

**Config Creation Process:**
1. User enters name, description, and JSON config
2. Frontend validates JSON syntax
3. Backend creates MCP config in database
4. Config can be enabled to write to `.mcp.json`
5. Claude Code reads `.mcp.json` on startup

**Example Creation Request:**
```json
{
  "name": "custom-api",
  "description": "Custom REST API integration",
  "category": "api",
  "config": {
    "command": "node",
    "args": ["./custom-mcp-server.js"],
    "env": {
      "API_KEY": "secret",
      "API_URL": "https://api.example.com"
    }
  }
}
```

### 6. MCP Server Search (GitHub Registry)

**Features:**
- Search MCP servers from GitHub `@modelcontextprotocol` organization
- Browse official MCP server packages
- View server documentation and capabilities
- Install servers directly from search results
- Add to project with default configuration

**Search Flow:**
1. User enters search query
2. Frontend queries MCP search API
3. Results display with package info
4. User can view details or add server
5. Config created automatically with defaults

**API Endpoint:**
```
GET /api/mcp-search?query=filesystem&page=1&per_page=10
```

### 7. View MCP Config JSON Dialog

**Features:**
- Full JSON configuration display
- Syntax highlighting for JSON
- Read-only view with copy functionality
- Environment variables display
- Command and arguments breakdown

**JSON Structure Example:**
```json
{
  "mcpServers": {
    "filesystem": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "/project/path"],
      "env": {
        "ENV_VAR": "value"
      }
    }
  }
}
```

### 8. Edit Custom MCP Config

**Editable Fields:**
- Description
- Category
- JSON configuration (command, args, env)

**Cannot Edit:**
- Config name (immutable identifier)
- Default configs (only custom configs)

**Editor Features:**
- JSON syntax validation
- Error highlighting
- Auto-formatting
- Save updates to database and `.mcp.json` if enabled

### 9. Bulk Operations

#### Enable All Configs
```tsx
const handleEnableAll = async () => {
  await axios.post(`/api/projects/${projectId}/mcp-configs/enable-all`);
};
```

#### Disable All Configs
```tsx
const handleDisableAll = async () => {
  await axios.post(`/api/projects/${projectId}/mcp-configs/disable-all`);
};
```

## Props

This is a page component and doesn't accept props. It uses:
- `ProjectContext` for current project selection
- Internal state management for MCP config data

## State Management

```tsx
const [activeFilter, setActiveFilter] = useState<FilterType>('all');
const [filterQuery, setFilterQuery] = useState('');
const [configs, setConfigs] = useState<MCPConfigsResponse>({
  enabled: [],
  available_default: [],
  custom: [],
  favorites: [],
});
const [loading, setLoading] = useState(true);
const [error, setError] = useState<string | null>(null);
const [selectedConfig, setSelectedConfig] = useState<MCPConfig | null>(null);
const [createDialogOpen, setCreateDialogOpen] = useState(false);
const [viewConfigDialogOpen, setViewConfigDialogOpen] = useState(false);
const [searchDialogOpen, setSearchDialogOpen] = useState(false);
```

## API Integration

### Endpoints Used

1. **GET /api/projects/{project_id}/mcp-configs/**
   - Fetches all MCP configs (enabled, default, custom, favorites)
   - Returns structured MCPConfigsResponse object

2. **POST /api/projects/{project_id}/mcp-configs/enable/{config_id}**
   - Enables an MCP config for the project
   - Writes config to `.mcp.json`
   - Query param: `mcp_config_type` (default or custom)

3. **POST /api/projects/{project_id}/mcp-configs/disable/{config_id}**
   - Disables an active MCP config
   - Removes config from `.mcp.json`

4. **POST /api/projects/{project_id}/mcp-configs/create**
   - Creates new custom MCP config
   - Request body: `{ name, description, category, config }`

5. **PUT /api/projects/{project_id}/mcp-configs/{config_id}**
   - Updates existing custom MCP config
   - Cannot edit default configs

6. **DELETE /api/projects/{project_id}/mcp-configs/{config_id}**
   - Deletes custom MCP config
   - Cannot delete default configs

7. **POST /api/projects/{project_id}/mcp-configs/import**
   - Imports MCP configs from existing `.mcp.json`
   - Creates records for each imported config

8. **POST /api/projects/{project_id}/mcp-configs/enable-all**
   - Enables all available MCP configs
   - Bulk operation

9. **POST /api/projects/{project_id}/mcp-configs/disable-all**
   - Disables all enabled MCP configs
   - Bulk operation

10. **GET /api/mcp-search**
    - Searches MCP servers from GitHub registry
    - Query params: `query`, `page`, `per_page`

## Default Framework MCP Configs

### Filesystem Server
```json
{
  "name": "filesystem",
  "command": "npx",
  "args": ["-y", "@modelcontextprotocol/server-filesystem", "/project/path"]
}
```

### GitHub Server
```json
{
  "name": "github",
  "command": "npx",
  "args": ["-y", "@modelcontextprotocol/server-github"],
  "env": {
    "GITHUB_TOKEN": "<token>"
  }
}
```

### PostgreSQL Server
```json
{
  "name": "postgres",
  "command": "npx",
  "args": ["-y", "@modelcontextprotocol/server-postgres", "postgresql://localhost/db"]
}
```

### SQLite Server
```json
{
  "name": "sqlite",
  "command": "npx",
  "args": ["-y", "@modelcontextprotocol/server-sqlite", "/path/to/database.db"]
}
```

## MCP Config File Structure

**Location:** `.mcp.json` in project root

**Database Source of Truth:** Database stores all configs; `.mcp.json` is generated output

**File Format:**
```json
{
  "mcpServers": {
    "server-name": {
      "command": "command-to-run",
      "args": ["arg1", "arg2"],
      "env": {
        "ENV_VAR": "value"
      }
    }
  }
}
```

**Example Complete `.mcp.json`:**
```json
{
  "mcpServers": {
    "filesystem": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "/project/path"]
    },
    "github": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": {
        "GITHUB_TOKEN": "ghp_xxxxxxxxxxxxx"
      }
    },
    "custom-api": {
      "command": "node",
      "args": ["./custom-server.js"],
      "env": {
        "API_KEY": "secret"
      }
    }
  }
}
```

## Common Use Cases

### 1. Enable Filesystem Access

**Use Case**: Allow Claude to read and write project files

**Steps:**
1. Find "filesystem" in default configs
2. Enable config
3. Verify `.mcp.json` includes filesystem server
4. Claude can now use filesystem tools

### 2. Add GitHub Integration

**Use Case**: Enable Claude to interact with GitHub repositories

**Steps:**
1. Find "github" in default configs
2. Enable config
3. Set `GITHUB_TOKEN` environment variable
4. Claude can use GitHub API tools

### 3. Create Custom API Integration

**Use Case**: Connect Claude to internal REST API

**Steps:**
1. Click "Create Custom MCP Config"
2. Name: "internal-api"
3. Description: "Company internal API integration"
4. JSON Config:
   ```json
   {
     "command": "node",
     "args": ["./mcp-servers/internal-api.js"],
     "env": {
       "API_KEY": "${INTERNAL_API_KEY}",
       "API_URL": "https://internal.company.com/api"
     }
   }
   ```
5. Save and enable
6. Claude can use internal API tools

### 4. Import Existing Configuration

**Use Case**: Project already has `.mcp.json`, import to database

**Steps:**
1. Click "Import from .mcp.json"
2. System reads existing `.mcp.json`
3. Creates database records for each server
4. All configs marked as enabled
5. Can now manage through UI

## UI Components

**Material-UI Components Used:**
- Card, CardContent, CardActionArea
- Button, IconButton, ToggleButton
- Dialog, DialogTitle, DialogContent, DialogActions
- TextField, Switch, Chip
- Grid, Stack, Container, Box
- CircularProgress, Alert
- Menu, MenuItem, List, ListItem

**Custom Styling:**
- Professional SaaS-style aesthetics
- Color-coded category badges
- Smooth hover effects and transitions
- Responsive grid layout
- Material theme integration

## Error Handling

**User-Facing Errors:**
- Failed to fetch MCP configs
- Failed to enable/disable config
- Failed to create custom config
- Invalid JSON configuration
- Config file not found
- Missing environment variables

**Error Display:**
- Alert banner at top of page
- Inline validation errors in dialogs
- Toast notifications for quick actions
- Detailed error messages in console

**JSON Validation:**
- Real-time syntax checking
- Error highlighting in editor
- Helpful error messages
- Prevents invalid config submission

## Performance Considerations

**Optimization Strategies:**
- Fetch configs only when project changes
- Debounced search input
- Memoized filtered config lists
- Lazy loading of JSON content
- Efficient state updates
- Virtualized lists for large config sets

## Accessibility

- Keyboard navigation support
- ARIA labels on interactive elements
- Screen reader-friendly descriptions
- Focus management in dialogs
- Color contrast compliance (WCAG AA)
- Semantic HTML structure

## Security Considerations

**Environment Variables:**
- Never display sensitive values in UI
- Mask API keys and tokens
- Use placeholder text for secrets
- Reference environment variables: `${VAR_NAME}`

**Command Execution:**
- Validate command and args
- Warn about custom commands
- Review configs before enabling
- Restrict command permissions

**File Access:**
- Validate file paths
- Prevent path traversal
- Restrict access to project scope
- Secure file permissions

## Integration with Claude Code

**MCP Config Flow:**
1. User creates/enables MCP config in UI
2. Backend writes config to `.mcp.json`
3. Claude Code CLI reads `.mcp.json` on startup
4. MCP tools become available to Claude
5. Claude uses tools in conversations

**Tool Usage Example:**
```
User: "Read the contents of README.md"
Claude: [Uses filesystem MCP server]
Claude: "Here's the content of README.md..."

User: "Check my GitHub repository status"
Claude: [Uses github MCP server]
Claude: "Your repository has 3 open pull requests..."
```

## Troubleshooting

**Config Not Working:**
1. Check `.mcp.json` syntax
2. Verify MCP server package installed
3. Check environment variables set
4. Review Claude Code logs
5. Test MCP server independently

**Import Failed:**
1. Ensure `.mcp.json` exists
2. Validate JSON syntax
3. Check file permissions
4. Review error message

**Enable Failed:**
1. Check if already enabled
2. Verify `.mcp.json` writable
3. Ensure no conflicting server names
4. Review database constraints

## Related Documentation

- [MCP Configs API](../api/endpoints/mcp-configs.md) - Backend API documentation
- [Claude Code MCP Integration](../architecture/mcp-integration.md) - MCP architecture
- [Skills Component](./Skills.md) - Related skills management UI
- [Hooks Component](./Hooks.md) - Related hooks management UI

---

**Last Updated**: 2025-11-21
**Component Version**: 2.0
**Status**: Active, Production Ready
