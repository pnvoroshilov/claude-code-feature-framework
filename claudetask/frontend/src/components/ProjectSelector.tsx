import React, { useState } from 'react';
import {
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Box,
  Typography,
  CircularProgress,
  Alert,
  Chip,
  Tooltip,
  IconButton,
} from '@mui/material';
import {
  Refresh as RefreshIcon,
  Folder as FolderIcon,
  CheckCircle as ActiveIcon,
  Warning as WarningIcon,
} from '@mui/icons-material';
import { useProject } from '../context/ProjectContext';

interface ProjectSelectorProps {
  size?: 'small' | 'medium';
  variant?: 'outlined' | 'standard' | 'filled';
  fullWidth?: boolean;
  showStatus?: boolean;
  minimal?: boolean;
  className?: string;
}

const ProjectSelector: React.FC<ProjectSelectorProps> = ({
  size = 'medium',
  variant = 'outlined',
  fullWidth = false,
  showStatus = true,
  minimal = false,
  className,
}) => {
  const {
    selectedProject,
    availableProjects,
    isLoading,
    error,
    selectProject,
    refreshProjects,
    isConnected,
    connectionStatus,
    hasProjects,
  } = useProject();

  const [isRefreshing, setIsRefreshing] = useState(false);

  const handleProjectChange = async (projectId: string) => {
    if (projectId === selectedProject?.id) {
      return;
    }
    
    try {
      await selectProject(projectId);
    } catch (error) {
      console.error('Failed to select project:', error);
    }
  };

  const handleRefresh = async () => {
    setIsRefreshing(true);
    try {
      await refreshProjects();
    } finally {
      setIsRefreshing(false);
    }
  };

  const getConnectionStatusColor = () => {
    switch (connectionStatus) {
      case 'connected':
        return 'success';
      case 'connecting':
        return 'warning';
      case 'error':
        return 'error';
      default:
        return 'default';
    }
  };

  const getConnectionStatusLabel = () => {
    switch (connectionStatus) {
      case 'connected':
        return 'Connected';
      case 'connecting':
        return 'Connecting...';
      case 'error':
        return 'Connection Error';
      default:
        return 'Disconnected';
    }
  };

  if (!hasProjects && !isLoading) {
    return (
      <Alert
        severity="info"
        sx={{
          my: 1,
          backgroundColor: 'rgba(59, 130, 246, 0.1)',
          border: '1px solid rgba(59, 130, 246, 0.3)',
          color: '#60a5fa',
          '& .MuiAlert-icon': {
            color: '#60a5fa',
          }
        }}
      >
        No projects found. Please initialize a project first.
      </Alert>
    );
  }

  if (error && !selectedProject) {
    return (
      <Alert
        severity="error"
        sx={{
          my: 1,
          backgroundColor: 'rgba(239, 68, 68, 0.1)',
          border: '1px solid rgba(239, 68, 68, 0.3)',
          color: '#f87171',
          '& .MuiAlert-icon': {
            color: '#f87171',
          }
        }}
        action={
          <IconButton
            size="small"
            onClick={handleRefresh}
            disabled={isRefreshing}
            sx={{
              color: '#f87171',
              '&:hover': {
                backgroundColor: 'rgba(239, 68, 68, 0.1)',
              }
            }}
          >
            {isRefreshing ? <CircularProgress size={16} sx={{ color: '#f87171' }} /> : <RefreshIcon />}
          </IconButton>
        }
      >
        {error}
      </Alert>
    );
  }

  return (
    <Box className={className}>
      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: showStatus ? 1 : 0 }}>
        <FormControl
          size={size}
          variant={variant}
          fullWidth={fullWidth}
          sx={{ minWidth: minimal ? 150 : 200 }}
          disabled={isLoading}
        >
          {!minimal && (
            <InputLabel
              id="project-selector-label"
              sx={{
                color: '#94a3b8',
                '&.Mui-focused': {
                  color: '#6366f1',
                }
              }}
            >
              {isLoading ? 'Loading...' : 'Project'}
            </InputLabel>
          )}
          <Select
            labelId="project-selector-label"
            value={selectedProject?.id || ''}
            label={!minimal && (isLoading ? 'Loading...' : 'Project')}
            onChange={(e) => handleProjectChange(e.target.value)}
            disabled={isLoading || availableProjects.length === 0}
            startAdornment={isLoading ? <CircularProgress size={16} sx={{ mr: 1, color: '#6366f1' }} /> : null}
            sx={minimal ? {
              backgroundColor: 'rgba(99, 102, 241, 0.1)',
              borderRadius: 2,
              px: 2,
              py: 0.5,
              fontWeight: 500,
              color: '#6366f1',
              border: '1px solid rgba(99, 102, 241, 0.3)',
              transition: 'all 0.2s',
              '&:hover': {
                backgroundColor: 'rgba(99, 102, 241, 0.15)',
                borderColor: 'rgba(99, 102, 241, 0.5)',
              },
              '&.Mui-focused': {
                backgroundColor: 'rgba(99, 102, 241, 0.15)',
              },
              '& .MuiSelect-select': {
                py: 0.75,
              },
              '&:before, &:after': {
                display: 'none',
              },
            } : {
              '& .MuiOutlinedInput-notchedOutline': {
                borderColor: '#334155',
              },
              '&:hover .MuiOutlinedInput-notchedOutline': {
                borderColor: '#475569',
              },
              '&.Mui-focused .MuiOutlinedInput-notchedOutline': {
                borderColor: '#6366f1',
              },
              '& .MuiSelect-icon': {
                color: '#94a3b8',
              }
            }}
          >
            {availableProjects.map((project) => (
              <MenuItem
                key={project.id}
                value={project.id}
                sx={{
                  backgroundColor: 'transparent',
                  '&:hover': {
                    backgroundColor: 'rgba(99, 102, 241, 0.1)',
                  },
                  '&.Mui-selected': {
                    backgroundColor: 'rgba(99, 102, 241, 0.15)',
                    '&:hover': {
                      backgroundColor: 'rgba(99, 102, 241, 0.2)',
                    }
                  }
                }}
              >
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, width: '100%' }}>
                  {!minimal && <FolderIcon fontSize="small" sx={{ color: '#6366f1' }} />}
                  <Box sx={{ flex: 1 }}>
                    <Typography variant="body2" noWrap sx={{ color: '#e2e8f0' }}>
                      {project.name}
                    </Typography>
                    {!minimal && project.path && (
                      <Typography
                        variant="caption"
                        sx={{ display: 'block', color: '#94a3b8' }}
                        noWrap
                      >
                        {project.path}
                      </Typography>
                    )}
                  </Box>
                  {!minimal && project.is_active && (
                    <Tooltip title="Active Project">
                      <ActiveIcon fontSize="small" sx={{ color: '#10b981' }} />
                    </Tooltip>
                  )}
                </Box>
              </MenuItem>
            ))}
          </Select>
        </FormControl>

        {!minimal && (
          <Tooltip title="Refresh Projects">
            <IconButton
              size="small"
              onClick={handleRefresh}
              disabled={isRefreshing || isLoading}
              sx={{
                color: '#94a3b8',
                '&:hover': {
                  backgroundColor: 'rgba(99, 102, 241, 0.1)',
                  color: '#6366f1',
                }
              }}
            >
              {isRefreshing ? <CircularProgress size={16} sx={{ color: '#6366f1' }} /> : <RefreshIcon />}
            </IconButton>
          </Tooltip>
        )}
      </Box>

      {showStatus && selectedProject && (
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, flexWrap: 'wrap' }}>
          <Chip
            icon={<FolderIcon />}
            label={selectedProject.name}
            size="small"
            variant="outlined"
            sx={{
              borderColor: '#334155',
              color: '#e2e8f0',
              backgroundColor: 'rgba(99, 102, 241, 0.1)',
              '& .MuiChip-icon': {
                color: '#6366f1',
              }
            }}
          />

          {selectedProject.tech_stack && selectedProject.tech_stack.length > 0 && (
            <Box sx={{ display: 'flex', gap: 0.5 }}>
              {selectedProject.tech_stack.slice(0, 3).map((tech, index) => (
                <Chip
                  key={index}
                  label={tech}
                  size="small"
                  variant="outlined"
                  sx={{
                    fontSize: '0.7rem',
                    borderColor: '#334155',
                    color: '#94a3b8',
                    backgroundColor: 'rgba(51, 65, 85, 0.3)',
                    '&:hover': {
                      backgroundColor: 'rgba(51, 65, 85, 0.5)',
                    }
                  }}
                />
              ))}
              {selectedProject.tech_stack.length > 3 && (
                <Chip
                  label={`+${selectedProject.tech_stack.length - 3}`}
                  size="small"
                  variant="outlined"
                  sx={{
                    fontSize: '0.7rem',
                    borderColor: '#334155',
                    color: '#94a3b8',
                    backgroundColor: 'rgba(51, 65, 85, 0.3)',
                  }}
                />
              )}
            </Box>
          )}

          <Chip
            label={getConnectionStatusLabel()}
            size="small"
            variant={isConnected ? 'filled' : 'outlined'}
            sx={{
              fontSize: '0.7rem',
              borderColor: connectionStatus === 'connected' ? '#10b981' :
                          connectionStatus === 'error' ? '#ef4444' : '#f59e0b',
              backgroundColor: connectionStatus === 'connected' ? 'rgba(16, 185, 129, 0.15)' :
                              connectionStatus === 'error' ? 'rgba(239, 68, 68, 0.15)' :
                              'rgba(245, 158, 11, 0.15)',
              color: connectionStatus === 'connected' ? '#10b981' :
                     connectionStatus === 'error' ? '#ef4444' : '#f59e0b',
              animation: connectionStatus === 'connecting' ? 'pulse 1.5s ease-in-out infinite' : 'none',
              '@keyframes pulse': {
                '0%': { opacity: 1 },
                '50%': { opacity: 0.5 },
                '100%': { opacity: 1 }
              }
            }}
          />

          {error && (
            <Tooltip title={error}>
              <WarningIcon fontSize="small" sx={{ color: '#f59e0b' }} />
            </Tooltip>
          )}
        </Box>
      )}
    </Box>
  );
};

export default ProjectSelector;