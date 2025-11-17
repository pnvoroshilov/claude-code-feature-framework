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
└──────────────────┬──────────────────────────────────────────┘
                   │ HTTP/REST API
                   │ WebSocket (Real-time updates)
┌──────────────────▼──────────────────────────────────────────┐
│                   Backend (FastAPI)                         │
│  - RESTful API Endpoints                                    │
│  - Business Logic Services                                  │
│  - Database ORM (SQLAlchemy)                                │
│  - Claude Code CLI Integration                              │
└──────────────────┬──────────────────────────────────────────┘
                   │
     ┌─────────────┼─────────────┐
     │             │             │
┌────▼────┐  ┌────▼────┐  ┌─────▼─────┐
│ SQLite  │  │ Claude  │  │   File    │
│Database │  │  Code   │  │  System   │
│         │  │   CLI   │  │ (.claude/)│
└─────────┘  └─────────┘  └───────────┘
```

## Technology Stack

### Frontend
- **Framework**: React 18 with TypeScript
- **UI Library**: Material-UI (MUI) v5
- **State Management**: React Context API
- **HTTP Client**: Axios
- **Routing**: React Router v6
- **Code Editor**: Monaco Editor (for editing hooks, skills, agents)

### Backend
- **Framework**: FastAPI (Python 3.9+)
- **ORM**: SQLAlchemy 2.0 with async support
- **Database**: SQLite (with async SQLite driver)
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
- Project-specific configuration (CLAUDE.md generation)
- Custom instructions support
- Two modes: SIMPLE and DEVELOPMENT
- Active project tracking

### 2. Task Management
- Task CRUD operations
- Status workflow tracking
- Git worktree integration (DEVELOPMENT mode)
- Task history and audit trail
- Stage results tracking

### 3. Hooks System
- Default hooks (framework-provided)
- Custom hooks (user-created via Claude)
- Per-project hook enablement
- Favorites system (cross-project)
- Integration with .claude/settings.json

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

## Database Schema

The system uses SQLite with the following main tables:

- **projects**: Project configurations and metadata
- **tasks**: Task tracking with status, worktree info, stage results
- **task_history**: Audit trail of task status changes
- **claude_sessions**: Claude Code session management
- **default_hooks**: Framework-provided hooks
- **custom_hooks**: User-created hooks
- **project_hooks**: Junction table for project-hook enablement
- **default_skills**: Framework-provided skills
- **custom_skills**: User-created skills
- **project_skills**: Junction table for project-skill enablement
- **default_mcp_configs**: Framework-provided MCP configurations
- **custom_mcp_configs**: User-created MCP configurations
- **project_mcp_configs**: Junction table for project-MCP enablement
- **agents**: Subagent configurations
- **project_settings**: Per-project settings

See [database-design.md](./database-design.md) for detailed schema documentation.

## API Architecture

### RESTful API Design
All endpoints follow REST conventions:
- `GET` - Retrieve resources
- `POST` - Create resources
- `PUT` - Update resources
- `DELETE` - Remove resources

### Endpoint Organization
```
/api/projects                    # Project management
/api/projects/{id}/tasks         # Task management
/api/projects/{id}/hooks         # Hooks management
/api/projects/{id}/skills        # Skills management
/api/projects/{id}/mcp-configs   # MCP configurations
/api/projects/{id}/subagents     # Subagent management
/api/projects/{id}/instructions  # Custom instructions
/api/sessions                    # Claude sessions
/api/editor                      # File editor endpoints
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

Last updated: 2025-11-18
