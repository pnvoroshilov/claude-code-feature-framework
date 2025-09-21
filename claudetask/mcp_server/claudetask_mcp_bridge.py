#!/usr/bin/env python3
"""ClaudeTask MCP Bridge Server

This MCP server provides tools for Claude Code to interact with ClaudeTask backend.
It implements the coordinator-executor pattern where Claude never directly modifies code
but delegates tasks to specialized agents working in git worktrees.
"""

import asyncio
import json
import argparse
import httpx
from typing import Any, Dict, List, Optional
from mcp.server import Server
from mcp.server.models import InitializationOptions
import mcp.types as types


class ClaudeTaskMCPServer:
    """MCP Server for ClaudeTask integration"""
    
    def __init__(self, project_id: str, project_path: str, server_url: str = "http://localhost:3333"):
        self.project_id = project_id
        self.project_path = project_path
        self.server_url = server_url.rstrip("/")
        self.server = Server("claudetask")
        
        # Setup tool handlers
        self._setup_tools()
        
    def _setup_tools(self):
        """Setup MCP tools"""
        
        @self.server.list_tools()
        async def handle_list_tools() -> list[types.Tool]:
            """List available tools"""
            return [
                types.Tool(
                    name="get_next_task",
                    description="Get the highest priority task from backlog",
                    inputSchema={
                        "type": "object",
                        "properties": {},
                        "required": []
                    }
                ),
                types.Tool(
                    name="analyze_task",
                    description="Analyze a specific task and create implementation plan",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "task_id": {
                                "type": "integer",
                                "description": "ID of the task to analyze"
                            }
                        },
                        "required": ["task_id"]
                    }
                ),
                types.Tool(
                    name="update_status",
                    description="Update task status",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "task_id": {
                                "type": "integer",
                                "description": "ID of the task"
                            },
                            "status": {
                                "type": "string",
                                "enum": ["Backlog", "Analysis", "Ready", "In Progress", "Testing", "Code Review", "Done", "Blocked"],
                                "description": "New status for the task"
                            },
                            "comment": {
                                "type": "string",
                                "description": "Optional comment about the status change"
                            }
                        },
                        "required": ["task_id", "status"]
                    }
                ),
                types.Tool(
                    name="create_worktree",
                    description="Create isolated git worktree for task development",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "task_id": {
                                "type": "integer",
                                "description": "ID of the task"
                            }
                        },
                        "required": ["task_id"]
                    }
                ),
                types.Tool(
                    name="verify_connection",
                    description="Verify connection to ClaudeTask backend",
                    inputSchema={
                        "type": "object",
                        "properties": {},
                        "required": []
                    }
                ),
                types.Tool(
                    name="get_task_queue",
                    description="Get current task queue status",
                    inputSchema={
                        "type": "object",
                        "properties": {},
                        "required": []
                    }
                ),
                types.Tool(
                    name="delegate_to_agent",
                    description="Delegate work to a specialized agent (coordinator pattern)",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "task_id": {
                                "type": "integer",
                                "description": "ID of the task"
                            },
                            "agent_type": {
                                "type": "string",
                                "enum": ["task-analyzer", "feature-developer", "bug-fixer", "test-runner", "code-reviewer"],
                                "description": "Type of agent to delegate to"
                            },
                            "instructions": {
                                "type": "string",
                                "description": "Specific instructions for the agent"
                            }
                        },
                        "required": ["task_id", "agent_type", "instructions"]
                    }
                ),
                types.Tool(
                    name="get_tasks_needing_analysis",
                    description="Get all tasks that are waiting for analysis (status = Analysis)",
                    inputSchema={
                        "type": "object",
                        "properties": {},
                        "required": []
                    }
                ),
                types.Tool(
                    name="update_task_analysis",
                    description="Save analysis results back to the task",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "task_id": {
                                "type": "integer",
                                "description": "ID of the task"
                            },
                            "analysis": {
                                "type": "string",
                                "description": "The analysis text/results to save to the task"
                            }
                        },
                        "required": ["task_id", "analysis"]
                    }
                )
            ]

        @self.server.call_tool()
        async def handle_call_tool(name: str, arguments: dict) -> list[types.TextContent]:
            """Handle tool calls"""
            try:
                if name == "get_next_task":
                    return await self._get_next_task()
                elif name == "analyze_task":
                    return await self._analyze_task(arguments["task_id"])
                elif name == "update_status":
                    return await self._update_status(
                        arguments["task_id"],
                        arguments["status"],
                        arguments.get("comment")
                    )
                elif name == "create_worktree":
                    return await self._create_worktree(arguments["task_id"])
                elif name == "verify_connection":
                    return await self._verify_connection()
                elif name == "get_task_queue":
                    return await self._get_task_queue()
                elif name == "delegate_to_agent":
                    return await self._delegate_to_agent(
                        arguments["task_id"],
                        arguments["agent_type"],
                        arguments["instructions"]
                    )
                elif name == "get_tasks_needing_analysis":
                    return await self._get_tasks_needing_analysis()
                elif name == "update_task_analysis":
                    return await self._update_task_analysis(
                        arguments["task_id"],
                        arguments["analysis"]
                    )
                else:
                    raise ValueError(f"Unknown tool: {name}")
                    
            except Exception as e:
                return [types.TextContent(
                    type="text",
                    text=f"Error executing {name}: {str(e)}"
                )]

    async def _get_next_task(self) -> list[types.TextContent]:
        """Get the highest priority task from backlog"""
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(f"{self.server_url}/api/mcp/next-task")
                response.raise_for_status()
                
                task = response.json()
                if not task:
                    return [types.TextContent(
                        type="text",
                        text="No tasks available in backlog"
                    )]
                
                return [types.TextContent(
                    type="text",
                    text=f"""Next Task Retrieved:

ID: {task['id']}
Title: {task['title']}
Type: {task['type']}
Priority: {task['priority']}
Status: {task['status']}

Description:
{task.get('description', 'No description provided')}

You should now analyze this task using the 'analyze_task' tool."""
                )]
                
            except httpx.HTTPError as e:
                return [types.TextContent(
                    type="text",
                    text=f"Failed to get next task: {str(e)}"
                )]

    async def _analyze_task(self, task_id: int) -> list[types.TextContent]:
        """Analyze a task and create implementation plan"""
        async with httpx.AsyncClient() as client:
            try:
                # Get task details
                response = await client.get(f"{self.server_url}/api/tasks/{task_id}")
                response.raise_for_status()
                task = response.json()
                
                # Update status to Analysis
                await client.patch(
                    f"{self.server_url}/api/tasks/{task_id}/status",
                    json={"status": "Analysis", "comment": "Started task analysis"}
                )
                
                return [types.TextContent(
                    type="text",
                    text=f"""Task Analysis Started:

Task: {task['title']}
Type: {task['type']}
Priority: {task['priority']}

Description:
{task.get('description', 'No description provided')}

COORDINATOR INSTRUCTIONS:
As the coordinator, you should:

1. Scan the codebase to understand the current implementation
2. Identify files that will be affected  
3. Assess complexity and potential risks
4. Create a detailed implementation plan
5. Save your analysis using 'update_task_analysis' tool
6. Update status to 'Ready' when analysis is complete
7. Delegate the actual implementation to the appropriate agent

NEVER modify code directly. Use the 'delegate_to_agent' tool for all implementation work.

Next steps:
1. Use tools to explore the codebase
2. Create your detailed analysis text
3. Save analysis using: update_task_analysis with task_id {task_id} and your analysis
4. Change status to 'Ready' using: update_status with task_id {task_id} and status 'Ready'
5. Delegate to appropriate agent for implementation using: delegate_to_agent"""
                )]
                
            except httpx.HTTPError as e:
                return [types.TextContent(
                    type="text",
                    text=f"Failed to analyze task: {str(e)}"
                )]

    async def _update_status(self, task_id: int, status: str, comment: Optional[str] = None) -> list[types.TextContent]:
        """Update task status"""
        async with httpx.AsyncClient() as client:
            try:
                data = {"status": status}
                if comment:
                    data["comment"] = comment
                
                response = await client.patch(
                    f"{self.server_url}/api/tasks/{task_id}/status",
                    json=data
                )
                response.raise_for_status()
                
                return [types.TextContent(
                    type="text",
                    text=f"Task {task_id} status updated to: {status}"
                )]
                
            except httpx.HTTPError as e:
                return [types.TextContent(
                    type="text",
                    text=f"Failed to update status: {str(e)}"
                )]

    async def _create_worktree(self, task_id: int) -> list[types.TextContent]:
        """Create git worktree for task"""
        import subprocess
        import os
        
        try:
            # Get task details
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{self.server_url}/api/tasks/{task_id}")
                response.raise_for_status()
                task = response.json()
            
            # Create branch name
            branch_name = f"feature/task-{task_id}"
            worktree_path = os.path.join(self.project_path, "worktrees", f"task-{task_id}")
            
            # Create worktree
            cmd = [
                "git", "worktree", "add",
                worktree_path,
                "-b", branch_name
            ]
            
            result = subprocess.run(
                cmd,
                cwd=self.project_path,
                capture_output=True,
                text=True
            )
            
            if result.returncode != 0:
                return [types.TextContent(
                    type="text",
                    text=f"Failed to create worktree: {result.stderr}"
                )]
            
            # Update task with branch and worktree info
            async with httpx.AsyncClient() as client:
                await client.patch(
                    f"{self.server_url}/api/tasks/{task_id}",
                    json={
                        "git_branch": branch_name,
                        "worktree_path": worktree_path
                    }
                )
            
            return [types.TextContent(
                type="text",
                text=f"""Worktree created successfully:

Branch: {branch_name}
Path: {worktree_path}

The agent can now work in this isolated environment.
All changes should be made in the worktree directory."""
            )]
            
        except Exception as e:
            return [types.TextContent(
                type="text",
                text=f"Failed to create worktree: {str(e)}"
            )]

    async def _verify_connection(self) -> list[types.TextContent]:
        """Verify connection to backend"""
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(f"{self.server_url}/api/mcp/connection")
                response.raise_for_status()
                status = response.json()
                
                if status["connected"]:
                    return [types.TextContent(
                        type="text",
                        text=f"""✅ ClaudeTask Connection Verified

Project: {status.get('project_name', 'Unknown')}
Path: {status.get('project_path', 'Unknown')}
Total Tasks: {status.get('tasks_count', 0)}
Active Task: {status.get('active_task', {}).get('title', 'None') if status.get('active_task') else 'None'}

Connection to ClaudeTask backend is working properly."""
                    )]
                else:
                    error = status.get("error", "Unknown error")
                    return [types.TextContent(
                        type="text",
                        text=f"❌ Connection Failed: {error}"
                    )]
                    
            except httpx.HTTPError as e:
                return [types.TextContent(
                    type="text",
                    text=f"❌ Connection Failed: {str(e)}"
                )]

    async def _get_task_queue(self) -> list[types.TextContent]:
        """Get task queue status"""
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(f"{self.server_url}/api/mcp/tasks/queue")
                response.raise_for_status()
                queue = response.json()
                
                pending_count = len(queue["pending_tasks"])
                in_progress_count = len(queue["in_progress_tasks"])
                completed_today = queue["completed_today"]
                
                queue_text = f"""📋 Task Queue Status

Pending Tasks: {pending_count}
In Progress: {in_progress_count}  
Completed Today: {completed_today}

"""
                
                if queue["pending_tasks"]:
                    queue_text += "Pending Tasks:\n"
                    for task in queue["pending_tasks"][:5]:  # Show first 5
                        queue_text += f"  #{task['id']} - {task['title']} ({task['priority']})\n"
                    if pending_count > 5:
                        queue_text += f"  ... and {pending_count - 5} more\n"
                
                if queue["in_progress_tasks"]:
                    queue_text += "\nIn Progress Tasks:\n"
                    for task in queue["in_progress_tasks"]:
                        queue_text += f"  #{task['id']} - {task['title']} ({task['status']})\n"
                
                return [types.TextContent(type="text", text=queue_text)]
                
            except httpx.HTTPError as e:
                return [types.TextContent(
                    type="text",
                    text=f"Failed to get task queue: {str(e)}"
                )]

    async def _delegate_to_agent(self, task_id: int, agent_type: str, instructions: str) -> list[types.TextContent]:
        """Delegate work to specialized agent"""
        async with httpx.AsyncClient() as client:
            try:
                # Update task with assigned agent
                await client.patch(
                    f"{self.server_url}/api/tasks/{task_id}",
                    json={"assigned_agent": agent_type}
                )
                
                # Get task details
                response = await client.get(f"{self.server_url}/api/tasks/{task_id}")
                response.raise_for_status()
                task = response.json()
                
                return [types.TextContent(
                    type="text",
                    text=f"""🤖 Task Delegated to {agent_type}

Task: #{task_id} - {task['title']}
Agent: {agent_type}
Worktree: {task.get('worktree_path', 'Not created yet')}

Instructions for {agent_type}:
{instructions}

COORDINATOR REMINDER:
- You have successfully delegated this task
- Monitor progress and provide guidance as needed
- The agent will work in the isolated worktree
- Update task status as work progresses
- Review completed work before merging

The {agent_type} should now:
1. Work in the designated worktree
2. Follow the implementation plan
3. Make necessary code changes
4. Run tests to verify functionality
5. Update you on progress

Next: Monitor the agent's work and update task status accordingly."""
                )]
                
            except httpx.HTTPError as e:
                return [types.TextContent(
                    type="text",
                    text=f"Failed to delegate to agent: {str(e)}"
                )]

    async def _get_tasks_needing_analysis(self) -> list[types.TextContent]:
        """Get all tasks that are waiting for analysis"""
        async with httpx.AsyncClient() as client:
            try:
                # Get active project first
                response = await client.get(f"{self.server_url}/api/projects/active")
                response.raise_for_status()
                project = response.json()
                
                if not project:
                    return [types.TextContent(
                        type="text",
                        text="No active project found"
                    )]
                
                # Get tasks in Analysis status
                response = await client.get(
                    f"{self.server_url}/api/projects/{project['id']}/tasks?status=Analysis"
                )
                response.raise_for_status()
                tasks = response.json()
                
                if not tasks:
                    return [types.TextContent(
                        type="text", 
                        text="🎉 No tasks currently need analysis! All tasks are being handled."
                    )]
                
                analysis_text = f"📋 Tasks Needing Analysis ({len(tasks)} found):\n\n"
                
                for task in tasks:
                    analysis_text += f"""
🔍 Task #{task['id']}: {task['title']}
   Type: {task['type']} | Priority: {task['priority']}
   Description: {task.get('description', 'No description')[:100]}{'...' if len(task.get('description', '')) > 100 else ''}
   
"""
                
                analysis_text += f"""
💡 Next Steps:
1. Use 'analyze_task' tool with a specific task_id to start analysis
2. After analysis, update status to 'Ready' when complete
3. Use 'delegate_to_agent' to assign implementation work

Example: Use analyze_task with task_id {tasks[0]['id']} to start analyzing "{tasks[0]['title']}"
"""
                
                return [types.TextContent(type="text", text=analysis_text)]
                
            except httpx.HTTPError as e:
                return [types.TextContent(
                    type="text",
                    text=f"Failed to get tasks needing analysis: {str(e)}"
                )]

    async def _update_task_analysis(self, task_id: int, analysis: str) -> list[types.TextContent]:
        """Save analysis results back to the task"""
        async with httpx.AsyncClient() as client:
            try:
                # Update task analysis field
                response = await client.patch(
                    f"{self.server_url}/api/tasks/{task_id}",
                    json={"analysis": analysis}
                )
                response.raise_for_status()
                
                # Get updated task details
                task_response = await client.get(f"{self.server_url}/api/tasks/{task_id}")
                task_response.raise_for_status()
                task = task_response.json()
                
                return [types.TextContent(
                    type="text",
                    text=f"""✅ Analysis Saved Successfully!

Task: #{task_id} - {task['title']}
Status: {task['status']}

Analysis has been saved to the task. You can now:
1. Change task status to 'Ready' using update_status tool
2. Delegate implementation to an agent using delegate_to_agent tool
3. Continue with the next steps in your workflow

The task now contains your analysis and is ready for the next phase."""
                )]
                
            except httpx.HTTPError as e:
                return [types.TextContent(
                    type="text",
                    text=f"Failed to save analysis: {str(e)}"
                )]

    async def run(self):
        """Run the MCP server"""
        from mcp.server.stdio import stdio_server
        from mcp.server.models import ServerCapabilities
        
        async with stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream,
                write_stream,
                InitializationOptions(
                    server_name="claudetask",
                    server_version="1.0.0",
                    capabilities=ServerCapabilities(
                        tools={}
                    )
                )
            )


async def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="ClaudeTask MCP Bridge Server")
    parser.add_argument("--project-id", required=True, help="Project ID")
    parser.add_argument("--project-path", required=True, help="Project path")
    parser.add_argument("--server", default="http://localhost:3333", help="Backend server URL")
    
    args = parser.parse_args()
    
    server = ClaudeTaskMCPServer(
        project_id=args.project_id,
        project_path=args.project_path,
        server_url=args.server
    )
    
    await server.run()


if __name__ == "__main__":
    asyncio.run(main())