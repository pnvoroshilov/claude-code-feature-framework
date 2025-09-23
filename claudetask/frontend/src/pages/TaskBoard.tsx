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
} from '@mui/material';
import {
  Add as AddIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  PlayArrow as StartIcon,
  Terminal as TerminalIcon,
} from '@mui/icons-material';
import { useQuery, useMutation, useQueryClient } from 'react-query';
import { getActiveProject, getTasks, createTask, updateTaskStatus, deleteTask, Task } from '../services/api';
import RealTerminal from '../components/RealTerminal';

const statusColumns = [
  { status: 'Backlog', title: 'Backlog', color: '#grey' },
  { status: 'Analysis', title: 'Analysis', color: '#blue' },
  { status: 'Ready', title: 'Ready', color: '#green' },
  { status: 'In Progress', title: 'In Progress', color: '#orange' },
  { status: 'Testing', title: 'Testing', color: '#purple' },
  { status: 'Code Review', title: 'Code Review', color: '#brown' },
  { status: 'Done', title: 'Done', color: '#darkgreen' },
];

const TaskBoard: React.FC = () => {
  const [createDialogOpen, setCreateDialogOpen] = useState(false);
  const [taskDetailsOpen, setTaskDetailsOpen] = useState(false);
  const [selectedTask, setSelectedTask] = useState<Task | null>(null);
  const [sessionActive, setSessionActive] = useState(false);
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
    updateStatusMutation.mutate({ taskId, status: newStatus });
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
                    <Typography variant="h6" sx={{ color: column.color }}>
                      {column.title}
                    </Typography>
                    <Chip label={columnTasks.length} size="small" />
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
                              <Box sx={{ mt: 1, display: 'flex', gap: 0.5 }}>
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
                            {column.status === 'Backlog' && (
                              <IconButton
                                size="small"
                                onClick={(e) => {
                                  e.stopPropagation();
                                  handleStatusChange(task.id, 'Analysis');
                                }}
                                title="Start Analysis"
                              >
                                <StartIcon />
                              </IconButton>
                            )}
                            <IconButton
                              size="small"
                              onClick={(e) => {
                                e.stopPropagation();
                                deleteTaskMutation.mutate(task.id);
                              }}
                              title="Delete Task"
                            >
                              <DeleteIcon />
                            </IconButton>
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
                <ClaudeTerminal
                  taskId={selectedTask?.id || 0}
                />
              </Box>
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setTaskDetailsOpen(false)}>Close</Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default TaskBoard;