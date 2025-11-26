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
- `endpoints/settings.md` - Project settings API for configuration management
- `endpoints/skills.md` - Skills management API with bulk operations
- `endpoints/hooks.md` - Hooks management API with bulk operations
- `endpoints/subagents.md` - Subagents management API for specialized AI assistants
- `endpoints/mcp-configs.md` - MCP server configuration management API
- `endpoints/rag-indexing.md` - RAG codebase indexing API

### `/components/`
React component documentation with props, usage examples, and patterns.

**Components:**
- `README.md` - Component index and architecture overview
- `FileBrowser.md` - GitHub-style file browser with complete file management and layout stability (v2.0.1)
- `RealTerminal.md` - Terminal interface with WebSocket buffering and smart scroll management (v2.1)
- `ClaudeSessions.md` - Embedded task session management UI with structured content rendering (v2.1)
- `ClaudeCodeSessions.md` - Native Claude Code session analytics and browsing interface
- `Sessions.md` - Unified Sessions page with Claude Code and Task sessions (v2.0)
- `Hooks.md` - Hooks management UI for automated shell command configuration
- `Subagents.md` - Subagent management UI for specialized AI assistants
- `Skills.md` - Skills management interface for extended capabilities
- `MCPConfigs.md` - MCP server configuration management interface
- `TaskBoard.md` - Task board with manual/AUTO mode toggle
- `ProjectModeToggle.md` - Project mode switching between SIMPLE and DEVELOPMENT workflows

### `/architecture/`
System architecture, design decisions, and database schema.

**Documents:**
- `overview.md` - High-level system architecture
- `intelligent-workflow.md` - Complete intelligent development workflow with agents and slash commands
- `modular-instructions.md` - Modular instruction system architecture
- `hooks-system.md` - Hooks system architecture and script file workflow
- `framework-updates.md` - Framework update system and file synchronization
- `project-modes.md` - SIMPLE vs DEVELOPMENT mode workflows

### `/deployment/`
Setup and deployment guides for local development and production.

**Guides:**
- `database-migrations.md` - Database migration guide and complete history

### `/claudetask/`
ClaudeTask framework documentation and workflow guides.

**Guides:**
- `slash-commands.md` - Complete slash command reference with examples

### `/skills/`
Claude Code skills documentation for extended capabilities.

**Skills:**
- `README.md` - Skills overview and usage guide
- `skills-system.md` - Complete skills system architecture and available skills (21 default skills including testing suite)
- `toon-format.md` - TOON Format skill for token-efficient data serialization
- `usecase-writer.md` - UseCase Writer skill for requirements documentation

### `/features/`
Core framework features and capabilities.

**Features:**
- `memory-system.md` - Project memory and conversation persistence with ChromaDB
- `auto-mode.md` - Autonomous task execution workflow (AUTO mode)

### `/guides/`
Step-by-step guides for specific tasks.

**Guides:**
- `local-worktree-merge.md` - Merging task changes without remote repository

### `/archive/`
Historical documentation and bug reports (not actively maintained).

**Archived Documents:**
- `MCP_CONFIG_NORMALIZATION_FIX.md` - Historical MCP config fix
- `MCP_SEARCH_PAGINATION_FIX.md` - Historical search pagination fix
- `MCP_SEARCH_COMPLETE_FIX.md` - Historical search completion fix

## Consolidated Documentation

The following standalone files have been documented within the main structure:

- **Testing Mode Configuration**: See `/architecture/project-modes.md` and `/features/auto-mode.md`
- **Manual Mode Toggle**: See `/components/TaskBoard.md` and `/features/auto-mode.md`
- **MCP Project ID Auto-Detection**: See `/architecture/framework-updates.md` and `/api/mcp-tools.md`

## Documentation Maintenance

### Automatic Updates

Documentation is automatically updated via the post-merge documentation hook:

1. **Trigger**: Git push to main branch
2. **Hook**: `post-merge-documentation` (PostToolUse event)
3. **Agent**: Documentation Updater agent
4. **Scope**: Comprehensive update of all affected documentation
5. **Commit**: Auto-commits with `[skip-hook]` tag to prevent recursion

### Update Workflow

```
Code Changes → Git Push → Hook Triggered → API Call → Claude Session → Update Docs → Auto-Commit
```

### Hook Configuration

```json
{
  "PostToolUse": [{
    "matcher": "tool==='Bash' && args.command.includes('git push')",
    "hooks": [{
      "type": "Custom",
      "script_file": ".claude/hooks/post-push-docs.sh"
    }]
  }]
}
```

### Manual Updates

To manually trigger documentation updates:

```bash
# Via Claude Code slash command
/update-documentation

# Via backend API
curl -X POST "http://localhost:3333/api/claude-sessions/execute-command?command=/update-documentation"
```

## Documentation Standards

### File Organization

- **Single Source of Truth**: Each concept documented in ONE place only
- **No Versioning**: Only current documentation state (no v1, v2, old/ directories)
- **No Duplication**: Reference other docs instead of duplicating content
- **Clean Structure**: Clear hierarchy and logical grouping

### Content Guidelines

- **Markdown Format**: All documentation in `.md` files
- **Code Examples**: Working, copy-pasteable examples
- **API Specs**: OpenAPI 3.0 format for all APIs
- **Timestamps**: Update "Last Updated" dates on changes
- **Links**: Use relative paths for internal documentation links

### Update Strategy

- **UPDATE**: Overwrite existing files when content changes
- **CREATE**: New documentation for new features/components
- **DELETE**: Remove documentation for deleted features
- **CONSOLIDATE**: Merge duplicate content into canonical location

## Quick Links

### Getting Started
- [Project README](../README.md) - Installation and quick start
- [Architecture Overview](./architecture/overview.md) - System architecture
- [API Tools Reference](./api/mcp-tools.md) - Complete MCP command reference

### Core Features
- [Memory System](./features/memory-system.md) - Persistent project memory with RAG
- [AUTO Mode](./features/auto-mode.md) - Autonomous task execution
- [Hooks System](./architecture/hooks-system.md) - Automated shell command hooks
- [Skills System](./skills/skills-system.md) - Modular knowledge modules

### Development Guides
- [Slash Commands](./claudetask/slash-commands.md) - Complete command reference
- [Database Migrations](./deployment/database-migrations.md) - Schema evolution guide
- [Local Worktree Merge](./guides/local-worktree-merge.md) - No-remote workflow

### API Reference
- [Claude Sessions API](./api/endpoints/claude-sessions.md) - Session management
- [Hooks API](./api/endpoints/hooks.md) - Hook configuration
- [Skills API](./api/endpoints/skills.md) - Skills management
- [RAG Indexing API](./api/endpoints/rag-indexing.md) - Codebase indexing

### UI Components
- [TaskBoard](./components/TaskBoard.md) - Task management interface
- [ClaudeSessions](./components/ClaudeSessions.md) - Embedded sessions
- [FileBrowser](./components/FileBrowser.md) - GitHub-style file browser
- [Hooks Management](./components/Hooks.md) - Hooks UI

---

**Documentation Version**: 2.6
**Last Updated**: 2025-11-26
**Total Documents**: 44
**Auto-Updated**: Yes (via post-merge hook)
**Status**: Current

**Latest Changes (v2.6)**:
- **Agent Skills Integration**: All agents now include mandatory `skills` field in frontmatter and MANDATORY skills section for consistent knowledge access
- **Workflow Simplification**: Confirmed 6-column DEVELOPMENT workflow (PR status merged into Code Review as of 2025-11-26)
- **Testing Skills Suite**: Comprehensive testing skills - Unit Testing, Integration Testing, UI Testing (with Playwright MCP configuration)
- **Refactoring Skills**: Python Refactor, React Refactor skills with Clean Architecture and SOLID principles
- **Merge Skill**: Comprehensive Git merge best practices for conflict resolution and worktree merging
- **Memory File Edit Capture**: New hook for automatically capturing file edit operations (Edit, Write, MultiEdit, Update tools)
- **Session Security**: Session ID validation (UUID format), pagination limits (max 100 per page), enhanced security
- **Memory System**: Centralized ChromaDB storage, improved session tracking, reduced summarization threshold to 30 messages
- **Skills Total**: 24 default skills (21 existing + UI Testing, Python Refactor, React Refactor)
