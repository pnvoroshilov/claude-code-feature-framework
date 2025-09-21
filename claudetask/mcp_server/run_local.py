#!/usr/bin/env python3
"""
Local MCP Server Runner
"""
import sys
import subprocess
import os

def main():
    # Activate virtual environment and run the MCP server
    server_path = os.path.dirname(os.path.abspath(__file__))
    venv_python = os.path.join(server_path, "venv", "bin", "python")
    server_script = os.path.join(server_path, "claudetask_mcp_bridge.py")
    
    # Default arguments for local testing
    args = [
        venv_python, server_script,
        "--project-id", "local-test",
        "--project-path", "/Users/pavelvorosilov/Desktop/Work/Start Up/Claude Code Feature Framework",
        "--server", "http://localhost:3333"
    ]
    
    # Override with command line arguments if provided
    if len(sys.argv) > 1:
        args = [venv_python, server_script] + sys.argv[1:]
    
    print(f"Starting MCP server with args: {args}")
    subprocess.run(args)

if __name__ == "__main__":
    main()