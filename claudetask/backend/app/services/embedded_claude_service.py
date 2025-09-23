"""Service for managing embedded Claude Code processes"""

import asyncio
import json
import logging
import os
import pty
import select
import subprocess
import sys
import termios
import tty
from typing import Dict, Optional, Any, AsyncGenerator
from pathlib import Path
import signal
from datetime import datetime
import pexpect
import threading

logger = logging.getLogger(__name__)


class EmbeddedClaudeProcess:
    """Manages a single embedded Claude Code process with pexpect"""
    
    def __init__(self, session_id: str, task_id: int, working_dir: str, context_file: str):
        self.session_id = session_id
        self.task_id = task_id
        self.working_dir = working_dir
        self.context_file = context_file
        self.child: Optional[pexpect.spawn] = None
        self.is_running = False
        self.message_queue = asyncio.Queue()
        self.read_thread = None
        self.stop_reading = threading.Event()
        
    async def start(self) -> bool:
        """Start the Claude process with pexpect"""
        try:
            logger.info(f"Starting Claude process for session {self.session_id}")
            logger.info(f"Working directory: {self.working_dir}")
            
            # Start Claude with pexpect
            self.child = pexpect.spawn('claude', cwd=self.working_dir, encoding='utf-8', timeout=10)
            logger.info(f"Started Claude with pexpect, PID={self.child.pid}")
            
            self.is_running = True
            
            # Start the reader thread
            self.stop_reading.clear()
            self.read_thread = threading.Thread(target=self._read_output_thread)
            self.read_thread.daemon = True
            self.read_thread.start()
            
            # Send initial greeting
            await self.message_queue.put({
                "type": "system",
                "content": f"Claude started for task #{self.task_id}",
                "timestamp": datetime.now().isoformat()
            })
            
            await self.message_queue.put({
                "type": "system",
                "content": f"Working directory: {self.working_dir}",
                "timestamp": datetime.now().isoformat()
            })
            
            # Wait for Claude to initialize
            await asyncio.sleep(2)
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to start Claude process: {e}")
            await self.message_queue.put({
                "type": "error",
                "content": f"Failed to start Claude process: {str(e)}",
                "timestamp": datetime.now().isoformat()
            })
            return False
    
    async def stop(self) -> bool:
        """Stop the Claude process"""
        try:
            if self.child and self.is_running:
                self.is_running = False
                
                # Stop the reader thread first with a short timeout
                self.stop_reading.set()
                if self.read_thread and self.read_thread.is_alive():
                    self.read_thread.join(timeout=1)  # Reduced timeout
                    
                    # If thread is still alive, that's ok - we're shutting down anyway
                    if self.read_thread.is_alive():
                        logger.warning(f"Reader thread for session {self.session_id} did not stop in time")
                
                # Try to terminate the child process gracefully first
                if self.child and self.child.isalive():
                    try:
                        # Send quit command to Claude
                        self.child.sendcontrol('c')  # Send Ctrl+C
                        self.child.send('/quit\n')  # Try to quit gracefully
                        # Give it a moment to quit
                        await asyncio.sleep(0.5)
                    except:
                        pass  # Ignore errors here, we'll force close anyway
                    
                    # Now force close if still alive
                    if self.child.isalive():
                        self.child.close(force=True)
                
                self.child = None
                
                # Try to put final message, but don't block on it
                try:
                    await asyncio.wait_for(
                        self.message_queue.put({
                            "type": "system",
                            "content": "Claude process stopped",
                            "timestamp": datetime.now().isoformat()
                        }),
                        timeout=0.5
                    )
                except asyncio.TimeoutError:
                    logger.warning(f"Could not send stop message for session {self.session_id}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error stopping Claude process: {e}")
            # Even on error, mark as stopped and cleanup
            self.is_running = False
            self.child = None
            return True  # Return True anyway to prevent hanging
    
    async def send_input(self, user_input: str) -> bool:
        """Send input to Claude process via pexpect"""
        try:
            logger.info(f"Attempting to send input to session {self.session_id}: {user_input[:50]}...")
            
            # Check if process is still alive
            if not self.child or not self.child.isalive():
                logger.error("Claude process is not running")
                await self.message_queue.put({
                    "type": "error",
                    "content": "Claude process is not running",
                    "timestamp": datetime.now().isoformat()
                })
                return False
            
            logger.info(f"Process is still running (PID: {self.child.pid})")
            
            # Echo user input to message queue
            await self.message_queue.put({
                "type": "user",
                "content": user_input,
                "timestamp": datetime.now().isoformat()
            })
            
            # Send to Claude - first send the text, then send Enter
            # Use send() for text and sendcontrol() for Enter
            self.child.send(user_input)
            self.child.sendcontrol('m')  # Send Ctrl+M (carriage return/Enter)
            logger.info(f"Successfully sent input to Claude via pexpect")
            
            return True
                
        except Exception as e:
            logger.error(f"Error sending input to Claude: {e}")
            await self.message_queue.put({
                "type": "error",
                "content": f"Failed to send input: {str(e)}",
                "timestamp": datetime.now().isoformat()
            })
            return False
    
    async def send_key(self, key: str) -> bool:
        """Send special key to Claude process"""
        try:
            logger.info(f"Attempting to send key '{key}' to session {self.session_id}")
            
            # Check if process is still alive
            if not self.child or not self.child.isalive():
                logger.error("Claude process is not running")
                return False
            
            # Map key names to pexpect commands
            if key == "up":
                self.child.send('\x1b[A')  # ESC[A - up arrow
            elif key == "down":
                self.child.send('\x1b[B')  # ESC[B - down arrow
            elif key == "left":
                self.child.send('\x1b[D')  # ESC[D - left arrow
            elif key == "right":
                self.child.send('\x1b[C')  # ESC[C - right arrow
            elif key == "enter":
                self.child.sendcontrol('m')  # Ctrl+M - Enter
            elif key == "escape" or key == "esc":
                self.child.send('\x1b')  # ESC
            elif key == "tab":
                self.child.send('\t')  # Tab
            elif key == "backspace":
                self.child.send('\x7f')  # Backspace
            elif key.startswith("ctrl+"):
                # Handle Ctrl+key combinations
                ctrl_key = key[5:]  # Remove 'ctrl+' prefix
                if len(ctrl_key) == 1:
                    self.child.sendcontrol(ctrl_key)
            elif len(key) == 1:
                # Single character - just send it
                self.child.send(key)
            else:
                # Try sending the number directly for menu selection
                self.child.send(key)
                
            logger.info(f"Successfully sent key '{key}' to Claude")
            return True
                
        except Exception as e:
            logger.error(f"Error sending key to Claude: {e}")
            return False
    
    def _read_output_thread(self):
        """Read output from Claude process via pexpect (runs in thread)"""
        logger.info(f"Started output reader thread for session {self.session_id}")
        
        # Create a new event loop for this thread
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            buffer = ""
            while not self.stop_reading.is_set() and self.child and self.child.isalive():
                try:
                    # Read any available output with timeout
                    index = self.child.expect([pexpect.TIMEOUT, pexpect.EOF], timeout=0.1)
                    
                    if index == 1:  # EOF
                        logger.info("Claude process ended (EOF)")
                        break
                    
                    # Get any available output
                    output = self.child.before
                    if output:
                        buffer += output
                        
                        # Split by lines and process
                        lines = buffer.split('\n')
                        # Keep the last incomplete line in buffer
                        buffer = lines[-1] if lines else ""
                        
                        # Process complete lines
                        for line in lines[:-1]:
                            if line:
                                # Basic ANSI cleanup but preserve content
                                import re
                                # Remove cursor movement and color codes
                                clean_line = re.sub(r'\x1b\[[0-9;]*[HJKmhl]', '', line)
                                # Remove other escape sequences
                                clean_line = re.sub(r'\x1b\[[0-9;?]*[A-Za-z]', '', clean_line)
                                # Remove OSC sequences
                                clean_line = re.sub(r'\x1b\].*?\x07', '', clean_line)
                                # Remove carriage returns at start
                                clean_line = re.sub(r'^\r+', '', clean_line)
                                clean_line = clean_line.strip()
                                
                                if clean_line:
                                    # Run the coroutine in this thread's loop
                                    loop.run_until_complete(
                                        self.message_queue.put({
                                            "type": "claude",
                                            "content": clean_line,
                                            "timestamp": datetime.now().isoformat()
                                        })
                                    )
                                    logger.debug(f"Sent Claude output: {clean_line[:100]}...")
                    
                except pexpect.TIMEOUT:
                    # Check if there's any data in buffer to read
                    try:
                        # Try reading any available data without blocking
                        data = self.child.read_nonblocking(size=1024, timeout=0)
                        if data:
                            buffer += data
                    except:
                        pass
                except pexpect.EOF:
                    logger.info("Claude process ended (EOF)")
                    break
                except Exception as e:
                    logger.error(f"Error in read thread: {e}")
                    # Don't break on errors, try to continue
                    continue
                
        except Exception as e:
            logger.error(f"Fatal error in output reader thread: {e}")
        finally:
            logger.info("Output reader thread exiting")
            loop.close()
    
    async def stream_messages(self) -> AsyncGenerator[Dict[str, Any], None]:
        """Stream messages from the process"""
        while self.is_running:
            try:
                message = await asyncio.wait_for(self.message_queue.get(), timeout=1.0)
                yield message
            except asyncio.TimeoutError:
                continue


class EmbeddedClaudeService:
    """Service for managing embedded Claude processes"""
    
    def __init__(self):
        self.sessions: Dict[str, EmbeddedClaudeProcess] = {}
        
    async def launch_session(
        self,
        session_id: str,
        task_id: int,
        project_path: str,
        context_file: str = ""
    ) -> bool:
        """Launch a new embedded Claude session"""
        try:
            # Create new process
            process = EmbeddedClaudeProcess(
                session_id=session_id,
                task_id=task_id,
                working_dir=project_path,
                context_file=context_file
            )
            
            # Start the process
            if await process.start():
                self.sessions[session_id] = process
                return True
            else:
                return False
                
        except Exception as e:
            logger.error(f"Failed to launch embedded session: {e}")
            return False
    
    async def stop_session(self, session_id: str) -> bool:
        """Stop an embedded Claude session"""
        if session_id in self.sessions:
            process = self.sessions[session_id]
            try:
                # Use asyncio timeout to prevent hanging
                result = await asyncio.wait_for(process.stop(), timeout=3.0)
            except asyncio.TimeoutError:
                logger.error(f"Timeout stopping session {session_id}, forcing cleanup")
                result = True  # Consider it stopped
            except Exception as e:
                logger.error(f"Error stopping session {session_id}: {e}")
                result = True  # Consider it stopped anyway
            
            # Always remove from sessions dict
            if session_id in self.sessions:
                del self.sessions[session_id]
            
            return result
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
    
    async def stream_output(self, session_id: str) -> AsyncGenerator[Dict[str, Any], None]:
        """Stream output from a Claude session"""
        if session_id in self.sessions:
            async for message in self.sessions[session_id].stream_messages():
                yield message
    
    def get_session(self, session_id: str) -> Optional[EmbeddedClaudeProcess]:
        """Get a Claude session by ID"""
        return self.sessions.get(session_id)
    
    async def stop_all_sessions(self):
        """Stop all active sessions"""
        for session_id in list(self.sessions.keys()):
            await self.stop_session(session_id)


# Global service instance
embedded_claude_service = EmbeddedClaudeService()