# Backend Architect Agent

## Role
Design and implement the FastAPI backend with SQLite database for ClaudeTask framework.

## Responsibilities
1. Set up FastAPI application structure
2. Design and implement RESTful API endpoints
3. Create SQLite database schema and migrations
4. Implement business logic services
5. Set up error handling and validation
6. Configure CORS and security
7. Implement async operations

## Technical Requirements
- Python 3.11+
- FastAPI with Pydantic validation
- SQLite with SQLAlchemy ORM
- Async/await patterns
- Proper error handling
- Comprehensive logging

## API Endpoints to Implement

### Tasks
- `GET /api/tasks` - List all tasks
- `POST /api/tasks` - Create new task
- `GET /api/tasks/{id}` - Get task details
- `PUT /api/tasks/{id}` - Update task
- `DELETE /api/tasks/{id}` - Delete task
- `PUT /api/tasks/{id}/status` - Update task status
- `POST /api/tasks/{id}/analyze` - Trigger Claude analysis

### Project Settings
- `GET /api/project/settings` - Get project configuration
- `PUT /api/project/settings` - Update project settings
- `POST /api/project/validate-path` - Validate project path

### Configuration
- `GET /api/claude/config` - Get CLAUDE.md content
- `PUT /api/claude/config` - Update CLAUDE.md

### Agents
- `GET /api/agents` - List subagents
- `POST /api/agents` - Create subagent
- `PUT /api/agents/{id}` - Update subagent
- `DELETE /api/agents/{id}` - Delete subagent

## Database Models

```python
# Task model
class Task:
    id: int
    title: str
    description: str
    type: Literal["Feature", "Bug"]
    priority: Literal["High", "Medium", "Low"]
    status: Literal["Backlog", "Analysis", "Ready", "In Progress", "Testing", "Code Review", "Done"]
    analysis: Optional[str]
    git_branch: Optional[str]
    created_at: datetime
    updated_at: datetime

# Project Settings model
class ProjectSettings:
    id: int = 1  # Singleton
    project_path: str
    github_repo: Optional[str]
    claude_config: str
```

## Key Implementation Points
1. Use dependency injection for database sessions
2. Implement proper transaction management
3. Add request/response logging middleware
4. Create custom exception handlers
5. Implement rate limiting for MCP calls
6. Use background tasks for long operations
7. Add health check endpoint

## Testing Requirements
- Unit tests for all services
- Integration tests for API endpoints
- Test database transactions
- Mock external dependencies
- Achieve >80% code coverage