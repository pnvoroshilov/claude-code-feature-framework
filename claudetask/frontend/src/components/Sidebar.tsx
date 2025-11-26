import React from 'react';
import {
  Drawer,
  List,
  ListItem,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  Toolbar,
  Box,
  IconButton,
  Tooltip,
  Typography,
  useTheme,
  useMediaQuery,
  alpha,
  Badge,
} from '@mui/material';
import {
  Dashboard as DashboardIcon,
  Assignment as TaskIcon,
  Settings as SettingsIcon,
  Folder as ProjectIcon,
  Terminal as TerminalIcon,
  Extension as SkillsIcon,
  Webhook as HooksIcon,
  Hub as MCPIcon,
  SmartToy as SubagentIcon,
  ChevronLeft as ChevronLeftIcon,
  ChevronRight as ChevronRightIcon,
  ViewKanban as LogoIcon,
  Article as LogsIcon,
} from '@mui/icons-material';
import { Link, useLocation } from 'react-router-dom';

interface SidebarProps {
  open: boolean;
  collapsed: boolean;
  onClose: () => void;
}

const menuItems = [
  { text: 'Dashboard', icon: <DashboardIcon />, path: '/' },
  { text: 'Task Board', icon: <TaskIcon />, path: '/tasks' },
  { text: 'Projects', icon: <ProjectIcon />, path: '/projects' },
  { text: 'Sessions', icon: <TerminalIcon />, path: '/sessions' },
  { text: 'Skills', icon: <SkillsIcon />, path: '/skills' },
  { text: 'Hooks', icon: <HooksIcon />, path: '/hooks' },
  { text: 'MCP Configs', icon: <MCPIcon />, path: '/mcp-configs' },
  { text: 'Logs', icon: <LogsIcon />, path: '/mcp-logs' },
  { text: 'Subagents', icon: <SubagentIcon />, path: '/subagents' },
  { text: 'Settings', icon: <SettingsIcon />, path: '/settings' },
];

const Sidebar: React.FC<SidebarProps> = ({ open, collapsed, onClose }) => {
  const location = useLocation();
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));

  const drawerWidth = collapsed ? 72 : 260;

  const drawer = (
    <Box
      sx={{
        display: 'flex',
        flexDirection: 'column',
        height: '100%',
        background: theme.palette.mode === 'dark'
          ? alpha(theme.palette.background.paper, 0.6)
          : alpha(theme.palette.background.paper, 0.8),
        backdropFilter: 'blur(20px)',
        position: 'relative',
        '&::after': {
          content: '""',
          position: 'absolute',
          top: 0,
          right: 0,
          width: '1px',
          height: '100%',
          background: theme.palette.mode === 'dark'
            ? 'linear-gradient(180deg, rgba(99, 102, 241, 0.2) 0%, rgba(139, 92, 246, 0.2) 100%)'
            : 'linear-gradient(180deg, rgba(99, 102, 241, 0.1) 0%, rgba(139, 92, 246, 0.1) 100%)',
        },
      }}
    >
      {/* Logo Section */}
      <Box
        sx={{
          p: collapsed ? 2 : 3,
          display: 'flex',
          alignItems: 'center',
          justifyContent: collapsed ? 'center' : 'flex-start',
          gap: 2,
          mt: 1,
          mb: 2,
          mx: 1,
          borderRadius: 2,
          background: 'linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%)',
          boxShadow: theme.palette.mode === 'dark'
            ? '0 4px 12px rgba(99, 102, 241, 0.3)'
            : '0 4px 12px rgba(99, 102, 241, 0.2)',
          transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
        }}
      >
        <LogoIcon
          sx={{
            fontSize: collapsed ? 32 : 36,
            color: 'white',
            filter: 'drop-shadow(0 2px 4px rgba(0,0,0,0.2))',
          }}
        />
        {!collapsed && (
          <Box>
            <Typography
              variant="h6"
              sx={{
                color: 'white',
                fontWeight: 700,
                fontSize: '1.1rem',
                letterSpacing: '-0.02em',
                lineHeight: 1.2,
              }}
            >
              ClaudeTask
            </Typography>
            <Typography
              variant="caption"
              sx={{
                color: alpha('#ffffff', 0.85),
                fontSize: '0.7rem',
                fontWeight: 500,
              }}
            >
              Framework
            </Typography>
          </Box>
        )}
      </Box>

      {/* Navigation Items */}
      <Box
        sx={{
          flexGrow: 1,
          overflowY: 'auto',
          overflowX: 'hidden',
          px: 1.5,
          py: 1,
          '&::-webkit-scrollbar': {
            width: '6px',
          },
          '&::-webkit-scrollbar-track': {
            background: 'transparent',
          },
          '&::-webkit-scrollbar-thumb': {
            background: alpha(theme.palette.primary.main, 0.2),
            borderRadius: '3px',
            '&:hover': {
              background: alpha(theme.palette.primary.main, 0.3),
            },
          },
        }}
      >
        <List sx={{ p: 0 }}>
          {menuItems.map((item) => {
            // Check if current path matches, including sub-routes for Sessions and Projects
            const isActive = item.path === '/sessions'
              ? location.pathname.startsWith('/sessions')
              : item.path === '/projects'
              ? location.pathname.startsWith('/projects') && !location.pathname.includes('/files')
              : location.pathname === item.path;
            return (
              <ListItem key={item.text} disablePadding sx={{ mb: 0.5 }}>
                <Tooltip
                  title={collapsed ? item.text : ''}
                  placement="right"
                  arrow
                >
                  <ListItemButton
                    component={Link}
                    to={item.path}
                    onClick={isMobile ? onClose : undefined}
                    selected={isActive}
                    sx={{
                      borderRadius: 2,
                      minHeight: 48,
                      justifyContent: collapsed ? 'center' : 'initial',
                      px: collapsed ? 1.5 : 2,
                      py: 1.25,
                      position: 'relative',
                      overflow: 'hidden',
                      transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
                      ...(isActive && {
                        background: 'linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%)',
                        color: 'white',
                        boxShadow: theme.palette.mode === 'dark'
                          ? '0 4px 12px rgba(99, 102, 241, 0.3)'
                          : '0 4px 12px rgba(99, 102, 241, 0.2)',
                        transform: 'translateX(4px)',
                        '&:hover': {
                          background: 'linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%)',
                          transform: 'translateX(6px)',
                        },
                        '&::before': {
                          content: '""',
                          position: 'absolute',
                          top: 0,
                          left: 0,
                          width: '3px',
                          height: '100%',
                          background: 'white',
                          boxShadow: '0 0 10px rgba(255,255,255,0.5)',
                        },
                      }),
                      ...(!isActive && {
                        bgcolor: 'transparent',
                        '&:hover': {
                          bgcolor: theme.palette.mode === 'dark'
                            ? alpha(theme.palette.primary.main, 0.12)
                            : alpha(theme.palette.primary.main, 0.08),
                          transform: 'translateX(4px)',
                        },
                      }),
                    }}
                  >
                    <ListItemIcon
                      sx={{
                        minWidth: 0,
                        mr: collapsed ? 0 : 2.5,
                        justifyContent: 'center',
                        color: isActive ? 'inherit' : 'text.secondary',
                        fontSize: 24,
                        transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
                        '& .MuiSvgIcon-root': {
                          fontSize: 24,
                        },
                      }}
                    >
                      {item.icon}
                    </ListItemIcon>
                    {!collapsed && (
                      <ListItemText
                        primary={item.text}
                        primaryTypographyProps={{
                          fontWeight: isActive ? 600 : 500,
                          fontSize: '0.875rem',
                          letterSpacing: '-0.01em',
                        }}
                      />
                    )}
                  </ListItemButton>
                </Tooltip>
              </ListItem>
            );
          })}
        </List>
      </Box>

      {/* Footer with version */}
      {!collapsed && !isMobile && (
        <Box
          sx={{
            p: 2.5,
            mx: 1.5,
            mb: 1.5,
            borderRadius: 2,
            background: theme.palette.mode === 'dark'
              ? alpha(theme.palette.background.default, 0.5)
              : alpha(theme.palette.background.default, 0.3),
            backdropFilter: 'blur(10px)',
            border: `1px solid ${alpha(theme.palette.divider, 0.1)}`,
            display: 'flex',
            flexDirection: 'column',
            gap: 0.5,
          }}
        >
          <Typography
            variant="caption"
            sx={{
              color: 'text.secondary',
              fontWeight: 600,
              fontSize: '0.75rem',
            }}
          >
            ClaudeTask Framework
          </Typography>
          <Typography
            variant="caption"
            sx={{
              color: alpha(theme.palette.text.secondary, 0.7),
              fontSize: '0.7rem',
            }}
          >
            Version 1.0.0
          </Typography>
        </Box>
      )}

      {/* Collapse Toggle (Desktop only) */}
      {!isMobile && (
        <Box
          sx={{
            p: 1.5,
            display: 'flex',
            justifyContent: 'center',
          }}
        >
          <Tooltip
            title={collapsed ? 'Expand Sidebar' : 'Collapse Sidebar'}
            placement="right"
            arrow
          >
            <IconButton
              onClick={onClose}
              size="small"
              sx={{
                width: 36,
                height: 36,
                background: theme.palette.mode === 'dark'
                  ? alpha(theme.palette.primary.main, 0.15)
                  : alpha(theme.palette.primary.main, 0.1),
                color: theme.palette.primary.main,
                backdropFilter: 'blur(10px)',
                transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
                '&:hover': {
                  background: 'linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%)',
                  color: 'white',
                  transform: 'scale(1.1)',
                  boxShadow: '0 4px 12px rgba(99, 102, 241, 0.3)',
                },
              }}
            >
              {collapsed ? <ChevronRightIcon /> : <ChevronLeftIcon />}
            </IconButton>
          </Tooltip>
        </Box>
      )}
    </Box>
  );

  return (
    <>
      {isMobile ? (
        <Drawer
          variant="temporary"
          open={open}
          onClose={onClose}
          ModalProps={{
            keepMounted: true, // Better mobile performance
          }}
          sx={{
            '& .MuiDrawer-paper': {
              width: 240,
              boxSizing: 'border-box',
              borderRight: 'none',
            },
          }}
        >
          {drawer}
        </Drawer>
      ) : (
        <Drawer
          variant="permanent"
          sx={{
            width: drawerWidth,
            flexShrink: 0,
            '& .MuiDrawer-paper': {
              width: drawerWidth,
              boxSizing: 'border-box',
              transition: theme.transitions.create('width', {
                easing: theme.transitions.easing.sharp,
                duration: theme.transitions.duration.enteringScreen,
              }),
              overflowX: 'hidden',
              borderRight: 'none',
            },
          }}
        >
          {drawer}
        </Drawer>
      )}
    </>
  );
};

export default Sidebar;