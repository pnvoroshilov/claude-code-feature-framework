import React, { useState, useEffect, useCallback } from 'react';
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
  TextField,
  InputAdornment,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Button,
  Tooltip,
  Card,
  CardContent,
  Grid,
  CircularProgress,
  Alert,
  Collapse,
  useTheme,
  alpha,
  Divider,
  Switch,
  FormControlLabel,
  LinearProgress,
  Pagination,
  Tabs,
  Tab,
} from '@mui/material';
import {
  Search as SearchIcon,
  Refresh as RefreshIcon,
  Delete as DeleteIcon,
  ExpandMore as ExpandMoreIcon,
  ExpandLess as ExpandLessIcon,
  CheckCircle as SuccessIcon,
  Error as ErrorIcon,
  HourglassEmpty as PendingIcon,
  PlayArrow as PlayIcon,
  Stop as StopIcon,
  DataObject as DataIcon,
  Timeline as TimelineIcon,
  Functions as FunctionsIcon,
  Storage as StorageIcon,
  Hub as MCPIcon,
  Webhook as HooksIcon,
  SkipNext as SkippedIcon,
} from '@mui/icons-material';
import { useProject } from '../context/ProjectContext';

interface MCPCall {
  id: number;
  tool_name: string;
  timestamp: string;
  end_timestamp?: string;
  status: 'pending' | 'success' | 'error';
  arguments: string | null;
  result: string | null;
  error: string | null;
  logs: Array<{
    timestamp: string;
    level: string;
    message: string;
    log_type: string;
  }>;
}

interface LogStats {
  total_calls: number;
  success_count: number;
  error_count: number;
  pending_count: number;
  success_rate: number;
  tools_used: Record<string, number>;
  unique_tools: number;
  project_name?: string;
  log_file?: string;
  log_file_exists: boolean;
  log_file_size_kb?: number;
  log_file_modified?: string;
}

interface HookExecution {
  id: number;
  hook_name: string;
  timestamp: string;
  end_timestamp?: string;
  status: 'running' | 'success' | 'error' | 'skipped';
  message: string | null;
  error: string | null;
  logs: Array<{
    timestamp: string;
    hook_name: string;
    status: string;
    message: string;
  }>;
}

interface HookStats {
  total_executions: number;
  success_count: number;
  error_count: number;
  skipped_count: number;
  success_rate: number;
  hooks_used: Record<string, number>;
  unique_hooks: number;
  project_name?: string;
  log_file?: string;
  log_file_exists: boolean;
  log_file_size_kb?: number;
  log_file_modified?: string;
}

const MCPLogs: React.FC = () => {
  const theme = useTheme();
  const { selectedProject } = useProject();

  // Tab state
  const [activeTab, setActiveTab] = useState(0);

  // MCP Logs state
  const [calls, setCalls] = useState<MCPCall[]>([]);
  const [stats, setStats] = useState<LogStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Hooks Logs state
  const [hookExecutions, setHookExecutions] = useState<HookExecution[]>([]);
  const [hookStats, setHookStats] = useState<HookStats | null>(null);
  const [hookLoading, setHookLoading] = useState(true);
  const [hookError, setHookError] = useState<string | null>(null);

  // Filters
  const [search, setSearch] = useState('');
  const [toolFilter, setToolFilter] = useState('');
  const [statusFilter, setStatusFilter] = useState('');

  // Hooks Filters
  const [hookSearch, setHookSearch] = useState('');
  const [hookFilter, setHookFilter] = useState('');
  const [hookStatusFilter, setHookStatusFilter] = useState('');

  // Pagination
  const [page, setPage] = useState(1);
  const [total, setTotal] = useState(0);
  const [limit] = useState(50);

  // Hooks Pagination
  const [hookPage, setHookPage] = useState(1);
  const [hookTotal, setHookTotal] = useState(0);

  // Auto-refresh
  const [autoRefresh, setAutoRefresh] = useState(false);

  // Expanded rows
  const [expandedRows, setExpandedRows] = useState<Set<number>>(new Set());
  const [expandedHookRows, setExpandedHookRows] = useState<Set<number>>(new Set());

  const fetchLogs = useCallback(async () => {
    try {
      const params = new URLSearchParams();
      params.append('limit', limit.toString());
      params.append('offset', ((page - 1) * limit).toString());
      if (search) params.append('search', search);
      if (toolFilter) params.append('tool_filter', toolFilter);
      if (statusFilter) params.append('status_filter', statusFilter);

      const response = await fetch(`/api/mcp-logs?${params.toString()}`);
      const data = await response.json();

      setCalls(data.calls || []);
      setTotal(data.total || 0);
      setError(null);
    } catch (err) {
      setError('Failed to fetch MCP logs');
      console.error('Error fetching logs:', err);
    } finally {
      setLoading(false);
    }
  }, [page, limit, search, toolFilter, statusFilter]);

  const fetchStats = useCallback(async () => {
    try {
      const response = await fetch('/api/mcp-logs/stats');
      const data = await response.json();
      setStats(data);
    } catch (err) {
      console.error('Error fetching stats:', err);
    }
  }, []);

  // Hook logs fetching
  const fetchHookLogs = useCallback(async () => {
    try {
      const params = new URLSearchParams();
      params.append('limit', limit.toString());
      params.append('offset', ((hookPage - 1) * limit).toString());
      if (hookSearch) params.append('search', hookSearch);
      if (hookFilter) params.append('hook_filter', hookFilter);
      if (hookStatusFilter) params.append('status_filter', hookStatusFilter);

      const response = await fetch(`/api/mcp-logs/hooks?${params.toString()}`);
      const data = await response.json();

      setHookExecutions(data.executions || []);
      setHookTotal(data.total || 0);
      setHookError(null);
    } catch (err) {
      setHookError('Failed to fetch hook logs');
      console.error('Error fetching hook logs:', err);
    } finally {
      setHookLoading(false);
    }
  }, [hookPage, limit, hookSearch, hookFilter, hookStatusFilter]);

  const fetchHookStats = useCallback(async () => {
    try {
      const response = await fetch('/api/mcp-logs/hooks/stats');
      const data = await response.json();
      setHookStats(data);
    } catch (err) {
      console.error('Error fetching hook stats:', err);
    }
  }, []);

  useEffect(() => {
    fetchLogs();
    fetchStats();
    fetchHookLogs();
    fetchHookStats();
  }, [fetchLogs, fetchStats, fetchHookLogs, fetchHookStats]);

  // Auto-refresh
  useEffect(() => {
    let interval: NodeJS.Timeout;
    if (autoRefresh) {
      interval = setInterval(() => {
        if (activeTab === 0) {
          fetchLogs();
          fetchStats();
        } else {
          fetchHookLogs();
          fetchHookStats();
        }
      }, 3000);
    }
    return () => {
      if (interval) clearInterval(interval);
    };
  }, [autoRefresh, activeTab, fetchLogs, fetchStats, fetchHookLogs, fetchHookStats]);

  const handleRefresh = () => {
    if (activeTab === 0) {
      setLoading(true);
      fetchLogs();
      fetchStats();
    } else {
      setHookLoading(true);
      fetchHookLogs();
      fetchHookStats();
    }
  };

  const handleClearLogs = async () => {
    if (!window.confirm('Are you sure you want to clear all MCP logs?')) return;

    try {
      const response = await fetch('/api/mcp-logs', { method: 'DELETE' });
      if (response.ok) {
        handleRefresh();
      }
    } catch (err) {
      setError('Failed to clear logs');
    }
  };

  const handleClearHookLogs = async () => {
    if (!window.confirm('Are you sure you want to clear all hook logs?')) return;

    try {
      const response = await fetch('/api/mcp-logs/hooks', { method: 'DELETE' });
      if (response.ok) {
        handleRefresh();
      }
    } catch (err) {
      setHookError('Failed to clear hook logs');
    }
  };

  const toggleRowExpand = (id: number) => {
    const newExpanded = new Set(expandedRows);
    if (newExpanded.has(id)) {
      newExpanded.delete(id);
    } else {
      newExpanded.add(id);
    }
    setExpandedRows(newExpanded);
  };

  const toggleHookRowExpand = (id: number) => {
    const newExpanded = new Set(expandedHookRows);
    if (newExpanded.has(id)) {
      newExpanded.delete(id);
    } else {
      newExpanded.add(id);
    }
    setExpandedHookRows(newExpanded);
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'success':
        return <SuccessIcon sx={{ color: theme.palette.success.main }} />;
      case 'error':
        return <ErrorIcon sx={{ color: theme.palette.error.main }} />;
      case 'skipped':
        return <SkippedIcon sx={{ color: theme.palette.info.main }} />;
      case 'running':
        return <PendingIcon sx={{ color: theme.palette.warning.main }} />;
      default:
        return <PendingIcon sx={{ color: theme.palette.warning.main }} />;
    }
  };

  const getStatusChip = (status: string) => {
    const colors: Record<string, 'success' | 'error' | 'warning' | 'info'> = {
      success: 'success',
      error: 'error',
      pending: 'warning',
      running: 'warning',
      skipped: 'info',
    };
    return (
      <Chip
        size="small"
        label={status}
        color={colors[status] || 'default'}
        icon={getStatusIcon(status)}
        sx={{ fontWeight: 500 }}
      />
    );
  };

  const formatTimestamp = (timestamp: string) => {
    try {
      return new Date(timestamp.replace(',', '.')).toLocaleString();
    } catch {
      return timestamp;
    }
  };

  const uniqueTools = stats?.tools_used ? Object.keys(stats.tools_used) : [];
  const uniqueHooks = hookStats?.hooks_used ? Object.keys(hookStats.hooks_used) : [];

  if (!selectedProject) {
    return (
      <Box sx={{ p: 3 }}>
        <Alert severity="info">
          Please select an active project to view MCP logs.
        </Alert>
      </Box>
    );
  }

  return (
    <Box sx={{ p: 3 }}>
      {/* Header */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Box>
          <Typography variant="h4" fontWeight={700}>
            Logs
          </Typography>
          <Typography variant="body2" color="text.secondary" sx={{ mt: 0.5 }}>
            View and analyze MCP calls and Hook executions for {selectedProject?.name || 'current project'}
          </Typography>
        </Box>
        <Box sx={{ display: 'flex', gap: 1, alignItems: 'center' }}>
          <FormControlLabel
            control={
              <Switch
                checked={autoRefresh}
                onChange={(e) => setAutoRefresh(e.target.checked)}
                color="primary"
              />
            }
            label="Auto-refresh"
          />
          <Tooltip title="Refresh logs">
            <IconButton onClick={handleRefresh} color="primary">
              <RefreshIcon />
            </IconButton>
          </Tooltip>
          <Tooltip title={activeTab === 0 ? "Clear MCP logs" : "Clear Hook logs"}>
            <IconButton onClick={activeTab === 0 ? handleClearLogs : handleClearHookLogs} color="error">
              <DeleteIcon />
            </IconButton>
          </Tooltip>
        </Box>
      </Box>

      {/* Tabs */}
      <Paper sx={{ mb: 3 }}>
        <Tabs
          value={activeTab}
          onChange={(_, newValue) => setActiveTab(newValue)}
          indicatorColor="primary"
          textColor="primary"
        >
          <Tab
            icon={<MCPIcon />}
            iconPosition="start"
            label={`MCP Calls ${stats?.total_calls ? `(${stats.total_calls})` : ''}`}
          />
          <Tab
            icon={<HooksIcon />}
            iconPosition="start"
            label={`Hooks ${hookStats?.total_executions ? `(${hookStats.total_executions})` : ''}`}
          />
        </Tabs>
      </Paper>

      {/* MCP Tab Content */}
      {activeTab === 0 && (
        <>

      {/* Stats Cards */}
      {stats && (
        <Grid container spacing={2} sx={{ mb: 3 }}>
          <Grid item xs={12} sm={6} md={3}>
            <Card
              sx={{
                background: `linear-gradient(135deg, ${alpha(theme.palette.primary.main, 0.1)} 0%, ${alpha(theme.palette.primary.main, 0.05)} 100%)`,
                border: `1px solid ${alpha(theme.palette.primary.main, 0.2)}`,
              }}
            >
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                  <FunctionsIcon sx={{ color: theme.palette.primary.main }} />
                  <Typography variant="subtitle2" color="text.secondary">
                    Total Calls
                  </Typography>
                </Box>
                <Typography variant="h4" fontWeight={700}>
                  {stats.total_calls}
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <Card
              sx={{
                background: `linear-gradient(135deg, ${alpha(theme.palette.success.main, 0.1)} 0%, ${alpha(theme.palette.success.main, 0.05)} 100%)`,
                border: `1px solid ${alpha(theme.palette.success.main, 0.2)}`,
              }}
            >
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                  <SuccessIcon sx={{ color: theme.palette.success.main }} />
                  <Typography variant="subtitle2" color="text.secondary">
                    Success Rate
                  </Typography>
                </Box>
                <Typography variant="h4" fontWeight={700}>
                  {stats.success_rate}%
                </Typography>
                <Typography variant="caption" color="text.secondary">
                  {stats.success_count} successful / {stats.error_count} errors
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <Card
              sx={{
                background: `linear-gradient(135deg, ${alpha(theme.palette.info.main, 0.1)} 0%, ${alpha(theme.palette.info.main, 0.05)} 100%)`,
                border: `1px solid ${alpha(theme.palette.info.main, 0.2)}`,
              }}
            >
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                  <DataIcon sx={{ color: theme.palette.info.main }} />
                  <Typography variant="subtitle2" color="text.secondary">
                    Unique Tools
                  </Typography>
                </Box>
                <Typography variant="h4" fontWeight={700}>
                  {stats.unique_tools}
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <Card
              sx={{
                background: `linear-gradient(135deg, ${alpha(theme.palette.warning.main, 0.1)} 0%, ${alpha(theme.palette.warning.main, 0.05)} 100%)`,
                border: `1px solid ${alpha(theme.palette.warning.main, 0.2)}`,
              }}
            >
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                  <StorageIcon sx={{ color: theme.palette.warning.main }} />
                  <Typography variant="subtitle2" color="text.secondary">
                    Log File Size
                  </Typography>
                </Box>
                <Typography variant="h4" fontWeight={700}>
                  {stats.log_file_size_kb ? `${stats.log_file_size_kb} KB` : '-'}
                </Typography>
                {stats.log_file_modified && (
                  <Typography variant="caption" color="text.secondary">
                    Last modified: {formatTimestamp(stats.log_file_modified)}
                  </Typography>
                )}
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      )}

      {/* Filters */}
      <Paper sx={{ p: 2, mb: 3 }}>
        <Grid container spacing={2} alignItems="center">
          <Grid item xs={12} md={4}>
            <TextField
              fullWidth
              size="small"
              placeholder="Search in logs..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              InputProps={{
                startAdornment: (
                  <InputAdornment position="start">
                    <SearchIcon />
                  </InputAdornment>
                ),
              }}
            />
          </Grid>
          <Grid item xs={12} md={3}>
            <FormControl fullWidth size="small">
              <InputLabel>Tool Filter</InputLabel>
              <Select
                value={toolFilter}
                label="Tool Filter"
                onChange={(e) => setToolFilter(e.target.value)}
              >
                <MenuItem value="">All Tools</MenuItem>
                {uniqueTools.map((tool) => (
                  <MenuItem key={tool} value={tool}>
                    {tool}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </Grid>
          <Grid item xs={12} md={3}>
            <FormControl fullWidth size="small">
              <InputLabel>Status Filter</InputLabel>
              <Select
                value={statusFilter}
                label="Status Filter"
                onChange={(e) => setStatusFilter(e.target.value)}
              >
                <MenuItem value="">All Statuses</MenuItem>
                <MenuItem value="success">Success</MenuItem>
                <MenuItem value="error">Error</MenuItem>
                <MenuItem value="pending">Pending</MenuItem>
              </Select>
            </FormControl>
          </Grid>
          <Grid item xs={12} md={2}>
            <Button
              fullWidth
              variant="outlined"
              onClick={() => {
                setSearch('');
                setToolFilter('');
                setStatusFilter('');
                setPage(1);
              }}
            >
              Clear Filters
            </Button>
          </Grid>
        </Grid>
      </Paper>

      {/* Error Alert */}
      {error && (
        <Alert severity="error" sx={{ mb: 3 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}

      {/* Loading */}
      {loading && <LinearProgress sx={{ mb: 2 }} />}

      {/* Logs Table */}
      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell width={50} />
              <TableCell>Timestamp</TableCell>
              <TableCell>Tool</TableCell>
              <TableCell>Status</TableCell>
              <TableCell>Arguments</TableCell>
              <TableCell>Result / Error</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {calls.length === 0 ? (
              <TableRow>
                <TableCell colSpan={6} align="center" sx={{ py: 4 }}>
                  <Typography color="text.secondary">
                    {loading ? 'Loading logs...' : 'No MCP calls found. MCP calls will appear here once the MCP server is running.'}
                  </Typography>
                </TableCell>
              </TableRow>
            ) : (
              calls.map((call) => (
                <React.Fragment key={call.id}>
                  <TableRow
                    hover
                    sx={{
                      cursor: 'pointer',
                      '&:hover': {
                        backgroundColor: alpha(theme.palette.primary.main, 0.05),
                      },
                    }}
                    onClick={() => toggleRowExpand(call.id)}
                  >
                    <TableCell>
                      <IconButton size="small">
                        {expandedRows.has(call.id) ? <ExpandLessIcon /> : <ExpandMoreIcon />}
                      </IconButton>
                    </TableCell>
                    <TableCell>
                      <Typography variant="body2" sx={{ fontFamily: 'monospace', fontSize: '0.75rem' }}>
                        {formatTimestamp(call.timestamp)}
                      </Typography>
                    </TableCell>
                    <TableCell>
                      <Chip
                        size="small"
                        label={call.tool_name}
                        sx={{
                          fontFamily: 'monospace',
                          fontWeight: 600,
                          backgroundColor: alpha(theme.palette.primary.main, 0.1),
                        }}
                      />
                    </TableCell>
                    <TableCell>{getStatusChip(call.status)}</TableCell>
                    <TableCell>
                      <Typography
                        variant="body2"
                        sx={{
                          fontFamily: 'monospace',
                          fontSize: '0.75rem',
                          maxWidth: 200,
                          overflow: 'hidden',
                          textOverflow: 'ellipsis',
                          whiteSpace: 'nowrap',
                        }}
                      >
                        {call.arguments ? call.arguments.slice(0, 50) + (call.arguments.length > 50 ? '...' : '') : '-'}
                      </Typography>
                    </TableCell>
                    <TableCell>
                      <Typography
                        variant="body2"
                        sx={{
                          fontFamily: 'monospace',
                          fontSize: '0.75rem',
                          maxWidth: 250,
                          overflow: 'hidden',
                          textOverflow: 'ellipsis',
                          whiteSpace: 'nowrap',
                          color: call.error ? theme.palette.error.main : 'inherit',
                        }}
                      >
                        {call.error || call.result?.slice(0, 60) || '-'}
                        {call.result && call.result.length > 60 ? '...' : ''}
                      </Typography>
                    </TableCell>
                  </TableRow>
                  <TableRow>
                    <TableCell colSpan={6} sx={{ py: 0 }}>
                      <Collapse in={expandedRows.has(call.id)} timeout="auto" unmountOnExit>
                        <Box sx={{ p: 2, backgroundColor: alpha(theme.palette.background.default, 0.5) }}>
                          <Grid container spacing={2}>
                            {call.arguments && (
                              <Grid item xs={12} md={6}>
                                <Typography variant="subtitle2" fontWeight={600} gutterBottom>
                                  Arguments
                                </Typography>
                                <Paper
                                  sx={{
                                    p: 1.5,
                                    backgroundColor: theme.palette.mode === 'dark' ? '#1a1a2e' : '#f5f5f5',
                                    maxHeight: 200,
                                    overflow: 'auto',
                                  }}
                                >
                                  <pre style={{ margin: 0, fontFamily: 'monospace', fontSize: '0.75rem', whiteSpace: 'pre-wrap' }}>
                                    {call.arguments}
                                  </pre>
                                </Paper>
                              </Grid>
                            )}
                            {(call.result || call.error) && (
                              <Grid item xs={12} md={6}>
                                <Typography variant="subtitle2" fontWeight={600} gutterBottom>
                                  {call.error ? 'Error' : 'Result'}
                                </Typography>
                                <Paper
                                  sx={{
                                    p: 1.5,
                                    backgroundColor: call.error
                                      ? alpha(theme.palette.error.main, 0.1)
                                      : theme.palette.mode === 'dark'
                                      ? '#1a1a2e'
                                      : '#f5f5f5',
                                    maxHeight: 200,
                                    overflow: 'auto',
                                  }}
                                >
                                  <pre
                                    style={{
                                      margin: 0,
                                      fontFamily: 'monospace',
                                      fontSize: '0.75rem',
                                      whiteSpace: 'pre-wrap',
                                      color: call.error ? theme.palette.error.main : 'inherit',
                                    }}
                                  >
                                    {call.error || call.result}
                                  </pre>
                                </Paper>
                              </Grid>
                            )}
                          </Grid>
                        </Box>
                      </Collapse>
                    </TableCell>
                  </TableRow>
                </React.Fragment>
              ))
            )}
          </TableBody>
        </Table>
      </TableContainer>

      {/* Pagination */}
      {total > limit && (
        <Box sx={{ display: 'flex', justifyContent: 'center', mt: 2 }}>
          <Pagination
            count={Math.ceil(total / limit)}
            page={page}
            onChange={(_, newPage) => setPage(newPage)}
            color="primary"
          />
        </Box>
      )}

      {/* Top Tools */}
      {stats && stats.tools_used && Object.keys(stats.tools_used).length > 0 && (
        <Paper sx={{ p: 2, mt: 3 }}>
          <Typography variant="h6" fontWeight={600} gutterBottom>
            Most Used Tools
          </Typography>
          <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
            {Object.entries(stats.tools_used)
              .slice(0, 10)
              .map(([tool, count]) => (
                <Chip
                  key={tool}
                  label={`${tool} (${count})`}
                  onClick={() => setToolFilter(tool)}
                  sx={{
                    fontFamily: 'monospace',
                    cursor: 'pointer',
                    '&:hover': {
                      backgroundColor: alpha(theme.palette.primary.main, 0.2),
                    },
                  }}
                />
              ))}
          </Box>
        </Paper>
      )}
        </>
      )}

      {/* Hooks Tab Content */}
      {activeTab === 1 && (
        <>
          {/* Hook Stats Cards */}
          {hookStats && (
            <Grid container spacing={2} sx={{ mb: 3 }}>
              <Grid item xs={12} sm={6} md={3}>
                <Card
                  sx={{
                    background: `linear-gradient(135deg, ${alpha(theme.palette.primary.main, 0.1)} 0%, ${alpha(theme.palette.primary.main, 0.05)} 100%)`,
                    border: `1px solid ${alpha(theme.palette.primary.main, 0.2)}`,
                  }}
                >
                  <CardContent>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                      <HooksIcon sx={{ color: theme.palette.primary.main }} />
                      <Typography variant="subtitle2" color="text.secondary">
                        Total Executions
                      </Typography>
                    </Box>
                    <Typography variant="h4" fontWeight={700}>
                      {hookStats.total_executions}
                    </Typography>
                  </CardContent>
                </Card>
              </Grid>
              <Grid item xs={12} sm={6} md={3}>
                <Card
                  sx={{
                    background: `linear-gradient(135deg, ${alpha(theme.palette.success.main, 0.1)} 0%, ${alpha(theme.palette.success.main, 0.05)} 100%)`,
                    border: `1px solid ${alpha(theme.palette.success.main, 0.2)}`,
                  }}
                >
                  <CardContent>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                      <SuccessIcon sx={{ color: theme.palette.success.main }} />
                      <Typography variant="subtitle2" color="text.secondary">
                        Success
                      </Typography>
                    </Box>
                    <Typography variant="h4" fontWeight={700} color="success.main">
                      {hookStats.success_count}
                    </Typography>
                  </CardContent>
                </Card>
              </Grid>
              <Grid item xs={12} sm={6} md={3}>
                <Card
                  sx={{
                    background: `linear-gradient(135deg, ${alpha(theme.palette.error.main, 0.1)} 0%, ${alpha(theme.palette.error.main, 0.05)} 100%)`,
                    border: `1px solid ${alpha(theme.palette.error.main, 0.2)}`,
                  }}
                >
                  <CardContent>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                      <ErrorIcon sx={{ color: theme.palette.error.main }} />
                      <Typography variant="subtitle2" color="text.secondary">
                        Errors
                      </Typography>
                    </Box>
                    <Typography variant="h4" fontWeight={700} color="error.main">
                      {hookStats.error_count}
                    </Typography>
                  </CardContent>
                </Card>
              </Grid>
              <Grid item xs={12} sm={6} md={3}>
                <Card
                  sx={{
                    background: `linear-gradient(135deg, ${alpha(theme.palette.info.main, 0.1)} 0%, ${alpha(theme.palette.info.main, 0.05)} 100%)`,
                    border: `1px solid ${alpha(theme.palette.info.main, 0.2)}`,
                  }}
                >
                  <CardContent>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                      <TimelineIcon sx={{ color: theme.palette.info.main }} />
                      <Typography variant="subtitle2" color="text.secondary">
                        Success Rate
                      </Typography>
                    </Box>
                    <Typography variant="h4" fontWeight={700}>
                      {hookStats.success_rate}%
                    </Typography>
                  </CardContent>
                </Card>
              </Grid>
            </Grid>
          )}

          {/* Hook Filters */}
          <Paper sx={{ p: 2, mb: 3 }}>
            <Grid container spacing={2} alignItems="center">
              <Grid item xs={12} md={4}>
                <TextField
                  fullWidth
                  size="small"
                  placeholder="Search hook logs..."
                  value={hookSearch}
                  onChange={(e) => setHookSearch(e.target.value)}
                  InputProps={{
                    startAdornment: (
                      <InputAdornment position="start">
                        <SearchIcon />
                      </InputAdornment>
                    ),
                  }}
                />
              </Grid>
              <Grid item xs={12} md={3}>
                <FormControl fullWidth size="small">
                  <InputLabel>Hook</InputLabel>
                  <Select
                    value={hookFilter}
                    label="Hook"
                    onChange={(e) => setHookFilter(e.target.value)}
                  >
                    <MenuItem value="">All Hooks</MenuItem>
                    {uniqueHooks.map((hook) => (
                      <MenuItem key={hook} value={hook}>
                        {hook}
                      </MenuItem>
                    ))}
                  </Select>
                </FormControl>
              </Grid>
              <Grid item xs={12} md={3}>
                <FormControl fullWidth size="small">
                  <InputLabel>Status</InputLabel>
                  <Select
                    value={hookStatusFilter}
                    label="Status"
                    onChange={(e) => setHookStatusFilter(e.target.value)}
                  >
                    <MenuItem value="">All Statuses</MenuItem>
                    <MenuItem value="success">Success</MenuItem>
                    <MenuItem value="error">Error</MenuItem>
                    <MenuItem value="running">Running</MenuItem>
                    <MenuItem value="skipped">Skipped</MenuItem>
                  </Select>
                </FormControl>
              </Grid>
              <Grid item xs={12} md={2}>
                <Button
                  fullWidth
                  variant="outlined"
                  onClick={() => {
                    setHookSearch('');
                    setHookFilter('');
                    setHookStatusFilter('');
                  }}
                >
                  Clear
                </Button>
              </Grid>
            </Grid>
          </Paper>

          {/* Hook Logs Table */}
          <TableContainer component={Paper}>
            {hookLoading && <LinearProgress />}
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell width={50} />
                  <TableCell>Timestamp</TableCell>
                  <TableCell>Hook Name</TableCell>
                  <TableCell>Status</TableCell>
                  <TableCell>Message</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {hookError ? (
                  <TableRow>
                    <TableCell colSpan={5}>
                      <Alert severity="error">{hookError}</Alert>
                    </TableCell>
                  </TableRow>
                ) : hookExecutions.length === 0 ? (
                  <TableRow>
                    <TableCell colSpan={5}>
                      <Alert severity="info">
                        No hook executions found. Hooks will appear here once they are triggered.
                      </Alert>
                    </TableCell>
                  </TableRow>
                ) : (
                  hookExecutions.map((exec) => (
                    <React.Fragment key={exec.id}>
                      <TableRow
                        hover
                        sx={{ cursor: 'pointer' }}
                        onClick={() => toggleHookRowExpand(exec.id)}
                      >
                        <TableCell>
                          <IconButton size="small">
                            {expandedHookRows.has(exec.id) ? <ExpandLessIcon /> : <ExpandMoreIcon />}
                          </IconButton>
                        </TableCell>
                        <TableCell>
                          <Typography variant="body2" sx={{ fontFamily: 'monospace', fontSize: '0.8rem' }}>
                            {formatTimestamp(exec.timestamp)}
                          </Typography>
                        </TableCell>
                        <TableCell>
                          <Chip
                            size="small"
                            label={exec.hook_name}
                            sx={{
                              fontFamily: 'monospace',
                              fontWeight: 600,
                              backgroundColor: alpha(theme.palette.secondary.main, 0.1),
                            }}
                          />
                        </TableCell>
                        <TableCell>{getStatusChip(exec.status)}</TableCell>
                        <TableCell>
                          <Typography
                            variant="body2"
                            sx={{
                              fontFamily: 'monospace',
                              fontSize: '0.75rem',
                              maxWidth: 350,
                              overflow: 'hidden',
                              textOverflow: 'ellipsis',
                              whiteSpace: 'nowrap',
                              color: exec.error ? theme.palette.error.main : 'inherit',
                            }}
                          >
                            {exec.error || exec.message?.slice(0, 80) || '-'}
                            {exec.message && exec.message.length > 80 ? '...' : ''}
                          </Typography>
                        </TableCell>
                      </TableRow>
                      <TableRow>
                        <TableCell colSpan={5} sx={{ py: 0 }}>
                          <Collapse in={expandedHookRows.has(exec.id)} timeout="auto" unmountOnExit>
                            <Box sx={{ p: 2, backgroundColor: alpha(theme.palette.background.default, 0.5) }}>
                              <Typography variant="subtitle2" fontWeight={600} gutterBottom>
                                Full Message
                              </Typography>
                              <Paper
                                sx={{
                                  p: 1.5,
                                  backgroundColor: exec.error
                                    ? alpha(theme.palette.error.main, 0.1)
                                    : theme.palette.mode === 'dark'
                                    ? '#1a1a2e'
                                    : '#f5f5f5',
                                  maxHeight: 200,
                                  overflow: 'auto',
                                }}
                              >
                                <pre
                                  style={{
                                    margin: 0,
                                    fontFamily: 'monospace',
                                    fontSize: '0.75rem',
                                    whiteSpace: 'pre-wrap',
                                    color: exec.error ? theme.palette.error.main : 'inherit',
                                  }}
                                >
                                  {exec.error || exec.message || 'No details available'}
                                </pre>
                              </Paper>
                            </Box>
                          </Collapse>
                        </TableCell>
                      </TableRow>
                    </React.Fragment>
                  ))
                )}
              </TableBody>
            </Table>
          </TableContainer>

          {/* Hook Pagination */}
          {hookTotal > limit && (
            <Box sx={{ display: 'flex', justifyContent: 'center', mt: 2 }}>
              <Pagination
                count={Math.ceil(hookTotal / limit)}
                page={hookPage}
                onChange={(_, newPage) => setHookPage(newPage)}
                color="primary"
              />
            </Box>
          )}

          {/* Most Used Hooks */}
          {hookStats && hookStats.hooks_used && Object.keys(hookStats.hooks_used).length > 0 && (
            <Paper sx={{ p: 2, mt: 3 }}>
              <Typography variant="h6" fontWeight={600} gutterBottom>
                Most Used Hooks
              </Typography>
              <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                {Object.entries(hookStats.hooks_used)
                  .slice(0, 10)
                  .map(([hook, count]) => (
                    <Chip
                      key={hook}
                      label={`${hook} (${count})`}
                      onClick={() => setHookFilter(hook)}
                      sx={{
                        fontFamily: 'monospace',
                        cursor: 'pointer',
                        '&:hover': {
                          backgroundColor: alpha(theme.palette.secondary.main, 0.2),
                        },
                      }}
                    />
                  ))}
              </Box>
            </Paper>
          )}
        </>
      )}
    </Box>
  );
};

export default MCPLogs;
