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
} from '@mui/icons-material';
import { useQuery, useMutation, useQueryClient } from 'react-query';
import { getTasks, createTask, updateTask, updateTaskStatus, deleteTask, Task, getActiveSessions, createClaudeSession, sendCommandToSession } from '../services/api';
import RealTerminal from '../components/RealTerminal';
import ProjectSelector from '../components/ProjectSelector';
import { useProject } from '../context/ProjectContext';

const statusColumns = [
  { status: 'Backlog', title: 'Backlog', color: '#grey' },
  { status: 'Analysis', title: 'Analysis', color: '#blue' },
  { status: 'In Progress', title: 'In Progress', color: '#orange' },
  { status: 'Testing', title: 'Testing', color: '#purple' },
  { status: 'Code Review', title: 'Code Review', color: '#brown' },
  { status: 'PR', title: 'Pull Request', color: '#1976d2' },
  { status: 'Done', title: 'Done', color: '#darkgreen' },
];

const TaskBoard: React.FC = () => {
  const [createDialogOpen, setCreateDialogOpen] = useState(false);
  const [taskDetailsOpen, setTaskDetailsOpen] = useState(false);
  const [selectedTask, setSelectedTask] = useState<Task | null>(null);
  const [statusMenuAnchor, setStatusMenuAnchor] = useState<null | HTMLElement>(null);
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

  const queryClient = useQueryClient();

  // Use project context instead of direct API call
  const { 
    selectedProject: project, 
    isConnected, 
    connectionStatus,
    error: projectError 
  } = useProject();
  
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

    if (descriptionTrimmed.length > 1000) {
      setSnackbar({ open: true, message: 'Description must be 1000 characters or less', severity: 'error' });
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
        
        // Auto-send /start-feature command when task moves to "In Progress"
        if (newStatus === 'In Progress') {
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
              // Send /start-feature command to existing session
              await sendCommandToSession(targetSession.session_id, `/start-feature ${taskId}`);
              setSnackbar({ 
                open: true, 
                message: `Task moved to ${newStatus} and /start-feature command sent to Claude session`, 
                severity: 'success' 
              });
            } else {
              // Create new Claude session and send command
              try {
                const sessionResult = await createClaudeSession(taskId);
                if (sessionResult.success) {
                  // Wait a moment for session to initialize
                  setTimeout(async () => {
                    try {
                      await sendCommandToSession(sessionResult.session_id, `/start-feature ${taskId}`);
                      setSnackbar({ 
                        open: true, 
                        message: `Task moved to ${newStatus}, new Claude session created, and /start-feature command sent`, 
                        severity: 'success' 
                      });
                    } catch (error) {
                      console.error('Failed to send /start-feature command:', error);
                      setSnackbar({ 
                        open: true, 
                        message: `Task moved to ${newStatus} and Claude session created, but failed to send /start-feature command`, 
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
            console.error('Failed to handle Claude session for In Progress task:', error);
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
  };

  const handleStatusMenuOpen = (event: React.MouseEvent<HTMLElement>, task: Task) => {
    event.stopPropagation();
    setStatusMenuAnchor(event.currentTarget);
    setSelectedTaskForStatus(task);
  };

  const handleStatusMenuClose = () => {
    setStatusMenuAnchor(null);
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

    if (descriptionTrimmed.length > 1000) {
      setSnackbar({ open: true, message: 'Description must be 1000 characters or less', severity: 'error' });
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
    return tasks?.filter(task => task.status === status) || [];
  };

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'High': return 'error';
      case 'Medium': return 'warning';
      case 'Low': return 'success';
      default: return 'default';
    }
  };

  if (!project) {
    return (
      <Box>
        <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
          <Typography variant="h4">Task Board</Typography>
        </Box>
        <ProjectSelector showStatus fullWidth />
        {projectError && (
          <Alert severity="error" sx={{ mt: 2 }}>
            {projectError}
          </Alert>
        )}
        {!projectError && (
          <Alert severity="info" sx={{ mt: 2 }}>
            Please select a project to view tasks.
          </Alert>
        )}
      </Box>
    );
  }

  if (isLoading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return (
      <Alert severity="error">
        Failed to load tasks. Please try again.
      </Alert>
    );
  }

  return (
    <Box sx={{ px: 1 }}>
      <Box display="flex" justifyContent="space-between" alignItems="flex-start" mb={3} gap={2}>
        <Box sx={{ flex: 1 }}>
          <Box display="flex" alignItems="center" gap={2} mb={2}>
            <Typography variant="h4">
              Task Board
            </Typography>
            <Chip
              size="small"
              label={isConnected ? 'Real-time updates' : 'Connecting...'}
              color={isConnected ? 'success' : 'warning'}
              variant={isConnected ? 'filled' : 'outlined'}
              sx={{
                animation: !isConnected ? 'pulse 1.5s ease-in-out infinite' : 'none',
                '@keyframes pulse': {
                  '0%': { opacity: 1 },
                  '50%': { opacity: 0.5 },
                  '100%': { opacity: 1 }
                }
              }}
            />
          </Box>
          <ProjectSelector showStatus />
        </Box>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={() => setCreateDialogOpen(true)}
          sx={{ mt: 1 }}
        >
          New Task
        </Button>
      </Box>

      <Grid container spacing={1}>
        {statusColumns.map((column) => {
          const columnTasks = getTasksByStatus(column.status);
          return (
            <Grid item xs={12} sm={6} md={4} lg={3} xl={1.71} key={column.status}>
              <Card sx={{ minHeight: '500px', height: '100%' }}>
                <CardContent>
                  <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                      {getStatusIcon(column.status)}
                      <Typography variant="h6" sx={{ color: column.color }}>
                        {column.title}
                      </Typography>
                    </Box>
                    <Chip 
                      label={columnTasks.length} 
                      size="small" 
                      sx={{ 
                        bgcolor: column.color,
                        color: 'white',
                        fontWeight: 'bold'
                      }} 
                    />
                  </Box>
                  
                  <List dense>
                    {columnTasks.map((task) => (
                      <ListItem
                        key={task.id}
                        button
                        onClick={() => handleTaskClick(task)}
                        sx={{
                          mb: 1,
                          border: '1px solid #e0e0e0',
                          borderRadius: 1,
                          bgcolor: 'background.paper',
                          cursor: 'pointer',
                          '&:hover': {
                            bgcolor: 'action.hover',
                          },
                        }}
                      >
                        <ListItemText
                          primary={
                            <Box>
                              <Typography variant="subtitle2" noWrap>
                                #{task.id} - {task.title}
                              </Typography>
                              <Box sx={{ mt: 1, display: 'flex', gap: 0.5, flexWrap: 'wrap' }}>
                                <Chip
                                  label={task.priority}
                                  size="small"
                                  color={getPriorityColor(task.priority) as any}
                                />
                                <Chip
                                  label={task.type}
                                  size="small"
                                  variant="outlined"
                                />
                                {getValidTransitions(task.status).length > 0 && (
                                  <Chip
                                    label={`${getValidTransitions(task.status).length} action${getValidTransitions(task.status).length > 1 ? 's' : ''}`}
                                    size="small"
                                    sx={{ 
                                      bgcolor: 'action.hover',
                                      fontSize: '0.7rem'
                                    }}
                                  />
                                )}
                              </Box>
                              {task.assigned_agent && (
                                <Chip
                                  label={`Agent: ${task.assigned_agent}`}
                                  size="small"
                                  sx={{ mt: 0.5 }}
                                />
                              )}
                            </Box>
                          }
                          secondary={
                            task.description ? (
                              <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                                {task.description.length > 50 
                                  ? `${task.description.substring(0, 50)}...`
                                  : task.description
                                }
                              </Typography>
                            ) : null
                          }
                        />
                        <ListItemSecondaryAction>
                          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 0.5 }}>
                            {getValidTransitions(task.status).length > 0 && (
                              <Tooltip title="Change Status">
                                <IconButton
                                  size="small"
                                  onClick={(e) => handleStatusMenuOpen(e, task)}
                                  disabled={updateStatusMutation.isLoading}
                                >
                                  {updateStatusMutation.isLoading && updateStatusMutation.variables?.taskId === task.id ? (
                                    <CircularProgress size={16} />
                                  ) : (
                                    <MoreIcon />
                                  )}
                                </IconButton>
                              </Tooltip>
                            )}
                            <Tooltip title="Delete Task">
                              <IconButton
                                size="small"
                                onClick={(e) => {
                                  e.stopPropagation();
                                  deleteTaskMutation.mutate(task.id);
                                }}
                                disabled={deleteTaskMutation.isLoading}
                              >
                                <DeleteIcon />
                              </IconButton>
                            </Tooltip>
                          </Box>
                        </ListItemSecondaryAction>
                      </ListItem>
                    ))}
                  </List>
                </CardContent>
              </Card>
            </Grid>
          );
        })}
      </Grid>

      {/* Create Task Dialog */}
      <Dialog open={createDialogOpen} onClose={() => setCreateDialogOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Create New Task</DialogTitle>
        <DialogContent>
          <TextField
            autoFocus
            margin="dense"
            label="Title"
            fullWidth
            variant="outlined"
            value={newTask.title}
            onChange={(e) => setNewTask({ ...newTask, title: e.target.value })}
            sx={{ mb: 2 }}
          />
          <TextField
            margin="dense"
            label="Description"
            fullWidth
            multiline
            rows={3}
            variant="outlined"
            value={newTask.description}
            onChange={(e) => setNewTask({ ...newTask, description: e.target.value })}
            sx={{ mb: 2 }}
          />
          <FormControl fullWidth sx={{ mb: 2 }}>
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
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setCreateDialogOpen(false)}>Cancel</Button>
          <Button
            onClick={handleCreateTask}
            variant="contained"
            disabled={!newTask.title.trim() || createTaskMutation.isLoading}
          >
            {createTaskMutation.isLoading ? <CircularProgress size={20} /> : 'Create'}
          </Button>
        </DialogActions>
      </Dialog>

      {/* Status Transition Menu */}
      <Menu
        anchorEl={statusMenuAnchor}
        open={Boolean(statusMenuAnchor)}
        onClose={handleStatusMenuClose}
        PaperProps={{
          sx: {
            maxHeight: 300,
            width: '280px',
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
      >
        <DialogTitle>
          Confirm Status Change
        </DialogTitle>
        <DialogContent>
          <Typography>
            {confirmAction?.message}
          </Typography>
          {confirmAction?.newStatus === 'Done' && (
            <Alert severity="info" sx={{ mt: 2 }}>
              This will mark the task as complete. Make sure the PR has been merged and all work is finished.
            </Alert>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setConfirmDialogOpen(false)}>Cancel</Button>
          <Button 
            onClick={handleConfirmStatusChange} 
            variant="contained"
            disabled={updateStatusMutation.isLoading}
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
          sx={{ width: '100%' }}
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
        sx={{ '& .MuiDialog-paper': { height: '90vh' } }}
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
                    sx={{ mr: 1 }}
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
                    sx={{ bgcolor: '#e3f2fd' }}
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
                    sx={{ mr: 1 }}
                  >
                    {saveLoading ? 'Saving...' : 'Save'}
                  </Button>
                  <Button
                    variant="outlined"
                    size="small"
                    startIcon={<CancelIcon />}
                    onClick={handleCancelEdit}
                    disabled={saveLoading}
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
                  rows={4}
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
                      bgcolor: '#f5f5f5',
                      color: '#1a1a1a',
                      p: 2,
                      borderRadius: 1,
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
                    bgcolor: '#f9fafb', 
                    p: 2, 
                    borderRadius: 1, 
                    border: '1px solid #e0e0e0',
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
                          borderBottom: index < selectedTask.stage_results!.length - 1 ? '1px solid #e0e0e0' : 'none'
                        }}
                      >
                        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 1 }}>
                          <Chip 
                            label={result.status} 
                            size="small" 
                            sx={{ 
                              bgcolor: result.status === 'Done' ? '#4caf50' : 
                                      result.status === 'In Progress' ? '#ff9800' : 
                                      result.status === 'Testing' ? '#9c27b0' : 
                                      result.status === 'Analysis' ? '#2196f3' : '#757575',
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
                    bgcolor: '#f3e5f5', 
                    p: 2, 
                    borderRadius: 1, 
                    border: '1px solid #e1bee7',
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
                            sx={{ ml: 1 }}
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
        <DialogActions>
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
              sx={{ mr: 'auto' }}
            >
              Complete Task (Merge PR)
            </Button>
          )}
          <Button onClick={() => setTaskDetailsOpen(false)}>Close</Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default TaskBoard;