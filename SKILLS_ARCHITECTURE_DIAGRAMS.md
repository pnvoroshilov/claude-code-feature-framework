# Skills & MCP Configs Architecture - Visual Diagrams

## 1. Skills Management Data Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                    SKILLS MANAGEMENT FLOW                       │
└─────────────────────────────────────────────────────────────────┘

┌──────────────────────────┐
│   React Frontend         │
│   (Skills.tsx)          │
│                         │
│  - Tab-based UI         │
│  - Toggle switches      │
│  - Create dialog        │
│  - Delete actions       │
└────────────┬────────────┘
             │
             │ HTTP Requests
             ▼
┌──────────────────────────────────────────────────────────────────┐
│              FastAPI Backend (skills.py Router)                  │
│                                                                   │
│  GET    /api/projects/{id}/skills/                              │
│  POST   /api/projects/{id}/skills/enable/{skill_id}             │
│  POST   /api/projects/{id}/skills/disable/{skill_id}            │
│  POST   /api/projects/{id}/skills/create                        │
│  DELETE /api/projects/{id}/skills/{skill_id}                    │
└────────────┬────────────────────────────────────────────────────┘
             │
             │ Delegates to
             ▼
┌──────────────────────────────────────────────────────────────────┐
│           SkillService (skill_service.py)                        │
│                                                                   │
│  ┌─ enable_skill()                                              │
│  │   • Validate skill exists                                    │
│  │   • Copy file to project                                    │
│  │   • Insert ProjectSkill record                              │
│  │                                                              │
│  ├─ disable_skill()                                             │
│  │   • Delete ProjectSkill record                              │
│  │   • Delete skill file from project                          │
│  │                                                              │
│  ├─ create_custom_skill()                                       │
│  │   • Create record in DB (status=creating)                   │
│  │   • Launch background task                                  │
│  │                                                              │
│  ├─ execute_skill_creation_cli()                                │
│  │   • Start Claude terminal session                           │
│  │   • Execute /create-skill command                           │
│  │   • Update status on completion                             │
│  │                                                              │
│  └─ get_project_skills()                                        │
│      • Aggregate enabled + default + custom                    │
└────────┬───────────────────────────────────────────────────────┘
         │
         │ Uses
         ├─────────────────────────────────────────┐
         │                                         │
         ▼                                         ▼
┌──────────────────────────┐      ┌──────────────────────────┐
│  SkillFileService       │      │   Database (SQLAlchemy)  │
│  (skill_file_service)   │      │                          │
│                         │      │  • DefaultSkill          │
│ • copy_skill_to_project │      │  • CustomSkill           │
│ • delete_skill_from     │      │  • ProjectSkill (Junction)│
│   project               │      │  • AgentSkillRec (Linked)│
│ • read_skill_content    │      └──────────────────────────┘
│ • validate_file_path    │
└──────────────────────────┘
         │
         │ Manages files
         ▼
┌──────────────────────────────────────────────────────────────────┐
│                  File System                                     │
│                                                                   │
│  Framework Assets:                                              │
│  ├─ framework-assets/claude-skills/                             │
│  │  ├─ business-requirements-analysis.md (single file)          │
│  │  ├─ api-development/ (directory-based skill)                │
│  │  ├─ code-review/                                            │
│  │  └─ [...10 more default skills...]                          │
│  │                                                              │
│  Project Skills:                                                │
│  └─ project/.claude/skills/                                    │
│     ├─ [enabled default skills copied here]                    │
│     ├─ [custom skills created here]                            │
│     └─ [files reflect database state]                          │
└──────────────────────────────────────────────────────────────────┘
```

---

## 2. Enable/Disable Toggle Mechanism

```
┌─────────────────────────────────────────────────────────────────┐
│                   ENABLE SKILL SEQUENCE                         │
└─────────────────────────────────────────────────────────────────┘

User Clicks Toggle "ON"
    │
    ▼
POST /api/projects/{id}/skills/enable/{skill_id}
    │
    ▼
SkillService.enable_skill()
    │
    ├─► Verify skill exists in DefaultSkill table
    │
    ├─► Check if already enabled in ProjectSkill
    │
    ├─► Call SkillFileService.copy_skill_to_project()
    │   │
    │   ├─► Check if source exists in framework-assets
    │   │
    │   ├─► Detect: single-file or directory-based?
    │   │   • Single: Copy file to project/.claude/skills/
    │   │   • Directory: Copy entire directory tree
    │   │
    │   └─► Create placeholder if source missing
    │
    ├─► Insert ProjectSkill(project_id, skill_id, "default")
    │
    └─► Return SkillInDB DTO with is_enabled=true

Database State:
    DefaultSkill(id=1, name="API Development", ...)
    ProjectSkill(project_id="p1", skill_id=1, skill_type="default")

File System State:
    project/.claude/skills/api-development/ ← Copied from framework-assets


┌─────────────────────────────────────────────────────────────────┐
│                   DISABLE SKILL SEQUENCE                        │
└─────────────────────────────────────────────────────────────────┘

User Clicks Toggle "OFF"
    │
    ▼
POST /api/projects/{id}/skills/disable/{skill_id}
    │
    ▼
SkillService.disable_skill()
    │
    ├─► Find ProjectSkill record (must exist)
    │
    ├─► Get skill details from DefaultSkill/CustomSkill
    │
    ├─► Call SkillFileService.delete_skill_from_project()
    │   │
    │   ├─► Detect: single-file or directory-based?
    │   │   • Single: Delete file from .claude/skills/
    │   │   • Directory: Delete entire directory (recursively)
    │   │
    │   └─► Graceful fail if already deleted
    │
    ├─► Delete ProjectSkill record from database
    │
    └─► For CustomSkill: Keep record in CustomSkill table
        For DefaultSkill: Already in DefaultSkill table

Database State:
    ProjectSkill(project_id="p1", skill_id=1) ← DELETED
    CustomSkill record ← KEPT (don't delete)

File System State:
    project/.claude/skills/api-development/ ← DELETED
```

---

## 3. Custom Skill Creation (Two-Phase Process)

```
┌─────────────────────────────────────────────────────────────────┐
│             CUSTOM SKILL CREATION - PHASE 1 & 2                 │
└─────────────────────────────────────────────────────────────────┘

PHASE 1: SYNCHRONOUS (REST API)
═══════════════════════════════

User Fills Dialog:
  - Skill Name: "Database Migration Helper"
  - Description: "Helps with complex database migrations"
    │
    ▼
POST /api/projects/{id}/skills/create
  Body: { name: "Database Migration Helper", description: "..." }
    │
    ▼
SkillService.create_custom_skill()
  │
  ├─► Validate skill name (3-100 chars)
  │
  ├─► Check uniqueness in CustomSkill table
  │
  ├─► Generate file_name: "database-migration-helper.md"
  │
  ├─► Create CustomSkill record:
  │   │
  │   ├─ name: "Database Migration Helper"
  │   ├─ description: "..."
  │   ├─ project_id: "p1"
  │   ├─ file_name: "database-migration-helper.md"
  │   ├─ status: "creating" ◄─────── IMPORTANT: Not active yet
  │   ├─ created_by: "user"
  │   └─ created_at: now()
  │
  ├─► Launch background task:
  │   execute_skill_creation_cli(project_id, skill_id, name, desc)
  │
  └─► IMMEDIATELY return SkillInDB with status="creating"
        (Frontend shows loading spinner)

Database State After Phase 1:
  CustomSkill(id=5, name="Database Migration Helper", status="creating")
  ProjectSkill(project_id="p1", skill_id=5, skill_type="custom") ← Auto-enabled


PHASE 2: ASYNCHRONOUS (Background Task)
════════════════════════════════════════

Background Task executes in parallel:
  execute_skill_creation_cli() runs asynchronously
    │
    ├─► Sanitize inputs (remove dangerous characters)
    │
    ├─► Create ClaudeTerminalSession:
    │   │
    │   └─► session.start() initializes Claude Code
    │
    ├─► Send /create-skill command:
    │   │
    │   └─► Command: /create-skill "Database Migration Helper" "Helps with..."
    │
    ├─► Claude Code executes slash command:
    │   │
    │   ├─► Routes to /create-skill handler
    │   │
    │   └─► Delegates to skills-creator agent
    │
    ├─► Agent creates skill file:
    │   │
    │   └─► Writes: project/.claude/skills/database-migration-helper.md
    │
    ├─► Backend polls/waits for file creation (30-min timeout)
    │
    ├─► On success:
    │   │
    │   ├─► Update CustomSkill:
    │   │   ├─ status: "active"
    │   │   ├─ content: [read file content]
    │   │   └─ updated_at: now()
    │   │
    │   └─► ProjectSkill already exists (added in Phase 1)
    │
    └─► On failure:
        │
        ├─► Update CustomSkill:
        │   ├─ status: "failed"
        │   ├─ error_message: "..."
        │   └─ updated_at: now()
        │
        └─► Delete ProjectSkill (disable the skill)

Database State After Phase 2 (Success):
  CustomSkill(id=5, status="active", content="# Database Migration Helper\n...", ...)
  ProjectSkill(project_id="p1", skill_id=5, skill_type="custom") ← ENABLED

File System State After Phase 2 (Success):
  project/.claude/skills/database-migration-helper.md ← CREATED by agent

Frontend Updates:
  - Status spinner disappears
  - Shows "database-migration-helper" in Custom Skills tab
  - Marked as enabled
  - Delete button available
```

---

## 4. Database Schema Relationships

```
┌──────────────────────────────────────────────────────────────────┐
│                 DATABASE SCHEMA DIAGRAM                          │
└──────────────────────────────────────────────────────────────────┘

┌──────────────────────┐
│    DefaultSkill      │
├──────────────────────┤
│ id (PK)              │
│ name (UNIQUE)        │────┐
│ description          │    │
│ category             │    │
│ file_name            │    │
│ content              │    │
│ is_active            │    │
│ created_at           │    │
│ updated_at           │    │
└──────────────────────┘    │
                             │ (1-to-many)
                             │
                             ├─── One DefaultSkill can be
                             │    enabled in many projects
                             │
                             ▼
┌──────────────────────┐
│   ProjectSkill       │
├──────────────────────┤
│ id (PK)              │
│ project_id (FK) ──┐  │
│ skill_id ◄────┐  │  │
│ skill_type     │  │  │
│ enabled_at     │  │  │
│ enabled_by     │  │  │
└──────────────────┤──┘
                    │
        ┌───────────┘
        │
        │ "default" or "custom"
        │
        ├─────────────────────────────┐
        │                             │
        ▼                             ▼
┌──────────────────────┐    ┌──────────────────────┐
│   DefaultSkill       │    │   CustomSkill        │
│ (already shown)      │    ├──────────────────────┤
│                      │    │ id (PK)              │
│                      │    │ project_id (FK)      │
│                      │    │ name                 │
│                      │    │ description          │
│                      │    │ category             │
│                      │    │ file_name            │
│                      │    │ content              │
│                      │    │ status               │
│                      │    │ error_message        │
│                      │    │ created_by           │
│                      │    │ created_at           │
│                      │    │ updated_at           │
│                      │    └──────────────────────┘
└──────────────────────┘


┌──────────────────────────────────────────────────────┐
│ AgentSkillRecommendation (Links agents to skills)   │
├──────────────────────────────────────────────────────┤
│ id (PK)                                              │
│ agent_name (e.g., "frontend-developer")              │
│ skill_id (FK to DefaultSkill)                        │
│ skill_type ("default" or "custom")                   │
│ priority (1-5, where 1 is highest)                   │
│ reason (why this skill is recommended)               │
│ created_at                                           │
└──────────────────────────────────────────────────────┘
```

---

## 5. MCP Configs - Proposed Implementation Pattern

```
┌─────────────────────────────────────────────────────────────────┐
│            MCP CONFIGS MANAGEMENT (Proposed)                    │
│         Following Skills Architecture Pattern                   │
└─────────────────────────────────────────────────────────────────┘

Same 3-Table Structure as Skills:

┌──────────────────────┐
│    MCPConfig         │  (like DefaultSkill)
├──────────────────────┤
│ id (PK)              │
│ name (UNIQUE)        │────┐
│ description          │    │
│ category             │    │ 1-to-many
│ config_type          │    │
│ file_name            │    │
│ config_content (JSON)│    │
│ is_active            │    │
│ created_at           │    │
│ updated_at           │    │
└──────────────────────┘    │
                             ▼
                   ┌──────────────────────┐
                   │  ProjectMCPConfig    │ (Junction)
                   ├──────────────────────┤
                   │ id (PK)              │
                   │ project_id (FK)      │
                   │ mcp_config_id (FK)   │
                   │ merged_at            │
                   │ merged_by            │
                   └──────────────────────┘
                             │
                             │ Stores
                             ▼
                   ┌──────────────────────┐
                   │ project/.mcp.json    │
                   │                      │
                   │ (Merged config with  │
                   │  all enabled MCPServ)│
                   └──────────────────────┘


Key Difference from Skills:

Skills:                          MCP Configs:
- Copy individual .md files      - Merge JSON objects
- Each skill is separate file    - Merge into single .mcp.json
- Independent operation          - Dependent on merge strategy
- JSON not required              - JSON schema validation required


Merge Algorithm:

┌─ Get all enabled MCPConfig records for project
│
├─ Load .mcp.json from project root (if exists)
│
├─ For each enabled config:
│  │
│  ├─ Parse config_content as JSON
│  │
│  └─ Deep merge mcpServers object:
│     │
│     ├─ Keep existing servers not in enabled configs
│     ├─ Update/add servers from enabled configs
│     └─ Preserve user-custom entries
│
├─ Validate merged JSON structure
│
└─ Write to project/.mcp.json
   │
   ├─ Create backup if needed
   │
   └─ Atomic write (write temp, then move)
```

---

## 6. API Response Flow Example

```
┌────────────────────────────────────────────────────────────────┐
│  GET /api/projects/p1/skills/ Response                         │
│  SkillsResponse Structure                                      │
└────────────────────────────────────────────────────────────────┘

{
  "enabled": [
    {
      "id": 1,
      "name": "API Development",
      "description": "Comprehensive expertise in API design...",
      "skill_type": "default",
      "category": "Development",
      "file_path": "/path/to/project/.claude/skills/api-development/",
      "is_enabled": true,
      "status": "active",
      "created_by": "system",
      "created_at": "2024-11-01T...",
      "updated_at": "2024-11-01T..."
    },
    {
      "id": 5,
      "name": "Database Migration Helper",
      "description": "Helps with complex database migrations",
      "skill_type": "custom",
      "category": "Custom",
      "file_path": "/path/to/project/.claude/skills/database-migration-helper.md",
      "is_enabled": true,
      "status": "active",
      "created_by": "user",
      "created_at": "2024-11-05T...",
      "updated_at": "2024-11-05T..."
    }
  ],
  
  "available_default": [
    {
      "id": 1,
      "name": "API Development",
      ...
      "is_enabled": true      ← Currently enabled
    },
    {
      "id": 2,
      "name": "Code Review",
      ...
      "is_enabled": false     ← Not enabled, but available
    },
    {
      "id": 3,
      "name": "Database Migration",
      ...
      "is_enabled": false     ← Not enabled
    }
  ],
  
  "custom": [
    {
      "id": 5,
      "name": "Database Migration Helper",
      ...
      "is_enabled": true
    }
  ]
}

Legend:
- enabled: Currently active skills (default + custom)
- available_default: All framework-provided skills
- custom: All user-created skills
```

---

## 7. Service Layer Architecture Comparison

```
┌─────────────────────────────────────────────────────────────────┐
│           SERVICE LAYER - SKILLS vs MCP CONFIGS                 │
└─────────────────────────────────────────────────────────────────┘

SKILLS:
┌────────────────────────────────────┐
│  Router (skills.py)                │
│  HTTP Endpoints                    │
└────────────────┬───────────────────┘
                 │
    ┌────────────▼────────────┐
    │  SkillService           │
    │  Business Logic         │
    │  - enable_skill()       │
    │  - disable_skill()      │
    │  - create_custom_skill()│
    │  - get_project_skills() │
    └────────┬────────────────┘
             │
    ┌────────▼──────────────┐
    │ SkillFileService      │
    │ File Operations       │
    │ - copy_skill          │
    │ - delete_skill        │
    │ - read_content        │
    │ - validate_path       │
    └────────┬──────────────┘
             │
    ┌────────▼──────────────┐
    │ Database (SQLAlchemy) │
    │ Data Persistence      │
    └───────────────────────┘


MCP CONFIGS (Following Same Pattern):
┌────────────────────────────────────┐
│  Router (mcp_configs.py)           │
│  HTTP Endpoints                    │
└────────────────┬───────────────────┘
                 │
    ┌────────────▼────────────────┐
    │  MCPConfigService           │
    │  Business Logic             │
    │  - enable_config()          │
    │  - disable_config()         │
    │  - create_custom_config()   │
    │  - merge_configs()          │
    │  - get_project_configs()    │
    └────────┬────────────────────┘
             │
    ┌────────▼──────────────────┐
    │ MCPConfigFileService      │
    │ File Operations           │
    │ - merge_config_to_project │
    │ - remove_config           │
    │ - regenerate_merged       │
    │ - validate_json           │
    └────────┬──────────────────┘
             │
    ┌────────▼──────────────────┐
    │ Database (SQLAlchemy)     │
    │ Data Persistence          │
    └───────────────────────────┘
```

---

## 8. Enable/Disable State Machine

```
┌─────────────────────────────────────────────────────────────────┐
│              STATE MACHINE: Skill Lifecycle                      │
└─────────────────────────────────────────────────────────────────┘

DEFAULT SKILL LIFECYCLE:
═══════════════════════

  ┌─────────────┐
  │  Available  │ (exists in DefaultSkill table, not enabled)
  │  (Database) │
  └──────┬──────┘
         │
    POST /enable
         │
         ▼
  ┌──────────────────┐
  │     Enabled      │ (in DefaultSkill + ProjectSkill tables)
  │  (File Copied)   │ (file in project/.claude/skills/)
  └────────┬─────────┘
           │
      POST /disable
           │
           ▼
  ┌─────────────┐
  │ Disabled    │ (back to Available state)
  │ (File Del)  │
  └─────────────┘


CUSTOM SKILL LIFECYCLE:
═════════════════════

  ┌──────────────────┐
  │    Creating      │ (status="creating", background task running)
  │  (Phase 1 Done)  │
  └────────┬─────────┘
           │
      CLI creates file
           │
           ▼
  ┌──────────────────┐
  │     Active       │ (status="active", file exists, enabled)
  │  (Phase 2 Done)  │
  └────────┬─────────┘
           │
      POST /disable
           │
           ▼
  ┌──────────────────┐
  │    Disabled      │ (status="active", file deleted, not enabled)
  │  (ProjectSkill   │ (CustomSkill record still exists)
  │   Removed)       │
  └────────┬─────────┘
           │
      POST /delete
           │
           ▼
  ┌──────────────────┐
  │    Deleted       │ (CustomSkill record deleted, file gone)
  │  (Permanent)     │
  └──────────────────┘

ALT PATH (Creation Failure):

  ┌──────────────────┐
  │    Creating      │
  │  (Phase 1 Done)  │
  └────────┬─────────┘
           │
      CLI fails
           │
           ▼
  ┌──────────────────┐
  │     Failed       │ (status="failed", error_message set)
  │  (Phase 2 Error) │ (file not created)
  └────────┬─────────┘
           │
      POST /delete (manual cleanup)
           │
           ▼
  ┌──────────────────┐
  │    Deleted       │
  │  (Permanent)     │
  └──────────────────┘
```

---

## 9. File Synchronization Model

```
┌─────────────────────────────────────────────────────────────────┐
│         FILE SYNCHRONIZATION: Database ← → Filesystem           │
└─────────────────────────────────────────────────────────────────┘

SOURCE OF TRUTH: DATABASE

┌──────────────────────────────────────────────────────────────────┐
│                     DATABASE STATE                              │
├──────────────────────────────────────────────────────────────────┤
│ DefaultSkill table:     10 skills defined                       │
│ CustomSkill table:      N custom skills per project             │
│ ProjectSkill table:     Which skills are enabled               │
└────────────┬───────────────────────────────────────────────────┘
             │
             │ DELETE from ProjectSkill
             │    │
             │    └─► SkillFileService.delete_skill_from_project()
             │        │
             │        └─► DELETE project/.claude/skills/[skill-dir]
             │
             │ INSERT into ProjectSkill
             │    │
             │    └─► SkillFileService.copy_skill_to_project()
             │        │
             │        └─► COPY framework-assets → project/.claude/skills/
             │
             ▼

┌──────────────────────────────────────────────────────────────────┐
│                   FILE SYSTEM STATE                              │
├──────────────────────────────────────────────────────────────────┤
│ project/.claude/skills/                                         │
│   ├── api-development/    (if enabled in DB)                   │
│   ├── code-review/        (if enabled in DB)                   │
│   ├── database-migration/ (if enabled in DB)                   │
│   └── ...                 (only files in DB)                    │
└──────────────────────────────────────────────────────────────────┘

GUARANTEE: Files always match database state
- If in ProjectSkill table → File exists
- If NOT in ProjectSkill table → File does not exist
```

