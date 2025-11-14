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
  Container,
  useTheme,
  Stack,
  Paper,
  Divider,
} from '@mui/material';
import {
  Assignment as TaskIcon,
  PlayArrow as PlayIcon,
  CheckCircle as DoneIcon,
  Warning as BlockedIcon,
  TrendingUp as TrendingIcon,
  Folder as ProjectIcon,
  Speed as SpeedIcon,
  Code as CodeIcon,
} from '@mui/icons-material';
import { useQuery } from 'react-query';
import { getActiveProject, getTaskQueue, getConnectionStatus } from '../services/api';
import MetricCard from '../components/MetricCard';

const Dashboard: React.FC = () => {
  const theme = useTheme();
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
      <Box sx={{ minHeight: '100vh', pb: 4 }}>
        <Container maxWidth="xl">
          <Box py={4}>
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
              Dashboard
            </Typography>
            <Typography variant="body1" color="text.secondary" mb={4}>
              Overview of your project and task progress
            </Typography>
          </Box>
          <Grid container spacing={3}>
            {[1, 2, 3, 4].map((i) => (
              <Grid item xs={12} sm={6} lg={3} key={i}>
                <Skeleton variant="rectangular" height={140} sx={{ borderRadius: 2 }} />
              </Grid>
            ))}
          </Grid>
        </Container>
      </Box>
    );
  }

  if (projectError || queueError) {
    return (
      <Box sx={{ minHeight: '100vh', pb: 4 }}>
        <Container maxWidth="xl">
          <Box py={4}>
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
              Dashboard
            </Typography>
            <Typography variant="body1" color="text.secondary" mb={4}>
              Overview of your project and task progress
            </Typography>
          </Box>
          <Alert severity="error" sx={{ borderRadius: 2 }}>
            Failed to load dashboard data. Please check your connection and try again.
          </Alert>
        </Container>
      </Box>
    );
  }

  if (!project) {
    return (
      <Box sx={{ minHeight: '100vh', pb: 4 }}>
        <Container maxWidth="xl">
          <Box py={4}>
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
              Welcome to ClaudeTask
            </Typography>
            <Typography variant="body1" color="text.secondary" mb={4}>
              Get started with AI-powered task management
            </Typography>
          </Box>
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
        </Container>
      </Box>
    );
  }

  return (
    <Box className="animate-fade-in" sx={{ minHeight: '100vh', pb: 4 }}>
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
                  background: `linear-gradient(135deg, ${theme.palette.primary.main}, ${theme.palette.primary.light})`,
                  WebkitBackgroundClip: 'text',
                  WebkitTextFillColor: 'transparent',
                  mb: 1,
                }}
              >
                Dashboard
              </Typography>
              <Typography variant="body1" color="text.secondary">
                Overview of your project and task progress
              </Typography>
            </Box>
            {project && (
              <Chip
                icon={<ProjectIcon />}
                label={project.name}
                sx={{
                  px: 2,
                  py: 2.5,
                  height: 'auto',
                  fontSize: '0.9rem',
                  fontWeight: 600,
                  background: `linear-gradient(135deg, ${alpha(theme.palette.primary.main, 0.15)}, ${alpha(theme.palette.primary.main, 0.05)})`,
                  border: `1px solid ${alpha(theme.palette.primary.main, 0.2)}`,
                  color: theme.palette.primary.main,
                }}
              />
            )}
          </Stack>

          {/* Connection Status Alert */}
          {connection && (
            <Alert
              severity={connection.connected ? 'success' : 'warning'}
              sx={{
                mb: 3,
                borderRadius: 2,
                border: connection.connected ? '1px solid' : 'none',
                borderColor: connection.connected ? alpha(theme.palette.success.main, 0.3) : 'transparent',
                background: connection.connected
                  ? alpha(theme.palette.success.main, 0.05)
                  : alpha(theme.palette.warning.main, 0.05),
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

          {/* Statistics Cards Grid */}
          <Grid container spacing={2} mb={4}>
            {[
              {
                label: 'Pending Tasks',
                value: queue?.pending_tasks.length || 0,
                color: theme.palette.primary.main,
                icon: TaskIcon,
                subtitle: 'Waiting to start'
              },
              {
                label: 'In Progress',
                value: queue?.in_progress_tasks.length || 0,
                color: theme.palette.warning.main,
                icon: PlayIcon,
                subtitle: 'Currently working'
              },
              {
                label: 'Completed Today',
                value: queue?.completed_today || 0,
                color: theme.palette.success.main,
                icon: DoneIcon,
                subtitle: 'Tasks finished'
              },
              {
                label: 'Total Tasks',
                value: (queue?.pending_tasks.length || 0) + (queue?.in_progress_tasks.length || 0),
                color: theme.palette.info.main,
                icon: TrendingIcon,
                subtitle: 'All active tasks'
              },
            ].map((stat) => (
              <Grid item xs={12} sm={6} lg={3} key={stat.label}>
                <Paper
                  sx={{
                    p: 3,
                    borderRadius: 2,
                    background: `linear-gradient(145deg, ${alpha(stat.color, 0.05)}, ${alpha(stat.color, 0.02)})`,
                    border: `1px solid ${alpha(stat.color, 0.15)}`,
                    transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
                    position: 'relative',
                    overflow: 'hidden',
                    '&:hover': {
                      transform: 'translateY(-4px)',
                      boxShadow: `0 12px 24px -6px ${alpha(stat.color, 0.2)}`,
                      border: `1px solid ${alpha(stat.color, 0.3)}`,
                    },
                    '&::before': {
                      content: '""',
                      position: 'absolute',
                      top: 0,
                      left: 0,
                      right: 0,
                      height: 4,
                      background: `linear-gradient(90deg, ${stat.color}, ${alpha(stat.color, 0.5)})`,
                    },
                  }}
                >
                  <Box display="flex" alignItems="start" justifyContent="space-between" mb={2}>
                    <Box
                      sx={{
                        width: 48,
                        height: 48,
                        borderRadius: 2,
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        background: `linear-gradient(135deg, ${alpha(stat.color, 0.2)}, ${alpha(stat.color, 0.1)})`,
                        border: `1px solid ${alpha(stat.color, 0.3)}`,
                      }}
                    >
                      <stat.icon sx={{ color: stat.color, fontSize: 24 }} />
                    </Box>
                  </Box>
                  <Typography variant="body2" color="text.secondary" gutterBottom sx={{ fontSize: '0.85rem' }}>
                    {stat.label}
                  </Typography>
                  <Typography variant="h3" sx={{ fontWeight: 700, color: stat.color, mb: 0.5 }}>
                    {stat.value}
                  </Typography>
                  <Typography variant="caption" color="text.secondary">
                    {stat.subtitle}
                  </Typography>
                </Paper>
              </Grid>
            ))}
          </Grid>
        </Box>

        {/* Main Content Grid */}
        <Grid container spacing={3}>
          {/* Project Info Card */}
          <Grid item xs={12} md={6}>
            <Card
              sx={{
                height: '100%',
                display: 'flex',
                flexDirection: 'column',
                position: 'relative',
                overflow: 'visible',
                background: theme.palette.mode === 'dark'
                  ? `linear-gradient(145deg, ${alpha(theme.palette.background.paper, 0.9)}, ${alpha(theme.palette.background.paper, 0.95)})`
                  : theme.palette.background.paper,
                border: `1px solid ${alpha(theme.palette.primary.main, 0.1)}`,
                borderRadius: 3,
                transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
                '&:hover': {
                  transform: 'translateY(-4px)',
                  boxShadow: theme.palette.mode === 'dark'
                    ? `0 12px 24px -6px ${alpha(theme.palette.primary.main, 0.3)}`
                    : `0 12px 24px -6px ${alpha(theme.palette.primary.main, 0.15)}`,
                  border: `1px solid ${alpha(theme.palette.primary.main, 0.3)}`,
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
                  height: 4,
                  background: `linear-gradient(90deg, ${theme.palette.primary.main}, ${theme.palette.primary.light})`,
                  borderTopLeftRadius: 12,
                  borderTopRightRadius: 12,
                }}
              />

              <CardContent sx={{ flexGrow: 1, pt: 3, p: 3 }}>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5, mb: 3 }}>
                  <Box
                    sx={{
                      width: 48,
                      height: 48,
                      borderRadius: 2,
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      background: `linear-gradient(135deg, ${alpha(theme.palette.primary.main, 0.2)}, ${alpha(theme.palette.primary.light, 0.1)})`,
                      border: `1px solid ${alpha(theme.palette.primary.main, 0.2)}`,
                    }}
                  >
                    <ProjectIcon sx={{ color: theme.palette.primary.main, fontSize: 28 }} />
                  </Box>
                  <Typography variant="h6" sx={{ fontWeight: 600 }}>
                    Active Project
                  </Typography>
                </Box>

                <Typography variant="h5" sx={{ fontWeight: 700, mb: 1 }}>
                  {project.name}
                </Typography>

                <Typography variant="body2" color="text.secondary" sx={{ mb: 3, wordBreak: 'break-all' }}>
                  {project.path}
                </Typography>

                <Divider sx={{ my: 2 }} />

                {project.tech_stack.length > 0 && (
                  <Box>
                    <Typography variant="subtitle2" sx={{ fontWeight: 600, mb: 1.5, display: 'flex', alignItems: 'center', gap: 0.5 }}>
                      <CodeIcon sx={{ fontSize: 18 }} />
                      Technology Stack
                    </Typography>
                    <Stack direction="row" spacing={1} flexWrap="wrap" useFlexGap>
                      {project.tech_stack.map((tech) => (
                        <Chip
                          key={tech}
                          label={tech}
                          size="small"
                          sx={{
                            fontWeight: 500,
                            background: `linear-gradient(135deg, ${alpha(theme.palette.primary.main, 0.15)}, ${alpha(theme.palette.primary.main, 0.05)})`,
                            color: theme.palette.primary.main,
                            border: `1px solid ${alpha(theme.palette.primary.main, 0.2)}`,
                          }}
                        />
                      ))}
                    </Stack>
                  </Box>
                )}
              </CardContent>
            </Card>
          </Grid>

          {/* Active Tasks Card */}
          <Grid item xs={12} md={6}>
            <Card
              sx={{
                height: '100%',
                display: 'flex',
                flexDirection: 'column',
                position: 'relative',
                overflow: 'visible',
                background: theme.palette.mode === 'dark'
                  ? `linear-gradient(145deg, ${alpha(theme.palette.background.paper, 0.9)}, ${alpha(theme.palette.background.paper, 0.95)})`
                  : theme.palette.background.paper,
                border: `1px solid ${alpha(theme.palette.warning.main, 0.1)}`,
                borderRadius: 3,
                transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
                '&:hover': {
                  transform: 'translateY(-4px)',
                  boxShadow: theme.palette.mode === 'dark'
                    ? `0 12px 24px -6px ${alpha(theme.palette.warning.main, 0.3)}`
                    : `0 12px 24px -6px ${alpha(theme.palette.warning.main, 0.15)}`,
                  border: `1px solid ${alpha(theme.palette.warning.main, 0.3)}`,
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
                  height: 4,
                  background: `linear-gradient(90deg, ${theme.palette.warning.main}, ${theme.palette.warning.light})`,
                  borderTopLeftRadius: 12,
                  borderTopRightRadius: 12,
                }}
              />

              <CardContent sx={{ flexGrow: 1, pt: 3, p: 3 }}>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5, mb: 3 }}>
                  <Box
                    sx={{
                      width: 48,
                      height: 48,
                      borderRadius: 2,
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      background: `linear-gradient(135deg, ${alpha(theme.palette.warning.main, 0.2)}, ${alpha(theme.palette.warning.light, 0.1)})`,
                      border: `1px solid ${alpha(theme.palette.warning.main, 0.2)}`,
                    }}
                  >
                    <SpeedIcon sx={{ color: theme.palette.warning.main, fontSize: 28 }} />
                  </Box>
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
                          borderColor: alpha(theme.palette.divider, 0.5),
                          background: alpha(theme.palette.background.paper, 0.5),
                          transition: 'all 0.2s cubic-bezier(0.4, 0, 0.2, 1)',
                          '&:hover': {
                            bgcolor: alpha(theme.palette.primary.main, 0.05),
                            borderColor: theme.palette.primary.main,
                            transform: 'translateX(4px)',
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
                            <Stack direction="row" spacing={0.5} mt={0.5} flexWrap="wrap" useFlexGap>
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
                            </Stack>
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

          {/* Pending Tasks Card */}
          <Grid item xs={12}>
            <Card
              sx={{
                position: 'relative',
                overflow: 'visible',
                background: theme.palette.mode === 'dark'
                  ? `linear-gradient(145deg, ${alpha(theme.palette.background.paper, 0.9)}, ${alpha(theme.palette.background.paper, 0.95)})`
                  : theme.palette.background.paper,
                border: `1px solid ${alpha(theme.palette.primary.main, 0.1)}`,
                borderRadius: 3,
                transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
                '&:hover': {
                  transform: 'translateY(-4px)',
                  boxShadow: theme.palette.mode === 'dark'
                    ? `0 12px 24px -6px ${alpha(theme.palette.primary.main, 0.3)}`
                    : `0 12px 24px -6px ${alpha(theme.palette.primary.main, 0.15)}`,
                  border: `1px solid ${alpha(theme.palette.primary.main, 0.3)}`,
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
                  height: 4,
                  background: `linear-gradient(90deg, ${theme.palette.primary.main}, ${theme.palette.info.main})`,
                  borderTopLeftRadius: 12,
                  borderTopRightRadius: 12,
                }}
              />

              <CardContent sx={{ pt: 3, p: 3 }}>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5, mb: 3 }}>
                  <Box
                    sx={{
                      width: 48,
                      height: 48,
                      borderRadius: 2,
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      background: `linear-gradient(135deg, ${alpha(theme.palette.primary.main, 0.2)}, ${alpha(theme.palette.primary.light, 0.1)})`,
                      border: `1px solid ${alpha(theme.palette.primary.main, 0.2)}`,
                    }}
                  >
                    <TaskIcon sx={{ color: theme.palette.primary.main, fontSize: 28 }} />
                  </Box>
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
                            transition: 'all 0.2s cubic-bezier(0.4, 0, 0.2, 1)',
                            border: `1px solid ${alpha(theme.palette.divider, 0.5)}`,
                            background: alpha(theme.palette.background.paper, 0.5),
                            '&:hover': {
                              borderColor: theme.palette.primary.main,
                              bgcolor: alpha(theme.palette.primary.main, 0.02),
                              transform: 'translateY(-2px)',
                              boxShadow: `0 8px 16px -4px ${alpha(theme.palette.primary.main, 0.15)}`,
                            }
                          }}
                        >
                          <CardContent sx={{ p: 2 }}>
                            <Typography variant="body2" sx={{ fontWeight: 600, mb: 1 }}>
                              {task.title}
                            </Typography>
                            <Stack direction="row" spacing={0.5} flexWrap="wrap" useFlexGap>
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
                            </Stack>
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
      </Container>
    </Box>
  );
};

export default Dashboard;
