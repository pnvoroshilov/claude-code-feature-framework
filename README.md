# ClaudeTask

A comprehensive task management framework designed specifically for Claude Code integration. ClaudeTask provides a visual web interface for managing development tasks while leveraging Claude's AI capabilities for automated analysis, implementation, and code review.

## ✨ Features

- **Visual Task Board**: Kanban-style interface for managing tasks across different stages
- **Claude Code Integration**: Seamless MCP (Model Context Protocol) integration with Claude
- **Automated Workflow**: Tasks are automatically analyzed and implemented by Claude
- **Project Memory System**: Automatic conversation persistence with RAG-based semantic search
  - No context loss between sessions
  - Intelligent summarization of project knowledge
  - ChromaDB-powered semantic search
- **AUTO Mode**: Fully autonomous task execution with automatic PR creation
- **Git Worktree Support**: Isolated development environments for each task
- **Local Merge Workflow**: Complete workflow for projects without remote repositories
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

Before installing ClaudeTask, ensure you have the following installed:

- **Python 3.8+**
  - Verify: `python3 --version`
  - Install pip: `python3 -m pip --version`
- **Node.js 16+** and **npm**
  - [Install Node.js](https://nodejs.org/)
  - Verify: `node --version` and `npm --version`
- **Git**
  - Verify: `git --version`
- **Claude Code** (latest version)
  - [Download Claude Code](https://claude.ai/download)

> **Note:** ClaudeTask runs directly on your system (not in Docker) to maintain access to your terminal, Git, and Claude Code integration.

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/pnvoroshilov/claude-code-feature-framework.git
   cd claude-code-feature-framework
   ```

2. **Install Backend:**
   ```bash
   cd claudetask/backend

   # Create virtual environment (recommended)
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate

   # Install dependencies
   pip install -r requirements.txt

   # Start backend server
   python -m uvicorn app.main:app --host 0.0.0.0 --port 3333 --reload
   ```

   Backend will be available at:
   - **API**: http://localhost:3333
   - **API Docs**: http://localhost:3333/docs
   - **Health Check**: http://localhost:3333/health

3. **Install Frontend** (in a new terminal):
   ```bash
   cd claudetask/frontend

   # Install dependencies
   npm install

   # Start frontend development server
   REACT_APP_API_URL=http://localhost:3333/api PORT=3000 npm start
   ```

   Frontend will be available at: http://localhost:3000

4. **Install MCP Server** (optional - for Claude Code integration):
   ```bash
   cd claudetask/mcp_server
   pip3 install -r requirements.txt
   ```

   The MCP server will be configured per-project (see Project Setup section below).

### Project Setup in ClaudeTask

After installation, set up your first project:

1. **Open ClaudeTask UI:** http://localhost:3000

2. **Navigate to "Project Setup"** (gear icon in sidebar)

3. **Create a new project:**
   - **Project Name**: e.g., "My App Development"
   - **Project Path**: Absolute path to your project directory
   - **Description**: Optional description
   - Click **"Initialize Project"**

4. **Configure Claude Code integration:**

   The initialization creates a `.mcp.json` file in your project directory. Example:
   ```json
   {
     "mcpServers": {
       "claudetask": {
         "command": "python3",
         "args": [
           "/Users/youruser/.claudetask_mcp/native_stdio_server.py"
         ],
         "env": {
           "CLAUDETASK_PROJECT_ID": "generated-uuid",
           "CLAUDETASK_PROJECT_PATH": "/path/to/your/project",
           "CLAUDETASK_BACKEND_URL": "http://localhost:3333"
         }
       }
     }
   }
   ```

5. **Restart Claude Code:**
   - Close Claude Code completely
   - Open your project directory in Claude Code
   - MCP tools should now be available

6. **Verify MCP connection:**
   ```bash
   # In Claude Code terminal, try:
   mcp:get_task_queue
   ```

### Managing ClaudeTask Services

You need to run both backend and frontend in separate terminals:

**Terminal 1 - Backend:**
```bash
cd claudetask/backend
source venv/bin/activate  # Activate virtual environment
python -m uvicorn app.main:app --host 0.0.0.0 --port 3333 --reload
```

**Terminal 2 - Frontend:**
```bash
cd claudetask/frontend
REACT_APP_API_URL=http://localhost:3333/api PORT=3000 npm start
```

**Tips:**
- Use `tmux` or `screen` to manage multiple terminals
- Or use process managers like `pm2` or `supervisor`
- Keep both services running while working with ClaudeTask

## 📋 Workflow

### Task Lifecycle

1. **Backlog** → **Analysis** → **Ready** → **In Progress** → **Testing** → **Code Review** → **Done**

### How it Works

1. **Create Tasks**: Use the web interface to create and prioritize tasks
2. **Claude Analysis**: Claude automatically analyzes tasks and creates implementation plans
3. **Automated Development**: Claude works in isolated git worktrees to implement features
   - Worktrees automatically sync with the latest main branch before creation
   - Each task gets the most recent code updates from origin/main
   - Works gracefully with both remote and local-only repositories
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

### Development Setup

ClaudeTask consists of three main components that run separately:

#### 1. Backend (FastAPI + SQLite)
```bash
cd claudetask/backend
source venv/bin/activate
python -m uvicorn app.main:app --host 0.0.0.0 --port 3333 --reload
```

#### 2. Frontend (React + TypeScript)
```bash
cd claudetask/frontend
REACT_APP_API_URL=http://localhost:3333/api PORT=3000 npm start
```

#### 3. MCP Server (Per-Project)
The MCP server runs automatically when Claude Code starts (configured in `.mcp.json` of your project).

### Development Tips

- **Hot Reload:** Both backend (`--reload`) and frontend automatically reload on changes
- **API Documentation:** Visit http://localhost:3333/docs for interactive API docs
- **Database:** SQLite database is created automatically at `claudetask/backend/claudetask.db`
- **Logs:** Backend logs are in `claudetask/backend/server.log`

## 📁 Project Structure

```
claude-code-feature-framework/
├── claudetask/
│   ├── backend/              # FastAPI backend (Python)
│   │   ├── app/
│   │   │   ├── models.py         # SQLAlchemy database models
│   │   │   ├── schemas.py        # Pydantic schemas for API
│   │   │   ├── main.py           # FastAPI application entry point
│   │   │   ├── database.py       # Database configuration
│   │   │   └── services/         # Business logic services
│   │   │       ├── task_service.py
│   │   │       ├── project_service.py
│   │   │       ├── real_claude_service.py
│   │   │       └── rag_service.py    # RAG semantic search
│   │   ├── requirements.txt
│   │   ├── claudetask.db         # SQLite database (auto-created)
│   │   └── server.log            # Application logs
│   │
│   ├── frontend/             # React frontend (TypeScript)
│   │   ├── src/
│   │   │   ├── components/       # Reusable React components
│   │   │   ├── pages/            # Page components (TaskBoard, Dashboard)
│   │   │   ├── services/         # API client services
│   │   │   └── App.tsx           # Main React app
│   │   ├── package.json
│   │   └── public/
│   │
│   └── mcp_server/           # MCP bridge (Python)
│       ├── claudetask_mcp_bridge.py  # Main MCP server
│       ├── native_stdio_server.py    # STDIO wrapper
│       ├── requirements.txt
│       └── rag/                  # RAG indexing system
│           ├── indexer.py
│           └── embeddings.py
│
├── framework-assets/         # Reusable agent configs
│   ├── claude-agents/        # Agent markdown files
│   ├── claude-configs/       # CLAUDE.md templates
│   └── claude-commands/      # Slash commands
│
├── .claude/                  # Project-specific Claude config
│   ├── agents/               # Agent configurations
│   └── commands/             # Custom slash commands
│
├── worktrees/                # Git worktrees for tasks (auto-created)
│   └── task-<id>/            # Isolated dev environment per task
│
├── install.sh                # Installation script
└── README.md                 # This file
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

### Getting Started
- [Installation & Setup](#quick-start) - Complete installation guide
- [Project Setup](#project-setup-in-claudetask) - First project configuration

### Core Features
- [Project Memory System](docs/features/memory-system.md) - Cross-session context preservation
- [AUTO Mode](docs/features/auto-mode.md) - Autonomous task execution

### Guides
- [Local Worktree Merge](docs/guides/local-worktree-merge.md) - Merging without remote repository
- [Testing Workflow](docs/how-to-switch-testing-modes.md) - Manual and automated testing

### Architecture
- [System Architecture](docs/architecture/overview.md) - Complete technical overview
- [Intelligent Workflow](docs/architecture/intelligent-workflow.md) - 7-phase development workflow
- [Hooks System](docs/architecture/hooks-system.md) - Automation with Claude Code hooks

### API Reference
- [MCP Tools](docs/api/mcp-tools.md) - Complete MCP command reference
- [REST API Endpoints](docs/api/endpoints/) - Backend API documentation

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

MIT License - see LICENSE file for details

## 🔧 Troubleshooting

### Common Issues

#### 1. Backend won't start

**Problem:** Backend fails to start or crashes immediately

**Solutions:**
```bash
# Check Python version
python3 --version  # Should be 3.8+

# Check virtual environment is activated
which python  # Should point to venv/bin/python

# Reinstall dependencies
cd claudetask/backend
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Check port is not in use
lsof -i :3333
# Kill process if needed: kill -9 <PID>

# Check logs
python -m uvicorn app.main:app --host 0.0.0.0 --port 3333 --reload
```

#### 2. MCP tools not available in Claude Code

**Problem:** `mcp:get_task_queue` returns "command not found"

**Solutions:**
1. Verify `.mcp.json` exists in your project directory
2. Check MCP server path in `.mcp.json` is correct
3. Restart Claude Code completely (quit and reopen)
4. Check MCP server is installed:
   ```bash
   ls ~/.claudetask_mcp/
   python3 ~/.claudetask_mcp/native_stdio_server.py --help
   ```

#### 3. Backend connection refused

**Problem:** Frontend shows "Failed to connect to backend"

**Solutions:**
```bash
# 1. Check backend is running
curl http://localhost:3333/health
# Should return: {"status": "healthy"}

# 2. Check backend process
ps aux | grep uvicorn

# 3. Check backend is listening on correct port
lsof -i :3333

# 4. Restart backend
cd claudetask/backend
source venv/bin/activate
python -m uvicorn app.main:app --host 0.0.0.0 --port 3333 --reload

# 5. Check CORS settings if accessing from different origin
```

#### 4. Database errors

**Problem:** "database is locked" or migration errors

**Solutions:**
```bash
# 1. Stop backend
# Press Ctrl+C in backend terminal

# 2. Remove old database
cd claudetask/backend
rm -f claudetask.db

# 3. Run migrations (if migration script exists)
python migrate_db.py

# 4. Restart backend
python -m uvicorn app.main:app --host 0.0.0.0 --port 3333 --reload
```

#### 5. Frontend won't load

**Problem:** http://localhost:3000 shows blank page or errors

**Solutions:**
```bash
# 1. Check Node version
node --version  # Should be 16+

# 2. Clear npm cache and reinstall
cd claudetask/frontend
rm -rf node_modules package-lock.json
npm install

# 3. Check environment variable
echo $REACT_APP_API_URL
# Should be: http://localhost:3333/api

# 4. Start with environment variable
REACT_APP_API_URL=http://localhost:3333/api PORT=3000 npm start

# 5. Check browser console for errors (F12)
```

#### 6. Port already in use

**Problem:** "Port already in use" error when starting services

**Solutions:**
```bash
# Find what's using the port
lsof -i :3000  # Frontend
lsof -i :3333  # Backend

# Kill the process
kill -9 <PID>

# Or use different ports:
# Backend: python -m uvicorn app.main:app --port 3334
# Frontend: PORT=3001 npm start
```

#### 7. Git worktree errors

**Problem:** "Cannot create worktree" or "worktree already exists"

**Solutions:**
```bash
# 1. List existing worktrees
git worktree list

# 2. Remove stuck worktree
git worktree remove worktrees/task-<id>
# Or force remove: git worktree remove --force worktrees/task-<id>

# 3. Prune invalid worktrees
git worktree prune

# 4. Check worktrees directory permissions
ls -la worktrees/
```

### Getting Help

If you encounter issues not covered here:

1. **Check the logs:**
   ```bash
   # Backend logs
   cd claudetask/backend
   tail -f server.log

   # Or check terminal output where backend is running
   ```

2. **Check environment:**
   ```bash
   # Python version
   python3 --version

   # Node version
   node --version

   # Virtual environment
   which python

   # Process status
   ps aux | grep uvicorn
   ps aux | grep node
   ```

3. **Search existing issues:**
   - [GitHub Issues](https://github.com/pnvoroshilov/claude-code-feature-framework/issues)

4. **Create a new issue:**
   - Include error messages
   - Include relevant logs
   - Include your environment (OS, Python version, Node version)
   - Include output of: `ps aux | grep -E "(uvicorn|node)"`

## 🆘 Support

For issues and questions:
1. Check the [Troubleshooting](#-troubleshooting) section above
2. Search [existing issues](https://github.com/pnvoroshilov/claude-code-feature-framework/issues)
3. Create a [new issue](https://github.com/pnvoroshilov/claude-code-feature-framework/issues/new) with:
   - Detailed problem description
   - Error messages and logs
   - Environment information (OS, versions)
   - Steps to reproduce

## 🎯 Recent Updates

- **Project Memory System** (2025-11-23) - Automatic conversation persistence with RAG search
- **AUTO Mode Improvements** (2025-11-22) - Automatic PR creation after successful tests
- **Local Worktree Merge** (2025-11-22) - Complete workflow for projects without remote repos
- **RAG-Enhanced Analysis** (2025-11-20) - Semantic code search for better context

## 🗺️ Roadmap

- [x] **RAG-Enhanced Analysis** - Semantic code search for better context (✅ Completed)
- [x] **Project Memory System** - Cross-session context preservation (✅ Completed)
- [ ] Advanced agent configurations with custom tools
- [ ] Integration with more Git providers (GitHub, GitLab, Bitbucket)
- [ ] Real-time task notifications via WebSocket (Partial - WebSocket infrastructure exists)
- [ ] Performance metrics and analytics dashboard
- [ ] Plugin system for custom agents
- [ ] Multi-project workspace support (✅ Exists, needs enhancement)
- [ ] Task templates and automation workflows
- [ ] Integration with CI/CD pipelines
- [ ] Mobile-friendly UI