import React, { useEffect, useRef, useState } from 'react';
import {
  Box,
  Paper,
  Typography,
  IconButton,
  Chip,
  CircularProgress,
  TextField,
  Button,
  ButtonGroup,
  Stack,
} from '@mui/material';
import {
  Terminal as ClaudeIcon,
  PlayArrow as StartIcon,
  Stop as StopIcon,
  Clear as ClearIcon,
  Send as SendIcon,
  ArrowUpward,
  ArrowDownward,
  ArrowBack,
  ArrowForward,
  Keyboard,
} from '@mui/icons-material';

interface XTermTerminalProps {
  taskId: number;
  projectPath?: string;
  onSessionStop?: () => void;
}

const XTermTerminal: React.FC<XTermTerminalProps> = ({ 
  taskId, 
  projectPath,
  onSessionStop 
}) => {
  const eventSourceRef = useRef<EventSource | null>(null);
  const [isActive, setIsActive] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [sessionId, setSessionId] = useState<string | null>(null);
  const sessionIdRef = useRef<string | null>(null);
  const [logMessages, setLogMessages] = useState<string[]>([]);
  const logFileRef = useRef<string>(`/tmp/claude-task-${taskId}-${Date.now()}.log`);
  const [commandInput, setCommandInput] = useState<string>('');

  // Helper to append to log file
  const appendToLog = (message: string) => {
    const timestamp = new Date().toLocaleTimeString();
    const logEntry = `[${timestamp}] ${message}\n`;
    
    // Save to state for display (last 100 lines)
    setLogMessages(prev => {
      const updated = [...prev, logEntry].slice(-100);
      console.log(`Messages count: ${updated.length}`);
      return updated;
    });
    
    // Log to console for debugging
    console.log(`Task ${taskId} log:`, message);
  };

  // Update sessionIdRef when sessionId changes
  useEffect(() => {
    sessionIdRef.current = sessionId;
  }, [sessionId]);

  const startSession = async () => {
    try {
      setIsLoading(true);
      
      const response = await fetch(`http://localhost:3333/api/sessions/launch/embedded`, {
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
        console.log('Session started:', data.session_id);
        setSessionId(data.session_id);
        sessionIdRef.current = data.session_id; // Update ref immediately
        setIsActive(true);
        connectToStream(data.session_id);
        
        // Auto-send command to start working on the task
        appendToLog('Waiting for Claude to initialize...');
        setTimeout(async () => {
          // Send task start command with more context
          appendToLog(`Sending command to start working on task #${taskId}...`);
          
          // First, ask Claude to look at the current project
          const contextCommand = `You are in the CriptoEarnBot project. Task #${taskId} is about creating a simple UI. Please analyze the project structure and suggest what UI components are needed.`;
          
          await sendMcpCommand(data.session_id, contextCommand);
          appendToLog(`Command sent: ${contextCommand}`);
        }, 3000); // Wait 3 seconds for Claude to fully initialize
      } else {
        console.error('Failed to start session:', data);
      }
    } catch (error) {
      console.error('Error starting session:', error);
    } finally {
      setIsLoading(false);
    }
  };
  
  const sendMcpCommand = async (sessionId: string, command: string) => {
    try {
      await fetch(`http://localhost:3333/api/sessions/embedded/${sessionId}/input`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ input: command }),
      });
    } catch (error) {
      console.error('Error sending MCP command:', error);
    }
  };

  const connectToStream = (sessionId: string) => {
    if (eventSourceRef.current) {
      eventSourceRef.current.close();
    }

    appendToLog(`Starting stream connection for session: ${sessionId}`);
    console.log('Connecting to stream for session:', sessionId);

    eventSourceRef.current = new EventSource(
      `http://localhost:3333/api/sessions/embedded/${sessionId}/stream`
    );

    eventSourceRef.current.onmessage = (event) => {
      try {
        const message = JSON.parse(event.data);
        console.log('Received message from stream:', message);
        
        if (message.type === 'claude' && message.content) {
          // Direct Claude output - no hex decoding needed anymore
          appendToLog(`[Claude]: ${message.content}`);
        } else if (message.type === 'terminal' && message.content) {
          // Legacy terminal handling for backward compatibility
          try {
            const bytes = new Uint8Array(
              message.content.match(/.{1,2}/g).map((byte: string) => parseInt(byte, 16))
            );
            const rawText = new TextDecoder().decode(bytes);
            
            // Debug: log raw text
            console.log('Raw terminal text:', rawText);
            
            // Clean up ANSI escape sequences more thoroughly
            // eslint-disable-next-line no-control-regex
            let text = rawText
              .replace(/\x1b\[[0-9;?]*[A-Za-z]/g, '') // Remove all ANSI escape sequences
              .replace(/\x1b\[[0-9;]*m/g, '') // Remove color codes
              .replace(/\x1b\]/g, '') // Remove OSC sequences
              .replace(/[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]/g, '') // Remove other control chars except \t, \n, \r
              .replace(/\r\n/g, '\n') // Normalize line endings
              .replace(/\r/g, '\n') // Convert carriage returns to newlines
              .replace(/�/g, ''); // Remove replacement characters
            
            // Always append to see what we get, even spaces/newlines
            appendToLog(`[Claude]: ${text || '[empty]'}`);
          } catch (error) {
            console.error('Error decoding terminal output:', error);
            appendToLog(`[Error decoding]: ${error}`);
          }
        } else if (message.type === 'system' && message.content) {
          appendToLog(`[System]: ${message.content}`);
        } else if (message.type === 'user' && message.content) {
          appendToLog(`[User]: ${message.content}`);
        } else if (message.type === 'error' && message.content) {
          appendToLog(`[Error]: ${message.content}`);
        }
      } catch (error) {
        console.error('Error parsing message:', error);
      }
    };

    eventSourceRef.current.onerror = (error) => {
      console.error('EventSource error:', error);
      appendToLog(`[ERROR]: Stream connection error`);
    };
  };

  const stopSession = async () => {
    try {
      if (sessionId) {
        await fetch(`http://localhost:3333/api/sessions/embedded/${sessionId}/stop`, {
          method: 'POST',
        });
        
        if (eventSourceRef.current) {
          eventSourceRef.current.close();
          eventSourceRef.current = null;
        }
        
        setSessionId(null);
        setIsActive(false);
        
        appendToLog('[SESSION TERMINATED]');
        
        if (onSessionStop) {
          onSessionStop();
        }
      }
    } catch (error) {
      console.error('Error stopping session:', error);
    }
  };

  const clearLogs = () => {
    setLogMessages([]);
    appendToLog('[LOGS CLEARED]');
  };

  const handleSendCommand = async () => {
    if (!sessionId || !commandInput.trim()) return;
    
    await sendMcpCommand(sessionId, commandInput);
    appendToLog(`Manual command sent: ${commandInput}`);
    setCommandInput('');
  };

  const sendKey = async (key: string) => {
    if (!sessionId) return;
    
    try {
      const response = await fetch(
        `http://localhost:3333/api/sessions/embedded/${sessionId}/key`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ key }),
        }
      );
      
      if (!response.ok) {
        console.error('Failed to send key:', key);
      }
    } catch (error) {
      console.error('Error sending key:', error);
    }
  };

  return (
    <Paper 
      elevation={3} 
      sx={{ 
        height: '600px', 
        display: 'flex', 
        flexDirection: 'column',
        bgcolor: '#1e1e1e',
        border: '1px solid #333',
      }}
    >
      {/* Terminal Header */}
      <Box 
        sx={{ 
          p: 1.5, 
          bgcolor: '#333', 
          display: 'flex', 
          justifyContent: 'space-between',
          alignItems: 'center',
          borderBottom: '1px solid #555',
        }}
      >
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
          <ClaudeIcon sx={{ color: '#fff' }} />
          <Typography variant="h6" sx={{ color: '#fff', fontSize: '14px' }}>
            Claude Terminal - Task #{taskId}
          </Typography>
          
          <Chip 
            label={isActive ? 'Active' : 'Inactive'} 
            size="small" 
            color={isActive ? 'success' : 'default'}
            sx={{ fontSize: '10px' }}
          />
        </Box>
        
        <Box>
          <IconButton 
            size="small" 
            onClick={clearLogs}
            sx={{ color: '#fff', mr: 1 }}
            title="Clear Logs"
          >
            <ClearIcon fontSize="small" />
          </IconButton>
          {isActive ? (
            <IconButton 
              size="small" 
              onClick={stopSession}
              sx={{ color: '#f44336' }}
              title="Stop Claude Session"
            >
              <StopIcon fontSize="small" />
            </IconButton>
          ) : (
            <IconButton 
              size="small" 
              onClick={startSession}
              sx={{ color: '#4caf50' }}
              title="Start Claude Session"
              disabled={isLoading}
            >
              {isLoading ? <CircularProgress size={16} /> : <StartIcon fontSize="small" />}
            </IconButton>
          )}
        </Box>
      </Box>

      {/* Log Display */}
      <Box 
        sx={{ 
          flex: 1,
          p: 2,
          overflow: 'auto',
          bgcolor: '#1e1e1e',
        }}
      >
        <Typography variant="body2" sx={{ color: '#888', mb: 1 }}>
          Session: {sessionId || 'Not started'} | Messages: {logMessages.length}
        </Typography>
        <Box
          component="pre"
          sx={{
            fontFamily: 'monospace',
            fontSize: '12px',
            color: '#fff',
            whiteSpace: 'pre-wrap',
            wordBreak: 'break-all',
            minHeight: '100px',
            border: '1px solid #333',
            padding: '10px',
            mb: 2,
          }}
        >
          {logMessages.length > 0 ? logMessages.join('') : 'Waiting for messages...'}
        </Box>
        
        {/* Interactive Controls */}
        {isActive && (
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
            {/* Arrow Keys and Selection */}
            <Box sx={{ display: 'flex', gap: 2, alignItems: 'center' }}>
              <Typography variant="body2" sx={{ color: '#888' }}>
                Navigation:
              </Typography>
              <ButtonGroup variant="outlined" size="small">
                <Button onClick={() => sendKey('up')} title="Up Arrow">
                  <ArrowUpward fontSize="small" />
                </Button>
                <Button onClick={() => sendKey('down')} title="Down Arrow">
                  <ArrowDownward fontSize="small" />
                </Button>
                <Button onClick={() => sendKey('left')} title="Left Arrow">
                  <ArrowBack fontSize="small" />
                </Button>
                <Button onClick={() => sendKey('right')} title="Right Arrow">
                  <ArrowForward fontSize="small" />
                </Button>
              </ButtonGroup>
              
              <ButtonGroup variant="outlined" size="small">
                <Button onClick={() => sendKey('enter')} sx={{ minWidth: '80px' }}>
                  Enter
                </Button>
                <Button onClick={() => sendKey('escape')} sx={{ minWidth: '80px' }}>
                  ESC
                </Button>
                <Button onClick={() => sendKey('tab')} sx={{ minWidth: '80px' }}>
                  Tab
                </Button>
              </ButtonGroup>
            </Box>
            
            {/* Number Keys for Menu Selection */}
            <Box sx={{ display: 'flex', gap: 2, alignItems: 'center' }}>
              <Typography variant="body2" sx={{ color: '#888' }}>
                Quick Select:
              </Typography>
              <ButtonGroup variant="outlined" size="small">
                {[1, 2, 3, 4, 5].map(num => (
                  <Button 
                    key={num}
                    onClick={() => sendKey(String(num))}
                    sx={{ minWidth: '40px' }}
                  >
                    {num}
                  </Button>
                ))}
              </ButtonGroup>
            </Box>
            
            {/* Text Input */}
            <Box sx={{ display: 'flex', gap: 1 }}>
              <TextField
                size="small"
                fullWidth
                placeholder="Type command..."
                value={commandInput}
                onChange={(e) => setCommandInput(e.target.value)}
                onKeyPress={(e) => {
                  if (e.key === 'Enter') {
                    handleSendCommand();
                  }
                }}
                sx={{
                  '& .MuiInputBase-root': {
                    color: '#fff',
                    bgcolor: '#333',
                  },
                }}
              />
              <Button
                variant="contained"
                size="small"
                onClick={handleSendCommand}
                endIcon={<SendIcon />}
              >
                Send
              </Button>
            </Box>
          </Box>
        )}
      </Box>
    </Paper>
  );
};

export default XTermTerminal;