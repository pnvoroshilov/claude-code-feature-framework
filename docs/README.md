# Project Documentation

This directory contains auto-generated and maintained documentation for the Claude Code Feature Framework project.

## 📁 Documentation Structure

### `/api/`
API documentation including OpenAPI specifications and endpoint details.
- `api-specification.yaml` - Complete OpenAPI 3.0 specification
- `endpoints/*.md` - Detailed documentation for individual API endpoints
  - `claude-sessions.md` - Claude Code session management and hook integration API

### `/components/`
React component documentation with props, usage examples, and patterns.
- `README.md` - Component index and overview
- `[ComponentName].md` - Individual component documentation

### `/architecture/`
System architecture, design decisions, and database schema.
- `overview.md` - High-level system architecture
- `database-design.md` - Database schema and relationships
- `hooks-system.md` - Hooks system architecture and script file workflow
- `adr/*.md` - Architecture Decision Records (ADRs)

### `/deployment/`
Setup and deployment guides for local development and production.
- `setup.md` - Local development environment setup
- `production.md` - Production deployment instructions
- `database-migrations.md` - Database migration guide and history

### `/claudetask/`
ClaudeTask framework documentation and workflow guides.
- `workflow.md` - Task management workflow
- `mcp-integration.md` - MCP tools and integration patterns
- `worktree-guide.md` - Git worktree usage for feature development

### `/examples/`
Practical usage examples and code snippets.
- `api-usage.md` - API integration examples
- `component-usage.md` - Component usage patterns

## 🔄 Documentation Maintenance

This documentation is **automatically updated** after every merge to the main branch via:

1. **Hook**: `post-merge-documentation` (framework-assets/claude-hooks/)
2. **Command**: `/update-documentation` (framework-assets/claude-commands/)
3. **Agent**: `documentation-updater-agent` (framework-assets/claude-agents/)

### Documentation Principles

✅ **Single Source of Truth** - No duplicate content
✅ **No Versioning** - Only current state is documented
✅ **Auto-Update** - Overwrite existing files with latest information
✅ **Auto-Create** - Generate docs for new features
✅ **Auto-Delete** - Remove docs for deleted features

### Manual Updates

To manually trigger documentation update:
```bash
/update-documentation          # Update all documentation
/update-documentation api      # Update only API docs
/update-documentation components # Update only component docs
```

## 📖 Reading the Documentation

Start with:
1. `architecture/overview.md` - Understand the system
2. `deployment/setup.md` - Set up development environment
3. `deployment/database-migrations.md` - Database schema evolution
4. `architecture/hooks-system.md` - Hooks system and automation
5. `api/endpoints/claude-sessions.md` - Claude session management API
6. `api/api-specification.yaml` - Browse available APIs
7. `components/README.md` - Explore UI components
8. `claudetask/workflow.md` - Learn task management workflow

## 🔧 Technology Stack

Documentation formats:
- **Markdown** - All documentation files
- **OpenAPI 3.0** - API specifications
- **YAML** - Structured API definitions

## ⚠️ Important Notes

1. **Do NOT manually version** - No `v1/`, `v2/`, `old/` directories
2. **Do NOT duplicate** - Each topic documented once
3. **Auto-maintained** - Files are auto-updated/created/deleted
4. **Current state only** - Documentation reflects current codebase

---

Last auto-update: This file manually created
Documentation system: Active and operational
