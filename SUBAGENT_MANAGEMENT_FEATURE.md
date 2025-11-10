# Subagent Management Feature

## Overview

The Subagent Management feature provides a comprehensive UI for managing Claude Code Task tool subagents. This feature allows users to:
- View and enable/disable default subagents
- Create custom subagents
- Manage subagent configurations per project
- Browse subagents by category (Development, Analysis, Testing, etc.)

## Architecture

The feature follows the same architectural patterns as Skills and MCP Configs:

### Database Models (`claudetask/backend/app/models.py`)

1. **DefaultSubagent** - Framework-provided subagents
   - Maps to Claude Code Task tool agent types (e.g., `frontend-developer`, `backend-architect`)
   - Contains metadata: name, description, category, tools_available, recommended_for

2. **CustomSubagent** - User-created custom subagents
   - Project-specific custom agent configurations
   - Includes config field for agent instructions/prompts

3. **ProjectSubagent** - Junction table
   - Links projects to enabled subagents (both default and custom)
   - Tracks when and by whom subagents were enabled

### Backend Services

**SubagentService** (`claudetask/backend/app/services/subagent_service.py`)
- `get_project_subagents()` - Get all subagents organized by type
- `enable_subagent()` - Enable a subagent for a project
- `disable_subagent()` - Disable a subagent
- `create_custom_subagent()` - Create and auto-enable custom subagent
- `delete_custom_subagent()` - Delete custom subagent

### API Endpoints

**Router** (`claudetask/backend/app/routers/subagents.py`)

```
GET    /api/projects/{project_id}/subagents/              - Get all subagents
POST   /api/projects/{project_id}/subagents/enable/{id}   - Enable subagent
POST   /api/projects/{project_id}/subagents/disable/{id}  - Disable subagent
POST   /api/projects/{project_id}/subagents/create        - Create custom
DELETE /api/projects/{project_id}/subagents/{id}          - Delete custom
```

### Frontend UI

**Component** (`claudetask/frontend/src/pages/Subagents.tsx`)

Features:
- Filter view: All, Default, Custom, Enabled
- Subagent cards with category badges and type indicators
- Toggle switches for enable/disable
- Create custom subagent dialog with full configuration
- View details dialog showing tools and recommendations
- Delete confirmation for custom subagents

**Navigation**
- Added to Sidebar with SmartToy icon
- Route: `/subagents`

## Default Subagents (21 pre-configured)

### Development (5)
- **Frontend Developer** - React, TypeScript, Material-UI specialist
- **Backend Architect** - Reliable backend systems design
- **Python Expert** - Production-ready Python code
- **Python API Expert** - FastAPI specialist
- **Mobile React Expert** - Mobile-first React development

### Analysis (5)
- **Business Analyst** - Requirements and stakeholder needs
- **Systems Analyst** - System design and architecture
- **Requirements Analyst** - Transform ideas into specifications
- **Root Cause Analyst** - Problem investigation
- **Context Analyzer** - RAG-powered codebase search

### Architecture (2)
- **System Architect** - Scalable system design
- **Frontend Architect** - UI architecture and patterns

### Testing & Quality (2)
- **Quality Engineer** - Testing strategies and QA
- **Web Tester** - E2E and browser automation

### DevOps (2)
- **DevOps Engineer** - CI/CD and infrastructure
- **DevOps Architect** - Infrastructure design

### Quality (2)
- **Refactoring Expert** - Code quality and refactoring
- **Fullstack Code Reviewer** - Comprehensive code review

### Documentation (2)
- **Technical Writer** - Technical documentation
- **Docs Generator** - Auto-generated documentation

### Security (1)
- **Security Engineer** - Vulnerability detection and compliance

### Performance (1)
- **Performance Engineer** - Performance optimization

## Installation & Setup

### 1. Run Database Migration

```bash
cd claudetask/backend
python migrate_subagents.py
```

This creates three new tables:
- `default_subagents`
- `custom_subagents`
- `project_subagents`

### 2. Start Backend Server

```bash
cd claudetask/backend
python -m uvicorn app.main:app --reload --port 3333
```

On startup, the server will automatically:
- Initialize database tables
- Seed 21 default subagents (if not already seeded)

### 3. Start Frontend

```bash
cd claudetask/frontend
npm start
```

Frontend will be available at `http://localhost:3000`

### 4. Access Subagent Management

Navigate to **Subagents** in the sidebar or go to `http://localhost:3000/subagents`

## Usage Guide

### Viewing Subagents

1. Navigate to the Subagents page
2. Use filter buttons to view:
   - **All** - All available subagents
   - **Default** - Framework-provided subagents
   - **Custom** - User-created subagents
   - **Enabled** - Currently enabled subagents

### Enabling/Disabling Subagents

1. Find the subagent card
2. Toggle the switch to enable/disable
3. Enabled subagents are available for use in Claude Code Task tool

### Creating Custom Subagents

1. Click **"Create Custom Subagent"** button
2. Fill in the form:
   - **Name** - Unique identifier
   - **Description** - What the subagent does
   - **Category** - Select from predefined categories
   - **Subagent Type** - The type identifier used in Task tool
   - **Configuration** - Agent instructions in markdown format
   - **Available Tools** - Comma-separated list of tools (optional)
3. Click **Create**
4. Custom subagent is automatically enabled after creation

### Viewing Subagent Details

1. Click the info icon (ⓘ) on any subagent card
2. View dialog shows:
   - Full description
   - Subagent type identifier
   - Available tools (as chips)
   - Recommended use cases
   - Status and creation date

### Deleting Custom Subagents

1. Click the delete icon on a custom subagent card
2. Confirm deletion
3. Note: Default subagents cannot be deleted

## Data Model

### DefaultSubagent

```python
id: int
name: str (unique)
description: str
category: str (Development, Analysis, Testing, etc.)
subagent_type: str (e.g., "frontend-developer")
tools_available: JSON (list of tool names)
recommended_for: JSON (list of use cases)
is_active: bool
created_at: datetime
updated_at: datetime
```

### CustomSubagent

```python
id: int
project_id: str (FK)
name: str
description: str
category: str
subagent_type: str
config: str (markdown instructions)
tools_available: JSON
status: str (active/creating/failed)
error_message: str
created_by: str
created_at: datetime
updated_at: datetime
```

### ProjectSubagent (Junction)

```python
id: int
project_id: str (FK)
subagent_id: int
subagent_type: str (default/custom)
enabled_at: datetime
enabled_by: str
```

## Integration with Claude Code

The subagent_type field maps directly to Claude Code Task tool agent types:

```python
# Example: Using enabled subagents in Task tool
Task tool with subagent_type="frontend-developer":
"Create a React component for user authentication"

Task tool with subagent_type="backend-architect":
"Design API endpoints for user management system"
```

## API Response Format

### SubagentsResponse

```json
{
  "enabled": [
    {
      "id": 1,
      "name": "Frontend Developer",
      "description": "React TypeScript specialist...",
      "subagent_kind": "default",
      "subagent_type": "frontend-developer",
      "category": "Development",
      "tools_available": ["Read", "Write", "Edit", "Bash"],
      "recommended_for": ["UI components", "React development"],
      "is_enabled": true,
      "created_at": "2024-01-01T00:00:00",
      "updated_at": "2024-01-01T00:00:00"
    }
  ],
  "available_default": [...],
  "custom": [...]
}
```

## File Structure

```
claudetask/
├── backend/
│   ├── app/
│   │   ├── models.py                    # + DefaultSubagent, CustomSubagent, ProjectSubagent
│   │   ├── schemas.py                   # + Subagent schemas
│   │   ├── database.py                  # + seed_default_subagents()
│   │   ├── main.py                      # + subagents router, seed call
│   │   ├── routers/
│   │   │   └── subagents.py            # NEW: Subagent API endpoints
│   │   └── services/
│   │       └── subagent_service.py     # NEW: Subagent business logic
│   └── migrate_subagents.py            # NEW: Database migration script
└── frontend/
    └── src/
        ├── pages/
        │   └── Subagents.tsx            # NEW: Subagent management UI
        ├── components/
        │   └── Sidebar.tsx              # + Subagent menu item
        └── App.tsx                      # + Subagent route
```

## Testing

### Manual Testing Checklist

- [ ] View all subagents on page load
- [ ] Filter by Default, Custom, Enabled
- [ ] Enable a default subagent
- [ ] Disable a subagent
- [ ] Create a custom subagent
- [ ] View subagent details dialog
- [ ] Delete a custom subagent
- [ ] Verify enabled subagents persist after page refresh
- [ ] Test with multiple projects (isolation check)

### API Testing

```bash
# Get all subagents for project
curl http://localhost:3333/api/projects/{project_id}/subagents/

# Enable a default subagent
curl -X POST http://localhost:3333/api/projects/{project_id}/subagents/enable/1?subagent_kind=default

# Create custom subagent
curl -X POST http://localhost:3333/api/projects/{project_id}/subagents/create \
  -H "Content-Type: application/json" \
  -d '{
    "name": "My Custom Agent",
    "description": "Custom agent description",
    "category": "Development",
    "subagent_type": "my-custom-agent",
    "config": "# Agent Instructions\nDo amazing things...",
    "tools_available": ["Read", "Write", "Bash"]
  }'
```

## Future Enhancements

- [ ] Subagent usage analytics
- [ ] Import/export subagent configurations
- [ ] Subagent templates marketplace
- [ ] Version control for custom subagents
- [ ] Team sharing of custom subagents
- [ ] Subagent performance metrics
- [ ] AI-assisted subagent creation
- [ ] Integration with Claude Code context menu

## Troubleshooting

### Migration Issues

If tables already exist, the migration script will skip creation.
To force recreation:
```bash
# Backup database first!
sqlite3 data/claudetask.db ".backup backup.db"

# Drop tables
sqlite3 data/claudetask.db "DROP TABLE IF EXISTS project_subagents;"
sqlite3 data/claudetask.db "DROP TABLE IF EXISTS custom_subagents;"
sqlite3 data/claudetask.db "DROP TABLE IF EXISTS default_subagents;"

# Re-run migration
python migrate_subagents.py
```

### Seed Data Not Loading

Check backend logs on startup:
```bash
# Should see:
# "Seeded 21 default subagents"
# "Subagents: Frontend Developer, Backend Architect, ..."
```

If not seeded, manually trigger:
```python
from app.database import seed_default_subagents
import asyncio
asyncio.run(seed_default_subagents())
```

### Frontend Not Loading

1. Check backend is running on port 3333
2. Verify REACT_APP_API_URL environment variable
3. Check browser console for API errors
4. Verify CORS settings in backend main.py

## Contributing

When adding new default subagents:

1. Add to `seed_default_subagents()` in `database.py`
2. Include all required fields: name, description, category, subagent_type
3. Add tools_available and recommended_for as JSON strings
4. Follow existing naming conventions
5. Update this documentation

## License

Part of the Claude Code Feature Framework
