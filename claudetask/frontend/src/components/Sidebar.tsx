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
} from '@mui/material';
import {
  Dashboard as DashboardIcon,
  Assignment as TaskIcon,
  Settings as SettingsIcon,
  Build as SetupIcon,
  Folder as ProjectIcon,
  Terminal as TerminalIcon,
  Extension as SkillsIcon,
  Webhook as HooksIcon,
  Hub as MCPIcon,
  SmartToy as SubagentIcon,
  Description as InstructionsIcon,
  ChevronLeft as ChevronLeftIcon,
  ChevronRight as ChevronRightIcon,
  History as HistoryIcon,
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
  { text: 'Claude Sessions', icon: <TerminalIcon />, path: '/sessions' },
  { text: 'Claude Code Sessions', icon: <HistoryIcon />, path: '/claude-code-sessions' },
  { text: 'Skills', icon: <SkillsIcon />, path: '/skills' },
  { text: 'Hooks', icon: <HooksIcon />, path: '/hooks' },
  { text: 'MCP Configs', icon: <MCPIcon />, path: '/mcp-configs' },
  { text: 'Subagents', icon: <SubagentIcon />, path: '/subagents' },
  { text: 'Project Instructions', icon: <InstructionsIcon />, path: '/instructions' },
  { text: 'Project Setup', icon: <SetupIcon />, path: '/setup' },
  { text: 'Settings', icon: <SettingsIcon />, path: '/settings' },
];

const Sidebar: React.FC<SidebarProps> = ({ open, collapsed, onClose }) => {
  const location = useLocation();
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));

  const drawerWidth = collapsed ? 72 : 240;

  const drawer = (
    <Box sx={{ display: 'flex', flexDirection: 'column', height: '100%' }}>
      <Toolbar />

      <Box sx={{ flexGrow: 1, overflowY: 'auto', px: 1 }}>
        <List>
          {menuItems.map((item) => {
            const isActive = location.pathname === item.path;
            return (
              <ListItem key={item.text} disablePadding>
                <Tooltip title={collapsed ? item.text : ''} placement="right">
                  <ListItemButton
                    component={Link}
                    to={item.path}
                    onClick={isMobile ? onClose : undefined}
                    selected={isActive}
                    sx={{
                      borderRadius: 2,
                      mx: 0.5,
                      my: 0.5,
                      minHeight: 48,
                      justifyContent: collapsed ? 'center' : 'initial',
                      px: 2,
                      transition: 'all 0.2s',
                      ...(isActive && {
                        background: 'linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%)',
                        color: 'white',
                        '&:hover': {
                          background: 'linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%)',
                        },
                      }),
                      ...(!isActive && {
                        '&:hover': {
                          bgcolor: alpha(theme.palette.primary.main, 0.08),
                          transform: 'translateX(4px)',
                        },
                      }),
                    }}
                  >
                    <ListItemIcon
                      sx={{
                        minWidth: 0,
                        mr: collapsed ? 0 : 2,
                        justifyContent: 'center',
                        color: isActive ? 'inherit' : 'text.secondary',
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
            p: 2,
            borderTop: 1,
            borderColor: 'divider',
            display: 'flex',
            flexDirection: 'column',
            gap: 0.5,
          }}
        >
          <Typography variant="caption" color="text.secondary">
            ClaudeTask Framework
          </Typography>
          <Typography variant="caption" color="text.secondary" fontWeight={600}>
            v1.0.0
          </Typography>
        </Box>
      )}

      {/* Collapse Toggle (Desktop only) */}
      {!isMobile && (
        <Box
          sx={{
            p: 1,
            borderTop: 1,
            borderColor: 'divider',
            display: 'flex',
            justifyContent: 'center',
          }}
        >
          <Tooltip title={collapsed ? 'Expand Sidebar' : 'Collapse Sidebar'}>
            <IconButton
              onClick={onClose}
              size="small"
              sx={{
                bgcolor: alpha(theme.palette.primary.main, 0.08),
                '&:hover': {
                  bgcolor: alpha(theme.palette.primary.main, 0.16),
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