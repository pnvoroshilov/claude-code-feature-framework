# Subagents API Endpoints

## Overview

The Subagents API manages specialized AI assistants with focused expertise and specific tool access. Subagents are used for task delegation and can be either default framework subagents or custom project-specific subagents.

## Base URL

```
http://localhost:3333/api/projects/{project_id}/subagents
```

## Endpoints

### GET `/api/projects/{project_id}/subagents`

Get all subagents for a project (enabled, available defaults, custom, and favorites).

**Response:**
```json
{
  "enabled": [
    {
      "id": 1,
      "name": "frontend-developer",
      "description": "React/TypeScript UI development specialist",
      "file_name": "frontend-developer.md",
      "category": "development",
      "is_custom": false,
      "is_favorite": false,
      "enabled_at": "2025-11-21T10:00:00Z"
    }
  ],
  "available_default": [
    {
      "id": 2,
      "name": "backend-architect",
      "description": "FastAPI/Python backend design specialist",
      "file_name": "backend-architect.md",
      "category": "architecture",
      "is_custom": false,
      "is_favorite": false
    }
  ],
  "custom": [
    {
      "id": 10,
      "name": "graphql-expert",
      "description": "GraphQL schema design and resolver optimization",
      "file_name": "graphql-expert.md",
      "category": "custom",
      "is_custom": true,
      "status": "active",
      "is_favorite": true,
      "created_at": "2025-11-21T09:00:00Z"
    }
  ]
}
```

### POST `/api/projects/{project_id}/subagents/enable/{subagent_id}`

Enable a subagent for a project.

**Query Parameters:**
- `subagent_kind` (optional): `"default"` or `"custom"`, defaults to `"default"`

**Process:**
1. Validates subagent exists in appropriate table
2. Inserts record into `project_subagents` junction table
3. Returns enabled subagent details

**Request:**
```http
POST /api/projects/my-project/subagents/enable/1?subagent_kind=default
```

**Response:**
```json
{
  "id": 1,
  "name": "frontend-developer",
  "description": "React/TypeScript UI development specialist",
  "file_name": "frontend-developer.md",
  "category": "development",
  "is_custom": false,
  "enabled_at": "2025-11-21T10:00:00Z"
}
```

**Error Responses:**
- `400` - Subagent already enabled or invalid type
- `404` - Subagent not found
- `500` - Database error

### POST `/api/projects/{project_id}/subagents/disable/{subagent_id}`

Disable a subagent for a project.

**Process:**
1. Removes record from `project_subagents` junction table
2. Keeps record in database (doesn't delete custom subagents)

**Request:**
```http
POST /api/projects/my-project/subagents/disable/1
```

**Response:**
```json
{
  "success": true,
  "message": "Subagent disabled successfully"
}
```

**Error Responses:**
- `404` - Subagent not found or not enabled
- `500` - Database error

### POST `/api/projects/{project_id}/subagents/enable-all`

Enable all available subagents (both default and custom) for a project.

**Process:**
1. Get all available default subagents
2. Get all custom subagents
3. Enable each subagent that isn't already enabled
4. Return count of newly enabled subagents

**Request:**
```http
POST /api/projects/my-project/subagents/enable-all
```

**Response:**
```json
{
  "success": true,
  "enabled_count": 12,
  "errors": []
}
```

**Response with Errors:**
```json
{
  "success": true,
  "enabled_count": 10,
  "errors": [
    "Failed to enable custom-analyzer: Database constraint violation",
    "Failed to enable security-expert: Permission denied"
  ]
}
```

**Status Codes:**
- `200 OK` - Operation completed (check enabled_count and errors)
- `500 Internal Server Error` - Operation failed completely

### POST `/api/projects/{project_id}/subagents/disable-all`

Disable all currently enabled subagents for a project.

**Process:**
1. Get all enabled subagents
2. Disable each enabled subagent
3. Return count of disabled subagents

**Request:**
```http
POST /api/projects/my-project/subagents/disable-all
```

**Response:**
```json
{
  "success": true,
  "disabled_count": 12,
  "errors": []
}
```

**Response with Errors:**
```json
{
  "success": true,
  "disabled_count": 10,
  "errors": [
    "Failed to disable frontend-developer: Database locked",
    "Failed to disable backend-architect: Active session exists"
  ]
}
```

**Status Codes:**
- `200 OK` - Operation completed (check disabled_count and errors)
- `500 Internal Server Error` - Operation failed completely

### POST `/api/projects/{project_id}/subagents/create`

Create a custom subagent using Claude Code CLI.

**Request Body:**
```json
{
  "name": "GraphQL Expert",
  "description": "Specialist in GraphQL schema design, resolvers, and query optimization"
}
```

**Process:**
1. Validates subagent name uniqueness
2. Inserts record into `custom_subagents` table with status "creating"
3. Launches background task for Claude Code CLI interaction
4. Returns subagent record (status updates when complete)

**Background Task:**
- Starts Claude terminal session
- Executes `/create-agent` command
- Sends agent name and description via terminal
- Waits for completion (with timeout)
- Updates subagent status to "active" or "failed"

**Response:**
```json
{
  "id": 10,
  "name": "graphql-expert",
  "description": "Specialist in GraphQL schema design, resolvers, and query optimization",
  "file_name": "graphql-expert.md",
  "status": "creating",
  "is_custom": true,
  "created_at": "2025-11-21T10:00:00Z"
}
```

**Status Values:**
- `creating` - Background task in progress
- `active` - Subagent ready to use
- `failed` - Creation failed (check error_message)

**Error Responses:**
- `400` - Invalid input or duplicate name
- `500` - Database or file system error

### DELETE `/api/projects/{project_id}/subagents/{subagent_id}`

Delete a custom subagent permanently.

**Process:**
1. Verifies subagent is custom (not default)
2. Removes from `project_subagents` junction table if enabled
3. Deletes record from `custom_subagents` table
4. Deletes subagent file from filesystem

**Request:**
```http
DELETE /api/projects/my-project/subagents/10
```

**Response:**
```json
{
  "success": true,
  "message": "Custom subagent deleted successfully"
}
```

**Error Responses:**
- `404` - Subagent not found or not a custom subagent
- `500` - Database or file system error

### POST `/api/projects/{project_id}/subagents/favorites/{subagent_id}`

Mark a subagent as favorite.

**Query Parameters:**
- `subagent_kind` (optional): `"default"` or `"custom"`, defaults to `"custom"`

**Process:**
1. Verifies subagent exists
2. Sets `is_favorite = True` in appropriate table
3. Returns updated subagent

**Note:** Favorites are global (not project-specific)

**Request:**
```http
POST /api/projects/my-project/subagents/favorites/1?subagent_kind=default
```

**Response:**
```json
{
  "id": 1,
  "name": "frontend-developer",
  "description": "React/TypeScript UI development specialist",
  "is_favorite": true,
  "updated_at": "2025-11-21T10:05:00Z"
}
```

**Error Responses:**
- `400` - Invalid subagent type
- `404` - Subagent not found
- `500` - Database error

### DELETE `/api/projects/{project_id}/subagents/favorites/{subagent_id}`

Remove a subagent from favorites.

**Query Parameters:**
- `subagent_kind` (optional): `"default"` or `"custom"`, defaults to `"custom"`

**Process:**
1. Verifies subagent exists and is marked as favorite
2. Sets `is_favorite = False`

**Request:**
```http
DELETE /api/projects/my-project/subagents/favorites/1?subagent_kind=default
```

**Response:**
```json
{
  "success": true,
  "message": "Subagent removed from favorites successfully"
}
```

**Error Responses:**
- `400` - Invalid subagent type
- `404` - Subagent not found
- `500` - Database error

### PATCH `/api/projects/{project_id}/subagents/{subagent_id}/status`

Update custom subagent status and archive it.

**Request Body:**
```json
{
  "status": "active",
  "error_message": null
}
```

**Process:**
1. Updates subagent status in `custom_subagents` table
2. Archives subagent to `.claudetask/agents/` for persistence
3. Enables subagent if status is "active"

**Use Case:**
This endpoint is called by MCP tools (`mcp__claudetask__update_subagent_status`) after subagent creation is complete.

**Response:**
```json
{
  "success": true,
  "message": "Subagent status updated and archived successfully"
}
```

**Error Responses:**
- `404` - Subagent not found
- `500` - Database or file system error

---

## Subagent Skills Management

### GET `/api/projects/{project_id}/subagents/{subagent_id}/skills`

Get all skills assigned to a subagent.

**Query Parameters:**
- `subagent_kind` (optional): `"default"` or `"custom"`, defaults to `"default"`

**Response:**
```json
[
  {
    "id": 1,
    "skill_id": 5,
    "skill_type": "default",
    "skill_name": "merge-skill",
    "skill_description": "Expert Git merge and conflict resolution",
    "skill_category": "git",
    "assigned_at": "2025-11-25T10:00:00Z"
  },
  {
    "id": 2,
    "skill_id": 8,
    "skill_type": "default",
    "skill_name": "python-refactor",
    "skill_description": "Clean Architecture refactoring for Python",
    "skill_category": "refactoring",
    "assigned_at": "2025-11-25T10:15:00Z"
  }
]
```

**Error Responses:**
- `404` - Subagent not found
- `500` - Database error

### POST `/api/projects/{project_id}/subagents/{subagent_id}/skills/assign`

Assign a single skill to a subagent.

**Query Parameters:**
- `skill_id` (required): ID of the skill to assign
- `skill_type` (optional): `"default"` or `"custom"`, defaults to `"default"`
- `subagent_kind` (optional): `"default"` or `"custom"`, defaults to `"default"`

**Process:**
1. Validates skill and subagent exist
2. Creates assignment in `subagent_skills` junction table
3. Returns skill assignment details

**Request:**
```http
POST /api/projects/my-project/subagents/1/skills/assign?skill_id=5&skill_type=default&subagent_kind=default
```

**Response:**
```json
{
  "id": 1,
  "skill_id": 5,
  "skill_type": "default",
  "skill_name": "merge-skill",
  "skill_description": "Expert Git merge and conflict resolution",
  "skill_category": "git",
  "assigned_at": "2025-11-25T10:00:00Z"
}
```

**Error Responses:**
- `400` - Skill already assigned or invalid type
- `404` - Skill or subagent not found
- `500` - Database error

### POST `/api/projects/{project_id}/subagents/{subagent_id}/skills/unassign`

Remove a skill assignment from a subagent.

**Query Parameters:**
- `skill_id` (required): ID of the skill to remove
- `skill_type` (optional): `"default"` or `"custom"`, defaults to `"default"`
- `subagent_kind` (optional): `"default"` or `"custom"`, defaults to `"default"`

**Process:**
1. Validates assignment exists
2. Removes record from `subagent_skills` junction table
3. Updates subagent markdown file to remove skill instructions

**Request:**
```http
POST /api/projects/my-project/subagents/1/skills/unassign?skill_id=5&skill_type=default&subagent_kind=default
```

**Response:**
```json
{
  "success": true,
  "message": "Skill unassigned successfully"
}
```

**Error Responses:**
- `400` - Skill not assigned or invalid type
- `404` - Skill or subagent not found
- `500` - Database error

### PUT `/api/projects/{project_id}/subagents/{subagent_id}/skills`

Set all skills for a subagent (replaces existing assignments).

**Query Parameters:**
- `subagent_kind` (optional): `"default"` or `"custom"`, defaults to `"default"`

**Request Body:**
```json
{
  "skill_ids": [5, 8, 12],
  "skill_types": ["default", "default", "custom"]
}
```

**Process:**
1. Removes all existing skill assignments
2. Creates new assignments for provided skills
3. Updates subagent markdown file with all skill instructions
4. Synchronizes skill files to `.claudetask/agents/{subagent}/skills/`

**Response:**
```json
[
  {
    "id": 1,
    "skill_id": 5,
    "skill_type": "default",
    "skill_name": "merge-skill",
    "skill_description": "Expert Git merge and conflict resolution",
    "skill_category": "git",
    "assigned_at": "2025-11-25T10:00:00Z"
  },
  {
    "id": 2,
    "skill_id": 8,
    "skill_type": "default",
    "skill_name": "python-refactor",
    "skill_description": "Clean Architecture refactoring for Python",
    "skill_category": "refactoring",
    "assigned_at": "2025-11-25T10:00:00Z"
  },
  {
    "id": 3,
    "skill_id": 12,
    "skill_type": "custom",
    "skill_name": "graphql-optimization",
    "skill_description": "GraphQL query optimization techniques",
    "skill_category": "performance",
    "assigned_at": "2025-11-25T10:00:00Z"
  }
]
```

**Skill File Synchronization:**

When skills are assigned, the system automatically:
1. Copies skill markdown files to `.claudetask/agents/{subagent_name}/skills/`
2. Updates agent's AGENT.md file to include skill instructions
3. Creates skill reference section in agent markdown

Example agent file structure after skill assignment:
```
.claudetask/agents/backend-architect/
├── AGENT.md                    # Agent instructions with skill references
├── skills/
│   ├── merge-skill/
│   │   ├── SKILL.md
│   │   ├── docs/
│   │   └── examples/
│   └── python-refactor/
│       ├── SKILL.md
│       ├── reference/
│       └── templates/
```

**Error Responses:**
- `400` - Invalid skill IDs or mismatched array lengths
- `404` - Skill or subagent not found
- `500` - Database or file system error

### Skills Assignment Workflow

```
[Select Skills in UI]
        ↓
PUT /subagents/{id}/skills
        ↓
[Clear existing assignments]
        ↓
[Create new assignments in DB]
        ↓
[Copy skill files to agent folder]
        ↓
[Update agent markdown with skills]
        ↓
[Return new assignments]
        ↓
    Skills active for agent
```

## Subagent Categories

Default framework subagents are organized by category:

- **Development** - Frontend, backend, and fullstack developers
- **Analysis** - Business analysts, requirements analysts, context analyzers
- **Testing** - Quality engineers, test automation, web testers
- **Architecture** - System architects, backend/frontend architects
- **DevOps** - Infrastructure, deployment, CI/CD specialists
- **Security** - Security engineers, vulnerability assessment
- **Documentation** - Technical writers, docs generators
- **Quality** - Code reviewers, refactoring experts
- **Performance** - Performance engineers, optimization specialists
- **Custom** - User-defined subagents

## Subagent File Storage

### Default Subagents
- **Source:** `framework-assets/claude-agents/*.md`
- **Database:** `default_subagents` table
- **Registration:** Via `project_subagents` junction table when enabled

### Custom Subagents
- **Database:** `custom_subagents` table
- **Archive:** `.claudetask/agents/*.md` (persistent storage)
- **Created via:** Claude Code CLI `/create-agent` command

## Subagent Status Lifecycle

```
[Create Custom Subagent]
        ↓
    status: "creating"
        ↓
[Background Task: Claude CLI]
        ↓
PATCH /subagents/{id}/status → status: "active"
        ↓
    [Archive to .claudetask/]
        ↓
    [Enable for project]
        ↓
    Ready for delegation
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

### Enable a default subagent
```bash
curl -X POST "http://localhost:3333/api/projects/my-project/subagents/enable/1?subagent_kind=default"
```

### Enable a custom subagent
```bash
curl -X POST "http://localhost:3333/api/projects/my-project/subagents/enable/10?subagent_kind=custom"
```

### Create a custom subagent
```bash
curl -X POST "http://localhost:3333/api/projects/my-project/subagents/create" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "GraphQL Expert",
    "description": "Specialist in GraphQL schema design and optimization"
  }'

# Returns: {"id": 10, "status": "creating", ...}

# Background task will update status automatically when complete
```

### Enable all subagents
```bash
curl -X POST "http://localhost:3333/api/projects/my-project/subagents/enable-all"
```

### Disable all subagents
```bash
curl -X POST "http://localhost:3333/api/projects/my-project/subagents/disable-all"
```

### Mark as favorite
```bash
curl -X POST "http://localhost:3333/api/projects/my-project/subagents/favorites/1?subagent_kind=default"
```

## Integration with Task Delegation

Subagents are used by the Task Coordinator for specialized work:

**Delegation Pattern:**
```markdown
Task tool with frontend-developer:
"Create a responsive navigation menu component.

Requirements:
- Mobile-first design
- Accessibility support
- Material-UI components

Please implement in src/components/Navigation.tsx"
```

**Agent Selection:**
- Coordinator analyzes task type
- Selects appropriate enabled subagent
- Provides task context and requirements
- Subagent executes with specialized knowledge

## Default Framework Subagents

### Development Specialists
- `frontend-developer` - React/TypeScript UI development
- `backend-architect` - FastAPI/Python backend design
- `python-expert` - Python coding and best practices
- `mobile-react-expert` - Mobile-first React development
- `python-api-expert` - RESTful API design and implementation
- `fullstack-developer` - End-to-end feature development

### Analysis Specialists
- `business-analyst` - Requirements gathering and analysis
- `requirements-analyst` - Technical specification creation
- `context-analyzer` - Codebase understanding and analysis
- `root-cause-analyst` - Bug investigation and debugging
- `systems-analyst` - System design and architecture planning

### Architecture Specialists
- `system-architect` - High-level system design
- `backend-architect` - Backend infrastructure planning
- `frontend-architect` - Frontend application structure
- `devops-architect` - Infrastructure and deployment design

### Testing & Quality
- `quality-engineer` - Test strategy and quality assurance
- `web-tester` - Web application testing
- `background-tester` - Service and integration testing
- `fullstack-code-reviewer` - Comprehensive code review

### Specialized Roles
- `security-engineer` - Security analysis and hardening
- `performance-engineer` - Performance optimization
- `technical-writer` - Documentation creation
- `refactoring-expert` - Code quality improvement
- `devops-engineer` - CI/CD and deployment automation
