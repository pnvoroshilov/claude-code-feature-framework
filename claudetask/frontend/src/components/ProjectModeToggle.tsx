import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Switch,
  FormControlLabel,
  Tooltip,
  Chip,
  alpha,
} from '@mui/material';
import {
  Lightbulb as SimpleIcon,
  Code as DevelopmentIcon,
  AccountTree as WorktreeIcon,
} from '@mui/icons-material';
import { useProject } from '../context/ProjectContext';
import { useThemeMode } from '../context/ThemeContext';
import { getProjectSettings, updateProjectSettings } from '../services/api';

const ProjectModeToggle: React.FC = () => {
  const { selectedProject, refreshProjects } = useProject();
  const { mode: themeMode } = useThemeMode();
  const [worktreeEnabled, setWorktreeEnabled] = useState<boolean>(true);
  const [loading, setLoading] = useState<boolean>(false);

  const projectMode = selectedProject?.project_mode || 'simple';

  // Load project settings to get worktree_enabled value
  useEffect(() => {
    const loadSettings = async () => {
      if (!selectedProject) return;

      try {
        const settings = await getProjectSettings(selectedProject.id);
        setWorktreeEnabled(settings.worktree_enabled);
      } catch (error) {
        console.error('Failed to load project settings:', error);
      }
    };

    loadSettings();
  }, [selectedProject]);

  const handleWorktreeToggle = async (event: React.ChangeEvent<HTMLInputElement>) => {
    if (!selectedProject) return;

    const newValue = event.target.checked;
    setLoading(true);

    try {
      await updateProjectSettings(selectedProject.id, {
        worktree_enabled: newValue
      });

      setWorktreeEnabled(newValue);

      // Refresh projects to trigger CLAUDE.md regeneration
      await refreshProjects();
    } catch (error) {
      console.error('Failed to update worktree setting:', error);
      // Revert on error
      setWorktreeEnabled(!newValue);
    } finally {
      setLoading(false);
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

      {/* Display-only mode indicator */}
      <Chip
        icon={projectMode === 'simple' ? <SimpleIcon /> : <DevelopmentIcon />}
        label={projectMode === 'simple' ? 'Simple' : 'Development'}
        size="small"
        sx={{
          fontWeight: 500,
          bgcolor: themeMode === 'dark'
            ? alpha('#6366f1', 0.2)
            : alpha('#6366f1', 0.1),
          color: '#6366f1',
          border: themeMode === 'dark' ? '1px solid #334155' : '1px solid #e2e8f0',
          '& .MuiChip-icon': {
            color: '#6366f1',
          },
        }}
      />

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

      {/* Worktree Toggle - Only show in development mode */}
      {projectMode === 'development' && (
        <Tooltip
          title={
            worktreeEnabled
              ? 'Git worktrees enabled - Each task gets isolated workspace'
              : 'Git worktrees disabled - Tasks work in main branch'
          }
          arrow
        >
          <FormControlLabel
            control={
              <Switch
                checked={worktreeEnabled}
                onChange={handleWorktreeToggle}
                disabled={loading}
                size="small"
                sx={{
                  '& .MuiSwitch-switchBase.Mui-checked': {
                    color: '#6366f1',
                  },
                  '& .MuiSwitch-switchBase.Mui-checked + .MuiSwitch-track': {
                    backgroundColor: '#6366f1',
                  },
                }}
              />
            }
            label={
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                <WorktreeIcon sx={{ fontSize: 16, color: '#94a3b8' }} />
                <Typography
                  variant="caption"
                  sx={{
                    color: '#94a3b8',
                    display: { xs: 'none', lg: 'block' },
                  }}
                >
                  Worktrees
                </Typography>
              </Box>
            }
            sx={{
              ml: 2,
              mr: 0,
              display: { xs: 'none', sm: 'flex' },
              '& .MuiFormControlLabel-label': {
                ml: 0.5,
              },
            }}
          />
        </Tooltip>
      )}
    </Box>
  );
};

export default ProjectModeToggle;
