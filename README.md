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

Before installing ClaudeTask, ensure you have the following installed:

- **Docker** (version 20.10+) and **Docker Compose** (version 2.0+)
  - [Install Docker Desktop](https://www.docker.com/products/docker-desktop/)
  - Verify: `docker --version` and `docker compose version`
- **Python 3.8+**
  - Verify: `python3 --version`
  - Install pip: `python3 -m pip --version`
- **Git**
  - Verify: `git --version`
- **Claude Code** (latest version)
  - [Download Claude Code](https://claude.ai/download)
- **Node.js 16+** and **npm** (for local development)
  - Verify: `node --version` and `npm --version`

### Installation

#### Option 1: Automated Installation (Recommended)

1. **Clone the repository:**
   ```bash
   git clone https://github.com/pnvoroshilov/claude-code-feature-framework.git
   cd claude-code-feature-framework
   ```

2. **Run the installation script:**
   ```bash
   chmod +x install.sh
   ./install.sh
   ```

   This script will:
   - ✅ Check all prerequisites
   - ✅ Install MCP server globally to `~/.claudetask_mcp`
   - ✅ Build and start Docker containers (backend + frontend)
   - ✅ Create `start-claudetask.sh` and `stop-claudetask.sh` scripts
   - ✅ Wait for services to be ready

3. **Access the application:**
   - **Frontend**: http://localhost:3000
   - **Backend API**: http://localhost:3333
   - **API Docs**: http://localhost:3333/docs

#### Option 2: Manual Installation

If you prefer to install manually or the automated script fails:

<details>
<summary>Click to expand manual installation steps</summary>

1. **Clone the repository:**
   ```bash
   git clone https://github.com/pnvoroshilov/claude-code-feature-framework.git
   cd claude-code-feature-framework
   ```

2. **Install MCP Server dependencies:**
   ```bash
   cd claudetask/mcp_server
   pip3 install -r requirements.txt
   cd ../..
   ```

3. **Start services with Docker:**
   ```bash
   # Build and start all services
   docker compose up -d --build

   # Check status
   docker compose ps
   ```

4. **Or run services locally (without Docker):**

   **Backend:**
   ```bash
   cd claudetask/backend
   pip3 install -r requirements.txt
   python3 -m uvicorn app.main:app --host 0.0.0.0 --port 3333 --reload
   ```

   **Frontend:**
   ```bash
   cd claudetask/frontend
   npm install
   REACT_APP_API_URL=http://localhost:3333/api PORT=3000 npm start
   ```

</details>

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

After installation, use these scripts:

```bash
# Start ClaudeTask
./start-claudetask.sh

# Stop ClaudeTask
./stop-claudetask.sh

# View logs
docker compose logs -f

# Restart services
docker compose restart
```

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

## 🔧 Troubleshooting

### Common Issues

#### 1. Docker containers won't start

**Problem:** `docker compose up` fails or containers exit immediately

**Solutions:**
```bash
# Check Docker is running
docker ps

# Check logs
docker compose logs

# Clean rebuild
docker compose down -v
docker compose up -d --build

# Check ports are not in use
lsof -i :3000  # Frontend
lsof -i :3333  # Backend
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
# Check backend is running
curl http://localhost:3333/health

# Check backend logs
docker compose logs backend

# Restart backend
docker compose restart backend
```

#### 4. Database errors

**Problem:** "database is locked" or migration errors

**Solutions:**
```bash
# Stop all services
docker compose down

# Remove old database
rm -rf data/*.db

# Restart fresh
docker compose up -d
```

#### 5. Frontend won't load

**Problem:** http://localhost:3000 shows blank page or errors

**Solutions:**
```bash
# Check frontend logs
docker compose logs frontend

# Rebuild frontend
docker compose down
docker compose up -d --build frontend

# Check browser console for errors (F12)
```

#### 6. Port already in use

**Problem:** "Port 3000 is already allocated" or "Port 3333 is already allocated"

**Solutions:**
```bash
# Find what's using the port
lsof -i :3000
lsof -i :3333

# Kill the process
kill -9 <PID>

# Or change ports in docker-compose.yml
```

### Getting Help

If you encounter issues not covered here:

1. **Check the logs:**
   ```bash
   docker compose logs -f
   ```

2. **Search existing issues:**
   - [GitHub Issues](https://github.com/pnvoroshilov/claude-code-feature-framework/issues)

3. **Create a new issue:**
   - Include error messages
   - Include relevant logs
   - Include your environment (OS, Docker version, Python version)

4. **Community support:**
   - Open a discussion on GitHub Discussions
   - Include your `docker compose ps` output

## 🆘 Support

For issues and questions:
1. Check the [Troubleshooting](#-troubleshooting) section above
2. Search [existing issues](https://github.com/pnvoroshilov/claude-code-feature-framework/issues)
3. Create a [new issue](https://github.com/pnvoroshilov/claude-code-feature-framework/issues/new) with:
   - Detailed problem description
   - Error messages and logs
   - Environment information (OS, versions)
   - Steps to reproduce

## 🎯 Roadmap

- [ ] **RAG-Enhanced Analysis** - Semantic code search for better context (✅ Completed)
- [ ] Advanced agent configurations with custom tools
- [ ] Integration with more Git providers (GitHub, GitLab, Bitbucket)
- [ ] Real-time task notifications via WebSocket
- [ ] Performance metrics and analytics dashboard
- [ ] Plugin system for custom agents
- [ ] Multi-project workspace support
- [ ] Task templates and automation workflows
- [ ] Integration with CI/CD pipelines
- [ ] Mobile-friendly UI