#!/usr/bin/env python3
"""Native MCP STDIO Server for ClaudeTask"""

import sys
import os
import asyncio
import argparse
import logging
import httpx
from pathlib import Path

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

async def get_project_id_by_path(project_path: str, backend_url: str) -> str | None:
    """
    Get project ID by querying backend API with project path.

    Args:
        project_path: Absolute path to the project
        backend_url: Backend API URL

    Returns:
        Project ID if found, None otherwise
    """
    try:
        # Normalize path to absolute
        abs_path = str(Path(project_path).resolve())

        async with httpx.AsyncClient(timeout=5.0) as client:
            # Query backend for project by path
            response = await client.get(f"{backend_url}/api/projects")
            if response.status_code == 200:
                projects = response.json()
                for project in projects:
                    if project.get("path") == abs_path:
                        logger.info(f"Found project ID {project['id']} for path {abs_path}")
                        return project["id"]

        logger.warning(f"No project found for path: {abs_path}")
        return None

    except Exception as e:
        logger.error(f"Failed to get project ID by path: {e}")
        return None

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

    # Auto-detect project ID by path if not explicitly provided
    final_project_id = args.project_id
    if args.project_id == project_id:  # Using default/env value
        detected_id = await get_project_id_by_path(args.project_path, args.server)
        if detected_id:
            final_project_id = detected_id
            logger.info(f"Auto-detected project ID: {detected_id}")
        else:
            logger.warning(f"Could not auto-detect project ID, using configured value: {args.project_id}")

    logger.info(f"Starting ClaudeTask MCP STDIO server for project {final_project_id}")

    # Create and run the MCP server
    server = ClaudeTaskMCPServer(
        project_id=final_project_id,
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