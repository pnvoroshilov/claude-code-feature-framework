# Project Documentation

This directory contains auto-generated and maintained documentation for the Claude Code Feature Framework project.

## Documentation Structure

### `/api/`
API documentation including OpenAPI specifications and endpoint details.

**Endpoints:**
- `endpoints/claude-sessions.md` - Claude Code session management and hook integration API
- `endpoints/skills.md` - Skills management API
- `endpoints/rag-indexing.md` - RAG codebase indexing API

### `/components/`
React component documentation with props, usage examples, and patterns.

**Components:**
- `README.md` - Component index and architecture overview
- `ClaudeSessions.md` - Embedded task session management UI with enhanced message display
- `ClaudeCodeSessions.md` - Native Claude Code session analytics and browsing interface
- `Hooks.md` - Hooks management UI for automated shell command configuration
- `Subagents.md` - Subagent management UI for specialized AI assistants
- `Skills.md` - Skills management interface for extended capabilities

### `/architecture/`
System architecture, design decisions, and database schema.

**Documents:**
- `overview.md` - High-level system architecture
- `hooks-system.md` - Hooks system architecture and script file workflow
- `database-design.md` - Database schema and relationships (to be created)
- `adr/*.md` - Architecture Decision Records (ADRs, to be created)

### `/deployment/`
Setup and deployment guides for local development and production.

**Guides:**
- `database-migrations.md` - Database migration guide and complete history
- `setup.md` - Local development environment setup (to be created)
- `production.md` - Production deployment instructions (to be created)

### `/claudetask/`
ClaudeTask framework documentation and workflow guides.

**Guides:**
- `workflow.md` - Task management workflow (to be created)
- `mcp-integration.md` - MCP tools and integration patterns (to be created)
- `worktree-guide.md` - Git worktree usage for feature development (to be created)

### `/examples/`
Practical usage examples and code snippets.

**Examples:**
- `api-usage.md` - API integration examples (to be created)
- `component-usage.md` - Component usage patterns (to be created)

### `/archive/`
Historical documentation and bug reports (not actively maintained).

## Documentation Maintenance

This documentation is **automatically updated** after every merge to the main branch via:

1. **Hook**: `post-merge-documentation` (framework-assets/claude-hooks/)
2. **Slash Command**: `/update-documentation` (triggered by hook)
3. **Agent**: `documentation-updater-agent` (framework-assets/claude-agents/)

### How It Works

```
Git Push to Main
      ↓
PostToolUse Hook Triggered
      ↓
Parse Git Command (post-push-docs.sh)
      ↓
Check for [skip-hook] Tag
      ↓
URL Encode Project Path
      ↓
Call Backend API (/api/claude-sessions/execute-command)
      ↓
Launch Embedded Claude Session (task_id=0)
      ↓
Execute /update-documentation Command
      ↓
Documentation Updater Agent Analyzes Changes
      ↓
Update/Create/Delete Documentation Files
      ↓
Commit with [skip-hook] Tag
```

### Documentation Principles

- **Single Source of Truth** - No duplicate content across files
- **No Versioning** - Only current state is documented (no v1/, v2/, old/)
- **Auto-Update** - Overwrite existing files with latest information
- **Auto-Create** - Generate docs for new features automatically
- **Auto-Delete** - Remove docs for deleted features

### Manual Updates

To manually trigger documentation update:

```bash
/update-documentation          # Update all documentation
/update-documentation api      # Update only API docs
/update-documentation components # Update only component docs
/update-documentation architecture # Update only architecture docs
/update-documentation deployment # Update only deployment docs
```

## Reading the Documentation

**Recommended Reading Order:**

1. `architecture/overview.md` - Understand the system architecture
2. `deployment/database-migrations.md` - Database schema evolution and migration history
3. `architecture/hooks-system.md` - Hooks system and automation workflow
4. `api/endpoints/claude-sessions.md` - Claude session management API
5. `components/README.md` - UI component architecture
6. `components/ClaudeSessions.md` - Session management interface

## Technology Stack

**Documentation Formats:**
- **Markdown** - All documentation files (.md)
- **OpenAPI 3.0** - API specifications (.yaml, planned)
- **Mermaid** - Diagrams and flowcharts (embedded in markdown)

**Frontend Stack:**
- React 18.x + TypeScript
- Material-UI (MUI) v5
- React Router v6

**Backend Stack:**
- FastAPI (Python)
- SQLAlchemy ORM
- SQLite database
- Pexpect for Claude process management

## Recent Updates

**Latest Changes (2025-11-16):**
- ✅ Enhanced ClaudeSessions UI with color-coded message bubbles
- ✅ Fixed hook-triggered sessions to skip /start-feature command
- ✅ Added task_id=0 support for hook sessions
- ✅ Improved message display formatting and scrolling
- ✅ Updated hooks system documentation with script_file workflow
- ✅ Documented database migration 004 (script_file support)

## Important Notes

**Do NOT:**
- ❌ Manually create versioned documentation (v1/, v2/, old/, archive/)
- ❌ Duplicate content across multiple files
- ❌ Keep documentation for deleted features

**Always:**
- ✅ Update existing files in place (overwrite)
- ✅ Delete documentation when features are removed
- ✅ Maintain single source of truth
- ✅ Document current codebase state only

## Contributing to Documentation

### Automated Updates
Documentation is primarily maintained by the `documentation-updater-agent`, which:
- Analyzes git changes automatically
- Updates relevant documentation files
- Creates new docs for new features
- Removes docs for deleted code

### Manual Updates
If you need to manually update documentation:

1. Edit the relevant `.md` file in `docs/`
2. Follow existing formatting and structure
3. Ensure no duplication with other files
4. Commit with descriptive message
5. The auto-updater will maintain it going forward

### Creating New Documentation
New documentation is automatically created when:
- New API endpoints are added
- New React components are created
- New architectural decisions are made
- New deployment steps are required

## Documentation Quality Standards

**All documentation should include:**
- Clear purpose and overview
- Practical, copy-pasteable examples
- Troubleshooting sections
- Related links and cross-references
- Last updated timestamp

**Code Examples:**
- Must be syntactically correct
- Should be runnable as-is
- Include necessary imports/setup
- Show realistic use cases

**API Documentation:**
- Complete endpoint descriptions
- Request/response examples
- Error response examples
- Authentication requirements (when applicable)
- Rate limiting info (when applicable)

## Troubleshooting Documentation

**If documentation is outdated:**
1. Run `/update-documentation` to trigger auto-update
2. Or manually edit the file and commit
3. Documentation will be updated on next merge to main

**If documentation is missing:**
1. Check if feature exists in codebase
2. Run `/update-documentation` to generate
3. Or manually create following templates in existing files

**If documentation is duplicated:**
1. Identify the authoritative source
2. Delete duplicate files
3. Update cross-references if needed

## Documentation Roadmap

**Planned Documentation:**
- [ ] Complete API OpenAPI 3.0 specification
- [ ] Frontend component library reference
- [ ] Deployment guides (setup.md, production.md)
- [ ] ClaudeTask workflow documentation
- [ ] MCP integration patterns guide
- [ ] Git worktree workflow guide
- [ ] Architecture decision records (ADRs)
- [ ] Database schema documentation
- [ ] Performance optimization guides

**Documentation Metrics:**
- Total files: 15 active, 3 archived
- API endpoints documented: 3
- Components documented: 2
- Last full update: 2025-11-16
- Auto-update status: Active and operational

---

**Documentation System Status:** ✅ Active
**Last Auto-Update:** 2025-11-16
**Auto-Update Trigger:** Post-merge hook with [skip-hook] prevention
**Maintainer:** documentation-updater-agent
