import React, { useState, useEffect } from 'react';
import {
  Box,
  Container,
  Tabs,
  Tab,
  Typography,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Grid,
  Chip,
  alpha,
  useTheme,
  Card,
  CardContent,
  IconButton,
  Tooltip,
  Stack,
  Paper,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Divider,
  List,
  ListItem,
  ListItemText,
  CircularProgress,
} from '@mui/material';
import {
  ExpandMore as ExpandMoreIcon,
  Computer as ComputerIcon,
  Stop as StopIcon,
  Speed as SpeedIcon,
  Memory as MemoryIcon,
  Info as InfoIcon,
  Chat as ChatIcon,
  Code as CodeIcon,
  Folder as FolderIcon,
} from '@mui/icons-material';
import { useLocation, useNavigate } from 'react-router-dom';
import axios from 'axios';
import { format } from 'date-fns';
import ClaudeCodeSessionsView from '../components/sessions/ClaudeCodeSessionsView';
import TaskSessionsView from '../components/sessions/TaskSessionsView';

const API_BASE = 'http://localhost:3333/api/claude-sessions';

interface ActiveSession {
  pid: string;
  cpu: string;
  mem: string;
  command: string;
  working_dir?: string;
  project_name?: string;
  session_id?: string;
  project_dir?: string;
  started?: string;
  task_id?: number;
  is_embedded?: boolean;
}

interface SessionDetails {
  session_id: string;
  file_path: string;
  file_size: number;
  created_at: string | null;
  last_timestamp: string | null;
  cwd: string | null;
  git_branch: string | null;
  claude_version: string | null;
  message_count: number;
  user_messages: number;
  assistant_messages: number;
  tool_calls: Record<string, number>;
  commands_used: string[];
  files_modified: string[];
  errors: Array<{ timestamp: string; content: string }>;
  messages?: Array<{
    type: string;
    timestamp: string;
    content: string;
    uuid: string;
    parent_uuid: string | null;
  }>;
}

type TabValue = 'claude-code' | 'tasks';

const Sessions: React.FC = () => {
  const theme = useTheme();
  const location = useLocation();
  const navigate = useNavigate();

  const [currentTab, setCurrentTab] = useState<TabValue>('claude-code');
  const [processMonitorExpanded, setProcessMonitorExpanded] = useState(false);
  const [activeSessions, setActiveSessions] = useState<ActiveSession[]>([]);
  const [detailsOpen, setDetailsOpen] = useState(false);
  const [selectedSession, setSelectedSession] = useState<SessionDetails | null>(null);
  const [loadingDetails, setLoadingDetails] = useState(false);

  // URL-based tab state management
  useEffect(() => {
    const path = location.pathname;

    if (path === '/sessions' || path === '/sessions/') {
      // Default to Claude Code Sessions
      navigate('/sessions/claude-code', { replace: true });
      setCurrentTab('claude-code');
    } else if (path.includes('/claude-code')) {
      setCurrentTab('claude-code');
    } else if (path.includes('/tasks')) {
      setCurrentTab('tasks');
    }
  }, [location.pathname, navigate]);

  // Fetch active sessions (only when process monitor is expanded)
  const fetchActiveSessions = async () => {
    try {
      const response = await axios.get(`${API_BASE}/active-sessions`);
      setActiveSessions(response.data.active_sessions || []);
    } catch (error) {
      console.error('Error fetching active sessions:', error);
    }
  };

  // Poll active sessions only when expanded
  useEffect(() => {
    if (processMonitorExpanded) {
      fetchActiveSessions(); // Fetch immediately
      const interval = setInterval(fetchActiveSessions, 5000);
      return () => clearInterval(interval);
    }
  }, [processMonitorExpanded]);

  // Tab change handler
  const handleTabChange = (_event: React.SyntheticEvent, newValue: TabValue) => {
    setCurrentTab(newValue);
    navigate(`/sessions/${newValue}`, { replace: true });
  };

  // Kill session handler
  const killSession = async (pid: string) => {
    if (!window.confirm(`Terminate Claude session (PID: ${pid})?`)) return;

    try {
      await axios.post(`${API_BASE}/sessions/${pid}/kill`);
      await fetchActiveSessions();
      alert('Session terminated successfully');
    } catch (error: any) {
      console.error('Error killing session:', error);
      alert(`Failed to kill session: ${error.response?.data?.detail || error.message}`);
    }
  };

  // Open session details handler
  const openSessionDetails = async (session: ActiveSession) => {
    if (!session.session_id || !session.project_dir) {
      alert('Session details not available');
      return;
    }

    // Embedded sessions (hook-*) don't have session files - show info from active session
    if (session.is_embedded || session.session_id.startsWith('hook-')) {
      alert(`Embedded Session (${session.session_id})\n\nPID: ${session.pid}\nProject: ${session.project_name || 'Unknown'}\nWorking Directory: ${session.working_dir || 'Unknown'}\n\nEmbedded sessions run within hooks and don't have persistent session files.`);
      return;
    }

    setLoadingDetails(true);
    setDetailsOpen(true);

    try {
      const response = await axios.get(
        `${API_BASE}/sessions/${session.session_id}?project_dir=${encodeURIComponent(session.project_dir)}&include_messages=true`
      );
      setSelectedSession(response.data.session);
    } catch (error: any) {
      console.error('Error fetching session details:', error);
      alert(`Failed to load session details: ${error.response?.data?.detail || error.message}`);
      setDetailsOpen(false);
    } finally {
      setLoadingDetails(false);
    }
  };

  const tabAccentColor = currentTab === 'claude-code' ? '#6366f1' : theme.palette.primary.main;

  return (
    <Container maxWidth="xl" sx={{ py: 4 }}>
      {/* Page Header */}
      <Box sx={{ mb: 4 }}>
        <Typography
          variant="h3"
          component="h1"
          sx={{
            fontWeight: 700,
            background: `linear-gradient(135deg, ${tabAccentColor}, ${alpha(tabAccentColor, 0.7)})`,
            WebkitBackgroundClip: 'text',
            WebkitTextFillColor: 'transparent',
            mb: 1,
          }}
        >
          Sessions
        </Typography>
        <Typography
          variant="body1"
          sx={{
            color: alpha(theme.palette.text.secondary, 0.8),
            maxWidth: '600px',
          }}
        >
          Monitor and manage Claude Code sessions and task-based sessions from a unified interface
        </Typography>
      </Box>

      {/* Tab Navigation */}
      <Tabs
        value={currentTab}
        onChange={handleTabChange}
        variant="scrollable"
        scrollButtons="auto"
        aria-label="Session type navigation"
        sx={{
          mb: 3,
          borderBottom: 1,
          borderColor: 'divider',
          '& .MuiTab-root': {
            minWidth: { xs: 120, md: 160 },
            fontSize: { xs: '0.875rem', md: '1rem' },
            fontWeight: 600,
            textTransform: 'none',
            transition: 'all 0.3s ease',
            '&:hover': {
              color: tabAccentColor,
            },
          },
          '& .Mui-selected': {
            color: `${tabAccentColor} !important`,
          },
          '& .MuiTabs-indicator': {
            backgroundColor: tabAccentColor,
            height: 3,
            borderRadius: '3px 3px 0 0',
          },
        }}
      >
        <Tab
          label="Claude Code Sessions"
          value="claude-code"
          id="tab-claude-code"
          aria-controls="tabpanel-claude-code"
        />
        <Tab
          label="Task Sessions"
          value="tasks"
          id="tab-tasks"
          aria-controls="tabpanel-tasks"
        />
      </Tabs>

      {/* Collapsible Process Monitor */}
      <Accordion
        expanded={processMonitorExpanded}
        onChange={() => setProcessMonitorExpanded(!processMonitorExpanded)}
        sx={{
          mb: 3,
          borderRadius: 2,
          '&:before': {
            display: 'none',
          },
          boxShadow: processMonitorExpanded
            ? `0 4px 12px ${alpha(theme.palette.primary.main, 0.1)}`
            : 'none',
          border: `1px solid ${alpha(theme.palette.divider, 0.1)}`,
        }}
        aria-label="Active process monitoring"
      >
        <AccordionSummary
          expandIcon={<ExpandMoreIcon />}
          aria-expanded={processMonitorExpanded}
          aria-controls="process-monitor-content"
          sx={{
            bgcolor: alpha(theme.palette.background.paper, 0.6),
            '&:hover': {
              bgcolor: alpha(theme.palette.primary.main, 0.04),
            },
          }}
        >
          <Stack direction="row" alignItems="center" spacing={1}>
            <ComputerIcon sx={{ color: theme.palette.primary.main }} />
            <Typography fontWeight={600}>System Processes</Typography>
            {activeSessions.length > 0 && (
              <Chip
                size="small"
                label={activeSessions.length}
                sx={{
                  bgcolor: alpha(theme.palette.success.main, 0.1),
                  color: theme.palette.success.main,
                  fontWeight: 600,
                }}
              />
            )}
          </Stack>
        </AccordionSummary>
        <AccordionDetails id="process-monitor-content" sx={{ p: 2 }}>
          {activeSessions.length > 0 ? (
            <Grid container spacing={2}>
              {activeSessions.map((session) => (
                <Grid item xs={12} md={6} lg={4} key={session.pid}>
                  <Card
                    sx={{
                      bgcolor: theme.palette.mode === 'dark' ? '#1e293b' : alpha(theme.palette.success.main, 0.02),
                      border: '1px solid',
                      borderColor: alpha(theme.palette.success.main, 0.2),
                      borderRadius: 2,
                      transition: 'all 0.3s ease',
                      '&:hover': {
                        transform: 'translateY(-2px)',
                        boxShadow: `0 8px 16px ${alpha(theme.palette.success.main, 0.2)}`,
                        borderColor: alpha(theme.palette.success.main, 0.4),
                      },
                    }}
                  >
                    <CardContent>
                      <Box display="flex" alignItems="center" justifyContent="space-between" mb={2}>
                        <Box display="flex" alignItems="center" gap={1.5}>
                          <Box
                            sx={{
                              width: 40,
                              height: 40,
                              borderRadius: 1.5,
                              display: 'flex',
                              alignItems: 'center',
                              justifyContent: 'center',
                              bgcolor: alpha(theme.palette.success.main, 0.1),
                              border: '1px solid',
                              borderColor: alpha(theme.palette.success.main, 0.2),
                            }}
                          >
                            <ComputerIcon sx={{ color: theme.palette.success.main, fontSize: 24 }} />
                          </Box>
                          <Box>
                            <Typography variant="body2" fontWeight={600}>
                              {session.is_embedded ? (
                                <>Embedded Session {session.task_id ? `(Task #${session.task_id})` : ''}</>
                              ) : (
                                <>PID: {session.pid}</>
                              )}
                            </Typography>
                            <Stack direction="row" spacing={1} mt={0.5}>
                              {session.is_embedded ? (
                                <Chip
                                  label="Embedded"
                                  size="small"
                                  sx={{
                                    height: 20,
                                    fontSize: '0.65rem',
                                    bgcolor: alpha(theme.palette.info.main, 0.1),
                                    color: theme.palette.info.main,
                                  }}
                                />
                              ) : (
                                <>
                                  <Chip
                                    label={`CPU: ${session.cpu}%`}
                                    size="small"
                                    icon={<SpeedIcon sx={{ fontSize: 12 }} />}
                                    sx={{
                                      height: 20,
                                      fontSize: '0.65rem',
                                      bgcolor: alpha(theme.palette.success.main, 0.1),
                                      color: theme.palette.success.main,
                                      '& .MuiChip-icon': {
                                        color: theme.palette.success.main,
                                      },
                                    }}
                                  />
                                  <Chip
                                    label={`Mem: ${session.mem}%`}
                                    size="small"
                                    icon={<MemoryIcon sx={{ fontSize: 12 }} />}
                                    sx={{
                                      height: 20,
                                      fontSize: '0.65rem',
                                      bgcolor: alpha(theme.palette.success.main, 0.1),
                                      color: theme.palette.success.main,
                                      '& .MuiChip-icon': {
                                        color: theme.palette.success.main,
                                      },
                                    }}
                                  />
                                </>
                              )}
                            </Stack>
                          </Box>
                        </Box>
                        <Tooltip title="Terminate Session">
                          <IconButton
                            size="small"
                            onClick={() => killSession(session.pid)}
                            sx={{
                              color: theme.palette.error.main,
                              '&:hover': {
                                bgcolor: alpha(theme.palette.error.main, 0.1),
                              },
                            }}
                          >
                            <StopIcon fontSize="small" />
                          </IconButton>
                        </Tooltip>
                      </Box>
                      {/* Project info */}
                      {session.project_name && (
                        <Paper
                          sx={{
                            p: 1,
                            mb: 1.5,
                            bgcolor: theme.palette.mode === 'dark' ? '#0f172a' : alpha(theme.palette.background.default, 0.5),
                            border: '1px solid',
                            borderColor: alpha(theme.palette.success.main, 0.2),
                            borderRadius: 1,
                          }}
                        >
                          <Typography
                            variant="caption"
                            sx={{
                              fontFamily: 'monospace',
                              fontSize: '0.7rem',
                              color: theme.palette.success.main,
                              display: 'flex',
                              alignItems: 'center',
                              gap: 0.5,
                            }}
                          >
                            <FolderIcon sx={{ fontSize: 14 }} />
                            {session.project_name}
                          </Typography>
                        </Paper>
                      )}
                      {/* View Details button */}
                      {session.session_id && session.project_dir && (
                        <Button
                          size="small"
                          variant="outlined"
                          startIcon={<InfoIcon />}
                          onClick={() => openSessionDetails(session)}
                          sx={{
                            fontSize: '0.7rem',
                            textTransform: 'none',
                            borderColor: alpha(theme.palette.success.main, 0.3),
                            color: theme.palette.success.main,
                            '&:hover': {
                              borderColor: theme.palette.success.main,
                              bgcolor: alpha(theme.palette.success.main, 0.1),
                            },
                          }}
                        >
                          View Details
                        </Button>
                      )}
                    </CardContent>
                  </Card>
                </Grid>
              ))}
            </Grid>
          ) : (
            <Paper
              sx={{
                p: 3,
                textAlign: 'center',
                bgcolor: theme.palette.mode === 'dark' ? '#1e293b' : alpha(theme.palette.background.paper, 0.7),
                border: '1px solid',
                borderColor: theme.palette.divider,
                borderRadius: 2,
              }}
            >
              <ComputerIcon sx={{ fontSize: 48, color: theme.palette.text.disabled, mb: 1 }} />
              <Typography color="text.secondary">No active Claude Code processes running</Typography>
            </Paper>
          )}
        </AccordionDetails>
      </Accordion>

      {/* Main content */}
      <Tabs
        value={currentTab}
        onChange={handleTabChange}
        aria-label="session tabs"
        sx={{
          mb: 3,
          '& .MuiTab-root': {
            textTransform: 'none',
            fontWeight: 500,
            minHeight: 44,
            px: 3,
          },
          '& .MuiTabs-indicator': {
            bgcolor: '#6366f1',
            height: 3,
            borderRadius: '3px 3px 0 0',
          },
        }}
      >
        <Tab
          label="Claude Code Sessions"
          value="claude-code"
          id="tab-claude-code"
          aria-controls="tabpanel-claude-code"
        />
        <Tab
          label="Task Sessions"
          value="tasks"
          id="tab-tasks"
          aria-controls="tabpanel-tasks"
        />
      </Tabs>

      {/* Tab Panels */}
      <Box
        role="tabpanel"
        hidden={currentTab !== 'claude-code'}
        id="tabpanel-claude-code"
        aria-labelledby="tab-claude-code"
      >
        {currentTab === 'claude-code' && <ClaudeCodeSessionsView />}
      </Box>

      <Box
        role="tabpanel"
        hidden={currentTab !== 'tasks'}
        id="tabpanel-tasks"
        aria-labelledby="tab-tasks"
      >
        {currentTab === 'tasks' && <TaskSessionsView />}
      </Box>

      {/* Session Details Dialog */}
      <Dialog
        open={detailsOpen}
        onClose={() => setDetailsOpen(false)}
        maxWidth="lg"
        fullWidth
        PaperProps={{
          sx: {
            bgcolor: theme.palette.mode === 'dark' ? '#1e293b' : 'background.paper',
            border: '1px solid',
            borderColor: theme.palette.mode === 'dark' ? '#334155' : alpha(theme.palette.divider, 0.1),
            borderRadius: 2,
          },
        }}
      >
        {loadingDetails ? (
          <Box display="flex" justifyContent="center" alignItems="center" minHeight="300px">
            <CircularProgress sx={{ color: '#6366f1' }} />
          </Box>
        ) : selectedSession && (
          <>
            <DialogTitle sx={{ borderBottom: '1px solid', borderColor: 'divider' }}>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <FolderIcon sx={{ color: theme.palette.success.main }} />
                <Typography variant="h6">
                  Active Session: {selectedSession.session_id.substring(0, 12)}...
                </Typography>
                <Chip
                  label="LIVE"
                  size="small"
                  sx={{
                    bgcolor: alpha(theme.palette.success.main, 0.1),
                    color: theme.palette.success.main,
                    fontWeight: 600,
                    animation: 'pulse 2s infinite',
                    '@keyframes pulse': {
                      '0%, 100%': { opacity: 1 },
                      '50%': { opacity: 0.6 },
                    },
                  }}
                />
              </Box>
            </DialogTitle>
            <DialogContent sx={{ pt: 3 }}>
              {/* Session Info */}
              <Grid container spacing={2} sx={{ mb: 3 }}>
                <Grid item xs={6} md={3}>
                  <Typography variant="caption" color="text.secondary">Working Directory</Typography>
                  <Typography variant="body2" sx={{ fontFamily: 'monospace', wordBreak: 'break-all' }}>
                    {selectedSession.cwd || 'N/A'}
                  </Typography>
                </Grid>
                <Grid item xs={6} md={3}>
                  <Typography variant="caption" color="text.secondary">Git Branch</Typography>
                  <Typography variant="body2">{selectedSession.git_branch || 'N/A'}</Typography>
                </Grid>
                <Grid item xs={6} md={3}>
                  <Typography variant="caption" color="text.secondary">Messages</Typography>
                  <Typography variant="body2">
                    {selectedSession.message_count} ({selectedSession.user_messages} user / {selectedSession.assistant_messages} assistant)
                  </Typography>
                </Grid>
                <Grid item xs={6} md={3}>
                  <Typography variant="caption" color="text.secondary">Claude Version</Typography>
                  <Typography variant="body2">{selectedSession.claude_version || 'N/A'}</Typography>
                </Grid>
              </Grid>

              <Divider sx={{ my: 2 }} />

              {/* Messages Section */}
              <Box sx={{ mb: 3 }}>
                <Typography variant="h6" sx={{ mb: 2, display: 'flex', alignItems: 'center', gap: 1 }}>
                  <ChatIcon sx={{ color: '#6366f1' }} />
                  Messages ({selectedSession.messages?.length || 0})
                </Typography>
                {selectedSession.messages && selectedSession.messages.length > 0 ? (
                  <List sx={{ maxHeight: 400, overflow: 'auto' }}>
                    {selectedSession.messages
                      .filter(msg => {
                        const content: any = msg.content;
                        if (typeof content === 'string') {
                          const trimmed = content.trim();
                          return trimmed && trimmed !== '...' && trimmed !== '…';
                        }
                        if (Array.isArray(content)) {
                          return (content as any[]).some((b: any) => b.type === 'text' && b.text?.trim());
                        }
                        return !!content;
                      })
                      .map((msg, idx) => (
                        <React.Fragment key={msg.uuid || idx}>
                          <ListItem
                            alignItems="flex-start"
                            sx={{
                              bgcolor: alpha(theme.palette.background.default, 0.3),
                              mb: 1,
                              borderRadius: 1,
                              borderLeft: `3px solid ${msg.type === 'user' ? theme.palette.primary.main : theme.palette.success.main}`,
                            }}
                          >
                            <ListItemText
                              primary={
                                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                                  <Typography variant="subtitle2">
                                    {msg.type === 'user' ? '👤 User' : '🤖 Assistant'}
                                  </Typography>
                                  <Typography variant="caption" color="text.secondary">
                                    {msg.timestamp ? format(new Date(msg.timestamp), 'HH:mm:ss') : ''}
                                  </Typography>
                                </Box>
                              }
                              secondary={
                                <Typography
                                  variant="body2"
                                  sx={{
                                    whiteSpace: 'pre-wrap',
                                    mt: 1,
                                    maxHeight: 200,
                                    overflow: 'auto',
                                    color: 'text.secondary',
                                  }}
                                >
                                  {(() => {
                                    const content: any = msg.content;
                                    if (typeof content === 'string') return content.trim();
                                    if (Array.isArray(content)) {
                                      return (content as any[])
                                        .filter((block: any) => block.type === 'text')
                                        .map((block: any) => block.text?.trim())
                                        .filter(Boolean)
                                        .join('\n');
                                    }
                                    return JSON.stringify(content, null, 2);
                                  })()}
                                </Typography>
                              }
                            />
                          </ListItem>
                        </React.Fragment>
                      ))}
                  </List>
                ) : (
                  <Typography color="text.secondary" align="center">
                    No messages available
                  </Typography>
                )}
              </Box>

              {/* Tools Used */}
              {Object.keys(selectedSession.tool_calls).length > 0 && (
                <Box sx={{ mb: 3 }}>
                  <Typography variant="h6" sx={{ mb: 2, display: 'flex', alignItems: 'center', gap: 1 }}>
                    <CodeIcon sx={{ color: '#6366f1' }} />
                    Tools Used ({Object.keys(selectedSession.tool_calls).length})
                  </Typography>
                  <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                    {Object.entries(selectedSession.tool_calls)
                      .sort(([, a], [, b]) => b - a)
                      .map(([tool, count]) => (
                        <Chip
                          key={tool}
                          label={`${tool}: ${count}`}
                          size="small"
                          sx={{
                            bgcolor: alpha('#6366f1', 0.1),
                            color: '#6366f1',
                          }}
                        />
                      ))}
                  </Box>
                </Box>
              )}
            </DialogContent>
            <DialogActions sx={{ borderTop: '1px solid', borderColor: 'divider', p: 2 }}>
              <Button
                onClick={() => setDetailsOpen(false)}
                variant="contained"
                sx={{
                  bgcolor: '#6366f1',
                  textTransform: 'none',
                  fontWeight: 600,
                  '&:hover': {
                    bgcolor: '#4f46e5',
                  },
                }}
              >
                Close
              </Button>
            </DialogActions>
          </>
        )}
      </Dialog>
    </Container>
  );
};

export default Sessions;
