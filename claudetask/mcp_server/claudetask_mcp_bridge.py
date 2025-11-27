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
            "requirements-analyst",  # Added for UC-01
            "system-architect",      # Added for UC-01
            "systems-analyst",
            "ux-ui-researcher",
            "web-tester"
        ]

        # Agent mapping for task types and statuses with intelligent specialization
        self.agent_mappings = {
            "Feature": {
                "Analysis": "requirements-analyst",  # UC-01: Requirements Writer
                "In Progress": "frontend-developer",
                "Testing": None,  # Manual testing (UC-04 Variant B)
                "Code Review": "fullstack-code-reviewer"  # Code Review + PR creation
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

        # Status progression flow (6 columns - PR merged into Code Review)
        self.status_flow = [
            "Backlog", "Analysis", "In Progress",
            "Testing", "Code Review", "Done"
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

        # MongoDB logging state (will be set after checking project settings)
        self._mongodb_logging_enabled = None  # None = not checked yet

        # Setup tool handlers
        self._setup_tools()

    async def _get_active_project_id(self) -> str:
        """Fetch the current active project ID from backend

        This method is called on every MCP tool invocation to ensure we're always
        using the currently active project, not a cached value.

        Returns:
            str: The active project ID, or the default project_id if fetch fails
        """
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                url = f"{self.server_url}/api/projects/active"
                self.logger.debug(f"Fetching active project from: {url}")
                response = await client.get(url)

                if response.status_code == 200:
                    active_project = response.json()
                    active_id = active_project["id"]
                    active_path = active_project["path"]
                    self.logger.debug(f"Active project: {active_id} ({active_path})")
                    return active_id
                else:
                    self.logger.warning(f"Failed to fetch active project (status {response.status_code}), using fallback: {self.project_id}")
                    return self.project_id
        except Exception as e:
            self.logger.warning(f"Error fetching active project: {e}, using fallback: {self.project_id}")
            return self.project_id

    async def _check_mongodb_logging(self) -> bool:
        """Check if MongoDB logging is enabled for the active project.

        Returns:
            True if storage_mode is 'mongodb', False otherwise
        """
        if self._mongodb_logging_enabled is not None:
            return self._mongodb_logging_enabled

        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(f"{self.server_url}/api/projects/active")
                if response.status_code == 200:
                    project = response.json()
                    storage_mode = project.get("storage_mode", "local")
                    self._mongodb_logging_enabled = (storage_mode == "mongodb")
                    self.logger.info(f"MongoDB logging: {'enabled' if self._mongodb_logging_enabled else 'disabled'} (storage_mode={storage_mode})")
                    return self._mongodb_logging_enabled
        except Exception as e:
            self.logger.debug(f"Could not check storage_mode: {e}")

        self._mongodb_logging_enabled = False
        return False

    async def _log_to_mongodb(
        self,
        tool_name: str,
        status: str,
        arguments: dict = None,
        result: str = None,
        error: str = None
    ):
        """Send MCP log entry to MongoDB via backend API.

        Args:
            tool_name: Name of the MCP tool
            status: Call status (success/error/pending)
            arguments: Tool arguments (optional)
            result: Result preview (optional)
            error: Error message if failed (optional)
        """
        if not await self._check_mongodb_logging():
            return

        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                params = {
                    "tool_name": tool_name,
                    "status": status
                }
                if arguments:
                    params["arguments"] = json.dumps(arguments, ensure_ascii=False)[:2000]
                if result:
                    params["result"] = result[:2000]
                if error:
                    params["error"] = error[:1000]

                await client.post(
                    f"{self.server_url}/api/mcp-logs/ingest/mcp",
                    params=params
                )
        except Exception as e:
            # Don't fail MCP calls if logging fails
            self.logger.debug(f"Failed to log to MongoDB: {e}")

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
                                "enum": [
                                    "ai-implementation-expert", "api-validator", "backend-architect",
                                    "background-tester", "context-analyzer",
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
                                "enum": ["Analysis", "In Progress", "Testing", "Code Review", "Done"],
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
                # Documentation RAG tools
                types.Tool(
                    name="search_documentation",
                    description="Semantic search across project documentation (docs/, README, etc.) using MongoDB Atlas Vector Search. Find relevant documentation sections.",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "Natural language query describing what documentation you're looking for"
                            },
                            "top_k": {
                                "type": "integer",
                                "description": "Number of results to return (default: 20)",
                                "default": 20
                            },
                            "doc_type": {
                                "type": "string",
                                "description": "Optional: filter by doc type (readme, guide, api-doc, markdown, etc.)"
                            },
                            "min_similarity": {
                                "type": "number",
                                "description": "Minimum similarity threshold (0.0-1.0)",
                                "minimum": 0,
                                "maximum": 1
                            }
                        },
                        "required": ["query"]
                    }
                ),
                types.Tool(
                    name="index_documentation",
                    description="Index all documentation files (docs/, README, CONTRIBUTING, etc.) for semantic search. Use for initial indexing.",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "full_reindex": {
                                "type": "boolean",
                                "description": "If true, delete existing index and rebuild (default: false)",
                                "default": False
                            }
                        },
                        "required": []
                    }
                ),
                types.Tool(
                    name="reindex_documentation",
                    description="Incrementally reindex changed documentation files. Faster than full reindex.",
                    inputSchema={
                        "type": "object",
                        "properties": {},
                        "required": []
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
                ),
                types.Tool(
                    name="update_custom_skill_status",
                    description="Update custom skill status and archive it after creation. Call this AFTER skill files are created and BEFORE completing the session. This ensures the skill is properly tracked and can be enabled/disabled.",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "skill_name": {
                                "type": "string",
                                "description": "Name of the skill (e.g., 'ui-designer-hubspot')"
                            },
                            "status": {
                                "type": "string",
                                "enum": ["active", "failed"],
                                "description": "New status for the skill"
                            },
                            "error_message": {
                                "type": "string",
                                "description": "Optional error message if status is 'failed'"
                            }
                        },
                        "required": ["skill_name", "status"]
                    }
                ),
                types.Tool(
                    name="get_project_settings",
                    description="Get current project settings including project_mode and worktree_enabled",
                    inputSchema={
                        "type": "object",
                        "properties": {},
                        "required": []
                    }
                ),
                types.Tool(
                    name="update_custom_subagent_status",
                    description="Update custom subagent status and archive it after creation. Call this AFTER subagent files are created and BEFORE completing the session.",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "subagent_type": {
                                "type": "string",
                                "description": "Type/name of the subagent (e.g., 'my-custom-agent')"
                            },
                            "status": {
                                "type": "string",
                                "enum": ["active", "failed"],
                                "description": "New status for the subagent"
                            },
                            "error_message": {
                                "type": "string",
                                "description": "Optional error message if status is 'failed'"
                            }
                        },
                        "required": ["subagent_type", "status"]
                    }
                ),
                types.Tool(
                    name="save_conversation_message",
                    description="Save a conversation message to project memory",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "message_type": {
                                "type": "string",
                                "enum": ["user", "assistant", "system"],
                                "description": "Type of message"
                            },
                            "content": {
                                "type": "string",
                                "description": "Full message content"
                            },
                            "task_id": {
                                "type": "integer",
                                "description": "Optional task ID"
                            },
                            "metadata": {
                                "type": "object",
                                "description": "Optional metadata"
                            }
                        },
                        "required": ["message_type", "content"]
                    }
                ),
                types.Tool(
                    name="get_project_memory_context",
                    description="Get full memory context for the current project",
                    inputSchema={
                        "type": "object",
                        "properties": {},
                        "required": []
                    }
                ),
                types.Tool(
                    name="update_project_summary",
                    description="Update project summary with new insights",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "trigger": {
                                "type": "string",
                                "enum": ["session_end", "important_decision", "task_complete"],
                                "description": "Event triggering the update"
                            },
                            "new_insights": {
                                "type": "string",
                                "description": "New insights to add to summary"
                            }
                        },
                        "required": ["trigger", "new_insights"]
                    }
                ),
                types.Tool(
                    name="search_project_memories",
                    description="Search project memory using RAG",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "Search query"
                            },
                            "limit": {
                                "type": "integer",
                                "description": "Max results to return",
                                "default": 20
                            },
                            "session_id": {
                                "type": "string",
                                "description": "Filter by session ID. Use 'current' for current session, or provide specific UUID"
                            },
                            "filters": {
                                "type": "object",
                                "description": "Optional filters"
                            }
                        },
                        "required": ["query"]
                    }
                )
            ]

        @self.server.call_tool()
        async def handle_call_tool(name: str, arguments: dict) -> list[types.TextContent]:
            """Handle tool calls with comprehensive logging"""
            # Log incoming MCP call (only for file-based logging, i.e. local mode)
            # For mongodb mode, file handler is not attached so these go to stderr only
            if not await self._check_mongodb_logging():
                self.logger.info(f"{'='*60}")
                self.logger.info(f"🔵 MCP CALL RECEIVED: {name}")
                self.logger.info(f"📥 Arguments: {json.dumps(arguments, indent=2, ensure_ascii=False)}")
                self.logger.info(f"{'='*60}")

            result = None
            try:
                # Execute the appropriate MCP function
                if name == "get_next_task":
                    result = await self._get_next_task()
                elif name == "get_task":
                    result = await self._get_task(arguments["task_id"])
                elif name == "analyze_task":
                    result = await self._analyze_task(arguments["task_id"])
                elif name == "update_status":
                    result = await self._update_status(
                        arguments["task_id"],
                        arguments["status"],
                        arguments.get("comment")
                    )
                elif name == "create_worktree":
                    result = await self._create_worktree(arguments["task_id"])
                elif name == "verify_connection":
                    result = await self._verify_connection()
                elif name == "get_task_queue":
                    result = await self._get_task_queue()
                elif name == "delegate_to_agent":
                    result = await self._delegate_to_agent(
                        arguments["task_id"],
                        arguments["agent_type"],
                        arguments["instructions"]
                    )
                elif name == "get_tasks_needing_analysis":
                    result = await self._get_tasks_needing_analysis()
                elif name == "update_task_analysis":
                    result = await self._update_task_analysis(
                        arguments["task_id"],
                        arguments["analysis"]
                    )
                elif name == "recommend_agent":
                    result = await self._recommend_agent(
                        arguments["task_type"],
                        arguments["status"],
                        arguments["title"],
                        arguments["description"]
                    )
                elif name == "list_agents":
                    result = await self._list_agents()
                elif name == "complete_task":
                    result = await self._complete_task(
                        arguments["task_id"],
                        arguments.get("create_pr", False)
                    )
                elif name == "start_claude_session":
                    result = await self._start_claude_session(
                        arguments["task_id"],
                        arguments.get("context", "")
                    )
                elif name == "get_session_status":
                    result = await self._get_session_status(
                        arguments["task_id"]
                    )
                elif name == "append_stage_result":
                    result = await self._append_stage_result(
                        arguments["task_id"],
                        arguments["status"],
                        arguments["summary"],
                        arguments.get("details")
                    )
                elif name == "set_testing_urls":
                    result = await self._set_testing_urls(
                        arguments["task_id"],
                        arguments["urls"]
                    )
                elif name == "stop_session":
                    result = await self._stop_session(
                        arguments["task_id"]
                    )
                elif name == "search_codebase":
                    result = await self._search_codebase(
                        arguments["query"],
                        arguments.get("top_k", 20),
                        arguments.get("language"),
                        arguments.get("min_similarity")
                    )
                elif name == "find_similar_tasks":
                    result = await self._find_similar_tasks(
                        arguments["task_description"],
                        arguments.get("top_k", 10)
                    )
                elif name == "reindex_codebase":
                    result = await self._reindex_codebase(
                        arguments.get("full_reindex", False)
                    )
                elif name == "index_codebase":
                    result = await self._index_codebase()
                elif name == "index_files":
                    result = await self._index_files(
                        arguments["file_paths"]
                    )
                # Documentation RAG handlers
                elif name == "search_documentation":
                    result = await self._search_documentation(
                        arguments["query"],
                        arguments.get("top_k", 20),
                        arguments.get("doc_type"),
                        arguments.get("min_similarity")
                    )
                elif name == "index_documentation":
                    result = await self._index_documentation(
                        arguments.get("full_reindex", False)
                    )
                elif name == "reindex_documentation":
                    result = await self._reindex_documentation()
                elif name == "complete_skill_creation_session":
                    result = await self._complete_skill_creation_session(
                        arguments["session_id"]
                    )
                elif name == "update_custom_skill_status":
                    result = await self._update_custom_skill_status(
                        arguments["skill_name"],
                        arguments["status"],
                        arguments.get("error_message")
                    )
                elif name == "update_custom_subagent_status":
                    result = await self._update_custom_subagent_status(
                        arguments["subagent_type"],
                        arguments["status"],
                        arguments.get("error_message")
                    )
                elif name == "get_project_settings":
                    result = await self._get_project_settings()
                elif name == "save_conversation_message":
                    result = await self._save_conversation_message(
                        arguments["message_type"],
                        arguments["content"],
                        arguments.get("task_id"),
                        arguments.get("metadata")
                    )
                elif name == "get_project_memory_context":
                    result = await self._get_project_memory_context()
                elif name == "update_project_summary":
                    result = await self._update_project_summary(
                        arguments["trigger"],
                        arguments["new_insights"]
                    )
                elif name == "search_project_memories":
                    result = await self._search_project_memories(
                        arguments["query"],
                        arguments.get("limit", 20),
                        arguments.get("session_id"),
                        arguments.get("filters")
                    )
                else:
                    raise ValueError(f"Unknown tool: {name}")

                # Log successful result
                result_text = ""
                if result:
                    # Convert result for logging (truncate if too long)
                    if isinstance(result, list) and result:
                        if hasattr(result[0], 'text'):
                            result_text = result[0].text[:500]  # First 500 chars
                            if len(result[0].text) > 500:
                                result_text += "...[truncated]"

                # Check storage mode for logging destination
                use_mongodb = await self._check_mongodb_logging()

                if use_mongodb:
                    # Log to MongoDB only
                    await self._log_to_mongodb(
                        tool_name=name,
                        status="success",
                        arguments=arguments,
                        result=result_text
                    )
                else:
                    # Log to file (local mode)
                    if result_text:
                        self.logger.info(f"{'='*60}")
                        self.logger.info(f"✅ MCP CALL SUCCESS: {name}")
                        self.logger.info(f"📤 Result preview: {result_text}")
                        self.logger.info(f"{'='*60}")

                return result

            except Exception as e:
                # Check storage mode for logging destination
                use_mongodb = await self._check_mongodb_logging()

                if use_mongodb:
                    # Log error to MongoDB only
                    await self._log_to_mongodb(
                        tool_name=name,
                        status="error",
                        arguments=arguments,
                        error=str(e)
                    )
                else:
                    # Log error to file (local mode)
                    self.logger.error(f"{'='*60}")
                    self.logger.error(f"❌ MCP CALL ERROR: {name}")
                    self.logger.error(f"🔴 Error: {str(e)}")
                    self.logger.error(f"{'='*60}")

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
        """Return current status only - instructions are in CLAUDE.md"""
        return f"Current Status: {status}"

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
            elif status == "Code Review":
                handler = "USER (Manual) + AGENT"
                commands = "Code review agent + PR creation + Manual review, then click 'Done' button (sends /merge command)"
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
                
                # Special instructions for Code Review status (includes PR creation)
                pr_instructions = ""
                if status == "Code Review":
                    pr_instructions = f"""

📝 CODE REVIEW STATUS - REVIEW + PR CREATION:

This status combines code review and PR management:
1. Run code review agent (fullstack-code-reviewer)
2. Create Pull Request: mcp:complete_task {task_id} true
3. USER: Manually review the Pull Request on GitHub
4. USER: Test the implementation
5. USER: Approve/request changes
6. USER: Click 'Done' button in UI (will send /merge command)
7. SYSTEM: /merge command will:
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
        """Create git worktree for task (ONLY for development mode)"""
        import subprocess
        import os

        try:
            # Get task details
            async with httpx.AsyncClient() as client:
                task_response = await client.get(f"{self.server_url}/api/tasks/{task_id}")
                task_response.raise_for_status()
                task = task_response.json()

                # Get project details to check project_mode
                project_response = await client.get(f"{self.server_url}/api/projects/{task['project_id']}")
                project_response.raise_for_status()
                project = project_response.json()

                # Get project settings to check worktree_enabled
                settings_response = await client.get(f"{self.server_url}/api/projects/{task['project_id']}/settings")
                settings_response.raise_for_status()
                settings = settings_response.json()
                worktree_enabled = settings.get('worktree_enabled', True)

                # Check if project is in development mode
                if project.get('project_mode') != 'development':
                    return [types.TextContent(
                        type="text",
                        text=f"❌ Cannot create worktree: Project is in '{project.get('project_mode', 'simple')}' mode.\n\n"
                             f"Worktrees are only available in 'development' mode.\n"
                             f"In 'simple' mode, work directly in the main branch without worktrees."
                    )]

                # Check if worktrees are enabled
                if not worktree_enabled:
                    return [types.TextContent(
                        type="text",
                        text=f"❌ Cannot create worktree: Worktrees are disabled for this project.\n\n"
                             f"The project is in 'development' mode but worktrees are turned off.\n"
                             f"Enable worktrees in project settings or work directly in the main branch."
                    )]

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

                    # If merged to main, trigger RAG reindexing via MongoDB Atlas API
                    reindex_status = ""
                    if result.get("merged"):
                        try:
                            self.logger.info(f"Task #{task_id} merged to main. Triggering MongoDB Atlas RAG reindexing...")
                            project_id = await self._get_active_project_id()

                            async with httpx.AsyncClient(timeout=300.0) as reindex_client:
                                reindex_response = await reindex_client.post(
                                    f"{self.server_url}/api/codebase-rag/{project_id}/reindex",
                                    json={"repo_path": self.project_path}
                                )

                                if reindex_response.status_code == 200:
                                    reindex_result = reindex_response.json()
                                    chunks = reindex_result.get('total_chunks', 0)
                                    reindex_status = f"- RAG Index Updated: ✅ Yes (MongoDB Atlas, {chunks} chunks)\n"
                                    self.logger.info(f"RAG reindexing completed: {chunks} chunks indexed")
                                else:
                                    reindex_status = f"- RAG Index Updated: ⚠️ Failed ({reindex_response.status_code})\n"
                                    self.logger.warning(f"RAG reindexing returned {reindex_response.status_code}")
                        except Exception as e:
                            reindex_status = f"- RAG Index Updated: ⚠️ Failed ({str(e)})\n"
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
        """Start a Claude session for a task with automatic context from analysis documents"""
        async with httpx.AsyncClient() as client:
            try:
                # Get task details to access worktree path
                task_response = await client.get(f"{self.server_url}/api/tasks/{task_id}")
                task_response.raise_for_status()
                task = task_response.json()

                # Build enhanced context from analysis documents
                enhanced_context = context
                worktree_path = task.get('worktree_path')

                if worktree_path and os.path.exists(worktree_path):
                    # Check for requirements.md
                    requirements_path = os.path.join(worktree_path, "Analyse", "requirements.md")
                    architecture_path = os.path.join(worktree_path, "Analyse", "architecture.md")
                    test_plan_path = os.path.join(worktree_path, "Tests", "test-plan.md")

                    analysis_docs = []

                    if os.path.exists(requirements_path):
                        try:
                            with open(requirements_path, 'r', encoding='utf-8') as f:
                                requirements_content = f.read()
                                analysis_docs.append(f"## 📋 REQUIREMENTS\n\n{requirements_content}")
                        except Exception as e:
                            logger.warning(f"Failed to read requirements.md: {e}")

                    if os.path.exists(architecture_path):
                        try:
                            with open(architecture_path, 'r', encoding='utf-8') as f:
                                architecture_content = f.read()
                                analysis_docs.append(f"## 🏗️ ARCHITECTURE\n\n{architecture_content}")
                        except Exception as e:
                            logger.warning(f"Failed to read architecture.md: {e}")

                    if os.path.exists(test_plan_path):
                        try:
                            with open(test_plan_path, 'r', encoding='utf-8') as f:
                                test_plan_content = f.read()
                                analysis_docs.append(f"## 🧪 TEST PLAN\n\n{test_plan_content}")
                        except Exception as e:
                            logger.warning(f"Failed to read test-plan.md: {e}")

                    if analysis_docs:
                        enhanced_context = f"""# 📚 TASK ANALYSIS DOCUMENTATION

{chr(10).join(analysis_docs)}

---

# 💬 ADDITIONAL CONTEXT

{context if context else "No additional context provided."}
"""

                # Start session via API with enhanced context
                response = await client.post(
                    f"{self.server_url}/api/tasks/{task_id}/session/start",
                    json={"context": enhanced_context}
                )
                response.raise_for_status()
                result = response.json()
                
                if result.get("success"):
                    # Check which analysis docs were loaded
                    docs_loaded = []
                    if worktree_path and os.path.exists(worktree_path):
                        if os.path.exists(os.path.join(worktree_path, "Analyse", "requirements.md")):
                            docs_loaded.append("requirements.md")
                        if os.path.exists(os.path.join(worktree_path, "Analyse", "architecture.md")):
                            docs_loaded.append("architecture.md")
                        if os.path.exists(os.path.join(worktree_path, "Tests", "test-plan.md")):
                            docs_loaded.append("test-plan.md")

                    docs_status = ""
                    if docs_loaded:
                        docs_status = f"\n📚 ANALYSIS DOCS LOADED: {', '.join(docs_loaded)}"

                    response_text = f"""🚀 CLAUDE SESSION STARTED - Task #{task_id}

📁 Working Directory: {result.get('session', {}).get('working_dir')}
🆔 Session ID: {result.get('session', {}).get('id')}
📊 Status: {result.get('session', {}).get('status')}{docs_status}

💡 SESSION FEATURES:
- Isolated workspace for this task
- Full access to project codebase
- MCP tools available for task management
- Session persists across reconnections
- Automatic context from analysis documents

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
        """Search codebase using MongoDB Atlas Vector Search API"""
        try:
            project_id = await self._get_active_project_id()

            # Build request body
            request_body = {
                "query": query,
                "limit": top_k
            }
            if language:
                request_body["language"] = language
            if min_similarity:
                request_body["min_similarity"] = min_similarity

            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    f"{self.server_url}/api/codebase-rag/{project_id}/search",
                    json=request_body
                )

                if response.status_code != 200:
                    error_detail = response.json().get("detail", response.text)
                    return [types.TextContent(
                        type="text",
                        text=f"❌ Search failed: {error_detail}"
                    )]

                data = response.json()
                results = data.get("results", [])

                if not results:
                    return [types.TextContent(
                        type="text",
                        text=f"No relevant code found for query: '{query}'"
                    )]

                # Format results
                response_text = f"🔍 **Code Search Results for: '{query}'** (MongoDB Atlas)\n\n"
                response_text += f"Found {len(results)} relevant code chunks:\n"

                if min_similarity:
                    response_text += f"Similarity threshold: {min_similarity}\n"

                response_text += "\n"

                for i, chunk in enumerate(results, 1):
                    file_path = chunk.get('file_path', 'unknown')
                    start_line = chunk.get('start_line', '?')
                    end_line = chunk.get('end_line', '?')
                    chunk_type = chunk.get('chunk_type', 'unknown')
                    lang = chunk.get('language', 'unknown')
                    summary = chunk.get('summary', 'No summary')
                    content = chunk.get('content', '')
                    similarity = chunk.get('similarity_score', 0)

                    response_text += f"**{i}. {file_path}** (lines {start_line}-{end_line}) [score: {similarity:.3f}]\n"
                    response_text += f"   Type: {chunk_type} | Language: {lang}\n"
                    response_text += f"   Summary: {summary}\n"
                    response_text += f"   Code:\n```{lang}\n{content}\n```\n\n"

                return [types.TextContent(type="text", text=response_text)]

        except Exception as e:
            self.logger.error(f"Error searching codebase: {e}")
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
        """Reindex codebase via MongoDB Atlas API (incremental or full)"""
        try:
            project_id = await self._get_active_project_id()

            async with httpx.AsyncClient(timeout=300.0) as client:
                if full_reindex:
                    self.logger.info("Starting full codebase reindex via MongoDB Atlas...")
                    response = await client.post(
                        f"{self.server_url}/api/codebase-rag/{project_id}/index",
                        json={"repo_path": self.project_path, "full_reindex": True}
                    )
                else:
                    self.logger.info("Starting incremental codebase reindex via MongoDB Atlas...")
                    response = await client.post(
                        f"{self.server_url}/api/codebase-rag/{project_id}/reindex",
                        json={"repo_path": self.project_path}
                    )

                if response.status_code == 200:
                    result = response.json()
                    stats = f"Files: {result.get('indexed_files', 'N/A')}, Chunks: {result.get('total_chunks', 'N/A')}"
                    return [types.TextContent(
                        type="text",
                        text=f"✅ {'Full' if full_reindex else 'Incremental'} codebase reindexing completed (MongoDB Atlas)\n\n{stats}"
                    )]
                else:
                    error_detail = response.json().get("detail", response.text)
                    return [types.TextContent(
                        type="text",
                        text=f"❌ Reindex failed: {error_detail}"
                    )]

        except Exception as e:
            self.logger.error(f"Error reindexing codebase: {e}")
            return [types.TextContent(
                type="text",
                text=f"Error reindexing codebase: {str(e)}"
            )]

    async def _index_codebase(self) -> list[types.TextContent]:
        """Index entire codebase from scratch via MongoDB Atlas API"""
        try:
            project_id = await self._get_active_project_id()

            self.logger.info("Starting full codebase indexing via MongoDB Atlas...")
            async with httpx.AsyncClient(timeout=600.0) as client:
                response = await client.post(
                    f"{self.server_url}/api/codebase-rag/{project_id}/index",
                    json={"repo_path": self.project_path, "full_reindex": True}
                )

                if response.status_code == 200:
                    result = response.json()
                    return [types.TextContent(
                        type="text",
                        text=f"✅ Codebase indexing completed (MongoDB Atlas)\n\n"
                             f"Files indexed: {result.get('indexed_files', 'N/A')}\n"
                             f"Total chunks: {result.get('total_chunks', 'N/A')}\n"
                             f"Skipped: {result.get('skipped_files', 0)}"
                    )]
                else:
                    error_detail = response.json().get("detail", response.text)
                    return [types.TextContent(
                        type="text",
                        text=f"❌ Indexing failed: {error_detail}"
                    )]

        except Exception as e:
            self.logger.error(f"Error indexing codebase: {e}")
            return [types.TextContent(
                type="text",
                text=f"❌ Error indexing codebase: {str(e)}"
            )]

    async def _index_files(self, file_paths: list[str]) -> list[types.TextContent]:
        """Index specific files via MongoDB Atlas API"""
        try:
            project_id = await self._get_active_project_id()

            self.logger.info(f"Starting indexing of {len(file_paths)} files via MongoDB Atlas...")
            async with httpx.AsyncClient(timeout=300.0) as client:
                response = await client.post(
                    f"{self.server_url}/api/codebase-rag/{project_id}/index-files",
                    json={"file_paths": file_paths, "repo_path": self.project_path}
                )

                if response.status_code == 200:
                    result = response.json()
                    return [types.TextContent(
                        type="text",
                        text=f"✅ File indexing completed (MongoDB Atlas)\n\n"
                             f"Files indexed: {result.get('indexed_files', 'N/A')}\n"
                             f"Files skipped: {result.get('skipped_files', 0)}\n"
                             f"Total chunks: {result.get('total_chunks', 'N/A')}"
                    )]
                else:
                    error_detail = response.json().get("detail", response.text)
                    return [types.TextContent(
                        type="text",
                        text=f"❌ File indexing failed: {error_detail}"
                    )]

        except Exception as e:
            self.logger.error(f"Error indexing files: {e}")
            return [types.TextContent(
                type="text",
                text=f"❌ Error indexing files: {str(e)}"
            )]

    # Documentation RAG methods

    async def _search_documentation(
        self,
        query: str,
        top_k: int = 20,
        doc_type: Optional[str] = None,
        min_similarity: Optional[float] = None
    ) -> list[types.TextContent]:
        """Search documentation using MongoDB Atlas Vector Search API"""
        try:
            project_id = await self._get_active_project_id()

            # Build request body
            request_body = {
                "query": query,
                "limit": top_k
            }
            if doc_type:
                request_body["doc_type"] = doc_type
            if min_similarity:
                request_body["min_similarity"] = min_similarity

            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    f"{self.server_url}/api/documentation-rag/{project_id}/search",
                    json=request_body
                )

                if response.status_code != 200:
                    error_detail = response.json().get("detail", response.text)
                    return [types.TextContent(
                        type="text",
                        text=f"❌ Documentation search failed: {error_detail}"
                    )]

                data = response.json()
                results = data.get("results", [])

                if not results:
                    return [types.TextContent(
                        type="text",
                        text=f"No relevant documentation found for query: '{query}'"
                    )]

                # Format results
                response_text = f"📚 **Documentation Search Results for: '{query}'** (MongoDB Atlas)\n\n"
                response_text += f"Found {len(results)} relevant documentation sections:\n"

                if doc_type:
                    response_text += f"Doc type filter: {doc_type}\n"
                if min_similarity:
                    response_text += f"Similarity threshold: {min_similarity}\n"

                response_text += "\n"

                for i, chunk in enumerate(results, 1):
                    file_path = chunk.get('file_path', 'unknown')
                    start_line = chunk.get('start_line', '?')
                    end_line = chunk.get('end_line', '?')
                    chunk_doc_type = chunk.get('doc_type', 'unknown')
                    title = chunk.get('title', '')
                    summary = chunk.get('summary', 'No summary')
                    content = chunk.get('content', '')
                    similarity = chunk.get('similarity_score', 0)

                    response_text += f"**{i}. {file_path}** (lines {start_line}-{end_line}) [score: {similarity:.3f}]\n"
                    if title:
                        response_text += f"   Title: {title}\n"
                    response_text += f"   Type: {chunk_doc_type}\n"
                    response_text += f"   Summary: {summary}\n"
                    response_text += f"   Content:\n```markdown\n{content[:500]}{'...' if len(content) > 500 else ''}\n```\n\n"

                return [types.TextContent(type="text", text=response_text)]

        except Exception as e:
            self.logger.error(f"Error searching documentation: {e}")
            return [types.TextContent(
                type="text",
                text=f"Error searching documentation: {str(e)}"
            )]

    async def _index_documentation(self, full_reindex: bool = False) -> list[types.TextContent]:
        """Index documentation files via MongoDB Atlas API"""
        try:
            project_id = await self._get_active_project_id()

            self.logger.info(f"Starting {'full' if full_reindex else 'incremental'} documentation indexing via MongoDB Atlas...")
            async with httpx.AsyncClient(timeout=600.0) as client:
                response = await client.post(
                    f"{self.server_url}/api/documentation-rag/{project_id}/index",
                    json={"repo_path": self.project_path, "full_reindex": full_reindex}
                )

                if response.status_code == 200:
                    result = response.json()
                    return [types.TextContent(
                        type="text",
                        text=f"✅ Documentation indexing completed (MongoDB Atlas)\n\n"
                             f"Files indexed: {result.get('indexed_files', 'N/A')}\n"
                             f"Total chunks: {result.get('total_chunks', 'N/A')}\n"
                             f"Skipped: {result.get('skipped_files', 0)}"
                    )]
                else:
                    error_detail = response.json().get("detail", response.text)
                    return [types.TextContent(
                        type="text",
                        text=f"❌ Documentation indexing failed: {error_detail}"
                    )]

        except Exception as e:
            self.logger.error(f"Error indexing documentation: {e}")
            return [types.TextContent(
                type="text",
                text=f"❌ Error indexing documentation: {str(e)}"
            )]

    async def _reindex_documentation(self) -> list[types.TextContent]:
        """Incrementally reindex documentation via MongoDB Atlas API"""
        try:
            project_id = await self._get_active_project_id()

            self.logger.info("Starting incremental documentation reindex via MongoDB Atlas...")
            async with httpx.AsyncClient(timeout=300.0) as client:
                response = await client.post(
                    f"{self.server_url}/api/documentation-rag/{project_id}/reindex",
                    json={"repo_path": self.project_path}
                )

                if response.status_code == 200:
                    result = response.json()
                    return [types.TextContent(
                        type="text",
                        text=f"✅ Documentation reindex completed (MongoDB Atlas)\n\n"
                             f"New files: {result.get('new_files', 0)}\n"
                             f"Updated files: {result.get('updated_files', 0)}\n"
                             f"Deleted files: {result.get('deleted_files', 0)}\n"
                             f"Total chunks: {result.get('total_chunks', 'N/A')}"
                    )]
                else:
                    error_detail = response.json().get("detail", response.text)
                    return [types.TextContent(
                        type="text",
                        text=f"❌ Documentation reindex failed: {error_detail}"
                    )]

        except Exception as e:
            self.logger.error(f"Error reindexing documentation: {e}")
            return [types.TextContent(
                type="text",
                text=f"Error reindexing documentation: {str(e)}"
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

    async def _update_custom_skill_status(
        self,
        skill_name: str,
        status: str,
        error_message: str | None = None
    ) -> list[types.TextContent]:
        """Update custom skill status and archive it"""
        # Get current active project (not cached - always fresh)
        project_id = await self._get_active_project_id()

        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                self.logger.info(f"Updating skill status: {skill_name} -> {status}")
                self.logger.info(f"Using active project_id: {project_id}")

                # Find skill by name
                url = f"{self.server_url}/api/projects/{project_id}/skills/"
                self.logger.info(f"Fetching skills from: {url}")
                response = await client.get(url)

                if response.status_code != 200:
                    error_text = f"❌ Failed to get skills: {response.status_code}\nURL: {url}\nResponse: {response.text}"
                    self.logger.error(error_text)
                    return [types.TextContent(
                        type="text",
                        text=error_text
                    )]

                skills_data = response.json()
                custom_skills = skills_data.get("custom", [])

                # Find skill by name
                skill = None
                for s in custom_skills:
                    if s["name"] == skill_name:
                        skill = s
                        break

                if not skill:
                    return [types.TextContent(
                        type="text",
                        text=f"❌ Skill '{skill_name}' not found"
                    )]

                skill_id = skill["id"]

                # Update skill status via backend API
                update_response = await client.patch(
                    f"{self.server_url}/api/projects/{project_id}/skills/{skill_id}/status",
                    json={
                        "status": status,
                        "error_message": error_message
                    }
                )

                if update_response.status_code == 200:
                    return [types.TextContent(
                        type="text",
                        text=f"✅ Skill '{skill_name}' status updated to '{status}' and archived successfully"
                    )]
                else:
                    return [types.TextContent(
                        type="text",
                        text=f"❌ Failed to update skill status: {update_response.status_code}\n{update_response.text}"
                    )]

            except Exception as e:
                self.logger.error(f"Error updating skill status: {e}")
                return [types.TextContent(
                    type="text",
                    text=f"❌ Error updating skill status: {str(e)}"
                )]

    async def _update_custom_subagent_status(
        self,
        subagent_type: str,
        status: str,
        error_message: str | None = None
    ) -> list[types.TextContent]:
        """Update custom subagent status and archive it"""
        # Get current active project (not cached - always fresh)
        project_id = await self._get_active_project_id()

        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                self.logger.info(f"Updating subagent status: {subagent_type} -> {status}")
                self.logger.info(f"Using active project_id: {project_id}")

                # Find subagent by type
                response = await client.get(
                    f"{self.server_url}/api/projects/{project_id}/subagents/"
                )

                if response.status_code != 200:
                    return [types.TextContent(
                        type="text",
                        text=f"❌ Failed to get subagents: {response.status_code}"
                    )]

                subagents_data = response.json()
                custom_subagents = subagents_data.get("custom", [])

                # Find subagent by type
                subagent = None
                for s in custom_subagents:
                    if s["subagent_type"] == subagent_type:
                        subagent = s
                        break

                if not subagent:
                    return [types.TextContent(
                        type="text",
                        text=f"❌ Subagent '{subagent_type}' not found"
                    )]

                subagent_id = subagent["id"]

                # Update subagent status via backend API
                update_response = await client.patch(
                    f"{self.server_url}/api/projects/{project_id}/subagents/{subagent_id}/status",
                    json={
                        "status": status,
                        "error_message": error_message
                    }
                )

                if update_response.status_code == 200:
                    return [types.TextContent(
                        type="text",
                        text=f"✅ Subagent '{subagent_type}' status updated to '{status}' and archived successfully"
                    )]
                else:
                    return [types.TextContent(
                        type="text",
                        text=f"❌ Failed to update subagent status: {update_response.status_code}\n{update_response.text}"
                    )]

            except Exception as e:
                self.logger.error(f"Error updating subagent status: {e}")
                return [types.TextContent(
                    type="text",
                    text=f"❌ Error updating subagent status: {str(e)}"
                )]

    async def _get_project_settings(self) -> list[types.TextContent]:
        """Get project settings including project_mode, worktree_enabled, and manual modes"""
        async with httpx.AsyncClient() as client:
            try:
                # Get project data (contains project_mode)
                project_response = await client.get(f"{self.server_url}/api/projects/{self.project_id}")
                project_response.raise_for_status()
                project_data = project_response.json()
                project_mode = project_data.get("project_mode", "simple")

                # Get project settings (contains worktree_enabled and manual_mode)
                settings_response = await client.get(f"{self.server_url}/api/projects/{self.project_id}/settings")
                settings_response.raise_for_status()
                settings_data = settings_response.json()
                worktree_enabled = settings_data.get("worktree_enabled", True)
                manual_mode = settings_data.get("manual_mode", False)

                # Determine workflow mode
                workflow_mode = "Manual" if manual_mode else "Automated"
                testing_variant = "UC-04 Variant B (Manual Testing)" if manual_mode else "UC-04 Variant A (Automated Testing)"
                review_variant = "UC-05 Variant B (Manual Review)" if manual_mode else "UC-05 Variant A (Auto-merge)"

                return [types.TextContent(
                    type="text",
                    text=f"""✅ PROJECT SETTINGS RETRIEVED

📋 Current Configuration:
- **Project Mode**: {project_mode}
- **Worktree Enabled**: {worktree_enabled}
- **Workflow Mode**: {workflow_mode} (manual_mode={manual_mode})
  - Testing: {testing_variant}
  - Code Review: {review_variant}

🎯 Workflow Behavior:
- Testing: {"Manual user testing required" if manual_mode else "Automated testing agents"}
- Review: {"Manual PR review & merge" if manual_mode else "Auto-merge after review"}

🎯 Instructions to Follow:
{self._get_mode_instructions(project_mode, worktree_enabled)}

Use these settings to determine which workflow instructions to apply from CLAUDE.md"""
                )]

            except httpx.HTTPError as e:
                self.logger.error(f"Failed to get project settings: {e}")
                return [types.TextContent(
                    type="text",
                    text=f"""❌ Failed to get project settings: {str(e)}

📋 Using fallback defaults:
- Project Mode: simple
- Worktree Enabled: false
- Workflow Mode: Automated (manual_mode=false)
  - Testing: UC-04 Variant A (Automated Testing)
  - Code Review: UC-05 Variant A (Auto-merge)

Apply SIMPLE mode instructions from CLAUDE.md"""
                )]

    def _get_mode_instructions(self, project_mode: str, worktree_enabled: bool) -> str:
        """Get mode-specific instructions based on settings"""
        if project_mode == "simple":
            return """
**Apply Mode 1 Instructions from CLAUDE.md:**
- SIMPLE Mode (3-column workflow)
- NO worktrees, branches, or PRs
- Direct work in main branch
- Backlog → In Progress → Done
"""
        elif project_mode == "development":
            if worktree_enabled:
                return """
**Apply Mode 2 Instructions from CLAUDE.md:**
- DEVELOPMENT Mode with Worktrees
- Full 6-column workflow
- Create worktrees for each task
- Use git branching and PRs
- Backlog → Analysis → In Progress → Testing → Code Review → Done
"""
            else:
                return """
**Apply Mode 3 Instructions from CLAUDE.md:**
- DEVELOPMENT Mode without Worktrees
- Full 6-column workflow
- Work in main/feature branches (NO worktrees)
- Use git branching and PRs
- Backlog → Analysis → In Progress → Testing → Code Review → Done
"""
        else:
            return f"""
**Unknown project mode: {project_mode}**
Apply SIMPLE mode instructions as fallback.
"""

    async def _save_conversation_message(
        self,
        message_type: str,
        content: str,
        task_id: Optional[int] = None,
        metadata: Optional[dict] = None
    ) -> list[types.TextContent]:
        """Save a conversation message to project memory

        Uses self.project_id from .mcp.json to ensure memory is stored
        in the correct project (the one Claude Code is opened in).
        """
        async with httpx.AsyncClient() as client:
            try:
                # Use project_id from .mcp.json, not active project from backend
                # This ensures memory is tied to the directory Claude Code is opened in
                project_id = self.project_id

                # Save message via backend API
                response = await client.post(
                    f"{self.server_url}/api/projects/{project_id}/memory/messages",
                    json={
                        "message_type": message_type,
                        "content": content,
                        "task_id": task_id,
                        "metadata": metadata
                    }
                )
                response.raise_for_status()

                result = response.json()
                return [types.TextContent(
                    type="text",
                    text=f"✅ Message saved to project memory (ID: {result['id']})"
                )]

            except Exception as e:
                self.logger.error(f"Error saving conversation message: {e}")
                return [types.TextContent(
                    type="text",
                    text=f"❌ Failed to save message: {str(e)}"
                )]

    async def _get_project_memory_context(self) -> list[types.TextContent]:
        """Get full memory context for the current project

        Uses self.project_id from .mcp.json to ensure memory is retrieved
        from the correct project (the one Claude Code is opened in).
        """
        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                # Use project_id from .mcp.json, not active project from backend
                # This ensures memory is tied to the directory Claude Code is opened in
                project_id = self.project_id

                # Get project summary
                summary_response = await client.get(
                    f"{self.server_url}/api/projects/{project_id}/memory/summary"
                )
                summary_data = summary_response.json() if summary_response.status_code == 200 else None

                # Get last 30 messages
                messages_response = await client.get(
                    f"{self.server_url}/api/projects/{project_id}/memory/messages?limit=30"
                )
                messages_json = messages_response.json() if messages_response.status_code == 200 else {}
                # API returns {"messages": [...], "total": N, "storage_mode": "..."}
                messages_data = messages_json.get("messages", []) if isinstance(messages_json, dict) else []

                # Perform RAG search if current task exists
                task_response = await client.get(f"{self.server_url}/api/mcp/current-task")
                relevant_memories = []
                if task_response.status_code == 200:
                    current_task = task_response.json()
                    if current_task and self.rag_initialized:
                        # Search for relevant memories
                        rag_results = await self.rag_service.search_memories(
                            project_id=project_id,
                            query=f"{current_task.get('title', '')} {current_task.get('description', '')}",
                            limit=20
                        )
                        relevant_memories = rag_results if rag_results else []

                # Format context
                context = f"""📚 PROJECT MEMORY CONTEXT LOADED

### 📋 Project Summary
{summary_data.get('summary', 'No summary available yet.') if summary_data else 'No summary available yet.'}

### 🕐 Last 30 Messages ({len(messages_data)} messages)
"""

                for msg in messages_data:  # Show all 30 messages for full context
                    content = msg.get('content', '')
                    content_preview = content[:150] if len(content) > 150 else content
                    timestamp = msg.get('timestamp', 'unknown')
                    msg_type = msg.get('message_type', 'unknown').upper()
                    context += f"\n[{timestamp}] {msg_type}: {content_preview}..."

                if relevant_memories:
                    context += f"\n\n### 🔍 Relevant Memories (RAG Search)\n"
                    for memory in relevant_memories[:5]:
                        context += f"- {memory.get('content', '')[:150]}...\n"

                context += "\n\n✅ Context loaded successfully. You have full project history available."

                return [types.TextContent(
                    type="text",
                    text=context
                )]

            except Exception as e:
                self.logger.error(f"Error getting project memory context: {e}")
                return [types.TextContent(
                    type="text",
                    text=f"⚠️ Could not load full memory context: {str(e)}\nContinuing without historical context."
                )]

    async def _update_project_summary(
        self,
        trigger: str,
        new_insights: str
    ) -> list[types.TextContent]:
        """Update project summary with new insights

        Uses self.project_id from .mcp.json to ensure summary is updated
        for the correct project (the one Claude Code is opened in).
        """
        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                # Use project_id from .mcp.json, not active project from backend
                # This ensures memory is tied to the directory Claude Code is opened in
                project_id = self.project_id

                # Update summary via backend API
                response = await client.post(
                    f"{self.server_url}/api/projects/{project_id}/memory/summary/update",
                    json={
                        "trigger": trigger,
                        "new_insights": new_insights
                    }
                )
                response.raise_for_status()

                return [types.TextContent(
                    type="text",
                    text=f"✅ Project summary updated (trigger: {trigger})"
                )]

            except Exception as e:
                self.logger.error(f"Error updating project summary: {e}")
                return [types.TextContent(
                    type="text",
                    text=f"❌ Failed to update summary: {str(e)}"
                )]

    async def _search_project_memories(
        self,
        query: str,
        limit: int = 20,
        session_id: Optional[str] = None,
        filters: Optional[dict] = None
    ) -> list[types.TextContent]:
        """Search project memory using RAG

        Uses self.project_id from .mcp.json to ensure search is performed
        for the correct project (the one Claude Code is opened in).

        Args:
            query: Search query
            limit: Max results to return
            session_id: Filter by session ID. Use 'current' for current session,
                       'last' for previous session, or specific UUID
            filters: Optional additional filters
        """
        try:
            if not self.rag_initialized:
                return [types.TextContent(
                    type="text",
                    text="⚠️ RAG service not initialized. Memory search unavailable."
                )]

            # Use project_id from .mcp.json, not active project from backend
            # This ensures memory is tied to the directory Claude Code is opened in
            project_id = self.project_id

            # Handle special session_id values
            resolved_session_id = None
            if session_id:
                if session_id.lower() == 'current':
                    # Get current session from database
                    resolved_session_id = await self._get_current_session_id(project_id)
                elif session_id.lower() == 'last':
                    # Get last (previous) session from database
                    resolved_session_id = await self._get_last_session_id(project_id)
                else:
                    # Use provided UUID directly
                    resolved_session_id = session_id

            # Add session_id to filters if provided
            search_filters = filters.copy() if filters else {}
            if resolved_session_id:
                search_filters['session_id'] = resolved_session_id

            # Perform RAG search
            results = await self.rag_service.search_memories(
                project_id=project_id,
                query=query,
                limit=limit,
                filters=search_filters if search_filters else None
            )

            if not results:
                session_info = f" (session: {resolved_session_id[:8]}...)" if resolved_session_id else ""
                return [types.TextContent(
                    type="text",
                    text=f"No memories found for query: '{query}'{session_info}"
                )]

            # Format results
            session_info = f" (session: {resolved_session_id[:8]}...)" if resolved_session_id else ""
            output = f"🔍 Found {len(results)} relevant memories{session_info}:\n\n"
            for i, result in enumerate(results, 1):
                output += f"{i}. {result.get('content', '')[:200]}...\n"
                output += f"   Relevance: {result.get('score', 0):.2f}\n\n"

            return [types.TextContent(
                type="text",
                text=output
            )]

        except Exception as e:
            self.logger.error(f"Error searching project memories: {e}")
            return [types.TextContent(
                type="text",
                text=f"❌ Search failed: {str(e)}"
            )]

    async def _get_current_session_id(self, project_id: str) -> Optional[str]:
        """Get the most recent session ID for a project"""
        try:
            import aiohttp
            async with aiohttp.ClientSession() as session:
                url = f"{self.backend_url}/api/projects/{project_id}/memory/sessions/current"
                async with session.get(url, timeout=5) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data.get('session_id')
        except Exception as e:
            self.logger.warning(f"Failed to get current session: {e}")
        return None

    async def _get_last_session_id(self, project_id: str) -> Optional[str]:
        """Get the previous (second most recent) session ID for a project"""
        try:
            import aiohttp
            async with aiohttp.ClientSession() as session:
                url = f"{self.backend_url}/api/projects/{project_id}/memory/sessions/last"
                async with session.get(url, timeout=5) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data.get('session_id')
        except Exception as e:
            self.logger.warning(f"Failed to get last session: {e}")
        return None

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
    # Configure logging for MCP calls
    import logging
    from pathlib import Path

    parser = argparse.ArgumentParser(description="ClaudeTask MCP Bridge Server")
    parser.add_argument("--project-id", required=True, help="Project ID")
    parser.add_argument("--project-path", required=True, help="Project path")
    parser.add_argument("--server", default="http://localhost:3333", help="Backend server URL")

    args = parser.parse_args()

    # Create logs directory in project's .claudetask folder
    project_path = Path(args.project_path)
    log_dir = project_path / ".claudetask" / "logs" / "mcp"
    log_dir.mkdir(parents=True, exist_ok=True)

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),  # Console output
            logging.FileHandler(log_dir / 'mcp_calls.log')  # File output in project's .claudetask folder
        ]
    )

    server = ClaudeTaskMCPServer(
        project_id=args.project_id,
        project_path=args.project_path,
        server_url=args.server
    )
    
    await server.run()


if __name__ == "__main__":
    asyncio.run(main())