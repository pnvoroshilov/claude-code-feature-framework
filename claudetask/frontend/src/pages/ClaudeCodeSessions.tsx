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
  Alert,
  TextField,
  MenuItem,
  Select,
  FormControl,
  InputLabel,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  TablePagination
} from '@mui/material';
import {
  Refresh as RefreshIcon,
  ExpandMore as ExpandMoreIcon,
  Search as SearchIcon,
  Info as InfoIcon,
  Message as MessageIcon,
  Code as CodeIcon,
  Error as ErrorIcon,
  Folder as FolderIcon,
  Timeline as TimelineIcon,
  Stop as StopIcon,
  Terminal as TerminalIcon
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

export default function ClaudeCodeSessions() {
  const [projects, setProjects] = useState<ClaudeCodeProject[]>([]);
  const [selectedProject, setSelectedProject] = useState<ClaudeCodeProject | null>(null);
  const [sessions, setSessions] = useState<ClaudeCodeSession[]>([]);
  const [statistics, setStatistics] = useState<SessionStatistics | null>(null);
  const [loading, setLoading] = useState(true);
  const [selectedSession, setSelectedSession] = useState<ClaudeCodeSession | null>(null);
  const [detailsOpen, setDetailsOpen] = useState(false);
  const [tabValue, setTabValue] = useState(0);
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState<ClaudeCodeSession[]>([]);
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(10);
  const [activeSessions, setActiveSessions] = useState<any[]>([]);
  const [showActiveDetails, setShowActiveDetails] = useState(false);

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

  const handleSearch = async () => {
    if (!searchQuery.trim()) return;

    try {
      setLoading(true);
      const url = selectedProject
        ? `${API_BASE}/sessions/search?query=${encodeURIComponent(searchQuery)}&project_name=${selectedProject.name}`
        : `${API_BASE}/sessions/search?query=${encodeURIComponent(searchQuery)}`;
      const response = await axios.get(url);
      setSearchResults(response.data.results);
    } catch (error) {
      console.error('Error searching sessions:', error);
    } finally {
      setLoading(false);
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

    // Refresh active sessions every 5 seconds
    const interval = setInterval(fetchActiveSessions, 5000);
    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    if (selectedProject) {
      fetchSessions(selectedProject.name, selectedProject.directory);
      fetchStatistics(selectedProject.name);
    }
  }, [selectedProject]);

  const displaySessions = searchResults.length > 0 ? searchResults : sessions;
  const paginatedSessions = displaySessions.slice(
    page * rowsPerPage,
    page * rowsPerPage + rowsPerPage
  );

  const handleChangePage = (_: unknown, newPage: number) => {
    setPage(newPage);
  };

  const handleChangeRowsPerPage = (event: React.ChangeEvent<HTMLInputElement>) => {
    setRowsPerPage(parseInt(event.target.value, 10));
    setPage(0);
  };

  return (
    <Box>
      <Box sx={{ mb: 3, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <Typography variant="h4" component="h1">
          Claude Code Sessions
        </Typography>
        <Button
          variant="outlined"
          startIcon={<RefreshIcon />}
          onClick={fetchProjects}
        >
          Refresh
        </Button>
      </Box>

      <Alert severity="info" sx={{ mb: 3 }}>
        📂 Reading sessions from <code>~/.claude/projects/</code> directory
      </Alert>

      {activeSessions.length > 0 && (
        <Alert
          severity="info"
          sx={{ mb: 2 }}
          action={
            <Button
              size="small"
              onClick={() => setShowActiveDetails(!showActiveDetails)}
            >
              {showActiveDetails ? 'Hide' : 'Show'} Details
            </Button>
          }
        >
          <Typography>
            💻 {activeSessions.length} total Claude Code process{activeSessions.length > 1 ? 'es' : ''} running on computer
          </Typography>

          {showActiveDetails && (
            <List dense sx={{ mt: 1, bgcolor: 'background.paper', borderRadius: 1 }}>
              {activeSessions.map((session) => (
                <ListItem
                  key={session.pid}
                  secondaryAction={
                    <IconButton
                      edge="end"
                      color="error"
                      size="small"
                      onClick={() => killSession(session.pid)}
                      title="Terminate Session"
                    >
                      <StopIcon fontSize="small" />
                    </IconButton>
                  }
                >
                  <Box sx={{ display: 'flex', alignItems: 'center', width: '100%' }}>
                    <TerminalIcon color="success" sx={{ mr: 2 }} />
                    <Box sx={{ flexGrow: 1 }}>
                      <Typography variant="body2" sx={{ fontWeight: 'medium' }}>
                        PID: {session.pid} | CPU: {session.cpu}% | Mem: {session.mem}%
                      </Typography>
                      <Typography
                        variant="caption"
                        sx={{ fontFamily: 'monospace', fontSize: '0.7rem', color: 'text.secondary' }}
                      >
                        {session.command.substring(0, 80)}
                      </Typography>
                    </Box>
                  </Box>
                </ListItem>
              ))}
            </List>
          )}
        </Alert>
      )}

      {/* Project Selector */}
      <Paper sx={{ p: 2, mb: 3 }}>
        <Grid container spacing={2} alignItems="center">
          <Grid item xs={12} md={6}>
            <FormControl fullWidth>
              <InputLabel>Project</InputLabel>
              <Select
                value={selectedProject?.name || ''}
                onChange={(e) => {
                  const project = projects.find(p => p.name === e.target.value);
                  if (project) setSelectedProject(project);
                }}
                label="Project"
              >
                {projects.map((project) => (
                  <MenuItem key={project.directory} value={project.name}>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', width: '100%', alignItems: 'center', gap: 1 }}>
                      <span>{project.name}</span>
                      <Chip
                        label={`${project.sessions_count} sessions`}
                        size="small"
                        variant="outlined"
                      />
                    </Box>
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </Grid>
          <Grid item xs={12} md={6}>
            <TextField
              fullWidth
              placeholder="Search sessions..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
              InputProps={{
                endAdornment: (
                  <IconButton onClick={handleSearch}>
                    <SearchIcon />
                  </IconButton>
                )
              }}
            />
          </Grid>
        </Grid>
      </Paper>

      {/* Statistics Cards */}
      {statistics && (
        <Grid container spacing={2} sx={{ mb: 3 }}>
          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Typography color="textSecondary" gutterBottom variant="body2">
                  Total Sessions
                </Typography>
                <Typography variant="h4" component="div">
                  {statistics.total_sessions}
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Typography color="textSecondary" gutterBottom variant="body2">
                  Total Messages
                </Typography>
                <Typography variant="h4" component="div">
                  {statistics.total_messages.toLocaleString()}
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Typography color="textSecondary" gutterBottom variant="body2">
                  Files Modified
                </Typography>
                <Typography variant="h4" component="div">
                  {statistics.total_files_modified}
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Typography color="textSecondary" gutterBottom variant="body2">
                  Total Errors
                </Typography>
                <Typography variant="h4" component="div" color="error.main">
                  {statistics.total_errors}
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      )}

      {/* Tool Usage Accordion */}
      {statistics && Object.keys(statistics.total_tool_calls).length > 0 && (
        <Accordion sx={{ mb: 3 }}>
          <AccordionSummary expandIcon={<ExpandMoreIcon />}>
            <CodeIcon sx={{ mr: 1 }} />
            <Typography>Tool Usage Statistics</Typography>
          </AccordionSummary>
          <AccordionDetails>
            <Grid container spacing={1}>
              {Object.entries(statistics.total_tool_calls)
                .sort(([, a], [, b]) => b - a)
                .slice(0, 10)
                .map(([tool, count]) => (
                  <Grid item xs={12} sm={6} md={4} key={tool}>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                      <Typography variant="body2">{tool}</Typography>
                      <Chip label={count} size="small" />
                    </Box>
                  </Grid>
                ))}
            </Grid>
          </AccordionDetails>
        </Accordion>
      )}

      {/* Sessions Table */}
      <TableContainer component={Paper}>
        {loading && <LinearProgress />}
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Session ID</TableCell>
              <TableCell>Branch</TableCell>
              <TableCell>Messages</TableCell>
              <TableCell>Tools</TableCell>
              <TableCell>Files</TableCell>
              <TableCell>Errors</TableCell>
              <TableCell>Created</TableCell>
              <TableCell align="right">Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {paginatedSessions.length === 0 ? (
              <TableRow>
                <TableCell colSpan={8} align="center">
                  <Typography variant="body2" color="textSecondary" sx={{ py: 3 }}>
                    {searchResults.length === 0 && searchQuery ? 'No sessions found' : 'No sessions available'}
                  </Typography>
                </TableCell>
              </TableRow>
            ) : (
              paginatedSessions.map((session) => (
                <TableRow key={session.session_id} hover>
                  <TableCell>
                    <Typography
                      variant="body2"
                      sx={{ fontFamily: 'monospace', fontSize: '0.75rem' }}
                    >
                      {session.session_id.substring(0, 12)}...
                    </Typography>
                  </TableCell>
                  <TableCell>
                    <Chip
                      label={session.git_branch || 'N/A'}
                      size="small"
                      variant="outlined"
                    />
                  </TableCell>
                  <TableCell>
                    <Typography variant="body2">
                      {session.message_count}
                      <Typography
                        component="span"
                        variant="caption"
                        color="textSecondary"
                        sx={{ ml: 0.5 }}
                      >
                        ({session.user_messages}↑ {session.assistant_messages}↓)
                      </Typography>
                    </Typography>
                  </TableCell>
                  <TableCell>
                    <Chip
                      label={Object.keys(session.tool_calls).length}
                      size="small"
                      color="primary"
                      variant="outlined"
                    />
                  </TableCell>
                  <TableCell>
                    {session.files_modified.length}
                  </TableCell>
                  <TableCell>
                    {session.errors.length > 0 ? (
                      <Chip
                        icon={<ErrorIcon />}
                        label={session.errors.length}
                        size="small"
                        color="error"
                      />
                    ) : (
                      '-'
                    )}
                  </TableCell>
                  <TableCell>
                    {session.created_at
                      ? format(new Date(session.created_at), 'MMM dd HH:mm')
                      : '-'}
                  </TableCell>
                  <TableCell align="right">
                    <IconButton
                      size="small"
                      onClick={() => openDetails(session)}
                      title="View Details"
                    >
                      <InfoIcon />
                    </IconButton>
                  </TableCell>
                </TableRow>
              ))
            )}
          </TableBody>
        </Table>
        <TablePagination
          rowsPerPageOptions={[10, 25, 50, 100]}
          component="div"
          count={displaySessions.length}
          rowsPerPage={rowsPerPage}
          page={page}
          onPageChange={handleChangePage}
          onRowsPerPageChange={handleChangeRowsPerPage}
        />
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
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <FolderIcon />
                <Typography variant="h6">
                  Session {selectedSession.session_id.substring(0, 12)}...
                </Typography>
              </Box>
            </DialogTitle>
            <DialogContent>
              <Tabs value={tabValue} onChange={(_, v) => setTabValue(v)}>
                <Tab label="Overview" icon={<InfoIcon />} iconPosition="start" />
                <Tab label="Messages" icon={<MessageIcon />} iconPosition="start" />
                <Tab label="Tools" icon={<CodeIcon />} iconPosition="start" />
                <Tab label="Timeline" icon={<TimelineIcon />} iconPosition="start" />
              </Tabs>

              <TabPanel value={tabValue} index={0}>
                <Grid container spacing={2}>
                  <Grid item xs={6}>
                    <Typography variant="subtitle2" color="textSecondary">
                      Working Directory
                    </Typography>
                    <Typography
                      variant="body2"
                      sx={{ fontFamily: 'monospace', mb: 2 }}
                    >
                      {selectedSession.cwd}
                    </Typography>
                  </Grid>
                  <Grid item xs={6}>
                    <Typography variant="subtitle2" color="textSecondary">
                      Git Branch
                    </Typography>
                    <Typography variant="body2" sx={{ mb: 2 }}>
                      {selectedSession.git_branch || 'N/A'}
                    </Typography>
                  </Grid>
                  <Grid item xs={6}>
                    <Typography variant="subtitle2" color="textSecondary">
                      Claude Version
                    </Typography>
                    <Typography variant="body2" sx={{ mb: 2 }}>
                      {selectedSession.claude_version || 'N/A'}
                    </Typography>
                  </Grid>
                  <Grid item xs={6}>
                    <Typography variant="subtitle2" color="textSecondary">
                      File Size
                    </Typography>
                    <Typography variant="body2" sx={{ mb: 2 }}>
                      {(selectedSession.file_size / 1024).toFixed(1)} KB
                    </Typography>
                  </Grid>
                  <Grid item xs={12}>
                    <Typography variant="subtitle2" color="textSecondary" gutterBottom>
                      Commands Used
                    </Typography>
                    <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                      {selectedSession.commands_used.length > 0 ? (
                        selectedSession.commands_used.map((cmd, idx) => (
                          <Chip key={idx} label={cmd} size="small" />
                        ))
                      ) : (
                        <Typography variant="body2" color="textSecondary">
                          No commands used
                        </Typography>
                      )}
                    </Box>
                  </Grid>
                  <Grid item xs={12}>
                    <Typography variant="subtitle2" color="textSecondary" gutterBottom>
                      Modified Files
                    </Typography>
                    {selectedSession.files_modified.length > 0 ? (
                      <Paper sx={{ p: 1, maxHeight: 200, overflow: 'auto' }}>
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
                      <Typography variant="body2" color="textSecondary">
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
                        <ListItem alignItems="flex-start">
                          <ListItemText
                            primary={
                              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                                <Typography variant="subtitle2">
                                  {msg.type === 'user' ? '👤 User' : '🤖 Assistant'}
                                </Typography>
                                <Typography variant="caption" color="textSecondary">
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
                                  overflow: 'auto'
                                }}
                              >
                                {msg.content.substring(0, 500)}
                                {msg.content.length > 500 && '...'}
                              </Typography>
                            }
                          />
                        </ListItem>
                        {idx < selectedSession.messages!.length - 1 && <Divider />}
                      </React.Fragment>
                    ))}
                  </List>
                ) : (
                  <Typography color="textSecondary" align="center">
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
                          <Card variant="outlined">
                            <CardContent>
                              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                                <Typography variant="body1">{tool}</Typography>
                                <Chip label={count} color="primary" />
                              </Box>
                            </CardContent>
                          </Card>
                        </Grid>
                      ))}
                  </Grid>
                ) : (
                  <Typography color="textSecondary" align="center">
                    No tools used
                  </Typography>
                )}
              </TabPanel>

              <TabPanel value={tabValue} index={3}>
                {selectedSession.errors.length > 0 ? (
                  <List>
                    {selectedSession.errors.map((error, idx) => (
                      <ListItem key={idx} sx={{ bgcolor: 'error.light', mb: 1, borderRadius: 1 }}>
                        <ListItemText
                          primary={
                            <Typography variant="caption">
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
                  <Typography color="textSecondary" align="center">
                    No errors recorded
                  </Typography>
                )}
              </TabPanel>
            </DialogContent>
          </>
        )}
      </Dialog>
    </Box>
  );
}
