# Skills & MCP Configs Architecture Analysis

## Executive Summary

The Claude Code Feature Framework has a sophisticated system for managing both **Skills** and **MCP Configurations**. This document provides a detailed breakdown of how skills are implemented so that MCP configs can be replicated using the same patterns.

---

## Part 1: Skills Management Architecture

### 1.1 Overview

Skills are specialized capabilities that can be:
- **Default Skills**: Framework-provided skills from `framework-assets/claude-skills/`
- **Custom Skills**: User-created skills for specific projects
- **Enabled/Disabled**: Per-project basis with file-based synchronization

### 1.2 Database Models

Located in: `/claudetask/backend/app/models.py`

#### DefaultSkill Table
```python
class DefaultSkill(Base):
    __tablename__ = "default_skills"
    
    id: Integer (PK)
    name: String(100) - UNIQUE
    description: Text
    category: String(50)  # e.g., "Analysis", "Development", "Testing"
    file_name: String(100)  # File path in framework-assets
    content: Text  # Skill markdown content
    skill_metadata: JSON
    is_active: Boolean
    created_at: DateTime
    updated_at: DateTime
```

#### CustomSkill Table
```python
class CustomSkill(Base):
    __tablename__ = "custom_skills"
    
    id: Integer (PK)
    project_id: String (FK)
    name: String(100)
    description: Text
    category: String(50)
    file_name: String(100)
    content: Text
    status: String(20)  # "creating", "active", "failed"
    error_message: Text
    created_by: String(100)
    created_at: DateTime
    updated_at: DateTime
```

#### ProjectSkill Table (Junction)
```python
class ProjectSkill(Base):
    __tablename__ = "project_skills"
    
    id: Integer (PK)
    project_id: String (FK)
    skill_id: Integer
    skill_type: String(10)  # "default" or "custom"
    enabled_at: DateTime
    enabled_by: String(100)
```

#### AgentSkillRecommendation Table
```python
class AgentSkillRecommendation(Base):
    __tablename__ = "agent_skill_recommendations"
    
    id: Integer (PK)
    agent_name: String(100)
    skill_id: Integer
    skill_type: String(10)  # "default" or "custom"
    priority: Integer  # 1-5 (1 = highest)
    reason: Text
    created_at: DateTime
```

### 1.3 API Endpoints

Located in: `/claudetask/backend/app/routers/skills.py`

#### Core Endpoints

| Method | Path | Purpose |
|--------|------|---------|
| GET | `/api/projects/{project_id}/skills/` | Get all skills (organized by type) |
| GET | `/api/projects/{project_id}/skills/defaults` | Get all default skills |
| POST | `/api/projects/{project_id}/skills/enable/{skill_id}` | Enable a default skill |
| POST | `/api/projects/{project_id}/skills/disable/{skill_id}` | Disable a skill |
| POST | `/api/projects/{project_id}/skills/create` | Create custom skill (async) |
| DELETE | `/api/projects/{project_id}/skills/{skill_id}` | Delete custom skill |
| GET | `/api/projects/{project_id}/skills/agents/{agent_name}/recommended` | Get recommended skills for agent |

#### Response Format (SkillsResponse)
```typescript
{
  enabled: Skill[];           // Currently enabled skills
  available_default: Skill[]; // All default skills (whether enabled or not)
  custom: Skill[]             // User-created custom skills
}
```

### 1.4 Enable/Disable Toggle Mechanism

#### Enable Skill Flow
1. **Validate** skill exists in `default_skills` table
2. **Copy** skill file from `framework-assets/claude-skills/` → `project/.claude/skills/`
3. **Insert** record into `project_skills` junction table
4. **Return** enabled skill DTO

#### Disable Skill Flow
1. **Find** skill in `project_skills` junction table
2. **Delete** skill file from `project/.claude/skills/`
3. **Delete** record from `project_skills` junction table
4. Keep record in `custom_skills` (don't delete for custom skills)

**Code Reference** (`SkillService.enable_skill` and `disable_skill`):
```python
async def enable_skill(self, project_id: str, skill_id: int) -> SkillInDB:
    # Check already enabled
    # Copy file via SkillFileService
    # Insert into project_skills
    # Return DTO

async def disable_skill(self, project_id: str, skill_id: int):
    # Delete from project_skills
    # Delete skill file via SkillFileService
    # Keep custom_skill record
```

### 1.5 File System Structure

#### Framework Assets Structure
```
framework-assets/
├── claude-skills/
│   ├── business-requirements-analysis.md      # Single file skill
│   ├── api-development/                        # Directory-based skill
│   │   ├── SKILL.md (main entry point)
│   │   ├── docs/
│   │   ├── examples/
│   │   └── resources/
│   ├── code-review/
│   ├── database-migration/
│   ├── debug-helper/
│   ├── deployment-helper/
│   ├── documentation-writer/
│   ├── git-workflow/
│   ├── refactoring/
│   ├── test-runner/
│   └── ui-component/
```

#### Project Skills Directory
```
project/
└── .claude/
    └── skills/
        ├── business-requirements-analysis.md
        ├── api-development/
        │   ├── SKILL.md
        │   ├── docs/
        │   ├── examples/
        │   └── resources/
        └── [other enabled skills...]
```

### 1.6 SkillFileService

Located in: `/claudetask/backend/app/services/skill_file_service.py`

**Key Methods:**

1. **copy_skill_to_project()**
   - Handles both single-file and directory-based skills
   - Detects based on `/` in filename
   - Creates placeholder if source not found
   - Returns bool success status

2. **delete_skill_from_project()**
   - Removes file or entire directory
   - Gracefully handles already-deleted files
   - Returns bool success status

3. **read_skill_content()**
   - Reads skill file asynchronously
   - Returns content or None on error

4. **skill_exists_in_project()**
   - Checks if skill file exists
   - Returns bool

5. **validate_skill_file_path()**
   - Security: prevents path traversal attacks
   - Ensures path is within `.claude/skills/` directory

**Key Implementation Detail:**
```python
def _get_framework_skills_dir(self) -> str:
    """Navigate from: backend/app/services → backend → claudetask → project_root"""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = Path(current_dir).parent.parent.parent.parent
    return os.path.join(project_root, "framework-assets", "claude-skills")
```

### 1.7 Custom Skill Creation (Two-Phase Process)

#### Phase 1: Create Record (Synchronous)
**Endpoint:** POST `/api/projects/{project_id}/skills/create`
```python
async def create_custom_skill(
    project_id: str,
    skill_create: SkillCreate
) -> SkillInDB:
    # Validate skill name
    # Check uniqueness
    # Generate file_name from skill name
    # Create record with status="creating"
    # Return DTO
    # Launch background task
```

#### Phase 2: CLI Execution (Asynchronous)
**Service:** `SkillCreationService.create_skill_via_claude_cli()`

Process:
1. Start Claude terminal session
2. Send `/create-skill "Name" "Description"` command
3. Claude Code executes command via `/create-skill` slash command
4. Delegates to `skills-creator` agent
5. Agent creates skill file in `project/.claude/skills/`
6. Backend waits for file to appear (30-minute timeout)
7. Updates status to "active" or "failed"
8. Automatically enables skill (adds to `project_skills`)

**Key Implementation:**
```python
async def execute_skill_creation_cli(
    self,
    project_id: str,
    skill_id: int,
    skill_name: str,
    skill_description: str
):
    # Sanitize inputs
    # Execute Claude CLI
    # Update skill status
    # Auto-enable skill on success
    # Handle failures gracefully
```

### 1.8 Frontend UI (React)

Located in: `/claudetask/frontend/src/pages/Skills.tsx`

**Key Features:**
- Tab-based UI (Default | Custom | Enabled)
- Toggle switches for enable/disable
- Create Custom Skill dialog with async form
- Status indicators (creating | active | failed)
- Delete button for custom skills
- Error handling and loading states

**API Integration Pattern:**
```typescript
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:3333'

// Fetch skills
GET ${API_BASE_URL}/api/projects/{activeProjectId}/skills/

// Enable skill
POST ${API_BASE_URL}/api/projects/{activeProjectId}/skills/enable/{skillId}

// Disable skill
POST ${API_BASE_URL}/api/projects/{activeProjectId}/skills/disable/{skillId}

// Create custom skill
POST ${API_BASE_URL}/api/projects/{activeProjectId}/skills/create
Body: { name, description }
```

### 1.9 Pydantic Schemas

Located in: `/claudetask/backend/app/schemas.py`

```python
class SkillBase(BaseModel):
    name: str = Field(..., min_length=3, max_length=100)
    description: str = Field(..., min_length=10, max_length=500)

class SkillCreate(SkillBase):
    pass

class SkillInDB(SkillBase):
    id: int
    skill_type: str  # "default" or "custom"
    category: str
    file_path: Optional[str] = None
    is_enabled: bool = False
    status: Optional[str] = None  # "creating", "active", "failed"
    created_by: Optional[str] = None
    created_at: datetime
    updated_at: datetime

class SkillsResponse(BaseModel):
    enabled: List[SkillInDB]
    available_default: List[SkillInDB]
    custom: List[SkillInDB]
```

---

## Part 2: MCP Configs Architecture (To Be Implemented)

### 2.1 Current MCP Structure

Located in: `/framework-assets/mcp-configs/`

**Files:**
- `mcp-template.json` - Template for MCP configuration
- `.mcp.json` - Example full configuration

**Current .mcp.json:**
```json
{
  "mcpServers": {
    "claudetask": {
      "command": "python3",
      "args": ["claudetask/mcp_server/native_stdio_server.py"],
      "env": {
        "CLAUDETASK_PROJECT_ID": "...",
        "CLAUDETASK_PROJECT_PATH": ".",
        "CLAUDETASK_BACKEND_URL": "http://localhost:3333"
      }
    },
    "playwright": {
      "command": "npx",
      "args": ["-y", "@playwright/mcp@latest"]
    }
  }
}
```

### 2.2 Proposed MCP Configs Management (Based on Skills Pattern)

#### Database Models

**MCPConfig Table**
```python
class MCPConfig(Base):
    __tablename__ = "mcp_configs"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False, unique=True)
    description = Column(Text, nullable=False)
    category = Column(String(50), nullable=False)  # e.g., "Data", "Testing", "Deployment"
    config_type = Column(String(50), nullable=False)  # "default" or "custom"
    file_name = Column(String(100), nullable=False)  # Config file path
    config_content = Column(Text, nullable=False)  # Full MCP config JSON
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
```

**ProjectMCPConfig Table (Junction)**
```python
class ProjectMCPConfig(Base):
    __tablename__ = "project_mcp_configs"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    project_id = Column(String, ForeignKey("projects.id"), nullable=False)
    mcp_config_id = Column(Integer, ForeignKey("mcp_configs.id"), nullable=False)
    merged_at = Column(DateTime, default=datetime.utcnow)
    merged_by = Column(String(100), default="user")
```

#### File System Structure

```
framework-assets/
└── mcp-configs/
    ├── mcp-template.json (reference template)
    ├── datadog.json
    ├── github-actions.json
    ├── aws-lambda.json
    ├── docker-compose.json
    └── [other configs]

project/
└── .claude/
    └── mcp-configs/
        ├── merged-config.json (merged enabled configs)
        └── [individual enabled configs]
```

#### API Endpoints Pattern

```
GET     /api/projects/{project_id}/mcp-configs/
GET     /api/projects/{project_id}/mcp-configs/defaults
POST    /api/projects/{project_id}/mcp-configs/enable/{config_id}
POST    /api/projects/{project_id}/mcp-configs/disable/{config_id}
POST    /api/projects/{project_id}/mcp-configs/create
DELETE  /api/projects/{project_id}/mcp-configs/{config_id}
GET     /api/projects/{project_id}/mcp-configs/agents/{agent_name}/recommended
```

#### MCPConfigService Pattern

```python
class MCPConfigService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.file_service = MCPConfigFileService()
    
    async def get_project_configs(self, project_id: str) -> MCPConfigsResponse:
        """Get all MCP configs organized by type"""
    
    async def enable_config(self, project_id: str, config_id: int) -> MCPConfigInDB:
        """Enable an MCP config by merging into .mcp.json"""
    
    async def disable_config(self, project_id: str, config_id: int):
        """Disable an MCP config and regenerate merged config"""
    
    async def create_custom_config(self, project_id: str, config_create: MCPConfigCreate):
        """Create custom MCP config"""
    
    async def merge_configs(self, project_id: str) -> str:
        """Merge enabled configs into single .mcp.json"""
```

#### MCPConfigFileService Pattern

```python
class MCPConfigFileService:
    async def merge_config_to_project(
        self,
        project_path: str,
        config_content: str,
        config_name: str
    ) -> bool:
        """Merge MCP config into project's .mcp.json"""
    
    async def remove_config_from_project(
        self,
        project_path: str,
        config_name: str
    ) -> bool:
        """Remove MCP config from project's .mcp.json"""
    
    async def regenerate_merged_config(self, project_path: str) -> bool:
        """Regenerate merged .mcp.json from all enabled configs"""
    
    def validate_config_json(self, config_content: str) -> bool:
        """Validate MCP JSON structure"""
```

### 2.3 Key Differences from Skills

| Aspect | Skills | MCP Configs |
|--------|--------|-----------|
| **File Structure** | Single file (.md) or directory | JSON objects |
| **Storage** | Markdown files in filesystem | JSON content in DB + merged JSON |
| **Merging** | Independent files | Merged into single .mcp.json |
| **Validation** | Text content | JSON schema validation |
| **Activation** | File copy to project | JSON merge into .mcp.json |
| **Runtime Impact** | Claude Code picks up files | Claude CLI reads .mcp.json on startup |

### 2.4 MCP Config Merging Algorithm

```python
async def regenerate_merged_config(self, project_id: str, project_path: str):
    """
    Algorithm:
    1. Get all enabled configs for project from project_mcp_configs
    2. Load each config's JSON content
    3. Load existing .mcp.json (if exists)
    4. Merge mcpServers:
       - Keep existing entries not in enabled configs
       - Update/add entries from enabled configs
       - Preserve custom entries
    5. Validate merged JSON
    6. Write to project/.mcp.json
    7. Return success/failure
    """
```

---

## Part 3: Implementation Checklist for MCP Configs

### Phase 1: Database Setup
- [ ] Create MCPConfig table (like DefaultSkill)
- [ ] Create CustomMCPConfig table (like CustomSkill)
- [ ] Create ProjectMCPConfig table (like ProjectSkill)
- [ ] Create AgentMCPConfigRecommendation table (like AgentSkillRecommendation)
- [ ] Run migrations

### Phase 2: Services
- [ ] Create MCPConfigService (mirror SkillService structure)
- [ ] Create MCPConfigFileService (mirror SkillFileService structure)
- [ ] Implement merge algorithm
- [ ] Add JSON validation

### Phase 3: API Endpoints
- [ ] Create MCPConfigRouter (mirror skills.py structure)
- [ ] Implement all CRUD endpoints
- [ ] Add validation and error handling

### Phase 4: Frontend
- [ ] Create MCPConfigs.tsx page (mirror Skills.tsx)
- [ ] Implement tab-based UI
- [ ] Add enable/disable toggles
- [ ] Add create/delete functionality

### Phase 5: Testing
- [ ] Unit tests for MCPConfigService
- [ ] Integration tests for API endpoints
- [ ] E2E tests for UI

---

## Key Implementation Patterns Summary

### Pattern 1: Two-Table Organization
- **Table 1**: Defines available items (DefaultSkill / DefaultMCPConfig)
- **Table 2**: Tracks user-created items (CustomSkill / CustomMCPConfig)
- **Junction**: Links items to projects (ProjectSkill / ProjectMCPConfig)

### Pattern 2: File System Synchronization
1. **Enable**: Copy/merge file → Insert DB record
2. **Disable**: Delete DB record → Delete/update file
3. **Files follow DB**: Database is source of truth

### Pattern 3: Service Layer Architecture
- **Router**: HTTP endpoints
- **Service**: Business logic
- **FileService**: File system operations
- **Schemas**: Pydantic validation

### Pattern 4: Frontend Integration
- Use API_BASE_URL environment variable
- Fetch project-specific endpoints
- Handle async operations with loading/error states
- Refresh data after mutations

---

## File Paths Reference

### Backend Services
- Skill Service: `/claudetask/backend/app/services/skill_service.py`
- Skill File Service: `/claudetask/backend/app/services/skill_file_service.py`
- Skill Router: `/claudetask/backend/app/routers/skills.py`
- Models: `/claudetask/backend/app/models.py`
- Schemas: `/claudetask/backend/app/schemas.py`

### Frontend
- Skills Page: `/claudetask/frontend/src/pages/Skills.tsx`

### Framework Assets
- Default Skills: `/framework-assets/claude-skills/`
- MCP Configs: `/framework-assets/mcp-configs/`

### Project Local
- Local Skills: `project/.claude/skills/`
- Local MCP Config: `project/.mcp.json`

---

## Important Security Considerations

1. **Path Traversal Prevention**: Validate all file paths are within `.claude/` directory
2. **JSON Validation**: Validate MCP config JSON structure before merging
3. **Backup Strategy**: Keep backup of original .mcp.json before merging
4. **Error Handling**: Graceful failure if merge fails (restore original)
5. **File Permissions**: Ensure proper permissions on created files/directories

---

## Conclusion

The Skills management system provides an excellent architectural foundation for implementing MCP Configs management. By following the same patterns:
- Database organization (Default + Custom + Junction)
- Service layer separation
- File system synchronization
- API design
- Frontend UI patterns

The MCP Configs system can be implemented consistently and maintainably within the existing framework architecture.
