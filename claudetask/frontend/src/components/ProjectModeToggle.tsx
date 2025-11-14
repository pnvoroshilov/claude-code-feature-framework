import React from 'react';
import {
  Box,
  ToggleButtonGroup,
  ToggleButton,
  Typography,
  alpha,
} from '@mui/material';
import {
  Lightbulb as SimpleIcon,
  Code as DevelopmentIcon,
} from '@mui/icons-material';
import { useProject } from '../context/ProjectContext';
import { useThemeMode } from '../context/ThemeContext';
import { updateProject } from '../services/api';

const ProjectModeToggle: React.FC = () => {
  const { selectedProject, refreshProjects } = useProject();
  const { mode: themeMode } = useThemeMode();

  const projectMode = selectedProject?.project_mode || 'simple';

  const handleModeChange = async (
    event: React.MouseEvent<HTMLElement>,
    newMode: string | null,
  ) => {
    if (!newMode || !selectedProject) return;

    try {
      await updateProject(selectedProject.id, {
        project_mode: newMode as 'simple' | 'development'
      });

      // Refresh projects to get updated data
      await refreshProjects();
    } catch (error) {
      console.error('Failed to update project mode:', error);
    }
  };

  if (!selectedProject) {
    return null;
  }

  return (
    <Box
      sx={{
        position: 'relative',
        zIndex: 1000,
        display: 'flex',
        alignItems: 'center',
        gap: 2,
        px: 3,
        py: 1.5,
        borderBottom: themeMode === 'dark' ? '1px solid #334155' : '1px solid #e2e8f0',
        bgcolor: themeMode === 'dark'
          ? alpha('#1e293b', 0.5)
          : alpha('#f8fafc', 0.8),
      }}
    >
      <Typography
        variant="body2"
        sx={{
          color: '#94a3b8',
          fontWeight: 500,
          display: { xs: 'none', sm: 'block' },
        }}
      >
        Project Mode:
      </Typography>

      <ToggleButtonGroup
        value={projectMode}
        exclusive
        onChange={handleModeChange}
        size="small"
        sx={{
          '& .MuiToggleButton-root': {
            px: 2,
            py: 0.5,
            textTransform: 'none',
            fontWeight: 500,
            border: themeMode === 'dark' ? '1px solid #334155' : '1px solid #e2e8f0',
            '&.Mui-selected': {
              bgcolor: themeMode === 'dark'
                ? alpha('#6366f1', 0.2)
                : alpha('#6366f1', 0.1),
              color: '#6366f1',
              '&:hover': {
                bgcolor: themeMode === 'dark'
                  ? alpha('#6366f1', 0.3)
                  : alpha('#6366f1', 0.2),
              },
            },
          },
        }}
      >
        <ToggleButton value="simple">
          <SimpleIcon sx={{ mr: 1, fontSize: 18 }} />
          Simple
        </ToggleButton>
        <ToggleButton value="development">
          <DevelopmentIcon sx={{ mr: 1, fontSize: 18 }} />
          Development
        </ToggleButton>
      </ToggleButtonGroup>

      <Typography
        variant="caption"
        sx={{
          color: '#94a3b8',
          display: { xs: 'none', md: 'block' },
        }}
      >
        {projectMode === 'simple'
          ? '3 columns: Backlog, In Progress, Done'
          : 'Full workflow with Git integration'}
      </Typography>
    </Box>
  );
};

export default ProjectModeToggle;
