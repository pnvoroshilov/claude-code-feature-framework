# ClaudeTask Framework Development Guide

## Project Overview
You are developing ClaudeTask - a local task management framework with Claude Code integration via MCP protocol. The system allows managing development tasks like in Jira, but with automatic development through Claude.

## Tech Stack
- Frontend: React + TypeScript + Material-UI
- Backend: Python FastAPI + SQLite
- MCP Server: Python-based implementation
- Deployment: Docker + Docker Compose
- VCS: Git with worktree support

## Project Structure
```
claudetask/
├── frontend/                 # React application
│   ├── src/
│   │   ├── components/      # UI components
│   │   ├── pages/          # Page components
│   │   ├── services/       # API services
│   │   ├── types/          # TypeScript types
│   │   └── App.tsx
│   └── package.json
├── backend/                 # FastAPI server
│   ├── app/
│   │   ├── api/            # API endpoints
│   │   ├── models/         # Data models
│   │   ├── services/       # Business logic
│   │   └── main.py
│   └── requirements.txt
├── mcp-server/             # MCP integration
│   ├── server.py
│   └── handlers/
├── docker-compose.yml
└── data/                   # Persistent data
```

## Development Guidelines

### Code Standards
- Use TypeScript for all React code
- Follow PEP 8 for Python code
- Write comprehensive docstrings
- Add type hints in Python
- Use async/await for all I/O operations
- Implement proper error handling
- Write unit tests for critical functions

### Git Workflow
- Create feature branches for each component
- Commit messages: `feat: `, `fix: `, `docs: `, `refactor: `
- Small, atomic commits
- PR descriptions should reference requirements

### API Design
- RESTful endpoints
- Consistent error responses
- Input validation with Pydantic
- CORS configuration for local development
- Proper HTTP status codes

### Database Schema
```sql
-- tasks table
CREATE TABLE tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    description TEXT,
    type TEXT CHECK(type IN ('Feature', 'Bug')),
    priority TEXT CHECK(priority IN ('High', 'Medium', 'Low')),
    status TEXT CHECK(status IN ('Backlog', 'Analysis', 'Ready', 'In Progress', 'Testing', 'Code Review', 'Done')),
    analysis TEXT,
    git_branch TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- project_settings table
CREATE TABLE project_settings (
    id INTEGER PRIMARY KEY CHECK (id = 1),
    project_path TEXT NOT NULL,
    github_repo TEXT,
    claude_config TEXT
);
```

### MCP Server Implementation
- Use Python MCP SDK
- Implement async handlers
- Proper error propagation
- Connection pooling for database
- Request/response logging
- Complete task workflow with merge operations

### Frontend Components

#### Core Components
1. **TaskBoard** - Kanban board with drag-and-drop
2. **TaskCard** - Individual task display
3. **TaskModal** - Create/edit task form
4. **StatusColumn** - Column for each status
5. **ConfigPanel** - Settings and configuration

#### State Management
- Use React Context for global state
- Local state for UI-specific data
- Optimistic updates for better UX

### Testing Strategy
- Unit tests for business logic
- Integration tests for API endpoints
- E2E tests for critical workflows
- Mock MCP server for testing

## Implementation Order

### Phase 1: Foundation
1. Set up Docker environment
2. Create basic FastAPI backend
3. Implement SQLite database
4. Basic React frontend setup

### Phase 2: Core Features
1. Task CRUD operations
2. Kanban board UI
3. Drag-and-drop functionality
4. Status management

### Phase 3: MCP Integration
1. MCP server implementation
2. Claude integration endpoints
3. Task analysis feature
4. Status automation

### Phase 4: Git Integration
1. Worktree management
2. Branch creation
3. GitHub PR integration
4. Merge automation

### Phase 5: Advanced Features
1. CLAUDE.md editor
2. Subagent management
3. Project settings
4. Analysis visualization

## Critical Implementation Notes

### Security
- All operations are local only
- No external API calls except GitHub
- Sanitize all user inputs
- Secure file path handling

### Performance
- Lazy load task details
- Implement pagination for large task lists
- Cache project analysis
- Optimize React re-renders

### Error Handling
- Graceful MCP connection failures
- Database transaction rollbacks
- User-friendly error messages
- Detailed logging for debugging

### Docker Configuration
```yaml
version: '3.8'
services:
  frontend:
    build: ./frontend
    ports: ["3000:3000"]
  backend:
    build: ./backend
    ports: ["8000:8000"]
    volumes: ["./data:/app/data"]
  mcp-server:
    build: ./mcp-server
    ports: ["3333:3333"]
```

## Commands to Run
- Development: `docker-compose up --build`
- Tests: `pytest backend/tests`
- Linting: `ruff check .`
- Type checking: `mypy backend/`

## Environment Variables
```env
PROJECT_PATH=/path/to/target/project
GITHUB_TOKEN=optional_for_pr_creation
MCP_SERVER_URL=http://mcp-server:3333
DATABASE_PATH=/app/data/claudetask.db
```