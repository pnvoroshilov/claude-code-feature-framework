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
  useTheme,
  alpha,
  Skeleton,
} from '@mui/material';
import {
  Add as AddIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  MoreVert as MoreVertIcon,
  Folder as FolderIcon,
  PlayArrow as PlayArrowIcon,
  Refresh as RefreshIcon,
  SystemUpdate as SystemUpdateIcon,
  GitHub as GitHubIcon,
  Code as CodeIcon,
} from '@mui/icons-material';
import { useQuery, useMutation, useQueryClient } from 'react-query';
import { format } from 'date-fns';
import { useNavigate } from 'react-router-dom';
import { getProjects, getActiveProject, updateProject, deleteProject, activateProject, updateFramework, Project } from '../../services/api';

interface EditProjectDialogProps {
  open: boolean;
  onClose: () => void;
  project: Project | null;
}

const EditProjectDialog: React.FC<EditProjectDialogProps> = ({ open, onClose, project }) => {
  const theme = useTheme();
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
    <Dialog
      open={open}
      onClose={onClose}
      maxWidth="sm"
      fullWidth
      PaperProps={{
        sx: {
          backgroundColor: theme.palette.background.paper,
          backgroundImage: 'none',
          border: `1px solid ${theme.palette.divider}`,
          boxShadow: `0 20px 25px -5px ${alpha(theme.palette.common.black, 0.3)}`,
        }
      }}
    >
      <DialogTitle sx={{
        color: theme.palette.text.primary,
        fontWeight: 600,
        fontSize: '1.25rem',
      }}>
        Edit Project
      </DialogTitle>
      <DialogContent>
        <Stack spacing={3} sx={{ mt: 2 }}>
          <TextField
            label="Project Name"
            fullWidth
            value={name}
            onChange={(e) => setName(e.target.value)}
            sx={{
              '& .MuiOutlinedInput-root': {
                color: theme.palette.text.primary,
                backgroundColor: alpha(theme.palette.background.default, 0.5),
                '& fieldset': { borderColor: theme.palette.divider },
                '&:hover fieldset': { borderColor: theme.palette.primary.main },
                '&.Mui-focused fieldset': { borderColor: theme.palette.primary.main }
              },
              '& .MuiInputLabel-root': {
                color: theme.palette.text.secondary,
                '&.Mui-focused': { color: theme.palette.primary.main }
              }
            }}
          />
          <TextField
            label="GitHub Repository (optional)"
            fullWidth
            value={githubRepo}
            onChange={(e) => setGithubRepo(e.target.value)}
            placeholder="https://github.com/username/repo"
            sx={{
              '& .MuiOutlinedInput-root': {
                color: theme.palette.text.primary,
                backgroundColor: alpha(theme.palette.background.default, 0.5),
                '& fieldset': { borderColor: theme.palette.divider },
                '&:hover fieldset': { borderColor: theme.palette.primary.main },
                '&.Mui-focused fieldset': { borderColor: theme.palette.primary.main }
              },
              '& .MuiInputLabel-root': {
                color: theme.palette.text.secondary,
                '&.Mui-focused': { color: theme.palette.primary.main }
              }
            }}
          />
          {project && (
            <Box sx={{
              p: 2,
              borderRadius: 1,
              backgroundColor: alpha(theme.palette.primary.main, 0.05),
              border: `1px solid ${alpha(theme.palette.primary.main, 0.1)}`,
            }}>
              <Typography variant="body2" sx={{ color: theme.palette.text.secondary, mb: 0.5 }}>
                <strong>Path:</strong> {project.path}
              </Typography>
              <Typography variant="body2" sx={{ color: theme.palette.text.secondary }}>
                <strong>Tech Stack:</strong> {project.tech_stack.join(', ') || 'Not detected'}
              </Typography>
            </Box>
          )}
        </Stack>
      </DialogContent>
      <DialogActions sx={{ px: 3, pb: 3 }}>
        <Button
          onClick={onClose}
          sx={{
            color: theme.palette.text.secondary,
            textTransform: 'none',
            fontWeight: 500,
            px: 2,
            '&:hover': { backgroundColor: alpha(theme.palette.text.secondary, 0.1) }
          }}
        >
          Cancel
        </Button>
        <Button
          onClick={handleSave}
          variant="contained"
          disabled={updateMutation.isLoading || !name.trim()}
          sx={{
            backgroundColor: theme.palette.primary.main,
            color: '#ffffff',
            fontWeight: 600,
            textTransform: 'none',
            px: 3,
            boxShadow: `0 4px 6px ${alpha(theme.palette.primary.main, 0.3)}`,
            '&:hover': {
              backgroundColor: theme.palette.primary.dark,
              boxShadow: `0 6px 8px ${alpha(theme.palette.primary.main, 0.4)}`,
            },
            '&:disabled': {
              backgroundColor: theme.palette.action.disabledBackground,
              color: theme.palette.action.disabled
            }
          }}
        >
          {updateMutation.isLoading ? 'Saving...' : 'Save Changes'}
        </Button>
      </DialogActions>
    </Dialog>
  );
};

const ProjectListView: React.FC = () => {
  const theme = useTheme();
  const navigate = useNavigate();
  const [editDialog, setEditDialog] = useState<{ open: boolean; project: Project | null }>({
    open: false,
    project: null,
  });
  const [menuAnchor, setMenuAnchor] = useState<{ element: HTMLElement | null; project: Project | null }>({
    element: null,
    project: null,
  });

  const queryClient = useQueryClient();

  const { data: projects = [], isLoading, error, refetch } = useQuery<Project[]>(
    'projects',
    getProjects
  );

  const { data: activeProject } = useQuery('activeProject', getActiveProject);

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
      setDeleteError(null);
    },
    onError: (error: any) => {
      const errorMessage = error.response?.data?.detail || error.message || 'Unknown error';
      console.error('Failed to delete project:', error);
      setDeleteError(errorMessage);
      setTimeout(() => setDeleteError(null), 5000);
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

  const [updateFrameworkLoading, setUpdateFrameworkLoading] = useState(false);
  const [updateFrameworkResult, setUpdateFrameworkResult] = useState<{
    success: boolean;
    message: string;
    updated_files?: string[];
  } | null>(null);
  const [deleteError, setDeleteError] = useState<string | null>(null);

  const handleUpdateFramework = async (project: Project) => {
    setUpdateFrameworkLoading(true);
    try {
      const result = await updateFramework(project.id);
      setUpdateFrameworkResult({
        success: result.success,
        message: result.message,
        updated_files: result.updated_files
      });
      setTimeout(() => setUpdateFrameworkResult(null), 5000);
    } catch (error) {
      setUpdateFrameworkResult({
        success: false,
        message: 'Failed to update framework files'
      });
    } finally {
      setUpdateFrameworkLoading(false);
    }
    handleMenuClose();
  };

  if (isLoading) {
    return (
      <Box>
        <Skeleton variant="text" width={200} height={40} sx={{ mb: 2 }} />
        <Skeleton variant="rectangular" height={400} sx={{ borderRadius: 2 }} />
      </Box>
    );
  }

  if (error) {
    return (
      <Alert
        severity="error"
        sx={{
          backgroundColor: alpha(theme.palette.error.main, 0.1),
          border: `1px solid ${alpha(theme.palette.error.main, 0.3)}`,
          color: theme.palette.error.light,
          '& .MuiAlert-icon': { color: theme.palette.error.light }
        }}
      >
        Failed to load projects. Please try again.
      </Alert>
    );
  }

  return (
    <Box>
      {/* Action Buttons */}
      <Stack direction="row" spacing={2} sx={{ mb: 3 }}>
        <Button
          startIcon={<RefreshIcon />}
          onClick={() => refetch()}
          variant="outlined"
          sx={{
            color: theme.palette.text.secondary,
            borderColor: theme.palette.divider,
            textTransform: 'none',
            fontWeight: 500,
            px: 2.5,
            '&:hover': {
              backgroundColor: alpha(theme.palette.primary.main, 0.1),
              borderColor: theme.palette.primary.main,
              color: theme.palette.primary.main,
            }
          }}
        >
          Refresh
        </Button>
        <Button
          startIcon={<AddIcon />}
          variant="contained"
          onClick={() => navigate('/projects/setup')}
          sx={{
            backgroundColor: theme.palette.primary.main,
            color: '#ffffff',
            fontWeight: 600,
            textTransform: 'none',
            px: 3,
            boxShadow: `0 4px 6px ${alpha(theme.palette.primary.main, 0.3)}`,
            '&:hover': {
              backgroundColor: theme.palette.primary.dark,
              boxShadow: `0 6px 8px ${alpha(theme.palette.primary.main, 0.4)}`,
            }
          }}
        >
          New Project
        </Button>
      </Stack>

      {/* Alerts */}
      {deleteError && (
        <Alert
          severity="error"
          sx={{
            mb: 3,
            backgroundColor: alpha(theme.palette.error.main, 0.1),
            border: `1px solid ${alpha(theme.palette.error.main, 0.3)}`,
            color: theme.palette.error.light,
            '& .MuiAlert-icon': { color: theme.palette.error.light }
          }}
          onClose={() => setDeleteError(null)}
        >
          {deleteError}
        </Alert>
      )}

      {updateFrameworkResult && (
        <Alert
          severity={updateFrameworkResult.success ? "success" : "error"}
          sx={{
            mb: 3,
            ...(updateFrameworkResult.success ? {
              backgroundColor: alpha(theme.palette.success.main, 0.1),
              border: `1px solid ${alpha(theme.palette.success.main, 0.3)}`,
              color: theme.palette.success.light,
              '& .MuiAlert-icon': { color: theme.palette.success.light }
            } : {
              backgroundColor: alpha(theme.palette.error.main, 0.1),
              border: `1px solid ${alpha(theme.palette.error.main, 0.3)}`,
              color: theme.palette.error.light,
              '& .MuiAlert-icon': { color: theme.palette.error.light }
            })
          }}
          onClose={() => setUpdateFrameworkResult(null)}
        >
          {updateFrameworkResult.message}
          {updateFrameworkResult.updated_files && updateFrameworkResult.updated_files.length > 0 && (
            <Box sx={{ mt: 1 }}>
              <Typography variant="body2">Updated files:</Typography>
              <ul style={{ margin: '4px 0', paddingLeft: '20px' }}>
                {updateFrameworkResult.updated_files.slice(0, 5).map((file, index) => (
                  <li key={index}><Typography variant="caption">{file}</Typography></li>
                ))}
                {updateFrameworkResult.updated_files.length > 5 && (
                  <li><Typography variant="caption">...and {updateFrameworkResult.updated_files.length - 5} more</Typography></li>
                )}
              </ul>
            </Box>
          )}
        </Alert>
      )}

      {activeProject && (
        <Alert
          icon={<FolderIcon />}
          severity="info"
          sx={{
            mb: 3,
            backgroundColor: alpha(theme.palette.primary.main, 0.1),
            border: `1px solid ${alpha(theme.palette.primary.main, 0.3)}`,
            color: theme.palette.primary.light,
            '& .MuiAlert-icon': { color: theme.palette.primary.light }
          }}
        >
          <Typography variant="body2">
            <strong>Active Project:</strong> {activeProject.name} • {activeProject.path}
          </Typography>
        </Alert>
      )}

      {/* Projects Table */}
      <TableContainer
        component={Paper}
        elevation={0}
        sx={{
          backgroundColor: theme.palette.background.paper,
          border: `1px solid ${theme.palette.divider}`,
          borderRadius: 2,
          overflow: 'hidden',
        }}
      >
        <Table
          sx={{
            '& .MuiTableHead-root': {
              backgroundColor: alpha(theme.palette.background.default, 0.5),
              '& .MuiTableCell-root': {
                color: theme.palette.text.secondary,
                fontWeight: 700,
                textTransform: 'uppercase',
                fontSize: '0.75rem',
                letterSpacing: '0.05em',
                borderBottom: `1px solid ${theme.palette.divider}`,
                py: 2,
              }
            },
            '& .MuiTableBody-root': {
              '& .MuiTableRow-root': {
                transition: 'all 0.2s ease',
                '&:hover': {
                  backgroundColor: alpha(theme.palette.primary.main, 0.05),
                  transform: 'scale(1.001)',
                }
              },
              '& .MuiTableCell-root': {
                color: theme.palette.text.primary,
                borderBottom: `1px solid ${theme.palette.divider}`,
                py: 2.5,
              }
            }
          }}
        >
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
                  <Box sx={{ py: 8 }}>
                    <FolderIcon sx={{ fontSize: 64, color: theme.palette.text.disabled, mb: 2 }} />
                    <Typography variant="h6" sx={{ color: theme.palette.text.secondary, mb: 1, fontWeight: 600 }}>
                      No projects found
                    </Typography>
                    <Typography variant="body2" sx={{ color: theme.palette.text.disabled, mb: 3 }}>
                      Create your first project to get started
                    </Typography>
                    <Button
                      variant="outlined"
                      startIcon={<AddIcon />}
                      onClick={() => navigate('/projects/setup')}
                      sx={{
                        textTransform: 'none',
                        fontWeight: 600,
                      }}
                    >
                      Create Project
                    </Button>
                  </Box>
                </TableCell>
              </TableRow>
            ) : (
              projects.map((project) => (
                <TableRow
                  key={project.id}
                  onClick={() => navigate(`/projects/${project.id}/files`)}
                  sx={{
                    cursor: 'pointer',
                    '&:hover': {
                      backgroundColor: alpha(theme.palette.primary.main, 0.08),
                    }
                  }}
                >
                  <TableCell>
                    <Stack direction="row" spacing={1.5} alignItems="center">
                      <Box sx={{
                        width: 40,
                        height: 40,
                        borderRadius: 1.5,
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        backgroundColor: alpha(theme.palette.primary.main, 0.1),
                        border: `1px solid ${alpha(theme.palette.primary.main, 0.2)}`,
                      }}>
                        <FolderIcon sx={{ color: theme.palette.primary.main, fontSize: 20 }} />
                      </Box>
                      <Typography variant="subtitle2" sx={{ fontWeight: 600, color: theme.palette.text.primary }}>
                        {project.name}
                      </Typography>
                    </Stack>
                  </TableCell>
                  <TableCell>
                    <Tooltip title={project.path} placement="top">
                      <Typography
                        variant="body2"
                        sx={{
                          maxWidth: 250,
                          overflow: 'hidden',
                          textOverflow: 'ellipsis',
                          whiteSpace: 'nowrap',
                          color: theme.palette.text.secondary,
                          fontFamily: 'monospace',
                          fontSize: '0.85rem',
                        }}
                      >
                        {project.path}
                      </Typography>
                    </Tooltip>
                  </TableCell>
                  <TableCell>
                    <Stack direction="row" spacing={0.5} flexWrap="wrap" gap={0.5}>
                      {project.tech_stack.slice(0, 2).map((tech) => (
                        <Chip
                          key={tech}
                          label={tech}
                          size="small"
                          sx={{
                            borderColor: theme.palette.divider,
                            color: theme.palette.text.secondary,
                            backgroundColor: alpha(theme.palette.primary.main, 0.08),
                            fontWeight: 500,
                            fontSize: '0.75rem',
                            '&:hover': { backgroundColor: alpha(theme.palette.primary.main, 0.15) }
                          }}
                        />
                      ))}
                      {project.tech_stack.length > 2 && (
                        <Chip
                          label={`+${project.tech_stack.length - 2}`}
                          size="small"
                          sx={{
                            borderColor: theme.palette.divider,
                            color: theme.palette.text.secondary,
                            backgroundColor: alpha(theme.palette.text.secondary, 0.1),
                            fontWeight: 600,
                            fontSize: '0.75rem',
                          }}
                        />
                      )}
                    </Stack>
                  </TableCell>
                  <TableCell>
                    {project.github_repo ? (
                      <Button
                        size="small"
                        startIcon={<GitHubIcon />}
                        href={project.github_repo}
                        target="_blank"
                        rel="noopener noreferrer"
                        sx={{
                          color: theme.palette.primary.main,
                          textTransform: 'none',
                          fontWeight: 500,
                          '&:hover': { backgroundColor: alpha(theme.palette.primary.main, 0.1) }
                        }}
                      >
                        View Repo
                      </Button>
                    ) : (
                      <Typography variant="body2" sx={{ color: theme.palette.text.disabled, fontStyle: 'italic' }}>
                        Not set
                      </Typography>
                    )}
                  </TableCell>
                  <TableCell>
                    <Chip
                      label={project.is_active ? 'Active' : 'Inactive'}
                      size="small"
                      sx={{
                        ...(project.is_active ? {
                          backgroundColor: alpha(theme.palette.success.main, 0.15),
                          color: theme.palette.success.light,
                          borderColor: alpha(theme.palette.success.main, 0.3),
                          border: '1px solid',
                          fontWeight: 600,
                        } : {
                          backgroundColor: alpha(theme.palette.text.secondary, 0.1),
                          color: theme.palette.text.secondary,
                          borderColor: alpha(theme.palette.text.secondary, 0.2),
                          border: '1px solid',
                        })
                      }}
                    />
                  </TableCell>
                  <TableCell>
                    <Typography variant="body2" sx={{ color: theme.palette.text.secondary }}>
                      {format(new Date(project.created_at), 'MMM dd, yyyy')}
                    </Typography>
                  </TableCell>
                  <TableCell align="right">
                    <IconButton
                      onClick={(e) => {
                        e.stopPropagation();
                        handleMenuClick(e, project);
                      }}
                      size="small"
                      sx={{
                        color: theme.palette.text.secondary,
                        transition: 'all 0.2s ease',
                        '&:hover': {
                          backgroundColor: alpha(theme.palette.primary.main, 0.1),
                          color: theme.palette.primary.main,
                          transform: 'scale(1.1)',
                        }
                      }}
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
        PaperProps={{
          sx: {
            backgroundColor: theme.palette.background.paper,
            border: `1px solid ${theme.palette.divider}`,
            boxShadow: `0 10px 15px -3px ${alpha(theme.palette.common.black, 0.3)}`,
            minWidth: 200,
            '& .MuiMenuItem-root': {
              color: theme.palette.text.primary,
              py: 1.5,
              px: 2,
              transition: 'all 0.2s ease',
              '&:hover': {
                backgroundColor: alpha(theme.palette.primary.main, 0.1),
                color: theme.palette.primary.main,
                '& .MuiListItemIcon-root': {
                  color: theme.palette.primary.main,
                }
              }
            }
          }
        }}
      >
        <MenuItem onClick={() => {
          navigate(`/projects/${menuAnchor.project!.id}/files`);
          handleMenuClose();
        }}>
          <ListItemIcon>
            <CodeIcon fontSize="small" sx={{ color: theme.palette.text.secondary }} />
          </ListItemIcon>
          <ListItemText primaryTypographyProps={{ fontWeight: 500 }}>Browse Files</ListItemText>
        </MenuItem>
        {menuAnchor.project && !menuAnchor.project.is_active && (
          <MenuItem onClick={() => handleActivate(menuAnchor.project!)}>
            <ListItemIcon>
              <PlayArrowIcon fontSize="small" sx={{ color: theme.palette.text.secondary }} />
            </ListItemIcon>
            <ListItemText primaryTypographyProps={{ fontWeight: 500 }}>Activate Project</ListItemText>
          </MenuItem>
        )}
        <MenuItem onClick={() => handleUpdateFramework(menuAnchor.project!)}>
          <ListItemIcon>
            <SystemUpdateIcon fontSize="small" sx={{ color: theme.palette.text.secondary }} />
          </ListItemIcon>
          <ListItemText primaryTypographyProps={{ fontWeight: 500 }}>Update Framework</ListItemText>
        </MenuItem>
        <MenuItem onClick={() => handleEdit(menuAnchor.project!)}>
          <ListItemIcon>
            <EditIcon fontSize="small" sx={{ color: theme.palette.text.secondary }} />
          </ListItemIcon>
          <ListItemText primaryTypographyProps={{ fontWeight: 500 }}>Edit Project</ListItemText>
        </MenuItem>
        <MenuItem
          onClick={() => handleDelete(menuAnchor.project!)}
          sx={{
            '&:hover': {
              backgroundColor: alpha(theme.palette.error.main, 0.1),
              color: `${theme.palette.error.main} !important`,
              '& .MuiListItemIcon-root': {
                color: `${theme.palette.error.main} !important`,
              }
            }
          }}
        >
          <ListItemIcon>
            <DeleteIcon fontSize="small" sx={{ color: theme.palette.error.main }} />
          </ListItemIcon>
          <ListItemText primaryTypographyProps={{ fontWeight: 500, color: theme.palette.error.main }}>Delete Project</ListItemText>
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

export default ProjectListView;
