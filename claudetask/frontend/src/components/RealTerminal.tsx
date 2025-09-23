import React, { useEffect, useRef, useState } from 'react';
import { Terminal } from '@xterm/xterm';
import { FitAddon } from '@xterm/addon-fit';
import { Box, IconButton, Paper } from '@mui/material';
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

      terminal.current.writeln('Terminal ready. Click start to begin.');
    } catch (error) {
      console.error('Failed to initialize terminal:', error);
    }

    return () => {
      try {
        terminal.current?.dispose();
      } catch (error) {
        console.warn('Error disposing terminal:', error);
      }
    };
  }, []);

  const startSession = async () => {
    try {
      terminal.current?.clear();
      terminal.current?.writeln('Starting session...');

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

  const connectWebSocket = (sessionId: string) => {
    const ws = new WebSocket(`ws://localhost:3333/api/sessions/embedded/${sessionId}/ws`);
    wsRef.current = ws;

    ws.onopen = () => {
      terminal.current?.writeln('Connected to Claude');
      ws.send(JSON.stringify({ type: 'ping' }));
    };

    ws.onmessage = (event) => {
      try {
        const message = JSON.parse(event.data);
        if (message.type !== 'pong' && message.content) {
          // Write everything directly to terminal
          terminal.current?.write(message.content);
        }
      } catch (error) {
        // If not JSON, write as plain text
        terminal.current?.write(event.data);
      }
    };

    ws.onerror = (error) => {
      terminal.current?.writeln('\r\nWebSocket error');
      console.error('WebSocket error:', error);
    };

    ws.onclose = () => {
      terminal.current?.writeln('\r\nConnection closed');
      setIsActive(false);
    };
  };

  const stopSession = async () => {
    if (wsRef.current) {
      wsRef.current.close();
    }
    if (sessionId) {
      try {
        await fetch(`http://localhost:3333/api/sessions/embedded/${sessionId}/stop`, {
          method: 'POST',
        });
      } catch (error) {
        console.error('Stop error:', error);
      }
    }
    setIsActive(false);
    setSessionId(null);
    terminal.current?.writeln('Session stopped');
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
          Claude Terminal - Task {taskId}
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