import React, { useState, useRef, useEffect } from 'react';
import {
  Box,
  Paper,
  Typography,
  IconButton,
  TextField,
  Button,
} from '@mui/material';
import {
  Terminal as TerminalIcon,
  PlayArrow,
  Stop,
  Clear,
  Send,
} from '@mui/icons-material';
import { styled } from '@mui/material/styles';

// Simple terminal styling like opcode
const TerminalContainer = styled(Paper)(({ theme }) => ({
  backgroundColor: '#1e1e1e',
  color: '#ffffff',
  fontFamily: '"JetBrains Mono", "SF Mono", monospace',
  fontSize: '13px',
  height: '500px',
  display: 'flex',
  flexDirection: 'column',
  border: '1px solid #333',
  borderRadius: '8px',
  overflow: 'hidden',
}));

const TerminalHeader = styled(Box)(({ theme }) => ({
  padding: '8px 12px',
  backgroundColor: '#2d2d2d',
  borderBottom: '1px solid #333',
  display: 'flex',
  justifyContent: 'space-between',
  alignItems: 'center',
}));

const TerminalOutput = styled(Box)(({ theme }) => ({
  flex: 1,
  padding: '12px',
  overflow: 'auto',
  backgroundColor: '#1e1e1e',
  fontFamily: '"JetBrains Mono", monospace',
  fontSize: '13px',
  lineHeight: '1.4',
  '&::-webkit-scrollbar': {
    width: '8px',
  },
  '&::-webkit-scrollbar-track': {
    background: '#2d2d2d',
  },
  '&::-webkit-scrollbar-thumb': {
    background: '#555',
    borderRadius: '4px',
  },
}));

const TerminalInputArea = styled(Box)(({ theme }) => ({
  padding: '12px',
  backgroundColor: '#2d2d2d',
  borderTop: '1px solid #333',
  display: 'flex',
  gap: '8px',
  alignItems: 'center',
}));

interface Message {
  id: number;
  text: string;
  isUser: boolean;
  timestamp: Date;
}

interface Props {
  taskId: number;
}

const SimpleClaudeTerminal: React.FC<Props> = ({ taskId }) => {
  const [isActive, setIsActive] = useState(false);
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [sessionId, setSessionId] = useState<string | null>(null);
  const outputRef = useRef<HTMLDivElement>(null);
  const eventSourceRef = useRef<EventSource | null>(null);

  useEffect(() => {
    if (outputRef.current) {
      outputRef.current.scrollTop = outputRef.current.scrollHeight;
    }
  }, [messages]);

  const addMessage = (text: string, isUser: boolean = false) => {
    setMessages(prev => [...prev, {
      id: Date.now(),
      text,
      isUser,
      timestamp: new Date()
    }]);
  };

  const startSession = async () => {
    try {
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
        addMessage(`Session started: ${data.session_id}`);
        
        // Connect to stream
        connectStream(data.session_id);
      } else {
        addMessage(`Error: ${data.error || 'Failed to start session'}`);
      }
    } catch (error) {
      addMessage(`Error: ${error}`);
    }
  };

  const connectStream = (sessionId: string) => {
    if (eventSourceRef.current) {
      eventSourceRef.current.close();
    }

    eventSourceRef.current = new EventSource(
      `http://localhost:3333/api/sessions/embedded/${sessionId}/stream`
    );

    eventSourceRef.current.onmessage = (event) => {
      try {
        const message = JSON.parse(event.data);
        // Clean up the content - remove special characters and formatting
        let cleanContent = message.content || '';
        
        // Remove common CLI formatting characters
        cleanContent = cleanContent
          .replace(/[╭╰╯╮├┤┌┐└┘│─┬┴┼]/g, '') // Remove box drawing chars
          .replace(/\u001b\[[0-9;]*m/g, '') // Remove ANSI color codes
          .replace(/[▏▎▍▌▋▊▉█]/g, '') // Remove block chars
          .replace(/^\s*[>│]\s*/gm, '') // Remove prompt chars
          .trim();

        if (cleanContent && cleanContent !== '(Thinking...)') {
          addMessage(cleanContent);
        }
      } catch (error) {
        console.error('Error parsing message:', error);
      }
    };

    eventSourceRef.current.onerror = (error) => {
      console.error('Stream error:', error);
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
    
    if (eventSourceRef.current) {
      eventSourceRef.current.close();
      eventSourceRef.current = null;
    }
    
    setIsActive(false);
    setSessionId(null);
    addMessage('Session stopped');
  };

  const sendCommand = async () => {
    if (!sessionId || !input.trim()) return;

    const command = input.trim();
    addMessage(`> ${command}`, true);
    setInput('');

    try {
      await fetch(`http://localhost:3333/api/sessions/embedded/${sessionId}/input`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ input: command }),
      });
    } catch (error) {
      addMessage(`Error sending command: ${error}`);
    }
  };

  const clearOutput = () => {
    setMessages([]);
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendCommand();
    }
  };

  return (
    <TerminalContainer>
      <TerminalHeader>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <TerminalIcon sx={{ color: '#888', fontSize: '18px' }} />
          <Typography sx={{ color: '#fff', fontSize: '14px', fontWeight: 500 }}>
            Claude Terminal - Task #{taskId}
          </Typography>
          {isActive && (
            <Box sx={{ 
              width: '8px', 
              height: '8px', 
              backgroundColor: '#4ade80', 
              borderRadius: '50%',
              ml: 1 
            }} />
          )}
        </Box>
        
        <Box sx={{ display: 'flex', gap: 0.5 }}>
          <IconButton
            size="small"
            onClick={clearOutput}
            sx={{ color: '#888', '&:hover': { color: '#fff' } }}
          >
            <Clear fontSize="small" />
          </IconButton>
          
          {isActive ? (
            <IconButton
              size="small"
              onClick={stopSession}
              sx={{ color: '#f87171', '&:hover': { color: '#fca5a5' } }}
            >
              <Stop fontSize="small" />
            </IconButton>
          ) : (
            <IconButton
              size="small"
              onClick={startSession}
              sx={{ color: '#4ade80', '&:hover': { color: '#86efac' } }}
            >
              <PlayArrow fontSize="small" />
            </IconButton>
          )}
        </Box>
      </TerminalHeader>

      <TerminalOutput ref={outputRef}>
        {messages.length === 0 ? (
          <Typography sx={{ color: '#666', fontStyle: 'italic' }}>
            {isActive ? 'Waiting for output...' : 'Click play to start Claude session'}
          </Typography>
        ) : (
          messages.map((msg) => (
            <Box key={msg.id} sx={{ mb: 0.5 }}>
              <Typography
                component="pre"
                sx={{
                  color: msg.isUser ? '#60a5fa' : '#fff',
                  fontSize: '13px',
                  fontFamily: 'inherit',
                  margin: 0,
                  whiteSpace: 'pre-wrap',
                  wordBreak: 'break-word',
                }}
              >
                {msg.text}
              </Typography>
            </Box>
          ))
        )}
      </TerminalOutput>

      {isActive && (
        <TerminalInputArea>
          <TextField
            fullWidth
            size="small"
            placeholder="Type your message or command..."
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={handleKeyPress}
            sx={{
              '& .MuiInputBase-root': {
                backgroundColor: '#1e1e1e',
                color: '#fff',
                fontSize: '13px',
                fontFamily: '"JetBrains Mono", monospace',
                border: '1px solid #555',
                borderRadius: '4px',
                '&:hover': {
                  borderColor: '#777',
                },
                '&.Mui-focused': {
                  borderColor: '#60a5fa',
                },
              },
              '& .MuiOutlinedInput-notchedOutline': {
                border: 'none',
              },
            }}
          />
          <Button
            variant="contained"
            size="small"
            onClick={sendCommand}
            disabled={!input.trim()}
            sx={{
              backgroundColor: '#3b82f6',
              '&:hover': {
                backgroundColor: '#2563eb',
              },
              '&:disabled': {
                backgroundColor: '#374151',
              },
            }}
          >
            <Send fontSize="small" />
          </Button>
        </TerminalInputArea>
      )}
    </TerminalContainer>
  );
};

export default SimpleClaudeTerminal;