#!/bin/bash
# Test script for MCP Docker server

echo "Testing ClaudeTask MCP Server in Docker..."
echo ""

# Test initialization and tool listing
./claudetask/mcp_docker_wrapper.sh \
  --project-id test-123 \
  --project-path "/Users/pavelvorosilov/Desktop/Work/Start Up/Claude Code Feature Framework" \
  --server http://localhost:3333 << 'EOF'
{"jsonrpc":"2.0","method":"initialize","params":{"protocolVersion":"1.0.0","capabilities":{},"clientInfo":{"name":"test","version":"1.0"}},"id":1}
{"jsonrpc":"2.0","method":"initialized","params":{},"id":2}
{"jsonrpc":"2.0","method":"tools/list","params":{},"id":3}
EOF