"""WebSocket connection manager for real-time task updates"""

import logging
from typing import Dict, Set, Optional
from fastapi import WebSocket
import json
import asyncio
from datetime import datetime

logger = logging.getLogger(__name__)


class TaskWebSocketManager:
    """Manages WebSocket connections for real-time task updates"""
    
    def __init__(self):
        # Store active connections by project_id
        self._connections: Dict[str, Set[WebSocket]] = {}
        self._connection_projects: Dict[WebSocket, str] = {}
        self._lock = asyncio.Lock()
    
    async def connect(self, websocket: WebSocket, project_id: str):
        """Accept and register a WebSocket connection for a project"""
        await websocket.accept()
        
        async with self._lock:
            # Add websocket to project's connection set
            if project_id not in self._connections:
                self._connections[project_id] = set()
            self._connections[project_id].add(websocket)
            self._connection_projects[websocket] = project_id
        
        logger.info(f"WebSocket connected for project {project_id}. Total connections: {len(self._connections.get(project_id, set()))}")
        
        # Send initial connection success message
        await websocket.send_json({
            "type": "connection",
            "status": "connected",
            "project_id": project_id,
            "timestamp": datetime.utcnow().isoformat()
        })
    
    async def disconnect(self, websocket: WebSocket):
        """Remove a WebSocket connection"""
        async with self._lock:
            # Find and remove the connection
            project_id = self._connection_projects.get(websocket)
            if project_id:
                if project_id in self._connections:
                    self._connections[project_id].discard(websocket)
                    # Clean up empty sets
                    if not self._connections[project_id]:
                        del self._connections[project_id]
                del self._connection_projects[websocket]
                logger.info(f"WebSocket disconnected from project {project_id}")
    
    async def broadcast_task_update(self, project_id: str, event_type: str, task_data: dict):
        """Broadcast a task update to all connected clients for a project"""
        if project_id not in self._connections:
            return
        
        message = {
            "type": "task_update",
            "event": event_type,
            "task": task_data,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Send to all connections for this project
        disconnected = []
        for websocket in self._connections[project_id]:
            try:
                await websocket.send_json(message)
            except Exception as e:
                logger.error(f"Error sending to websocket: {e}")
                disconnected.append(websocket)
        
        # Clean up disconnected clients
        for ws in disconnected:
            await self.disconnect(ws)
        
        logger.info(f"Broadcast {event_type} to {len(self._connections[project_id])} clients for project {project_id}")

    async def broadcast_message(self, message: dict, project_id: Optional[str] = None):
        """Broadcast a generic message to clients
        
        Args:
            message: The message dict to broadcast
            project_id: Optional project_id to broadcast to specific project.
                       If None, extracts from message['project_id'] if available
        """
        # Determine target project
        target_project = project_id or message.get('project_id')
        
        if not target_project:
            logger.warning("No project_id specified for broadcast_message")
            return
            
        if target_project not in self._connections:
            logger.debug(f"No active connections for project {target_project}")
            return
        
        # Add timestamp if not present
        if 'timestamp' not in message:
            message['timestamp'] = datetime.utcnow().isoformat()
        
        # Send to all connections for this project
        disconnected = []
        for websocket in self._connections[target_project]:
            try:
                await websocket.send_json(message)
            except Exception as e:
                logger.error(f"Error sending to websocket: {e}")
                disconnected.append(websocket)
        
        # Clean up disconnected clients
        for ws in disconnected:
            await self.disconnect(ws)
        
        logger.info(f"Broadcast message type '{message.get('type')}' to {len(self._connections[target_project])} clients for project {target_project}")
    
    async def send_error(self, websocket: WebSocket, error_message: str):
        """Send an error message to a specific client"""
        try:
            await websocket.send_json({
                "type": "error",
                "message": error_message,
                "timestamp": datetime.utcnow().isoformat()
            })
        except Exception as e:
            logger.error(f"Failed to send error message: {e}")
    
    async def handle_ping(self, websocket: WebSocket):
        """Handle ping message from client"""
        try:
            await websocket.send_json({
                "type": "pong",
                "timestamp": datetime.utcnow().isoformat()
            })
        except Exception as e:
            logger.error(f"Failed to send pong: {e}")
    
    def get_connection_count(self, project_id: Optional[str] = None) -> int:
        """Get the number of active connections"""
        if project_id:
            return len(self._connections.get(project_id, set()))
        return sum(len(conns) for conns in self._connections.values())
    
    def get_connected_projects(self) -> list:
        """Get list of projects with active connections"""
        return list(self._connections.keys())


# Global instance
task_websocket_manager = TaskWebSocketManager()