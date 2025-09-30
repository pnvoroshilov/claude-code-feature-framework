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
  alpha,
  Skeleton,
} from '@mui/material';
import {
  Assignment as TaskIcon,
  PlayArrow as PlayIcon,
  CheckCircle as DoneIcon,
  Warning as BlockedIcon,
  TrendingUp as TrendingIcon,
  Folder as ProjectIcon,
  Speed as SpeedIcon,
} from '@mui/icons-material';
import { useQuery } from 'react-query';
import { getActiveProject, getTaskQueue, getConnectionStatus } from '../services/api';
import MetricCard from '../components/MetricCard';

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

  if (projectLoading || queueLoading || connectionLoading) {
    return (
      <Box>
        <Typography variant="h4" gutterBottom sx={{ fontWeight: 700, mb: 3 }}>
          Dashboard
        </Typography>
        <Grid container spacing={3}>
          {[1, 2, 3, 4].map((i) => (
            <Grid item xs={12} sm={6} lg={3} key={i}>
              <Skeleton variant="rectangular" height={140} sx={{ borderRadius: 2 }} />
            </Grid>
          ))}
        </Grid>
      </Box>
    );
  }

  if (projectError || queueError) {
    return (
      <Box>
        <Typography variant="h4" gutterBottom sx={{ fontWeight: 700, mb: 3 }}>
          Dashboard
        </Typography>
        <Alert severity="error" sx={{ borderRadius: 2 }}>
          Failed to load dashboard data. Please check your connection and try again.
        </Alert>
      </Box>
    );
  }

  if (!project) {
    return (
      <Box>
        <Typography variant="h4" gutterBottom sx={{ fontWeight: 700, mb: 3 }}>
          Welcome to ClaudeTask
        </Typography>
        <Alert
          severity="info"
          sx={{
            borderRadius: 2,
            '& .MuiAlert-message': {
              width: '100%'
            }
          }}
        >
          <Typography variant="body1" gutterBottom sx={{ fontWeight: 600 }}>
            No active project found
          </Typography>
          <Typography variant="body2">
            Please initialize a project to get started with task management.
          </Typography>
        </Alert>
      </Box>
    );
  }

  return (
    <Box className="animate-fade-in">
      {/* Page Header */}
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" gutterBottom sx={{ fontWeight: 700 }}>
          Dashboard
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Overview of your project and task progress
        </Typography>
      </Box>

      {/* Connection Status Alert */}
      {connection && (
        <Alert
          severity={connection.connected ? 'success' : 'warning'}
          sx={{
            mb: 3,
            borderRadius: 2,
            border: connection.connected ? '1px solid' : 'none',
            borderColor: connection.connected ? alpha('#22c55e', 0.3) : 'transparent',
            background: connection.connected
              ? alpha('#22c55e', 0.05)
              : alpha('#f59e0b', 0.05),
          }}
        >
          {connection.connected ? (
            <Box>
              <Typography variant="body2" sx={{ fontWeight: 600 }}>
                Connected to ClaudeTask
              </Typography>
              <Typography variant="caption">
                Project: {connection.project_name}
              </Typography>
            </Box>
          ) : (
            <Box>
              <Typography variant="body2" sx={{ fontWeight: 600 }}>
                Claude Code not connected
              </Typography>
              <Typography variant="caption">
                {connection.error || 'Unknown error'}
              </Typography>
            </Box>
          )}
        </Alert>
      )}

      {/* Metrics Grid */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} sm={6} lg={3}>
          <MetricCard
            title="Pending Tasks"
            value={queue?.pending_tasks.length || 0}
            icon={TaskIcon}
            color="primary"
            subtitle="Waiting to start"
          />
        </Grid>
        <Grid item xs={12} sm={6} lg={3}>
          <MetricCard
            title="In Progress"
            value={queue?.in_progress_tasks.length || 0}
            icon={PlayIcon}
            color="warning"
            subtitle="Currently working"
          />
        </Grid>
        <Grid item xs={12} sm={6} lg={3}>
          <MetricCard
            title="Completed Today"
            value={queue?.completed_today || 0}
            icon={DoneIcon}
            color="success"
            subtitle="Tasks finished"
          />
        </Grid>
        <Grid item xs={12} sm={6} lg={3}>
          <MetricCard
            title="Total Tasks"
            value={(queue?.pending_tasks.length || 0) + (queue?.in_progress_tasks.length || 0)}
            icon={TrendingIcon}
            color="info"
            subtitle="All active tasks"
          />
        </Grid>
      </Grid>

      {/* Project Info and Task Lists */}
      <Grid container spacing={3}>
        {/* Project Info */}
        <Grid item xs={12} md={6}>
          <Card
            sx={{
              height: '100%',
              transition: 'all 0.3s',
              '&:hover': {
                transform: 'translateY(-2px)',
                boxShadow: 6,
              }
            }}
          >
            <CardContent sx={{ p: 3 }}>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 3 }}>
                <ProjectIcon color="primary" />
                <Typography variant="h6" sx={{ fontWeight: 600 }}>
                  Active Project
                </Typography>
              </Box>

              <Typography variant="h5" sx={{ fontWeight: 700, mb: 1 }}>
                {project.name}
              </Typography>

              <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
                {project.path}
              </Typography>

              {project.tech_stack.length > 0 && (
                <Box>
                  <Typography variant="subtitle2" sx={{ fontWeight: 600, mb: 1.5 }}>
                    Technology Stack
                  </Typography>
                  <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                    {project.tech_stack.map((tech) => (
                      <Chip
                        key={tech}
                        label={tech}
                        size="small"
                        sx={{
                          fontWeight: 500,
                          background: alpha('#6366f1', 0.1),
                          color: 'primary.main',
                          border: '1px solid',
                          borderColor: alpha('#6366f1', 0.2),
                        }}
                      />
                    ))}
                  </Box>
                </Box>
              )}
            </CardContent>
          </Card>
        </Grid>

        {/* Active Tasks */}
        <Grid item xs={12} md={6}>
          <Card
            sx={{
              height: '100%',
              transition: 'all 0.3s',
              '&:hover': {
                transform: 'translateY(-2px)',
                boxShadow: 6,
              }
            }}
          >
            <CardContent sx={{ p: 3 }}>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 3 }}>
                <SpeedIcon color="warning" />
                <Typography variant="h6" sx={{ fontWeight: 600 }}>
                  Active Tasks
                </Typography>
              </Box>

              {queue?.in_progress_tasks.length ? (
                <List dense sx={{ maxHeight: 280, overflowY: 'auto' }}>
                  {queue.in_progress_tasks.map((task) => (
                    <ListItem
                      key={task.id}
                      sx={{
                        borderRadius: 2,
                        mb: 1,
                        border: '1px solid',
                        borderColor: 'divider',
                        transition: 'all 0.2s',
                        '&:hover': {
                          bgcolor: alpha('#6366f1', 0.05),
                          borderColor: 'primary.main',
                        }
                      }}
                    >
                      <ListItemIcon sx={{ minWidth: 40 }}>
                        {getStatusIcon(task.status)}
                      </ListItemIcon>
                      <ListItemText
                        primary={
                          <Typography variant="body2" sx={{ fontWeight: 600 }}>
                            {task.title}
                          </Typography>
                        }
                        secondary={
                          <Box sx={{ mt: 0.5, display: 'flex', gap: 0.5 }}>
                            <Chip
                              label={task.status}
                              size="small"
                              color={getStatusColor(task.status) as any}
                              sx={{ height: 20, fontSize: '0.7rem' }}
                            />
                            {task.assigned_agent && (
                              <Chip
                                label={`Agent: ${task.assigned_agent}`}
                                size="small"
                                variant="outlined"
                                sx={{ height: 20, fontSize: '0.7rem' }}
                              />
                            )}
                          </Box>
                        }
                      />
                    </ListItem>
                  ))}
                </List>
              ) : (
                <Box
                  sx={{
                    py: 4,
                    textAlign: 'center',
                    color: 'text.secondary'
                  }}
                >
                  <TaskIcon sx={{ fontSize: 48, opacity: 0.3, mb: 1 }} />
                  <Typography variant="body2">
                    No active tasks at the moment
                  </Typography>
                </Box>
              )}
            </CardContent>
          </Card>
        </Grid>

        {/* Pending Tasks */}
        <Grid item xs={12}>
          <Card
            sx={{
              transition: 'all 0.3s',
              '&:hover': {
                transform: 'translateY(-2px)',
                boxShadow: 6,
              }
            }}
          >
            <CardContent sx={{ p: 3 }}>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 3 }}>
                <TaskIcon color="primary" />
                <Typography variant="h6" sx={{ fontWeight: 600 }}>
                  Next Tasks in Queue
                </Typography>
              </Box>

              {queue?.pending_tasks.length ? (
                <Grid container spacing={2}>
                  {queue.pending_tasks.slice(0, 6).map((task) => (
                    <Grid item xs={12} sm={6} md={4} key={task.id}>
                      <Card
                        variant="outlined"
                        sx={{
                          transition: 'all 0.2s',
                          '&:hover': {
                            borderColor: 'primary.main',
                            bgcolor: alpha('#6366f1', 0.02),
                            transform: 'translateY(-2px)',
                          }
                        }}
                      >
                        <CardContent sx={{ p: 2 }}>
                          <Typography variant="body2" sx={{ fontWeight: 600, mb: 1 }}>
                            {task.title}
                          </Typography>
                          <Box sx={{ display: 'flex', gap: 0.5, flexWrap: 'wrap' }}>
                            <Chip
                              label={task.priority}
                              size="small"
                              color={
                                task.priority === 'High' ? 'error' :
                                task.priority === 'Medium' ? 'warning' : 'default'
                              }
                              sx={{ height: 20, fontSize: '0.7rem' }}
                            />
                            <Chip
                              label={task.type}
                              size="small"
                              variant="outlined"
                              sx={{ height: 20, fontSize: '0.7rem' }}
                            />
                          </Box>
                        </CardContent>
                      </Card>
                    </Grid>
                  ))}
                </Grid>
              ) : (
                <Box
                  sx={{
                    py: 4,
                    textAlign: 'center',
                    color: 'text.secondary'
                  }}
                >
                  <TaskIcon sx={{ fontSize: 48, opacity: 0.3, mb: 1 }} />
                  <Typography variant="body2">
                    No pending tasks in the queue
                  </Typography>
                </Box>
              )}
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
};

export default Dashboard;