#!/usr/bin/env python3
"""HTTP MCP Server for ClaudeTask"""

import asyncio
import json
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# Import the MCP bridge functionality
from claudetask_mcp_bridge import ClaudeTaskMCPServer

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="ClaudeTask MCP Server", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3334", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global MCP bridge instance
mcp_bridge: Optional[ClaudeTaskMCPServer] = None

@app.on_event("startup")
async def startup_event():
    """Initialize MCP bridge on startup"""
    global mcp_bridge
    
    # Default project configuration
    project_id = "ff9cc152-3f38-49ab-bec0-0e7cbf84594a"
    project_path = "/Users/pavelvorosilov/Desktop/Work/Start Up/Claude Code Feature Framework"
    backend_url = "http://localhost:3333"
    
    try:
        mcp_bridge = ClaudeTaskMCPServer(
            project_id=project_id,
            project_path=project_path,
            server_url=backend_url
        )
        logger.info(f"MCP Server initialized for project {project_id}")
    except Exception as e:
        logger.error(f"Failed to initialize MCP server: {e}")
        mcp_bridge = None

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "mcp_bridge_ready": mcp_bridge is not None
    }

@app.get("/tools")
async def list_tools():
    """List available MCP tools"""
    if not mcp_bridge:
        raise HTTPException(status_code=503, detail="MCP bridge not initialized")
    
    return {
        "tools": [
            {
                "name": "get_task_queue",
                "description": "View all tasks in the queue",
                "input_schema": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            },
            {
                "name": "get_next_task",
                "description": "Get the highest priority task ready for work",
                "input_schema": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            },
            {
                "name": "get_task",
                "description": "Get details of a specific task",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "task_id": {"type": "integer"}
                    },
                    "required": ["task_id"]
                }
            },
            {
                "name": "analyze_task",
                "description": "Analyze a specific task and create implementation plan",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "task_id": {"type": "integer"}
                    },
                    "required": ["task_id"]
                }
            },
            {
                "name": "update_task_analysis",
                "description": "Save analysis results back to the task",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "task_id": {"type": "integer"},
                        "analysis": {"type": "string"}
                    },
                    "required": ["task_id", "analysis"]
                }
            },
            {
                "name": "complete_task",
                "description": "Complete a task and merge its branch",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "task_id": {"type": "integer"},
                        "create_pr": {"type": "boolean", "default": False}
                    },
                    "required": ["task_id"]
                }
            },
            {
                "name": "update_status",
                "description": "Update task status and receive next steps",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "task_id": {"type": "integer"},
                        "status": {"type": "string", "enum": ["Backlog", "Analysis", "Ready", "In Progress", "Testing", "Code Review", "Done", "Blocked"]}
                    },
                    "required": ["task_id", "status"]
                }
            },
            {
                "name": "create_worktree",
                "description": "Create a git worktree for a task",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "task_id": {"type": "integer"},
                        "branch_name": {"type": "string"}
                    },
                    "required": ["task_id"]
                }
            },
            {
                "name": "delegate_to_agent",
                "description": "Delegate task to a specialist agent",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "task_id": {"type": "integer"},
                        "agent_type": {"type": "string"},
                        "instructions": {"type": "string"}
                    },
                    "required": ["task_id", "agent_type", "instructions"]
                }
            },
            {
                "name": "start_claude_session",
                "description": "Start a Claude Code session for a task",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "task_id": {"type": "integer"},
                        "context": {"type": "string", "default": ""}
                    },
                    "required": ["task_id"]
                }
            },
            {
                "name": "get_session_status",
                "description": "Get status of Claude sessions",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "task_id": {"type": "integer"}
                    }
                }
            }
        ]
    }

@app.post("/tools/{tool_name}")
async def call_tool(tool_name: str, arguments: Dict[str, Any]):
    """Execute an MCP tool"""
    if not mcp_bridge:
        raise HTTPException(status_code=503, detail="MCP bridge not initialized")
    
    try:
        # Map tool names to methods
        tool_methods = {
            "get_task_queue": mcp_bridge._get_task_queue,
            "get_next_task": mcp_bridge._get_next_task,
            "get_task": mcp_bridge._get_task,
            "analyze_task": mcp_bridge._analyze_task,
            "update_task_analysis": mcp_bridge._update_task_analysis,
            "complete_task": mcp_bridge._complete_task,
            "update_status": mcp_bridge._update_status,
            "create_worktree": mcp_bridge._create_worktree,
            "delegate_to_agent": mcp_bridge._delegate_to_agent,
            "start_claude_session": mcp_bridge._start_claude_session,
            "get_session_status": mcp_bridge._get_session_status
        }
        
        if tool_name not in tool_methods:
            raise HTTPException(status_code=404, detail=f"Tool '{tool_name}' not found")
        
        method = tool_methods[tool_name]
        
        # Call the method with appropriate arguments
        if tool_name == "get_task_queue":
            result = await method()
        elif tool_name == "get_next_task":
            result = await method()
        elif tool_name == "get_task":
            result = await method(arguments.get("task_id"))
        elif tool_name == "analyze_task":
            result = await method(arguments.get("task_id"))
        elif tool_name == "update_task_analysis":
            result = await method(arguments.get("task_id"), arguments.get("analysis"))
        elif tool_name == "complete_task":
            result = await method(arguments.get("task_id"), arguments.get("create_pr", False))
        elif tool_name == "update_status":
            result = await method(arguments.get("task_id"), arguments.get("status"))
        elif tool_name == "create_worktree":
            result = await method(arguments.get("task_id"), arguments.get("branch_name"))
        elif tool_name == "delegate_to_agent":
            result = await method(arguments.get("task_id"), arguments.get("agent_type"), arguments.get("instructions"))
        elif tool_name == "start_claude_session":
            result = await method(arguments.get("task_id"), arguments.get("context", ""))
        elif tool_name == "get_session_status":
            result = await method(arguments.get("task_id"))
        else:
            result = await method(**arguments)
        
        return {
            "success": True,
            "result": result,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error executing tool '{tool_name}': {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/agents")
async def list_agents():
    """List available agents"""
    if not mcp_bridge:
        raise HTTPException(status_code=503, detail="MCP bridge not initialized")
    
    return {"agents": mcp_bridge.available_agents}

@app.get("/project/info")
async def get_project_info():
    """Get current project information"""
    if not mcp_bridge:
        raise HTTPException(status_code=503, detail="MCP bridge not initialized")
    
    return {
        "project_id": mcp_bridge.project_id,
        "project_path": mcp_bridge.project_path,
        "backend_url": mcp_bridge.backend_url
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=3335)