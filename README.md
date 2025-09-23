# ClaudeTask

A comprehensive task management framework designed specifically for Claude Code integration. ClaudeTask provides a visual web interface for managing development tasks while leveraging Claude's AI capabilities for automated analysis, implementation, and code review.

## ✨ Features

- **Visual Task Board**: Kanban-style interface for managing tasks across different stages
- **Claude Code Integration**: Seamless MCP (Model Context Protocol) integration with Claude
- **Automated Workflow**: Tasks are automatically analyzed and implemented by Claude
- **Git Worktree Support**: Isolated development environments for each task
- **Technology Agnostic**: Works with any programming language or framework
- **Coordinator-Executor Pattern**: Claude acts as coordinator, delegating work to specialized agents

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │    Backend      │    │   MCP Server    │
│  (React + TS)   │◄───┤ (FastAPI + DB)  │◄───┤ (Claude Bridge) │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                                       ▲
                                                       │
                                               ┌───────────────┐
                                               │  Claude Code  │
                                               └───────────────┘
```

## 🚀 Quick Start

### Prerequisites

- Docker and Docker Compose
- Python 3.8+
- Git
- Claude Code

### Installation

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd ClaudeTask
   ```

2. **Run the installation script:**
   ```bash
   ./install.sh
   ```

3. **Access the application:**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:3333

### Project Setup

1. Open http://localhost:3000 in your browser
2. Navigate to "Project Setup"
3. Enter your project path and name
4. Click "Initialize Project"
5. Restart Claude Code to load the MCP configuration

## 📋 Workflow

### Task Lifecycle

1. **Backlog** → **Analysis** → **Ready** → **In Progress** → **Testing** → **Code Review** → **Done**

### How it Works

1. **Create Tasks**: Use the web interface to create and prioritize tasks
2. **Claude Analysis**: Claude automatically analyzes tasks and creates implementation plans
3. **Automated Development**: Claude works in isolated git worktrees to implement features
4. **Testing & Review**: Automated testing and code review process
5. **Merge**: Completed tasks are merged back to main branch

## 🔗 MCP Integration

ClaudeTask supports Claude Code integration through MCP (Model Context Protocol).

### Quick Setup for Other Projects

1. **Auto-initialize in your project:**
```bash
# From your project directory
python3 "/path/to/framework/claudetask/scripts/init_project.py"
```

2. **Manual setup** - Add to your project's `.mcp.json`:
```json
{
  "mcpServers": {
    "claudetask": {
      "command": "python3",
      "args": [
        "/path/to/framework/claudetask/mcp_server/native_stdio_server.py"
      ],
      "env": {
        "CLAUDETASK_PROJECT_ID": "ff9cc152-3f38-49ab-bec0-0e7cbf84594a",
        "CLAUDETASK_PROJECT_PATH": "/path/to/your/project",
        "CLAUDETASK_BACKEND_URL": "http://localhost:3333"
      }
    }
  }
}
```

3. **Restart Claude Code** in your project

### Prerequisites

Ensure these services are running:
- **Backend**: `cd claudetask/backend && python -m uvicorn app.main:app --host 0.0.0.0 --port 3333`
- **Frontend**: `cd claudetask/frontend && REACT_APP_API_URL=http://localhost:3333/api PORT=3334 npm start`

### Available MCP Tools

- `mcp:get_task_queue` - View all tasks in queue
- `mcp:get_next_task` - Get highest priority task
- `mcp:get_task <id>` - Get specific task details with next steps
- `mcp:analyze_task <id>` - Analyze task and create plan
- `mcp:update_task_analysis <id> "<analysis>"` - Save analysis
- `mcp:update_status <id> <status>` - Update task status
- `mcp:create_worktree <id>` - Create git worktree
- `mcp:delegate_to_agent <id> <agent> "<instructions>"` - Delegate to agent
- `mcp:complete_task <id>` - Complete and merge task

### Usage in Claude Code

```bash
# Start task workflow
mcp:get_task_queue
mcp:get_next_task
mcp:get_task 4

# Follow the next steps provided by MCP responses
mcp:update_status 4 "In Progress"
mcp:delegate_to_agent 4 "frontend-developer" "Implement the feature"
```

## 🛠️ Development

### Running Locally

```bash
# Start services
./start-claudetask.sh

# Stop services
./stop-claudetask.sh
```

### Manual Setup

#### Backend
```bash
cd claudetask/backend
pip install -r requirements.txt
python -m app.main
```

#### Frontend
```bash
cd claudetask/frontend
npm install
npm start
```

#### MCP Server
```bash
cd claudetask/mcp_server
pip install -r requirements.txt
python claudetask_mcp_bridge.py --project-id <id> --project-path <path>
```

## 📁 Project Structure

```
ClaudeTask/
├── claudetask/
│   ├── backend/          # FastAPI backend
│   │   ├── app/
│   │   │   ├── models.py         # Database models
│   │   │   ├── schemas.py        # Pydantic schemas
│   │   │   ├── main.py           # FastAPI app
│   │   │   └── services/         # Business logic
│   │   └── requirements.txt
│   ├── frontend/         # React frontend
│   │   ├── src/
│   │   │   ├── components/       # React components
│   │   │   ├── pages/            # Application pages
│   │   │   └── services/         # API services
│   │   └── package.json
│   └── mcp_server/       # MCP bridge server
│       ├── claudetask_mcp_bridge.py
│       └── requirements.txt
├── docker-compose.yml    # Docker services
├── install.sh           # Installation script
└── README.md
```

## 🔧 Configuration

### Project Configuration

When you initialize a project, ClaudeTask creates:

- `.claudetask/` directory with project metadata
- `.mcp.json` file for Claude Code integration
- `CLAUDE.md` with project-specific instructions
- Default agent configurations

### Environment Variables

- `DATABASE_URL`: Database connection string
- `REACT_APP_API_URL`: Backend API URL for frontend

## 🔐 Security

- Tasks run in isolated git worktrees
- No direct file system access from web interface
- MCP server requires project-specific configuration
- All changes go through git workflow

## 🧪 Testing

```bash
# Backend tests
cd claudetask/backend
pytest

# Frontend tests
cd claudetask/frontend
npm test
```

## 📖 Documentation

- [Use Cases](use-cases.md) - Detailed usage scenarios
- [Framework Workflow](framework-workflow.md) - Technical workflow details
- [Requirements](requirements.md) - Complete requirements specification

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

MIT License - see LICENSE file for details

## 🆘 Support

For issues and questions:
1. Check the documentation
2. Search existing issues
3. Create a new issue with detailed information

## 🎯 Roadmap

- [ ] Advanced agent configurations
- [ ] Integration with more Git providers
- [ ] Real-time task notifications
- [ ] Performance metrics and analytics
- [ ] Plugin system for custom agents
- [ ] Multi-project workspace support