import React from 'react';
import {
  AppBar,
  Toolbar,
  Typography,
  Box,
  IconButton,
  Chip,
  CircularProgress,
  Tooltip,
  alpha,
} from '@mui/material';
import {
  Settings as SettingsIcon,
  Refresh as RefreshIcon,
  Menu as MenuIcon,
  Brightness4 as DarkModeIcon,
  Brightness7 as LightModeIcon,
} from '@mui/icons-material';
import { useQuery } from 'react-query';
import { Link } from 'react-router-dom';
import { getConnectionStatus } from '../services/api';
import { useThemeMode } from '../context/ThemeContext';
import ProjectSelector from './ProjectSelector';

interface HeaderProps {
  onMenuClick: () => void;
}

const Header: React.FC<HeaderProps> = ({ onMenuClick }) => {
  const { mode, toggleTheme } = useThemeMode();

  const { data: connection, isLoading: connectionLoading, refetch: refetchConnection } = useQuery(
    'connectionStatus',
    getConnectionStatus,
    { refetchInterval: 10000 }
  );

  return (
    <AppBar
      position="fixed"
      elevation={0}
      sx={{
        zIndex: (theme) => theme.zIndex.drawer + 1,
        backdropFilter: 'blur(10px)',
        bgcolor: mode === 'dark'
          ? alpha('#1e293b', 0.8)
          : alpha('#ffffff', 0.8),
        borderBottom: mode === 'dark' ? '1px solid #334155' : '1px solid #e2e8f0',
      }}
    >
      <Toolbar>
        <IconButton
          color="inherit"
          aria-label="open drawer"
          edge="start"
          onClick={onMenuClick}
          sx={{ mr: 2, display: { md: 'none' } }}
        >
          <MenuIcon />
        </IconButton>

        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
          <Box
            sx={{
              width: 32,
              height: 32,
              borderRadius: 2,
              background: 'linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              fontWeight: 700,
              color: 'white',
              fontSize: '1rem',
            }}
          >
            CT
          </Box>
          <Typography
            variant="h6"
            component="div"
            sx={{
              fontWeight: 700,
              background: 'linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%)',
              WebkitBackgroundClip: 'text',
              WebkitTextFillColor: 'transparent',
              backgroundClip: 'text',
              display: { xs: 'none', sm: 'block' },
            }}
          >
            ClaudeTask
          </Typography>

          {/* Project Selector - Minimal */}
          <Box sx={{ display: { xs: 'none', md: 'block' } }}>
            <ProjectSelector
              size="small"
              variant="standard"
              showStatus={false}
              minimal={true}
            />
          </Box>
        </Box>

        <Box sx={{ flexGrow: 1 }} />

          {/* Connection Status */}
          {connectionLoading ? (
            <CircularProgress size={20} />
          ) : (
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <Tooltip title={connection?.connected ? 'Claude Connected' : 'Claude Disconnected'}>
                <Chip
                  label={connection?.connected ? 'Connected' : 'Disconnected'}
                  color={connection?.connected ? 'success' : 'error'}
                  size="small"
                  variant="outlined"
                  sx={{
                    height: 28,
                    fontWeight: 500,
                    display: { xs: 'none', md: 'flex' },
                  }}
                />
              </Tooltip>
              <Tooltip title="Refresh Connection">
                <IconButton
                  size="small"
                  onClick={() => refetchConnection()}
                  sx={{
                    color: 'text.secondary',
                    '&:hover': {
                      color: 'primary.main',
                      transform: 'rotate(90deg)',
                    },
                    transition: 'all 0.3s',
                  }}
                >
                  <RefreshIcon />
                </IconButton>
              </Tooltip>
            </Box>
          )}

          {/* Theme Toggle */}
          <Tooltip title={mode === 'dark' ? 'Light Mode' : 'Dark Mode'}>
            <IconButton
              onClick={toggleTheme}
              size="small"
              sx={{
                color: 'text.secondary',
                '&:hover': {
                  color: 'primary.main',
                },
              }}
            >
              {mode === 'dark' ? <LightModeIcon /> : <DarkModeIcon />}
            </IconButton>
          </Tooltip>

          {/* Settings */}
          <Tooltip title="Settings">
            <IconButton
              component={Link}
              to="/settings"
              size="small"
              sx={{
                color: 'text.secondary',
                '&:hover': {
                  color: 'primary.main',
                },
              }}
            >
              <SettingsIcon />
            </IconButton>
          </Tooltip>
        </Box>
      </Toolbar>
    </AppBar>
  );
};

export default Header;