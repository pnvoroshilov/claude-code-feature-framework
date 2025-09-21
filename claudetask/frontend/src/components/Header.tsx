import React from 'react';
import {
  AppBar,
  Toolbar,
  Typography,
  Box,
  IconButton,
  Chip,
  CircularProgress,
} from '@mui/material';
import { Settings as SettingsIcon, Refresh as RefreshIcon } from '@mui/icons-material';
import { useQuery } from 'react-query';
import { Link } from 'react-router-dom';
import { getActiveProject, getConnectionStatus } from '../services/api';

const Header: React.FC = () => {
  const { data: project, isLoading: projectLoading } = useQuery(
    'activeProject',
    getActiveProject,
    { refetchInterval: 30000 }
  );

  const { data: connection, isLoading: connectionLoading, refetch: refetchConnection } = useQuery(
    'connectionStatus',
    getConnectionStatus,
    { refetchInterval: 10000 }
  );

  return (
    <AppBar position="fixed" sx={{ zIndex: (theme) => theme.zIndex.drawer + 1 }}>
      <Toolbar>
        <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
          ClaudeTask
        </Typography>
        
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
          {/* Project Status */}
          {projectLoading ? (
            <CircularProgress size={20} color="inherit" />
          ) : project ? (
            <Chip
              label={`Project: ${project.name}`}
              color="secondary"
              variant="outlined"
              sx={{ color: 'white', borderColor: 'white' }}
            />
          ) : (
            <Chip
              label="No Project Active"
              color="error"
              variant="outlined"
              sx={{ color: 'white', borderColor: 'white' }}
            />
          )}

          {/* Connection Status */}
          {connectionLoading ? (
            <CircularProgress size={20} color="inherit" />
          ) : (
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <Chip
                label={connection?.connected ? 'Claude Connected' : 'Claude Disconnected'}
                color={connection?.connected ? 'success' : 'error'}
                size="small"
                variant="outlined"
                sx={{ color: 'white', borderColor: 'white' }}
              />
              <IconButton
                color="inherit"
                onClick={() => refetchConnection()}
                size="small"
              >
                <RefreshIcon />
              </IconButton>
            </Box>
          )}

          {/* Settings */}
          <IconButton
            color="inherit"
            component={Link}
            to="/settings"
          >
            <SettingsIcon />
          </IconButton>
        </Box>
      </Toolbar>
    </AppBar>
  );
};

export default Header;