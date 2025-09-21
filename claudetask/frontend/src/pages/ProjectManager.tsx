import React, { useState } from 'react';
import {
  Box,
  Typography,
  Paper,
  Button,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  IconButton,
  Chip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Alert,
  Stack,
  Tooltip,
  Menu,
  MenuItem,
  ListItemIcon,
  ListItemText,
} from '@mui/material';
import {
  Add as AddIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  MoreVert as MoreVertIcon,
  Folder as FolderIcon,
  PlayArrow as PlayArrowIcon,
  Refresh as RefreshIcon,
} from '@mui/icons-material';
import { useQuery, useMutation, useQueryClient } from 'react-query';
import { format } from 'date-fns';
import { getProjects, getActiveProject, updateProject, deleteProject, activateProject, Project } from '../services/api';

interface EditProjectDialogProps {
  open: boolean;
  onClose: () => void;
  project: Project | null;
}

const EditProjectDialog: React.FC<EditProjectDialogProps> = ({ open, onClose, project }) => {
  const [name, setName] = useState('');
  const [githubRepo, setGithubRepo] = useState('');
  const queryClient = useQueryClient();

  React.useEffect(() => {
    if (project) {
      setName(project.name);
      setGithubRepo(project.github_repo || '');
    }
  }, [project]);

  const updateMutation = useMutation(
    ({ id, data }: { id: string; data: Partial<Project> }) => updateProject(id, data),
    {
      onSuccess: () => {
        queryClient.invalidateQueries('projects');
        onClose();
      },
    }
  );

  const handleSave = () => {
    if (!project) return;
    updateMutation.mutate({
      id: project.id,
      data: {
        name,
        github_repo: githubRepo || undefined,
      },
    });
  };

  return (
    <Dialog open={open} onClose={onClose} maxWidth="sm" fullWidth>
      <DialogTitle>Edit Project</DialogTitle>
      <DialogContent>
        <Stack spacing={2} sx={{ mt: 1 }}>
          <TextField
            label="Project Name"
            fullWidth
            value={name}
            onChange={(e) => setName(e.target.value)}
          />
          <TextField
            label="GitHub Repository (optional)"
            fullWidth
            value={githubRepo}
            onChange={(e) => setGithubRepo(e.target.value)}
            placeholder="https://github.com/username/repo"
          />
          {project && (
            <Box>
              <Typography variant="body2" color="text.secondary">
                Project Path: {project.path}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Tech Stack: {project.tech_stack.join(', ') || 'Not detected'}
              </Typography>
            </Box>
          )}
        </Stack>
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose}>Cancel</Button>
        <Button 
          onClick={handleSave} 
          variant="contained"
          disabled={updateMutation.isLoading || !name.trim()}
        >
          Save
        </Button>
      </DialogActions>
    </Dialog>
  );
};

const ProjectManager: React.FC = () => {
  const [editDialog, setEditDialog] = useState<{ open: boolean; project: Project | null }>({
    open: false,
    project: null,
  });
  const [menuAnchor, setMenuAnchor] = useState<{ element: HTMLElement | null; project: Project | null }>({
    element: null,
    project: null,
  });

  const queryClient = useQueryClient();

  // Queries
  const { data: projects = [], isLoading, error, refetch } = useQuery<Project[]>(
    'projects',
    getProjects
  );

  const { data: activeProject } = useQuery('activeProject', getActiveProject);

  // Mutations
  const activateMutation = useMutation(activateProject, {
    onSuccess: () => {
      queryClient.invalidateQueries('projects');
      queryClient.invalidateQueries('activeProject');
    },
  });

  const deleteMutation = useMutation(deleteProject, {
    onSuccess: () => {
      queryClient.invalidateQueries('projects');
      queryClient.invalidateQueries('activeProject');
    },
  });

  const handleMenuClick = (event: React.MouseEvent<HTMLElement>, project: Project) => {
    setMenuAnchor({ element: event.currentTarget, project });
  };

  const handleMenuClose = () => {
    setMenuAnchor({ element: null, project: null });
  };

  const handleEdit = (project: Project) => {
    setEditDialog({ open: true, project });
    handleMenuClose();
  };

  const handleDelete = (project: Project) => {
    if (window.confirm(`Are you sure you want to delete "${project.name}"?`)) {
      deleteMutation.mutate(project.id);
    }
    handleMenuClose();
  };

  const handleActivate = (project: Project) => {
    activateMutation.mutate(project.id);
    handleMenuClose();
  };

  if (isLoading) {
    return (
      <Box sx={{ p: 3 }}>
        <Typography>Loading projects...</Typography>
      </Box>
    );
  }

  if (error) {
    return (
      <Box sx={{ p: 3 }}>
        <Alert severity="error">
          Failed to load projects. Please try again.
        </Alert>
      </Box>
    );
  }

  return (
    <Box sx={{ p: 3 }}>
      <Stack direction="row" justifyContent="space-between" alignItems="center" sx={{ mb: 3 }}>
        <Typography variant="h4" component="h1">
          Project Manager
        </Typography>
        <Stack direction="row" spacing={2}>
          <Button
            startIcon={<RefreshIcon />}
            onClick={() => refetch()}
            variant="outlined"
          >
            Refresh
          </Button>
          <Button
            startIcon={<AddIcon />}
            variant="contained"
            onClick={() => window.location.href = '/setup'}
          >
            New Project
          </Button>
        </Stack>
      </Stack>

      {activeProject && (
        <Alert severity="info" sx={{ mb: 3 }}>
          Active Project: <strong>{activeProject.name}</strong> ({activeProject.path})
        </Alert>
      )}

      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Name</TableCell>
              <TableCell>Path</TableCell>
              <TableCell>Tech Stack</TableCell>
              <TableCell>GitHub</TableCell>
              <TableCell>Status</TableCell>
              <TableCell>Created</TableCell>
              <TableCell align="right">Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {projects.length === 0 ? (
              <TableRow>
                <TableCell colSpan={7} align="center">
                  <Box sx={{ py: 4 }}>
                    <FolderIcon sx={{ fontSize: 48, color: 'text.secondary', mb: 2 }} />
                    <Typography variant="h6" color="text.secondary">
                      No projects found
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Create your first project to get started
                    </Typography>
                  </Box>
                </TableCell>
              </TableRow>
            ) : (
              projects.map((project) => (
                <TableRow key={project.id}>
                  <TableCell>
                    <Typography variant="subtitle2">{project.name}</Typography>
                  </TableCell>
                  <TableCell>
                    <Tooltip title={project.path}>
                      <Typography 
                        variant="body2" 
                        sx={{ 
                          maxWidth: 200, 
                          overflow: 'hidden', 
                          textOverflow: 'ellipsis',
                          whiteSpace: 'nowrap' 
                        }}
                      >
                        {project.path}
                      </Typography>
                    </Tooltip>
                  </TableCell>
                  <TableCell>
                    <Stack direction="row" spacing={0.5} flexWrap="wrap">
                      {project.tech_stack.slice(0, 2).map((tech) => (
                        <Chip key={tech} label={tech} size="small" variant="outlined" />
                      ))}
                      {project.tech_stack.length > 2 && (
                        <Chip label={`+${project.tech_stack.length - 2}`} size="small" />
                      )}
                    </Stack>
                  </TableCell>
                  <TableCell>
                    {project.github_repo ? (
                      <Button
                        size="small"
                        href={project.github_repo}
                        target="_blank"
                        rel="noopener noreferrer"
                      >
                        View Repo
                      </Button>
                    ) : (
                      <Typography variant="body2" color="text.secondary">
                        Not set
                      </Typography>
                    )}
                  </TableCell>
                  <TableCell>
                    <Chip
                      label={project.is_active ? 'Active' : 'Inactive'}
                      color={project.is_active ? 'success' : 'default'}
                      size="small"
                    />
                  </TableCell>
                  <TableCell>
                    <Typography variant="body2">
                      {format(new Date(project.created_at), 'MMM dd, yyyy')}
                    </Typography>
                  </TableCell>
                  <TableCell align="right">
                    <IconButton
                      onClick={(e) => handleMenuClick(e, project)}
                      size="small"
                    >
                      <MoreVertIcon />
                    </IconButton>
                  </TableCell>
                </TableRow>
              ))
            )}
          </TableBody>
        </Table>
      </TableContainer>

      {/* Context Menu */}
      <Menu
        anchorEl={menuAnchor.element}
        open={Boolean(menuAnchor.element)}
        onClose={handleMenuClose}
      >
        {menuAnchor.project && !menuAnchor.project.is_active && (
          <MenuItem onClick={() => handleActivate(menuAnchor.project!)}>
            <ListItemIcon>
              <PlayArrowIcon fontSize="small" />
            </ListItemIcon>
            <ListItemText>Activate</ListItemText>
          </MenuItem>
        )}
        <MenuItem onClick={() => handleEdit(menuAnchor.project!)}>
          <ListItemIcon>
            <EditIcon fontSize="small" />
          </ListItemIcon>
          <ListItemText>Edit</ListItemText>
        </MenuItem>
        <MenuItem onClick={() => handleDelete(menuAnchor.project!)}>
          <ListItemIcon>
            <DeleteIcon fontSize="small" />
          </ListItemIcon>
          <ListItemText>Delete</ListItemText>
        </MenuItem>
      </Menu>

      {/* Edit Dialog */}
      <EditProjectDialog
        open={editDialog.open}
        onClose={() => setEditDialog({ open: false, project: null })}
        project={editDialog.project}
      />
    </Box>
  );
};

export default ProjectManager;