#!/bin/bash
# ClaudeTask MCP Docker Wrapper
# This script allows Claude Code to communicate with the MCP server running in Docker

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Parse arguments - they come from .mcp.json configuration
PROJECT_ID=""
PROJECT_PATH=""
SERVER_URL="http://localhost:3333"

while [[ $# -gt 0 ]]; do
  case $1 in
    --project-id)
      PROJECT_ID="$2"
      shift 2
      ;;
    --project-path)
      PROJECT_PATH="$2"
      shift 2
      ;;
    --server)
      SERVER_URL="$2"
      shift 2
      ;;
    *)
      shift
      ;;
  esac
done

# Ensure the MCP server image is built
docker-compose -f "$SCRIPT_DIR/../docker-compose.yml" build mcp_server 2>/dev/null

# Run the MCP server in Docker with stdio communication
exec docker run --rm -i \
  --network claudecodefeatureframework_claudetask-network \
  -v "$PROJECT_PATH:/project:rw" \
  -v /var/run/docker.sock:/var/run/docker.sock \
  -e PROJECT_ID="$PROJECT_ID" \
  -e PROJECT_PATH="/project" \
  -e SERVER_URL="http://backend:3333" \
  claudetask-mcp:latest \
  --project-id "$PROJECT_ID" \
  --project-path "/project" \
  --server "http://backend:3333"