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
  Chip,
  CircularProgress,
  IconButton,
  Tooltip,
  ToggleButtonGroup,
  ToggleButton,
  Stack,
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
  Terminal as TerminalIcon,
  Folder as FolderIcon,
  CheckCircle as CheckCircleIcon,
  AccessTime as AccessTimeIcon,
  Storage as StorageIcon,
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

type FilterType = 'all' | 'recent' | 'large' | 'errors' | 'tool-heavy';

const ClaudeCodeSessionsView: React.FC = () => {
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
      case 'recent':
        filtered = sessions.filter(s => {
          if (!s.last_timestamp) return false;
          const lastActivity = new Date(s.last_timestamp);
          const hourAgo = new Date(Date.now() - 60 * 60 * 1000);
          return lastActivity > hourAgo;
        });
        break;
      case 'large':
        filtered = sessions.filter(s => s.message_count > 100);
        break;
      case 'errors':
        filtered = sessions.filter(s => s.errors.length > 0);
        break;
      case 'tool-heavy':
        filtered = sessions.filter(s => Object.keys(s.tool_calls).length > 5);
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
    recent: sessions.filter(s => {
      if (!s.last_timestamp) return false;
      const lastActivity = new Date(s.last_timestamp);
      const hourAgo = new Date(Date.now() - 60 * 60 * 1000);
      return lastActivity > hourAgo;
    }).length,
    large: sessions.filter(s => s.message_count > 100).length,
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
          bgcolor: theme.palette.mode === 'dark' ? '#1e293b' : 'background.paper',
          border: '1px solid',
          borderColor: theme.palette.mode === 'dark' ? '#334155' : alpha(theme.palette.divider, 0.1),
          borderLeft: `4px solid #6366f1`,
          borderRadius: 2,
          transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
          '&:hover': {
            transform: 'translateY(-4px)',
            borderColor: '#6366f1',
            boxShadow: `0 12px 24px -6px ${alpha('#6366f1', 0.3)}`,
          },
        }}
      >
        {/* Status indicator */}
        <Box
          sx={{
            position: 'absolute',
            top: 0,
            left: 0,
            right: 0,
            height: 3,
            background: hasErrors
              ? theme.palette.error.main
              : isActive
              ? theme.palette.success.main
              : alpha(theme.palette.text.secondary, 0.3),
            borderTopLeftRadius: 8,
            borderTopRightRadius: 8,
          }}
        />

        <CardContent sx={{ flexGrow: 1, pt: 3 }}>
          {/* Header */}
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
                  }}
                >
                  {session.session_id.substring(0, 12)}...
                  {isActive && (
                    <Tooltip title="Active Session">
                      <CheckCircleIcon sx={{ fontSize: 18, color: theme.palette.success.main }} />
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
                        bgcolor: alpha('#6366f1', 0.1),
                        color: '#6366f1',
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
                  color: '#6366f1',
                  '&:hover': {
                    bgcolor: alpha('#6366f1', 0.1),
                  },
                }}
              >
                <InfoIcon fontSize="small" />
              </IconButton>
            </Tooltip>
          </Box>

          <Divider sx={{ my: 2 }} />

          {/* Metadata */}
          <Stack spacing={1.5}>
            <Box display="flex" alignItems="center" justifyContent="space-between">
              <Typography variant="caption" sx={{ display: 'flex', alignItems: 'center', gap: 0.5, color: 'text.secondary' }}>
                <MessageIcon sx={{ fontSize: 14 }} />
                Messages
              </Typography>
              <Typography variant="body2" fontWeight={600}>
                {session.message_count}
                <Typography component="span" variant="caption" sx={{ ml: 0.5, color: 'text.secondary' }}>
                  ({session.user_messages} / {session.assistant_messages})
                </Typography>
              </Typography>
            </Box>

            <Box display="flex" alignItems="center" justifyContent="space-between">
              <Typography variant="caption" sx={{ display: 'flex', alignItems: 'center', gap: 0.5, color: 'text.secondary' }}>
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
              <Typography variant="caption" sx={{ display: 'flex', alignItems: 'center', gap: 0.5, color: 'text.secondary' }}>
                <StorageIcon sx={{ fontSize: 14 }} />
                Files Modified
              </Typography>
              <Typography variant="body2" fontWeight={600}>
                {session.files_modified.length}
              </Typography>
            </Box>

            {hasErrors && (
              <Box display="flex" alignItems="center" justifyContent="space-between">
                <Typography variant="caption" sx={{ display: 'flex', alignItems: 'center', gap: 0.5, color: 'error.main' }}>
                  <ErrorIcon sx={{ fontSize: 14 }} />
                  Errors
                </Typography>
                <Chip
                  label={session.errors.length}
                  size="small"
                  sx={{
                    height: 20,
                    fontSize: '0.7rem',
                    bgcolor: alpha(theme.palette.error.main, 0.1),
                    color: 'error.main',
                  }}
                />
              </Box>
            )}

            <Box display="flex" alignItems="center" justifyContent="space-between">
              <Typography variant="caption" sx={{ display: 'flex', alignItems: 'center', gap: 0.5, color: 'text.secondary' }}>
                <AccessTimeIcon sx={{ fontSize: 14 }} />
                Created
              </Typography>
              <Typography variant="caption" fontWeight={500}>
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
                bgcolor: theme.palette.mode === 'dark' ? '#0f172a' : alpha(theme.palette.background.default, 0.5),
                border: '1px solid',
                borderColor: alpha(theme.palette.success.main, 0.3),
                borderRadius: 1,
              }}
            >
              <Typography
                variant="caption"
                sx={{
                  fontFamily: 'monospace',
                  color: theme.palette.success.main,
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

  return (
    <Box>
      {/* Search and Filter Bar */}
      <Paper
        sx={{
          p: 2,
          mb: 3,
          borderRadius: 2,
          bgcolor: theme.palette.mode === 'dark' ? '#1e293b' : 'background.paper',
          border: '1px solid',
          borderColor: theme.palette.mode === 'dark' ? '#334155' : alpha(theme.palette.divider, 0.1),
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
                  <SearchIcon sx={{ color: 'text.secondary' }} />
                </InputAdornment>
              ),
            }}
            sx={{
              '& .MuiOutlinedInput-root': {
                borderRadius: 2,
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
            sx={{ minWidth: 200 }}
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
                '&.Mui-selected': {
                  bgcolor: '#6366f1',
                  color: '#fff',
                  '&:hover': {
                    bgcolor: '#4f46e5',
                  },
                },
              },
            }}
          >
            <ToggleButton value="all">
              All <Badge badgeContent={sessions.length} sx={{ ml: 1 }} />
            </ToggleButton>
            <ToggleButton value="recent">
              Recent <Badge badgeContent={stats.recent} sx={{ ml: 1 }} />
            </ToggleButton>
            <ToggleButton value="large">
              Large <Badge badgeContent={stats.large} sx={{ ml: 1 }} />
            </ToggleButton>
            <ToggleButton value="errors">
              Errors <Badge badgeContent={stats.errors} sx={{ ml: 1 }} />
            </ToggleButton>
          </ToggleButtonGroup>

          <Button
            variant="outlined"
            startIcon={<RefreshIcon />}
            onClick={() => {
              fetchProjects();
              if (selectedProject) {
                fetchSessions(selectedProject.name, selectedProject.directory);
              }
            }}
            sx={{
              borderRadius: 2,
              textTransform: 'none',
              fontWeight: 600,
              borderColor: '#6366f1',
              color: '#6366f1',
              '&:hover': {
                bgcolor: alpha('#6366f1', 0.1),
                borderColor: '#4f46e5',
              },
            }}
          >
            Refresh
          </Button>
        </Stack>
      </Paper>

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
                  bgcolor: theme.palette.mode === 'dark' ? '#1e293b' : 'background.paper',
                  border: '1px solid',
                  borderColor: theme.palette.mode === 'dark' ? '#334155' : alpha(theme.palette.divider, 0.1),
                }}
              >
                <TerminalIcon sx={{ fontSize: 64, color: 'text.secondary', mb: 2 }} />
                <Typography variant="h6" gutterBottom>
                  No sessions found
                </Typography>
                <Typography variant="body2" color="text.secondary" mb={3}>
                  {searchQuery
                    ? 'Try adjusting your search query'
                    : activeFilter !== 'all'
                    ? 'Try changing the filter'
                    : 'No Claude Code sessions available for this project'}
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
        {selectedSession && (
          <>
            <DialogTitle sx={{ borderBottom: '1px solid', borderColor: 'divider' }}>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <FolderIcon sx={{ color: '#6366f1' }} />
                <Typography variant="h6">
                  Session {selectedSession.session_id.substring(0, 12)}...
                </Typography>
              </Box>
            </DialogTitle>
            <DialogContent>
              <Tabs
                value={tabValue}
                onChange={(_, v) => setTabValue(v)}
                sx={{
                  borderBottom: '1px solid',
                  borderColor: 'divider',
                  '& .MuiTab-root': {
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
                    <Typography variant="subtitle2" color="text.secondary">
                      Working Directory
                    </Typography>
                    <Typography variant="body2" sx={{ fontFamily: 'monospace', mb: 2 }}>
                      {selectedSession.cwd}
                    </Typography>
                  </Grid>
                  <Grid item xs={6}>
                    <Typography variant="subtitle2" color="text.secondary">
                      Git Branch
                    </Typography>
                    <Typography variant="body2" sx={{ mb: 2 }}>
                      {selectedSession.git_branch || 'N/A'}
                    </Typography>
                  </Grid>
                  <Grid item xs={6}>
                    <Typography variant="subtitle2" color="text.secondary">
                      Claude Version
                    </Typography>
                    <Typography variant="body2" sx={{ mb: 2 }}>
                      {selectedSession.claude_version || 'N/A'}
                    </Typography>
                  </Grid>
                  <Grid item xs={6}>
                    <Typography variant="subtitle2" color="text.secondary">
                      File Size
                    </Typography>
                    <Typography variant="body2" sx={{ mb: 2 }}>
                      {(selectedSession.file_size / 1024).toFixed(1)} KB
                    </Typography>
                  </Grid>
                  <Grid item xs={12}>
                    <Typography variant="subtitle2" color="text.secondary" gutterBottom>
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
                        <Typography variant="body2" color="text.secondary">
                          No commands used
                        </Typography>
                      )}
                    </Box>
                  </Grid>
                  <Grid item xs={12}>
                    <Typography variant="subtitle2" color="text.secondary" gutterBottom>
                      Modified Files
                    </Typography>
                    {selectedSession.files_modified.length > 0 ? (
                      <Paper
                        sx={{
                          p: 1,
                          maxHeight: 200,
                          overflow: 'auto',
                          bgcolor: theme.palette.mode === 'dark' ? '#0f172a' : alpha(theme.palette.background.default, 0.5),
                          border: '1px solid',
                          borderColor: alpha(theme.palette.divider, 0.1),
                        }}
                      >
                        {selectedSession.files_modified.map((file, idx) => (
                          <Typography
                            key={idx}
                            variant="body2"
                            sx={{ fontFamily: 'monospace', fontSize: '0.75rem' }}
                          >
                            {file}
                          </Typography>
                        ))}
                      </Paper>
                    ) : (
                      <Typography variant="body2" color="text.secondary">
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
                        <ListItem alignItems="flex-start" sx={{ bgcolor: alpha(theme.palette.background.default, 0.3), mb: 1, borderRadius: 1 }}>
                          <ListItemText
                            primary={
                              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                                <Typography variant="subtitle2">
                                  {msg.type === 'user' ? '👤 User' : '🤖 Assistant'}
                                </Typography>
                                <Typography variant="caption" color="text.secondary">
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
                                  color: 'text.secondary',
                                }}
                              >
                                {(() => {
                                  const content: any = msg.content;

                                  if (typeof content === 'string') {
                                    return content;
                                  }

                                  if (Array.isArray(content)) {
                                    const textContent = (content as any[])
                                      .filter((block: any) => block.type === 'text')
                                      .map((block: any) => block.text)
                                      .join('\n');
                                    return textContent;
                                  }

                                  if (content && typeof content === 'object' && 'text' in content) {
                                    return (content as any).text;
                                  }

                                  return JSON.stringify(content, null, 2);
                                })()}
                              </Typography>
                            }
                          />
                        </ListItem>
                        {idx < selectedSession.messages!.length - 1 && <Divider />}
                      </React.Fragment>
                    ))}
                  </List>
                ) : (
                  <Typography color="text.secondary" align="center">
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
                              bgcolor: theme.palette.mode === 'dark' ? '#0f172a' : alpha(theme.palette.background.default, 0.3),
                              border: '1px solid',
                              borderColor: alpha(theme.palette.divider, 0.1),
                            }}
                          >
                            <CardContent>
                              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                                <Typography variant="body1">{tool}</Typography>
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
                  <Typography color="text.secondary" align="center">
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
                          bgcolor: alpha(theme.palette.error.main, 0.1),
                          border: '1px solid',
                          borderColor: alpha(theme.palette.error.main, 0.3),
                          mb: 1,
                          borderRadius: 1,
                        }}
                      >
                        <ListItemText
                          primary={
                            <Typography variant="caption" color="error.main">
                              {format(new Date(error.timestamp), 'MMM dd HH:mm:ss')}
                            </Typography>
                          }
                          secondary={
                            <Typography variant="body2" sx={{ whiteSpace: 'pre-wrap' }}>
                              {error.content}
                            </Typography>
                          }
                        />
                      </ListItem>
                    ))}
                  </List>
                ) : (
                  <Typography color="text.secondary" align="center">
                    No errors recorded
                  </Typography>
                )}
              </TabPanel>
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
    </Box>
  );
};

export default ClaudeCodeSessionsView;
