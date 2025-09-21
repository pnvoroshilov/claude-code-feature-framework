import React from 'react';
import {
  Box,
  Grid,
  Card,
  CardContent,
  Typography,
  CircularProgress,
  Alert,
  Chip,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  IconButton,
} from '@mui/material';
import {
  Assignment as TaskIcon,
  PlayArrow as PlayIcon,
  CheckCircle as DoneIcon,
  Warning as BlockedIcon,
} from '@mui/icons-material';
import { useQuery } from 'react-query';
import { getActiveProject, getTaskQueue, getConnectionStatus } from '../services/api';

const Dashboard: React.FC = () => {
  const { data: project, isLoading: projectLoading, error: projectError } = useQuery(
    'activeProject',
    getActiveProject,
    { refetchInterval: 30000 }
  );

  const { data: queue, isLoading: queueLoading, error: queueError } = useQuery(
    'taskQueue',
    getTaskQueue,
    { 
      refetchInterval: 10000,
      enabled: !!project
    }
  );

  const { data: connection, isLoading: connectionLoading } = useQuery(
    'connectionStatus',
    getConnectionStatus,
    { refetchInterval: 10000 }
  );

  if (projectLoading || queueLoading || connectionLoading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress />
      </Box>
    );
  }

  if (projectError || queueError) {
    return (
      <Alert severity="error">
        Failed to load dashboard data. Please check your connection.
      </Alert>
    );
  }

  if (!project) {
    return (
      <Box>
        <Typography variant="h4" gutterBottom>
          Welcome to ClaudeTask
        </Typography>
        <Alert severity="info" sx={{ mb: 3 }}>
          No active project found. Please initialize a project to get started.
        </Alert>
      </Box>
    );
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'Done': return 'success';
      case 'In Progress': return 'primary';
      case 'Testing': return 'warning';
      case 'Code Review': return 'secondary';
      case 'Blocked': return 'error';
      default: return 'default';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'Done': return <DoneIcon />;
      case 'In Progress': return <PlayIcon />;
      case 'Blocked': return <BlockedIcon />;
      default: return <TaskIcon />;
    }
  };

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Dashboard
      </Typography>

      {/* Connection Status */}
      <Alert 
        severity={connection?.connected ? 'success' : 'warning'} 
        sx={{ mb: 3 }}
      >
        {connection?.connected ? (
          `✅ Connected to ClaudeTask - Project: ${connection.project_name}`
        ) : (
          `⚠️ Claude Code not connected - ${connection?.error || 'Unknown error'}`
        )}
      </Alert>

      <Grid container spacing={3}>
        {/* Project Info */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Active Project
              </Typography>
              <Typography variant="h5" color="primary" gutterBottom>
                {project.name}
              </Typography>
              <Typography variant="body2" color="text.secondary" gutterBottom>
                {project.path}
              </Typography>
              {project.tech_stack.length > 0 && (
                <Box sx={{ mt: 2 }}>
                  <Typography variant="subtitle2" gutterBottom>
                    Technologies:
                  </Typography>
                  <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                    {project.tech_stack.map((tech) => (
                      <Chip key={tech} label={tech} size="small" />
                    ))}
                  </Box>
                </Box>
              )}
            </CardContent>
          </Card>
        </Grid>

        {/* Task Statistics */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Task Statistics
              </Typography>
              <Grid container spacing={2}>
                <Grid item xs={4}>
                  <Box textAlign="center">
                    <Typography variant="h4" color="primary">
                      {queue?.pending_tasks.length || 0}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Pending
                    </Typography>
                  </Box>
                </Grid>
                <Grid item xs={4}>
                  <Box textAlign="center">
                    <Typography variant="h4" color="warning.main">
                      {queue?.in_progress_tasks.length || 0}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      In Progress
                    </Typography>
                  </Box>
                </Grid>
                <Grid item xs={4}>
                  <Box textAlign="center">
                    <Typography variant="h4" color="success.main">
                      {queue?.completed_today || 0}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Completed Today
                    </Typography>
                  </Box>
                </Grid>
              </Grid>
            </CardContent>
          </Card>
        </Grid>

        {/* Active Tasks */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Active Tasks
              </Typography>
              {queue?.in_progress_tasks.length ? (
                <List>
                  {queue.in_progress_tasks.map((task) => (
                    <ListItem key={task.id} divider>
                      <ListItemIcon>
                        {getStatusIcon(task.status)}
                      </ListItemIcon>
                      <ListItemText
                        primary={task.title}
                        secondary={
                          <Box sx={{ mt: 1 }}>
                            <Chip
                              label={task.status}
                              size="small"
                              color={getStatusColor(task.status) as any}
                            />
                            {task.assigned_agent && (
                              <Chip
                                label={`Agent: ${task.assigned_agent}`}
                                size="small"
                                sx={{ ml: 1 }}
                              />
                            )}
                          </Box>
                        }
                      />
                    </ListItem>
                  ))}
                </List>
              ) : (
                <Typography variant="body2" color="text.secondary">
                  No active tasks
                </Typography>
              )}
            </CardContent>
          </Card>
        </Grid>

        {/* Pending Tasks */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Next Tasks in Queue
              </Typography>
              {queue?.pending_tasks.length ? (
                <List>
                  {queue.pending_tasks.slice(0, 5).map((task) => (
                    <ListItem key={task.id} divider>
                      <ListItemIcon>
                        <TaskIcon />
                      </ListItemIcon>
                      <ListItemText
                        primary={task.title}
                        secondary={
                          <Box sx={{ mt: 1 }}>
                            <Chip
                              label={task.priority}
                              size="small"
                              color={
                                task.priority === 'High' ? 'error' :
                                task.priority === 'Medium' ? 'warning' : 'default'
                              }
                            />
                            <Chip
                              label={task.type}
                              size="small"
                              sx={{ ml: 1 }}
                            />
                          </Box>
                        }
                      />
                    </ListItem>
                  ))}
                </List>
              ) : (
                <Typography variant="body2" color="text.secondary">
                  No pending tasks
                </Typography>
              )}
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
};

export default Dashboard;