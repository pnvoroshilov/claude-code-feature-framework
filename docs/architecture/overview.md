# System Architecture Overview

## High-Level Architecture

ClaudeTask Framework is a full-stack task management system designed to streamline development workflows with Claude Code integration. The system follows a modern web application architecture with clear separation between frontend, backend, and integration layers.

```
┌─────────────────────────────────────────────────────────────┐
│                     Frontend (React)                        │
│  - Task Management UI                                       │
│  - Project Configuration                                    │
│  - Hooks & Skills Management                                │
│  - Claude Sessions Monitoring                               │
│  - Cloud Storage Settings                                   │
└──────────────────┬──────────────────────────────────────────┘
                   │ HTTP/REST API
                   │ WebSocket (Real-time updates)
┌──────────────────▼──────────────────────────────────────────┐
│                   Backend (FastAPI)                         │
│  - RESTful API Endpoints                                    │
│  - Business Logic Services                                  │
│  - Repository Pattern (Storage Abstraction)                 │
│  - Database ORM (SQLAlchemy)                                │
│  - Claude Code CLI Integration                              │
└──────────────────┬──────────────────────────────────────────┘
                   │
     ┌─────────────┴─────────────┐
     │                           │
┌────▼────────┐         ┌────────▼──────┐
│ Local       │   OR    │ Cloud         │
│ Storage     │         │ Storage       │
├─────────────┤         ├───────────────┤
│ SQLite      │         │ MongoDB Atlas │
│ ChromaDB    │         │ Vector Search │
│ 384d        │         │ 1024d         │
└─────────────┘         └───────────────┘
        │                       │
        └───────────┬───────────┘
                    │
        ┌───────────▼───────────┐
        │ Claude Code CLI       │
        │ File System (.claude/)│
        └───────────────────────┘
```

## Technology Stack

### Frontend
- **Framework**: React 18 with TypeScript
- **UI Library**: Material-UI (MUI) v5
- **State Management**: React Context API + React Query for server state
- **HTTP Client**: Axios
- **Routing**: React Router v6
- **Code Editor**: Monaco Editor (for file browser, hooks, skills, agents)
- **Markdown Rendering**: react-markdown with GitHub-flavored markdown
- **Syntax Highlighting**: highlight.js for markdown code blocks

### Backend
- **Framework**: FastAPI (Python 3.9+)
- **ORM**: SQLAlchemy 2.0 with async support
- **Database**:
  - **Local**: SQLite (with async SQLite driver)
  - **Cloud**: MongoDB Atlas (Motor async driver)
- **Vector Search**:
  - **Local**: ChromaDB with all-MiniLM-L6-v2 (384d)
  - **Cloud**: MongoDB Vector Search with voyage-3-large (1024d)
- **Storage Pattern**: Repository Pattern for storage abstraction
- **Validation**: Pydantic v2
- **CORS**: FastAPI CORS middleware
- **Background Tasks**: FastAPI BackgroundTasks

### Integration
- **Claude Code CLI**: Command-line interface integration
- **Git Operations**: subprocess-based git workflow
- **File System**: Direct file I/O for .claude/ directory management

## Core Components

### 1. Project Management
- Multi-project workspace support
- Project-specific configuration (CLAUDE.md generation with explicit mode indicators)
- Custom instructions support
- Two modes: SIMPLE and DEVELOPMENT (selected at project creation, immutable)
- Per-project worktree toggle (DEVELOPMENT mode only)
- Dynamic project settings via MCP get_project_settings tool
- Active project tracking
- Automatic directory trust initialization
- CASCADE DELETE constraints for safe project deletion
- CLAUDE.md regeneration script for syncing legacy projects

### 2. Task Management
- Task CRUD operations
- Status workflow tracking
- Git worktree integration (DEVELOPMENT mode)
- Task history and audit trail
- Stage results tracking

### 3. Hooks System
- Default hooks (framework-provided)
- Custom hooks (user-created via Claude)
- Per-project hook enablement via UI
- Favorites system (cross-project)
- Separate script file support for complex hooks
- Automatic settings.json generation from hook configs
- Hook scripts with executable permissions (chmod +x)
- Integration with .claude/settings.json and .claude/settings.local.json
- No auto-enablement during project initialization (user chooses which hooks to enable)
- Post-merge documentation update hook with recursion prevention
- See [Hooks System Documentation](./hooks-system.md)

### 4. Skills System
- Default skills (framework-provided)
- Custom skills (user-created via Claude)
- Per-project skill enablement
- Favorites system (cross-project)
- Integration with .claude/settings.json

### 5. Claude Sessions
- Task-based Claude Code session management
- Session status tracking
- Message history storage
- Session metadata and statistics
- Multiple session modes (terminal, embedded, websocket)

### 6. MCP Configurations
- Default MCP server configurations
- Custom MCP configurations
- Per-project MCP enablement
- Integration with .claude/settings.json

### 7. Framework Update System
- Automatic synchronization of framework files to projects
- Preserves user customizations while updating framework components
- Updates agents, commands, hooks, and CLAUDE.md templates
- MCP configuration merging with preservation of user's custom servers
- Automatic generation of `.claude/settings.json` (empty hooks by default)
- Automatic generation of `.claude/settings.local.json` for MCP server enablement
  - Pre-configured with claudetask, playwright, serena MCP servers
  - enableAllProjectMcpServers flag set to true
- Backup of critical files (CLAUDE.md → CLAUDE.md.backup)
- Hook scripts copied with executable permissions (chmod +x)
- Complete agent refresh to remove deprecated configurations
- See [Framework Updates Documentation](./framework-updates.md)

### 8. Dual Storage System (NEW)
- **Repository Pattern** for storage abstraction
- **Per-project storage mode** selection (local or MongoDB)
- **Local Storage**: SQLite + ChromaDB + all-MiniLM-L6-v2 (384d)
- **Cloud Storage**: MongoDB Atlas + Vector Search + voyage-3-large (1024d)
- **Codebase RAG**: Semantic code search across entire repository (MongoDB only)
- **Migration Tool**: CLI utility for data migration between backends
- **100% Backward Compatible**: All existing projects use local storage by default
- **Cloud Configuration UI**: Settings page for MongoDB Atlas and Voyage AI setup
- See [MongoDB Atlas Storage Documentation](../features/mongodb-atlas-storage.md)

### 9. Project Memory System
- Automatic conversation persistence across sessions
- Project summary generation and maintenance (3-5 pages)
- RAG-based semantic search (ChromaDB for local, Vector Search for cloud)
- Session context loading at startup
- Message indexing with embeddings (model depends on storage mode)
- Historical knowledge retrieval
- Cross-session context preservation
- Automatic memory hooks (enabled by default)
- See [Memory System Documentation](../features/memory-system.md)

### 10. File Browser System
- GitHub-style file browsing interface
- Monaco Editor integration for code editing
- Project-scoped file access
- Security with path traversal protection
- Read and write operations with change detection
- Markdown preview with GitHub-flavored markdown
- Support for 15+ programming languages

## Data Flow

### Task Lifecycle
```
1. User creates task in UI
   ↓
2. Frontend → POST /api/projects/{id}/tasks
   ↓
3. Backend validates and stores in database
   ↓
4. Task appears in TaskBoard (Backlog column)
   ↓
5. User moves to "In Progress"
   ↓
6. (DEVELOPMENT mode) System creates git worktree
   ↓
7. User works on task
   ↓
8. User marks task as Done
   ↓
9. System updates task status and history
```

### Hook Enablement Flow
```
1. User views available hooks in UI
   ↓
2. Frontend → GET /api/projects/{id}/hooks
   ↓
3. Backend fetches default + custom + enabled hooks
   ↓
4. User clicks "Enable" on a hook
   ↓
5. Frontend → POST /api/projects/{id}/hooks/enable/{hook_id}
   ↓
6. Backend merges hook config into .claude/settings.json
   ↓
7. Backend creates project_hooks junction record
   ↓
8. Hook is now active for the project
```

### Claude Session Flow

#### Task-Based Session Flow
```
1. User starts working on a task
   ↓
2. Frontend → POST /api/sessions (create session)
   ↓
3. Backend launches Claude Code CLI with task_id
   ↓
4. Session status: idle → initializing → active
   ↓
5. User interacts with Claude via terminal/embedded mode
   ↓
6. Backend tracks messages and metadata
   ↓
7. User completes task
   ↓
8. Frontend → POST /api/sessions/{id}/complete
   ↓
9. Session status: completed
```

#### Hook-Triggered Session Flow
```
1. Git hook triggers (e.g., post-push)
   ↓
2. Hook script → POST /api/claude-sessions/execute-command
   ↓
3. Backend creates session with task_id=0 (hook session)
   ↓
4. Session initialization: skips /start-feature command
   ↓
5. Backend sends slash command to Claude stdin
   ↓
6. Claude executes command asynchronously
   ↓
7. Session remains active for command execution
   ↓
8. Results saved with [skip-hook] tag to prevent recursion
```

**Key Differences:**
- **Task Sessions** (`task_id > 0`): Include `/start-feature` initialization for task context
- **Hook Sessions** (`task_id = 0`): Skip task initialization, execute only the provided command

### File Browser Flow
```
1. User navigates to project files
   ↓
2. Frontend → GET /api/projects/{id}/files/browse
   ↓
3. Backend validates project access and path security
   ↓
4. Backend reads directory contents (filtered)
   ↓
5. Frontend displays file list with breadcrumbs
   ↓
6. User clicks file to open
   ↓
7. Frontend → GET /api/projects/{id}/files/read?path={file}
   ↓
8. Backend reads file content (UTF-8/Latin-1)
   ↓
9. Frontend loads content into Monaco Editor
   ↓
10. User edits file content
   ↓
11. Frontend → POST /api/projects/{id}/files/save
   ↓
12. Backend validates path and writes file
   ↓
13. Frontend confirms save success
```

**Security Features:**
- **Path Validation**: All paths resolved and checked against project root
- **Size Limits**: 10MB maximum file size prevents memory issues
- **Encoding Support**: UTF-8 primary, Latin-1 fallback
- **Filtered Files**: Hidden files and node_modules automatically excluded

## Database Schema

The system supports dual storage backends with consistent schema across both:

### Local Storage (SQLite)

Main tables:
- **projects**: Project configurations and metadata with CASCADE DELETE constraints
- **tasks**: Task tracking with status, worktree info, stage results, testing URLs
- **task_history**: Audit trail of task status changes
- **claude_sessions**: Claude Code session management
- **default_hooks**: Framework-provided hooks with optional script_file column
- **custom_hooks**: User-created hooks with optional script_file column
- **project_hooks**: Junction table for project-hook enablement
- **default_skills**: Framework-provided skills
- **custom_skills**: User-created skills
- **project_skills**: Junction table for project-skill enablement
- **default_mcp_configs**: Framework-provided MCP configurations
- **custom_mcp_configs**: User-created MCP configurations
- **project_mcp_configs**: Junction table for project-MCP enablement
- **agents**: Subagent configurations
- **project_settings**: Per-project settings including worktree_enabled and **storage_mode** fields
- **conversation_memory**: All conversation messages with metadata
- **project_summaries**: Condensed project knowledge (3-5 pages)
- **memory_rag_status**: RAG indexing tracking
- **memory_sessions**: Session context loading tracking

**New in v2.11**: `project_settings.storage_mode` field determines which storage backend to use.

### Cloud Storage (MongoDB Atlas)

Collections (created automatically):
- **projects**: Same schema as SQLite, using ObjectId
- **tasks**: Same schema as SQLite, with manual cascade delete
- **task_history**: Task status change audit trail
- **conversation_memory**: Messages with 1024d voyage-3-large embeddings
- **project_settings**: Project configuration including storage mode
- **codebase_chunks**: Semantic code chunks with embeddings (NEW v2.11)

**Indexes**:
- Standard indexes on project_id, status, timestamps
- **Vector Search Index** on conversation_memory.embedding (1024 dimensions, cosine similarity)
- **Vector Search Index** on codebase_chunks.embedding (1024 dimensions, cosine similarity)

### Storage Mode Selection

Projects can independently choose storage backend via `project_settings.storage_mode`:
- `"local"` (default): SQLite + ChromaDB
- `"mongodb"`: MongoDB Atlas + Vector Search

See [Database Migrations Documentation](../deployment/database-migrations.md) for complete migration history and [MongoDB Atlas Storage Documentation](../features/mongodb-atlas-storage.md) for cloud storage details.

## API Architecture

### RESTful API Design
All endpoints follow REST conventions:
- `GET` - Retrieve resources
- `POST` - Create resources
- `PUT` - Update resources
- `DELETE` - Remove resources

### Endpoint Organization
```
/api/projects                        # Project management
/api/projects/{id}/tasks             # Task management
/api/projects/{id}/hooks             # Hooks management
/api/projects/{id}/skills            # Skills management
/api/projects/{id}/mcp-configs       # MCP configurations
/api/projects/{id}/subagents         # Subagent management
/api/projects/{id}/instructions      # Custom instructions
/api/projects/{id}/files             # File browser and editor
/api/projects/{id}/memory            # Memory management
/api/sessions                        # Claude sessions
/api/settings/cloud-storage          # Cloud storage configuration (NEW v2.11)
/api/codebase                        # Codebase RAG indexing and search (NEW v2.11)
/api/editor                          # File editor endpoints (legacy)
```

## Security Considerations

### Current Implementation
- CORS enabled for local development (localhost:3000)
- No authentication/authorization (local desktop app)
- File system access restricted to project directories
- SQL injection prevention via SQLAlchemy ORM

### Future Enhancements
- User authentication for multi-user scenarios
- Role-based access control
- API rate limiting
- Enhanced CORS configuration for production

## Deployment Architecture

### Development Mode
```
Frontend: localhost:3000 (React dev server)
Backend:  localhost:3333 (Uvicorn ASGI server)
Database: SQLite file (claudetask/backend/claudetask.db)
```

### Production Considerations
- Frontend: Static build served via nginx/CDN
- Backend: Gunicorn + Uvicorn workers
- Database: PostgreSQL for production scale
- Process management: systemd/supervisor
- Reverse proxy: nginx

## Extension Points

The framework is designed for extensibility:

1. **Custom Hooks**: Create project-specific automation via Claude
2. **Custom Skills**: Add reusable capabilities for Claude agents
3. **Custom MCP Configs**: Integrate additional MCP servers
4. **Subagents**: Define specialized AI agents for specific tasks
5. **Custom Instructions**: Project-specific guidelines in CLAUDE.md

## Performance Considerations

- **Async I/O**: FastAPI with async/await for non-blocking operations
- **Database Connection Pooling**: SQLAlchemy async engine
- **Frontend Optimization**: React.memo, useMemo, useCallback for render optimization
- **Lazy Loading**: Dynamic imports for large components
- **Caching**: Frontend state management reduces redundant API calls

## Monitoring and Observability

- **Task History**: Complete audit trail of status changes
- **Claude Sessions**: Message history and metadata tracking
- **Stage Results**: Cumulative results at each task stage
- **Error Handling**: Structured error responses with detailed messages

---

## Recent Architectural Enhancements

### Explicit Project Mode Visibility (2025-11-20)
- **Mode Indicator in CLAUDE.md**: Every generated CLAUDE.md now includes explicit mode declaration
  - Format: `# 🎯 PROJECT MODE: [SIMPLE|DEVELOPMENT]`
  - Automatically inserted at top of file by `claude_config_generator.py`
  - Includes workflow description and characteristics
  - Ensures Claude Code always knows which mode is active
- **Mode Selection During Creation**: Project mode selected in ProjectSetup UI
  - Radio button interface with clear descriptions
  - Default: SIMPLE mode for new projects
  - Mode is immutable after creation (stored in database)
  - Cannot be changed mid-project to prevent workflow confusion
- **CLAUDE.md Regeneration Script**: New migration utility for syncing legacy projects
  - `claudetask/backend/migrations/regenerate_claude_md.py`
  - Reads configuration from database (mode, worktree_enabled, custom_instructions)
  - Creates backup before overwriting (CLAUDE.md.backup)
  - Updates `projects.claude_config` field
  - Useful for adding explicit mode indicators to existing projects

### Project Initialization Improvements (2025-11-20)
- **Hooks Directory Reorganization**: Hook scripts now stored in `.claude/hooks/` subdirectory
- **No Auto-Enablement**: Hooks are not automatically enabled during project creation
  - Gives users full control over which hooks to enable
  - Empty `.claude/settings.json` with `{"hooks": {}}` structure
  - Users enable hooks via UI, which merges hook configs into settings.json
- **Automatic settings.local.json Generation**: New file created during initialization
  - Pre-configured with essential MCP servers (claudetask, playwright, serena)
  - `enableAllProjectMcpServers: true` flag enables all project-specific MCP servers
  - No need for manual MCP server configuration
- **Script-Only Hook Copying**: Only `.sh` script files copied to project, not JSON configs
  - JSON configs stay in framework database
  - Cleaner project structure
  - Hook configs merged into settings.json only when enabled

### Database Migration 006 (CASCADE DELETE)
- Automatic cascade deletion of all project-related records
- Orphaned record cleanup during migration
- Safer and simpler project deletion workflow
- Prevents database inconsistencies

### Database Migration 005 (Worktree Toggle)
- Per-project worktree enable/disable functionality
- Dynamic CLAUDE.md generation based on worktree setting
- UI toggle in ProjectModeToggle component
- Single source of truth in database

### Database Migration 004 (Script File Support)
- Separate script files for complex hooks
- Improved hook maintainability and organization
- Automatic executable permissions on hook scripts

### MCP get_project_settings Tool
- Dynamic project configuration access from Claude Code
- Real-time project mode and worktree status
- Custom instructions accessible without file reads
- Single source of truth for project configuration

### Project Initialization Improvements
- Increased timeout to 30 seconds for directory trust
- Better handling of Claude session startup
- Automatic git repository initialization
- Framework update mechanism for existing projects

---

## Intelligent Development Workflow (2025-11-21)

The framework now implements a complete intelligent development workflow that guides tasks from inception through deployment using specialized agents and automation.

### Workflow Phases

**7-Phase DEVELOPMENT Mode Workflow**:
1. **Backlog**: Task creation and prioritization
2. **Analysis**: Automated requirements and architecture documentation by specialized agents
3. **In Progress**: Development in isolated git worktrees with automatic context injection
4. **Testing**: Manual testing with automated test environment setup
5. **Code Review**: Peer review of task-specific changes only
6. **Pull Request**: PR creation with comprehensive documentation linking
7. **Done**: Merge and automatic resource cleanup

### Key Components

#### Slash Commands
Quick workflow automation commands for triggering agents and managing workflow:
- `/start-feature [task-id]`: Start analysis phase with requirements-analyst and system-architect agents
- `/start-develop [task-id]`: Begin implementation after analysis complete
- `/test [task-id]`: Setup test environment (backend + frontend servers) for manual testing
- `/PR [task-id]`: Create pull request with complete documentation (requirements, architecture, tests)
- `/merge [task-id]`: Merge PR and cleanup all resources (sessions, processes, ports)

#### Specialized Agents

**Analysis Agents** (automated during `/start-feature`):
- `requirements-analyst`: Creates `Analyze/Requirements/` with:
  - requirements.md - User stories and acceptance criteria
  - acceptance-criteria.md - Business and functional requirements
  - constraints.md - Non-functional requirements (performance, security)
  - Constraints and success metrics

- `system-architect`: Creates `Analyse/architecture.md` with:
  - System component design
  - Technical implementation approach
  - Integration points and data flow
  - Implementation steps and technology stack
  - Security and performance considerations

**Implementation Agents** (used during development):
- `frontend-developer`: React/TypeScript UI development
- `backend-architect`: FastAPI/Python backend development
- `mobile-react-expert`: Mobile-responsive React components
- `python-api-expert`: API endpoint and service creation
- `devops-engineer`: Deployment and infrastructure

**Review and Merge Agents**:
- `fullstack-code-reviewer`: Code quality, security, and architecture validation
- `pr-merge-agent`: PR creation, documentation gathering, and merge coordination

#### Git Worktree Management

**Purpose**: Isolated development environments per task (optional in DEVELOPMENT mode)

**Structure**:
```
worktrees/
├── task-1/
│   ├── Analyse/           # Analysis documentation
│   │   ├── README.md      # Workflow instructions
│   │   ├── requirements.md  # Business requirements
│   │   └── architecture.md  # Technical design
│   ├── Tests/             # Testing documentation
│   │   ├── README.md      # Test instructions
│   │   └── test-plan.md   # Test results
│   └── [source code]      # Implementation files
└── task-2/
    └── ...
```

**Worktree Features**:
- Automatic main branch sync before creation
- Sync with latest main during development
- Task-specific folders (Analyse/, Tests/) with README templates
- Feature branch per task: `feature/task-{id}`
- Clean isolation between parallel tasks

#### Automatic Context Injection

**Enhanced MCP `start_claude_session` (v2.0)**:
- Automatically reads `requirements.md` and `architecture.md` from task worktree
- Injects analysis documents into Claude session context
- Provides complete task understanding to implementation agents
- Context format:
  ```
  Task #42: [Task Title]

  Requirements (from requirements.md):
  [Business requirements and acceptance criteria]

  Architecture (from architecture.md):
  [Technical approach and implementation plan]

  Your role: Implement this feature following the requirements and architecture.
  ```

### Workflow Automation

#### Auto-Transitions
Tasks automatically progress through certain phases:
- **Analysis → In Progress**: After requirements.md and architecture.md created by agents
- **In Progress → Testing**: When implementation detected (commits, agent completion reports)

#### Manual Transitions
User controls critical workflow transitions:
- **Backlog → Analysis**: User runs `/start-feature [task-id]`
- **Testing → Code Review**: User confirms tests pass, updates status manually
- **Code Review → PR**: User runs `/PR [task-id]` after review approved
- **PR → Done**: User runs `/merge [task-id]` after PR merged to main

### Resource Management

**Test Environment Setup** (via `/test` command):
1. Finds available ports for backend and frontend servers
2. Starts backend: `python -m uvicorn app.main:app --port [FREE_PORT]`
3. Starts frontend: `PORT=[FREE_PORT] npm start`
4. **MANDATORY**: Saves testing URLs to task database via `mcp:set_testing_urls`
5. Creates `Tests/` folder with test-plan.md template and README
6. Notifies user with direct access URLs

**Cleanup on Completion** (via `/merge` command):
1. Stops Claude Code session for task
2. Terminates embedded terminal sessions
3. Kills test server processes (backend and frontend)
4. Releases occupied ports
5. Clears testing URLs from database
6. Updates task status to "Done"
7. Optional: Removes task worktree

### Integration with Project Modes

**SIMPLE Mode**:
- Simplified 3-column workflow (Backlog → In Progress → Done)
- No analysis phase (no automated agents)
- No worktrees (work directly in main branch)
- No test environment automation
- Direct commits to main branch
- Faster for solo development and prototypes

**DEVELOPMENT Mode**:
- Full 7-column workflow with all phases
- Automated analysis with requirements-analyst and system-architect
- Git worktrees (can be toggled on/off per project)
- Test environment automation with URL persistence
- PR workflow with comprehensive documentation
- Quality gates: testing and code review required

**See**: [Intelligent Workflow Documentation](./intelligent-workflow.md) for complete details, examples, and best practices

---

## Related Documentation

- [Intelligent Workflow](./intelligent-workflow.md) - Complete workflow guide with all 7 phases
- [Slash Commands](../claudetask/slash-commands.md) - All available workflow automation commands
- [Project Modes](./project-modes.md) - SIMPLE vs DEVELOPMENT mode workflows
- [Settings API](../api/endpoints/settings.md) - Project configuration management
- [MCP Tools](../api/mcp-tools.md) - MCP tool reference including enhanced start_claude_session
- [Hooks System](./hooks-system.md) - Automation through Claude Code hooks
- [Framework Updates](./framework-updates.md) - File synchronization system
- [Database Migrations](../deployment/database-migrations.md) - Schema evolution history

---

---

## Project Memory System (2025-11-23)

The framework now includes an intelligent memory system that preserves conversation context across sessions, eliminating the need to re-explain project architecture and decisions.

### Memory Components

**Database Tables**:
- `conversation_memory`: Stores all user/assistant/system messages
- `project_summaries`: Maintains 3-5 page condensed project knowledge
- `memory_rag_status`: Tracks RAG indexing for semantic search
- `memory_sessions`: Session context loading statistics

**RAG Integration**:
- **Centralized ChromaDB**: Single instance at framework root `.claude/data/chromadb`
- ChromaDB collections per project (`memory_{project_id}`)
- Embedding model: `all-MiniLM-L6-v2`
- Automatic real-time indexing of conversations
- Semantic search for historical context retrieval
- Shared database reduces memory overhead across projects

**Memory Hooks** (enabled by default):
- `memory-conversation-capture`: Automatically saves all messages
- `memory-session-summarizer`: Updates project summary after sessions

### Automatic Context Loading

At session start, Claude Code automatically receives:
1. **Project Summary**: 3-5 pages of architecture, decisions, patterns
2. **Recent Messages**: Last 50 messages for immediate context
3. **RAG Results**: Top 20 semantically relevant historical messages

### API Endpoints

New memory management endpoints:
```
POST /api/projects/{id}/memory/messages      # Save message
GET  /api/projects/{id}/memory/context       # Get full context
PUT  /api/projects/{id}/memory/summary       # Update summary
POST /api/projects/{id}/memory/search        # Search memories
GET  /api/projects/{id}/memory/stats         # Memory statistics
```

### MCP Tools

Memory-related MCP commands:
- `mcp__claudetask__get_project_memory_context`: Load full context
- `mcp__claudetask__save_conversation_message`: Save important insight
- `mcp__claudetask__update_project_summary`: Update project knowledge
- `mcp__claudetask__search_project_memories`: Semantic search

### Benefits

- **No Context Loss**: Sessions start with full project understanding
- **Knowledge Accumulation**: Gets smarter with each interaction
- **Pattern Recognition**: Historical solutions automatically recalled
- **Faster Onboarding**: New sessions don't need re-explanation

**See**: [Memory System Documentation](../features/memory-system.md) for complete details

---

## AUTO Mode Improvements (2025-11-22)

Enhanced autonomous task execution with automatic PR creation after successful tests.

### Key Improvement

**Before**: Even in AUTO mode, user had to manually execute `/PR` after tests passed.

**After**: In AUTO mode (`manual_mode = false`), `/PR` executes automatically after successful tests.

### AUTO Mode Workflow

When `manual_mode = false`:
1. Task automatically selected from queue
2. Analysis performed automatically
3. Implementation done automatically
4. Tests setup automatically
5. **User tests manually** (only pause point)
6. After `/PR` or successful tests: **PR created automatically**
7. Loop continues with next task

### Configuration

```bash
# Enable AUTO mode
mcp__claudetask__update_project_settings --manual_mode=false

# Check current mode
mcp__claudetask__get_project_settings
```

**See**: [AUTO Mode Documentation](../features/auto-mode.md) for complete workflow details

---

## Local Worktree Merge (2025-11-22)

Added comprehensive workflow for merging task changes when project has no remote repository.

### Use Case

For projects without GitHub/GitLab hosting:
- No remote repository configured
- Task development done in local worktrees
- Need to merge changes to main branch locally

### Merge Process

```bash
# Verify no remote
git remote -v  # Should be empty

# Merge locally
git checkout main
git merge feature/task-{id} --no-ff -m "Merge task #{id} [skip-hook]"

# Cleanup
git worktree remove worktrees/task-{id}
git branch -d feature/task-{id}
git worktree prune
```

### Key Features

- Safe merge verification steps
- Conflict resolution strategies
- Complete cleanup procedures
- `[skip-hook]` tag prevents hook recursion
- Alternative rebase workflow option

**See**: [Local Worktree Merge Guide](../guides/local-worktree-merge.md) for step-by-step instructions

---

---

## MongoDB Atlas Storage Integration (2025-11-26)

The framework now supports dual storage backends, allowing projects to choose between local SQLite or cloud MongoDB Atlas storage.

### Repository Pattern

All data access goes through the Repository Pattern, which abstracts storage implementation:

```python
# Business logic doesn't know which storage is used
repo = await RepositoryFactory.get_project_repository(project_id, db)
project = await repo.get_by_id(project_id)
```

### Storage Backends

**Local Storage** (Default):
- SQLite for structured data
- ChromaDB for vector embeddings
- all-MiniLM-L6-v2 embeddings (384 dimensions)
- Completely offline and private
- No external dependencies
- Conversation memory RAG only

**Cloud Storage** (MongoDB Atlas):
- MongoDB Atlas for structured data
- MongoDB Vector Search for embeddings
- voyage-3-large embeddings (1024 dimensions)
- **Codebase RAG**: Semantic code search across entire repository
- Distributed and scalable
- Requires MongoDB Atlas cluster and Voyage AI API key

### Per-Project Selection

Each project can independently choose its storage backend via `project_settings.storage_mode`:
- New projects default to `"local"`
- Can be changed to `"mongodb"` after configuring credentials
- Migration tool available for moving data between backends

### Configuration

Cloud storage requires environment variables:
```bash
MONGODB_CONNECTION_STRING=mongodb+srv://user:pass@cluster.mongodb.net/
MONGODB_DATABASE_NAME=claudetask
VOYAGE_AI_API_KEY=vo-your-api-key-here
```

Configuration managed via Cloud Storage Settings UI (`/settings/cloud-storage`):
- Test connections before saving
- Save credentials to `.env` file
- Health monitoring
- Remove configuration

### Migration

CLI tool for migrating project data from SQLite to MongoDB:
```bash
python -m claudetask.migrations.migrate_to_mongodb \
  --project-id=<id> \
  --dry-run  # Preview before executing
```

Migration process:
1. Validates MongoDB and Voyage AI connectivity
2. Copies all project data to MongoDB
3. Re-embeds conversation messages with voyage-3-large (1024d)
4. Updates `storage_mode` from "local" to "mongodb"
5. Preserves original SQLite data (no deletion)

### Key Features

- **100% Backward Compatible**: All existing projects continue using local storage
- **Abstracted Business Logic**: Code doesn't know which storage is used
- **Easy Extension**: Can add PostgreSQL, DynamoDB, or other backends
- **No Breaking Changes**: All existing functionality works identically
- **Codebase RAG**: Semantic code search with natural language queries (MongoDB only)
- **Smart Embeddings**: voyage-3-large (1024d) for superior code understanding

### Codebase RAG

**MongoDB-only feature** for semantic code search:

```bash
# Index entire codebase
POST /api/codebase/index
{
  "repo_path": "/path/to/project",
  "full_reindex": true
}

# Search with natural language
POST /api/codebase/search
{
  "query": "authentication middleware with JWT verification",
  "limit": 20
}
```

**Features**:
- Semantic chunking (500 tokens, 50 overlap)
- Multi-language support (15+ languages)
- Symbol extraction (functions, classes, variables)
- Sub-200ms search performance
- Incremental reindexing

**See**: [MongoDB Atlas Storage Documentation](../features/mongodb-atlas-storage.md) for complete details
**See**: [Codebase RAG API Documentation](../api/endpoints/codebase-rag.md) for API reference

---

Last updated: 2025-11-26
