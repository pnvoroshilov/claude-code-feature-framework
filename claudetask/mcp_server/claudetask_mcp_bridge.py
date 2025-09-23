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
        
        # Available local agents (verified to exist in /agents/development/)
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
            "ux-ui-researcher",
            "web-tester"
        ]
        
        # Agent mapping for task types and statuses with intelligent specialization
        self.agent_mappings = {
            "Feature": {
                "Ready": "frontend-developer",
                "In Progress": "frontend-developer",
                "Testing": "background-tester",
                "Code Review": "fullstack-code-reviewer"
            },
            "Bug": {
                "Ready": "backend-architect",
                "In Progress": "backend-architect",
                "Testing": "background-tester",
                "Code Review": "fullstack-code-reviewer"
            },
            "Refactoring": {
                "Ready": "backend-architect",
                "In Progress": "backend-architect",
                "Testing": "background-tester",
                "Code Review": "fullstack-code-reviewer"
            },
            "Documentation": {
                "Ready": "docs-generator",
                "In Progress": "docs-generator",
                "Testing": "docs-generator",
                "Code Review": "fullstack-code-reviewer"
            },
            "Performance": {
                "Ready": "devops-engineer",
                "In Progress": "devops-engineer",
                "Testing": "background-tester",
                "Code Review": "fullstack-code-reviewer"
            },
            "Security": {
                "Ready": "devops-engineer",
                "In Progress": "devops-engineer",
                "Testing": "background-tester",
                "Code Review": "fullstack-code-reviewer"
            },
            "DevOps": {
                "Ready": "devops-engineer",
                "In Progress": "devops-engineer",
                "Testing": "devops-engineer",
                "Code Review": "fullstack-code-reviewer"
            },
            "MCP": {
                "Ready": "mcp-engineer",
                "In Progress": "mcp-engineer",
                "Testing": "background-tester",
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
                                    "background-tester", "context-analyzer", "data-formatter",
                                    "devops-engineer", "docs-generator", "frontend-developer",
                                    "fullstack-code-reviewer", "mcp-engineer", "memory-sync",
                                    "mobile-react-expert", "python-api-expert"
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

    def _get_agent_for_task(self, task_type: str, status: str, title: str = "", description: str = "") -> str:
        """Get the appropriate agent for a task type and status with intelligent context analysis"""
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
                result = response.json()
                
                # Get task details to provide progression guidance
                task_response = await client.get(f"{self.server_url}/api/tasks/{task_id}")
                task_response.raise_for_status()
                task = task_response.json()
                
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
                    
                    response_text = f"""{status_emoji} TASK COMPLETION - Task #{task_id}

📋 Task: {task['title']}
🌳 Branch: {task['git_branch']}

🎯 RESULTS:
- Merged to main: {'✅ Yes' if result.get('merged') else '❌ No'}
- Worktree removed: {'✅ Yes' if result.get('worktree_removed') else '❌ No'}  
- Branch deleted: {'✅ Yes' if result.get('branch_deleted') else '❌ No'}
"""
                    
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