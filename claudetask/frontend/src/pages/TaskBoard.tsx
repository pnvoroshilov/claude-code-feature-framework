import React, { useState } from 'react';
import {
  Box,
  Grid,
  Card,
  CardContent,
  Typography,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Chip,
  IconButton,
  List,
  ListItem,
  ListItemText,
  ListItemSecondaryAction,
  CircularProgress,
  Alert,
  Menu,
  Tooltip,
  Snackbar,
  Container,
  alpha,
  useTheme,
  Paper,
  Stack,
  InputAdornment,
  ToggleButtonGroup,
  ToggleButton,
  Badge,
  Divider,
} from '@mui/material';
import {
  Add as AddIcon,
  Delete as DeleteIcon,
  PlayArrow as StartIcon,
  MoreVert as MoreIcon,
  ArrowBack as BackIcon,
  CheckCircle as CompleteIcon,
  BugReport as BugIcon,
  Block as BlockIcon,
  Code as CodeIcon,
  Assignment as AssignmentIcon,
  Send as PRIcon,
  Edit as EditIcon,
  Save as SaveIcon,
  Cancel as CancelIcon,
  Search as SearchIcon,
  FilterList as FilterListIcon,
  CalendarToday as CalendarIcon,
  Person as PersonIcon,
  Timeline as TimelineIcon,
  Folder as FolderIcon,
} from '@mui/icons-material';
import { useQuery, useMutation, useQueryClient } from 'react-query';
import { useNavigate } from 'react-router-dom';
import { getTasks, createTask, updateTask, updateTaskStatus, deleteTask, Task, getActiveSessions, createClaudeSession, sendCommandToSession, getProjectSettings } from '../services/api';
import RealTerminal from '../components/RealTerminal';
import ProjectModeToggle from '../components/ProjectModeToggle';
import { useProject } from '../context/ProjectContext';

// Simple mode: Only 3 columns
const simpleStatusColumns = [
  { status: 'Backlog', title: 'Backlog', color: '#grey' },
  { status: 'In Progress', title: 'In Progress', color: '#orange' },
  { status: 'Done', title: 'Done', color: '#darkgreen' },
];

// Development mode: Full workflow with 7 columns
const developmentStatusColumns = [
  { status: 'Backlog', title: 'Backlog', color: '#grey' },
  { status: 'Analysis', title: 'Analysis', color: '#blue' },
  { status: 'In Progress', title: 'In Progress', color: '#orange' },
  { status: 'Testing', title: 'Testing', color: '#purple' },
  { status: 'Code Review', title: 'Code Review', color: '#brown' },
  { status: 'PR', title: 'Pull Request', color: '#1976d2' },
  { status: 'Done', title: 'Done', color: '#darkgreen' },
];

type ViewMode = 'kanban' | 'list';

const TaskBoard: React.FC = () => {
  const theme = useTheme();
  const navigate = useNavigate();
  const [createDialogOpen, setCreateDialogOpen] = useState(false);
  const [taskDetailsOpen, setTaskDetailsOpen] = useState(false);
  const [selectedTask, setSelectedTask] = useState<Task | null>(null);
  const [menuAnchorPosition, setMenuAnchorPosition] = useState<{ top: number; left: number } | null>(null);
  const [selectedTaskForStatus, setSelectedTaskForStatus] = useState<Task | null>(null);
  const [confirmDialogOpen, setConfirmDialogOpen] = useState(false);
  const [confirmAction, setConfirmAction] = useState<{ task: Task; newStatus: string; message: string } | null>(null);
  const [snackbar, setSnackbar] = useState<{ open: boolean; message: string; severity: 'success' | 'error' | 'info' | 'warning' }>({ open: false, message: '', severity: 'info' });
  const [newTask, setNewTask] = useState({
    title: '',
    description: '',
    type: 'Feature' as 'Feature' | 'Bug',
    priority: 'Medium' as 'High' | 'Medium' | 'Low',
  });
  const [isEditMode, setIsEditMode] = useState(false);
  const [editedTask, setEditedTask] = useState<{
    title: string;
    description: string;
    analysis: string;
  }>({ title: '', description: '', analysis: '' });
  const [saveLoading, setSaveLoading] = useState(false);
  const [viewMode, setViewMode] = useState<ViewMode>('kanban');
  const [searchQuery, setSearchQuery] = useState('');
  const [activeFilter, setActiveFilter] = useState<'all' | 'feature' | 'bug'>('all');

  const queryClient = useQueryClient();

  // Use project context instead of direct API call
  const {
    selectedProject: project,
    isConnected,
    connectionStatus,
    error: projectError
  } = useProject();

  // Select columns based on project mode
  const statusColumns = project?.project_mode === 'simple'
    ? simpleStatusColumns
    : developmentStatusColumns;

  const { data: tasks, isLoading, error } = useQuery(
    ['tasks', project?.id],
    () => project ? getTasks(project.id) : Promise.resolve([]),
    { enabled: !!project }
  );

  const createTaskMutation = useMutation(
    (taskData: typeof newTask) => project ? createTask(project.id, taskData) : Promise.reject('No project'),
    {
      onSuccess: () => {
        queryClient.invalidateQueries(['tasks', project?.id]);
        setCreateDialogOpen(false);
        setNewTask({ title: '', description: '', type: 'Feature', priority: 'Medium' });
      },
    }
  );

  const updateStatusMutation = useMutation(
    ({ taskId, status }: { taskId: number; status: string }) => updateTaskStatus(taskId, status),
    {
      onSuccess: () => {
        queryClient.invalidateQueries(['tasks', project?.id]);
      },
    }
  );

  const deleteTaskMutation = useMutation(deleteTask, {
    onSuccess: () => {
      queryClient.invalidateQueries(['tasks', project?.id]);
    },
  });

  const updateTaskMutation = useMutation(
    ({ taskId, data }: { taskId: number; data: Partial<Task> }) => updateTask(taskId, data),
    {
      onSuccess: (updatedTask) => {
        queryClient.invalidateQueries(['tasks', project?.id]);
        // Update selected task if it's the same task
        if (selectedTask && selectedTask.id === updatedTask.id) {
          setSelectedTask(updatedTask);
        }
      },
    }
  );

  const handleCreateTask = () => {
    const titleTrimmed = newTask.title.trim();
    const descriptionTrimmed = newTask.description.trim();

    if (!titleTrimmed) {
      setSnackbar({ open: true, message: 'Title is required', severity: 'error' });
      return;
    }

    // Input validation with length limits
    if (titleTrimmed.length > 200) {
      setSnackbar({ open: true, message: 'Title must be 200 characters or less', severity: 'error' });
      return;
    }

    const taskData = {
      ...newTask,
      title: titleTrimmed,
      ...(descriptionTrimmed && { description: descriptionTrimmed })
    };

    createTaskMutation.mutate(taskData);
  };

  const handleStatusChange = async (taskId: number, newStatus: string) => {
    updateStatusMutation.mutate({ taskId, status: newStatus }, {
      onSuccess: async () => {
        setSnackbar({ open: true, message: `Task moved to ${newStatus}`, severity: 'success' });

        // Fetch project settings to check manual mode flags
        let projectSettings = null;
        if (project?.id) {
          try {
            projectSettings = await getProjectSettings(project.id);
          } catch (error) {
            console.error('Failed to fetch project settings:', error);
          }
        }

        // Define command mapping for each status based on workflow use cases
        let command: string | null = null;

        switch (newStatus) {
          case 'Analysis':
            // UC-01: Backlog → Analysis triggers /start-feature
            command = `/start-feature ${taskId}`;
            break;

          case 'In Progress':
            // UC-02: Analysis → In Progress triggers /start-develop
            command = `/start-develop`;
            break;

          case 'Testing':
            // UC-04: In Progress → Testing triggers /test command
            // The command handles both manual and automated modes
            command = `/test ${taskId}`;
            break;

          case 'Code Review':
            // UC-05: Testing → Code Review triggers /PR command
            // The command handles both manual and automated modes
            command = `/PR ${taskId}`;
            break;

          case 'PR':
          case 'Done':
            // No auto-commands for PR or Done statuses
            command = null;
            break;

          default:
            command = null;
        }

        // Auto-send command if one is defined
        if (command) {
          try {
            // Check for active Claude sessions
            const sessions = await getActiveSessions();
            // Ensure sessions is an array (extra safety check)
            const sessionsArray = Array.isArray(sessions) ? sessions : [];
            let targetSession = sessionsArray.find(s => s.task_id === taskId);

            if (!targetSession && sessionsArray.length > 0) {
              // If no session for this task but there are active sessions, use the first one
              targetSession = sessionsArray[0];
            }

            if (targetSession) {
              // Send command to existing session
              await sendCommandToSession(targetSession.session_id, command);
              setSnackbar({
                open: true,
                message: `Task moved to ${newStatus} and "${command}" command sent to Claude session`,
                severity: 'success'
              });
            } else {
              // Create new Claude session and send command
              try {
                const sessionResult = await createClaudeSession(taskId);
                if (sessionResult.success) {
                  // Capture command in closure to avoid null type issues
                  const commandToSend = command;
                  // Wait a moment for session to initialize
                  setTimeout(async () => {
                    try {
                      await sendCommandToSession(sessionResult.session_id, commandToSend);
                      setSnackbar({
                        open: true,
                        message: `Task moved to ${newStatus}, new Claude session created, and "${commandToSend}" command sent`,
                        severity: 'success'
                      });
                    } catch (error) {
                      console.error(`Failed to send ${commandToSend} command:`, error);
                      setSnackbar({
                        open: true,
                        message: `Task moved to ${newStatus} and Claude session created, but failed to send "${commandToSend}" command`,
                        severity: 'warning'
                      });
                    }
                  }, 2000);
                } else {
                  setSnackbar({
                    open: true,
                    message: `Task moved to ${newStatus} but failed to create Claude session: ${sessionResult.error}`,
                    severity: 'warning'
                  });
                }
              } catch (error) {
                console.error('Failed to create Claude session:', error);
                setSnackbar({
                  open: true,
                  message: `Task moved to ${newStatus} but failed to create Claude session`,
                  severity: 'warning'
                });
              }
            }
          } catch (error) {
            console.error(`Failed to handle Claude session for ${newStatus} task:`, error);
            setSnackbar({
              open: true,
              message: `Task moved to ${newStatus} but failed to handle Claude session`,
              severity: 'warning'
            });
          }
        }
      },
      onError: () => {
        setSnackbar({ open: true, message: 'Failed to update task status', severity: 'error' });
      }
    });
  };

  // Define valid status transitions
  const getValidTransitions = (currentStatus: string): Array<{ status: string; label: string; icon: JSX.Element; description: string; requiresConfirmation?: boolean }> => {
    const isSimpleMode = project?.project_mode === 'simple';

    if (isSimpleMode) {
      // Simple mode: only Backlog → In Progress → Done
      switch (currentStatus) {
        case 'Backlog':
          return [
            { status: 'In Progress', label: 'Start Working', icon: <StartIcon />, description: 'Begin working on this task' }
          ];
        case 'In Progress':
          return [
            { status: 'Done', label: 'Mark Complete', icon: <CompleteIcon />, description: 'Task is complete', requiresConfirmation: true },
            { status: 'Backlog', label: 'Back to Backlog', icon: <BackIcon />, description: 'Return to backlog' }
          ];
        case 'Done':
          return [
            { status: 'In Progress', label: 'Reopen', icon: <StartIcon />, description: 'Reopen this task' }
          ];
        // Handle tasks that might have old statuses from development mode
        case 'Analysis':
        case 'Testing':
        case 'Code Review':
        case 'PR':
          return [
            { status: 'In Progress', label: 'Move to In Progress', icon: <StartIcon />, description: 'Simplify to In Progress status' },
            { status: 'Done', label: 'Mark Complete', icon: <CompleteIcon />, description: 'Task is complete', requiresConfirmation: true }
          ];
        default:
          return [];
      }
    } else {
      // Development mode: full workflow
      switch (currentStatus) {
        case 'Backlog':
          return [
            { status: 'Analysis', label: 'Start Analysis', icon: <StartIcon />, description: 'Begin task analysis phase' }
          ];
        case 'Analysis':
          return [
            { status: 'In Progress', label: 'Start Development', icon: <CodeIcon />, description: 'Move to active development' },
            { status: 'Backlog', label: 'Back to Backlog', icon: <BackIcon />, description: 'Return to backlog for re-prioritization' }
          ];
        case 'In Progress':
          return [
            { status: 'Testing', label: 'Ready for Testing', icon: <BugIcon />, description: 'Code complete, ready for testing' },
            { status: 'Blocked', label: 'Mark as Blocked', icon: <BlockIcon />, description: 'Task is blocked by dependencies' },
            { status: 'Analysis', label: 'Back to Analysis', icon: <BackIcon />, description: 'Needs more analysis' }
          ];
        case 'Testing':
          return [
            { status: 'Code Review', label: 'Ready for Review', icon: <AssignmentIcon />, description: 'Testing complete, ready for code review' },
            { status: 'In Progress', label: 'Back to Development', icon: <BackIcon />, description: 'Issues found, back to development' },
            { status: 'Blocked', label: 'Mark as Blocked', icon: <BlockIcon />, description: 'Testing blocked by issues' }
          ];
        case 'Code Review':
          return [
            { status: 'PR', label: 'Create Pull Request', icon: <PRIcon />, description: 'Code approved, ready for PR' },
            { status: 'In Progress', label: 'Rework Required', icon: <BackIcon />, description: 'Code changes requested' }
          ];
        case 'PR':
          return [
            { status: 'Done', label: 'Mark Complete', icon: <CompleteIcon />, description: 'PR merged, task complete', requiresConfirmation: true },
            { status: 'Code Review', label: 'Back to Review', icon: <BackIcon />, description: 'PR changes requested' }
          ];
        case 'Blocked':
          return [
            { status: 'Analysis', label: 'Resume Analysis', icon: <StartIcon />, description: 'Blocker resolved, resume analysis' },
            { status: 'In Progress', label: 'Resume Development', icon: <CodeIcon />, description: 'Blocker resolved, resume development' },
            { status: 'Testing', label: 'Resume Testing', icon: <BugIcon />, description: 'Blocker resolved, resume testing' }
          ];
        default:
          return [];
      }
    }
  };

  const handleStatusMenuOpen = (event: React.MouseEvent<HTMLButtonElement>, task: Task) => {
    event.stopPropagation();
    const rect = event.currentTarget.getBoundingClientRect();
    setMenuAnchorPosition({
      top: rect.bottom + window.scrollY,
      left: rect.left + window.scrollX,
    });
    setSelectedTaskForStatus(task);
  };

  const handleStatusMenuClose = () => {
    setMenuAnchorPosition(null);
    setSelectedTaskForStatus(null);
  };

  const handleStatusTransition = (task: Task, newStatus: string, requiresConfirmation?: boolean, description?: string) => {
    if (requiresConfirmation) {
      setConfirmAction({ task, newStatus, message: description || `Are you sure you want to move this task to ${newStatus}?` });
      setConfirmDialogOpen(true);
    } else {
      handleStatusChange(task.id, newStatus);
    }
    handleStatusMenuClose();

    // Update selected task in detail dialog if it's the same task
    if (selectedTask && selectedTask.id === task.id) {
      setSelectedTask({ ...selectedTask, status: newStatus as Task['status'] });
    }
  };

  const handleConfirmStatusChange = () => {
    if (confirmAction) {
      handleStatusChange(confirmAction.task.id, confirmAction.newStatus);

      // Update selected task in detail dialog if it's the same task
      if (selectedTask && selectedTask.id === confirmAction.task.id) {
        setSelectedTask({ ...selectedTask, status: confirmAction.newStatus as Task['status'] });
      }
    }
    setConfirmDialogOpen(false);
    setConfirmAction(null);
  };

  const handleEditClick = () => {
    if (selectedTask) {
      setEditedTask({
        title: selectedTask.title,
        description: selectedTask.description || '',
        analysis: selectedTask.analysis || ''
      });
      setIsEditMode(true);
    }
  };

  const handleCancelEdit = () => {
    setIsEditMode(false);
    if (selectedTask) {
      setEditedTask({
        title: selectedTask.title,
        description: selectedTask.description || '',
        analysis: selectedTask.analysis || ''
      });
    }
  };

  const handleSaveEdit = async () => {
    if (!selectedTask || !editedTask.title.trim()) {
      setSnackbar({ open: true, message: 'Title is required', severity: 'error' });
      return;
    }

    // Input validation with length limits
    const titleTrimmed = editedTask.title.trim();
    const descriptionTrimmed = editedTask.description.trim();
    const analysisTrimmed = editedTask.analysis.trim();

    if (titleTrimmed.length > 200) {
      setSnackbar({ open: true, message: 'Title must be 200 characters or less', severity: 'error' });
      return;
    }

    if (analysisTrimmed.length > 5000) {
      setSnackbar({ open: true, message: 'Analysis must be 5000 characters or less', severity: 'error' });
      return;
    }

    setSaveLoading(true);
    try {
      const updateData = {
        title: titleTrimmed,
        ...(descriptionTrimmed && { description: descriptionTrimmed }),
        ...(analysisTrimmed && { analysis: analysisTrimmed })
      };

      await updateTaskMutation.mutateAsync({
        taskId: selectedTask.id,
        data: updateData
      });
      setIsEditMode(false);
      setSnackbar({ open: true, message: 'Task updated successfully', severity: 'success' });
    } catch (error) {
      console.error('Failed to update task:', error);
      setSnackbar({ open: true, message: 'Failed to update task', severity: 'error' });
    } finally {
      setSaveLoading(false);
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'Backlog': return <AssignmentIcon />;
      case 'Analysis': return <StartIcon />;
      case 'In Progress': return <CodeIcon />;
      case 'Testing': return <BugIcon />;
      case 'Code Review': return <AssignmentIcon />;
      case 'PR': return <PRIcon />;
      case 'Done': return <CompleteIcon />;
      case 'Blocked': return <BlockIcon />;
      default: return <AssignmentIcon />;
    }
  };

  const handleTaskClick = (task: Task) => {
    setSelectedTask(task);
    setTaskDetailsOpen(true);
    // Reset edit mode when opening a new task
    setIsEditMode(false);
    setEditedTask({
      title: task.title,
      description: task.description || '',
      analysis: task.analysis || ''
    });
  };

  const getTasksByStatus = (status: string) => {
    let filtered = tasks?.filter(task => task.status === status) || [];

    // Apply type filter
    if (activeFilter !== 'all') {
      filtered = filtered.filter(task =>
        task.type.toLowerCase() === activeFilter
      );
    }

    // Apply search filter
    if (searchQuery.trim()) {
      const query = searchQuery.toLowerCase();
      filtered = filtered.filter(task =>
        task.title.toLowerCase().includes(query) ||
        task.description?.toLowerCase().includes(query) ||
        task.id.toString().includes(query)
      );
    }

    return filtered;
  };

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'High': return 'error';
      case 'Medium': return 'warning';
      case 'Low': return 'success';
      default: return 'default';
    }
  };

  const getStatusColor = (status: string) => {
    const column = statusColumns.find(c => c.status === status);
    return column?.color || '#grey';
  };

  // Task Card Component - Compact modern design
  const TaskCard: React.FC<{ task: Task }> = ({ task }) => {
    const isBug = task.type === 'Bug';

    return (
      <Card
        sx={{
          mb: 1.5,
          position: 'relative',
          cursor: 'pointer',
          // Bug cards have reddish background
          background: isBug
            ? theme.palette.mode === 'dark'
              ? alpha(theme.palette.error.main, 0.12)
              : alpha(theme.palette.error.main, 0.04)
            : theme.palette.background.paper,
          border: `1px solid ${
            isBug
              ? alpha(theme.palette.error.main, 0.25)
              : alpha(theme.palette.divider, 0.12)
          }`,
          borderRadius: 1.5,
          transition: 'all 0.2s ease-in-out',
          '&:hover': {
            transform: 'translateY(-2px)',
            boxShadow: `0 4px 12px ${alpha(theme.palette.common.black, 0.08)}`,
            border: `1px solid ${
              isBug
                ? alpha(theme.palette.error.main, 0.4)
                : alpha(theme.palette.primary.main, 0.3)
            }`,
            '& .task-actions': {
              opacity: 1,
            },
          },
        }}
        onClick={() => handleTaskClick(task)}
      >
        <CardContent sx={{ p: 1.5, '&:last-child': { pb: 1.5 } }}>
          {/* Header with action buttons */}
          <Box display="flex" alignItems="flex-start" justifyContent="space-between" mb={1}>
            {/* Task ID badge */}
            <Chip
              label={`#${task.id}`}
              size="small"
              sx={{
                height: 18,
                fontSize: '0.65rem',
                fontWeight: 600,
                background: alpha(theme.palette.primary.main, 0.1),
                color: theme.palette.primary.main,
                '& .MuiChip-label': {
                  px: 0.75,
                },
              }}
            />

            {/* Action buttons */}
            <Box
              className="task-actions"
              sx={{
                display: 'flex',
                gap: 0.5,
                opacity: 0.6,
                transition: 'opacity 0.2s',
              }}
            >
              <IconButton
                size="small"
                onClick={(e) => {
                  e.stopPropagation();
                  handleStatusMenuOpen(e, task);
                }}
                sx={{
                  width: 24,
                  height: 24,
                  color: theme.palette.text.secondary,
                  '&:hover': {
                    background: alpha(theme.palette.primary.main, 0.1),
                    color: theme.palette.primary.main,
                  },
                }}
              >
                <MoreIcon sx={{ fontSize: 16 }} />
              </IconButton>

              <IconButton
                size="small"
                onClick={(e) => {
                  e.stopPropagation();
                  if (window.confirm(`Delete task "${task.title}"?`)) {
                    deleteTaskMutation.mutate(task.id);
                  }
                }}
                sx={{
                  width: 24,
                  height: 24,
                  color: theme.palette.text.secondary,
                  '&:hover': {
                    background: alpha(theme.palette.error.main, 0.1),
                    color: theme.palette.error.main,
                  },
                }}
              >
                <DeleteIcon sx={{ fontSize: 16 }} />
              </IconButton>
            </Box>
          </Box>

          {/* Task title */}
          <Typography
            variant="body2"
            sx={{
              fontWeight: 500,
              mb: 0.5,
              overflow: 'hidden',
              textOverflow: 'ellipsis',
              display: '-webkit-box',
              WebkitLineClamp: 2,
              WebkitBoxOrient: 'vertical',
              lineHeight: 1.4,
              fontSize: '0.875rem',
              color: isBug ? theme.palette.error.main : theme.palette.text.primary,
            }}
          >
            {task.title}
          </Typography>

          {/* Task description (first 200 chars) */}
          {task.description && (
            <Typography
              variant="caption"
              sx={{
                display: '-webkit-box',
                mb: 1,
                color: theme.palette.text.secondary,
                overflow: 'hidden',
                textOverflow: 'ellipsis',
                WebkitLineClamp: 3,
                WebkitBoxOrient: 'vertical',
                fontSize: '0.7rem',
                opacity: 0.8,
                lineHeight: 1.3,
              }}
            >
              {task.description.substring(0, 200)}
              {task.description.length > 200 ? '...' : ''}
            </Typography>
          )}

          {/* Priority and Type chips */}
          <Stack direction="row" spacing={0.5} alignItems="center">
            {/* Priority chip */}
            <Chip
              label={task.priority}
              size="small"
              color={getPriorityColor(task.priority) as any}
              sx={{
                height: 20,
                fontSize: '0.65rem',
                fontWeight: 600,
                '& .MuiChip-label': {
                  px: 0.75,
                },
              }}
            />

            {/* Type chip with icon */}
            <Chip
              icon={isBug ? <BugIcon sx={{ fontSize: 12 }} /> : <CodeIcon sx={{ fontSize: 12 }} />}
              label={task.type}
              size="small"
              variant="outlined"
              sx={{
                height: 20,
                fontSize: '0.65rem',
                fontWeight: 600,
                borderColor: isBug ? theme.palette.error.main : theme.palette.primary.main,
                color: isBug ? theme.palette.error.main : theme.palette.primary.main,
                '& .MuiChip-label': {
                  px: 0.5,
                },
                '& .MuiChip-icon': {
                  ml: 0.5,
                  mr: -0.25,
                },
              }}
            />
          </Stack>
        </CardContent>
      </Card>
    );
  };

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
                mb: 3,
              }}
            >
              Task Board
            </Typography>
            {projectError && (
              <Alert severity="error" sx={{ borderRadius: 2 }}>
                {projectError}
              </Alert>
            )}
            {!projectError && (
              <Alert severity="info" sx={{ borderRadius: 2 }}>
                Please select a project from the top menu to view tasks.
              </Alert>
            )}
          </Box>
        </Container>
      </Box>
    );
  }

  if (isLoading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress size={48} />
      </Box>
    );
  }

  if (error) {
    return (
      <Alert severity="error" sx={{ m: 2, borderRadius: 2 }}>
        Failed to load tasks. Please try again.
      </Alert>
    );
  }

  return (
    <Box sx={{ minHeight: '100vh', pb: 4 }}>
      {/* Project Mode and Worktree Toggle */}
      <ProjectModeToggle />

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
                Task Board
              </Typography>
              <Typography variant="body1" color="text.secondary" sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                Manage and track your project tasks
                {project && (
                  <Chip
                    size="small"
                    label={project.project_mode === 'simple' ? 'Simple Mode' : 'Development Mode'}
                    sx={{
                      height: 20,
                      fontSize: '0.7rem',
                      fontWeight: 600,
                      background: project.project_mode === 'simple'
                        ? `linear-gradient(135deg, ${alpha(theme.palette.info.main, 0.2)}, ${alpha(theme.palette.info.light, 0.1)})`
                        : `linear-gradient(135deg, ${alpha(theme.palette.secondary.main, 0.2)}, ${alpha(theme.palette.secondary.light, 0.1)})`,
                      border: `1px solid ${alpha(project.project_mode === 'simple' ? theme.palette.info.main : theme.palette.secondary.main, 0.3)}`,
                      color: project.project_mode === 'simple' ? theme.palette.info.dark : theme.palette.secondary.dark,
                    }}
                  />
                )}
                {isConnected && (
                  <Chip
                    size="small"
                    label="Real-time updates"
                    color="success"
                    sx={{ height: 20, fontSize: '0.7rem' }}
                  />
                )}
              </Typography>
            </Box>
            <Stack direction="row" spacing={2}>
              <Button
                variant="outlined"
                size="large"
                startIcon={<FolderIcon />}
                onClick={() => project && navigate(`/projects/${project.id}/files`)}
                disabled={!project}
                sx={{
                  borderRadius: 2,
                  px: 3,
                  py: 1.5,
                  borderWidth: 2,
                  '&:hover': {
                    borderWidth: 2,
                    transform: 'translateY(-2px)',
                  },
                }}
              >
                File Browser
              </Button>
              <Button
                variant="contained"
                size="large"
                startIcon={<AddIcon />}
                onClick={() => setCreateDialogOpen(true)}
                sx={{
                  borderRadius: 2,
                  px: 3,
                  py: 1.5,
                  background: `linear-gradient(135deg, ${theme.palette.primary.main}, ${theme.palette.primary.dark})`,
                  boxShadow: `0 8px 16px ${alpha(theme.palette.primary.main, 0.3)}`,
                  '&:hover': {
                    background: `linear-gradient(135deg, ${theme.palette.primary.dark}, ${theme.palette.primary.main})`,
                    transform: 'translateY(-2px)',
                    boxShadow: `0 12px 20px ${alpha(theme.palette.primary.main, 0.4)}`,
                },
              }}
            >
              New Task
            </Button>
          </Stack>
          </Stack>

          {/* Search and Filter Bar */}
          <Paper
            sx={{
              p: 2,
              mb: 3,
              borderRadius: 2,
              background: alpha(theme.palette.background.paper, 0.8),
              backdropFilter: 'blur(10px)',
              border: `1px solid ${alpha(theme.palette.primary.main, 0.1)}`,
            }}
          >
            <Stack
              direction={{ xs: 'column', md: 'row' }}
              spacing={2}
              alignItems="center"
              sx={{
                display: 'flex',
                justifyContent: 'space-between',
                width: '100%'
              }}
            >
              {/* Search - Left side */}
              <TextField
                placeholder="Search tasks..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                InputProps={{
                  startAdornment: (
                    <InputAdornment position="start">
                      <SearchIcon color="action" />
                    </InputAdornment>
                  ),
                }}
                sx={{
                  width: { xs: '100%', md: '400px' },
                  '& .MuiOutlinedInput-root': {
                    borderRadius: 2,
                  },
                }}
              />

              {/* Filter Toggle - Right side */}
              <Box sx={{ display: 'flex', gap: 2, flexShrink: 0 }}>
                <ToggleButtonGroup
                  value={activeFilter}
                  exclusive
                  onChange={(e, newFilter) => {
                    if (newFilter !== null) {
                      setActiveFilter(newFilter);
                    }
                  }}
                  sx={{
                    gap: 1.5,
                    '& .MuiToggleButton-root': {
                      borderRadius: 2,
                      px: 3,
                      py: 1.5,
                      minWidth: 100,
                      textTransform: 'none',
                      fontWeight: 500,
                      '&.Mui-selected': {
                        background: `linear-gradient(135deg, ${theme.palette.primary.main}, ${theme.palette.primary.dark})`,
                        color: theme.palette.primary.contrastText,
                        '&:hover': {
                          background: `linear-gradient(135deg, ${theme.palette.primary.dark}, ${theme.palette.primary.main})`,
                        },
                      },
                    },
                  }}
                >
                  <ToggleButton value="all">
                    All
                  </ToggleButton>
                  <ToggleButton value="feature">
                    Features
                  </ToggleButton>
                  <ToggleButton value="bug">
                    Bugs
                  </ToggleButton>
                </ToggleButtonGroup>
              </Box>
            </Stack>
          </Paper>
        </Box>

        {/* Kanban Board */}
        <Grid container spacing={3}>
          {statusColumns.map((column) => {
            const columnTasks = getTasksByStatus(column.status);
            return (
              <Grid item xs={12} sm={6} md={4} lg={project?.project_mode === 'simple' ? 4 : 1.71} key={column.status}>
                <Paper
                  sx={{
                    minHeight: '500px',
                    borderRadius: 2,
                    background: alpha(theme.palette.background.paper, 0.6),
                    backdropFilter: 'blur(10px)',
                    border: `1px solid ${alpha(theme.palette.primary.main, 0.1)}`,
                    overflow: 'hidden',
                  }}
                >
                  <Box
                    sx={{
                      p: 2,
                      background: `linear-gradient(135deg, ${alpha(column.color, 0.15)}, ${alpha(column.color, 0.05)})`,
                      borderBottom: `2px solid ${alpha(column.color, 0.3)}`,
                    }}
                  >
                    <Box display="flex" justifyContent="space-between" alignItems="center">
                      <Box display="flex" alignItems="center" gap={1}>
                        {getStatusIcon(column.status)}
                        <Typography variant="h6" sx={{ fontWeight: 600, color: column.color }}>
                          {column.title}
                        </Typography>
                      </Box>
                      <Chip
                        label={columnTasks.length}
                        size="small"
                        sx={{
                          bgcolor: column.color,
                          color: 'white',
                          fontWeight: 'bold',
                          minWidth: 32,
                          height: 24,
                        }}
                      />
                    </Box>
                  </Box>

                  <Box sx={{ p: 2 }}>
                    {columnTasks.length === 0 ? (
                      <Paper
                        sx={{
                          p: 4,
                          textAlign: 'center',
                          background: alpha(theme.palette.background.paper, 0.3),
                          border: `1px dashed ${alpha(theme.palette.text.secondary, 0.2)}`,
                          borderRadius: 2,
                        }}
                      >
                        <AssignmentIcon sx={{ fontSize: 48, color: theme.palette.text.disabled, mb: 1 }} />
                        <Typography variant="body2" color="text.secondary">
                          No tasks
                        </Typography>
                      </Paper>
                    ) : (
                      columnTasks.map((task) => <TaskCard key={task.id} task={task} />)
                    )}
                  </Box>
                </Paper>
              </Grid>
            );
          })}
        </Grid>
      </Container>

      {/* Create Task Dialog */}
      <Dialog
        open={createDialogOpen}
        onClose={() => setCreateDialogOpen(false)}
        maxWidth="sm"
        fullWidth
        PaperProps={{
          sx: {
            borderRadius: 3,
            background: theme.palette.background.paper,
          },
        }}
      >
        <DialogTitle sx={{ pb: 1 }}>
          <Typography variant="h5" fontWeight={600}>
            Create New Task
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Add a new task to your project
          </Typography>
        </DialogTitle>
        <DialogContent>
          <Stack spacing={3} mt={2}>
            <TextField
              autoFocus
              label="Title"
              fullWidth
              variant="outlined"
              value={newTask.title}
              onChange={(e) => setNewTask({ ...newTask, title: e.target.value })}
              required
              placeholder="Enter task title"
            />
            <TextField
              label="Description"
              fullWidth
              multiline
              rows={8}
              variant="outlined"
              value={newTask.description}
              onChange={(e) => setNewTask({ ...newTask, description: e.target.value })}
              placeholder="Describe the task in detail"
            />
            <FormControl fullWidth>
              <InputLabel>Type</InputLabel>
              <Select
                value={newTask.type}
                label="Type"
                onChange={(e) => setNewTask({ ...newTask, type: e.target.value as 'Feature' | 'Bug' })}
              >
                <MenuItem value="Feature">Feature</MenuItem>
                <MenuItem value="Bug">Bug</MenuItem>
              </Select>
            </FormControl>
            <FormControl fullWidth>
              <InputLabel>Priority</InputLabel>
              <Select
                value={newTask.priority}
                label="Priority"
                onChange={(e) => setNewTask({ ...newTask, priority: e.target.value as 'High' | 'Medium' | 'Low' })}
              >
                <MenuItem value="High">High</MenuItem>
                <MenuItem value="Medium">Medium</MenuItem>
                <MenuItem value="Low">Low</MenuItem>
              </Select>
            </FormControl>
          </Stack>
        </DialogContent>
        <DialogActions sx={{ px: 3, pb: 3 }}>
          <Button onClick={() => setCreateDialogOpen(false)} sx={{ borderRadius: 2 }}>
            Cancel
          </Button>
          <Button
            onClick={handleCreateTask}
            variant="contained"
            disabled={!newTask.title.trim() || createTaskMutation.isLoading}
            sx={{
              borderRadius: 2,
              px: 3,
              background: `linear-gradient(135deg, ${theme.palette.primary.main}, ${theme.palette.primary.dark})`,
            }}
          >
            {createTaskMutation.isLoading ? <CircularProgress size={24} /> : 'Create Task'}
          </Button>
        </DialogActions>
      </Dialog>

      {/* Status Transition Menu */}
      <Menu
        open={Boolean(menuAnchorPosition)}
        onClose={handleStatusMenuClose}
        anchorReference="anchorPosition"
        anchorPosition={menuAnchorPosition || undefined}
        PaperProps={{
          sx: {
            maxHeight: 300,
            width: '280px',
            borderRadius: 2,
          }
        }}
      >
        {selectedTaskForStatus && getValidTransitions(selectedTaskForStatus.status).map((transition) => (
          <MenuItem
            key={transition.status}
            onClick={() => handleStatusTransition(
              selectedTaskForStatus,
              transition.status,
              transition.requiresConfirmation,
              transition.description
            )}
            sx={{ py: 1.5 }}
          >
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5, width: '100%' }}>
              <Box sx={{ color: 'primary.main' }}>
                {transition.icon}
              </Box>
              <Box sx={{ flex: 1 }}>
                <Typography variant="body2" sx={{ fontWeight: 500 }}>
                  {transition.label}
                </Typography>
                <Typography variant="caption" color="text.secondary">
                  {transition.description}
                </Typography>
              </Box>
            </Box>
          </MenuItem>
        ))}
      </Menu>

      {/* Confirmation Dialog */}
      <Dialog
        open={confirmDialogOpen}
        onClose={() => setConfirmDialogOpen(false)}
        maxWidth="sm"
        fullWidth
        PaperProps={{
          sx: { borderRadius: 3 },
        }}
      >
        <DialogTitle>
          Confirm Status Change
        </DialogTitle>
        <DialogContent>
          <Typography>
            {confirmAction?.message}
          </Typography>
          {confirmAction?.newStatus === 'Done' && (
            <Alert severity="info" sx={{ mt: 2, borderRadius: 2 }}>
              This will mark the task as complete. Make sure the PR has been merged and all work is finished.
            </Alert>
          )}
        </DialogContent>
        <DialogActions sx={{ px: 3, pb: 3 }}>
          <Button onClick={() => setConfirmDialogOpen(false)} sx={{ borderRadius: 2 }}>Cancel</Button>
          <Button
            onClick={handleConfirmStatusChange}
            variant="contained"
            disabled={updateStatusMutation.isLoading}
            sx={{ borderRadius: 2 }}
          >
            {updateStatusMutation.isLoading ? <CircularProgress size={20} /> : 'Confirm'}
          </Button>
        </DialogActions>
      </Dialog>

      {/* Snackbar for notifications */}
      <Snackbar
        open={snackbar.open}
        autoHideDuration={6000}
        onClose={() => setSnackbar({ ...snackbar, open: false })}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}
      >
        <Alert
          onClose={() => setSnackbar({ ...snackbar, open: false })}
          severity={snackbar.severity}
          sx={{ width: '100%', borderRadius: 2 }}
        >
          {snackbar.message}
        </Alert>
      </Snackbar>

      {/* Task Details Dialog */}
      <Dialog
        open={taskDetailsOpen}
        onClose={() => setTaskDetailsOpen(false)}
        maxWidth="xl"
        fullWidth
        PaperProps={{
          sx: {
            height: '90vh',
            borderRadius: 3,
          },
        }}
      >
        <DialogTitle>
          <Box display="flex" justifyContent="space-between" alignItems="center">
            <Typography variant="h6">
              #{selectedTask?.id} - {isEditMode ? 'Editing Task' : selectedTask?.title}
            </Typography>
            <Box display="flex" gap={1} alignItems="center">
              {!isEditMode ? (
                <>
                  <Button
                    variant="outlined"
                    size="small"
                    startIcon={<EditIcon />}
                    onClick={handleEditClick}
                    sx={{ mr: 1, borderRadius: 2 }}
                  >
                    Edit
                  </Button>
                  <Chip
                    label={selectedTask?.priority}
                    size="small"
                    color={getPriorityColor(selectedTask?.priority || '') as any}
                  />
                  <Chip
                    label={selectedTask?.type}
                    size="small"
                    variant="outlined"
                  />
                  <Chip
                    label={selectedTask?.status}
                    size="small"
                    sx={{ bgcolor: alpha(getStatusColor(selectedTask?.status || ''), 0.2) }}
                  />
                </>
              ) : (
                <>
                  <Button
                    variant="contained"
                    size="small"
                    startIcon={saveLoading ? <CircularProgress size={16} /> : <SaveIcon />}
                    onClick={handleSaveEdit}
                    disabled={saveLoading || !editedTask.title.trim()}
                    sx={{ mr: 1, borderRadius: 2 }}
                  >
                    {saveLoading ? 'Saving...' : 'Save'}
                  </Button>
                  <Button
                    variant="outlined"
                    size="small"
                    startIcon={<CancelIcon />}
                    onClick={handleCancelEdit}
                    disabled={saveLoading}
                    sx={{ borderRadius: 2 }}
                  >
                    Cancel
                  </Button>
                </>
              )}
            </Box>
          </Box>
        </DialogTitle>
        <DialogContent>
          {selectedTask && (
            <Box>
              {isEditMode && (
                <>
                  <Typography variant="subtitle1" gutterBottom sx={{ fontWeight: 'bold' }}>
                    Title
                  </Typography>
                  <TextField
                    fullWidth
                    variant="outlined"
                    value={editedTask.title}
                    onChange={(e) => setEditedTask({ ...editedTask, title: e.target.value })}
                    placeholder="Enter task title"
                    required
                    error={!editedTask.title.trim()}
                    helperText={!editedTask.title.trim() ? 'Title is required' : ''}
                    sx={{ mb: 3 }}
                  />
                </>
              )}

              <Typography variant="subtitle1" gutterBottom sx={{ fontWeight: 'bold' }}>
                Description
              </Typography>
              {isEditMode ? (
                <TextField
                  fullWidth
                  multiline
                  rows={12}
                  variant="outlined"
                  value={editedTask.description}
                  onChange={(e) => setEditedTask({ ...editedTask, description: e.target.value })}
                  placeholder="Enter task description"
                  sx={{ mb: 3 }}
                />
              ) : (
                <Typography variant="body1" paragraph sx={{ whiteSpace: 'pre-wrap', mb: 3 }}>
                  {selectedTask.description || 'No description provided'}
                </Typography>
              )}

              <Typography variant="subtitle1" gutterBottom sx={{ fontWeight: 'bold' }}>
                Analysis
              </Typography>
              {isEditMode ? (
                <TextField
                  fullWidth
                  multiline
                  rows={6}
                  variant="outlined"
                  value={editedTask.analysis}
                  onChange={(e) => setEditedTask({ ...editedTask, analysis: e.target.value })}
                  placeholder="Enter task analysis"
                  sx={{
                    mb: 3,
                    '& .MuiInputBase-input': {
                      fontFamily: 'monospace',
                      fontSize: '0.875rem'
                    }
                  }}
                />
              ) : (
                selectedTask.analysis ? (
                  <Typography
                    variant="body2"
                    paragraph
                    sx={{
                      whiteSpace: 'pre-wrap',
                      bgcolor: alpha(theme.palette.background.default, 0.5),
                      color: theme.palette.text.primary,
                      p: 2,
                      borderRadius: 2,
                      fontFamily: 'monospace',
                      mb: 3
                    }}
                  >
                    {selectedTask.analysis}
                  </Typography>
                ) : (
                  <Typography variant="body1" paragraph sx={{ fontStyle: 'italic', color: 'text.secondary', mb: 3 }}>
                    No analysis provided
                  </Typography>
                )
              )}

              {!isEditMode && selectedTask.stage_results && selectedTask.stage_results.length > 0 && (
                <>
                  <Typography variant="subtitle1" gutterBottom sx={{ fontWeight: 'bold', mt: 3 }}>
                    Stage Results
                  </Typography>
                  <Box sx={{
                    bgcolor: alpha(theme.palette.background.default, 0.3),
                    p: 2,
                    borderRadius: 2,
                    border: `1px solid ${alpha(theme.palette.primary.main, 0.1)}`,
                    mb: 3,
                    maxHeight: '300px',
                    overflowY: 'auto'
                  }}>
                    {selectedTask.stage_results.map((result, index) => (
                      <Box
                        key={index}
                        sx={{
                          mb: index < selectedTask.stage_results!.length - 1 ? 2 : 0,
                          pb: index < selectedTask.stage_results!.length - 1 ? 2 : 0,
                          borderBottom: index < selectedTask.stage_results!.length - 1 ? `1px solid ${alpha(theme.palette.divider, 0.1)}` : 'none'
                        }}
                      >
                        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 1 }}>
                          <Chip
                            label={result.status}
                            size="small"
                            sx={{
                              bgcolor: result.status === 'Done' ? theme.palette.success.main :
                                      result.status === 'In Progress' ? theme.palette.warning.main :
                                      result.status === 'Testing' ? theme.palette.secondary.main :
                                      result.status === 'Analysis' ? theme.palette.info.main : theme.palette.grey[600],
                              color: 'white',
                              fontWeight: 'bold'
                            }}
                          />
                          <Typography variant="caption" color="text.secondary">
                            {new Date(result.timestamp).toLocaleString()}
                          </Typography>
                        </Box>
                        <Typography variant="body2" sx={{ fontWeight: 'bold', mb: 0.5 }}>
                          {result.summary}
                        </Typography>
                        {result.details && (
                          <Typography variant="body2" color="text.secondary" sx={{ fontStyle: 'italic' }}>
                            {result.details}
                          </Typography>
                        )}
                      </Box>
                    ))}
                  </Box>
                </>
              )}

              {!isEditMode && selectedTask.status === 'Testing' && selectedTask.testing_urls && Object.keys(selectedTask.testing_urls).length > 0 && (
                <>
                  <Typography variant="subtitle1" gutterBottom sx={{ fontWeight: 'bold', mt: 3 }}>
                    Testing Environment URLs
                  </Typography>
                  <Box sx={{
                    bgcolor: alpha(theme.palette.secondary.main, 0.1),
                    p: 2,
                    borderRadius: 2,
                    border: `1px solid ${alpha(theme.palette.secondary.main, 0.3)}`,
                    mb: 3
                  }}>
                    {Object.entries(selectedTask.testing_urls).map(([env, url]) => (
                      <Box key={env} sx={{ mb: 1, '&:last-child': { mb: 0 } }}>
                        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                          <Typography variant="body2" sx={{ fontWeight: 'bold', textTransform: 'capitalize' }}>
                            {env}:
                          </Typography>
                          <Button
                            size="small"
                            variant="outlined"
                            href={url}
                            target="_blank"
                            rel="noopener noreferrer"
                            sx={{ ml: 1, borderRadius: 2 }}
                          >
                            Open
                          </Button>
                        </Box>
                        <Typography
                          variant="body2"
                          color="text.secondary"
                          sx={{
                            fontFamily: 'monospace',
                            fontSize: '0.75rem',
                            wordBreak: 'break-all'
                          }}
                        >
                          {url}
                        </Typography>
                      </Box>
                    ))}
                  </Box>
                </>
              )}

              {!isEditMode && (
                <>
                  <Typography variant="subtitle1" gutterBottom sx={{ fontWeight: 'bold', mt: 3 }}>
                    Details
                  </Typography>
                  <Box sx={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 2, mt: 1 }}>
                <Box>
                  <Typography variant="body2" color="text.secondary">Created</Typography>
                  <Typography variant="body1">{new Date(selectedTask.created_at).toLocaleString()}</Typography>
                </Box>
                <Box>
                  <Typography variant="body2" color="text.secondary">Updated</Typography>
                  <Typography variant="body1">{new Date(selectedTask.updated_at).toLocaleString()}</Typography>
                </Box>
                {selectedTask.git_branch && (
                  <Box>
                    <Typography variant="body2" color="text.secondary">Git Branch</Typography>
                    <Typography variant="body1">{selectedTask.git_branch}</Typography>
                  </Box>
                )}
                {selectedTask.assigned_agent && (
                  <Box>
                    <Typography variant="body2" color="text.secondary">Assigned Agent</Typography>
                    <Typography variant="body1">{selectedTask.assigned_agent}</Typography>
                  </Box>
                )}
                {selectedTask.estimated_hours && (
                  <Box>
                    <Typography variant="body2" color="text.secondary">Estimated Hours</Typography>
                    <Typography variant="body1">{selectedTask.estimated_hours}h</Typography>
                  </Box>
                )}
                {selectedTask.completed_at && (
                  <Box>
                    <Typography variant="body2" color="text.secondary">Completed</Typography>
                    <Typography variant="body1">{new Date(selectedTask.completed_at).toLocaleString()}</Typography>
                  </Box>
                )}
                  </Box>

                  {/* Status Transitions Section */}
                  {selectedTask && getValidTransitions(selectedTask.status).length > 0 && (
                    <>
                      <Typography variant="subtitle1" gutterBottom sx={{ fontWeight: 'bold', mt: 4 }}>
                        Available Actions
                      </Typography>
                  <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap', mt: 2 }}>
                    {getValidTransitions(selectedTask.status).map((transition) => (
                      <Button
                        key={transition.status}
                        variant="outlined"
                        startIcon={transition.icon}
                        onClick={() => handleStatusTransition(
                          selectedTask,
                          transition.status,
                          transition.requiresConfirmation,
                          transition.description
                        )}
                        disabled={updateStatusMutation.isLoading}
                        sx={{
                          textTransform: 'none',
                          mb: 1,
                          borderRadius: 2,
                          '&:hover': {
                            backgroundColor: 'primary.main',
                            color: 'white',
                          },
                        }}
                      >
                        {updateStatusMutation.isLoading && updateStatusMutation.variables?.taskId === selectedTask.id ? (
                          <CircularProgress size={16} sx={{ mr: 1 }} />
                        ) : null}
                        {transition.label}
                      </Button>
                    ))}
                  </Box>
                  <Typography variant="caption" color="text.secondary" sx={{ mt: 1, display: 'block' }}>
                    Current status: <strong>{selectedTask.status}</strong>
                      </Typography>
                    </>
                  )}

                  {/* Claude Terminal Section */}
                  <Typography variant="subtitle1" gutterBottom sx={{ fontWeight: 'bold', mt: 4 }}>
                    Claude Terminal
                  </Typography>
                  <Box sx={{ mt: 2 }}>
                    <RealTerminal
                      taskId={selectedTask?.id || 0}
                    />
                  </Box>
                </>
              )}
            </Box>
          )}
        </DialogContent>
        <DialogActions sx={{ px: 3, pb: 3 }}>
          {selectedTask?.status === 'PR' && (
            <Button
              variant="contained"
              color="success"
              onClick={async () => {
                // Send /merge command to Claude session via WebSocket
                try {
                  // Get active sessions to find session for this task
                  const sessionsResponse = await fetch(`http://localhost:3333/api/sessions/embedded/active`);

                  if (!sessionsResponse.ok) {
                    throw new Error(`HTTP error! status: ${sessionsResponse.status}`);
                  }

                  const sessionsData = await sessionsResponse.json();

                  // Extract sessions array from response object
                  const sessions = sessionsData.sessions || [];

                  // Ensure sessions is an array
                  if (!Array.isArray(sessions)) {
                    throw new Error('Sessions response does not contain a valid sessions array');
                  }

                  const session = sessions.find((s: any) => s.task_id === selectedTask.id);

                  if (session) {
                    // Connect to WebSocket and send /merge command
                    const ws = new WebSocket(`ws://localhost:3333/api/sessions/embedded/${session.session_id}/ws`);

                    ws.onopen = () => {
                      // Send /merge command with task ID
                      ws.send(JSON.stringify({
                        type: 'input',
                        content: `/merge ${selectedTask.id}\r`
                      }));

                      // Close WebSocket after sending
                      setTimeout(() => {
                        ws.close();
                        // Close dialog and refresh
                        setTaskDetailsOpen(false);
                        window.location.reload();
                      }, 1000);
                    };

                    ws.onerror = (error) => {
                      console.error('WebSocket error:', error);
                      setSnackbar({
                        open: true,
                        message: 'Failed to send /merge command. Please check if Claude session is active.',
                        severity: 'error'
                      });
                    };
                  } else {
                    setSnackbar({
                      open: true,
                      message: 'No active Claude session found for this task. Please start a session first.',
                      severity: 'warning'
                    });
                  }
                } catch (error) {
                  console.error('Failed to send merge command:', error);
                  const errorMessage = error instanceof Error ? error.message : 'Unknown error';
                  setSnackbar({
                    open: true,
                    message: `Failed to send merge command: ${errorMessage}`,
                    severity: 'error'
                  });
                }
              }}
              sx={{ mr: 'auto', borderRadius: 2 }}
            >
              Complete Task (Merge PR)
            </Button>
          )}
          <Button onClick={() => setTaskDetailsOpen(false)} variant="contained" sx={{ borderRadius: 2 }}>
            Close
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default TaskBoard;
