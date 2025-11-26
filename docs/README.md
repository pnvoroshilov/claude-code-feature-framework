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
- `ClaudeCodeSessions.md` - Native Claude Code session analytics with LIVE badge indicators and pagination (v2.3.1)
- `Sessions.md` - Unified Sessions page with embedded session support and enhanced error handling (v2.2.1)
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
- `agent-skills-system.md` - Agent skills integration with mandatory skill invocation (34 agents updated)

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
- `session-continuation.md` - Session continuation with full conversation context (NEW v2.1)

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
- [Session Continuation](./features/session-continuation.md) - Resume sessions with full context
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

**Documentation Version**: 2.10.0
**Last Updated**: 2025-11-26
**Total Documents**: 47
**Auto-Updated**: Yes (via post-merge hook)
**Status**: Current

**Latest Changes (v2.10.0)**:
- **NEW: Architecture Mindset Skill**: Principal Architect/CTO-level thinking framework (commit 00c6e0b57)
  - Five Pillars of Architectural Truth (trade-offs, pessimism, data gravity, simplicity, Conway's Law)
  - Interrogation Engine for requirements discovery
  - Trade-off analysis framework with comparison matrices
  - Failure mode design patterns and mitigations
  - Reference documentation files for deep dives
  - Integration with other skills (architecture-patterns, code-review, requirements-analysis)
- **NEW: Unified Projects Page**: Tabbed interface for project management (commit a3a75b909)
  - Three tabs: Projects (list), Instructions (CLAUDE.md editor), Setup (new project wizard)
  - URL-based tab navigation with clean routing
  - ProjectListView with context menu actions
  - Framework update functionality per project
  - Project editing and deletion capabilities
- **Skills System Update**: Total of 11 default skills (up from 10)
  - Architecture Mindset (NEW)
  - Architecture Patterns (enhanced)
  - Unit Testing, Integration Testing, UI Testing
  - Security Best Practices, Python Refactor, React Refactor
  - Merge Skill, Requirements Analysis, Technical Design
- **Component Documentation**: New Projects component documented (v1.0)
- **Agent Updates**: All 34 agents include Skill tool for proper skill loading (commit 2806059f9)

**Previous Changes (v2.9.2)**:
- **Embedded Sessions Cleanup**: Removed embedded sessions from System Processes list (commit eee34daec)
  - Embedded sessions (from `real_claude_service`) no longer appear in active sessions API
  - They are internal implementation details without persistent session files
  - Use `/api/sessions/embedded/active` endpoint to monitor them separately
  - Prevents session details loading failures and duplicate entries
- **Hook Session Handling**: Enhanced UI for hook-triggered sessions (commit 8c8753d58)
  - Frontend gracefully handles `hook-*` sessions without persistent files
  - Shows informative alert with session metadata (PID, project, working directory)
  - Prevents "View Details" errors for embedded hook sessions
- **Session ID Validation**: Enhanced validation to support hook IDs (commits 28cfaac60, 2eb9d5d82)
  - Added `hook-xxxxxxxx` format to valid session ID patterns
  - Validation pattern: `/^(UUID|agent-[a-f0-9]{8}|hook-[a-f0-9]{8})$/`
  - Supports three formats: UUID, agent-ID, and hook-ID
- **Subagent Context Optimization**: CLAUDE.md updated for subagent efficiency (commit 7974d1ebc)
  - Subagents spawned via Task tool skip project context loading
  - Reduces redundant MCP calls when parent session already has context
  - Improves subagent initialization performance

**Previous Changes (v2.9.1)**:
- **Active Sessions Bug Fix**: Fixed API field name in ClaudeCodeSessionsView (v2.3.1)
  - Corrected API response field from `sessions` to `active_sessions`
  - Enhanced error messages with detailed session ID and project information
  - Improved user feedback for failed session detail loads
- **Active Session Visual Indicators**: Prominent "LIVE" badge with pulsing animations (v2.3)
  - Real-time active session detection (5-second polling via `/active-sessions`)
  - Green "LIVE" badge with pulsing white dot on running session cards
  - Green-themed card backgrounds and glowing shadow effects
  - Session ID tracking with Set-based state management
  - Clear visual distinction between active and historical sessions
- **Embedded Session Support**: Enhanced Sessions page with embedded session detection (v2.2)
  - "Embedded" chip for task-based Claude sessions
  - Task ID association display
  - Visual differentiation from standalone sessions
  - Support for agent-ID session format (`agent-xxxxxxxx`)
- **Session ID Validation Enhancement**: Dual format support (UUID + agent-ID)
  - UUID format: `a1b2c3d4-1234-5678-90ab-cdef12345678`
  - Agent ID format: `agent-abc12345`
  - Prevents path traversal attacks with strict pattern matching
- **Documentation Updates**: All session-related documentation updated to v2.2-2.3

**Previous Changes (v2.8)**:
- Agent Skills System Documentation (34 agents with mandatory skills)
- Session Messages Endpoint with JSONL parsing
- Empty Message Filtering (server-side and client-side)
- ClaudeCodeSessions UI Redesign (tabs → single panel)
- Server-side Pagination (20 per page, max 100)
- Path Security and Performance Optimization

**Previous Changes (v2.7)**:
- **Session Messages and Continue Session**: JSONL parsing with security validation
- **ClaudeCodeSessions Pagination**: 20 items per page with server-side limit/offset

**Previous Changes (v2.6)**:
- **Agent Skills Integration**: All agents include mandatory `skills` field and MANDATORY skills section
- **Workflow Simplification**: 6-column DEVELOPMENT workflow (PR merged into Code Review)
- **Testing Skills Suite**: Unit Testing, Integration Testing, UI Testing (Playwright MCP)
- **Refactoring Skills**: Python Refactor, React Refactor with Clean Architecture
- **Session Security**: UUID validation, pagination limits (max 100), enhanced security
- **Skills Total**: 24 default skills
