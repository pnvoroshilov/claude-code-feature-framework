"""Enhanced Claude Terminal Service with WebSocket streaming"""

import asyncio
import json
import logging
import os
import uuid
from typing import Dict, Optional, Any, List
from datetime import datetime
import pexpect
import threading
from dataclasses import dataclass, asdict
from enum import Enum

logger = logging.getLogger(__name__)


class MessageType(Enum):
    """Types of messages in Claude terminal"""
    SYSTEM = "system"
    USER = "user"
    CLAUDE = "claude"
    ERROR = "error"
    TOOL = "tool"
    STATUS = "status"


class MessageSubtype(Enum):
    """Subtypes for more detailed message classification"""
    INIT = "init"
    COMPLETE = "complete"
    TOOL_USE = "tool_use"
    TOOL_RESULT = "tool_result"
    ERROR = "error"
    PROMPT = "prompt"
    RESPONSE = "response"


@dataclass
class ClaudeMessage:
    """Structured message from Claude terminal"""
    type: str
    content: str
    timestamp: str
    subtype: Optional[str] = None
    session_id: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    
    def to_json(self) -> str:
        """Convert to JSON string"""
        return json.dumps(asdict(self))


class ClaudeTerminalSession:
    """Manages a single Claude terminal session with enhanced features"""
    
    def __init__(self, session_id: str, task_id: int, working_dir: str, skip_permissions: bool = True):
        self.session_id = session_id
        self.task_id = task_id
        self.working_dir = working_dir
        self.skip_permissions = skip_permissions
        self.child: Optional[pexpect.spawn] = None
        self.is_running = False
        self.message_queue = asyncio.Queue()
        self.read_thread = None
        self.stop_reading = threading.Event()
        self.websocket_clients: List[Any] = []
        self.session_start_time = datetime.now()
        self.message_history: List[ClaudeMessage] = []
        self.current_tool_use = None
        # Deduplication
        self.last_messages = []  # Keep last 5 messages for deduplication
        self.max_last_messages = 5
        self.metrics = {
            "messages_sent": 0,
            "messages_received": 0,
            "tools_executed": 0,
            "errors_count": 0,
            "session_duration": 0
        }
        # Log file for Claude terminal output
        self.log_file_path = os.path.join(working_dir, ".claudetask", f"claude-session-{session_id}.log")
        self.log_file = None
        
    async def start(self) -> bool:
        """Start the Claude process with enhanced initialization"""
        try:
            logger.info(f"Starting Claude session {self.session_id} for task #{self.task_id}")
            logger.info(f"Working directory: {self.working_dir}")
            
            # Check if working directory exists
            if not os.path.exists(self.working_dir):
                logger.error(f"Working directory does not exist: {self.working_dir}")
                await self._send_message(
                    MessageType.ERROR,
                    f"Working directory does not exist: {self.working_dir}"
                )
                return False
            
            # Start Claude with pexpect
            env = os.environ.copy()
            # Add any necessary environment variables
            env['TERM'] = 'xterm-256color'

            # Prepare Claude command arguments
            claude_args = ['--dangerously-skip-permissions'] if self.skip_permissions else []

            self.child = pexpect.spawn(
                'claude',
                claude_args,
                cwd=self.working_dir,
                encoding='utf-8',
                timeout=None,  # No timeout
                env=env,
                dimensions=(24, 80)  # Standard terminal size
            )

            logger.info(f"Started Claude with pexpect (skip_permissions={self.skip_permissions}), PID={self.child.pid}")

            # Logging disabled to reduce disk I/O
            # # Open log file for writing
            # try:
            #     os.makedirs(os.path.dirname(self.log_file_path), exist_ok=True)
            #     self.log_file = open(self.log_file_path, 'w', encoding='utf-8', buffering=1)  # Line buffered
            #     self.log_file.write(f"=== Claude Session {self.session_id} ===\n")
            #     self.log_file.write(f"Started at: {datetime.now().isoformat()}\n")
            #     self.log_file.write(f"Task ID: {self.task_id}\n")
            #     self.log_file.write(f"Working Dir: {self.working_dir}\n")
            #     self.log_file.write(f"PID: {self.child.pid}\n")
            #     self.log_file.write("=" * 50 + "\n\n")
            #     logger.info(f"Logging Claude output to: {self.log_file_path}")
            # except Exception as e:
            #     logger.error(f"Failed to open log file: {e}")
            #     self.log_file = None
            self.log_file = None  # Logging disabled

            self.is_running = True
            
            # Start the reader thread
            self.stop_reading.clear()
            self.read_thread = threading.Thread(
                target=self._read_output_thread,
                name=f"ClaudeReader-{self.session_id}"
            )
            self.read_thread.daemon = True
            self.read_thread.start()
            
            # Send initialization message
            await self._send_message(
                MessageType.SYSTEM,
                f"Claude session started for task #{self.task_id}",
                subtype=MessageSubtype.INIT,
                metadata={
                    "pid": self.child.pid,
                    "working_dir": self.working_dir,
                    "session_id": self.session_id
                }
            )
            
            # Wait for Claude to fully initialize (5 seconds for complete startup)
            await asyncio.sleep(5)
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to start Claude process: {e}", exc_info=True)
            await self._send_message(
                MessageType.ERROR,
                f"Failed to start Claude process: {str(e)}"
            )
            return False
    
    async def stop(self) -> bool:
        """Stop the Claude process gracefully"""
        try:
            if self.child and self.is_running:
                logger.info(f"Stopping Claude session {self.session_id}")
                self.is_running = False
                
                # Stop the reader thread
                self.stop_reading.set()
                if self.read_thread:
                    self.read_thread.join(timeout=2)
                
                # Close the pexpect child gracefully
                if self.child.isalive():
                    try:
                        # Try to exit gracefully first
                        self.child.sendcontrol('c')
                        await asyncio.sleep(0.5)
                        self.child.sendline('exit')
                        self.child.expect(pexpect.EOF, timeout=2)
                    except:
                        # Force close if graceful exit fails
                        self.child.close(force=True)
                
                self.child = None

                # Logging disabled
                # # Close log file
                # if self.log_file:
                #     try:
                #         self.log_file.write(f"\n{'=' * 50}\n")
                #         self.log_file.write(f"Session ended at: {datetime.now().isoformat()}\n")
                #         self.log_file.write(f"Duration: {(datetime.now() - self.session_start_time).total_seconds():.2f}s\n")
                #         self.log_file.close()
                #         self.log_file = None
                #         logger.info(f"Closed log file: {self.log_file_path}")
                #     except Exception as e:
                #         logger.error(f"Failed to close log file: {e}")

                # Calculate session duration
                duration = (datetime.now() - self.session_start_time).total_seconds()
                self.metrics["session_duration"] = duration

                await self._send_message(
                    MessageType.SYSTEM,
                    "Claude session stopped",
                    subtype=MessageSubtype.COMPLETE,
                    metadata=self.metrics
                )
            
            return True
            
        except Exception as e:
            logger.error(f"Error stopping Claude process: {e}")
            return False
    
    async def send_input(self, user_input: str) -> bool:
        """Send input to Claude process"""
        try:
            if not self.child or not self.child.isalive():
                logger.error("Claude process is not running")
                await self._send_message(
                    MessageType.ERROR,
                    "Claude process is not running"
                )
                return False
            
            logger.info(f"Sending input to Claude: {user_input[:100]}...")
            
            # Track user message
            await self._send_message(
                MessageType.USER,
                user_input,
                subtype=MessageSubtype.PROMPT
            )
            
            # Send to Claude
            self.child.sendline(user_input)
            self.metrics["messages_sent"] += 1
            
            return True
                
        except Exception as e:
            logger.error(f"Error sending input to Claude: {e}")
            await self._send_message(
                MessageType.ERROR,
                f"Failed to send input: {str(e)}"
            )
            return False
    
    async def send_key(self, key: str) -> bool:
        """Send special key to Claude process"""
        try:
            if not self.child or not self.child.isalive():
                return False
            
            logger.debug(f"Sending key '{key}' to Claude")
            
            # Map key names to control sequences
            key_map = {
                "up": "\x1b[A",
                "down": "\x1b[B",
                "left": "\x1b[D", 
                "right": "\x1b[C",
                "enter": "\r",
                "escape": "\x1b",
                "esc": "\x1b",
                "tab": "\t",
                "backspace": "\x7f",
                "delete": "\x1b[3~",
                "home": "\x1b[H",
                "end": "\x1b[F",
                "pageup": "\x1b[5~",
                "pagedown": "\x1b[6~"
            }
            
            if key in key_map:
                self.child.send(key_map[key])
            elif key.startswith("ctrl+") and len(key) == 6:
                # Handle Ctrl+key combinations
                ctrl_key = key[5].lower()
                if ctrl_key.isalpha():
                    # Ctrl+A = 1, Ctrl+B = 2, etc.
                    self.child.send(chr(ord(ctrl_key) - ord('a') + 1))
            elif key.isdigit():
                # Send number directly
                self.child.send(key)
            elif len(key) == 1:
                # Single character
                self.child.send(key)
            
            return True
                
        except Exception as e:
            logger.error(f"Error sending key to Claude: {e}")
            return False
    
    def _read_output_thread(self):
        """Enhanced output reader thread with better parsing"""
        logger.info(f"Started output reader thread for session {self.session_id}")
        
        # Create event loop for this thread
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            buffer = ""
            ansi_pattern = r'\x1b\[[0-9;]*[A-Za-z]|\x1b\].*?\x07|\x1b\[[0-9;]*m'
            
            while not self.stop_reading.is_set() and self.child and self.child.isalive():
                try:
                    # Read any available data
                    try:
                        data = self.child.read_nonblocking(size=4096, timeout=0.1)
                        if data:
                            buffer += data
                    except pexpect.TIMEOUT:
                        pass
                    except pexpect.EOF:
                        logger.info("Claude process ended (EOF)")
                        break
                    
                    # Process complete lines
                    if '\n' in buffer or '\r' in buffer:
                        import re
                        
                        # Split by newlines and carriage returns
                        lines = re.split(r'[\r\n]+', buffer)
                        # Keep incomplete line in buffer
                        buffer = lines[-1] if not buffer.endswith(('\n', '\r')) else ""
                        
                        # Process complete lines
                        for line in lines[:-1] if buffer else lines:
                            if not line:
                                continue
                            
                            # For xterm.js: preserve ANSI codes and formatting
                            # Only remove excessive whitespace
                            processed_line = line.rstrip()

                            # Logging disabled
                            # # Write raw output to log file
                            # if self.log_file:
                            #     try:
                            #         self.log_file.write(f"[{datetime.now().strftime('%H:%M:%S')}] {processed_line}\n")
                            #     except Exception as e:
                            #         logger.error(f"Failed to write to log file: {e}")

                            # Skip completely empty lines and thinking indicators
                            if processed_line and processed_line.strip() not in ['(Thinking...)', '...', '']:
                                # Check for duplicates using clean version for comparison
                                clean_for_comparison = re.sub(ansi_pattern, '', processed_line).strip()
                                
                                if clean_for_comparison not in self.last_messages:
                                    # Add to deduplication list
                                    self.last_messages.append(clean_for_comparison)
                                    if len(self.last_messages) > self.max_last_messages:
                                        self.last_messages.pop(0)
                                    
                                    # Detect message type based on clean content
                                    message_type = self._detect_message_type(clean_for_comparison)
                                    
                                    # Send the original line with ANSI codes preserved
                                    loop.run_until_complete(
                                        self._send_message(
                                            message_type,
                                            processed_line,
                                            subtype=MessageSubtype.RESPONSE
                                        )
                                    )
                                    
                                    self.metrics["messages_received"] += 1
                                    logger.debug(f"Claude output: {clean_for_comparison[:100]}...")
                                else:
                                    logger.debug(f"Skipped duplicate message: {clean_for_comparison[:50]}...")
                    
                except Exception as e:
                    logger.error(f"Error in read thread: {e}")
                    continue
                
        except Exception as e:
            logger.error(f"Fatal error in output reader thread: {e}")
        finally:
            logger.info(f"Output reader thread exiting for session {self.session_id}")
            loop.close()
    
    def _detect_message_type(self, content: str) -> MessageType:
        """Detect the type of message based on content"""
        content_lower = content.lower()
        
        # Tool use detection
        if any(x in content_lower for x in ["executing", "running", "creating", "writing"]):
            self.metrics["tools_executed"] += 1
            return MessageType.TOOL
        
        # Error detection
        if any(x in content_lower for x in ["error", "failed", "exception", "traceback"]):
            self.metrics["errors_count"] += 1
            return MessageType.ERROR
        
        # System messages
        if content.startswith("[") or content.startswith("System:"):
            return MessageType.SYSTEM
        
        # Default to Claude response
        return MessageType.CLAUDE
    
    async def _send_message(
        self,
        msg_type: MessageType,
        content: str,
        subtype: Optional[MessageSubtype] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """Send a structured message to the queue and WebSocket clients"""
        message = ClaudeMessage(
            type=msg_type.value,
            content=content,
            timestamp=datetime.now().isoformat(),
            subtype=subtype.value if subtype else None,
            session_id=self.session_id,
            metadata=metadata
        )
        
        # Add to history
        self.message_history.append(message)
        
        # Put in queue for SSE streaming
        await self.message_queue.put(message)
        
        # Send to WebSocket clients if any
        if self.websocket_clients:
            message_json = message.to_json()
            disconnected_clients = []
            
            for client in self.websocket_clients:
                try:
                    await client.send_text(message_json)
                except:
                    disconnected_clients.append(client)
            
            # Remove disconnected clients
            for client in disconnected_clients:
                self.websocket_clients.remove(client)
    
    async def stream_messages(self):
        """Stream messages from the queue"""
        while self.is_running:
            try:
                message = await asyncio.wait_for(self.message_queue.get(), timeout=1.0)
                yield message
            except asyncio.TimeoutError:
                continue
    
    def add_websocket_client(self, websocket):
        """Add a WebSocket client for real-time streaming"""
        if websocket not in self.websocket_clients:
            self.websocket_clients.append(websocket)
            logger.info(f"Added WebSocket client to session {self.session_id}")
    
    def remove_websocket_client(self, websocket):
        """Remove a WebSocket client"""
        if websocket in self.websocket_clients:
            self.websocket_clients.remove(websocket)
            logger.info(f"Removed WebSocket client from session {self.session_id}")
    
    def get_session_info(self) -> Dict[str, Any]:
        """Get current session information"""
        return {
            "session_id": self.session_id,
            "task_id": self.task_id,
            "working_dir": self.working_dir,
            "is_running": self.is_running,
            "pid": self.child.pid if self.child else None,
            "start_time": self.session_start_time.isoformat(),
            "metrics": self.metrics,
            "message_count": len(self.message_history)
        }
    
    def get_message_history(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get message history"""
        history = [asdict(msg) for msg in self.message_history]
        if limit:
            return history[-limit:]
        return history


class ClaudeTerminalService:
    """Service for managing multiple Claude terminal sessions"""
    
    def __init__(self):
        self.sessions: Dict[str, ClaudeTerminalSession] = {}
        self.active_sessions_limit = 5  # Limit concurrent sessions
        
    async def create_session(
        self,
        task_id: int,
        project_path: str,
        session_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create a new Claude terminal session"""
        try:
            # Check active sessions limit
            active_count = sum(1 for s in self.sessions.values() if s.is_running)
            if active_count >= self.active_sessions_limit:
                return {
                    "success": False,
                    "error": f"Maximum {self.active_sessions_limit} concurrent sessions allowed"
                }
            
            # Generate session ID if not provided
            if not session_id:
                session_id = f"claude-task-{task_id}-{uuid.uuid4().hex[:8]}"
            
            # Create new session
            session = ClaudeTerminalSession(
                session_id=session_id,
                task_id=task_id,
                working_dir=project_path,
                skip_permissions=True  # Use dangerous mode for task sessions (directory already trusted)
            )
            
            # Start the session
            if await session.start():
                self.sessions[session_id] = session
                return {
                    "success": True,
                    "session_id": session_id,
                    "info": session.get_session_info()
                }
            else:
                return {
                    "success": False,
                    "error": "Failed to start Claude session"
                }
                
        except Exception as e:
            logger.error(f"Failed to create session: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e)
            }
    
    async def stop_session(self, session_id: str) -> bool:
        """Stop a Claude session"""
        if session_id in self.sessions:
            session = self.sessions[session_id]
            result = await session.stop()
            # Keep session in memory for history access
            return result
        return False
    
    async def remove_session(self, session_id: str) -> bool:
        """Remove a session from memory"""
        if session_id in self.sessions:
            session = self.sessions[session_id]
            if session.is_running:
                await session.stop()
            del self.sessions[session_id]
            return True
        return False
    
    async def send_input(self, session_id: str, user_input: str) -> bool:
        """Send input to a Claude session"""
        if session_id in self.sessions:
            return await self.sessions[session_id].send_input(user_input)
        return False
    
    async def send_key(self, session_id: str, key: str) -> bool:
        """Send special key to a Claude session"""
        if session_id in self.sessions:
            return await self.sessions[session_id].send_key(key)
        return False
    
    def get_session(self, session_id: str) -> Optional[ClaudeTerminalSession]:
        """Get a Claude session by ID"""
        return self.sessions.get(session_id)
    
    def get_all_sessions(self) -> List[Dict[str, Any]]:
        """Get information about all sessions"""
        return [session.get_session_info() for session in self.sessions.values()]
    
    def get_active_sessions(self) -> List[Dict[str, Any]]:
        """Get information about active sessions"""
        return [
            session.get_session_info()
            for session in self.sessions.values()
            if session.is_running
        ]
    
    async def stop_all_sessions(self):
        """Stop all active sessions"""
        for session_id in list(self.sessions.keys()):
            await self.stop_session(session_id)
    
    def add_websocket_to_session(self, session_id: str, websocket) -> bool:
        """Add WebSocket client to a session for real-time streaming"""
        if session_id in self.sessions:
            self.sessions[session_id].add_websocket_client(websocket)
            return True
        return False
    
    def remove_websocket_from_session(self, session_id: str, websocket) -> bool:
        """Remove WebSocket client from a session"""
        if session_id in self.sessions:
            self.sessions[session_id].remove_websocket_client(websocket)
            return True
        return False


# Global service instance
claude_terminal_service = ClaudeTerminalService()