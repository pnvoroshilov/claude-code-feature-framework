# Project Documentation

This directory contains auto-generated and maintained documentation for the Claude Code Feature Framework project.

## Documentation Structure

### `/api/`
API documentation including OpenAPI specifications and endpoint details.

**Core Documentation:**
- `mcp-tools.md` - Complete MCP tool reference with usage patterns and examples

**Endpoints:**
- `endpoints/claude-sessions.md` - Claude Code session management and hook integration API
- `endpoints/file-browser.md` - File browser API with comprehensive file management (v2.0)
- `endpoints/skills.md` - Skills management API
- `endpoints/rag-indexing.md` - RAG codebase indexing API

### `/components/`
React component documentation with props, usage examples, and patterns.

**Components:**
- `README.md` - Component index and architecture overview
- `FileBrowser.md` - GitHub-style file browser with complete file management and layout stability (v2.0.1)
- `RealTerminal.md` - Terminal interface with WebSocket buffering and smart scroll management (v2.1)
- `ClaudeSessions.md` - Embedded task session management UI with structured content rendering (v2.1)
- `ClaudeCodeSessions.md` - Native Claude Code session analytics and browsing interface
- `Hooks.md` - Hooks management UI for automated shell command configuration
- `Subagents.md` - Subagent management UI for specialized AI assistants
- `Skills.md` - Skills management interface for extended capabilities

### `/architecture/`
System architecture, design decisions, and database schema.

**Documents:**
- `overview.md` - High-level system architecture
- `hooks-system.md` - Hooks system architecture and script file workflow
- `framework-updates.md` - Framework update system and file synchronization
- `project-modes.md` - SIMPLE vs DEVELOPMENT mode workflows
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

### `/skills/`
Claude Code skills documentation for extended capabilities.

**Skills:**
- `README.md` - Skills overview and usage guide
- `toon-format.md` - TOON Format skill for token-efficient data serialization
- `usecase-writer.md` - UseCase Writer skill for requirements documentation

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
3. `architecture/framework-updates.md` - Framework update system and file synchronization
4. `api/mcp-tools.md` - MCP tool reference and usage patterns
5. `architecture/hooks-system.md` - Hooks system and automation workflow
6. `api/endpoints/claude-sessions.md` - Claude session management API
7. `components/README.md` - UI component architecture
8. `components/ClaudeSessions.md` - Session management interface

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

**Latest Changes (2025-11-20):**
- ✅ **New Hook: Documentation Update Injection**: UserPromptSubmit event hook for automatic recovery
  - Companion to Post-Merge Documentation hook
  - Detects pending documentation update markers
  - Injects /update-documentation command into next user prompt
  - One-time trigger with automatic cleanup
  - Provides fallback when API calls fail
  - Documentation: `architecture/hooks-system.md` Case Study 2
- ✅ **Hooks Initialization Change**: Hooks no longer auto-enabled on project creation
  - All hook scripts (.sh files) copied to .claude/hooks/ during initialization
  - Scripts made executable automatically
  - Empty .claude/settings.json created (no hooks enabled by default)
  - Users enable hooks via UI as needed
  - Prevents unwanted automation on new projects
- ✅ **Framework Update System**: Automatic synchronization of framework files
  - Updates hooks, commands, and agents in existing projects
  - Preserves user customizations while updating framework components
  - Updates hook scripts (.sh files) during framework sync
  - Preserves .claude/settings.json (user's enabled hooks)
  - Merges MCP configurations intelligently
  - New documentation: `architecture/framework-updates.md`
- ✅ **Database Migration 006**: CASCADE DELETE constraints for project deletion
  - Automatic cascade deletion of all related records
  - Orphaned record cleanup during migration
  - Safer and simpler project deletion
- ✅ **Database Migration 005**: Worktree toggle support
  - Per-project worktree enable/disable
  - Dynamic CLAUDE.md generation based on setting
  - UI toggle in ProjectModeToggle component
- ✅ **MCP get_project_settings Tool**: Dynamic project configuration access
  - Read project mode (simple vs development)
  - Check worktree_enabled status
  - Access custom instructions dynamically
  - Single source of truth in database
- ✅ **Project Initialization**: Increased timeout to 30 seconds
  - Accommodates directory trust initialization
  - Better handling of Claude session startup
- ✅ **RealTerminal v2.1**: WebSocket buffering and smart scroll management
  - User scroll detection prevents auto-scroll interruption
  - Buffered output writes reduce scroll jumping
  - Extended scrollback buffer (10,000 lines)
- ✅ **New Skills Added**: TOON Format and UseCase Writer as framework defaults
  - TOON Format: Token-efficient data serialization (30-60% token savings)
  - UseCase Writer: Professional requirements documentation (UML, Cockburn, IEEE 830)
- ✅ **TaskBoard Enhancement**: File Browser navigation link added to header
- ✅ **Mode Switch**: Project switched from SIMPLE to DEVELOPMENT mode
- ✅ **Documentation Cleanup**: Removed 30+ obsolete documentation files

**Previous Changes (2025-11-19):**
- ✅ **FileBrowser v2.0.1**: UI/UX refinements and layout stability improvements
  - Increased breadcrumb maxWidth from 80px to 200px for significantly better visibility
  - Fixed editor panel layout to prevent full-width expansion on first file open
  - Added null check for selectedFile in Editor component to prevent TypeScript errors
  - Improved delete operation with proper null safety (captures deleted path before clearing dialog)
  - Enhanced paste operations with auto-generated unique names to prevent file conflicts
  - Improved header button alignment and visibility
  - Replaced conditional rendering with visibility toggles to prevent layout shifts
  - Added minimum width to button container for stable layout
  - Fixed breadcrumb overflow handling with proper truncation
  - Ensured file action buttons never wrap or disappear
  - Added comprehensive layout documentation with best practices

**Previous Changes (2025-11-18):**
- ✅ **FileBrowser v2.0**: Comprehensive file management system
  - Create files and directories with modal dialogs
  - Rename files and directories with validation
  - Delete files and directories with confirmation
  - Copy/paste files and directories with clipboard support
  - Context menu for right-click operations
  - Auto-generated unique names for paste operations
  - Enhanced API with 4 new endpoints: create, rename, delete, copy
- ✅ **API v2.0**: File management endpoints
  - `POST /files/create` - Create files and directories
  - `POST /files/rename` - Rename/move files and directories
  - `POST /files/delete` - Delete files and directories
  - `POST /files/copy` - Copy files and directories

**Earlier Updates (2025-11-16):**
- ✅ **Enhanced ClaudeSessions UI v2.1**: Structured content rendering for Claude API format
- ✅ Fixed hook-triggered sessions to skip /start-feature command
- ✅ Added task_id=0 support for hook sessions
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
- Total files: 23 active, 3 archived
- API endpoints documented: 4 (including 8 total endpoints)
- MCP tools documented: 15+ tools with complete reference
- Components documented: 7 (FileBrowser, RealTerminal, ClaudeSessions, etc.)
- Hooks documented: 8 framework hooks (including inject-docs-update)
- Skills documented: 2 (TOON Format, UseCase Writer)
- Database migrations documented: 7 complete migrations (including hook sync)
- Last full update: 2025-11-20 22:30
- Auto-update status: Active and operational

---

**Documentation System Status:** ✅ Active
**Last Auto-Update:** 2025-11-20
**Auto-Update Trigger:** Post-merge hook with [skip-hook] prevention
**Maintainer:** documentation-updater-agent
