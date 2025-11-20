# Framework Update System

Complete guide to the ClaudeTask Framework update mechanism that synchronizes framework files with existing projects.

## Overview

The Framework Update Service automatically updates framework-provided files in existing projects when the framework is updated. This ensures all projects benefit from bug fixes, new features, and improvements without manual intervention.

## Architecture

### Update Flow

```
Framework Update Triggered
         ↓
FrameworkUpdateService.update_framework()
         ↓
┌────────────────────────────────────────┐
│ 1. Update .mcp.json Configuration      │
│    - Preserve user's custom MCP servers │
│    - Update claudetask MCP server config│
│    - Add new framework MCP servers      │
└────────────┬───────────────────────────┘
             ↓
┌────────────────────────────────────────┐
│ 2. Regenerate CLAUDE.md                │
│    - Detect project technologies        │
│    - Generate from latest template      │
│    - Backup existing CLAUDE.md          │
└────────────┬───────────────────────────┘
             ↓
┌────────────────────────────────────────┐
│ 3. Update Agent Files                  │
│    - Remove old .claude/agents/         │
│    - Copy latest agents from framework  │
│    - Ensure all agents are current      │
└────────────┬───────────────────────────┘
             ↓
┌────────────────────────────────────────┐
│ 4. Update Command Files                │
│    - Copy commands to .claude/commands/ │
│    - Skip README.md                     │
│    - Preserve user customizations       │
└────────────┬───────────────────────────┘
             ↓
┌────────────────────────────────────────┐
│ 5. Update Hook Files                   │
│    - Copy hook configs (.json files)    │
│    - Copy hook scripts (.sh files)      │
│    - Make scripts executable (chmod +x) │
│    - Generate .claude/settings.json     │
└────────────┬───────────────────────────┘
             ↓
┌────────────────────────────────────────┐
│ 6. Return Update Report                │
│    - List of updated files              │
│    - Any errors encountered             │
│    - Success/failure status             │
└────────────────────────────────────────┘
```

## Service Implementation

**Location:** `claudetask/backend/app/services/framework_update_service.py`

### Core Method

```python
class FrameworkUpdateService:
    @staticmethod
    async def update_framework(project_path: str, project_id: str) -> Dict:
        """Update framework files in an existing project

        Args:
            project_path: Absolute path to project
            project_id: Project UUID

        Returns:
            Dict with success status, updated_files list, and any errors
        """
```

## Update Components

### 1. MCP Configuration Update

**Purpose:** Keep MCP server configurations current while preserving user customizations.

**Process:**
1. Read existing `.mcp.json` from project
2. Extract user's custom MCP servers (non-claudetask servers)
3. Load latest MCP template from `framework-assets/mcp-configs/mcp-template.json`
4. Update claudetask server with current paths:
   - Python interpreter: `venv/bin/python`
   - Server script: `mcp_server/native_stdio_server.py`
   - Project path environment variable
5. Merge user servers + framework servers
6. Write updated `.mcp.json`

**Example:**

```python
# Preserve user's custom servers
preserved_servers = {}
for name, config in existing_config["mcpServers"].items():
    if not name.startswith("claudetask"):
        preserved_servers[name] = config

# Update claudetask config from template
template_servers["claudetask"]["command"] = venv_python
template_servers["claudetask"]["args"] = [native_server_script]
template_servers["claudetask"]["env"]["CLAUDETASK_PROJECT_PATH"] = project_path

# Merge
new_config = {
    "mcpServers": {
        **preserved_servers,
        **template_servers
    }
}
```

### 2. CLAUDE.md Regeneration

**Purpose:** Update project instructions with latest framework guidance.

**Process:**
1. Detect project technologies using `ProjectService._detect_technologies()`
2. Get project metadata from `.claudetask/project.json`
3. Backup existing `CLAUDE.md` to `CLAUDE.md.backup`
4. Generate new `CLAUDE.md` using `generate_claude_md()` from template
5. Write new CLAUDE.md

**Technology Detection:**

```python
def _detect_technologies(project_path: str) -> List[str]:
    """Detect technologies used in project

    Checks for:
    - package.json → Node.js, React
    - requirements.txt → Python
    - Cargo.toml → Rust
    - go.mod → Go
    - pom.xml → Java
    """
```

**Generated Content:**
- Project mode instructions (SIMPLE or DEVELOPMENT)
- Worktree configuration (if enabled)
- Technology-specific guidance
- Task workflow instructions
- Critical restrictions and safety rules

### 3. Agent Files Update

**Purpose:** Ensure all specialized agents are up-to-date.

**Process:**
1. **Complete Refresh**: Remove entire `.claude/agents/` directory
2. Recreate `.claude/agents/` directory
3. Copy all `.md` files from `framework-assets/claude-agents/`
4. Track updated files for report

**Why Complete Refresh:**
- Ensures no orphaned agents from previous versions
- Guarantees all agents are current
- Removes deprecated agent configurations
- Clean slate for each update

**Available Agents:**
- `ai-implementation-expert.md`
- `api-validator.md`
- `backend-architect.md`
- `business-analyst.md`
- `context-analyzer.md`
- `docs-generator.md`
- `frontend-developer.md`
- `fullstack-code-reviewer.md`
- And 10+ more specialized agents

### 4. Command Files Update

**Purpose:** Provide latest slash commands to projects.

**Process:**
1. Copy `.md` files from `framework-assets/claude-commands/`
2. Skip `README.md` (internal documentation)
3. Preserve user-modified commands (overwrite with latest)
4. Destination: `.claude/commands/`

**Available Commands:**
- `/create-agent` - Create new specialized agent
- `/create-hook` - Create new automation hook
- `/create-skill` - Create new skill definition
- `/edit-agent` - Modify existing agent
- `/edit-hook` - Modify existing hook
- `/edit-skill` - Modify existing skill
- `/merge` - Merge PR and cleanup
- `/start-feature` - Start new feature development
- `/update-documentation` - Trigger documentation update

### 5. Hook Files Update (NEW in Recent Changes)

**Purpose:** Update automation hooks with latest implementations.

**Process:**

#### Step 1: Copy Hook Configurations
```python
for hook_file in os.listdir(hooks_source_dir):
    if hook_file.endswith(".json"):
        source_file = os.path.join(hooks_source_dir, hook_file)
        dest_file = os.path.join(hooks_dir, hook_file)
        shutil.copy2(source_file, dest_file)

        # Read hook config for settings.json
        with open(source_file, 'r') as f:
            hook_data = json.load(f)
            if "hook_config" in hook_data:
                # Collect hook configs
                for event_type, event_hooks in hook_data["hook_config"].items():
                    if event_type not in hook_configs:
                        hook_configs[event_type] = []
                    hook_configs[event_type].extend(event_hooks)
```

#### Step 2: Copy Hook Scripts
```python
elif hook_file.endswith(".sh"):
    source_file = os.path.join(hooks_source_dir, hook_file)
    dest_file = os.path.join(hooks_dir, hook_file)
    shutil.copy2(source_file, dest_file)

    # Make script executable
    os.chmod(dest_file, 0o755)
```

#### Step 3: Generate settings.json
```python
# Create/update .claude/settings.json
settings_file = os.path.join(claude_dir, "settings.json")
settings_data = {"hooks": hook_configs}

# Merge with existing settings if file exists
if os.path.exists(settings_file):
    with open(settings_file, 'r') as f:
        existing_settings = json.load(f)
        existing_settings["hooks"] = hook_configs
        settings_data = existing_settings

with open(settings_file, 'w') as f:
    json.dump(settings_data, f, indent=2)
```

**Hook Files Copied:**
- `bash-command-logger.json` - Log all bash commands
- `code-formatter.json` - Auto-format code on save
- `desktop-notifications.json` - Desktop alerts
- `file-protection.json` - Protect critical files
- `git-auto-commit.json` - Auto-commit on milestones
- `post-merge-documentation.json` - Documentation updates
- `post-push-docs.sh` - Documentation update script (executable)

**Result:** `.claude/settings.json` is automatically configured with all hook events.

## API Integration

### Endpoint

**POST** `/api/projects/{project_id}/update-framework`

**Request:**
```json
{
  "project_id": "uuid-string"
}
```

**Response:**
```json
{
  "success": true,
  "updated_files": [
    ".mcp.json",
    "CLAUDE.md",
    "CLAUDE.md.backup",
    ".claude/agents/backend-architect.md",
    ".claude/agents/frontend-developer.md",
    ".claude/commands/create-agent.md",
    ".claude/commands/update-documentation.md",
    ".claude/hooks/post-merge-documentation.json",
    ".claude/hooks/post-push-docs.sh",
    ".claude/settings.json"
  ],
  "errors": [],
  "message": "Successfully updated 10 framework files"
}
```

### Frontend Integration

**Component:** ProjectSettings or ProjectList

```typescript
const handleUpdateFramework = async (projectId: string) => {
  try {
    const response = await axios.post(
      `/api/projects/${projectId}/update-framework`
    );

    console.log(`Updated ${response.data.updated_files.length} files`);
    showNotification("Framework updated successfully");
  } catch (error) {
    showNotification("Framework update failed", "error");
  }
};
```

## Use Cases

### 1. Framework Bug Fix

**Scenario:** Bug fixed in `post-push-docs.sh` hook script

**Update Process:**
1. Developer fixes bug in `framework-assets/claude-hooks/post-push-docs.sh`
2. User clicks "Update Framework" in project settings
3. Framework update service copies fixed script
4. Script is made executable automatically
5. Next hook trigger uses fixed version

### 2. New Agent Added

**Scenario:** New `performance-engineer.md` agent created

**Update Process:**
1. Developer adds agent to `framework-assets/claude-agents/`
2. User updates framework
3. Old `.claude/agents/` directory is removed
4. All agents (including new one) are copied
5. New agent immediately available in Task tool

### 3. CLAUDE.md Template Update

**Scenario:** Critical instruction added to CLAUDE.md template

**Update Process:**
1. Developer updates `framework-assets/claude-configs/CLAUDE.md` template
2. User updates framework
3. Old CLAUDE.md backed up to CLAUDE.md.backup
4. New CLAUDE.md generated with latest instructions
5. Claude Code reads updated instructions on next session

### 4. New MCP Server Added

**Scenario:** Playwright MCP server added to framework

**Update Process:**
1. Developer adds playwright config to `mcp-template.json`
2. User updates framework
3. User's custom MCP servers are preserved
4. Playwright server config is merged into `.mcp.json`
5. Claude Code can use playwright tools immediately

## Project Initialization vs Framework Update

### Project Initialization

**When:** New project is added to ClaudeTask

**Actions:**
- Copy all framework files for first time
- Create `.claudetask/` directory
- Initialize git repository (if needed)
- Generate initial CLAUDE.md
- Copy agents, commands, hooks
- Create database records

**Service:** `ProjectService.initialize_project()`

### Framework Update

**When:** Existing project needs framework updates

**Actions:**
- Update existing framework files
- Preserve user customizations
- Backup critical files (CLAUDE.md)
- Clean refresh of agents
- Merge MCP configurations
- Update hooks and settings

**Service:** `FrameworkUpdateService.update_framework()`

## File Preservation Strategy

### Files Completely Replaced
- `.claude/agents/*.md` (clean refresh)
- `CLAUDE.md` (backup created)
- `.claude/hooks/*.json`
- `.claude/hooks/*.sh`

### Files Merged
- `.mcp.json` (user servers preserved)
- `.claude/settings.json` (hooks merged)

### Files Never Touched
- User's project source code
- `.claudetask/project.json`
- User's custom hooks/skills in database
- Task data and history

## Error Handling

### Common Errors

**1. Framework Directory Not Found**
```python
if not os.path.exists(framework_path):
    return {
        "success": False,
        "errors": [f"Framework path not found: {framework_path}"]
    }
```

**2. MCP Template Read Failure**
```python
try:
    with open(mcp_template_path, "r") as f:
        template_config = json.load(f)
except Exception as e:
    return {
        "success": False,
        "message": f"Failed to read MCP template: {e}"
    }
```

**3. Permission Errors**
```python
try:
    os.chmod(dest_file, 0o755)
except PermissionError as e:
    errors.append(f"Failed to make {dest_file} executable: {e}")
    # Continue with other files
```

### Error Recovery

**Partial Success:**
- Update continues even if individual file fails
- All errors collected in errors list
- Success = True if critical files updated
- Updated files list shows what succeeded

**Complete Failure:**
- Returns success = False
- Provides detailed error message
- No changes committed if transaction-based
- User can retry after fixing issue

## Logging and Debugging

### Update Logging

```python
print(f"Updated {len(source_agents)} agent files: {source_agents[:5]}...")
print(f"Generated CLAUDE.md: {len(generated_content)} chars, has critical restrictions: {has_critical_restrictions}")
```

**Log Locations:**
- Backend stdout: Framework update progress
- `.claude/logs/hooks/`: Hook execution logs
- Backend logs: Error details

### Verification

**After Update:**
```bash
# Check updated files
ls -la .claude/agents/
ls -la .claude/commands/
ls -la .claude/hooks/

# Verify executable permissions
ls -la .claude/hooks/*.sh

# Check settings.json
cat .claude/settings.json | jq '.hooks'

# Verify CLAUDE.md
head -20 CLAUDE.md
diff CLAUDE.md CLAUDE.md.backup
```

## Best Practices

### For Framework Developers

1. **Test Template Changes**: Verify CLAUDE.md template generates correctly
2. **Version Hooks**: Update version in hook JSON when changing scripts
3. **Document Changes**: Update hook setup_instructions for breaking changes
4. **Backward Compatibility**: Preserve existing hook configurations when possible
5. **Idempotent Updates**: Ensure updates can be run multiple times safely

### For Users

1. **Backup Before Update**: Although CLAUDE.md is backed up, manual backup is safer
2. **Review Changes**: Check CLAUDE.md.backup for any custom modifications to preserve
3. **Test After Update**: Run a simple task to verify framework works
4. **Update Regularly**: Get bug fixes and improvements promptly
5. **Report Issues**: If update fails, report errors for framework improvement

## Future Enhancements

1. **Selective Updates**: Choose which components to update (agents only, hooks only, etc.)
2. **Version Tracking**: Track framework version in project metadata
3. **Migration Scripts**: Automatic data migration for breaking changes
4. **Rollback Support**: Revert to previous framework version if update breaks project
5. **Update Notifications**: Alert users when framework updates are available
6. **Diff Preview**: Show what will change before applying update
7. **Conflict Resolution**: Interactive merge for conflicting customizations

## Related Documentation

- [Hooks System Architecture](./hooks-system.md) - Detailed hook implementation
- [Database Migrations](../deployment/database-migrations.md) - Schema evolution
- [Project Modes](./project-modes.md) - SIMPLE vs DEVELOPMENT mode
- [MCP Tools Reference](../api/mcp-tools.md) - MCP server configuration
