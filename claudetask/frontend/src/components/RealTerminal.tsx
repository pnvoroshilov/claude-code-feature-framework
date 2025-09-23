import React, { useEffect, useRef, useState, useCallback } from 'react';
import { Terminal } from '@xterm/xterm';
import { FitAddon } from '@xterm/addon-fit';
import { Box, IconButton, Paper, CircularProgress } from '@mui/material';
import { PlayArrow, Stop, Clear } from '@mui/icons-material';
import { styled } from '@mui/material/styles';
import '@xterm/xterm/css/xterm.css';

const TerminalContainer = styled(Paper)(({ theme }) => ({
  height: '600px',
  display: 'flex',
  flexDirection: 'column',
  backgroundColor: '#000',
  borderRadius: '8px',
  overflow: 'hidden',
}));

const TerminalHeader = styled(Box)(({ theme }) => ({
  height: '40px',
  backgroundColor: '#333',
  display: 'flex',
  justifyContent: 'space-between',
  alignItems: 'center',
  padding: '0 12px',
}));

interface RealTerminalProps {
  taskId: number;
}

const RealTerminal: React.FC<RealTerminalProps> = ({ taskId }) => {
  const terminalRef = useRef<HTMLDivElement>(null);
  const terminal = useRef<Terminal | null>(null);
  const fitAddon = useRef<FitAddon | null>(null);
  const wsRef = useRef<WebSocket | null>(null);
  const [isActive, setIsActive] = useState(false);
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [isConnecting, setIsConnecting] = useState(false);
  const sessionCheckDoneRef = useRef(false);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const userStoppedRef = useRef(false);

  useEffect(() => {
    if (!terminalRef.current) return;

    try {
      // Create terminal with minimal config for maximum compatibility
      terminal.current = new Terminal({
        theme: {
          background: '#000000',
          foreground: '#ffffff',
          cursor: '#ffffff',
        },
        fontFamily: 'monospace',
        fontSize: 14,
        cursorBlink: true,
        convertEol: true,
        scrollback: 1000,
      });

      // Add fit addon
      fitAddon.current = new FitAddon();
      terminal.current.loadAddon(fitAddon.current);

      // Open terminal
      terminal.current.open(terminalRef.current);
      
      // Wait for terminal to be fully initialized before fitting
      setTimeout(() => {
        if (fitAddon.current && terminal.current) {
          try {
            fitAddon.current.fit();
          } catch (e) {
            console.warn('Failed to fit terminal:', e);
          }
        }
      }, 100);

      // Handle all input
      terminal.current.onData((data) => {
        console.log('Terminal input:', data, 'charCode:', data.charCodeAt(0));
        if (wsRef.current?.readyState === WebSocket.OPEN) {
          wsRef.current.send(JSON.stringify({
            type: 'input',
            content: data
          }));
        }
      });

      terminal.current.writeln('Terminal ready. Checking for active session...');
      
      // Auto-check for active session and launch if needed
      checkActiveSession();
    } catch (error) {
      console.error('Failed to initialize terminal:', error);
    }

    return () => {
      try {
        if (reconnectTimeoutRef.current) {
          clearTimeout(reconnectTimeoutRef.current);
        }
        // Don't close WebSocket on unmount to keep session alive
        // wsRef.current?.close();
        terminal.current?.dispose();
      } catch (error) {
        console.warn('Error disposing terminal:', error);
      }
    };
  }, []);

  const checkActiveSession = useCallback(async () => {
    if (sessionCheckDoneRef.current) return;
    sessionCheckDoneRef.current = true;
    
    try {
      console.log(`Checking for active Claude sessions for task ${taskId}...`);
      terminal.current?.writeln('\r\nChecking for active session...');
      
      // Get all active sessions
      const response = await fetch('http://localhost:3333/api/sessions/embedded/active');
      
      if (response.ok) {
        const sessions = await response.json();
        console.log('Active sessions:', sessions);
        
        // Find session for this task
        const existingSession = sessions.find((s: any) => s.task_id === taskId);
        
        if (existingSession) {
          console.log(`Found existing session ${existingSession.session_id} for task ${taskId}`);
          terminal.current?.writeln(`\r\nReconnecting to session ${existingSession.session_id}...`);
          setSessionId(existingSession.session_id);
          setIsActive(true);
          connectWebSocket(existingSession.session_id, true);
        } else {
          console.log(`No active session found for task ${taskId}, auto-launching...`);
          terminal.current?.writeln('\r\nNo active session found. Starting new session...');
          terminal.current?.writeln(`Will auto-run: /start-feature ${taskId}`);
          // Auto-launch new session
          await startSession();
        }
      } else {
        console.log('Failed to check active sessions, auto-launching new session');
        // If check fails, try to start a new session
        await startSession();
      }
    } catch (error) {
      console.error('Error checking active session:', error);
      terminal.current?.writeln('\r\nError checking session. Starting new session...');
      // On error, try to start a new session
      await startSession();
    }
  }, [taskId]);

  const startSession = async () => {
    try {
      terminal.current?.clear();
      terminal.current?.writeln(`Starting Claude session for Task #${taskId}...`);
      terminal.current?.writeln(`Will auto-run: /start-feature ${taskId}`);

      const response = await fetch('http://localhost:3333/api/sessions/launch/embedded', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ task_id: taskId, context_file: '' }),
      });

      const data = await response.json();
      
      if (data.success) {
        setSessionId(data.session_id);
        setIsActive(true);
        terminal.current?.writeln(`Session started: ${data.session_id}`);
        connectWebSocket(data.session_id);
      } else {
        terminal.current?.writeln(`Error: ${data.error}`);
      }
    } catch (error) {
      terminal.current?.writeln(`Error: ${error}`);
    }
  };

  const connectWebSocket = (sessionId: string, isReconnect: boolean = false) => {
    // Close existing connection if any
    if (wsRef.current) {
      wsRef.current.close();
    }
    
    setIsConnecting(true);
    const ws = new WebSocket(`ws://localhost:3333/api/sessions/embedded/${sessionId}/ws`);
    wsRef.current = ws;

    ws.onopen = () => {
      setIsConnecting(false);
      terminal.current?.writeln('\r\nConnected to Claude');
      
      // Send initial ping
      ws.send(JSON.stringify({ type: 'ping' }));
      
      // If reconnecting, request history
      if (isReconnect) {
        console.log('Requesting session history on reconnect');
        ws.send(JSON.stringify({ type: 'get_history' }));
      }
    };

    ws.onmessage = (event) => {
      try {
        const message = JSON.parse(event.data);
        
        // Handle history replay
        if (message.type === 'history') {
          console.log(`Replaying ${message.content?.length || 0} history messages`);
          terminal.current?.clear();
          terminal.current?.writeln('=== Session History ===');
          
          // Replay all history messages
          if (Array.isArray(message.content)) {
            message.content.forEach((historyMsg: any) => {
              if (historyMsg.content) {
                terminal.current?.write(historyMsg.content);
              }
            });
          }
          terminal.current?.writeln('\r\n=== Live Session ===');
        } else if (message.type === 'output' && message.content) {
          // Write regular output
          terminal.current?.write(message.content);
        } else if (message.type !== 'pong' && message.content) {
          // Write any other content
          terminal.current?.write(message.content);
        }
      } catch (error) {
        // If not JSON, write as plain text
        terminal.current?.write(event.data);
      }
    };

    ws.onerror = (error) => {
      setIsConnecting(false);
      terminal.current?.writeln('\r\nWebSocket error');
      console.error('WebSocket error:', error);
    };

    ws.onclose = () => {
      setIsConnecting(false);
      
      // Check if user explicitly stopped the session
      if (userStoppedRef.current) {
        terminal.current?.writeln('\r\nSession stopped.');
        setIsActive(false);
        userStoppedRef.current = false;
      } else {
        terminal.current?.writeln('\r\nConnection closed. Session remains active.');
        // Try to reconnect after a delay only if not user-stopped
        if (isActive && sessionId) {
          reconnectTimeoutRef.current = setTimeout(() => {
            console.log('Attempting to reconnect...');
            connectWebSocket(sessionId, true);
          }, 3000);
        }
      }
    };
  };

  const stopSession = async () => {
    console.log(`Stopping session ${sessionId}`);
    
    // Mark as user-stopped to prevent reconnection
    userStoppedRef.current = true;
    
    // Clear reconnect timeout
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
      reconnectTimeoutRef.current = null;
    }
    
    // Close WebSocket first
    if (wsRef.current) {
      wsRef.current.close();
      wsRef.current = null;
    }
    
    // Then stop the backend session
    if (sessionId) {
      try {
        terminal.current?.writeln('\r\nStopping session...');
        const response = await fetch(`http://localhost:3333/api/sessions/embedded/${sessionId}/stop`, {
          method: 'POST',
        });
        const result = await response.json();
        console.log('Stop session result:', result);
      } catch (error) {
        console.error('Stop error:', error);
        terminal.current?.writeln('\r\nError stopping session');
      }
    }
    
    setIsActive(false);
    setSessionId(null);
    sessionCheckDoneRef.current = false; // Allow checking for session again
  };

  const clearTerminal = () => {
    try {
      terminal.current?.clear();
    } catch (error) {
      console.warn('Error clearing terminal:', error);
    }
  };

  return (
    <TerminalContainer>
      <TerminalHeader>
        <Box sx={{ color: '#fff', fontSize: '14px' }}>
          Claude Terminal - Task {taskId} {sessionId && `(${sessionId.slice(0, 8)}...)`}
          {isConnecting && <CircularProgress size={16} sx={{ ml: 1, color: '#fff' }} />}
        </Box>
        <Box sx={{ display: 'flex', gap: 1 }}>
          <IconButton size="small" onClick={clearTerminal} sx={{ color: '#fff' }}>
            <Clear />
          </IconButton>
          {isActive ? (
            <IconButton size="small" onClick={stopSession} sx={{ color: '#f44336' }}>
              <Stop />
            </IconButton>
          ) : (
            <IconButton size="small" onClick={startSession} sx={{ color: '#4caf50' }}>
              <PlayArrow />
            </IconButton>
          )}
        </Box>
      </TerminalHeader>
      <Box sx={{ flex: 1 }} ref={terminalRef} />
    </TerminalContainer>
  );
};

export default RealTerminal;