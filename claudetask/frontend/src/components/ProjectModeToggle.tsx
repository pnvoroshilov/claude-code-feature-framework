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
  PersonOutline as ManualIcon,
  SmartToy as AutoIcon,
} from '@mui/icons-material';
import { useProject } from '../context/ProjectContext';
import { useThemeMode } from '../context/ThemeContext';
import { getProjectSettings, updateProjectSettings } from '../services/api';

const ProjectModeToggle: React.FC = () => {
  const { selectedProject, refreshProjects } = useProject();
  const { mode: themeMode } = useThemeMode();
  const [worktreeEnabled, setWorktreeEnabled] = useState<boolean>(true);
  const [manualMode, setManualMode] = useState<boolean>(true);
  const [loading, setLoading] = useState<boolean>(false);

  const projectMode = selectedProject?.project_mode || 'simple';

  console.log('ProjectModeToggle render:', {
    projectMode,
    worktreeEnabled,
    selectedProject: selectedProject?.name,
    willShowWorktreeToggle: projectMode === 'development'
  });

  // Load project settings to get worktree_enabled value
  useEffect(() => {
    const loadSettings = async () => {
      if (!selectedProject) {
        console.log('No selected project, skipping settings load');
        return;
      }

      try {
        console.log('Loading project settings for:', selectedProject.id);
        const settings = await getProjectSettings(selectedProject.id);
        console.log('Project settings loaded:', settings);
        setWorktreeEnabled(settings.worktree_enabled);
        setManualMode(settings.manual_mode);
      } catch (error) {
        console.error('Failed to load project settings:', error);
      }
    };

    loadSettings();
  }, [selectedProject]);

  const handleWorktreeToggle = async (event: React.ChangeEvent<HTMLInputElement>) => {
    if (!selectedProject) {
      console.error('No selected project');
      return;
    }

    const newValue = event.target.checked;
    console.log('Worktree toggle clicked:', { newValue, projectId: selectedProject.id });
    setLoading(true);

    try {
      console.log('Updating project settings...');
      await updateProjectSettings(selectedProject.id, {
        worktree_enabled: newValue
      });
      console.log('Settings updated successfully');

      setWorktreeEnabled(newValue);

      // Refresh projects to trigger CLAUDE.md regeneration
      console.log('Refreshing projects...');
      await refreshProjects();
      console.log('Projects refreshed');
    } catch (error) {
      console.error('Failed to update worktree setting:', error);
      // Revert on error
      setWorktreeEnabled(!newValue);
    } finally {
      setLoading(false);
    }
  };

  const handleManualModeToggle = async (event: React.ChangeEvent<HTMLInputElement>) => {
    if (!selectedProject) {
      console.error('No selected project');
      return;
    }

    const newValue = event.target.checked;
    console.log('Manual mode toggle clicked:', { newValue, projectId: selectedProject.id });
    setLoading(true);

    try {
      console.log('Updating manual mode setting...');
      await updateProjectSettings(selectedProject.id, {
        manual_mode: newValue
      });
      console.log('Manual mode updated successfully');

      setManualMode(newValue);

      // Refresh projects to trigger CLAUDE.md regeneration
      console.log('Refreshing projects...');
      await refreshProjects();
      console.log('Projects refreshed');
    } catch (error) {
      console.error('Failed to update manual mode setting:', error);
      // Revert on error
      setManualMode(!newValue);
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

      {/* Manual Mode Toggle - Show for all projects */}
      <Tooltip
        title={
          manualMode
            ? 'Manual Mode: You test and review tasks manually'
            : 'Automated Mode: Testing agents and code review run automatically'
        }
        arrow
      >
        <FormControlLabel
          control={
            <Switch
              checked={manualMode}
              onChange={handleManualModeToggle}
              disabled={loading}
              size="small"
              sx={{
                '& .MuiSwitch-switchBase.Mui-checked': {
                  color: '#3b82f6',
                },
                '& .MuiSwitch-switchBase.Mui-checked + .MuiSwitch-track': {
                  backgroundColor: '#3b82f6',
                },
              }}
            />
          }
          label={
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
              {manualMode ? (
                <ManualIcon sx={{ fontSize: 16, color: '#3b82f6' }} />
              ) : (
                <AutoIcon sx={{ fontSize: 16, color: '#10b981' }} />
              )}
              <Chip
                label={manualMode ? 'MANUAL' : 'AUTO'}
                size="small"
                sx={{
                  height: 20,
                  fontSize: '0.7rem',
                  fontWeight: 600,
                  bgcolor: manualMode
                    ? alpha('#3b82f6', 0.15)
                    : alpha('#10b981', 0.15),
                  color: manualMode ? '#3b82f6' : '#10b981',
                  border: `1px solid ${manualMode
                    ? alpha('#3b82f6', 0.3)
                    : alpha('#10b981', 0.3)}`,
                  '& .MuiChip-label': {
                    px: 1,
                  },
                }}
              />
            </Box>
          }
          sx={{
            ml: 2,
            mr: 0,
            display: 'flex',
            '& .MuiFormControlLabel-label': {
              ml: 0.5,
            },
          }}
        />
      </Tooltip>

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
