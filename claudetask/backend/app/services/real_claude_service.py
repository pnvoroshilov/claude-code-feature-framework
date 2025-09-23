import asyncio
import threading
import pexpect
import json
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime

logger = logging.getLogger(__name__)

class RealClaudeSession:
    def __init__(self, session_id: str, task_id: int, working_dir: str):
        self.session_id = session_id
        self.task_id = task_id
        self.working_dir = working_dir
        self.child: Optional[pexpect.spawn] = None
        self.is_running = False
        self.websocket_clients: List[Any] = []
        self.stop_reading = threading.Event()
        self.read_thread: Optional[threading.Thread] = None
        self.main_loop: Optional[asyncio.AbstractEventLoop] = None
        self.claude_initialized = False
        self.output_history: List[Dict[str, Any]] = []
        self.max_history_size = 1000  # Keep last 1000 messages

    async def start(self) -> bool:
        """Start Claude process"""
        try:
            logger.info(f"Starting Claude process for session {self.session_id}")
            
            # Store the current event loop
            self.main_loop = asyncio.get_running_loop()
            
            # Start Claude with pexpect in dangerous mode
            self.child = pexpect.spawn(
                'claude --dangerously-skip-permissions',
                cwd=self.working_dir,
                timeout=None,
                encoding='utf-8',
                codec_errors='ignore'
            )
            
            if not self.child.isalive():
                logger.error("Failed to start Claude process")
                return False
            
            self.is_running = True
            
            # Start reading output in separate thread
            self.read_thread = threading.Thread(target=self._read_output_thread, daemon=True)
            self.read_thread.start()
            
            logger.info(f"Claude started successfully, PID: {self.child.pid}")
            return True
            
        except Exception as e:
            logger.error(f"Error starting Claude: {e}")
            return False

    def _read_output_thread(self):
        """Read all output from Claude and send to clients"""
        try:
            while not self.stop_reading.is_set() and self.child and self.child.isalive():
                try:
                    # Read any available data
                    data = self.child.read_nonblocking(size=1024, timeout=0.1)
                    if data:
                        # Send raw data to all WebSocket clients
                        self._send_to_clients(data)
                        
                except pexpect.TIMEOUT:
                    continue
                except pexpect.EOF:
                    logger.info("Claude process ended")
                    break
                except Exception as e:
                    logger.error(f"Error reading output: {e}")
                    break
                    
        except Exception as e:
            logger.error(f"Fatal error in read thread: {e}")
        finally:
            logger.info(f"Output reader thread exiting for session {self.session_id}")

    def _send_to_clients(self, content: str):
        """Send content to all connected WebSocket clients"""
        # Create message
        message = {
            "type": "output",
            "content": content,
            "timestamp": datetime.now().isoformat()
        }
        
        # Store in history
        self._store_in_history(message)
        
        # Check if this is initial Claude output and we haven't sent the task command yet
        if not self.claude_initialized and ("Claude" in content or "Welcome" in content or ">" in content):
            self.claude_initialized = True
            # Schedule sending the task initialization command
            self._schedule_task_initialization()
        
        # Send to all connected clients
        if self.websocket_clients and self.main_loop:
            disconnected_clients = []
            for client in self.websocket_clients:
                try:
                    # Schedule the coroutine in the main event loop
                    if self.main_loop and not self.main_loop.is_closed():
                        asyncio.run_coroutine_threadsafe(
                            client.send_json(message),
                            self.main_loop
                        )
                    else:
                        logger.warning("Main event loop is not available")
                        disconnected_clients.append(client)
                except Exception as e:
                    logger.warning(f"Failed to send to client: {e}")
                    disconnected_clients.append(client)
            
            # Remove disconnected clients
            for client in disconnected_clients:
                if client in self.websocket_clients:
                    self.websocket_clients.remove(client)
    
    def _store_in_history(self, message: Dict[str, Any]):
        """Store message in session history"""
        self.output_history.append(message)
        
        # Keep history size manageable
        if len(self.output_history) > self.max_history_size:
            self.output_history = self.output_history[-self.max_history_size:]
    
    def get_history(self) -> List[Dict[str, Any]]:
        """Get session history"""
        return self.output_history.copy()
    
    def send_history_to_client(self, client):
        """Send full history to a reconnecting client"""
        if not self.main_loop or not self.output_history:
            return
            
        try:
            # Send a special "history" message
            history_message = {
                "type": "history",
                "content": self.output_history,
                "timestamp": datetime.now().isoformat()
            }
            
            if self.main_loop and not self.main_loop.is_closed():
                asyncio.run_coroutine_threadsafe(
                    client.send_json(history_message),
                    self.main_loop
                )
        except Exception as e:
            logger.warning(f"Failed to send history to client: {e}")
    
    def _schedule_task_initialization(self):
        """Schedule sending the task initialization command"""
        if self.main_loop and not self.main_loop.is_closed():
            # Wait a bit to let Claude fully initialize, then send command
            asyncio.run_coroutine_threadsafe(
                self._send_task_command_delayed(),
                self.main_loop
            )
    
    async def _send_task_command_delayed(self):
        """Send task initialization command after a delay"""
        try:
            # Wait 2 seconds for Claude to fully initialize
            await asyncio.sleep(2)
            # Send the /start-feature command with task ID
            task_command = f"/start-feature {self.task_id}"
            await self.send_input(task_command)
            # Wait a moment and send Enter
            await asyncio.sleep(0.5)
            await self.send_input("\r")
            logger.info(f"Sent /start-feature command for Task #{self.task_id}")
        except Exception as e:
            logger.error(f"Failed to send task initialization command: {e}")

    async def send_input(self, data: str) -> bool:
        """Send input to Claude"""
        try:
            if not self.child or not self.child.isalive():
                return False
            
            logger.debug(f"Sending input: {repr(data)}")
            self.child.send(data)
            return True
            
        except Exception as e:
            logger.error(f"Error sending input: {e}")
            return False

    def add_websocket_client(self, websocket):
        """Add WebSocket client and send history"""
        self.websocket_clients.append(websocket)
        logger.info(f"Added WebSocket client, total: {len(self.websocket_clients)}")
        
        # Send history to the new client
        if self.output_history:
            self.send_history_to_client(websocket)
            logger.info(f"Sent {len(self.output_history)} history messages to new client")

    def remove_websocket_client(self, websocket):
        """Remove WebSocket client"""
        if websocket in self.websocket_clients:
            self.websocket_clients.remove(websocket)
            logger.info(f"Removed WebSocket client, total: {len(self.websocket_clients)}")

    async def stop(self) -> bool:
        """Stop the session"""
        try:
            logger.info(f"Stopping session {self.session_id} for task {self.task_id}")
            
            # Signal the read thread to stop
            self.stop_reading.set()
            
            # Clear reconnect timeout if any
            if hasattr(self, 'reconnect_timeout'):
                if self.reconnect_timeout:
                    self.reconnect_timeout.cancel()
            
            # Terminate the child process
            if self.child and self.child.isalive():
                logger.info(f"Terminating Claude process PID: {self.child.pid}")
                try:
                    # Try graceful termination first
                    self.child.sendcontrol('c')  # Send Ctrl+C
                    await asyncio.sleep(0.5)
                    
                    if self.child.isalive():
                        self.child.terminate(force=True)
                        self.child.wait()
                except Exception as term_error:
                    logger.error(f"Error terminating process: {term_error}")
                    # Force kill if terminate fails
                    try:
                        import signal
                        import os
                        os.kill(self.child.pid, signal.SIGKILL)
                    except:
                        pass
            
            self.is_running = False
            
            # Wait for read thread to finish
            if self.read_thread and self.read_thread.is_alive():
                self.read_thread.join(timeout=2)
                if self.read_thread.is_alive():
                    logger.warning(f"Read thread didn't stop cleanly for session {self.session_id}")
            
            # Close all WebSocket connections
            for client in self.websocket_clients[:]:
                try:
                    await client.close()
                except:
                    pass
            self.websocket_clients.clear()
            
            logger.info(f"Session {self.session_id} stopped successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error stopping session: {e}", exc_info=True)
            return False


class RealClaudeService:
    def __init__(self):
        self.sessions: Dict[str, RealClaudeSession] = {}

    async def create_session(self, task_id: int, project_path: str, session_id: str) -> Dict[str, Any]:
        """Create a new Claude session"""
        try:
            session = RealClaudeSession(session_id, task_id, project_path)
            
            if await session.start():
                self.sessions[session_id] = session
                return {
                    "success": True,
                    "session_id": session_id,
                    "info": {
                        "pid": session.child.pid if session.child else None,
                        "working_dir": project_path
                    }
                }
            else:
                return {"success": False, "error": "Failed to start Claude process"}
                
        except Exception as e:
            logger.error(f"Error creating session: {e}")
            return {"success": False, "error": str(e)}

    def get_session(self, session_id: str) -> Optional[RealClaudeSession]:
        """Get session by ID"""
        return self.sessions.get(session_id)

    async def send_input(self, session_id: str, data: str) -> bool:
        """Send input to session"""
        session = self.get_session(session_id)
        if session:
            return await session.send_input(data)
        return False

    async def stop_session(self, session_id: str) -> bool:
        """Stop a session"""
        session = self.sessions.get(session_id)
        if session:
            success = await session.stop()
            if success:
                del self.sessions[session_id]
            return success
        return False

    def get_active_sessions(self) -> List[Dict[str, Any]]:
        """Get all active sessions"""
        return [
            {
                "session_id": session_id,
                "task_id": session.task_id,
                "is_running": session.is_running,
                "working_dir": session.working_dir,
                "clients": len(session.websocket_clients)
            }
            for session_id, session in self.sessions.items()
        ]


# Global service instance
real_claude_service = RealClaudeService()