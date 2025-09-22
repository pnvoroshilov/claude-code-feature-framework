"""Claude Code session management service for task-based development"""

import os
import json
import uuid
import asyncio
import subprocess
from typing import Optional, Dict, Any, List
from datetime import datetime
from pathlib import Path
import logging
from enum import Enum

logger = logging.getLogger(__name__)


class SessionStatus(Enum):
    """Session status enumeration"""
    IDLE = "idle"
    INITIALIZING = "initializing"
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    ERROR = "error"


class SessionMessage:
    """Represents a message in Claude session"""
    def __init__(self, role: str, content: str, timestamp: Optional[datetime] = None):
        self.role = role  # user, assistant, system
        self.content = content
        self.timestamp = timestamp or datetime.utcnow()
        self.tools_used = []
        self.artifacts = []
    
    def to_dict(self):
        return {
            "role": self.role,
            "content": self.content,
            "timestamp": self.timestamp.isoformat(),
            "tools_used": self.tools_used,
            "artifacts": self.artifacts
        }


class ClaudeSessionService:
    """Service for managing Claude Code sessions per task"""
    
    def __init__(self):
        self.active_sessions = {}  # task_id -> session_data
        self.session_processes = {}  # task_id -> process
        
    async def create_session(
        self,
        task_id: int,
        project_path: str,
        worktree_path: Optional[str] = None,
        initial_context: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create a new Claude session for a task
        
        Args:
            task_id: Task ID
            project_path: Main project path
            worktree_path: Task worktree path (if exists)
            initial_context: Initial context/instructions for Claude
            
        Returns:
            Session information dict
        """
        try:
            session_id = f"session-{task_id}-{uuid.uuid4().hex[:8]}"
            
            # Determine working directory
            working_dir = worktree_path or project_path
            
            session_data = {
                "id": session_id,
                "task_id": task_id,
                "status": SessionStatus.INITIALIZING.value,
                "project_path": project_path,
                "working_dir": working_dir,
                "worktree_path": worktree_path,
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat(),
                "messages": [],
                "context": initial_context or "",
                "metadata": {
                    "total_messages": 0,
                    "tools_used_count": {},
                    "errors": [],
                    "artifacts_created": []
                }
            }
            
            # Store session in memory (will be persisted to DB later)
            self.active_sessions[task_id] = session_data
            
            # Initialize Claude context
            if initial_context:
                await self._initialize_context(session_data, initial_context)
            
            session_data["status"] = SessionStatus.ACTIVE.value
            
            logger.info(f"Created Claude session {session_id} for task {task_id}")
            
            return {
                "success": True,
                "session": session_data,
                "message": f"Session {session_id} created successfully"
            }
            
        except Exception as e:
            logger.error(f"Failed to create session: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to create Claude session"
            }
    
    async def _initialize_context(self, session_data: Dict, context: str):
        """Initialize Claude session with context"""
        try:
            # Add system message with context
            system_message = SessionMessage(
                role="system",
                content=f"Task Context: {context}\n\nWorking Directory: {session_data['working_dir']}"
            )
            session_data["messages"].append(system_message.to_dict())
            
            # Read CLAUDE.md if exists
            claude_md_path = os.path.join(session_data['project_path'], "CLAUDE.md")
            if os.path.exists(claude_md_path):
                with open(claude_md_path, 'r') as f:
                    claude_instructions = f.read()
                    instruction_msg = SessionMessage(
                        role="system",
                        content=f"Project Instructions:\n{claude_instructions}"
                    )
                    session_data["messages"].append(instruction_msg.to_dict())
                    
        except Exception as e:
            logger.error(f"Failed to initialize context: {str(e)}")
    
    async def send_message(
        self,
        task_id: int,
        message: str,
        role: str = "user"
    ) -> Dict[str, Any]:
        """
        Send a message to Claude session
        
        Args:
            task_id: Task ID
            message: Message content
            role: Message role (user/system)
            
        Returns:
            Response dict with Claude's reply
        """
        try:
            session_data = self.active_sessions.get(task_id)
            if not session_data:
                return {
                    "success": False,
                    "error": "No active session for this task"
                }
            
            if session_data["status"] != SessionStatus.ACTIVE.value:
                return {
                    "success": False,
                    "error": f"Session is {session_data['status']}, not active"
                }
            
            # Add user message
            user_msg = SessionMessage(role=role, content=message)
            session_data["messages"].append(user_msg.to_dict())
            session_data["metadata"]["total_messages"] += 1
            
            # Here we would integrate with actual Claude API
            # For now, simulate a response
            assistant_response = await self._process_with_claude(
                session_data, message
            )
            
            # Add assistant response
            assistant_msg = SessionMessage(
                role="assistant",
                content=assistant_response["content"]
            )
            assistant_msg.tools_used = assistant_response.get("tools_used", [])
            assistant_msg.artifacts = assistant_response.get("artifacts", [])
            
            session_data["messages"].append(assistant_msg.to_dict())
            session_data["updated_at"] = datetime.utcnow().isoformat()
            
            # Update metadata
            for tool in assistant_msg.tools_used:
                tool_name = tool.get("name", "unknown")
                session_data["metadata"]["tools_used_count"][tool_name] = \
                    session_data["metadata"]["tools_used_count"].get(tool_name, 0) + 1
            
            return {
                "success": True,
                "response": assistant_msg.to_dict(),
                "session_status": session_data["status"]
            }
            
        except Exception as e:
            logger.error(f"Failed to send message: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _process_with_claude(
        self,
        session_data: Dict,
        message: str
    ) -> Dict[str, Any]:
        """
        Process message with Claude (placeholder for actual integration)
        
        This would integrate with Claude API or MCP bridge
        """
        # Simulate Claude processing
        await asyncio.sleep(0.5)
        
        # Placeholder response
        return {
            "content": f"I understand you want to work on task {session_data['task_id']}. "
                      f"I'm analyzing the codebase in {session_data['working_dir']}...",
            "tools_used": [
                {"name": "Read", "count": 1},
                {"name": "Grep", "count": 2}
            ],
            "artifacts": []
        }
    
    async def pause_session(self, task_id: int) -> Dict[str, Any]:
        """Pause an active session"""
        try:
            session_data = self.active_sessions.get(task_id)
            if not session_data:
                return {
                    "success": False,
                    "error": "No active session for this task"
                }
            
            if session_data["status"] == SessionStatus.ACTIVE.value:
                session_data["status"] = SessionStatus.PAUSED.value
                session_data["updated_at"] = datetime.utcnow().isoformat()
                
                logger.info(f"Paused session for task {task_id}")
                
                return {
                    "success": True,
                    "message": "Session paused successfully"
                }
            else:
                return {
                    "success": False,
                    "error": f"Cannot pause session in {session_data['status']} state"
                }
                
        except Exception as e:
            logger.error(f"Failed to pause session: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def resume_session(self, task_id: int) -> Dict[str, Any]:
        """Resume a paused session"""
        try:
            session_data = self.active_sessions.get(task_id)
            if not session_data:
                return {
                    "success": False,
                    "error": "No session found for this task"
                }
            
            if session_data["status"] == SessionStatus.PAUSED.value:
                session_data["status"] = SessionStatus.ACTIVE.value
                session_data["updated_at"] = datetime.utcnow().isoformat()
                
                logger.info(f"Resumed session for task {task_id}")
                
                return {
                    "success": True,
                    "message": "Session resumed successfully",
                    "session": session_data
                }
            else:
                return {
                    "success": False,
                    "error": f"Cannot resume session in {session_data['status']} state"
                }
                
        except Exception as e:
            logger.error(f"Failed to resume session: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def complete_session(
        self,
        task_id: int,
        summary: Optional[str] = None
    ) -> Dict[str, Any]:
        """Complete and archive a session"""
        try:
            session_data = self.active_sessions.get(task_id)
            if not session_data:
                return {
                    "success": False,
                    "error": "No session found for this task"
                }
            
            session_data["status"] = SessionStatus.COMPLETED.value
            session_data["updated_at"] = datetime.utcnow().isoformat()
            session_data["completed_at"] = datetime.utcnow().isoformat()
            
            if summary:
                session_data["summary"] = summary
            
            # Generate session statistics
            stats = {
                "total_messages": session_data["metadata"]["total_messages"],
                "tools_used": session_data["metadata"]["tools_used_count"],
                "duration": self._calculate_duration(
                    session_data["created_at"],
                    session_data["completed_at"]
                ),
                "artifacts_created": len(session_data["metadata"]["artifacts_created"])
            }
            session_data["statistics"] = stats
            
            logger.info(f"Completed session for task {task_id}")
            
            return {
                "success": True,
                "message": "Session completed successfully",
                "statistics": stats
            }
            
        except Exception as e:
            logger.error(f"Failed to complete session: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _calculate_duration(self, start: str, end: str) -> str:
        """Calculate session duration"""
        try:
            start_dt = datetime.fromisoformat(start)
            end_dt = datetime.fromisoformat(end)
            duration = end_dt - start_dt
            
            hours, remainder = divmod(duration.seconds, 3600)
            minutes, seconds = divmod(remainder, 60)
            
            return f"{hours}h {minutes}m {seconds}s"
        except:
            return "N/A"
    
    async def get_session(self, task_id: int) -> Optional[Dict[str, Any]]:
        """Get session data for a task"""
        return self.active_sessions.get(task_id)
    
    async def get_session_messages(
        self,
        task_id: int,
        limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Get messages from a session"""
        session_data = self.active_sessions.get(task_id)
        if not session_data:
            return []
        
        messages = session_data.get("messages", [])
        if limit:
            return messages[-limit:]
        return messages
    
    async def stream_session_output(
        self,
        task_id: int,
        callback: callable
    ):
        """
        Stream real-time session output to callback function
        
        This would be used for WebSocket streaming to UI
        """
        session_data = self.active_sessions.get(task_id)
        if not session_data:
            await callback({
                "error": "No session found"
            })
            return
        
        # Stream messages as they come
        last_index = 0
        while session_data["status"] == SessionStatus.ACTIVE.value:
            messages = session_data.get("messages", [])
            if len(messages) > last_index:
                # Send new messages
                for msg in messages[last_index:]:
                    await callback({
                        "type": "message",
                        "data": msg
                    })
                last_index = len(messages)
            
            # Also send status updates
            await callback({
                "type": "status",
                "data": {
                    "status": session_data["status"],
                    "updated_at": session_data["updated_at"]
                }
            })
            
            await asyncio.sleep(1)  # Poll interval
    
    async def export_session(self, task_id: int) -> Dict[str, Any]:
        """Export session data for persistence or analysis"""
        session_data = self.active_sessions.get(task_id)
        if not session_data:
            return {
                "success": False,
                "error": "No session found"
            }
        
        return {
            "success": True,
            "data": session_data
        }