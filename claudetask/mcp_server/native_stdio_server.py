#!/usr/bin/env python3
"""Native MCP STDIO Server for ClaudeTask"""

import sys
import os
import asyncio
import argparse
import logging

# Add parent directory to path to import the bridge
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mcp_server.claudetask_mcp_bridge import ClaudeTaskMCPServer

# Setup logging to stderr so it doesn't interfere with stdio
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stderr
)
logger = logging.getLogger(__name__)

async def main():
    """Main entry point for STDIO server"""
    # Default configuration - can be overridden with arguments
    project_id = os.environ.get('CLAUDETASK_PROJECT_ID', 'ff9cc152-3f38-49ab-bec0-0e7cbf84594a')
    project_path = os.environ.get('CLAUDETASK_PROJECT_PATH', '/Users/pavelvorosilov/Desktop/Work/Start Up/Claude Code Feature Framework')
    backend_url = os.environ.get('CLAUDETASK_BACKEND_URL', 'http://localhost:3333')
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="ClaudeTask MCP STDIO Server")
    parser.add_argument('--project-id', default=project_id, help='Project ID')
    parser.add_argument('--project-path', default=project_path, help='Project path')
    parser.add_argument('--server', default=backend_url, help='Backend server URL')
    
    args = parser.parse_args()
    
    logger.info(f"Starting ClaudeTask MCP STDIO server for project {args.project_id}")
    
    # Create and run the MCP server
    server = ClaudeTaskMCPServer(
        project_id=args.project_id,
        project_path=args.project_path,
        server_url=args.server
    )
    
    # Run the server using native MCP protocol
    await server.run()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Server error: {e}", exc_info=True)
        sys.exit(1)