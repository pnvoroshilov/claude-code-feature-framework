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
  Fab,
  Menu,
  Tooltip,
  Snackbar,
} from '@mui/material';
import {
  Add as AddIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  PlayArrow as StartIcon,
  Terminal as TerminalIcon,
  MoreVert as MoreIcon,
  ArrowForward as NextIcon,
  ArrowBack as BackIcon,
  CheckCircle as CompleteIcon,
  BugReport as BugIcon,
  Block as BlockIcon,
  Code as CodeIcon,
  Assignment as AssignmentIcon,
  Send as PRIcon,
} from '@mui/icons-material';
import { useQuery, useMutation, useQueryClient } from 'react-query';
import { getActiveProject, getTasks, createTask, updateTaskStatus, deleteTask, Task } from '../services/api';
import RealTerminal from '../components/RealTerminal';

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
  const [sessionActive, setSessionActive] = useState(false);
  const [statusMenuAnchor, setStatusMenuAnchor] = useState<null | HTMLElement>(null);
  const [selectedTaskForStatus, setSelectedTaskForStatus] = useState<Task | null>(null);
  const [confirmDialogOpen, setConfirmDialogOpen] = useState(false);
  const [confirmAction, setConfirmAction] = useState<{ task: Task; newStatus: string; message: string } | null>(null);
  const [snackbar, setSnackbar] = useState<{ open: boolean; message: string; severity: 'success' | 'error' | 'info' }>({ open: false, message: '', severity: 'info' });
  const [newTask, setNewTask] = useState({
    title: '',
    description: '',
    type: 'Feature' as 'Feature' | 'Bug',
    priority: 'Medium' as 'High' | 'Medium' | 'Low',
  });

  const queryClient = useQueryClient();

  const { data: project } = useQuery('activeProject', getActiveProject);
  
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

  const handleCreateTask = () => {
    if (newTask.title.trim()) {
      createTaskMutation.mutate(newTask);
    }
  };

  const handleStatusChange = (taskId: number, newStatus: string) => {
    updateStatusMutation.mutate({ taskId, status: newStatus }, {
      onSuccess: () => {
        setSnackbar({ open: true, message: `Task moved to ${newStatus}`, severity: 'success' });
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
  };

  const handleConfirmStatusChange = () => {
    if (confirmAction) {
      handleStatusChange(confirmAction.task.id, confirmAction.newStatus);
    }
    setConfirmDialogOpen(false);
    setConfirmAction(null);
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
      <Alert severity="info">
        No active project found. Please initialize a project first.
      </Alert>
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
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4">
          Task Board
        </Typography>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={() => setCreateDialogOpen(true)}
        >
          New Task
        </Button>
      </Box>

      <Grid container spacing={2}>
        {statusColumns.map((column) => {
          const columnTasks = getTasksByStatus(column.status);
          return (
            <Grid item xs={12} md={6} lg={3} xl={12/7} key={column.status}>
              <Card sx={{ minHeight: '500px' }}>
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
              #{selectedTask?.id} - {selectedTask?.title}
            </Typography>
            <Box display="flex" gap={1}>
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
            </Box>
          </Box>
        </DialogTitle>
        <DialogContent>
          {selectedTask && (
            <Box>
              <Typography variant="subtitle1" gutterBottom sx={{ fontWeight: 'bold' }}>
                Description
              </Typography>
              <Typography variant="body1" paragraph sx={{ whiteSpace: 'pre-wrap' }}>
                {selectedTask.description || 'No description provided'}
              </Typography>

              {selectedTask.analysis && (
                <>
                  <Typography variant="subtitle1" gutterBottom sx={{ fontWeight: 'bold', mt: 3 }}>
                    Analysis
                  </Typography>
                  <Typography 
                    variant="body2" 
                    paragraph 
                    sx={{ 
                      whiteSpace: 'pre-wrap',
                      bgcolor: '#f5f5f5',
                      p: 2,
                      borderRadius: 1,
                      fontFamily: 'monospace'
                    }}
                  >
                    {selectedTask.analysis}
                  </Typography>
                </>
              )}

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

              {/* Claude Terminal Section */}
              <Typography variant="subtitle1" gutterBottom sx={{ fontWeight: 'bold', mt: 4 }}>
                Claude Terminal
              </Typography>
              <Box sx={{ mt: 2 }}>
                <RealTerminal
                  taskId={selectedTask?.id || 0}
                />
              </Box>
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
                  const sessions = await sessionsResponse.json();
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
                      alert('Failed to send /merge command. Please check if Claude session is active.');
                    };
                  } else {
                    alert('No active Claude session found for this task. Please start a session first.');
                  }
                } catch (error) {
                  console.error('Failed to send merge command:', error);
                  alert('Failed to send merge command. Please try again.');
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