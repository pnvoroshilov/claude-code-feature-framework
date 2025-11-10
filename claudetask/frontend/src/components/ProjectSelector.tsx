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
      <Alert severity="info" sx={{ my: 1 }}>
        No projects found. Please initialize a project first.
      </Alert>
    );
  }

  if (error && !selectedProject) {
    return (
      <Alert 
        severity="error" 
        sx={{ my: 1 }}
        action={
          <IconButton size="small" onClick={handleRefresh} disabled={isRefreshing}>
            {isRefreshing ? <CircularProgress size={16} /> : <RefreshIcon />}
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
            <InputLabel id="project-selector-label">
              {isLoading ? 'Loading...' : 'Project'}
            </InputLabel>
          )}
          <Select
            labelId="project-selector-label"
            value={selectedProject?.id || ''}
            label={!minimal && (isLoading ? 'Loading...' : 'Project')}
            onChange={(e) => handleProjectChange(e.target.value)}
            disabled={isLoading || availableProjects.length === 0}
            startAdornment={isLoading ? <CircularProgress size={16} sx={{ mr: 1 }} /> : null}
          >
            {availableProjects.map((project) => (
              <MenuItem key={project.id} value={project.id}>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, width: '100%' }}>
                  {!minimal && <FolderIcon fontSize="small" color="primary" />}
                  <Box sx={{ flex: 1 }}>
                    <Typography variant="body2" noWrap>
                      {project.name}
                    </Typography>
                    {!minimal && project.path && (
                      <Typography
                        variant="caption"
                        color="text.secondary"
                        sx={{ display: 'block' }}
                        noWrap
                      >
                        {project.path}
                      </Typography>
                    )}
                  </Box>
                  {!minimal && project.is_active && (
                    <Tooltip title="Active Project">
                      <ActiveIcon fontSize="small" color="success" />
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
            >
              {isRefreshing ? <CircularProgress size={16} /> : <RefreshIcon />}
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
            color="primary"
          />
          
          {selectedProject.tech_stack && selectedProject.tech_stack.length > 0 && (
            <Box sx={{ display: 'flex', gap: 0.5 }}>
              {selectedProject.tech_stack.slice(0, 3).map((tech, index) => (
                <Chip
                  key={index}
                  label={tech}
                  size="small"
                  variant="outlined"
                  sx={{ fontSize: '0.7rem' }}
                />
              ))}
              {selectedProject.tech_stack.length > 3 && (
                <Chip
                  label={`+${selectedProject.tech_stack.length - 3}`}
                  size="small"
                  variant="outlined"
                  sx={{ fontSize: '0.7rem' }}
                />
              )}
            </Box>
          )}

          <Chip
            label={getConnectionStatusLabel()}
            size="small"
            color={getConnectionStatusColor() as any}
            variant={isConnected ? 'filled' : 'outlined'}
            sx={{ 
              fontSize: '0.7rem',
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
              <WarningIcon fontSize="small" color="warning" />
            </Tooltip>
          )}
        </Box>
      )}
    </Box>
  );
};

export default ProjectSelector;