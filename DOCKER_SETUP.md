# ClaudeTask Docker Setup

## Quick Start

All ClaudeTask services run in Docker containers for easy deployment.

### 1. Start All Services

```bash
# Build and start all containers
docker-compose up -d

# Or rebuild if needed
docker-compose up -d --build
```

### 2. Access Services

- **Frontend UI**: http://localhost:3334
- **Backend API**: http://localhost:3333
- **API Docs**: http://localhost:3333/docs

### 3. MCP Server (for Claude Code)

The MCP server also runs in Docker via a wrapper script. When you initialize a project with ClaudeTask, it automatically configures `.mcp.json` to use the Docker wrapper.

## Docker Architecture

```
claudetask-backend     # FastAPI backend (port 3333)
claudetask-frontend    # React frontend (port 3334)  
claudetask-mcp        # MCP server (stdio, runs on demand)
```

All containers share the `claudetask-network` for internal communication.

## MCP Docker Integration

The MCP server runs in Docker when Claude Code connects to it:

1. **Automatic**: When Claude Code reads `.mcp.json`, it launches the MCP server via the Docker wrapper
2. **Manual Test**: Use the test script to verify MCP is working:
   ```bash
   ./test_mcp_docker.sh
   ```

## Managing Containers

```bash
# View running containers
docker ps

# View logs
docker-compose logs -f backend
docker-compose logs -f frontend

# Stop all services
docker-compose down

# Stop and remove volumes
docker-compose down -v

# Rebuild specific service
docker-compose build backend
docker-compose up -d backend
```

## Environment Variables

Services communicate internally using Docker network:
- Backend connects to database at `/app/data/claudetask.db`
- Frontend connects to backend at `http://backend:3333`
- MCP connects to backend at `http://backend:3333`

## Troubleshooting

### Port Already in Use
If ports 3333 or 3334 are already in use:
```bash
# Find process using port
lsof -i :3333
lsof -i :3334

# Kill process or change ports in docker-compose.yml
```

### MCP Connection Issues
The MCP server needs the backend to be running:
```bash
# Ensure backend is healthy
docker ps
# Look for (healthy) status

# Test MCP connection
./test_mcp_docker.sh
```

### Database Issues
Database is stored in Docker volume:
```bash
# Reset database (WARNING: deletes all data)
docker-compose down -v
docker-compose up -d
```

## Development Mode

For development with hot-reload:
```bash
# Backend with hot-reload
docker-compose run --rm -p 3333:3333 -v $(pwd)/claudetask/backend:/app backend

# Frontend with hot-reload  
docker-compose run --rm -p 3334:3000 -v $(pwd)/claudetask/frontend:/app frontend
```

## Production Deployment

For production, use the nginx profile:
```bash
docker-compose --profile production up -d
```

This adds an nginx reverse proxy on port 80.