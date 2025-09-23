import React, { useEffect, useRef, useState, useCallback } from 'react';
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
  Tooltip,
  Divider,
  Alert,
  LinearProgress,
  Badge,
  Collapse,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
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
  Wifi,
  WifiOff,
  ExpandMore,
  ExpandLess,
  CheckCircle,
  Error as ErrorIcon,
  Warning,
  Info,
  Build,
  Person,
  SmartToy,
  History,
  ContentCopy,
  Download,
  Fullscreen,
  FullscreenExit,
  Settings,
} from '@mui/icons-material';
import { styled } from '@mui/material/styles';
import { Fade, Grow, Slide } from '@mui/material';

// Styled components for better visuals (opcode-style)
const StyledTerminalContainer = styled(Paper)(({ theme }) => ({
  height: '100%',
  minHeight: '600px',
  display: 'flex',
  flexDirection: 'column',
  backgroundColor: '#1a1a1a',
  border: '1px solid #333333',
  borderRadius: '12px',
  overflow: 'hidden',
  position: 'relative',
  boxShadow: '0 8px 32px rgba(0, 0, 0, 0.4)',
  backdropFilter: 'blur(10px)',
  fontFamily: '"JetBrains Mono", "SF Mono", Monaco, "Cascadia Code", "Roboto Mono", monospace',
}));

const StyledHeader = styled(Box)(({ theme }) => ({
  padding: '16px 20px',
  background: 'linear-gradient(135deg, #2a2a2a 0%, #1e1e1e 100%)',
  borderBottom: '1px solid #404040',
  display: 'flex',
  justifyContent: 'space-between',
  alignItems: 'center',
  backdropFilter: 'blur(8px)',
  borderTopLeftRadius: '12px',
  borderTopRightRadius: '12px',
}));

const StyledMessageContainer = styled(Box)(({ theme }) => ({
  flex: 1,
  overflow: 'auto',
  padding: '20px 24px',
  backgroundColor: '#1a1a1a',
  fontFamily: '"JetBrains Mono", "SF Mono", Monaco, "Cascadia Code", "Roboto Mono", monospace',
  fontSize: '14px',
  lineHeight: '1.7',
  color: '#e8e8e8',
  '&::-webkit-scrollbar': {
    width: '10px',
  },
  '&::-webkit-scrollbar-track': {
    background: 'rgba(0, 0, 0, 0.2)',
    borderRadius: '8px',
  },
  '&::-webkit-scrollbar-thumb': {
    background: 'linear-gradient(135deg, #4a4a4a 0%, #6a6a6a 100%)',
    borderRadius: '8px',
    border: '2px solid transparent',
    backgroundClip: 'content-box',
    '&:hover': {
      background: 'linear-gradient(135deg, #5a5a5a 0%, #7a7a7a 100%)',
      backgroundClip: 'content-box',
    },
  },
}));

const MessageLine = styled(Box)<{ messageType: string }>(({ theme, messageType }) => ({
  marginBottom: '12px',
  padding: '12px 16px',
  borderRadius: '8px',
  backgroundColor: 
    messageType === 'error' ? 'rgba(239, 68, 68, 0.08)' :
    messageType === 'claude' ? 'rgba(34, 197, 94, 0.06)' :
    messageType === 'user' ? 'rgba(59, 130, 246, 0.06)' :
    messageType === 'tool' ? 'rgba(245, 158, 11, 0.06)' :
    messageType === 'system' ? 'rgba(139, 92, 246, 0.06)' :
    'rgba(255, 255, 255, 0.02)',
  borderLeft: `4px solid ${
    messageType === 'error' ? '#ef4444' :
    messageType === 'claude' ? '#22c55e' :
    messageType === 'user' ? '#3b82f6' :
    messageType === 'tool' ? '#f59e0b' :
    messageType === 'system' ? '#8b5cf6' :
    'rgba(255, 255, 255, 0.1)'
  }`,
  transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
  cursor: 'default',
  position: 'relative',
  '&:hover': {
    backgroundColor: 
      messageType === 'error' ? 'rgba(239, 68, 68, 0.12)' :
      messageType === 'claude' ? 'rgba(34, 197, 94, 0.1)' :
      messageType === 'user' ? 'rgba(59, 130, 246, 0.1)' :
      messageType === 'tool' ? 'rgba(245, 158, 11, 0.1)' :
      messageType === 'system' ? 'rgba(139, 92, 246, 0.1)' :
      'rgba(255, 255, 255, 0.04)',
    transform: 'translateX(2px)',
    boxShadow: '0 4px 12px rgba(0, 0, 0, 0.15)',
  },
  '&::before': {
    content: '""',
    position: 'absolute',
    left: 0,
    top: 0,
    bottom: 0,
    width: '4px',
    background: `linear-gradient(135deg, ${
      messageType === 'error' ? '#ef4444' :
      messageType === 'claude' ? '#22c55e' :
      messageType === 'user' ? '#3b82f6' :
      messageType === 'tool' ? '#f59e0b' :
      messageType === 'system' ? '#8b5cf6' :
      'rgba(255, 255, 255, 0.1)'
    }, transparent)`,
    borderRadius: '0 4px 4px 0',
  },
}));


interface ClaudeTerminalProps {
  taskId: number;
  projectPath?: string;
  onSessionStop?: () => void;
}

interface ClaudeMessage {
  type: 'system' | 'user' | 'claude' | 'error' | 'tool' | 'status' | 'pong' | 'ping' | 'output' | 'history';
  content: string | any[];
  timestamp: string;
  subtype?: string;
  session_id?: string;
  metadata?: any;
}

interface SessionMetrics {
  messages_sent: number;
  messages_received: number;
  tools_executed: number;
  errors_count: number;
  session_duration: number;
}

const ClaudeTerminal: React.FC<ClaudeTerminalProps> = ({ 
  taskId, 
  projectPath,
  onSessionStop 
}) => {
  const [isActive, setIsActive] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [messages, setMessages] = useState<ClaudeMessage[]>([]);
  const [commandInput, setCommandInput] = useState<string>('');
  const [useWebSocket, setUseWebSocket] = useState(true);
  const [wsConnected, setWsConnected] = useState(false);
  const [showControls, setShowControls] = useState(true);
  const [showMetrics, setShowMetrics] = useState(false);
  const [isFullscreen, setIsFullscreen] = useState(false);
  const [metrics, setMetrics] = useState<SessionMetrics>({
    messages_sent: 0,
    messages_received: 0,
    tools_executed: 0,
    errors_count: 0,
    session_duration: 0,
  });
  const [isTyping, setIsTyping] = useState(false);
  
  const wsRef = useRef<WebSocket | null>(null);
  const eventSourceRef = useRef<EventSource | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout>();
  const containerRef = useRef<HTMLDivElement>(null);
  const typingTimeoutRef = useRef<NodeJS.Timeout>();

  // Define connection functions with useCallback to prevent recreating on each render
  const connectWebSocket = useCallback((sessionId: string) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      return;
    }

    const wsUrl = `ws://localhost:3333/api/sessions/embedded/${sessionId}/ws`;
    console.log('Connecting to WebSocket:', wsUrl);
    
    const ws = new WebSocket(wsUrl);
    wsRef.current = ws;

    ws.onopen = () => {
      console.log('WebSocket connected');
      setWsConnected(true);
      ws.send(JSON.stringify({ type: 'ping' }));
    };

    ws.onmessage = (event) => {
      try {
        const message = JSON.parse(event.data);
        console.log('WebSocket message received:', message);
        
        if (message.type && message.type !== 'pong') {
          // Handle history message specially
          if (message.type === 'history') {
            console.log('Received session history, restoring messages...');
            const historyMessages = message.content as any[];
            if (Array.isArray(historyMessages)) {
              setMessages(historyMessages);
              console.log(`Restored ${historyMessages.length} messages from history`);
            }
          } else {
            setMessages(prev => [...prev, message as ClaudeMessage]);
          }
          
          // Update metrics based on message type
          if (message.type === 'claude' || message.type === 'output') {
            setMetrics(prev => ({ ...prev, messages_received: prev.messages_received + 1 }));
            setIsTyping(false);
          } else if (message.type === 'tool') {
            setMetrics(prev => ({ ...prev, tools_executed: prev.tools_executed + 1 }));
          } else if (message.type === 'error') {
            setMetrics(prev => ({ ...prev, errors_count: prev.errors_count + 1 }));
          }
        }
      } catch (error) {
        console.error('Error parsing WebSocket message:', error);
      }
    };

    ws.onerror = (error) => {
      console.error('WebSocket error:', error);
      setWsConnected(false);
    };

    ws.onclose = () => {
      console.log('WebSocket disconnected');
      setWsConnected(false);
      wsRef.current = null;
      
      if (isActive) {
        reconnectTimeoutRef.current = setTimeout(() => {
          console.log('Attempting to reconnect WebSocket...');
          connectWebSocket(sessionId);
        }, 2000);
      }
    };
  }, [isActive]);

  const connectSSE = useCallback((sessionId: string) => {
    if (eventSourceRef.current) {
      eventSourceRef.current.close();
    }

    console.log('Connecting to SSE stream for session:', sessionId);
    
    eventSourceRef.current = new EventSource(
      `http://localhost:3333/api/sessions/embedded/${sessionId}/stream`
    );

    eventSourceRef.current.onmessage = (event) => {
      try {
        const message = JSON.parse(event.data) as ClaudeMessage;
        console.log('SSE message received:', message);
        setMessages(prev => [...prev, message]);
      } catch (error) {
        console.error('Error parsing SSE message:', error);
      }
    };

    eventSourceRef.current.onerror = (error) => {
      console.error('SSE error:', error);
    };
  }, []);

  // Auto-launch session on mount
  useEffect(() => {
    const autoStartSession = async () => {
      if (!taskId) {
        console.log('No taskId, skipping auto-start');
        return;
      }
      if (isActive || sessionId) {
        console.log('Session already active, skipping auto-start');
        return;
      }
      
      console.log('Auto-starting session for task:', taskId);
      
      try {
        setIsLoading(true);
        
        const response = await fetch(`http://localhost:3333/api/sessions/launch/embedded`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ task_id: taskId }),
        });
        
        const data = await response.json();
        console.log('Auto-start session response:', data);
        
        if (data.success) {
          setSessionId(data.session_id);
          setIsActive(true);
          setMetrics({
            messages_sent: 0,
            messages_received: 0,
            tools_executed: 0,
            errors_count: 0,
            session_duration: 0,
          });
          
          // Check if this is a reconnection or new session
          const isReconnection = data.message === 'Reconnected to existing Claude session';
          
          if (isReconnection) {
            console.log('Auto-reconnected to existing session:', data.session_id);
            setMessages([{
              type: 'system',
              content: `Reconnected to existing session: ${data.session_id}`,
              timestamp: new Date().toISOString()
            }]);
          } else {
            console.log('Auto-started new session:', data.session_id);
            if (data.info) {
              setMessages([{
                type: 'system',
                content: `Session started: PID ${data.info.pid}, Working Directory: ${data.info.working_dir}`,
                timestamp: new Date().toISOString()
              }]);
            }
          }
          
          // Connect WebSocket for both new and reconnected sessions
          if (useWebSocket) {
            connectWebSocket(data.session_id);
          } else {
            connectSSE(data.session_id);
          }
        } else {
          console.error('Failed to auto-start session:', data);
          setMessages([{
            type: 'error',
            content: `Failed to start session: ${data.error || 'Unknown error'}`,
            timestamp: new Date().toISOString()
          }]);
        }
      } catch (error) {
        console.error('Error auto-starting session:', error);
        setMessages([{
          type: 'error',
          content: `Error starting session: ${error}`,
          timestamp: new Date().toISOString()
        }]);
      } finally {
        setIsLoading(false);
      }
    };
    
    // Run auto-start immediately when component mounts
    autoStartSession();
  }, [taskId]); // Only depend on taskId to avoid infinite loops
  
  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (wsRef.current) {
        wsRef.current.close();
      }
      if (eventSourceRef.current) {
        eventSourceRef.current.close();
      }
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current);
      }
      if (typingTimeoutRef.current) {
        clearTimeout(typingTimeoutRef.current);
      }
    };
  }, []);

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
        setIsActive(true);
        setMetrics({
          messages_sent: 0,
          messages_received: 0,
          tools_executed: 0,
          errors_count: 0,
          session_duration: 0,
        });
        
        if (data.info) {
          setMessages(prev => [...prev, {
            type: 'system',
            content: `Session started: PID ${data.info.pid}, Working Directory: ${data.info.working_dir}`,
            timestamp: new Date().toISOString()
          }]);
        }
        
        if (useWebSocket) {
          connectWebSocket(data.session_id);
        } else {
          connectSSE(data.session_id);
        }
      } else {
        console.error('Failed to start session:', data);
        setMessages(prev => [...prev, {
          type: 'error',
          content: `Failed to start session: ${data.error || 'Unknown error'}`,
          timestamp: new Date().toISOString()
        }]);
      }
    } catch (error) {
      console.error('Error starting session:', error);
      setMessages(prev => [...prev, {
        type: 'error',
        content: `Error starting session: ${error}`,
        timestamp: new Date().toISOString()
      }]);
    } finally {
      setIsLoading(false);
    }
  };

  const stopSession = async () => {
    try {
      if (sessionId) {
        await fetch(`http://localhost:3333/api/sessions/embedded/${sessionId}/stop`, {
          method: 'POST',
        });
        
        if (wsRef.current) {
          wsRef.current.close();
          wsRef.current = null;
        }
        if (eventSourceRef.current) {
          eventSourceRef.current.close();
          eventSourceRef.current = null;
        }
        
        setSessionId(null);
        setIsActive(false);
        setWsConnected(false);
        
        setMessages(prev => [...prev, {
          type: 'system',
          content: 'Session terminated',
          timestamp: new Date().toISOString()
        }]);
        
        if (onSessionStop) {
          onSessionStop();
        }
      }
    } catch (error) {
      console.error('Error stopping session:', error);
    }
  };

  const clearMessages = () => {
    setMessages([]);
  };

  const sendCommand = async (command: string) => {
    if (!sessionId || !command.trim()) return;
    
    setMetrics(prev => ({ ...prev, messages_sent: prev.messages_sent + 1 }));
    setIsTyping(true);
    
    if (typingTimeoutRef.current) {
      clearTimeout(typingTimeoutRef.current);
    }
    typingTimeoutRef.current = setTimeout(() => {
      setIsTyping(false);
    }, 30000); // Stop typing indicator after 30 seconds
    
    if (useWebSocket && wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({
        type: 'input',
        content: command
      }));
    } else {
      try {
        await fetch(`http://localhost:3333/api/sessions/embedded/${sessionId}/input`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ input: command }),
        });
      } catch (error) {
        console.error('Error sending command:', error);
      }
    }
  };

  const handleSendCommand = async () => {
    if (commandInput.trim()) {
      await sendCommand(commandInput);
      setCommandInput('');
    }
  };

  const sendKey = async (key: string) => {
    if (!sessionId) return;
    
    if (useWebSocket && wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({
        type: 'key',
        key: key
      }));
    } else {
      try {
        await fetch(
          `http://localhost:3333/api/sessions/embedded/${sessionId}/key`,
          {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify({ key }),
          }
        );
      } catch (error) {
        console.error('Error sending key:', error);
      }
    }
  };

  const copyAllMessages = () => {
    const text = messages.map(m => 
      `[${new Date(m.timestamp).toLocaleTimeString()}] [${m.type.toUpperCase()}]: ${m.content}`
    ).join('\n');
    navigator.clipboard.writeText(text);
  };

  const downloadLog = () => {
    const text = messages.map(m => 
      `[${new Date(m.timestamp).toISOString()}] [${m.type.toUpperCase()}]${m.subtype ? ` (${m.subtype})` : ''}: ${m.content}`
    ).join('\n');
    const blob = new Blob([text], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `claude-session-${sessionId || 'unknown'}.log`;
    a.click();
    URL.revokeObjectURL(url);
  };

  const toggleFullscreen = () => {
    setIsFullscreen(!isFullscreen);
    if (!isFullscreen && containerRef.current) {
      containerRef.current.requestFullscreen?.();
    } else if (document.fullscreenElement) {
      document.exitFullscreen?.();
    }
  };

  const getMessageIcon = (type: string) => {
    switch (type) {
      case 'system': return <Info fontSize="small" />;
      case 'user': return <Person fontSize="small" />;
      case 'claude': return <SmartToy fontSize="small" />;
      case 'error': return <ErrorIcon fontSize="small" />;
      case 'tool': return <Build fontSize="small" />;
      case 'status': return <CheckCircle fontSize="small" />;
      default: return null;
    }
  };

  const getMessageColor = (type: string) => {
    switch (type) {
      case 'system': return '#6e7681';
      case 'user': return '#388bfd';
      case 'claude': return '#2ea043';
      case 'error': return '#f85149';
      case 'tool': return '#ffab00';
      case 'status': return '#a371f7';
      default: return '#c9d1d9';
    }
  };

  return (
    <StyledTerminalContainer ref={containerRef}>
      {/* Terminal Header */}
      <StyledHeader>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
          <ClaudeIcon sx={{ 
            color: '#6366f1', 
            fontSize: '24px',
            filter: 'drop-shadow(0 0 8px rgba(99, 102, 241, 0.3))'
          }} />
          <Typography variant="h6" sx={{ 
            color: '#ffffff', 
            fontSize: '16px', 
            fontWeight: 700,
            fontFamily: '"JetBrains Mono", monospace',
            textShadow: '0 1px 2px rgba(0, 0, 0, 0.3)'
          }}>
            Claude Terminal
          </Typography>
          <Typography variant="caption" sx={{ 
            color: '#a0a0a0', 
            fontSize: '12px',
            fontFamily: '"JetBrains Mono", monospace',
            backgroundColor: 'rgba(255, 255, 255, 0.05)',
            padding: '4px 8px',
            borderRadius: '6px',
            border: '1px solid rgba(255, 255, 255, 0.1)'
          }}>
            Task #{taskId}
          </Typography>
          
          <Grow in={isActive}>
            <Chip
              label="● Active"
              size="small"
              sx={{ 
                backgroundColor: 'rgba(34, 197, 94, 0.2)',
                color: '#22c55e',
                fontSize: '11px',
                height: '24px',
                fontFamily: '"JetBrains Mono", monospace',
                fontWeight: 600,
                border: '1px solid rgba(34, 197, 94, 0.3)',
                boxShadow: '0 0 8px rgba(34, 197, 94, 0.2)',
                '&:hover': {
                  backgroundColor: 'rgba(34, 197, 94, 0.25)',
                  boxShadow: '0 0 12px rgba(34, 197, 94, 0.3)',
                }
              }}
            />
          </Grow>
          
          {isActive && (
            <Tooltip title={wsConnected ? 'WebSocket Connected' : 'Using SSE'}>
              <Chip
                icon={wsConnected ? <Wifi sx={{ fontSize: '14px' }} /> : <WifiOff sx={{ fontSize: '14px' }} />}
                label={wsConnected ? 'WebSocket' : 'SSE'}
                size="small"
                sx={{
                  backgroundColor: wsConnected ? 'rgba(59, 130, 246, 0.2)' : 'rgba(245, 158, 11, 0.2)',
                  color: wsConnected ? '#3b82f6' : '#f59e0b',
                  fontSize: '11px',
                  height: '24px',
                  fontFamily: '"JetBrains Mono", monospace',
                  fontWeight: 600,
                  border: wsConnected ? '1px solid rgba(59, 130, 246, 0.3)' : '1px solid rgba(245, 158, 11, 0.3)',
                  boxShadow: wsConnected ? '0 0 8px rgba(59, 130, 246, 0.2)' : '0 0 8px rgba(245, 158, 11, 0.2)',
                  '& .MuiChip-icon': {
                    marginLeft: '4px'
                  },
                  '&:hover': {
                    backgroundColor: wsConnected ? 'rgba(59, 130, 246, 0.25)' : 'rgba(245, 158, 11, 0.25)',
                    boxShadow: wsConnected ? '0 0 12px rgba(59, 130, 246, 0.3)' : '0 0 12px rgba(245, 158, 11, 0.3)',
                  }
                }}
              />
            </Tooltip>
          )}
          
          <Fade in={isTyping}>
            <Chip
              label="⟨⟩ Claude is typing..."
              size="small"
              sx={{
                backgroundColor: 'rgba(139, 92, 246, 0.2)',
                color: '#8b5cf6',
                fontSize: '11px',
                height: '24px',
                fontFamily: '"JetBrains Mono", monospace',
                fontWeight: 600,
                border: '1px solid rgba(139, 92, 246, 0.3)',
                boxShadow: '0 0 8px rgba(139, 92, 246, 0.2)',
                animation: 'pulse 2s infinite',
                '@keyframes pulse': {
                  '0%': {
                    boxShadow: '0 0 8px rgba(139, 92, 246, 0.2)',
                  },
                  '50%': {
                    boxShadow: '0 0 16px rgba(139, 92, 246, 0.4)',
                  },
                  '100%': {
                    boxShadow: '0 0 8px rgba(139, 92, 246, 0.2)',
                  },
                }
              }}
            />
          </Fade>
        </Box>
        
        <Box sx={{ display: 'flex', gap: 1 }}>
          <Tooltip title="Toggle Metrics" arrow>
            <IconButton 
              size="small" 
              onClick={() => setShowMetrics(!showMetrics)}
              sx={{ 
                color: '#a0a0a0',
                backgroundColor: 'rgba(255, 255, 255, 0.05)',
                border: '1px solid rgba(255, 255, 255, 0.1)',
                borderRadius: '8px',
                width: '36px',
                height: '36px',
                transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
                '&:hover': {
                  color: '#ffffff',
                  backgroundColor: 'rgba(255, 255, 255, 0.1)',
                  borderColor: 'rgba(255, 255, 255, 0.2)',
                  boxShadow: '0 4px 12px rgba(0, 0, 0, 0.2)',
                  transform: 'translateY(-1px)',
                }
              }}
            >
              <Badge 
                badgeContent={metrics.messages_received} 
                sx={{
                  '& .MuiBadge-badge': {
                    backgroundColor: '#6366f1',
                    color: '#ffffff',
                    fontSize: '10px',
                    fontWeight: 600,
                    border: '1px solid rgba(255, 255, 255, 0.2)',
                    boxShadow: '0 0 8px rgba(99, 102, 241, 0.3)',
                  }
                }}
                max={99}
              >
                <History fontSize="small" />
              </Badge>
            </IconButton>
          </Tooltip>
          
          <Tooltip title="Copy All" arrow>
            <IconButton 
              size="small" 
              onClick={copyAllMessages}
              sx={{ 
                color: '#a0a0a0',
                backgroundColor: 'rgba(255, 255, 255, 0.05)',
                border: '1px solid rgba(255, 255, 255, 0.1)',
                borderRadius: '8px',
                width: '36px',
                height: '36px',
                transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
                '&:hover': {
                  color: '#ffffff',
                  backgroundColor: 'rgba(255, 255, 255, 0.1)',
                  borderColor: 'rgba(255, 255, 255, 0.2)',
                  boxShadow: '0 4px 12px rgba(0, 0, 0, 0.2)',
                  transform: 'translateY(-1px)',
                },
                '&:disabled': {
                  color: '#555555',
                  backgroundColor: 'rgba(255, 255, 255, 0.02)',
                  borderColor: 'rgba(255, 255, 255, 0.05)',
                }
              }}
              disabled={messages.length === 0}
            >
              <ContentCopy fontSize="small" />
            </IconButton>
          </Tooltip>
          
          <Tooltip title="Download Log" arrow>
            <IconButton 
              size="small" 
              onClick={downloadLog}
              sx={{ 
                color: '#a0a0a0',
                backgroundColor: 'rgba(255, 255, 255, 0.05)',
                border: '1px solid rgba(255, 255, 255, 0.1)',
                borderRadius: '8px',
                width: '36px',
                height: '36px',
                transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
                '&:hover': {
                  color: '#ffffff',
                  backgroundColor: 'rgba(255, 255, 255, 0.1)',
                  borderColor: 'rgba(255, 255, 255, 0.2)',
                  boxShadow: '0 4px 12px rgba(0, 0, 0, 0.2)',
                  transform: 'translateY(-1px)',
                },
                '&:disabled': {
                  color: '#555555',
                  backgroundColor: 'rgba(255, 255, 255, 0.02)',
                  borderColor: 'rgba(255, 255, 255, 0.05)',
                }
              }}
              disabled={messages.length === 0}
            >
              <Download fontSize="small" />
            </IconButton>
          </Tooltip>
          
          <Tooltip title="Clear Messages" arrow>
            <IconButton 
              size="small" 
              onClick={clearMessages}
              sx={{ 
                color: '#a0a0a0',
                backgroundColor: 'rgba(255, 255, 255, 0.05)',
                border: '1px solid rgba(255, 255, 255, 0.1)',
                borderRadius: '8px',
                width: '36px',
                height: '36px',
                transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
                '&:hover': {
                  color: '#ffffff',
                  backgroundColor: 'rgba(255, 255, 255, 0.1)',
                  borderColor: 'rgba(255, 255, 255, 0.2)',
                  boxShadow: '0 4px 12px rgba(0, 0, 0, 0.2)',
                  transform: 'translateY(-1px)',
                }
              }}
            >
              <ClearIcon fontSize="small" />
            </IconButton>
          </Tooltip>
          
          <Tooltip title="Toggle Fullscreen">
            <IconButton 
              size="small" 
              onClick={toggleFullscreen}
              sx={{ color: '#8b949e' }}
            >
              {isFullscreen ? <FullscreenExit fontSize="small" /> : <Fullscreen fontSize="small" />}
            </IconButton>
          </Tooltip>
          
          <Divider orientation="vertical" flexItem sx={{ mx: 1, bgcolor: '#30363d' }} />
          
          {isActive ? (
            <Tooltip title="Stop Session">
              <IconButton 
                size="small" 
                onClick={stopSession}
                sx={{ 
                  color: '#f85149',
                  '&:hover': {
                    backgroundColor: 'rgba(248, 81, 73, 0.1)'
                  }
                }}
              >
                <StopIcon fontSize="small" />
              </IconButton>
            </Tooltip>
          ) : (
            <Tooltip title="Start Session">
              <IconButton 
                size="small" 
                onClick={startSession}
                sx={{ 
                  color: '#2ea043',
                  '&:hover': {
                    backgroundColor: 'rgba(46, 160, 67, 0.1)'
                  }
                }}
                disabled={isLoading}
              >
                {isLoading ? <CircularProgress size={16} /> : <StartIcon fontSize="small" />}
              </IconButton>
            </Tooltip>
          )}
        </Box>
      </StyledHeader>

      {/* Metrics Panel */}
      <Collapse in={showMetrics}>
        <Box sx={{ 
          p: 2, 
          bgcolor: '#161b22', 
          borderBottom: '1px solid #30363d',
          display: 'flex',
          gap: 3,
        }}>
          <Box>
            <Typography variant="caption" sx={{ color: '#8b949e' }}>
              Messages Sent
            </Typography>
            <Typography variant="h6" sx={{ color: '#f0f6fc' }}>
              {metrics.messages_sent}
            </Typography>
          </Box>
          <Box>
            <Typography variant="caption" sx={{ color: '#8b949e' }}>
              Messages Received
            </Typography>
            <Typography variant="h6" sx={{ color: '#f0f6fc' }}>
              {metrics.messages_received}
            </Typography>
          </Box>
          <Box>
            <Typography variant="caption" sx={{ color: '#8b949e' }}>
              Tools Executed
            </Typography>
            <Typography variant="h6" sx={{ color: '#ffab00' }}>
              {metrics.tools_executed}
            </Typography>
          </Box>
          <Box>
            <Typography variant="caption" sx={{ color: '#8b949e' }}>
              Errors
            </Typography>
            <Typography variant="h6" sx={{ color: '#f85149' }}>
              {metrics.errors_count}
            </Typography>
          </Box>
        </Box>
      </Collapse>

      {/* Progress indicator */}
      {isTyping && (
        <LinearProgress 
          sx={{ 
            height: '2px',
            backgroundColor: '#161b22',
            '& .MuiLinearProgress-bar': {
              backgroundColor: '#a371f7'
            }
          }}
        />
      )}

      {/* Messages Display */}
      <StyledMessageContainer>
        {messages.length === 0 ? (
          <Box sx={{ 
            display: 'flex', 
            flexDirection: 'column', 
            alignItems: 'center', 
            justifyContent: 'center',
            height: '100%',
            gap: 2
          }}>
            <ClaudeIcon sx={{ fontSize: 48, color: '#30363d' }} />
            <Typography sx={{ color: '#8b949e', fontSize: '14px' }}>
              {isActive ? 'Waiting for messages...' : 'Click the play button to start a Claude session'}
            </Typography>
          </Box>
        ) : (
          messages.map((msg, index) => (
            <MessageLine key={index} messageType={msg.type}>
              <Box sx={{ display: 'flex', alignItems: 'flex-start', gap: 1 }}>
                <Box sx={{ color: getMessageColor(msg.type), mt: 0.5 }}>
                  {getMessageIcon(msg.type)}
                </Box>
                <Box sx={{ flex: 1 }}>
                  <Typography
                    component="span"
                    sx={{
                      color: '#8b949e',
                      fontSize: '11px',
                      fontFamily: 'monospace',
                      display: 'inline-block',
                      mb: 0.5
                    }}
                  >
                    {new Date(msg.timestamp).toLocaleTimeString()}
                    {msg.subtype && ` • ${msg.subtype}`}
                  </Typography>
                  <Typography
                    sx={{
                      color: getMessageColor(msg.type),
                      fontSize: '13px',
                      fontFamily: 'monospace',
                      whiteSpace: 'pre-wrap',
                      wordBreak: 'break-word',
                      lineHeight: 1.6
                    }}
                  >
                    {typeof msg.content === 'string' ? msg.content : JSON.stringify(msg.content)}
                  </Typography>
                </Box>
              </Box>
            </MessageLine>
          ))
        )}
        <div ref={messagesEndRef} />
      </StyledMessageContainer>

      {/* Interactive Controls */}
      {isActive && (
        <Box sx={{ 
          borderTop: '1px solid #30363d',
          bgcolor: '#161b22'
        }}>
          <Box sx={{ p: 1, display: 'flex', alignItems: 'center', gap: 1 }}>
            <IconButton
              size="small"
              onClick={() => setShowControls(!showControls)}
              sx={{ color: '#8b949e' }}
            >
              {showControls ? <ExpandMore /> : <ExpandLess />}
            </IconButton>
            <Typography variant="caption" sx={{ color: '#8b949e' }}>
              Quick Controls
            </Typography>
          </Box>
          
          <Collapse in={showControls}>
            <Box sx={{ p: 2, pt: 0 }}>
              <Stack spacing={2}>
                {/* Arrow Keys and Selection */}
                <Box sx={{ display: 'flex', gap: 2, alignItems: 'center', flexWrap: 'wrap' }}>
                  <ButtonGroup variant="outlined" size="small">
                    <Tooltip title="Up Arrow">
                      <Button onClick={() => sendKey('up')} sx={{ minWidth: '40px' }}>
                        <ArrowUpward fontSize="small" />
                      </Button>
                    </Tooltip>
                    <Tooltip title="Down Arrow">
                      <Button onClick={() => sendKey('down')} sx={{ minWidth: '40px' }}>
                        <ArrowDownward fontSize="small" />
                      </Button>
                    </Tooltip>
                    <Tooltip title="Left Arrow">
                      <Button onClick={() => sendKey('left')} sx={{ minWidth: '40px' }}>
                        <ArrowBack fontSize="small" />
                      </Button>
                    </Tooltip>
                    <Tooltip title="Right Arrow">
                      <Button onClick={() => sendKey('right')} sx={{ minWidth: '40px' }}>
                        <ArrowForward fontSize="small" />
                      </Button>
                    </Tooltip>
                  </ButtonGroup>
                  
                  <ButtonGroup variant="outlined" size="small">
                    <Button onClick={() => sendKey('enter')} sx={{ minWidth: '60px' }}>
                      Enter
                    </Button>
                    <Button onClick={() => sendKey('escape')} sx={{ minWidth: '50px' }}>
                      ESC
                    </Button>
                    <Button onClick={() => sendKey('tab')} sx={{ minWidth: '50px' }}>
                      Tab
                    </Button>
                  </ButtonGroup>
                  
                  <ButtonGroup variant="outlined" size="small">
                    {[1, 2, 3, 4, 5].map(num => (
                      <Tooltip key={num} title={`Select option ${num}`}>
                        <Button 
                          onClick={() => sendKey(String(num))}
                          sx={{ minWidth: '36px' }}
                        >
                          {num}
                        </Button>
                      </Tooltip>
                    ))}
                  </ButtonGroup>
                </Box>
              </Stack>
            </Box>
          </Collapse>
          
          {/* Command Input */}
          <Box sx={{ 
            p: 2, 
            display: 'flex', 
            gap: 1,
            borderTop: '1px solid #30363d' 
          }}>
            <TextField
              size="small"
              fullWidth
              placeholder="Type a command or message..."
              value={commandInput}
              onChange={(e) => setCommandInput(e.target.value)}
              onKeyPress={(e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                  e.preventDefault();
                  handleSendCommand();
                }
              }}
              multiline
              maxRows={3}
              sx={{
                '& .MuiInputBase-root': {
                  color: '#f0f6fc',
                  backgroundColor: '#0d1117',
                  fontFamily: 'monospace',
                  fontSize: '13px',
                  border: '1px solid #30363d',
                  '&:hover': {
                    borderColor: '#484f58'
                  },
                  '&.Mui-focused': {
                    borderColor: '#388bfd'
                  }
                },
                '& .MuiOutlinedInput-notchedOutline': {
                  border: 'none'
                }
              }}
            />
            <Button
              variant="contained"
              size="small"
              onClick={handleSendCommand}
              disabled={!commandInput.trim()}
              endIcon={<SendIcon />}
              sx={{
                backgroundColor: '#238636',
                color: '#ffffff',
                '&:hover': {
                  backgroundColor: '#2ea043'
                },
                '&:disabled': {
                  backgroundColor: '#21262d',
                  color: '#484f58'
                }
              }}
            >
              Send
            </Button>
          </Box>
        </Box>
      )}
    </StyledTerminalContainer>
  );
};

export default ClaudeTerminal;