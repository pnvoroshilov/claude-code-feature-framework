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
  Avatar,
  Badge,
  Breadcrumbs,
  Link as MuiLink,
} from '@mui/material';
import {
  Settings as SettingsIcon,
  Refresh as RefreshIcon,
  Menu as MenuIcon,
  Brightness4 as DarkModeIcon,
  Brightness7 as LightModeIcon,
  Notifications as NotificationsIcon,
  Home as HomeIcon,
  NavigateNext as NavigateNextIcon,
} from '@mui/icons-material';
import { useQuery } from 'react-query';
import { Link, useLocation } from 'react-router-dom';
import { getConnectionStatus } from '../services/api';
import { useThemeMode } from '../context/ThemeContext';
import ProjectSelector from './ProjectSelector';

interface HeaderProps {
  onMenuClick: () => void;
}

const Header: React.FC<HeaderProps> = ({ onMenuClick }) => {
  const { mode, toggleTheme } = useThemeMode();
  const location = useLocation();

  const { data: connection, isLoading: connectionLoading, refetch: refetchConnection } = useQuery(
    'connectionStatus',
    getConnectionStatus,
    { refetchInterval: 10000 }
  );

  // Generate breadcrumbs from current path
  const generateBreadcrumbs = () => {
    const paths = location.pathname.split('/').filter(Boolean);
    const breadcrumbs = [{ label: 'Home', path: '/' }];

    let currentPath = '';
    paths.forEach((path) => {
      currentPath += `/${path}`;
      breadcrumbs.push({
        label: path.charAt(0).toUpperCase() + path.slice(1),
        path: currentPath,
      });
    });

    return breadcrumbs;
  };

  const breadcrumbs = generateBreadcrumbs();

  return (
    <AppBar
      position="fixed"
      elevation={0}
      sx={{
        zIndex: (theme) => theme.zIndex.drawer + 1,
        backdropFilter: 'blur(20px)',
        WebkitBackdropFilter: 'blur(20px)',
        bgcolor: mode === 'dark'
          ? alpha('#0f172a', 0.85)
          : alpha('#ffffff', 0.85),
        borderBottom: mode === 'dark'
          ? `1px solid ${alpha('#334155', 0.5)}`
          : `1px solid ${alpha('#e2e8f0', 0.5)}`,
        transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
        '&::before': {
          content: '""',
          position: 'absolute',
          bottom: 0,
          left: 0,
          right: 0,
          height: '1px',
          background: mode === 'dark'
            ? 'linear-gradient(90deg, transparent, rgba(99, 102, 241, 0.5), transparent)'
            : 'linear-gradient(90deg, transparent, rgba(99, 102, 241, 0.3), transparent)',
          opacity: 0.5,
        },
      }}
    >
      <Toolbar sx={{ minHeight: { xs: 64, sm: 70 }, px: { xs: 2, sm: 3 } }}>
        {/* Mobile Menu Button */}
        <IconButton
          color="inherit"
          aria-label="open drawer"
          edge="start"
          onClick={onMenuClick}
          sx={{
            mr: 2,
            display: { md: 'none' },
            color: 'text.primary',
            '&:hover': {
              background: `linear-gradient(135deg, ${alpha('#6366f1', 0.15)}, ${alpha('#8b5cf6', 0.1)})`,
            },
          }}
        >
          <MenuIcon />
        </IconButton>

        {/* Left Section: Logo & Breadcrumbs */}
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, flexGrow: 1 }}>
          {/* Logo */}
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5 }}>
            <Box
              sx={{
                width: 40,
                height: 40,
                borderRadius: 2.5,
                background: 'linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                fontWeight: 700,
                color: 'white',
                fontSize: '1.1rem',
                boxShadow: mode === 'dark'
                  ? `0 4px 12px ${alpha('#6366f1', 0.3)}`
                  : `0 4px 12px ${alpha('#6366f1', 0.2)}`,
                transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
                '&:hover': {
                  transform: 'scale(1.05)',
                  boxShadow: mode === 'dark'
                    ? `0 6px 16px ${alpha('#6366f1', 0.4)}`
                    : `0 6px 16px ${alpha('#6366f1', 0.3)}`,
                },
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
                fontSize: '1.25rem',
                letterSpacing: '-0.02em',
              }}
            >
              ClaudeTask
            </Typography>
          </Box>

          {/* Breadcrumbs - Desktop */}
          <Box sx={{ display: { xs: 'none', lg: 'flex' }, alignItems: 'center', ml: 2 }}>
            <Breadcrumbs
              separator={<NavigateNextIcon fontSize="small" sx={{ color: 'text.secondary' }} />}
              sx={{
                '& .MuiBreadcrumbs-separator': {
                  mx: 1,
                },
              }}
            >
              {breadcrumbs.map((crumb, index) => {
                const isLast = index === breadcrumbs.length - 1;
                return isLast ? (
                  <Typography
                    key={crumb.path}
                    color="text.primary"
                    sx={{
                      display: 'flex',
                      alignItems: 'center',
                      gap: 0.5,
                      fontWeight: 600,
                      fontSize: '0.875rem',
                    }}
                  >
                    {crumb.label}
                  </Typography>
                ) : (
                  <MuiLink
                    key={crumb.path}
                    component={Link}
                    to={crumb.path}
                    sx={{
                      display: 'flex',
                      alignItems: 'center',
                      gap: 0.5,
                      color: 'text.secondary',
                      textDecoration: 'none',
                      fontSize: '0.875rem',
                      transition: 'color 0.2s',
                      '&:hover': {
                        color: 'primary.main',
                      },
                    }}
                  >
                    {index === 0 && <HomeIcon sx={{ fontSize: 16 }} />}
                    {crumb.label}
                  </MuiLink>
                );
              })}
            </Breadcrumbs>
          </Box>

          {/* Project Selector - Minimal */}
          <Box sx={{ display: { xs: 'none', md: 'block' }, ml: 'auto', mr: 2 }}>
            <ProjectSelector
              size="small"
              variant="standard"
              showStatus={false}
              minimal={true}
            />
          </Box>
        </Box>

        {/* Right Section: Actions */}
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          {/* Connection Status */}
          {connectionLoading ? (
            <CircularProgress size={20} sx={{ color: 'primary.main' }} />
          ) : (
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <Tooltip title={connection?.connected ? 'Claude Connected' : 'Claude Disconnected'}>
                <Chip
                  label={connection?.connected ? 'Connected' : 'Disconnected'}
                  color={connection?.connected ? 'success' : 'error'}
                  size="small"
                  variant="outlined"
                  sx={{
                    height: 32,
                    fontWeight: 600,
                    fontSize: '0.75rem',
                    display: { xs: 'none', md: 'flex' },
                    backdropFilter: 'blur(8px)',
                    background: connection?.connected
                      ? alpha('#10b981', 0.08)
                      : alpha('#ef4444', 0.08),
                    borderColor: connection?.connected
                      ? alpha('#10b981', 0.3)
                      : alpha('#ef4444', 0.3),
                  }}
                />
              </Tooltip>
              <Tooltip title="Refresh Connection">
                <IconButton
                  size="small"
                  onClick={() => refetchConnection()}
                  sx={{
                    color: 'text.secondary',
                    transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
                    '&:hover': {
                      color: 'primary.main',
                      background: `linear-gradient(135deg, ${alpha('#6366f1', 0.15)}, ${alpha('#8b5cf6', 0.1)})`,
                      transform: 'rotate(180deg)',
                    },
                  }}
                >
                  <RefreshIcon fontSize="small" />
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
                transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
                '&:hover': {
                  color: mode === 'dark' ? '#fbbf24' : '#6366f1',
                  background: mode === 'dark'
                    ? `linear-gradient(135deg, ${alpha('#fbbf24', 0.15)}, ${alpha('#f59e0b', 0.1)})`
                    : `linear-gradient(135deg, ${alpha('#6366f1', 0.15)}, ${alpha('#8b5cf6', 0.1)})`,
                  transform: 'rotate(180deg)',
                },
              }}
            >
              {mode === 'dark' ? (
                <LightModeIcon fontSize="small" />
              ) : (
                <DarkModeIcon fontSize="small" />
              )}
            </IconButton>
          </Tooltip>

          {/* Notifications */}
          <Tooltip title="Notifications">
            <IconButton
              size="small"
              sx={{
                color: 'text.secondary',
                transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
                display: { xs: 'none', sm: 'flex' },
                '&:hover': {
                  color: 'primary.main',
                  background: `linear-gradient(135deg, ${alpha('#6366f1', 0.15)}, ${alpha('#8b5cf6', 0.1)})`,
                },
              }}
            >
              <Badge
                badgeContent={3}
                color="error"
                sx={{
                  '& .MuiBadge-badge': {
                    background: 'linear-gradient(135deg, #ef4444, #dc2626)',
                    boxShadow: `0 2px 8px ${alpha('#ef4444', 0.4)}`,
                    fontWeight: 600,
                    fontSize: '0.65rem',
                  },
                }}
              >
                <NotificationsIcon fontSize="small" />
              </Badge>
            </IconButton>
          </Tooltip>

          {/* User Avatar */}
          <Tooltip title="Profile">
            <IconButton
              size="small"
              sx={{
                p: 0,
                ml: 0.5,
                display: { xs: 'none', sm: 'flex' },
                transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
                '&:hover': {
                  transform: 'scale(1.1)',
                },
              }}
            >
              <Badge
                overlap="circular"
                anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}
                badgeContent={
                  <Box
                    sx={{
                      width: 10,
                      height: 10,
                      borderRadius: '50%',
                      background: 'linear-gradient(135deg, #10b981, #059669)',
                      border: `2px solid ${mode === 'dark' ? '#0f172a' : '#ffffff'}`,
                      boxShadow: `0 0 0 1px ${alpha('#10b981', 0.3)}`,
                    }}
                  />
                }
              >
                <Avatar
                  sx={{
                    width: 32,
                    height: 32,
                    background: 'linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%)',
                    fontSize: '0.875rem',
                    fontWeight: 600,
                    boxShadow: mode === 'dark'
                      ? `0 2px 8px ${alpha('#6366f1', 0.3)}`
                      : `0 2px 8px ${alpha('#6366f1', 0.2)}`,
                  }}
                >
                  CT
                </Avatar>
              </Badge>
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
                transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
                '&:hover': {
                  color: 'primary.main',
                  background: `linear-gradient(135deg, ${alpha('#6366f1', 0.15)}, ${alpha('#8b5cf6', 0.1)})`,
                  transform: 'rotate(90deg)',
                },
              }}
            >
              <SettingsIcon fontSize="small" />
            </IconButton>
          </Tooltip>
        </Box>
      </Toolbar>
    </AppBar>
  );
};

export default Header;
