import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Button,
  Grid,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Alert,
  Chip,
  CircularProgress,
  IconButton,
  Tooltip,
  ToggleButtonGroup,
  ToggleButton,
  Stack,
  Container,
  alpha,
  useTheme,
  Divider,
  Badge,
  InputAdornment,
  Paper,
  TextField,
  Tabs,
  Tab,
  List,
  ListItem,
  ListItemText,
} from '@mui/material';
import {
  Refresh as RefreshIcon,
  Search as SearchIcon,
  Info as InfoIcon,
  Message as MessageIcon,
  Code as CodeIcon,
  Error as ErrorIcon,
  Timeline as TimelineIcon,
  Stop as StopIcon,
  Terminal as TerminalIcon,
  Folder as FolderIcon,
  PlayArrow as PlayIcon,
  Computer as ComputerIcon,
  Storage as StorageIcon,
  Speed as SpeedIcon,
  CheckCircle as CheckCircleIcon,
  AccessTime as AccessTimeIcon,
  Memory as MemoryIcon,
} from '@mui/icons-material';
import axios from 'axios';
import { format } from 'date-fns';

const API_BASE = 'http://localhost:3333/api/claude-sessions';

interface ClaudeCodeProject {
  name: string;
  path: string;
  directory: string;
  sessions_count: number;
  last_modified: string;
}

interface ClaudeCodeSession {
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

interface SessionStatistics {
  total_sessions: number;
  total_messages: number;
  total_tool_calls: Record<string, number>;
  total_files_modified: number;
  total_errors: number;
  recent_sessions: ClaudeCodeSession[];
}

interface ActiveSession {
  pid: string;
  cpu: string;
  mem: string;
  command: string;
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

type FilterType = 'all' | 'active' | 'completed' | 'errors';

export default function ClaudeCodeSessions() {
  const theme = useTheme();
  const [projects, setProjects] = useState<ClaudeCodeProject[]>([]);
  const [selectedProject, setSelectedProject] = useState<ClaudeCodeProject | null>(null);
  const [sessions, setSessions] = useState<ClaudeCodeSession[]>([]);
  const [statistics, setStatistics] = useState<SessionStatistics | null>(null);
  const [loading, setLoading] = useState(true);
  const [selectedSession, setSelectedSession] = useState<ClaudeCodeSession | null>(null);
  const [detailsOpen, setDetailsOpen] = useState(false);
  const [tabValue, setTabValue] = useState(0);
  const [searchQuery, setSearchQuery] = useState('');
  const [activeSessions, setActiveSessions] = useState<ActiveSession[]>([]);
  const [activeFilter, setActiveFilter] = useState<FilterType>('all');

  const fetchProjects = async () => {
    try {
      setLoading(true);
      const response = await axios.get(`${API_BASE}/projects`);
      setProjects(response.data.projects);
      if (response.data.projects.length > 0 && !selectedProject) {
        setSelectedProject(response.data.projects[0]);
      }
    } catch (error) {
      console.error('Error fetching projects:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchSessions = async (projectName: string, projectDir: string) => {
    try {
      setLoading(true);
      const response = await axios.get(
        `${API_BASE}/projects/${encodeURIComponent(projectName)}/sessions?project_dir=${encodeURIComponent(projectDir)}`
      );
      setSessions(response.data.sessions);
    } catch (error) {
      console.error('Error fetching sessions:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchStatistics = async (projectName?: string) => {
    try {
      const url = projectName
        ? `${API_BASE}/statistics?project_name=${projectName}`
        : `${API_BASE}/statistics`;
      const response = await axios.get(url);
      setStatistics(response.data.statistics);
    } catch (error) {
      console.error('Error fetching statistics:', error);
    }
  };

  const fetchActiveSessions = async () => {
    try {
      const response = await axios.get(`${API_BASE}/active-sessions`);
      setActiveSessions(response.data.active_sessions);
    } catch (error) {
      console.error('Error fetching active sessions:', error);
    }
  };

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

  const openDetails = async (session: ClaudeCodeSession) => {
    try {
      if (!selectedProject) return;

      const response = await axios.get(
        `${API_BASE}/sessions/${session.session_id}?project_dir=${encodeURIComponent(selectedProject.directory)}&include_messages=true`
      );
      setSelectedSession(response.data.session);
      setDetailsOpen(true);
      setTabValue(0);
    } catch (error) {
      console.error('Error fetching session details:', error);
    }
  };

  useEffect(() => {
    fetchProjects();
    fetchActiveSessions();

    const interval = setInterval(fetchActiveSessions, 5000);
    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    if (selectedProject) {
      fetchSessions(selectedProject.name, selectedProject.directory);
      fetchStatistics(selectedProject.name);
    }
  }, [selectedProject]);

  // Filter sessions
  const getFilteredSessions = (): ClaudeCodeSession[] => {
    let filtered = sessions;

    switch (activeFilter) {
      case 'active':
        // Sessions with recent activity
        filtered = sessions.filter(s => {
          if (!s.last_timestamp) return false;
          const lastActivity = new Date(s.last_timestamp);
          const hourAgo = new Date(Date.now() - 60 * 60 * 1000);
          return lastActivity > hourAgo;
        });
        break;
      case 'completed':
        // Sessions that are not recent
        filtered = sessions.filter(s => {
          if (!s.last_timestamp) return true;
          const lastActivity = new Date(s.last_timestamp);
          const hourAgo = new Date(Date.now() - 60 * 60 * 1000);
          return lastActivity <= hourAgo;
        });
        break;
      case 'errors':
        filtered = sessions.filter(s => s.errors.length > 0);
        break;
      default:
        filtered = sessions;
    }

    // Apply search filter
    if (searchQuery.trim()) {
      const query = searchQuery.toLowerCase();
      filtered = filtered.filter(
        s =>
          s.session_id.toLowerCase().includes(query) ||
          s.git_branch?.toLowerCase().includes(query) ||
          s.cwd?.toLowerCase().includes(query)
      );
    }

    return filtered;
  };

  const filteredSessions = getFilteredSessions();

  // Statistics
  const stats = {
    active: activeSessions.length,
    completed: sessions.filter(s => {
      if (!s.last_timestamp) return true;
      const lastActivity = new Date(s.last_timestamp);
      const hourAgo = new Date(Date.now() - 60 * 60 * 1000);
      return lastActivity <= hourAgo;
    }).length,
    total: statistics?.total_sessions || 0,
    errors: statistics?.total_errors || 0,
  };

  const SessionCard: React.FC<{ session: ClaudeCodeSession }> = ({ session }) => {
    const isActive = session.last_timestamp
      ? new Date(session.last_timestamp) > new Date(Date.now() - 60 * 60 * 1000)
      : false;
    const hasErrors = session.errors.length > 0;

    return (
      <Card
        sx={{
          height: '100%',
          display: 'flex',
          flexDirection: 'column',
          position: 'relative',
          overflow: 'visible',
          bgcolor: '#1e293b',
          border: '1px solid #334155',
          borderRadius: 2,
          transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
          '&:hover': {
            transform: 'translateY(-4px)',
            borderColor: '#475569',
            boxShadow: `0 12px 24px -6px ${alpha('#6366f1', 0.3)}`,
          },
        }}
      >
        {/* Status indicator bar */}
        <Box
          sx={{
            position: 'absolute',
            top: 0,
            left: 0,
            right: 0,
            height: 3,
            background: hasErrors
              ? '#ef4444'
              : isActive
              ? '#10b981'
              : '#64748b',
            borderTopLeftRadius: 8,
            borderTopRightRadius: 8,
          }}
        />

        <CardContent sx={{ flexGrow: 1, pt: 3 }}>
          {/* Header with icon and actions */}
          <Box display="flex" justifyContent="space-between" alignItems="start" mb={2}>
            <Box display="flex" alignItems="start" gap={1.5} flexGrow={1}>
              <Box
                sx={{
                  width: 48,
                  height: 48,
                  borderRadius: 2,
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  bgcolor: alpha('#6366f1', 0.1),
                  border: '1px solid',
                  borderColor: alpha('#6366f1', 0.2),
                }}
              >
                <TerminalIcon sx={{ color: '#6366f1', fontSize: 28 }} />
              </Box>
              <Box flexGrow={1}>
                <Typography
                  variant="h6"
                  component="div"
                  sx={{
                    fontWeight: 600,
                    fontSize: '1rem',
                    mb: 0.5,
                    fontFamily: 'monospace',
                    display: 'flex',
                    alignItems: 'center',
                    gap: 1,
                    color: '#e2e8f0',
                  }}
                >
                  {session.session_id.substring(0, 12)}...
                  {isActive && (
                    <Tooltip title="Active Session">
                      <CheckCircleIcon sx={{ fontSize: 18, color: '#10b981' }} />
                    </Tooltip>
                  )}
                </Typography>
                <Stack direction="row" spacing={0.5} flexWrap="wrap">
                  <Chip
                    label={session.git_branch || 'No branch'}
                    size="small"
                    icon={<FolderIcon sx={{ fontSize: 14 }} />}
                    sx={{
                      height: 22,
                      fontSize: '0.7rem',
                      fontWeight: 500,
                      bgcolor: alpha('#6366f1', 0.1),
                      border: '1px solid',
                      borderColor: alpha('#6366f1', 0.2),
                      color: '#6366f1',
                      '& .MuiChip-icon': {
                        color: '#6366f1',
                      },
                    }}
                  />
                  {selectedProject && (
                    <Chip
                      label={selectedProject.name}
                      size="small"
                      sx={{
                        height: 22,
                        fontSize: '0.7rem',
                        fontWeight: 500,
                        bgcolor: alpha('#3b82f6', 0.1),
                        border: '1px solid',
                        borderColor: alpha('#3b82f6', 0.2),
                        color: '#3b82f6',
                      }}
                    />
                  )}
                </Stack>
              </Box>
            </Box>

            {/* Action button */}
            <Tooltip title="View Details">
              <IconButton
                size="small"
                onClick={() => openDetails(session)}
                sx={{
                  color: '#3b82f6',
                  '&:hover': {
                    bgcolor: alpha('#3b82f6', 0.1),
                  },
                }}
              >
                <InfoIcon fontSize="small" />
              </IconButton>
            </Tooltip>
          </Box>

          <Divider sx={{ my: 2, borderColor: '#334155' }} />

          {/* Metadata */}
          <Stack spacing={1.5}>
            <Box display="flex" alignItems="center" justifyContent="space-between">
              <Typography variant="caption" sx={{ display: 'flex', alignItems: 'center', gap: 0.5, color: '#94a3b8' }}>
                <MessageIcon sx={{ fontSize: 14 }} />
                Messages
              </Typography>
              <Typography variant="body2" fontWeight={600} color="#e2e8f0">
                {session.message_count}
                <Typography component="span" variant="caption" sx={{ ml: 0.5, color: '#94a3b8' }}>
                  ({session.user_messages} / {session.assistant_messages})
                </Typography>
              </Typography>
            </Box>

            <Box display="flex" alignItems="center" justifyContent="space-between">
              <Typography variant="caption" sx={{ display: 'flex', alignItems: 'center', gap: 0.5, color: '#94a3b8' }}>
                <CodeIcon sx={{ fontSize: 14 }} />
                Tools Used
              </Typography>
              <Chip
                label={Object.keys(session.tool_calls).length}
                size="small"
                sx={{
                  height: 20,
                  fontSize: '0.7rem',
                  bgcolor: alpha('#6366f1', 0.1),
                  color: '#6366f1',
                }}
              />
            </Box>

            <Box display="flex" alignItems="center" justifyContent="space-between">
              <Typography variant="caption" sx={{ display: 'flex', alignItems: 'center', gap: 0.5, color: '#94a3b8' }}>
                <StorageIcon sx={{ fontSize: 14 }} />
                Files Modified
              </Typography>
              <Typography variant="body2" fontWeight={600} color="#e2e8f0">
                {session.files_modified.length}
              </Typography>
            </Box>

            {hasErrors && (
              <Box display="flex" alignItems="center" justifyContent="space-between">
                <Typography variant="caption" sx={{ display: 'flex', alignItems: 'center', gap: 0.5, color: '#ef4444' }}>
                  <ErrorIcon sx={{ fontSize: 14 }} />
                  Errors
                </Typography>
                <Chip
                  label={session.errors.length}
                  size="small"
                  sx={{
                    height: 20,
                    fontSize: '0.7rem',
                    bgcolor: alpha('#ef4444', 0.1),
                    color: '#ef4444',
                  }}
                />
              </Box>
            )}

            <Box display="flex" alignItems="center" justifyContent="space-between">
              <Typography variant="caption" sx={{ display: 'flex', alignItems: 'center', gap: 0.5, color: '#94a3b8' }}>
                <AccessTimeIcon sx={{ fontSize: 14 }} />
                Created
              </Typography>
              <Typography variant="caption" fontWeight={500} color="#e2e8f0">
                {session.created_at ? format(new Date(session.created_at), 'MMM dd HH:mm') : 'N/A'}
              </Typography>
            </Box>
          </Stack>

          {/* Terminal Preview for Active Sessions */}
          {isActive && session.cwd && (
            <Paper
              sx={{
                mt: 2,
                p: 1.5,
                bgcolor: '#0f172a',
                border: '1px solid',
                borderColor: alpha('#10b981', 0.3),
                borderRadius: 1,
              }}
            >
              <Typography
                variant="caption"
                sx={{
                  fontFamily: 'monospace',
                  color: '#10b981',
                  display: 'block',
                  overflow: 'hidden',
                  textOverflow: 'ellipsis',
                  whiteSpace: 'nowrap',
                }}
              >
                $ cd {session.cwd}
              </Typography>
            </Paper>
          )}

          {/* Action buttons */}
          <Stack direction="row" spacing={1} mt={2}>
            <Button
              fullWidth
              size="small"
              variant="contained"
              onClick={() => openDetails(session)}
              sx={{
                borderRadius: 1.5,
                bgcolor: '#6366f1',
                textTransform: 'none',
                fontWeight: 500,
                '&:hover': {
                  bgcolor: '#4f46e5',
                },
              }}
            >
              View Details
            </Button>
          </Stack>
        </CardContent>
      </Card>
    );
  };

  const ActiveSessionCard: React.FC<{ session: ActiveSession }> = ({ session }) => (
    <Card
      sx={{
        bgcolor: '#1e293b',
        border: '1px solid',
        borderColor: alpha('#10b981', 0.3),
        borderRadius: 2,
        transition: 'all 0.3s ease',
        '&:hover': {
          transform: 'translateY(-2px)',
          boxShadow: `0 8px 16px ${alpha('#10b981', 0.2)}`,
          borderColor: alpha('#10b981', 0.5),
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
                bgcolor: alpha('#10b981', 0.1),
                border: '1px solid',
                borderColor: alpha('#10b981', 0.2),
              }}
            >
              <ComputerIcon sx={{ color: '#10b981', fontSize: 24 }} />
            </Box>
            <Box>
              <Typography variant="body2" fontWeight={600} color="#e2e8f0">
                PID: {session.pid}
              </Typography>
              <Stack direction="row" spacing={1} mt={0.5}>
                <Chip
                  label={`CPU: ${session.cpu}%`}
                  size="small"
                  icon={<SpeedIcon sx={{ fontSize: 12, color: '#10b981' }} />}
                  sx={{
                    height: 20,
                    fontSize: '0.65rem',
                    bgcolor: alpha('#10b981', 0.1),
                    color: '#10b981',
                    '& .MuiChip-icon': {
                      color: '#10b981',
                    },
                  }}
                />
                <Chip
                  label={`Mem: ${session.mem}%`}
                  size="small"
                  icon={<MemoryIcon sx={{ fontSize: 12, color: '#10b981' }} />}
                  sx={{
                    height: 20,
                    fontSize: '0.65rem',
                    bgcolor: alpha('#10b981', 0.1),
                    color: '#10b981',
                    '& .MuiChip-icon': {
                      color: '#10b981',
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
                color: '#ef4444',
                '&:hover': {
                  bgcolor: alpha('#ef4444', 0.1),
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
            bgcolor: '#0f172a',
            border: '1px solid',
            borderColor: alpha('#10b981', 0.2),
            borderRadius: 1,
          }}
        >
          <Typography
            variant="caption"
            sx={{
              fontFamily: 'monospace',
              fontSize: '0.65rem',
              color: '#10b981',
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
  );

  return (
    <Box sx={{ minHeight: '100vh', pb: 4 }}>
      <Container maxWidth="xl">
        {/* Hero Header */}
        <Box py={4}>
          <Stack direction="row" justifyContent="space-between" alignItems="center" mb={3}>
            <Box>
              <Typography
                variant="h3"
                component="h1"
                sx={{
                  fontWeight: 700,
                  background: 'linear-gradient(135deg, #6366f1, #8b5cf6)',
                  WebkitBackgroundClip: 'text',
                  WebkitTextFillColor: 'transparent',
                  mb: 1,
                }}
              >
                Claude Code Sessions
              </Typography>
              <Typography variant="body1" color="#94a3b8">
                Monitor and manage Claude AI sessions across all projects
              </Typography>
            </Box>
            <Button
              variant="contained"
              size="large"
              startIcon={<RefreshIcon />}
              onClick={() => {
                fetchProjects();
                fetchActiveSessions();
              }}
              sx={{
                borderRadius: 2,
                px: 3,
                py: 1.5,
                bgcolor: '#6366f1',
                boxShadow: `0 8px 16px ${alpha('#6366f1', 0.3)}`,
                textTransform: 'none',
                fontWeight: 600,
                '&:hover': {
                  bgcolor: '#4f46e5',
                  transform: 'translateY(-2px)',
                  boxShadow: `0 12px 20px ${alpha('#6366f1', 0.4)}`,
                },
              }}
            >
              Refresh
            </Button>
          </Stack>

          {/* Statistics Cards */}
          <Grid container spacing={2} mb={3}>
            {[
              { label: 'Active Sessions', value: stats.active, color: '#10b981', icon: <PlayIcon /> },
              { label: 'Completed', value: stats.completed, color: '#3b82f6', icon: <CheckCircleIcon /> },
              { label: 'Total Sessions', value: stats.total, color: '#6366f1', icon: <TerminalIcon /> },
              { label: 'Errors', value: stats.errors, color: '#ef4444', icon: <ErrorIcon /> },
            ].map((stat) => (
              <Grid item xs={12} sm={6} md={3} key={stat.label}>
                <Paper
                  sx={{
                    p: 2.5,
                    borderRadius: 2,
                    bgcolor: '#1e293b',
                    border: '1px solid',
                    borderColor: alpha(stat.color, 0.2),
                    transition: 'all 0.3s ease',
                    '&:hover': {
                      transform: 'translateY(-4px)',
                      boxShadow: `0 8px 16px ${alpha(stat.color, 0.2)}`,
                      borderColor: alpha(stat.color, 0.4),
                    },
                  }}
                >
                  <Box display="flex" alignItems="center" gap={1.5} mb={1}>
                    <Box
                      sx={{
                        width: 32,
                        height: 32,
                        borderRadius: 1,
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        bgcolor: alpha(stat.color, 0.1),
                        color: stat.color,
                      }}
                    >
                      {stat.icon}
                    </Box>
                    <Typography variant="body2" color="#94a3b8">
                      {stat.label}
                    </Typography>
                  </Box>
                  <Typography variant="h3" sx={{ fontWeight: 700, color: stat.color }}>
                    {stat.value}
                  </Typography>
                </Paper>
              </Grid>
            ))}
          </Grid>

          {/* Active Sessions Alert */}
          {activeSessions.length > 0 && (
            <Alert
              severity="success"
              icon={<ComputerIcon />}
              sx={{
                mb: 3,
                borderRadius: 2,
                border: '1px solid',
                borderColor: alpha('#10b981', 0.3),
                bgcolor: alpha('#10b981', 0.1),
                color: '#10b981',
                '& .MuiAlert-icon': {
                  color: '#10b981',
                },
                '& .MuiAlert-message': {
                  color: '#e2e8f0',
                },
              }}
            >
              <Typography variant="body2" fontWeight={600}>
                {activeSessions.length} active Claude Code process{activeSessions.length > 1 ? 'es' : ''} running
              </Typography>
            </Alert>
          )}

          {/* Active Sessions Grid */}
          {activeSessions.length > 0 && (
            <Box mb={3}>
              <Typography variant="h6" fontWeight={600} mb={2} color="#e2e8f0">
                Running Processes
              </Typography>
              <Grid container spacing={2}>
                {activeSessions.map((session) => (
                  <Grid item xs={12} md={6} lg={4} key={session.pid}>
                    <ActiveSessionCard session={session} />
                  </Grid>
                ))}
              </Grid>
            </Box>
          )}

          {/* Search and Filter Bar */}
          <Paper
            sx={{
              p: 2,
              mb: 3,
              borderRadius: 2,
              bgcolor: '#1e293b',
              border: '1px solid #334155',
            }}
          >
            <Stack direction={{ xs: 'column', md: 'row' }} spacing={2} alignItems="center">
              {/* Search */}
              <TextField
                fullWidth
                placeholder="Search sessions by ID, branch, or path..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                InputProps={{
                  startAdornment: (
                    <InputAdornment position="start">
                      <SearchIcon sx={{ color: '#64748b' }} />
                    </InputAdornment>
                  ),
                }}
                sx={{
                  '& .MuiOutlinedInput-root': {
                    borderRadius: 2,
                    bgcolor: '#0f172a',
                    color: '#e2e8f0',
                    '& fieldset': {
                      borderColor: '#334155',
                    },
                    '&:hover fieldset': {
                      borderColor: '#475569',
                    },
                    '&.Mui-focused fieldset': {
                      borderColor: '#6366f1',
                    },
                  },
                  '& .MuiInputBase-input::placeholder': {
                    color: '#64748b',
                    opacity: 1,
                  },
                }}
              />

              {/* Project Selector */}
              <TextField
                select
                value={selectedProject?.name || ''}
                onChange={(e) => {
                  const project = projects.find((p) => p.name === e.target.value);
                  if (project) setSelectedProject(project);
                }}
                SelectProps={{
                  native: true,
                }}
                sx={{
                  minWidth: 200,
                  '& .MuiOutlinedInput-root': {
                    borderRadius: 2,
                    bgcolor: '#0f172a',
                    color: '#e2e8f0',
                    '& fieldset': {
                      borderColor: '#334155',
                    },
                    '&:hover fieldset': {
                      borderColor: '#475569',
                    },
                    '&.Mui-focused fieldset': {
                      borderColor: '#6366f1',
                    },
                  },
                  '& option': {
                    bgcolor: '#1e293b',
                    color: '#e2e8f0',
                  },
                }}
              >
                {projects.map((project) => (
                  <option key={project.directory} value={project.name}>
                    {project.name} ({project.sessions_count})
                  </option>
                ))}
              </TextField>

              {/* Filter Toggle */}
              <ToggleButtonGroup
                value={activeFilter}
                exclusive
                onChange={(e, newFilter) => {
                  if (newFilter !== null) {
                    setActiveFilter(newFilter);
                  }
                }}
                sx={{
                  flexShrink: 0,
                  '& .MuiToggleButton-root': {
                    borderRadius: 2,
                    px: 2,
                    py: 1,
                    textTransform: 'none',
                    fontWeight: 500,
                    color: '#94a3b8',
                    borderColor: '#334155',
                    '&:hover': {
                      bgcolor: alpha('#6366f1', 0.1),
                      borderColor: '#475569',
                    },
                    '&.Mui-selected': {
                      bgcolor: '#6366f1',
                      color: '#fff',
                      borderColor: '#6366f1',
                      '&:hover': {
                        bgcolor: '#4f46e5',
                        borderColor: '#4f46e5',
                      },
                    },
                  },
                }}
              >
                <ToggleButton value="all">
                  All <Badge badgeContent={sessions.length} sx={{ ml: 1, '& .MuiBadge-badge': { bgcolor: '#6366f1', color: '#fff' } }} />
                </ToggleButton>
                <ToggleButton value="active">
                  Active <Badge badgeContent={stats.active} sx={{ ml: 1, '& .MuiBadge-badge': { bgcolor: '#10b981', color: '#fff' } }} />
                </ToggleButton>
                <ToggleButton value="completed">
                  Completed <Badge badgeContent={stats.completed} sx={{ ml: 1, '& .MuiBadge-badge': { bgcolor: '#3b82f6', color: '#fff' } }} />
                </ToggleButton>
                <ToggleButton value="errors">
                  Errors <Badge badgeContent={stats.errors} sx={{ ml: 1, '& .MuiBadge-badge': { bgcolor: '#ef4444', color: '#fff' } }} />
                </ToggleButton>
              </ToggleButtonGroup>
            </Stack>
          </Paper>
        </Box>

        {/* Sessions Grid */}
        {loading ? (
          <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
            <CircularProgress size={48} sx={{ color: '#6366f1' }} />
          </Box>
        ) : (
          <Grid container spacing={3}>
            {filteredSessions.length === 0 ? (
              <Grid item xs={12}>
                <Paper
                  sx={{
                    p: 6,
                    textAlign: 'center',
                    borderRadius: 2,
                    bgcolor: '#1e293b',
                    border: '1px solid #334155',
                  }}
                >
                  <TerminalIcon sx={{ fontSize: 64, color: '#64748b', mb: 2 }} />
                  <Typography variant="h6" gutterBottom color="#e2e8f0">
                    No sessions found
                  </Typography>
                  <Typography variant="body2" color="#94a3b8" mb={3}>
                    {searchQuery
                      ? 'Try adjusting your search query'
                      : activeFilter !== 'all'
                      ? 'Try changing the filter'
                      : 'No Claude sessions available for this project'}
                  </Typography>
                </Paper>
              </Grid>
            ) : (
              filteredSessions.map((session) => (
                <Grid item xs={12} sm={6} lg={4} key={session.session_id}>
                  <SessionCard session={session} />
                </Grid>
              ))
            )}
          </Grid>
        )}
      </Container>

      {/* Session Details Dialog */}
      <Dialog
        open={detailsOpen}
        onClose={() => setDetailsOpen(false)}
        maxWidth="lg"
        fullWidth
        PaperProps={{
          sx: {
            bgcolor: '#1e293b',
            border: '1px solid #334155',
            borderRadius: 2,
          },
        }}
      >
        {selectedSession && (
          <>
            <DialogTitle sx={{ borderBottom: '1px solid #334155' }}>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <FolderIcon sx={{ color: '#6366f1' }} />
                <Typography variant="h6" color="#e2e8f0">
                  Session {selectedSession.session_id.substring(0, 12)}...
                </Typography>
              </Box>
            </DialogTitle>
            <DialogContent>
              <Tabs
                value={tabValue}
                onChange={(_, v) => setTabValue(v)}
                sx={{
                  borderBottom: '1px solid #334155',
                  '& .MuiTab-root': {
                    color: '#94a3b8',
                    textTransform: 'none',
                    fontWeight: 500,
                    '&.Mui-selected': {
                      color: '#6366f1',
                    },
                  },
                  '& .MuiTabs-indicator': {
                    bgcolor: '#6366f1',
                  },
                }}
              >
                <Tab label="Overview" icon={<InfoIcon />} iconPosition="start" />
                <Tab label="Messages" icon={<MessageIcon />} iconPosition="start" />
                <Tab label="Tools" icon={<CodeIcon />} iconPosition="start" />
                <Tab label="Timeline" icon={<TimelineIcon />} iconPosition="start" />
              </Tabs>

              <TabPanel value={tabValue} index={0}>
                <Grid container spacing={2}>
                  <Grid item xs={6}>
                    <Typography variant="subtitle2" color="#94a3b8">
                      Working Directory
                    </Typography>
                    <Typography variant="body2" sx={{ fontFamily: 'monospace', mb: 2, color: '#e2e8f0' }}>
                      {selectedSession.cwd}
                    </Typography>
                  </Grid>
                  <Grid item xs={6}>
                    <Typography variant="subtitle2" color="#94a3b8">
                      Git Branch
                    </Typography>
                    <Typography variant="body2" sx={{ mb: 2, color: '#e2e8f0' }}>
                      {selectedSession.git_branch || 'N/A'}
                    </Typography>
                  </Grid>
                  <Grid item xs={6}>
                    <Typography variant="subtitle2" color="#94a3b8">
                      Claude Version
                    </Typography>
                    <Typography variant="body2" sx={{ mb: 2, color: '#e2e8f0' }}>
                      {selectedSession.claude_version || 'N/A'}
                    </Typography>
                  </Grid>
                  <Grid item xs={6}>
                    <Typography variant="subtitle2" color="#94a3b8">
                      File Size
                    </Typography>
                    <Typography variant="body2" sx={{ mb: 2, color: '#e2e8f0' }}>
                      {(selectedSession.file_size / 1024).toFixed(1)} KB
                    </Typography>
                  </Grid>
                  <Grid item xs={12}>
                    <Typography variant="subtitle2" color="#94a3b8" gutterBottom>
                      Commands Used
                    </Typography>
                    <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                      {selectedSession.commands_used.length > 0 ? (
                        selectedSession.commands_used.map((cmd, idx) => (
                          <Chip
                            key={idx}
                            label={cmd}
                            size="small"
                            sx={{
                              bgcolor: alpha('#6366f1', 0.1),
                              color: '#6366f1',
                              border: '1px solid',
                              borderColor: alpha('#6366f1', 0.2),
                            }}
                          />
                        ))
                      ) : (
                        <Typography variant="body2" color="#94a3b8">
                          No commands used
                        </Typography>
                      )}
                    </Box>
                  </Grid>
                  <Grid item xs={12}>
                    <Typography variant="subtitle2" color="#94a3b8" gutterBottom>
                      Modified Files
                    </Typography>
                    {selectedSession.files_modified.length > 0 ? (
                      <Paper
                        sx={{
                          p: 1,
                          maxHeight: 200,
                          overflow: 'auto',
                          bgcolor: '#0f172a',
                          border: '1px solid #334155',
                        }}
                      >
                        {selectedSession.files_modified.map((file, idx) => (
                          <Typography
                            key={idx}
                            variant="body2"
                            sx={{ fontFamily: 'monospace', fontSize: '0.75rem', color: '#e2e8f0' }}
                          >
                            {file}
                          </Typography>
                        ))}
                      </Paper>
                    ) : (
                      <Typography variant="body2" color="#94a3b8">
                        No files modified
                      </Typography>
                    )}
                  </Grid>
                </Grid>
              </TabPanel>

              <TabPanel value={tabValue} index={1}>
                {selectedSession.messages && selectedSession.messages.length > 0 ? (
                  <List sx={{ maxHeight: 500, overflow: 'auto' }}>
                    {selectedSession.messages.map((msg, idx) => (
                      <React.Fragment key={msg.uuid}>
                        <ListItem alignItems="flex-start" sx={{ bgcolor: '#0f172a', mb: 1, borderRadius: 1 }}>
                          <ListItemText
                            primary={
                              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                                <Typography variant="subtitle2" color="#e2e8f0">
                                  {msg.type === 'user' ? '👤 User' : '🤖 Assistant'}
                                </Typography>
                                <Typography variant="caption" color="#94a3b8">
                                  {format(new Date(msg.timestamp), 'HH:mm:ss')}
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
                                  color: '#94a3b8',
                                }}
                              >
                                {(() => {
                                  const content: any = msg.content;

                                  // Handle string content - SHOW FULL CONTENT
                                  if (typeof content === 'string') {
                                    return content;
                                  }

                                  // Handle array content (Claude API format) - SHOW FULL CONTENT
                                  if (Array.isArray(content)) {
                                    const textContent = (content as any[])
                                      .filter((block: any) => block.type === 'text')
                                      .map((block: any) => block.text)
                                      .join('\n');
                                    return textContent;
                                  }

                                  // Handle object with text property - SHOW FULL CONTENT
                                  if (content && typeof content === 'object' && 'text' in content) {
                                    return (content as any).text;
                                  }

                                  // Fallback: stringify - SHOW FULL CONTENT
                                  return JSON.stringify(content, null, 2);
                                })()}
                              </Typography>
                            }
                          />
                        </ListItem>
                        {idx < selectedSession.messages!.length - 1 && <Divider sx={{ borderColor: '#334155' }} />}
                      </React.Fragment>
                    ))}
                  </List>
                ) : (
                  <Typography color="#94a3b8" align="center">
                    No messages available
                  </Typography>
                )}
              </TabPanel>

              <TabPanel value={tabValue} index={2}>
                {Object.keys(selectedSession.tool_calls).length > 0 ? (
                  <Grid container spacing={2}>
                    {Object.entries(selectedSession.tool_calls)
                      .sort(([, a], [, b]) => b - a)
                      .map(([tool, count]) => (
                        <Grid item xs={12} sm={6} md={4} key={tool}>
                          <Card
                            sx={{
                              bgcolor: '#0f172a',
                              border: '1px solid #334155',
                            }}
                          >
                            <CardContent>
                              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                                <Typography variant="body1" color="#e2e8f0">{tool}</Typography>
                                <Chip
                                  label={count}
                                  sx={{
                                    bgcolor: alpha('#6366f1', 0.1),
                                    color: '#6366f1',
                                  }}
                                />
                              </Box>
                            </CardContent>
                          </Card>
                        </Grid>
                      ))}
                  </Grid>
                ) : (
                  <Typography color="#94a3b8" align="center">
                    No tools used
                  </Typography>
                )}
              </TabPanel>

              <TabPanel value={tabValue} index={3}>
                {selectedSession.errors.length > 0 ? (
                  <List>
                    {selectedSession.errors.map((error, idx) => (
                      <ListItem
                        key={idx}
                        sx={{
                          bgcolor: alpha('#ef4444', 0.1),
                          border: '1px solid',
                          borderColor: alpha('#ef4444', 0.3),
                          mb: 1,
                          borderRadius: 1,
                        }}
                      >
                        <ListItemText
                          primary={
                            <Typography variant="caption" color="#ef4444">
                              {format(new Date(error.timestamp), 'MMM dd HH:mm:ss')}
                            </Typography>
                          }
                          secondary={
                            <Typography variant="body2" sx={{ whiteSpace: 'pre-wrap', color: '#e2e8f0' }}>
                              {error.content}
                            </Typography>
                          }
                        />
                      </ListItem>
                    ))}
                  </List>
                ) : (
                  <Typography color="#94a3b8" align="center">
                    No errors recorded
                  </Typography>
                )}
              </TabPanel>
            </DialogContent>
            <DialogActions sx={{ borderTop: '1px solid #334155', p: 2 }}>
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
    </Box>
  );
}
