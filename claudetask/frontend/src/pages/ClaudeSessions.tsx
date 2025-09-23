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
  Card,
  CardContent,
  Grid,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Divider,
  LinearProgress,
  Alert
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
    <Box>
      <Box sx={{ mb: 3, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <Typography variant="h4" component="h1">
          Claude Sessions
        </Typography>
        <Button
          variant="outlined"
          startIcon={<RefreshIcon />}
          onClick={fetchSessions}
        >
          Refresh
        </Button>
      </Box>

      {/* Active Sessions Summary */}
      {activeSessions.length > 0 && (
        <Alert severity="info" sx={{ mb: 2 }}>
          {activeSessions.length} active session{activeSessions.length > 1 ? 's' : ''} running
        </Alert>
      )}

      {/* Statistics Cards */}
      <Grid container spacing={2} sx={{ mb: 3 }}>
        <Grid item xs={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Total Sessions
              </Typography>
              <Typography variant="h5" component="div">
                {sessions.length}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Active
              </Typography>
              <Typography variant="h5" component="div" color="success.main">
                {activeSessions.length}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Completed
              </Typography>
              <Typography variant="h5" component="div" color="primary.main">
                {completedSessions.length}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                With Errors
              </Typography>
              <Typography variant="h5" component="div" color="error.main">
                {sessions.filter(s => s.status === 'error').length}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Sessions Table */}
      <TableContainer component={Paper}>
        {loading && <LinearProgress />}
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Task</TableCell>
              <TableCell>Status</TableCell>
              <TableCell>Working Directory</TableCell>
              <TableCell>Messages</TableCell>
              <TableCell>Duration</TableCell>
              <TableCell>Started</TableCell>
              <TableCell align="right">Actions</TableCell>
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
                <TableRow key={session.id} hover>
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
                <List>
                  {selectedSession.messages?.length ? (
                    selectedSession.messages.map((msg, idx) => (
                      <React.Fragment key={idx}>
                        <ListItem alignItems="flex-start">
                          <ListItemIcon>
                            {msg.role === 'user' ? '👤' : '🤖'}
                          </ListItemIcon>
                          <ListItemText
                            primary={msg.role === 'user' ? 'User' : 'Claude'}
                            secondary={
                              <Typography variant="body2" sx={{ whiteSpace: 'pre-wrap' }}>
                                {msg.content}
                              </Typography>
                            }
                          />
                        </ListItem>
                        {idx < selectedSession.messages!.length - 1 && <Divider />}
                      </React.Fragment>
                    ))
                  ) : (
                    <Typography color="textSecondary" align="center">
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
    </Box>
  );
}