"""MCP Client Service for backend integration"""

import httpx
import os
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)


class MCPService:
    """Service for communicating with MCP tools"""
    
    def __init__(self, server_url: str = "http://localhost:3333"):
        self.server_url = server_url.rstrip("/")
        
    async def trigger_task_analysis(self, task_id: int) -> Optional[Dict[str, Any]]:
        """
        Trigger task analysis via MCP.
        This simulates what Claude Code would do when it calls analyze_task.
        """
        try:
            # Get active project to find the MCP server details
            async with httpx.AsyncClient() as client:
                # Get active project
                response = await client.get(f"{self.server_url}/api/projects/active")
                if response.status_code != 200:
                    logger.error("No active project found for MCP analysis")
                    return None
                
                project = response.json()
                if not project:
                    logger.error("No active project found")
                    return None
                
                # Check if MCP server is available by testing connection
                try:
                    mcp_response = await client.get(f"{self.server_url}/api/mcp/connection")
                    if mcp_response.status_code != 200:
                        logger.error("MCP server not available")
                        return None
                    
                    connection_status = mcp_response.json()
                    if not connection_status.get("connected"):
                        logger.error("MCP server not connected")
                        return None
                        
                except Exception as e:
                    logger.error(f"Failed to check MCP connection: {e}")
                    return None
                
                # Simulate the MCP analyze_task call
                # In a real implementation, this would use the MCP protocol
                # For now, we'll make an HTTP call to our own MCP endpoint
                analyze_response = await client.post(
                    f"{self.server_url}/api/mcp/analyze-task",
                    json={"task_id": task_id}
                )
                
                if analyze_response.status_code == 200:
                    result = analyze_response.json()
                    logger.info(f"Task {task_id} analysis triggered successfully")
                    return result
                else:
                    logger.error(f"Failed to trigger task analysis: {analyze_response.text}")
                    return None
                    
        except Exception as e:
            logger.error(f"Error triggering task analysis: {e}")
            return None
    
    async def notify_claude_code(self, task_id: int, message: str) -> bool:
        """
        Send a notification to Claude Code about task status.
        This could be used to notify Claude Code that a task needs attention.
        """
        try:
            # This is a placeholder for future Claude Code notification system
            logger.info(f"Notification for task {task_id}: {message}")
            return True
        except Exception as e:
            logger.error(f"Failed to notify Claude Code: {e}")
            return False


# Global instance
mcp_service = MCPService()