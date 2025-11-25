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
} from '@mui/material';
import {
  ExpandMore as ExpandMoreIcon,
  Computer as ComputerIcon,
  Stop as StopIcon,
  Speed as SpeedIcon,
  Memory as MemoryIcon,
} from '@mui/icons-material';
import { useLocation, useNavigate } from 'react-router-dom';
import axios from 'axios';
import ClaudeCodeSessionsView from '../components/sessions/ClaudeCodeSessionsView';
import TaskSessionsView from '../components/sessions/TaskSessionsView';

const API_BASE = 'http://localhost:3333/api/claude-sessions';

interface ActiveSession {
  pid: string;
  cpu: string;
  mem: string;
  command: string;
}

type TabValue = 'claude-code' | 'tasks';

const Sessions: React.FC = () => {
  const theme = useTheme();
  const location = useLocation();
  const navigate = useNavigate();

  const [currentTab, setCurrentTab] = useState<TabValue>('claude-code');
  const [processMonitorExpanded, setProcessMonitorExpanded] = useState(false);
  const [activeSessions, setActiveSessions] = useState<ActiveSession[]>([]);

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
          {activeSessions.length === 0 ? (
            <Typography variant="body2" color="text.secondary" align="center" sx={{ py: 2 }}>
              No active Claude Code processes running
            </Typography>
          ) : (
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
                              PID: {session.pid}
                            </Typography>
                            <Stack direction="row" spacing={1} mt={0.5}>
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
                      <Paper
                        sx={{
                          p: 1,
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
                            fontSize: '0.65rem',
                            color: theme.palette.success.main,
                            display: 'block',
                            overflow: 'hidden',
                            textOverflow: 'ellipsis',
                            whiteSpace: 'nowrap',
                          }}
                        >
                          {session.command}
                        </Typography>
                      </Paper>
                    </CardContent>
                  </Card>
                </Grid>
              ))}
            </Grid>
          )}
        </AccordionDetails>
      </Accordion>

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
    </Container>
  );
};

export default Sessions;
