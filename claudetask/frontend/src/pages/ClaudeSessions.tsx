import React, { useState, useEffect } from 'react';
import {
  Box,
  Paper,
  Typography,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Chip,
  IconButton,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  Tabs,
  Tab,
  Grid,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Divider,
  LinearProgress,
  Alert,
  Container,
  alpha,
  useTheme,
  Stack
} from '@mui/material';
import {
  PlayArrow as PlayIcon,
  Pause as PauseIcon,
  Stop as StopIcon,
  Refresh as RefreshIcon,
  History as HistoryIcon,
  Terminal as TerminalIcon,
  Message as MessageIcon,
  Code as CodeIcon,
  Info as InfoIcon,
  CheckCircle as CompleteIcon,
  Error as ErrorIcon
} from '@mui/icons-material';
import axios from 'axios';
import { format } from 'date-fns';

const API_BASE = 'http://localhost:3333/api';

interface ClaudeSession {
  id: string;
  task_id: number;
  task_title?: string;
  project_id: string;
  status: 'idle' | 'initializing' | 'active' | 'paused' | 'completed' | 'error';
  working_dir: string;
  context?: string;
  messages?: any[];
  session_metadata?: {
    tools_used?: string[];
    error_count?: number;
    start_time?: string;
    end_time?: string;
  };
  summary?: string;
  statistics?: {
    messages_sent?: number;
    messages_received?: number;
    tool_calls?: number;
    duration_minutes?: number;
  };
  created_at: string;
  updated_at: string;
  completed_at?: string;
}

interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

function TabPanel(props: TabPanelProps) {
  const { children, value, index, ...other } = props;
  return (
    <div role="tabpanel" hidden={value !== index} {...other}>
      {value === index && <Box sx={{ p: 3 }}>{children}</Box>}
    </div>
  );
}

const getStatusColor = (status: ClaudeSession['status']) => {
  switch (status) {
    case 'idle': return 'default';
    case 'initializing': return 'info';
    case 'active': return 'success';
    case 'paused': return 'warning';
    case 'completed': return 'primary';
    case 'error': return 'error';
    default: return 'default';
  }
};

const getStatusIcon = (status: ClaudeSession['status']) => {
  switch (status) {
    case 'active': return <PlayIcon fontSize="small" />;
    case 'paused': return <PauseIcon fontSize="small" />;
    case 'completed': return <CompleteIcon fontSize="small" />;
    case 'error': return <ErrorIcon fontSize="small" />;
    default: return <InfoIcon fontSize="small" />;
  }
};

export default function ClaudeSessions() {
  const theme = useTheme();
  const [sessions, setSessions] = useState<ClaudeSession[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedSession, setSelectedSession] = useState<ClaudeSession | null>(null);
  const [detailsOpen, setDetailsOpen] = useState(false);
  const [tabValue, setTabValue] = useState(0);

  const fetchSessions = async () => {
    try {
      setLoading(true);
      // Get active project first
      const projectRes = await axios.get(`${API_BASE}/projects/active`);
      if (projectRes.data) {
        // Fetch sessions for the active project
        const sessionsRes = await axios.get(`${API_BASE}/projects/${projectRes.data.id}/sessions`);
        setSessions(sessionsRes.data);
      }
    } catch (error) {
      console.error('Error fetching sessions:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchSessions();
    
    // Listen for session status changes
    const handleSessionChange = () => {
      fetchSessions();
    };
    window.addEventListener('session-status-changed', handleSessionChange);
    
    // Refresh every 5 seconds for active sessions
    const interval = setInterval(() => {
      if (sessions.some(s => s.status === 'active' || s.status === 'initializing')) {
        fetchSessions();
      }
    }, 5000);
    
    return () => {
      clearInterval(interval);
      window.removeEventListener('session-status-changed', handleSessionChange);
    };
  }, []);

  const handleLaunchSession = async (taskId: number) => {
    try {
      await axios.post(`${API_BASE}/sessions/launch`, { task_id: taskId });
      fetchSessions();
    } catch (error) {
      console.error('Error launching session:', error);
    }
  };

  const handlePauseSession = async (taskId: number) => {
    try {
      await axios.post(`${API_BASE}/sessions/${taskId}/pause`);
      fetchSessions();
    } catch (error) {
      console.error('Error pausing session:', error);
    }
  };

  const handleResumeSession = async (taskId: number) => {
    try {
      await axios.post(`${API_BASE}/sessions/${taskId}/resume`);
      fetchSessions();
    } catch (error) {
      console.error('Error resuming session:', error);
    }
  };

  const handleCompleteSession = async (taskId: number) => {
    try {
      await axios.post(`${API_BASE}/sessions/${taskId}/complete`);
      fetchSessions();
    } catch (error) {
      console.error('Error completing session:', error);
    }
  };

  const openDetails = (session: ClaudeSession) => {
    setSelectedSession(session);
    setDetailsOpen(true);
    setTabValue(0);
  };

  const activeSessions = sessions.filter(s => s.status === 'active' || s.status === 'initializing');
  const completedSessions = sessions.filter(s => s.status === 'completed');

  return (
    <Container maxWidth="xl" sx={{ py: 4 }}>
      {/* Header Section */}
      <Box sx={{ mb: 5 }}>
        <Box display="flex" justifyContent="space-between" alignItems="flex-start" mb={2}>
          <Box>
            <Typography
              variant="h3"
              component="h1"
              sx={{
                fontWeight: 700,
                background: `linear-gradient(135deg, ${theme.palette.primary.main}, ${theme.palette.primary.light})`,
                WebkitBackgroundClip: 'text',
                WebkitTextFillColor: 'transparent',
                mb: 1,
              }}
            >
              Claude Sessions
            </Typography>
            <Typography
              variant="body1"
              sx={{
                color: alpha(theme.palette.text.secondary, 0.8),
                maxWidth: '600px',
              }}
            >
              Monitor and manage Claude Code autonomous sessions for your tasks
            </Typography>
          </Box>
          <Button
            variant="contained"
            startIcon={<RefreshIcon />}
            onClick={fetchSessions}
            sx={{
              background: `linear-gradient(135deg, ${theme.palette.primary.main}, ${theme.palette.primary.dark})`,
              color: '#fff',
              fontWeight: 600,
              textTransform: 'none',
              px: 3,
              py: 1.5,
              borderRadius: 2,
              boxShadow: `0 4px 12px ${alpha(theme.palette.primary.main, 0.3)}`,
              transition: 'all 0.3s ease',
              '&:hover': {
                background: `linear-gradient(135deg, ${theme.palette.primary.dark}, ${theme.palette.primary.main})`,
                transform: 'translateY(-2px)',
                boxShadow: `0 6px 20px ${alpha(theme.palette.primary.main, 0.4)}`,
              },
            }}
          >
            Refresh
          </Button>
        </Box>
      </Box>

      {/* Active Sessions Summary */}
      {activeSessions.length > 0 && (
        <Alert
          severity="info"
          sx={{
            mb: 3,
            backgroundColor: alpha(theme.palette.info.main, 0.1),
            border: `1px solid ${alpha(theme.palette.info.main, 0.3)}`,
            borderRadius: 2,
            '& .MuiAlert-icon': { color: theme.palette.info.main },
          }}
        >
          {activeSessions.length} active session{activeSessions.length > 1 ? 's' : ''} running
        </Alert>
      )}

      {/* Statistics Cards */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        {[
          { label: 'Total Sessions', value: sessions.length, color: theme.palette.primary.main, icon: <HistoryIcon /> },
          { label: 'Active', value: activeSessions.length, color: theme.palette.success.main, icon: <PlayIcon /> },
          { label: 'Completed', value: completedSessions.length, color: theme.palette.info.main, icon: <CompleteIcon /> },
          { label: 'With Errors', value: sessions.filter(s => s.status === 'error').length, color: theme.palette.error.main, icon: <ErrorIcon /> },
        ].map((stat, index) => (
          <Grid item xs={12} sm={6} md={3} key={index}>
            <Paper
              sx={{
                p: 2.5,
                borderRadius: 2,
                background: `linear-gradient(145deg, ${alpha(stat.color, 0.05)}, ${alpha(stat.color, 0.02)})`,
                border: `1px solid ${alpha(stat.color, 0.15)}`,
                transition: 'all 0.3s ease',
                '&:hover': {
                  transform: 'translateY(-4px)',
                  boxShadow: `0 8px 24px ${alpha(stat.color, 0.2)}`,
                  border: `1px solid ${alpha(stat.color, 0.3)}`,
                },
              }}
            >
              <Stack direction="row" alignItems="center" spacing={2}>
                <Box
                  sx={{
                    p: 1.5,
                    borderRadius: 2,
                    background: `linear-gradient(135deg, ${alpha(stat.color, 0.2)}, ${alpha(stat.color, 0.1)})`,
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                  }}
                >
                  {React.cloneElement(stat.icon, { sx: { color: stat.color, fontSize: 28 } })}
                </Box>
                <Box sx={{ flex: 1 }}>
                  <Typography
                    variant="body2"
                    sx={{
                      color: alpha(theme.palette.text.secondary, 0.7),
                      fontWeight: 500,
                      mb: 0.5,
                    }}
                  >
                    {stat.label}
                  </Typography>
                  <Typography
                    variant="h4"
                    sx={{
                      fontWeight: 700,
                      color: stat.color,
                    }}
                  >
                    {stat.value}
                  </Typography>
                </Box>
              </Stack>
            </Paper>
          </Grid>
        ))}
      </Grid>

      {/* Sessions Table */}
      <TableContainer
        component={Paper}
        sx={{
          borderRadius: 2,
          background: alpha(theme.palette.background.paper, 0.6),
          border: `1px solid ${alpha(theme.palette.divider, 0.1)}`,
          overflow: 'hidden',
        }}
      >
        {loading && <LinearProgress sx={{ backgroundColor: alpha(theme.palette.primary.main, 0.1) }} />}
        <Table>
          <TableHead>
            <TableRow
              sx={{
                background: `linear-gradient(135deg, ${alpha(theme.palette.primary.main, 0.08)}, ${alpha(theme.palette.primary.main, 0.02)})`,
              }}
            >
              <TableCell sx={{ fontWeight: 600, color: theme.palette.text.primary }}>Task</TableCell>
              <TableCell sx={{ fontWeight: 600, color: theme.palette.text.primary }}>Status</TableCell>
              <TableCell sx={{ fontWeight: 600, color: theme.palette.text.primary }}>Working Directory</TableCell>
              <TableCell sx={{ fontWeight: 600, color: theme.palette.text.primary }}>Messages</TableCell>
              <TableCell sx={{ fontWeight: 600, color: theme.palette.text.primary }}>Duration</TableCell>
              <TableCell sx={{ fontWeight: 600, color: theme.palette.text.primary }}>Started</TableCell>
              <TableCell align="right" sx={{ fontWeight: 600, color: theme.palette.text.primary }}>Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {sessions.length === 0 ? (
              <TableRow>
                <TableCell colSpan={7} align="center">
                  <Typography variant="body2" color="textSecondary" sx={{ py: 3 }}>
                    No Claude sessions found
                  </Typography>
                </TableCell>
              </TableRow>
            ) : (
              sessions.map((session) => (
                <TableRow
                  key={session.id}
                  sx={{
                    cursor: 'pointer',
                    transition: 'all 0.2s ease',
                    '&:hover': {
                      backgroundColor: alpha(theme.palette.primary.main, 0.04),
                    },
                  }}
                >
                  <TableCell>
                    <Typography variant="body2">
                      {session.task_title || `Task #${session.task_id}`}
                    </Typography>
                  </TableCell>
                  <TableCell>
                    <Chip 
                      label={session.status}
                      color={getStatusColor(session.status)}
                      size="small"
                      icon={getStatusIcon(session.status)}
                    />
                  </TableCell>
                  <TableCell>
                    <Typography variant="body2" sx={{ fontFamily: 'monospace', fontSize: '0.8rem' }}>
                      {session.working_dir.split('/').slice(-2).join('/')}
                    </Typography>
                  </TableCell>
                  <TableCell>
                    {session.statistics?.messages_sent || 0} / {session.statistics?.messages_received || 0}
                  </TableCell>
                  <TableCell>
                    {session.statistics?.duration_minutes 
                      ? `${session.statistics.duration_minutes} min`
                      : '-'}
                  </TableCell>
                  <TableCell>
                    {format(new Date(session.created_at), 'MMM dd HH:mm')}
                  </TableCell>
                  <TableCell align="right">
                    <Box sx={{ display: 'flex', gap: 1, justifyContent: 'flex-end' }}>
                      {session.status === 'idle' && (
                        <IconButton 
                          size="small" 
                          color="primary"
                          onClick={() => handleLaunchSession(session.task_id)}
                          title="Launch Session"
                        >
                          <PlayIcon />
                        </IconButton>
                      )}
                      {session.status === 'active' && (
                        <IconButton 
                          size="small" 
                          color="warning"
                          onClick={() => handlePauseSession(session.task_id)}
                          title="Pause Session"
                        >
                          <PauseIcon />
                        </IconButton>
                      )}
                      {session.status === 'paused' && (
                        <IconButton 
                          size="small" 
                          color="success"
                          onClick={() => handleResumeSession(session.task_id)}
                          title="Resume Session"
                        >
                          <PlayIcon />
                        </IconButton>
                      )}
                      {(session.status === 'active' || session.status === 'paused') && (
                        <IconButton 
                          size="small" 
                          color="error"
                          onClick={() => handleCompleteSession(session.task_id)}
                          title="Complete Session"
                        >
                          <StopIcon />
                        </IconButton>
                      )}
                      <IconButton 
                        size="small"
                        onClick={() => openDetails(session)}
                        title="View Details"
                      >
                        <HistoryIcon />
                      </IconButton>
                    </Box>
                  </TableCell>
                </TableRow>
              ))
            )}
          </TableBody>
        </Table>
      </TableContainer>

      {/* Session Details Dialog */}
      <Dialog 
        open={detailsOpen} 
        onClose={() => setDetailsOpen(false)}
        maxWidth="lg"
        fullWidth
      >
        {selectedSession && (
          <>
            <DialogTitle>
              Session Details - {selectedSession.task_title || `Task #${selectedSession.task_id}`}
              <Chip 
                label={selectedSession.status}
                color={getStatusColor(selectedSession.status)}
                size="small"
                sx={{ ml: 2 }}
              />
            </DialogTitle>
            <DialogContent>
              <Tabs value={tabValue} onChange={(_, v) => setTabValue(v)}>
                <Tab label="Overview" icon={<InfoIcon />} iconPosition="start" />
                <Tab label="Messages" icon={<MessageIcon />} iconPosition="start" />
                <Tab label="Tools Used" icon={<CodeIcon />} iconPosition="start" />
                <Tab label="Terminal Output" icon={<TerminalIcon />} iconPosition="start" />
              </Tabs>

              <TabPanel value={tabValue} index={0}>
                <Grid container spacing={2}>
                  <Grid item xs={6}>
                    <Typography variant="subtitle2" color="textSecondary">Session ID</Typography>
                    <Typography variant="body1" sx={{ fontFamily: 'monospace', mb: 2 }}>
                      {selectedSession.id}
                    </Typography>
                  </Grid>
                  <Grid item xs={6}>
                    <Typography variant="subtitle2" color="textSecondary">Working Directory</Typography>
                    <Typography variant="body1" sx={{ fontFamily: 'monospace', mb: 2 }}>
                      {selectedSession.working_dir}
                    </Typography>
                  </Grid>
                  <Grid item xs={12}>
                    <Typography variant="subtitle2" color="textSecondary">Context</Typography>
                    <Paper sx={{ p: 2, bgcolor: 'grey.50' }}>
                      <Typography variant="body2" sx={{ whiteSpace: 'pre-wrap' }}>
                        {selectedSession.context || 'No context provided'}
                      </Typography>
                    </Paper>
                  </Grid>
                  {selectedSession.summary && (
                    <Grid item xs={12}>
                      <Typography variant="subtitle2" color="textSecondary">Summary</Typography>
                      <Typography variant="body2">
                        {selectedSession.summary}
                      </Typography>
                    </Grid>
                  )}
                </Grid>
              </TabPanel>

              <TabPanel value={tabValue} index={1}>
                <List sx={{ maxHeight: '600px', overflow: 'auto' }}>
                  {selectedSession.messages?.length ? (
                    selectedSession.messages.map((msg, idx) => (
                      <React.Fragment key={idx}>
                        <ListItem
                          alignItems="flex-start"
                          sx={{
                            flexDirection: 'column',
                            alignItems: 'stretch',
                            py: 2,
                            gap: 1,
                          }}
                        >
                          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                            <Box sx={{ fontSize: '1.5rem' }}>
                              {msg.role === 'user' ? '👤' : '🤖'}
                            </Box>
                            <Typography
                              variant="subtitle2"
                              sx={{
                                fontWeight: 600,
                                color: msg.role === 'user' ? theme.palette.primary.main : theme.palette.success.main
                              }}
                            >
                              {msg.role === 'user' ? 'User' : 'Claude'}
                            </Typography>
                          </Box>
                          <Paper
                            sx={{
                              p: 2,
                              bgcolor: msg.role === 'user'
                                ? alpha(theme.palette.primary.main, 0.05)
                                : alpha(theme.palette.success.main, 0.05),
                              border: `1px solid ${
                                msg.role === 'user'
                                  ? alpha(theme.palette.primary.main, 0.2)
                                  : alpha(theme.palette.success.main, 0.2)
                              }`,
                              borderRadius: 2,
                            }}
                          >
                            <Box
                              sx={{
                                whiteSpace: 'pre-wrap',
                                wordBreak: 'break-word',
                                overflowWrap: 'break-word',
                                fontSize: '0.9rem',
                                lineHeight: 1.6,
                              }}
                            >
                              {(() => {
                                const content = msg.content;

                                // If content is a simple string
                                if (typeof content === 'string') {
                                  return content;
                                }

                                // If content is an array (Claude API format)
                                if (Array.isArray(content)) {
                                  return content.map((block: any, i: number) => {
                                    if (block.type === 'text') {
                                      return <div key={i} style={{ marginBottom: '8px' }}>{block.text}</div>;
                                    }
                                    if (block.type === 'tool_use') {
                                      return (
                                        <Box key={i} sx={{ mt: 1, p: 1.5, bgcolor: alpha(theme.palette.info.main, 0.08), borderRadius: 1, border: `1px solid ${alpha(theme.palette.info.main, 0.2)}` }}>
                                          <Typography variant="caption" sx={{ fontWeight: 600, color: theme.palette.info.main, display: 'block', mb: 0.5 }}>
                                            🔧 Tool: {block.name}
                                          </Typography>
                                          <pre style={{ margin: 0, fontSize: '0.75rem', whiteSpace: 'pre-wrap', wordBreak: 'break-word', overflow: 'auto' }}>
                                            {JSON.stringify(block.input, null, 2)}
                                          </pre>
                                        </Box>
                                      );
                                    }
                                    if (block.type === 'tool_result') {
                                      const resultContent = typeof block.content === 'string'
                                        ? block.content
                                        : Array.isArray(block.content) && block.content[0]?.type === 'text'
                                        ? block.content[0].text
                                        : JSON.stringify(block.content, null, 2);

                                      return (
                                        <Box key={i} sx={{ mt: 1, p: 1.5, bgcolor: alpha(theme.palette.success.main, 0.08), borderRadius: 1, border: `1px solid ${alpha(theme.palette.success.main, 0.2)}` }}>
                                          <Typography variant="caption" sx={{ fontWeight: 600, color: theme.palette.success.main, display: 'block', mb: 0.5 }}>
                                            ✅ Tool Result
                                          </Typography>
                                          <div style={{ fontSize: '0.85rem', whiteSpace: 'pre-wrap', wordBreak: 'break-word', overflow: 'auto', maxHeight: '400px' }}>
                                            {resultContent}
                                          </div>
                                        </Box>
                                      );
                                    }
                                    // Unknown block type
                                    return <div key={i} style={{ marginTop: '8px' }}>{JSON.stringify(block, null, 2)}</div>;
                                  });
                                }

                                // If content has a 'text' property
                                if (content && typeof content === 'object' && 'text' in content) {
                                  return (content as any).text;
                                }

                                // Fallback: stringify the entire object
                                return <pre style={{ margin: 0, whiteSpace: 'pre-wrap', wordBreak: 'break-word' }}>{JSON.stringify(content, null, 2)}</pre>;
                              })()}
                            </Box>
                          </Paper>
                        </ListItem>
                        {idx < selectedSession.messages!.length - 1 && <Divider sx={{ my: 1 }} />}
                      </React.Fragment>
                    ))
                  ) : (
                    <Typography color="textSecondary" align="center" sx={{ py: 4 }}>
                      No messages yet
                    </Typography>
                  )}
                </List>
              </TabPanel>

              <TabPanel value={tabValue} index={2}>
                {selectedSession.session_metadata?.tools_used?.length ? (
                  <List>
                    {selectedSession.session_metadata.tools_used.map((tool, idx) => (
                      <ListItem key={idx}>
                        <ListItemIcon>
                          <CodeIcon />
                        </ListItemIcon>
                        <ListItemText primary={tool} />
                      </ListItem>
                    ))}
                  </List>
                ) : (
                  <Typography color="textSecondary" align="center">
                    No tools used yet
                  </Typography>
                )}
              </TabPanel>

              <TabPanel value={tabValue} index={3}>
                <Paper sx={{ p: 2, bgcolor: 'grey.900', color: 'grey.50' }}>
                  <Typography variant="body2" sx={{ fontFamily: 'monospace', whiteSpace: 'pre-wrap' }}>
                    $ claude --working-dir '{selectedSession.working_dir}' \{'\n'}
                      --context-file '.claude/task-{selectedSession.task_id}-context.md' \{'\n'}
                      --task-id {selectedSession.task_id} \{'\n'}
                      --mcp-server http://localhost:3335{'\n'}
                    {'\n'}
                    [Terminal output will appear here when session is active]
                  </Typography>
                </Paper>
              </TabPanel>
            </DialogContent>
          </>
        )}
      </Dialog>
    </Container>
  );
}