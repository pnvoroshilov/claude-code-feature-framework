# Skills API Endpoints

## Overview

The Skills API manages both default framework skills and custom user-created skills. Skills are reusable AI agent capabilities that can be enabled per-project.

## Base URL

```
http://localhost:3333/api/projects/{project_id}/skills
```

## Endpoints

### GET `/api/projects/{project_id}/skills`

Get all skills for a project (both enabled and available).

**Response:**
```json
{
  "default_skills": [
    {
      "id": 1,
      "name": "RAG Search",
      "description": "Semantic code search capability",
      "file_name": "rag-search.md",
      "skill_content": "# RAG Search Skill...",
      "is_enabled": true,
      "tags": ["search", "rag"],
      "category": "search",
      "is_favorite": false
    }
  ],
  "custom_skills": [
    {
      "id": 1,
      "name": "Custom Analyzer",
      "description": "Project-specific analysis tool",
      "file_name": "custom-analyzer.md",
      "skill_content": "# Custom Analyzer...",
      "is_enabled": false,
      "status": "active",
      "is_favorite": true
    }
  ]
}
```

### POST `/api/projects/{project_id}/skills/enable/{skill_id}`

Enable a skill by copying it to project's `.claude/skills/` directory.

**Query Parameters:**
- `skill_type` (optional): `"default"` or `"custom"`, defaults to `"default"`

**Process:**
1. Validates skill exists in appropriate table (default_skills or custom_skills)
2. Copies skill file to project's `.claude/skills/` directory
3. Inserts record into `project_skills` junction table
4. Returns enabled skill details

**Request:**
```http
POST /api/projects/my-project/skills/enable/1?skill_type=default
```

**Response:**
```json
{
  "id": 1,
  "name": "RAG Search",
  "description": "Semantic code search capability",
  "file_name": "rag-search.md",
  "skill_content": "# RAG Search Skill...",
  "enabled_at": "2025-11-16T10:30:00Z"
}
```

**Error Responses:**
- `400` - Skill already enabled or invalid skill type
- `404` - Skill not found
- `500` - File system error during copy

### DELETE `/api/projects/{project_id}/skills/disable/{skill_id}`

Disable a skill by removing it from project's `.claude/skills/` directory.

**Query Parameters:**
- `skill_type` (optional): `"default"` or `"custom"`, defaults to `"default"`

**Process:**
1. Validates skill is currently enabled
2. Removes skill file from `.claude/skills/`
3. Removes record from `project_skills` junction table

**Request:**
```http
DELETE /api/projects/my-project/skills/disable/1?skill_type=default
```

**Response:**
```json
{
  "success": true,
  "message": "Skill disabled successfully"
}
```

**Error Responses:**
- `404` - Skill not found or not enabled
- `500` - File system error during removal

### POST `/api/projects/{project_id}/skills/sync-framework`

Synchronize default skills from framework-assets to database.

**Process:**
1. Scans `framework-assets/claude-skills/*.md`
2. Updates existing default skills
3. Inserts new default skills
4. Returns count of synchronized skills

**Response:**
```json
{
  "success": true,
  "message": "Default skills synchronized from framework",
  "skills_synced": 5,
  "skills_updated": 2,
  "skills_added": 3
}
```

### POST `/api/projects/{project_id}/skills`

Create a new custom skill.

**Request Body:**
```json
{
  "name": "My Custom Skill",
  "description": "Description of skill functionality",
  "skill_content": "# My Custom Skill\n\nSkill implementation...",
  "tags": ["custom", "analysis"],
  "category": "analysis"
}
```

**Response:**
```json
{
  "id": 10,
  "name": "My Custom Skill",
  "description": "Description of skill functionality",
  "file_name": "my-custom-skill.md",
  "skill_content": "# My Custom Skill...",
  "status": "draft",
  "created_at": "2025-11-16T10:30:00Z"
}
```

**Status Values:**
- `draft` - Initial creation state
- `active` - Skill is complete and ready to use
- `error` - Creation failed with error

### PATCH `/api/projects/{project_id}/skills/{skill_id}/status`

Update custom skill status and archive it to `.claudetask/custom-skills/`.

**Request Body:**
```json
{
  "status": "active",
  "error_message": null
}
```

**Process:**
1. Updates skill status in `custom_skills` table
2. Archives skill to `.claudetask/custom-skills/{file_name}` for persistence
3. If status is "active", enables the skill automatically

**Use Case:**
This endpoint is called by MCP tools (`mcp__claudetask__update_skill_status`) after skill creation is complete.

**Response:**
```json
{
  "success": true,
  "message": "Skill status updated and archived successfully"
}
```

**Error Responses:**
- `404` - Skill not found
- `500` - Database or file system error

### PUT `/api/projects/{project_id}/skills/{skill_id}/content`

Update custom skill content through UI.

**Request Body:**
```json
{
  "content": "# Updated Skill Content\n\nNew implementation..."
}
```

**Process:**
1. Updates skill content in `custom_skills` table
2. Updates archive in `.claudetask/custom-skills/`
3. If skill is enabled, updates `.claude/skills/` as well

**Use Case:**
This endpoint is called when users edit skill content through the Skills UI page.

**Response:**
```json
{
  "success": true,
  "message": "Skill content updated successfully"
}
```

**Error Responses:**
- `400` - Content is required
- `404` - Skill not found
- `500` - Database or file system error

### PUT `/api/projects/{project_id}/skills/{skill_id}`

Update custom skill metadata (name, description, tags, category).

**Request Body:**
```json
{
  "name": "Updated Skill Name",
  "description": "Updated description",
  "tags": ["updated", "tags"],
  "category": "analysis"
}
```

**Response:**
```json
{
  "id": 10,
  "name": "Updated Skill Name",
  "description": "Updated description",
  "tags": ["updated", "tags"],
  "category": "analysis",
  "updated_at": "2025-11-16T10:35:00Z"
}
```

### DELETE `/api/projects/{project_id}/skills/{skill_id}`

Delete a custom skill.

**Process:**
1. Disables skill if enabled (removes from `.claude/skills/`)
2. Deletes from `custom_skills` table
3. Removes archive from `.claudetask/custom-skills/`

**Response:**
```json
{
  "success": true,
  "message": "Custom skill deleted successfully"
}
```

### POST `/api/projects/{project_id}/skills/{skill_id}/favorite`

Add skill to favorites.

**Response:**
```json
{
  "success": true,
  "message": "Skill added to favorites"
}
```

### DELETE `/api/projects/{project_id}/skills/{skill_id}/favorite`

Remove skill from favorites.

**Response:**
```json
{
  "success": true,
  "message": "Skill removed from favorites"
}
```

## Skill File Storage

### Default Skills
- **Source:** `framework-assets/claude-skills/*.md`
- **Database:** `default_skills` table
- **Active (when enabled):** `{project}/.claude/skills/*.md`

### Custom Skills
- **Database:** `custom_skills` table
- **Archive:** `{project}/.claudetask/custom-skills/*.md` (persistent storage)
- **Active (when enabled):** `{project}/.claude/skills/*.md`

## Skill Status Lifecycle

```
[Create Custom Skill]
        ↓
    status: "draft"
        ↓
[MCP Tool Creates Content]
        ↓
PATCH /skills/{id}/status → status: "active"
        ↓
    [Auto-enable skill]
        ↓
    [Archive to .claudetask/]
        ↓
    Ready to use
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

### Enable a default skill
```bash
curl -X POST "http://localhost:3333/api/projects/my-project/skills/enable/1?skill_type=default"
```

### Enable a custom skill
```bash
curl -X POST "http://localhost:3333/api/projects/my-project/skills/enable/5?skill_type=custom"
```

### Create and activate a custom skill
```bash
# 1. Create skill
curl -X POST "http://localhost:3333/api/projects/my-project/skills" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Code Analyzer",
    "description": "Analyzes code quality",
    "skill_content": "# Code Analyzer\n...",
    "category": "analysis"
  }'

# Returns: {"id": 10, "status": "draft", ...}

# 2. Update status to active (triggers archival and auto-enable)
curl -X PATCH "http://localhost:3333/api/projects/my-project/skills/10/status" \
  -H "Content-Type: application/json" \
  -d '{"status": "active"}'

# Skill is now enabled and archived
```

### Update skill content via UI
```bash
curl -X PUT "http://localhost:3333/api/projects/my-project/skills/10/content" \
  -H "Content-Type: application/json" \
  -d '{"content": "# Updated Skill\n\nNew implementation..."}'
```

## Integration with MCP Tools

Skills are created and managed through MCP tools:

- `mcp__claudetask__create_skill` - Creates draft skill
- `mcp__claudetask__update_skill_status` - Updates status and archives skill
- `mcp__claudetask__enable_skill` - Enables skill for project
- `mcp__claudetask__disable_skill` - Disables skill

These tools call the Skills API endpoints documented above.
