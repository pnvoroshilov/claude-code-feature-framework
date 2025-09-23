import React, { useEffect, useRef, useState } from 'react';
import { Terminal } from '@xterm/xterm';
import { FitAddon } from '@xterm/addon-fit';
import { WebLinksAddon } from '@xterm/addon-web-links';
import { WebglAddon } from '@xterm/addon-webgl';
import { Box, IconButton, Tooltip, Paper, Typography } from '@mui/material';
import { PlayArrow, Stop, Clear, Fullscreen, FullscreenExit } from '@mui/icons-material';
import { styled } from '@mui/material/styles';
import '@xterm/xterm/css/xterm.css';

const TerminalContainer = styled(Paper)(({ theme }) => ({
  height: '100%',
  minHeight: '600px',
  display: 'flex',
  flexDirection: 'column',
  backgroundColor: '#1e1e1e',
  border: '1px solid #333',
  borderRadius: '8px',
  overflow: 'hidden',
  fontFamily: '"JetBrains Mono", "SF Mono", Monaco, "Cascadia Code", monospace',
}));

const TerminalHeader = styled(Box)(({ theme }) => ({
  padding: '8px 12px',
  backgroundColor: '#2d2d2d',
  borderBottom: '1px solid #333',
  display: 'flex',
  justifyContent: 'space-between',
  alignItems: 'center',
  minHeight: '48px',
}));

const TerminalContent = styled(Box)(({ theme }) => ({
  flex: 1,
  position: 'relative',
  backgroundColor: '#1e1e1e',
  '& .xterm': {
    height: '100%',
    width: '100%',
  },
  '& .xterm-viewport': {
    backgroundColor: '#1e1e1e !important',
  },
  '& .xterm-screen': {
    backgroundColor: '#1e1e1e !important',
  },
}));

interface XTerminalEmulatorProps {
  taskId: number;
}

const XTerminalEmulator: React.FC<XTerminalEmulatorProps> = ({ taskId }) => {
  const terminalRef = useRef<HTMLDivElement>(null);
  const terminal = useRef<Terminal | null>(null);
  const fitAddon = useRef<FitAddon | null>(null);
  const [isActive, setIsActive] = useState(false);
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [isFullscreen, setIsFullscreen] = useState(false);
  const wsRef = useRef<WebSocket | null>(null);
  const eventSourceRef = useRef<EventSource | null>(null);

  // Initialize terminal
  useEffect(() => {
    if (!terminalRef.current) return;

    // Create terminal instance
    terminal.current = new Terminal({
      theme: {
        background: '#1e1e1e',
        foreground: '#ffffff',
        cursor: '#ffffff',
        cursorAccent: '#000000',
        selectionBackground: 'rgba(255, 255, 255, 0.3)',
        black: '#1e1e1e',
        red: '#f87171',
        green: '#4ade80',
        yellow: '#facc15',
        blue: '#60a5fa',
        magenta: '#c084fc',
        cyan: '#22d3ee',
        white: '#f3f4f6',
        brightBlack: '#374151',
        brightRed: '#fca5a5',
        brightGreen: '#86efac',
        brightYellow: '#fde047',
        brightBlue: '#93c5fd',
        brightMagenta: '#d8b4fe',
        brightCyan: '#67e8f9',
        brightWhite: '#ffffff',
      },
      fontFamily: '"JetBrains Mono", "SF Mono", Monaco, "Cascadia Code", monospace',
      fontSize: 13,
      lineHeight: 1.2,
      letterSpacing: 0,
      cursorBlink: true,
      cursorStyle: 'block',
      scrollback: 10000,
      tabStopWidth: 4,
      convertEol: true,
      allowTransparency: false,
      allowProposedApi: true,
    });

    // Create addons
    fitAddon.current = new FitAddon();
    const webLinksAddon = new WebLinksAddon();
    
    // Load addons
    terminal.current.loadAddon(fitAddon.current);
    terminal.current.loadAddon(webLinksAddon);
    
    // Try to load WebGL addon (fallback if not supported)
    try {
      const webglAddon = new WebglAddon();
      terminal.current.loadAddon(webglAddon);
    } catch (e) {
      console.warn('WebGL addon not supported, using canvas renderer');
    }

    // Open terminal
    terminal.current.open(terminalRef.current);
    
    // Initial fit
    setTimeout(() => {
      fitAddon.current?.fit();
    }, 100);

    // Handle data input
    terminal.current.onData((data) => {
      if (isActive && sessionId) {
        sendInput(data);
      }
    });

    // Welcome message
    terminal.current.writeln('\x1b[1;32m╭─ Claude Terminal Ready ─╮\x1b[0m');
    terminal.current.writeln('\x1b[32m│ Click play to start     │\x1b[0m');
    terminal.current.writeln('\x1b[1;32m╰─────────────────────────╯\x1b[0m');
    terminal.current.writeln('');

    // Cleanup
    return () => {
      terminal.current?.dispose();
    };
  }, []);

  // Handle resize
  useEffect(() => {
    const handleResize = () => {
      if (fitAddon.current) {
        fitAddon.current.fit();
      }
    };

    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  // Cleanup connections on unmount
  useEffect(() => {
    return () => {
      if (wsRef.current) {
        wsRef.current.close();
      }
      if (eventSourceRef.current) {
        eventSourceRef.current.close();
      }
    };
  }, []);

  const startSession = async () => {
    try {
      terminal.current?.clear();
      terminal.current?.writeln('\x1b[33mStarting Claude session...\x1b[0m');

      const response = await fetch('http://localhost:3333/api/sessions/launch/embedded', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          task_id: taskId,
          context_file: '',
        }),
      });

      const data = await response.json();
      
      if (data.success) {
        setSessionId(data.session_id);
        setIsActive(true);
        
        terminal.current?.writeln(`\x1b[32m✓ Session started: ${data.session_id}\x1b[0m`);
        terminal.current?.writeln('');
        
        // Connect to stream
        connectWebSocket(data.session_id);
      } else {
        terminal.current?.writeln(`\x1b[31m✗ Error: ${data.error || 'Failed to start session'}\x1b[0m`);
      }
    } catch (error) {
      terminal.current?.writeln(`\x1b[31m✗ Error: ${error}\x1b[0m`);
    }
  };

  const connectWebSocket = (sessionId: string) => {
    const wsUrl = `ws://localhost:3333/api/sessions/embedded/${sessionId}/ws`;
    
    const ws = new WebSocket(wsUrl);
    wsRef.current = ws;

    ws.onopen = () => {
      terminal.current?.writeln('\x1b[36m🔗 Connected to Claude\x1b[0m');
      terminal.current?.writeln('');
      ws.send(JSON.stringify({ type: 'ping' }));
    };

    ws.onmessage = (event) => {
      try {
        const message = JSON.parse(event.data);
        
        if (message.type !== 'pong' && message.content) {
          // Write directly to terminal with ANSI support
          terminal.current?.write(message.content);
          
          // Add newline if not present
          if (!message.content.endsWith('\n') && !message.content.endsWith('\r')) {
            terminal.current?.writeln('');
          }
        }
      } catch (error) {
        console.error('Error parsing WebSocket message:', error);
      }
    };

    ws.onerror = (error) => {
      terminal.current?.writeln(`\x1b[31m✗ WebSocket error\x1b[0m`);
      console.error('WebSocket error:', error);
    };

    ws.onclose = () => {
      terminal.current?.writeln('\x1b[33m⚠ Connection closed\x1b[0m');
      wsRef.current = null;
    };
  };

  const stopSession = async () => {
    if (sessionId) {
      try {
        await fetch(`http://localhost:3333/api/sessions/embedded/${sessionId}/stop`, {
          method: 'POST',
        });
      } catch (error) {
        console.error('Error stopping session:', error);
      }
    }
    
    if (wsRef.current) {
      wsRef.current.close();
      wsRef.current = null;
    }
    
    setIsActive(false);
    setSessionId(null);
    terminal.current?.writeln('\x1b[33m⏹ Session stopped\x1b[0m');
  };

  const sendInput = async (data: string) => {
    if (!sessionId) return;

    // Send via WebSocket if available
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      // Handle special keys
      if (data === '\r') {
        wsRef.current.send(JSON.stringify({
          type: 'key',
          key: 'enter'
        }));
      } else if (data === '\u007f') { // Backspace
        wsRef.current.send(JSON.stringify({
          type: 'key',
          key: 'backspace'
        }));
      } else if (data === '\t') {
        wsRef.current.send(JSON.stringify({
          type: 'key',
          key: 'tab'
        }));
      } else if (data === '\u001b') { // Escape
        wsRef.current.send(JSON.stringify({
          type: 'key',
          key: 'escape'
        }));
      } else if (data.startsWith('\u001b[')) {
        // Arrow keys
        if (data === '\u001b[A') {
          wsRef.current.send(JSON.stringify({ type: 'key', key: 'up' }));
        } else if (data === '\u001b[B') {
          wsRef.current.send(JSON.stringify({ type: 'key', key: 'down' }));
        } else if (data === '\u001b[C') {
          wsRef.current.send(JSON.stringify({ type: 'key', key: 'right' }));
        } else if (data === '\u001b[D') {
          wsRef.current.send(JSON.stringify({ type: 'key', key: 'left' }));
        }
      } else {
        // Regular input
        wsRef.current.send(JSON.stringify({
          type: 'input',
          content: data
        }));
      }
    } else {
      // Fallback to HTTP
      try {
        await fetch(`http://localhost:3333/api/sessions/embedded/${sessionId}/input`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ input: data }),
        });
      } catch (error) {
        console.error('Error sending input:', error);
      }
    }
  };

  const clearTerminal = () => {
    terminal.current?.clear();
  };

  const toggleFullscreen = () => {
    setIsFullscreen(!isFullscreen);
    // Resize terminal after fullscreen toggle
    setTimeout(() => {
      fitAddon.current?.fit();
    }, 100);
  };

  return (
    <TerminalContainer 
      sx={{ 
        height: isFullscreen ? '100vh' : '100%',
        position: isFullscreen ? 'fixed' : 'relative',
        top: isFullscreen ? 0 : 'auto',
        left: isFullscreen ? 0 : 'auto',
        right: isFullscreen ? 0 : 'auto',
        bottom: isFullscreen ? 0 : 'auto',
        zIndex: isFullscreen ? 9999 : 'auto',
      }}
    >
      <TerminalHeader>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
          <Box sx={{ display: 'flex', gap: 0.5 }}>
            <Box sx={{ width: 12, height: 12, borderRadius: '50%', backgroundColor: '#f87171' }} />
            <Box sx={{ width: 12, height: 12, borderRadius: '50%', backgroundColor: '#facc15' }} />
            <Box sx={{ width: 12, height: 12, borderRadius: '50%', backgroundColor: '#4ade80' }} />
          </Box>
          <Typography sx={{ color: '#ffffff', fontSize: '13px', fontFamily: 'monospace' }}>
            claude@task-{taskId}:~
          </Typography>
          {isActive && (
            <Box sx={{ 
              width: '8px', 
              height: '8px', 
              backgroundColor: '#4ade80', 
              borderRadius: '50%',
              animation: 'pulse 2s infinite',
              '@keyframes pulse': {
                '0%': { opacity: 1 },
                '50%': { opacity: 0.5 },
                '100%': { opacity: 1 },
              }
            }} />
          )}
        </Box>
        
        <Box sx={{ display: 'flex', gap: 0.5 }}>
          <Tooltip title="Clear Terminal">
            <IconButton
              size="small"
              onClick={clearTerminal}
              sx={{ color: '#888', '&:hover': { color: '#fff' } }}
            >
              <Clear fontSize="small" />
            </IconButton>
          </Tooltip>
          
          <Tooltip title="Toggle Fullscreen">
            <IconButton
              size="small"
              onClick={toggleFullscreen}
              sx={{ color: '#888', '&:hover': { color: '#fff' } }}
            >
              {isFullscreen ? <FullscreenExit fontSize="small" /> : <Fullscreen fontSize="small" />}
            </IconButton>
          </Tooltip>
          
          {isActive ? (
            <Tooltip title="Stop Session">
              <IconButton
                size="small"
                onClick={stopSession}
                sx={{ color: '#f87171', '&:hover': { color: '#fca5a5' } }}
              >
                <Stop fontSize="small" />
              </IconButton>
            </Tooltip>
          ) : (
            <Tooltip title="Start Session">
              <IconButton
                size="small"
                onClick={startSession}
                sx={{ color: '#4ade80', '&:hover': { color: '#86efac' } }}
              >
                <PlayArrow fontSize="small" />
              </IconButton>
            </Tooltip>
          )}
        </Box>
      </TerminalHeader>

      <TerminalContent ref={terminalRef} />
    </TerminalContainer>
  );
};

export default XTerminalEmulator;