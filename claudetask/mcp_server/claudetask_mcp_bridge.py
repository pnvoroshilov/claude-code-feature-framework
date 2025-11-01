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
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional
from mcp.server import Server
from mcp.server.models import InitializationOptions
import mcp.types as types

# Add parent directory to path for config import
sys.path.insert(0, str(Path(__file__).parent.parent))
from config import get_config

# RAG imports
from rag import RAGService, RAGConfig


class ClaudeTaskMCPServer:
    """MCP Server for ClaudeTask integration"""
    
    def __init__(self, project_id: str, project_path: str, server_url: str = "http://localhost:3333"):
        self.project_id = project_id
        self.project_path = project_path
        self.server_url = server_url.rstrip("/")
        self.server = Server("claudetask")
        
        # Initialize logger
        import logging
        self.logger = logging.getLogger(__name__)
        
        # Available local agents (verified to exist in framework-assets/claude-agents/)
        self.available_agents = [
            "ai-implementation-expert",
            "api-validator",
            "backend-architect",
            "background-tester",
            "business-analyst",
            "context-analyzer",
            "data-formatter",
            "devops-engineer",
            "docs-generator",
            "frontend-developer",
            "fullstack-code-reviewer",
            "mcp-engineer",
            "memory-sync",
            "mobile-react-expert",
            "python-api-expert",
            "systems-analyst",
            "ux-ui-researcher",
            "web-tester"
        ]
        
        # Agent mapping for task types and statuses with intelligent specialization
        self.agent_mappings = {
            "Feature": {
                "Ready": "frontend-developer",
                "In Progress": "frontend-developer",
                "Testing": None,  # Manual testing only
                "Code Review": "fullstack-code-reviewer"
            },
            "Bug": {
                "Ready": "backend-architect",
                "In Progress": "backend-architect",
                "Testing": None,  # Manual testing only
                "Code Review": "fullstack-code-reviewer"
            },
            "Refactoring": {
                "Ready": "backend-architect",
                "In Progress": "backend-architect",
                "Testing": None,  # Manual testing only
                "Code Review": "fullstack-code-reviewer"
            },
            "Documentation": {
                "Ready": "docs-generator",
                "In Progress": "docs-generator",
                "Testing": None,  # Manual review only
                "Code Review": "fullstack-code-reviewer"
            },
            "Performance": {
                "Ready": "devops-engineer",
                "In Progress": "devops-engineer",
                "Testing": None,  # Manual testing only
                "Code Review": "fullstack-code-reviewer"
            },
            "Security": {
                "Ready": "devops-engineer",
                "In Progress": "devops-engineer",
                "Testing": None,  # Manual testing only
                "Code Review": "fullstack-code-reviewer"
            },
            "DevOps": {
                "Ready": "devops-engineer",
                "In Progress": "devops-engineer",
                "Testing": None,  # Manual testing only
                "Code Review": "fullstack-code-reviewer"
            },
            "MCP": {
                "Ready": "mcp-engineer",
                "In Progress": "mcp-engineer",
                "Testing": None,  # Manual testing only
                "Code Review": "fullstack-code-reviewer"
            },
            "Integration": {
                "Ready": "mcp-engineer",
                "In Progress": "mcp-engineer",
                "Testing": "background-tester",
                "Code Review": "fullstack-code-reviewer"
            },
            "API": {
                "Ready": "api-validator",
                "In Progress": "python-api-expert",
                "Testing": "api-validator",
                "Code Review": "fullstack-code-reviewer"
            },
            "Mobile": {
                "Ready": "mobile-react-expert",
                "In Progress": "mobile-react-expert",
                "Testing": "background-tester",
                "Code Review": "fullstack-code-reviewer"
            },
            "Testing": {
                "Ready": "background-tester",
                "In Progress": "background-tester",
                "Testing": "background-tester",
                "Code Review": "fullstack-code-reviewer"
            },
            "E2E": {
                "Ready": "web-tester",
                "In Progress": "web-tester",
                "Testing": "web-tester",
                "Code Review": "fullstack-code-reviewer"
            },
            "UX": {
                "Ready": "ux-ui-researcher",
                "In Progress": "ux-ui-researcher",
                "Testing": "ux-ui-researcher",
                "Code Review": "ux-ui-researcher"
            },
            "UI": {
                "Ready": "ux-ui-researcher",
                "In Progress": "ux-ui-researcher",
                "Testing": "web-tester",
                "Code Review": "ux-ui-researcher"
            },
            "AI": {
                "Ready": "ai-implementation-expert",
                "In Progress": "ai-implementation-expert",
                "Testing": "background-tester",
                "Code Review": "fullstack-code-reviewer"
            },
            "ML": {
                "Ready": "ai-implementation-expert",
                "In Progress": "ai-implementation-expert",
                "Testing": "background-tester",
                "Code Review": "fullstack-code-reviewer"
            },
            "Context": {
                "Ready": "context-analyzer",
                "In Progress": "context-analyzer",
                "Testing": "background-tester",
                "Code Review": "fullstack-code-reviewer"
            },
            "Memory": {
                "Ready": "memory-sync",
                "In Progress": "memory-sync",
                "Testing": "background-tester",
                "Code Review": "fullstack-code-reviewer"
            },
            "Data": {
                "Ready": "data-formatter",
                "In Progress": "data-formatter",
                "Testing": "background-tester",
                "Code Review": "fullstack-code-reviewer"
            }
        }
        
        # Status progression flow
        self.status_flow = [
            "Backlog", "Analysis", "Ready", "In Progress",
            "Testing", "Code Review", "PR", "Done"
        ]

        # Initialize RAG service with centralized config
        config = get_config(project_path)
        self.rag_service = RAGService(RAGConfig(
            chromadb_path=str(config.chromadb_dir),
            embedding_model="all-MiniLM-L6-v2",
            chunk_size=500,
            chunk_overlap=50
        ))
        self.rag_initialized = False  # Will be set to True after async init

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
                    name="get_task",
                    description="Get details of a specific task",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "task_id": {
                                "type": "integer",
                                "description": "ID of the task to get"
                            }
                        },
                        "required": ["task_id"]
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
                                "enum": ["Backlog", "Analysis", "Ready", "In Progress", "Testing", "Code Review", "PR", "Done", "Blocked"],
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
                                "enum": [
                                    "ai-implementation-expert", "api-validator", "backend-architect",
                                    "background-tester", "business-analyst", "context-analyzer", 
                                    "data-formatter", "devops-engineer", "docs-generator", 
                                    "frontend-developer", "fullstack-code-reviewer", "mcp-engineer", 
                                    "memory-sync", "mobile-react-expert", "python-api-expert",
                                    "systems-analyst", "ux-ui-researcher", "web-tester"
                                ],
                                "description": "Type of agent to delegate to (all available specialized agents)"
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
                ),
                types.Tool(
                    name="recommend_agent",
                    description="Get intelligent agent recommendation based on task context",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "task_type": {
                                "type": "string",
                                "description": "Type of the task"
                            },
                            "status": {
                                "type": "string",
                                "description": "Current status of the task"
                            },
                            "title": {
                                "type": "string",
                                "description": "Task title for context analysis"
                            },
                            "description": {
                                "type": "string",
                                "description": "Task description for context analysis"
                            }
                        },
                        "required": ["task_type", "status", "title", "description"]
                    }
                ),
                types.Tool(
                    name="list_agents",
                    description="Get information about all available specialized agents",
                    inputSchema={
                        "type": "object",
                        "properties": {},
                        "required": []
                    }
                ),
                types.Tool(
                    name="complete_task",
                    description="Merge task branch to main and cleanup worktree",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "task_id": {
                                "type": "integer",
                                "description": "Task ID to complete"
                            },
                            "create_pr": {
                                "type": "boolean",
                                "description": "Create PR instead of direct merge (default: false)"
                            }
                        },
                        "required": ["task_id"]
                    }
                ),
                types.Tool(
                    name="start_claude_session",
                    description="Start a Claude Code session for a task",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "task_id": {
                                "type": "integer",
                                "description": "Task ID to start session for"
                            },
                            "context": {
                                "type": "string",
                                "description": "Additional context for the session"
                            }
                        },
                        "required": ["task_id"]
                    }
                ),
                types.Tool(
                    name="get_session_status",
                    description="Get current Claude session status for a task",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "task_id": {
                                "type": "integer",
                                "description": "Task ID to check session for"
                            }
                        },
                        "required": ["task_id"]
                    }
                ),
                types.Tool(
                    name="append_stage_result",
                    description="Append a new stage result to task's cumulative results",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "task_id": {
                                "type": "integer",
                                "description": "ID of the task to append stage result to"
                            },
                            "status": {
                                "type": "string",
                                "enum": ["Analysis", "In Progress", "Testing", "Code Review", "PR", "Done"],
                                "description": "Current status/stage of the task"
                            },
                            "summary": {
                                "type": "string",
                                "description": "Summary of what was accomplished in this stage"
                            },
                            "details": {
                                "type": "string",
                                "description": "Optional detailed information about this stage"
                            }
                        },
                        "required": ["task_id", "status", "summary"]
                    }
                ),
                types.Tool(
                    name="set_testing_urls",
                    description="Save testing environment URLs for a task (e.g., frontend, backend URLs)",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "task_id": {
                                "type": "integer",
                                "description": "ID of the task"
                            },
                            "urls": {
                                "type": "object",
                                "description": "Dictionary of environment names to their URLs (e.g., {\"frontend\": \"http://localhost:3001\", \"backend\": \"http://localhost:3333\"})",
                                "additionalProperties": {
                                    "type": "string"
                                }
                            }
                        },
                        "required": ["task_id", "urls"]
                    }
                ),
                types.Tool(
                    name="stop_session",
                    description="Stop/complete the Claude session for a task and kill any test server processes",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "task_id": {
                                "type": "integer",
                                "description": "ID of the task to stop session for"
                            }
                        },
                        "required": ["task_id"]
                    }
                ),
                types.Tool(
                    name="search_codebase",
                    description="Semantic search across codebase using RAG to find relevant code chunks. Returns multiple results for comprehensive analysis.",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "Natural language query describing what code you're looking for"
                            },
                            "top_k": {
                                "type": "integer",
                                "description": "Number of results to return (default: 20, max: 100). Use higher values for comprehensive analysis.",
                                "default": 20,
                                "minimum": 1,
                                "maximum": 100
                            },
                            "language": {
                                "type": "string",
                                "description": "Optional: filter by programming language (python, javascript, typescript, etc.)"
                            },
                            "min_similarity": {
                                "type": "number",
                                "description": "Optional: minimum similarity threshold (0.0-1.0). Only return results above this threshold.",
                                "minimum": 0.0,
                                "maximum": 1.0
                            }
                        },
                        "required": ["query"]
                    }
                ),
                types.Tool(
                    name="find_similar_tasks",
                    description="Find similar historical tasks using RAG to learn from past implementations",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "task_description": {
                                "type": "string",
                                "description": "Description of the current task"
                            },
                            "top_k": {
                                "type": "integer",
                                "description": "Number of similar tasks to return (default: 10, max: 50)",
                                "default": 10,
                                "minimum": 1,
                                "maximum": 50
                            }
                        },
                        "required": ["task_description"]
                    }
                ),
                types.Tool(
                    name="reindex_codebase",
                    description="Trigger incremental reindexing of codebase (used after merge to main)",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "full_reindex": {
                                "type": "boolean",
                                "description": "If true, perform full reindex instead of incremental (default: false)",
                                "default": False
                            }
                        },
                        "required": []
                    }
                ),
                types.Tool(
                    name="index_codebase",
                    description="Index entire codebase for RAG semantic search. Use this for initial indexing or when you want to rebuild the entire index from scratch.",
                    inputSchema={
                        "type": "object",
                        "properties": {},
                        "required": []
                    }
                ),
                types.Tool(
                    name="index_files",
                    description="Index or re-index specific files for RAG semantic search. Useful for updating the index after modifying specific files.",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "file_paths": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "List of file paths to index (absolute or relative to project root)"
                            }
                        },
                        "required": ["file_paths"]
                    }
                ),
                types.Tool(
                    name="complete_skill_creation_session",
                    description="Complete skill creation session by sending /exit to Claude terminal and stopping the process. MUST be called after skill files are created to clean up the session.",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "session_id": {
                                "type": "string",
                                "description": "Session ID of the skill creation session (format: skill-creation-*)"
                            }
                        },
                        "required": ["session_id"]
                    }
                )
            ]

        @self.server.call_tool()
        async def handle_call_tool(name: str, arguments: dict) -> list[types.TextContent]:
            """Handle tool calls"""
            try:
                if name == "get_next_task":
                    return await self._get_next_task()
                elif name == "get_task":
                    return await self._get_task(arguments["task_id"])
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
                elif name == "recommend_agent":
                    return await self._recommend_agent(
                        arguments["task_type"],
                        arguments["status"],
                        arguments["title"],
                        arguments["description"]
                    )
                elif name == "list_agents":
                    return await self._list_agents()
                elif name == "complete_task":
                    return await self._complete_task(
                        arguments["task_id"],
                        arguments.get("create_pr", False)
                    )
                elif name == "start_claude_session":
                    return await self._start_claude_session(
                        arguments["task_id"],
                        arguments.get("context", "")
                    )
                elif name == "get_session_status":
                    return await self._get_session_status(
                        arguments["task_id"]
                    )
                elif name == "append_stage_result":
                    return await self._append_stage_result(
                        arguments["task_id"],
                        arguments["status"],
                        arguments["summary"],
                        arguments.get("details")
                    )
                elif name == "set_testing_urls":
                    return await self._set_testing_urls(
                        arguments["task_id"],
                        arguments["urls"]
                    )
                elif name == "stop_session":
                    return await self._stop_session(
                        arguments["task_id"]
                    )
                elif name == "search_codebase":
                    return await self._search_codebase(
                        arguments["query"],
                        arguments.get("top_k", 20),
                        arguments.get("language"),
                        arguments.get("min_similarity")
                    )
                elif name == "find_similar_tasks":
                    return await self._find_similar_tasks(
                        arguments["task_description"],
                        arguments.get("top_k", 10)
                    )
                elif name == "reindex_codebase":
                    return await self._reindex_codebase(
                        arguments.get("full_reindex", False)
                    )
                elif name == "index_codebase":
                    return await self._index_codebase()
                elif name == "index_files":
                    return await self._index_files(
                        arguments["file_paths"]
                    )
                elif name == "complete_skill_creation_session":
                    return await self._complete_skill_creation_session(
                        arguments["session_id"]
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
                    text=f"""✅ TASK RETRIEVED - IMMEDIATE ACTION REQUIRED:

ID: {task['id']}
Title: {task['title']}
Type: {task['type']}
Priority: {task['priority']}
Status: {task['status']}

Description:
{task.get('description', 'No description provided')}

⚡ EXECUTE IMMEDIATELY:
mcp:analyze_task {task['id']}

This command will start the analysis process for this task."""
                )]
                
            except httpx.HTTPError as e:
                return [types.TextContent(
                    type="text",
                    text=f"Failed to get next task: {str(e)}"
                )]
    
    async def _get_task(self, task_id: int) -> list[types.TextContent]:
        """Get details of a specific task"""
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(f"{self.server_url}/api/tasks/{task_id}")
                response.raise_for_status()
                
                task = response.json()
                
                # Determine next steps based on current status
                next_steps = self._get_next_steps_for_status(task['status'], task['type'])
                
                return [types.TextContent(
                    type="text",
                    text=f"""📋 TASK DETAILS - Task #{task_id}

Title: {task['title']}
Type: {task['type']}
Priority: {task['priority']}
Status: {task['status']}

Description:
{task.get('description', 'No description provided')}

Analysis:
{task.get('analysis', 'Not analyzed yet')}

{next_steps}"""
                )]
                
            except httpx.HTTPError as e:
                return [types.TextContent(
                    type="text",
                    text=f"Failed to get task {task_id}: {str(e)}"
                )]
    
    def _get_next_steps_for_status(self, status: str, task_type: str) -> str:
        """Get next steps instructions based on current task status"""
        if status == "Backlog":
            return """📍 NEXT STEPS (Status: Backlog):
1. Analyze the task: mcp:analyze_task <task_id>
2. The analysis will automatically move status to 'Analysis'
3. Complete your analysis and save it
4. Move to 'Ready' when analysis is complete"""
        
        elif status == "Analysis":
            return """📍 NEXT STEPS (Status: Analysis):
⚠️ MANDATORY DUAL DELEGATION - ALWAYS DELEGATE TO BOTH:

1. FIRST delegate to Business Analyst:
   mcp:delegate_to_agent <task_id> business-analyst "Analyze business requirements"
   
2. THEN delegate to Systems Analyst:
   mcp:delegate_to_agent <task_id> systems-analyst "Analyze technical requirements"
   
3. Save combined analysis: mcp:update_task_analysis <task_id> "<combined_analysis>"

4. ⚠️ MANDATORY: Update to In Progress: mcp:update_status <task_id> "In Progress"
   (NEVER update to Ready - go directly to In Progress)"""
        
        elif status == "Ready":
            return """⚠️ DEPRECATED STATUS - Should not be in Ready
1. Immediately update to 'In Progress': mcp:update_status <task_id> "In Progress"
2. Tasks should go: Analysis → In Progress (not Ready)
3. After updating status, delegate to appropriate agent"""
        
        elif status == "In Progress":
            return """📍 NEXT STEPS (Status: In Progress):
1. Monitor development progress
2. When complete, move to: mcp:update_status <task_id> "Testing"
3. Or if blocked: mcp:update_status <task_id> "Blocked" """
        
        elif status == "Testing":
            return """📍 NEXT STEPS (Status: Testing):
🔴 FULL STOP - MANUAL TESTING ONLY
1. Prepare test environment (ensure app is running)
2. Provide URLs/endpoints for user to test manually
3. Document what needs to be tested
4. ⚠️ NO AUTO PROGRESSION - Wait for user
5. ONLY user can update status after manual testing
Note: NEVER automatically move to Code Review"""
        
        elif status == "Code Review":
            return """📍 NEXT STEPS (Status: Code Review):
1. Complete code review with appropriate agent
2. After review complete → Update to Pull Request: mcp:update_status <task_id> "PR"
3. Then create PR ONLY (no merge): mcp:complete_task <task_id> true
⚠️ DO NOT merge to main, DO NOT run tests"""
        
        elif status == "PR":
            return """📍 NEXT STEPS (Status: Pull Request):
🔴 FULL STOP - NO AUTO ACTIONS
1. PR has been created (not merged)
2. Awaiting user to handle merge
3. NO automatic actions allowed
4. User will manually merge and update status
⚠️ DO NOT attempt any automatic actions"""
        
        elif status == "Done":
            return """✅ TASK COMPLETE
This task has been merged to main branch and is complete."""
        
        elif status == "Blocked":
            return """⚠️ TASK BLOCKED
1. Resolve the blocking issue
2. Update status back to previous state when unblocked
3. Document resolution in task comments"""
        
        else:
            return f"""📍 CURRENT STATUS: {status}
Use mcp:update_status to progress the task through the workflow."""

    def _get_agent_for_task(self, task_type: str, status: str, title: str = "", description: str = "") -> Optional[str]:
        """Get the appropriate agent for a task type and status with intelligent context analysis"""
        # Special handling for Testing status - no automation
        if status == "Testing":
            return None  # No agent delegation for manual testing
        
        # First check explicit type mappings
        agent = self.agent_mappings.get(task_type, {}).get(status, None)
        
        # If no explicit mapping, use intelligent context analysis
        if not agent:
            agent = self._analyze_task_context(task_type, title, description, status)
        
        # Validate agent exists
        if agent not in self.available_agents:
            return "backend-architect"  # fallback to available agent
        return agent
    
    def _analyze_task_context(self, task_type: str, title: str, description: str, status: str) -> str:
        """Intelligently analyze task context to select the best agent"""
        text = f"{title} {description}".lower()
        
        # AI/ML patterns
        if any(keyword in text for keyword in ["ai", "ml", "machine learning", "neural", "model", "training", "inference"]):
            return "ai-implementation-expert"
        
        # API patterns
        if any(keyword in text for keyword in ["api", "endpoint", "rest", "graphql", "webhook", "integration"]):
            if "python" in text or "fastapi" in text or "django" in text:
                return "python-api-expert"
            return "api-validator"
        
        # Mobile patterns
        if any(keyword in text for keyword in ["mobile", "react native", "ios", "android", "app"]):
            return "mobile-react-expert"
        
        # E2E and browser testing patterns
        if any(keyword in text for keyword in ["e2e", "end-to-end", "playwright", "cypress", "selenium", "browser test", "visual regression"]):
            return "web-tester"
        
        # UX/UI research patterns
        if any(keyword in text for keyword in ["ux", "ui", "user experience", "user interface", "usability", "design system", "accessibility", "wcag", "user research"]):
            return "ux-ui-researcher"
        
        # Testing patterns  
        if any(keyword in text for keyword in ["test", "testing", "coverage", "unit test", "integration test"]):
            return "background-tester"
        
        # Documentation patterns
        if any(keyword in text for keyword in ["docs", "documentation", "readme", "guide", "manual"]):
            return "docs-generator"
        
        # Code review patterns
        if any(keyword in text for keyword in ["review", "refactor", "optimize", "clean"]):
            return "fullstack-code-reviewer"
        
        # Context/Memory patterns
        if any(keyword in text for keyword in ["context", "memory", "state", "session", "cache"]):
            if "sync" in text or "synchronize" in text:
                return "memory-sync"
            return "context-analyzer"
        
        # Data patterns
        if any(keyword in text for keyword in ["data", "format", "parse", "transform", "csv", "json", "xml"]):
            return "data-formatter"
        
        # DevOps patterns
        if any(keyword in text for keyword in ["deploy", "docker", "kubernetes", "ci/cd", "pipeline", "infrastructure"]):
            return "devops-engineer"
        
        # MCP patterns
        if any(keyword in text for keyword in ["mcp", "protocol", "server", "bridge", "tool"]):
            return "mcp-engineer"
        
        # Frontend patterns
        if any(keyword in text for keyword in ["ui", "frontend", "react", "component", "css", "html"]):
            return "frontend-developer"
        
        # Default to backend for general tasks
        return "backend-architect"
    
    def _validate_agent_exists(self, agent_type: str) -> bool:
        """Validate that the requested agent actually exists locally"""
        return agent_type in self.available_agents
    
    def _get_status_progression_instructions(self, task_type: str, current_status: str) -> str:
        """Get detailed status progression instructions with agent mappings"""
        try:
            current_index = self.status_flow.index(current_status)
        except ValueError:
            current_index = 0
            
        next_status = self.status_flow[current_index + 1] if current_index + 1 < len(self.status_flow) else "Done"
        recommended_agent = self._get_agent_for_task(task_type, next_status)
        
        instructions = f"""📋 STATUS PROGRESSION GUIDE - {task_type.upper()} TASK

Current Status: {current_status}
Next Status: {next_status}
Recommended Agent: {recommended_agent}

🔄 COMPLETE WORKFLOW:
"""
        
        for i, status in enumerate(self.status_flow):
            is_current = status == current_status
            is_next = status == next_status
            agent = self._get_agent_for_task(task_type, status)
            
            if status == "Backlog":
                handler = "YOU (Coordinator)"
                commands = "mcp:get_next_task"
            elif status == "Analysis":
                handler = "YOU (Coordinator)"
                commands = "mcp:analyze_task <task_id>"
            elif status == "PR":
                handler = "USER (Manual)"
                commands = "Manual review and testing, then click 'Done' button (sends /merge command)"
            else:
                handler = f"AGENT: {agent}"
                commands = f"1. mcp:delegate_to_agent <task_id> {agent} '<instructions>' (registers intent)\n     2. /task \"{agent}\" \"<full task details>\" (ACTUAL delegation)"
            
            marker = "🔴 CURRENT" if is_current else "🟡 NEXT" if is_next else "⚪"
            
            instructions += f"""
{marker} {i+1}. {status}:
   Handler: {handler}
   Command: {commands}
   Updates: mcp:update_status <task_id> "{status}"
"""
        
        instructions += f"""

⚡ IMMEDIATE NEXT ACTIONS:
1️⃣ UPDATE STATUS: mcp:update_status <task_id> "{next_status}"
2️⃣ REGISTER DELEGATION: mcp:delegate_to_agent <task_id> {recommended_agent} "<instructions>"
3️⃣ EXECUTE DELEGATION: /task "{recommended_agent}" "<full task details>"
4️⃣ MONITOR: Track progress and advance to next status when complete

🎯 AUTO-PROGRESSION COMMANDS:
- Current → Next: mcp:update_status <task_id> "{next_status}"
- Register Intent: mcp:delegate_to_agent <task_id> {recommended_agent} "<instructions>"
- Actual Delegation: /task "{recommended_agent}" "<task details>"
- Check Queue: mcp:get_task_queue
- Get Next: mcp:get_next_task

⚠️ CRITICAL: mcp:delegate_to_agent only REGISTERS intent. Use /task to ACTUALLY delegate!
"""
        
        return instructions

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
                
                # Get recommended agent for this task type
                recommended_agent = self._get_agent_for_task(
                    task['type'], "Ready", task.get('title', ''), task.get('description', '')
                )
                progression_guide = self._get_status_progression_instructions(task['type'], "Analysis")
                
                return [types.TextContent(
                    type="text",
                    text=f"""🔍 ANALYSIS MODE ACTIVATED - TASK #{task_id}

Task: {task['title']}
Type: {task['type']}  
Priority: {task['priority']}
Recommended Agent: {recommended_agent}

Description:
{task.get('description', 'No description provided')}

⚡ EXECUTE THIS SEQUENCE NOW:

1️⃣ IMMEDIATELY scan the codebase:
   - Use grep/find to locate relevant files
   - Read main implementation files
   - Identify dependencies and impacts

2️⃣ CREATE your analysis (include):
   - Affected files list
   - Implementation approach
   - Risk assessment
   - Estimated complexity
   - Security considerations
   - Performance implications

3️⃣ SAVE your analysis:
   mcp:update_task_analysis {task_id} "<your comprehensive analysis>"

4️⃣ UPDATE status to Ready:
   mcp:update_status {task_id} Ready

5️⃣ UPDATE status to In Progress (creates worktree):
   mcp:update_status {task_id} "In Progress"
   
   ⚠️ This will automatically create:
   - Worktree: ./worktrees/task-{task_id}
   - Branch: feature/task-{task_id}

6️⃣ DELEGATE with worktree instructions:
   mcp:delegate_to_agent {task_id} {recommended_agent} "Work in worktree ./worktrees/task-{task_id}"

7️⃣ EXECUTE actual delegation with CRITICAL worktree instruction:
   /task "{recommended_agent}" "Task #{task_id}: {task['title']}
   
   🌳 CRITICAL: Work in worktree directory!
   FIRST COMMAND: cd ./worktrees/task-{task_id}
   
   ALL changes must be made in the worktree, NOT in main directory!
   
   [Include your implementation instructions here]"

{progression_guide}

🚀 START NOW with step 1 - scan the codebase!"""
                )]
                
            except httpx.HTTPError as e:
                return [types.TextContent(
                    type="text",
                    text=f"Failed to analyze task: {str(e)}"
                )]

    async def _sync_worktree(self, task_id: int) -> Dict[str, Any]:
        """Sync worktree with latest main branch changes"""
        import subprocess
        import os
        
        try:
            # Get task details  
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{self.server_url}/api/tasks/{task_id}")
                response.raise_for_status()
                task = response.json()
            
            if not task.get("worktree_path"):
                return {"success": False, "error": "Task has no worktree"}
                
            worktree_path = task["worktree_path"]
            
            if not os.path.exists(worktree_path):
                return {"success": False, "error": f"Worktree does not exist: {worktree_path}"}
            
            self.logger.info(f"Syncing worktree {worktree_path} with latest main branch")
            
            # First, ensure main branch is up to date
            # Check if we have a remote origin
            remotes_result = subprocess.run(
                ["git", "remote"],
                cwd=self.project_path,
                capture_output=True,
                text=True
            )
            has_origin = "origin" in remotes_result.stdout
            
            if has_origin:
                # Fetch latest changes from origin in main repo
                fetch_result = subprocess.run(
                    ["git", "fetch", "origin"],
                    cwd=self.project_path,
                    capture_output=True,
                    text=True
                )
                
                if fetch_result.returncode != 0:
                    self.logger.warning(f"Failed to fetch from origin: {fetch_result.stderr}")
                else:
                    self.logger.info("Successfully fetched latest changes from origin")
                    
                    # Save current branch in main repo
                    current_branch_result = subprocess.run(
                        ["git", "branch", "--show-current"],
                        cwd=self.project_path,
                        capture_output=True,
                        text=True
                    )
                    current_branch = current_branch_result.stdout.strip()
                    
                    # Switch to main branch in main repo
                    checkout_result = subprocess.run(
                        ["git", "checkout", "main"],
                        cwd=self.project_path,
                        capture_output=True,
                        text=True
                    )
                    
                    if checkout_result.returncode == 0:
                        # Pull latest changes to main
                        pull_result = subprocess.run(
                            ["git", "pull", "origin", "main"],
                            cwd=self.project_path,
                            capture_output=True,
                            text=True
                        )
                        
                        if pull_result.returncode != 0:
                            self.logger.warning(f"Failed to pull latest main: {pull_result.stderr}")
                        else:
                            self.logger.info("Successfully updated main branch with latest changes")
                        
                        # Switch back to original branch if it wasn't main
                        if current_branch and current_branch != "main":
                            subprocess.run(
                                ["git", "checkout", current_branch],
                                cwd=self.project_path,
                                capture_output=True,
                                text=True
                            )
                
                # Now merge main into the worktree branch
                merge_result = subprocess.run(
                    ["git", "merge", "origin/main", "--no-edit", "-m", "Sync with latest main branch"],
                    cwd=worktree_path,
                    capture_output=True,
                    text=True
                )
                
                if merge_result.returncode == 0:
                    self.logger.info(f"Successfully synced worktree with main branch")
                    return {"success": True, "message": "Worktree synced with latest main branch"}
                else:
                    # Check if there are merge conflicts
                    if "CONFLICT" in merge_result.stdout or "CONFLICT" in merge_result.stderr:
                        self.logger.warning(f"Merge conflicts detected in worktree: {merge_result.stderr}")
                        return {
                            "success": False, 
                            "error": "Merge conflicts detected. Manual resolution required.",
                            "conflicts": True
                        }
                    else:
                        self.logger.error(f"Failed to merge main into worktree: {merge_result.stderr}")
                        return {"success": False, "error": f"Failed to merge: {merge_result.stderr}"}
            else:
                self.logger.info("No remote origin found - skipping sync")
                return {"success": True, "message": "No remote origin - using local main branch"}
                
        except Exception as e:
            self.logger.error(f"Error syncing worktree: {e}")
            return {"success": False, "error": str(e)}
    
    async def _update_status(self, task_id: int, status: str, comment: Optional[str] = None) -> list[types.TextContent]:
        """Update task status"""
        async with httpx.AsyncClient() as client:
            try:
                # Sync worktree with main before transitioning to new work phases
                sync_message = ""
                sync_statuses = ["In Progress", "Testing", "Code Review"]
                if status in sync_statuses:
                    # Get current task status before update
                    task_response = await client.get(f"{self.server_url}/api/tasks/{task_id}")
                    task_response.raise_for_status()
                    current_task = task_response.json()
                    
                    # Only sync if transitioning to a new phase (not staying in same status)
                    if current_task.get("status") != status and current_task.get("worktree_path"):
                        sync_result = await self._sync_worktree(task_id)
                        if sync_result["success"]:
                            sync_message = "\n🔄 Worktree synced with latest main branch changes"
                            if comment:
                                comment += " (Worktree synced with main)"
                            else:
                                comment = "Worktree synced with main"
                        elif sync_result.get("conflicts"):
                            sync_message = "\n⚠️ WARNING: Merge conflicts detected - manual resolution required"
                            if comment:
                                comment += " (MERGE CONFLICTS - manual resolution required)"
                            else:
                                comment = "MERGE CONFLICTS - manual resolution required"
                
                data = {"status": status}
                if comment:
                    data["comment"] = comment
                
                response = await client.patch(
                    f"{self.server_url}/api/tasks/{task_id}/status",
                    json=data
                )
                response.raise_for_status()
                result = response.json()
                
                # Get task details to provide progression guidance
                task_response = await client.get(f"{self.server_url}/api/tasks/{task_id}")
                task_response.raise_for_status()
                task = task_response.json()

                # If status changed to Done, index the task in RAG
                rag_index_status = ""
                if status == "Done" and self.rag_initialized:
                    try:
                        self.logger.info(f"Task #{task_id} marked as Done. Indexing in RAG task history...")
                        await self.rag_service.index_task(task)
                        rag_index_status = "\n- RAG Task Indexed: ✅ Yes (available for future similarity search)"
                        self.logger.info(f"Task #{task_id} indexed successfully in RAG task history")
                    except Exception as e:
                        rag_index_status = f"\n- RAG Task Indexed: ⚠️ Failed ({str(e)})"
                        self.logger.error(f"Failed to index task #{task_id} in RAG: {e}")

                # Get next steps guidance
                progression_guide = self._get_status_progression_instructions(task['type'], status)
                
                # Check if worktree was created (happens automatically when changing to In Progress)
                worktree_info = ""
                if status == "In Progress" and result.get("worktree"):
                    worktree = result["worktree"]
                    if worktree.get("created"):
                        worktree_info = f"""
🌳 WORKTREE AUTOMATICALLY CREATED:
- Branch: {worktree.get('branch')}
- Path: {worktree.get('path')}
- Ready for development!
"""
                    elif worktree.get("exists"):
                        worktree_info = f"""
🌳 WORKTREE ALREADY EXISTS:
- Branch: {worktree.get('branch')}
- Path: {worktree.get('path')}
"""
                
                # Special instructions for Code Review status
                pr_instructions = ""
                if status == "Code Review":
                    pr_instructions = f"""

📝 CODE REVIEW COMPLETED - CREATE PR NOW:

After code review is complete, create a Pull Request:
1. Use mcp:complete_task {task_id} true (creates PR)
2. Then update status: mcp:update_status {task_id} PR
3. Task will enter PR status for manual review
4. User will test and review PR manually
5. User will click 'Done' button which sends /merge command
"""
                
                # Special instructions for PR status
                if status == "PR":
                    pr_instructions = f"""

🔍 PULL REQUEST CREATED - AWAITING MANUAL REVIEW:

Task is now in PR status. Required actions:
1. USER: Manually review the Pull Request
2. USER: Test the implementation 
3. USER: Approve/request changes on GitHub
4. USER: Click 'Done' button in UI (will send /merge command)
5. SYSTEM: /merge command will:
   - Merge PR to main branch
   - Clean up worktree
   - Update status to Done
   - Stop Claude session
"""
                
                return [types.TextContent(
                    type="text",
                    text=f"""✅ STATUS UPDATED SUCCESSFULLY

Task #{task_id}: {task['title']}
Type: {task['type']}
New Status: {status}
{f"Comment: {comment}" if comment else ""}
{sync_message}{rag_index_status}
{worktree_info}
{pr_instructions}
{progression_guide}

🚀 CONTINUE AUTONOMOUS WORKFLOW - Execute the next actions above!"""
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
            
            # First, sync main branch with latest updates
            self.logger.info(f"Syncing main branch with latest updates for task {task_id}")
            
            # Check if we have a remote origin
            remotes_result = subprocess.run(
                ["git", "remote"],
                cwd=self.project_path,
                capture_output=True,
                text=True
            )
            has_origin = "origin" in remotes_result.stdout
            
            if has_origin:
                # Fetch latest changes from origin
                fetch_result = subprocess.run(
                    ["git", "fetch", "origin"],
                    cwd=self.project_path,
                    capture_output=True,
                    text=True
                )
                
                if fetch_result.returncode != 0:
                    self.logger.warning(f"Failed to fetch from origin: {fetch_result.stderr}")
                else:
                    self.logger.info("Successfully fetched latest changes from origin")
                    
                    # Update main branch with latest changes
                    # Save current branch to restore later
                    current_branch_result = subprocess.run(
                        ["git", "branch", "--show-current"],
                        cwd=self.project_path,
                        capture_output=True,
                        text=True
                    )
                    current_branch = current_branch_result.stdout.strip()
                    
                    # Switch to main branch
                    checkout_result = subprocess.run(
                        ["git", "checkout", "main"],
                        cwd=self.project_path,
                        capture_output=True,
                        text=True
                    )
                    
                    if checkout_result.returncode == 0:
                        # Pull latest changes
                        pull_result = subprocess.run(
                            ["git", "pull", "origin", "main"],
                            cwd=self.project_path,
                            capture_output=True,
                            text=True
                        )
                        
                        if pull_result.returncode != 0:
                            self.logger.warning(f"Failed to pull latest main: {pull_result.stderr}")
                        else:
                            self.logger.info("Successfully updated main branch with latest changes")
                        
                        # Switch back to original branch if it wasn't main
                        if current_branch and current_branch != "main":
                            subprocess.run(
                                ["git", "checkout", current_branch],
                                cwd=self.project_path,
                                capture_output=True,
                                text=True
                            )
                    else:
                        self.logger.warning(f"Failed to checkout main branch: {checkout_result.stderr}")
            else:
                self.logger.info("No remote origin found - using local main branch")
            
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
                # Get task details first
                response = await client.get(f"{self.server_url}/api/tasks/{task_id}")
                response.raise_for_status()
                task = response.json()
                
                # Validate agent exists locally
                if not self._validate_agent_exists(agent_type):
                    return [types.TextContent(
                        type="text",
                        text=f"❌ AGENT NOT AVAILABLE: {agent_type}\n\nAvailable agents: {', '.join(self.available_agents)}\n\nPlease use delegate_to_agent with one of the available agents."
                    )]
                
                # Get recommended agent for comparison
                recommended_agent = self._get_agent_for_task(
                    task['type'], task['status'], task.get('title', ''), task.get('description', '')
                )
                
                validation_note = ""
                if agent_type != recommended_agent:
                    validation_note = f"\n⚠️  NOTE: {agent_type} selected for {task['type']} task. Recommended: {recommended_agent}\n"
                
                # Update task with assigned agent
                await client.patch(
                    f"{self.server_url}/api/tasks/{task_id}",
                    json={"assigned_agent": agent_type}
                )
                
                # Get status progression guidance
                progression_guide = self._get_status_progression_instructions(task['type'], task['status'])
                
                # Get worktree path if it exists
                worktree_path = task.get('worktree_path', '')
                if not worktree_path and task['status'] == 'In Progress':
                    # Worktree should exist for In Progress tasks
                    worktree_path = f"./worktrees/task-{task_id}"
                
                worktree_instruction = ""
                if worktree_path:
                    worktree_instruction = f"""

🌳 WORKTREE WORKSPACE:
Path: {worktree_path}

⚠️ CRITICAL INSTRUCTION FOR AGENT:
ALL WORK MUST BE DONE IN THE WORKTREE DIRECTORY!
cd {worktree_path}

The agent MUST:
1. Change to worktree directory: cd {worktree_path}
2. Perform ALL file operations in this isolated workspace
3. Commit changes in the feature branch
4. NEVER modify files in the main project directory"""
                
                return [types.TextContent(
                    type="text",
                    text=f"""⚠️ DELEGATION REGISTERED BUT NOT EXECUTED!

Task #{task_id}: {task['title']}
Type: {task['type']} | Status: {task['status']}
Agent Selected: {agent_type}
{validation_note}
📋 Instructions Recorded:
{instructions}
{worktree_instruction}

🚨 CRITICAL: DELEGATION IS NOT COMPLETE YET!

You must now USE the Task tool to actually delegate:

🔥 EXECUTE THIS COMMAND NOW:
/task "{agent_type}" "Task #{task_id}: {task['title']}\n\nType: {task['type']}\nInstructions: {instructions}\n\n🌳 WORKSPACE: {worktree_path if worktree_path else 'Will be created'}\n\n⚠️ CRITICAL: You MUST work in the worktree directory!\nFirst command: cd {worktree_path if worktree_path else f'./worktrees/task-{task_id}'}\n\nALL file changes must be made in this worktree, NOT in the main project directory!\n\nPlease implement this task following the provided instructions."

IMPORTANT: Delegation is NOT complete until you run the Task tool above!

📋 After Task tool execution, continue with:
1️⃣ UPDATE status: mcp:update_status {task_id} "In Progress" (if not already)
2️⃣ MONITOR agent progress
3️⃣ ENSURE agent is working in worktree: {worktree_path if worktree_path else f'./worktrees/task-{task_id}'}

{progression_guide}"""
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

    async def _recommend_agent(self, task_type: str, status: str, title: str, description: str) -> list[types.TextContent]:
        """Get intelligent agent recommendation based on task context"""
        try:
            # Special handling for Testing status
            if status == "Testing":
                response_text = """⚠️ TESTING STATUS - MANUAL TESTING ONLY

Status: Testing
Action: NO AGENT DELEGATION

📋 MANUAL TESTING REQUIREMENTS:
1. Prepare test environment (ensure app is running)
2. Provide URLs/endpoints for user testing
3. Document test scenarios
4. Wait for user to complete manual testing

❌ DO NOT:
- Delegate to testing agents
- Run automated tests
- Use background-tester or web-tester

✅ DO:
- Ensure environment is ready
- Provide access information
- Wait for manual testing completion

🚀 NEXT STEPS:
1. Prepare testing environment
2. Notify user that environment is ready
3. Wait for user to test manually
4. After testing: mcp:update_status <task_id> "Code Review"
"""
                return [types.TextContent(type="text", text=response_text)]
            
            # Get agent recommendation using our intelligent analysis
            recommended_agent = self._get_agent_for_task(task_type, status, title, description)
            
            # Also get the basic mapping for comparison
            basic_recommendation = self.agent_mappings.get(task_type, {}).get(status, "backend-architect")
            
            # Analyze why this agent was selected
            context_analysis = self._get_recommendation_reasoning(task_type, title, description, recommended_agent)
            
            response_text = f"""🎯 INTELLIGENT AGENT RECOMMENDATION

Task Type: {task_type}
Status: {status}
Title: {title}

🤖 RECOMMENDED AGENT: {recommended_agent}

📊 ANALYSIS:
{context_analysis}

📋 COMPARISON:
- Context-based recommendation: {recommended_agent}
- Basic type mapping: {basic_recommendation}
- Match: {'✅ Yes' if recommended_agent == basic_recommendation else '⚠️ No - Context override applied'}

🚀 NEXT STEPS:
1. Use delegate_to_agent with: {recommended_agent}
2. Or explore other agents with: mcp:list_agents
3. Register delegation: mcp:delegate_to_agent <task_id> {recommended_agent} "<instructions>"
4. Execute: /task "{recommended_agent}" "<task details>"
"""
            
            return [types.TextContent(type="text", text=response_text)]
            
        except Exception as e:
            return [types.TextContent(
                type="text",
                text=f"Failed to recommend agent: {str(e)}"
            )]
    
    def _get_recommendation_reasoning(self, task_type: str, title: str, description: str, recommended_agent: str) -> str:
        """Get reasoning for why a specific agent was recommended"""
        text = f"{title} {description}".lower()
        
        # Create reasoning based on detected patterns
        reasoning = []
        
        if "ai" in text or "ml" in text:
            reasoning.append("🧠 AI/ML keywords detected - requires specialized ML expertise")
        if "api" in text:
            reasoning.append("🔌 API keywords detected - needs API design and validation skills")
        if "test" in text:
            reasoning.append("🧪 Testing keywords detected - requires testing expertise")
        if "mobile" in text:
            reasoning.append("📱 Mobile keywords detected - needs mobile development skills")
        if "docs" in text or "documentation" in text:
            reasoning.append("📚 Documentation keywords detected - requires technical writing skills")
        if "review" in text or "refactor" in text:
            reasoning.append("🔍 Code review keywords detected - needs comprehensive review skills")
        if "context" in text or "memory" in text:
            reasoning.append("🧩 Context/Memory keywords detected - requires state management expertise")
        if "data" in text and ("format" in text or "parse" in text):
            reasoning.append("📊 Data formatting keywords detected - needs data processing skills")
        if "deploy" in text or "docker" in text:
            reasoning.append("🚀 DevOps keywords detected - requires infrastructure expertise")
        if "mcp" in text:
            reasoning.append("🔗 MCP keywords detected - needs protocol integration expertise")
        if "frontend" in text or "ui" in text:
            reasoning.append("🎨 Frontend keywords detected - requires UI/UX development skills")
        
        if not reasoning:
            reasoning.append(f"📝 Task type '{task_type}' matched to standard agent mapping")
        
        return "\n".join(f"  • {r}" for r in reasoning)

    async def _list_agents(self) -> list[types.TextContent]:
        """Get information about all available specialized agents"""
        try:
            agent_descriptions = {
                "ai-implementation-expert": "🧠 AI/ML specialist - machine learning, neural networks, model training/inference",
                "api-validator": "🔌 API specialist - REST/GraphQL endpoints, validation, testing",
                "backend-architect": "🏗️ Backend specialist - server architecture, databases, core logic",
                "background-tester": "🧪 Testing specialist - unit/integration tests, coverage, automation",
                "context-analyzer": "🧩 Context specialist - state analysis, context management, session handling",
                "data-formatter": "📊 Data specialist - parsing, transformation, CSV/JSON/XML processing",
                "devops-engineer": "🚀 DevOps specialist - deployment, Docker, CI/CD, infrastructure",
                "docs-generator": "📚 Documentation specialist - technical writing, guides, API docs",
                "frontend-developer": "🎨 Frontend specialist - React, UI/UX, components, styling",
                "fullstack-code-reviewer": "🔍 Code review specialist - comprehensive review, refactoring, optimization",
                "mcp-engineer": "🔗 MCP specialist - protocol integration, server bridges, tools",
                "memory-sync": "💾 Memory specialist - synchronization, caching, state persistence",
                "mobile-react-expert": "📱 Mobile specialist - React Native, iOS/Android development",
                "python-api-expert": "🐍 Python API specialist - FastAPI, Django, Python web services"
            }
            
            response_text = """🤖 AVAILABLE SPECIALIZED AGENTS

Here are all the agents available for task delegation:

"""
            
            for agent in self.available_agents:
                description = agent_descriptions.get(agent, "📝 Specialized agent")
                response_text += f"""
**{agent}**
{description}

"""
            
            response_text += """
💡 INTELLIGENT SELECTION:
- Use 'recommend_agent' tool for context-based recommendations
- Agents are automatically selected based on task keywords and type
- Override recommendations when you have specific expertise needs

🎯 DELEGATION WORKFLOW:
1. Get recommendation: mcp:recommend_agent <type> <status> "<title>" "<description>"
2. Register intent: mcp:delegate_to_agent <task_id> <agent> "<instructions>"
3. Execute delegation: /task "<agent>" "<full task details>"

📋 TASK TYPE MAPPINGS:
- Feature/Bug → frontend-developer, backend-architect
- API → api-validator, python-api-expert  
- Mobile → mobile-react-expert
- Testing → background-tester
- E2E Testing → web-tester
- UX/UI Research → ux-ui-researcher
- Documentation → docs-generator
- Code Review → fullstack-code-reviewer
- AI/ML → ai-implementation-expert
- DevOps → devops-engineer
- Context/Memory → context-analyzer, memory-sync
- Data → data-formatter
- MCP → mcp-engineer
"""
            
            return [types.TextContent(type="text", text=response_text)]
            
        except Exception as e:
            return [types.TextContent(
                type="text",
                text=f"Failed to list agents: {str(e)}"
            )]
    
    async def _complete_task(self, task_id: int, create_pr: bool = False) -> list[types.TextContent]:
        """Complete a task by merging to main and cleaning up worktree"""
        async with httpx.AsyncClient() as client:
            try:
                # Get task details first
                response = await client.get(f"{self.server_url}/api/tasks/{task_id}")
                response.raise_for_status()
                task = response.json()
                
                if not task:
                    return [types.TextContent(
                        type="text",
                        text=f"Task {task_id} not found"
                    )]
                
                # Check if task has a git branch
                if not task.get('git_branch'):
                    return [types.TextContent(
                        type="text",
                        text=f"Task {task_id} has no associated git branch"
                    )]
                
                # Call the completion endpoint
                completion_response = await client.post(
                    f"{self.server_url}/api/tasks/{task_id}/complete",
                    json={"create_pr": create_pr}
                )
                completion_response.raise_for_status()
                result = completion_response.json()
                
                if result.get("success"):
                    status_emoji = "✅" if result.get("merged") else "📝"

                    # If merged to main, trigger RAG reindexing of changed files only
                    reindex_status = ""
                    if result.get("merged") and self.rag_initialized:
                        try:
                            self.logger.info(f"Task #{task_id} merged to main. Triggering RAG reindexing of changed files...")
                            # Reindex only files changed in the merge commit (HEAD is the merge commit)
                            await self.rag_service.reindex_merge_commit(self.project_path)
                            reindex_status = "- RAG Index Updated: ✅ Yes (changed files only)\n"
                            self.logger.info("RAG reindexing completed successfully")
                        except Exception as e:
                            reindex_status = f"- RAG Index Updated: ⚠️  Failed ({str(e)})\n"
                            self.logger.error(f"RAG reindexing failed: {e}")

                    response_text = f"""{status_emoji} TASK COMPLETION - Task #{task_id}

📋 Task: {task['title']}
🌳 Branch: {task['git_branch']}

🎯 RESULTS:
- Merged to main: {'✅ Yes' if result.get('merged') else '❌ No'}
- Worktree removed: {'✅ Yes' if result.get('worktree_removed') else '❌ No'}
- Branch deleted: {'✅ Yes' if result.get('branch_deleted') else '❌ No'}
{reindex_status}"""
                    
                    if result.get('pr_url'):
                        response_text += f"- Pull Request: {result['pr_url']}\n"
                    
                    if result.get('errors'):
                        response_text += f"\n⚠️ WARNINGS:\n"
                        for error in result['errors']:
                            response_text += f"- {error}\n"
                    
                    response_text += f"""
📊 SUMMARY:
Task has been {'merged to main branch' if result.get('merged') else 'prepared for review via PR'}.
{'The worktree and feature branch have been cleaned up.' if result.get('worktree_removed') else 'Manual cleanup may be required.'}

✨ Task #{task_id} is now complete!"""
                    
                else:
                    response_text = f"""❌ TASK COMPLETION FAILED - Task #{task_id}

📋 Task: {task['title']}
🌳 Branch: {task['git_branch']}

🔴 ERRORS:
"""
                    for error in result.get('errors', ['Unknown error']):
                        response_text += f"- {error}\n"
                    
                    response_text += """
💡 TROUBLESHOOTING:
1. Check for merge conflicts: git status
2. Ensure branch is up to date: git pull origin main
3. Verify worktree status: git worktree list
4. Try manual merge if needed"""
                
                return [types.TextContent(type="text", text=response_text)]
                
            except httpx.HTTPStatusError as e:
                error_detail = ""
                if e.response.text:
                    try:
                        error_json = e.response.json()
                        error_detail = error_json.get("detail", str(e))
                    except:
                        error_detail = e.response.text
                else:
                    error_detail = str(e)
                    
                return [types.TextContent(
                    type="text",
                    text=f"Failed to complete task {task_id}: {error_detail}"
                )]
            except Exception as e:
                return [types.TextContent(
                    type="text",
                    text=f"Error completing task {task_id}: {str(e)}"
                )]
    
    async def _start_claude_session(self, task_id: int, context: str = "") -> list[types.TextContent]:
        """Start a Claude session for a task"""
        async with httpx.AsyncClient() as client:
            try:
                # Start session via API
                response = await client.post(
                    f"{self.server_url}/api/tasks/{task_id}/session/start",
                    json={"context": context}
                )
                response.raise_for_status()
                result = response.json()
                
                if result.get("success"):
                    response_text = f"""🚀 CLAUDE SESSION STARTED - Task #{task_id}

📁 Working Directory: {result.get('session', {}).get('working_dir')}
🆔 Session ID: {result.get('session', {}).get('id')}
📊 Status: {result.get('session', {}).get('status')}

💡 SESSION FEATURES:
- Isolated workspace for this task
- Full access to project codebase
- MCP tools available for task management
- Session persists across reconnections

🛠️ AVAILABLE COMMANDS:
- Update status: mcp:update_status {task_id} <status>
- Complete task: mcp:complete_task {task_id}
- Delegate work: mcp:delegate_to_agent {task_id} <agent> "<instructions>"
- Check session: mcp:get_session_status {task_id}

✨ Session is now active and ready for development!"""
                else:
                    response_text = f"""❌ FAILED TO START SESSION - Task #{task_id}

Error: {result.get('error', 'Unknown error')}

💡 Troubleshooting:
1. Check if task exists and is in valid state
2. Ensure project path is accessible
3. Verify Claude integration is configured"""
                
                return [types.TextContent(type="text", text=response_text)]
                
            except httpx.HTTPStatusError as e:
                return [types.TextContent(
                    type="text",
                    text=f"Failed to start session: HTTP {e.response.status_code}"
                )]
            except Exception as e:
                return [types.TextContent(
                    type="text",
                    text=f"Error starting session: {str(e)}"
                )]
    
    async def _get_session_status(self, task_id: int) -> list[types.TextContent]:
        """Get Claude session status for a task"""
        async with httpx.AsyncClient() as client:
            try:
                # Get session status
                response = await client.get(
                    f"{self.server_url}/api/tasks/{task_id}/session"
                )
                
                if response.status_code == 404:
                    return [types.TextContent(
                        type="text",
                        text=f"No Claude session found for task {task_id}"
                    )]
                
                response.raise_for_status()
                session = response.json()
                
                # Format session status
                response_text = f"""📊 CLAUDE SESSION STATUS - Task #{task_id}

🆔 Session ID: {session.get('id', 'N/A')}
📍 Status: {session.get('status', 'unknown').upper()}
📁 Working Directory: {session.get('working_dir', 'N/A')}

📈 STATISTICS:
- Total Messages: {len(session.get('messages', []))}
- Session Started: {session.get('created_at', 'N/A')}
- Last Updated: {session.get('updated_at', 'N/A')}
"""
                
                # Add metadata if available
                metadata = session.get('metadata', {})
                if metadata:
                    tools_used = metadata.get('tools_used_count', {})
                    if tools_used:
                        response_text += "\n🔧 TOOLS USED:\n"
                        for tool, count in tools_used.items():
                            response_text += f"- {tool}: {count} times\n"
                
                # Add recent messages
                messages = session.get('messages', [])
                if messages:
                    response_text += f"\n💬 RECENT MESSAGES ({min(3, len(messages))} of {len(messages)}):\n"
                    for msg in messages[-3:]:
                        role = msg.get('role', 'unknown')
                        content = msg.get('content', '')[:100]
                        if len(msg.get('content', '')) > 100:
                            content += "..."
                        response_text += f"- [{role}]: {content}\n"
                
                response_text += f"""
🎯 SESSION CONTROLS:
- Pause: mcp:pause_session {task_id}
- Resume: mcp:resume_session {task_id}
- Send message: POST /api/tasks/{task_id}/session/message"""
                
                return [types.TextContent(type="text", text=response_text)]
                
            except httpx.HTTPError as e:
                return [types.TextContent(
                    type="text",
                    text=f"Failed to get session status: {str(e)}"
                )]

    async def _append_stage_result(self, task_id: int, status: str, summary: str, details: Optional[str] = None) -> list[types.TextContent]:
        """Append a new stage result to task's cumulative results"""
        async with httpx.AsyncClient() as client:
            try:
                # Prepare the stage result data
                stage_result_data = {
                    "status": status,
                    "summary": summary
                }
                if details:
                    stage_result_data["details"] = details
                
                # Send to backend API
                response = await client.post(
                    f"{self.server_url}/api/tasks/{task_id}/stage-result",
                    json=stage_result_data
                )
                response.raise_for_status()
                result = response.json()
                
                # Get updated task details
                task_response = await client.get(f"{self.server_url}/api/tasks/{task_id}")
                task_response.raise_for_status()
                task = task_response.json()
                
                # Count total stage results
                stage_results_count = len(task.get('stage_results', []))
                
                return [types.TextContent(
                    type="text",
                    text=f"""✅ STAGE RESULT APPENDED SUCCESSFULLY

Task #{task_id}: {task['title']}
Status: {status}
Summary: {summary}
{f'Details: {details}' if details else ''}

📊 CUMULATIVE RESULTS:
Total stage results recorded: {stage_results_count}

💡 STAGE RESULTS HISTORY:
{self._format_stage_results(task.get('stage_results', []))}

🎯 NEXT STEPS:
- Stage result has been permanently saved
- Continue with task workflow
- Use mcp:get_task {task_id} to see all cumulative results
- Results are preserved across status changes"""
                )]
                
            except httpx.HTTPError as e:
                return [types.TextContent(
                    type="text",
                    text=f"Failed to append stage result: {str(e)}"
                )]
            except Exception as e:
                return [types.TextContent(
                    type="text",
                    text=f"Error appending stage result: {str(e)}"
                )]
    
    def _format_stage_results(self, stage_results: list) -> str:
        """Format stage results for display"""
        if not stage_results:
            return "No stage results recorded yet"
        
        formatted = []
        for i, result in enumerate(stage_results[-5:], 1):  # Show last 5 results
            timestamp = result.get('timestamp', 'Unknown time')
            status = result.get('status', 'Unknown status')
            summary = result.get('summary', 'No summary')
            formatted.append(f"{i}. [{timestamp}] {status}: {summary}")
        
        if len(stage_results) > 5:
            formatted.insert(0, f"... (showing last 5 of {len(stage_results)} results)")
        
        return "\n".join(formatted)

    async def _set_testing_urls(self, task_id: int, urls: Dict[str, str]) -> list[types.TextContent]:
        """Set testing environment URLs for a task"""
        async with httpx.AsyncClient() as client:
            try:
                # Send to backend API
                response = await client.patch(
                    f"{self.server_url}/api/tasks/{task_id}/testing-urls",
                    json={"testing_urls": urls}
                )
                response.raise_for_status()
                task = response.json()
                
                # Format URLs for display
                urls_display = "\n".join([f"- {env}: {url}" for env, url in urls.items()])
                
                return [types.TextContent(
                    type="text",
                    text=f"""✅ TESTING URLS UPDATED SUCCESSFULLY

Task #{task_id}: {task['title']}
Status: {task['status']}

🔗 TESTING ENVIRONMENT URLS:
{urls_display}

🎯 NEXT STEPS:
- Testing URLs have been saved to the task
- URLs will be displayed in the task details dialog
- Share these URLs with testers when task reaches Testing status
- URLs are preserved and accessible via task details"""
                )]
                
            except httpx.HTTPError as e:
                return [types.TextContent(
                    type="text",
                    text=f"Failed to update testing URLs: {str(e)}"
                )]
            except Exception as e:
                return [types.TextContent(
                    type="text",
                    text=f"Error updating testing URLs: {str(e)}"
                )]

    async def _stop_session(self, task_id: int) -> list[types.TextContent]:
        """Stop/complete the Claude session for a task and kill any test server processes"""
        import subprocess
        import signal
        import re
        from urllib.parse import urlparse
        
        async with httpx.AsyncClient() as client:
            try:
                # Get task details first to check for testing URLs
                task_response = await client.get(f"{self.server_url}/api/tasks/{task_id}")
                task_response.raise_for_status()
                task = task_response.json()
                
                results = []
                errors = []
                
                # 1. Stop the Claude session
                try:
                    response = await client.post(
                        f"{self.server_url}/api/sessions/{task_id}/complete"
                    )
                    if response.status_code == 200:
                        results.append("✅ Claude session completed successfully")
                    elif response.status_code == 404:
                        results.append("ℹ️ No active Claude session found to complete")
                    else:
                        errors.append(f"Failed to complete Claude session: HTTP {response.status_code}")
                except httpx.HTTPError as e:
                    errors.append(f"Error completing Claude session: {str(e)}")
                
                # 2. Try to stop embedded session if it exists
                try:
                    # Check if there's an embedded session
                    session_response = await client.get(f"{self.server_url}/api/tasks/{task_id}/session")
                    if session_response.status_code == 200:
                        session = session_response.json()
                        session_id = session.get('id')
                        if session_id:
                            stop_response = await client.post(
                                f"{self.server_url}/api/sessions/embedded/{session_id}/stop"
                            )
                            if stop_response.status_code == 200:
                                results.append("✅ Embedded Claude session stopped successfully")
                            else:
                                errors.append(f"Failed to stop embedded session: HTTP {stop_response.status_code}")
                except httpx.HTTPError as e:
                    # Embedded session endpoints might not exist, so this is optional
                    self.logger.warning(f"Could not stop embedded session: {str(e)}")
                
                # 3. Kill test server processes based on testing_urls
                testing_urls = task.get('testing_urls', {})
                if testing_urls:
                    results.append("🔍 Looking for test server processes to terminate...")
                    
                    ports_to_kill = []
                    for env_name, url in testing_urls.items():
                        try:
                            parsed_url = urlparse(url)
                            if parsed_url.port:
                                ports_to_kill.append((env_name, parsed_url.port))
                        except Exception as e:
                            errors.append(f"Error parsing URL for {env_name}: {str(e)}")
                    
                    if ports_to_kill:
                        killed_processes = []
                        for env_name, port in ports_to_kill:
                            try:
                                # Find processes using the port
                                lsof_result = subprocess.run(
                                    ["lsof", "-ti", f":{port}"],
                                    capture_output=True,
                                    text=True
                                )
                                
                                if lsof_result.returncode == 0 and lsof_result.stdout.strip():
                                    pids = lsof_result.stdout.strip().split('\n')
                                    for pid in pids:
                                        try:
                                            pid = int(pid.strip())
                                            # Kill the process
                                            subprocess.run(["kill", str(pid)], check=True)
                                            killed_processes.append(f"PID {pid} (port {port}, {env_name})")
                                        except (ValueError, subprocess.CalledProcessError) as e:
                                            errors.append(f"Failed to kill PID {pid}: {str(e)}")
                                else:
                                    results.append(f"ℹ️ No processes found on port {port} ({env_name})")
                                    
                            except FileNotFoundError:
                                # lsof not available, try alternative approach
                                try:
                                    # Try using ps and grep to find processes
                                    ps_result = subprocess.run(
                                        ["ps", "aux"],
                                        capture_output=True,
                                        text=True
                                    )
                                    
                                    if ps_result.returncode == 0:
                                        # Look for processes that might be using this port
                                        lines = ps_result.stdout.split('\n')
                                        for line in lines:
                                            if str(port) in line and any(keyword in line.lower() for keyword in ['node', 'npm', 'uvicorn', 'python', 'serve']):
                                                # Extract PID (usually second column)
                                                parts = line.split()
                                                if len(parts) > 1:
                                                    try:
                                                        pid = int(parts[1])
                                                        subprocess.run(["kill", str(pid)], check=True)
                                                        killed_processes.append(f"PID {pid} (port {port}, {env_name})")
                                                    except (ValueError, subprocess.CalledProcessError):
                                                        pass
                                except subprocess.CalledProcessError:
                                    errors.append(f"Could not find processes on port {port} ({env_name})")
                        
                        if killed_processes:
                            results.append(f"✅ Terminated processes: {', '.join(killed_processes)}")
                        else:
                            results.append("ℹ️ No test server processes found to terminate")
                    else:
                        results.append("ℹ️ No valid ports found in testing URLs")
                else:
                    results.append("ℹ️ No testing URLs configured - no test servers to stop")
                
                # 4. Clear testing URLs from task
                if testing_urls:
                    try:
                        await client.patch(
                            f"{self.server_url}/api/tasks/{task_id}/testing-urls",
                            json={"testing_urls": {}}
                        )
                        results.append("✅ Testing URLs cleared from task")
                    except httpx.HTTPError as e:
                        errors.append(f"Failed to clear testing URLs: {str(e)}")
                
                # Prepare response
                response_text = f"""🛑 SESSION STOP COMPLETED - Task #{task_id}
                
📋 Task: {task['title']}
Status: {task['status']}

✅ RESULTS:
{chr(10).join(f"• {result}" for result in results)}"""
                
                if errors:
                    response_text += f"""

⚠️ WARNINGS/ERRORS:
{chr(10).join(f"• {error}" for error in errors)}"""
                
                response_text += f"""

📊 SUMMARY:
Claude session for task #{task_id} has been stopped and test environment cleaned up.
- Session completed and embedded session stopped
- Test server processes terminated
- Testing URLs cleared
- Resources freed for other tasks

Task is now ready for final status updates or closure."""
                
                return [types.TextContent(type="text", text=response_text)]
                
            except httpx.HTTPError as e:
                return [types.TextContent(
                    type="text",
                    text=f"Failed to stop session for task {task_id}: {str(e)}"
                )]
            except Exception as e:
                return [types.TextContent(
                    type="text",
                    text=f"Error stopping session for task {task_id}: {str(e)}"
                )]

    async def _search_codebase(
        self,
        query: str,
        top_k: int = 20,
        language: Optional[str] = None,
        min_similarity: Optional[float] = None
    ) -> list[types.TextContent]:
        """Search codebase using RAG with optional similarity filtering"""
        if not self.rag_initialized:
            return [types.TextContent(
                type="text",
                text="⚠️  RAG service not initialized. Cannot search codebase."
            )]

        try:
            # Build filters
            filters = {}
            if language:
                filters['language'] = language

            # Search with higher limit to allow filtering
            search_limit = min(top_k * 2, 100) if min_similarity else top_k

            results = await self.rag_service.search_codebase(
                query=query,
                top_k=search_limit,
                filters=filters if filters else None
            )

            # Apply similarity threshold if specified
            if min_similarity and results:
                # Note: ChromaDB returns results sorted by similarity (distance)
                # We would need to modify search_codebase to return distances
                # For now, just take top_k results
                results = results[:top_k]

            if not results:
                return [types.TextContent(
                    type="text",
                    text=f"No relevant code found for query: '{query}'"
                )]

            # Format results with statistics
            total_chunks = self.rag_service.codebase_collection.count()
            response = f"🔍 **Code Search Results for: '{query}'**\n\n"
            response += f"Found {len(results)} relevant code chunks (out of {total_chunks} total):\n"

            if min_similarity:
                response += f"Similarity threshold: {min_similarity}\n"

            response += "\n"

            for i, chunk in enumerate(results, 1):
                response += f"**{i}. {chunk.file_path}** (lines {chunk.start_line}-{chunk.end_line})\n"
                response += f"   Type: {chunk.chunk_type} | Language: {chunk.language}\n"
                response += f"   Summary: {chunk.summary}\n"
                response += f"   Code:\n```{chunk.language}\n{chunk.content}\n```\n\n"

            return [types.TextContent(type="text", text=response)]

        except Exception as e:
            return [types.TextContent(
                type="text",
                text=f"Error searching codebase: {str(e)}"
            )]

    async def _find_similar_tasks(
        self,
        task_description: str,
        top_k: int = 5
    ) -> list[types.TextContent]:
        """Find similar historical tasks"""
        if not self.rag_initialized:
            return [types.TextContent(
                type="text",
                text="⚠️  RAG service not initialized. Cannot search tasks."
            )]

        try:
            results = await self.rag_service.find_similar_tasks(
                task_description=task_description,
                top_k=top_k
            )

            if not results:
                return [types.TextContent(
                    type="text",
                    text=f"No similar tasks found for: '{task_description}'"
                )]

            # Format results
            response = f"📋 **Similar Tasks Found**\n\n"
            response += f"Found {len(results)} similar tasks:\n\n"

            for i, task in enumerate(results, 1):
                response += f"**{i}. Task #{task.get('task_id')}**: {task.get('title')}\n"
                response += f"   Type: {task.get('task_type')} | Priority: {task.get('priority')}\n"
                response += f"   Status: {task.get('status')}\n\n"

            return [types.TextContent(type="text", text=response)]

        except Exception as e:
            return [types.TextContent(
                type="text",
                text=f"Error finding similar tasks: {str(e)}"
            )]

    async def _reindex_codebase(
        self,
        full_reindex: bool = False
    ) -> list[types.TextContent]:
        """Reindex codebase (incremental or full)"""
        if not self.rag_initialized:
            return [types.TextContent(
                type="text",
                text="⚠️  RAG service not initialized. Cannot reindex."
            )]

        try:
            if full_reindex:
                self.logger.info("Starting full codebase reindex...")
                await self.rag_service.index_codebase(self.project_path)
                return [types.TextContent(
                    type="text",
                    text="✅ Full codebase reindexing completed successfully"
                )]
            else:
                self.logger.info("Starting incremental codebase reindex...")
                await self.rag_service.update_index_incremental(self.project_path)
                return [types.TextContent(
                    type="text",
                    text="✅ Incremental codebase reindexing completed successfully"
                )]

        except Exception as e:
            return [types.TextContent(
                type="text",
                text=f"Error reindexing codebase: {str(e)}"
            )]

    async def _index_codebase(self) -> list[types.TextContent]:
        """Index entire codebase from scratch"""
        if not self.rag_initialized:
            return [types.TextContent(
                type="text",
                text="⚠️  RAG service not initialized. Cannot index codebase."
            )]

        try:
            self.logger.info("Starting full codebase indexing...")
            await self.rag_service.index_codebase(self.project_path)

            # Get collection stats
            count = self.rag_service.codebase_collection.count()

            return [types.TextContent(
                type="text",
                text=f"✅ Codebase indexing completed successfully\n\nTotal chunks indexed: {count}"
            )]

        except Exception as e:
            self.logger.error(f"Error indexing codebase: {e}")
            return [types.TextContent(
                type="text",
                text=f"❌ Error indexing codebase: {str(e)}"
            )]

    async def _index_files(self, file_paths: list[str]) -> list[types.TextContent]:
        """Index specific files"""
        if not self.rag_initialized:
            return [types.TextContent(
                type="text",
                text="⚠️  RAG service not initialized. Cannot index files."
            )]

        try:
            self.logger.info(f"Starting indexing of {len(file_paths)} files...")
            result = await self.rag_service.index_files(file_paths, self.project_path)

            response_text = f"""✅ File indexing completed successfully

Files indexed: {result['indexed_files']}
Files skipped: {result['skipped_files']}
Total chunks: {result['total_chunks']}"""

            return [types.TextContent(
                type="text",
                text=response_text
            )]

        except Exception as e:
            self.logger.error(f"Error indexing files: {e}")
            return [types.TextContent(
                type="text",
                text=f"❌ Error indexing files: {str(e)}"
            )]

    async def _complete_skill_creation_session(self, session_id: str) -> list[types.TextContent]:
        """Complete skill creation session by sending /exit and stopping Claude process"""
        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                self.logger.info(f"Completing skill creation session: {session_id}")

                # Send /exit command to Claude terminal
                exit_response = await client.post(
                    f"{self.server_url}/api/claude-terminal/sessions/{session_id}/input",
                    json={"input": "/exit"}
                )

                if exit_response.status_code != 200:
                    self.logger.warning(f"Failed to send /exit command: {exit_response.status_code}")

                # Wait a moment for graceful exit
                await asyncio.sleep(1)

                # Stop the session (kills the process)
                stop_response = await client.post(
                    f"{self.server_url}/api/claude-terminal/sessions/{session_id}/stop"
                )

                if stop_response.status_code == 200:
                    return [types.TextContent(
                        type="text",
                        text=f"✅ Skill creation session completed successfully\n\nSession {session_id} stopped and cleaned up."
                    )]
                else:
                    return [types.TextContent(
                        type="text",
                        text=f"⚠️  Session exit sent, but stop failed: {stop_response.status_code}"
                    )]

            except Exception as e:
                self.logger.error(f"Error completing skill creation session: {e}")
                return [types.TextContent(
                    type="text",
                    text=f"❌ Error completing session: {str(e)}"
                )]

    async def run(self):
        """Run the MCP server"""
        from mcp.server.stdio import stdio_server
        from mcp.server.models import ServerCapabilities

        # Initialize RAG service in background
        try:
            self.logger.info("Initializing RAG service...")
            await self.rag_service.initialize()
            self.rag_initialized = True
            self.logger.info("RAG service initialized successfully")

            # Check if index exists, if not - create initial index
            if not await self.rag_service.index_exists():
                self.logger.info("No RAG index found. Creating initial index...")
                await self.rag_service.index_codebase(self.project_path)
            else:
                self.logger.info("RAG index exists. Running incremental update...")
                await self.rag_service.update_index_incremental(self.project_path)

        except Exception as e:
            self.logger.error(f"Failed to initialize RAG service: {e}")
            self.logger.warning("Server will run without RAG features")

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