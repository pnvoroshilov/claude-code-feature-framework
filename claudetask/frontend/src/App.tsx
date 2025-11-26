import React, { useState } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { Box } from '@mui/material';
import { QueryClient, QueryClientProvider } from 'react-query';
import { ReactQueryDevtools } from 'react-query/devtools';

import Header from './components/Header';
import Sidebar from './components/Sidebar';
import Dashboard from './pages/Dashboard';
import Projects from './pages/Projects';
import TaskBoard from './pages/TaskBoard';
import Sessions from './pages/Sessions';
import Skills from './pages/Skills';
import Hooks from './pages/Hooks';
import MCPConfigs from './pages/MCPConfigs';
import MCPLogs from './pages/MCPLogs';
import Subagents from './pages/Subagents';
import Settings from './pages/Settings';
import FileBrowser from './pages/FileBrowser';
import CloudStorageSettings from './pages/CloudStorageSettings';
import { ProjectProvider } from './context/ProjectContext';
import { ThemeProvider } from './context/ThemeContext';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
      staleTime: 5000,
    },
  },
});

function App() {
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);

  const toggleSidebar = () => {
    if (window.innerWidth < 960) {
      setSidebarOpen(!sidebarOpen);
    } else {
      setSidebarCollapsed(!sidebarCollapsed);
    }
  };

  const handleSidebarClose = () => {
    if (window.innerWidth < 960) {
      setSidebarOpen(false);
    }
  };

  return (
    <ThemeProvider>
      <QueryClientProvider client={queryClient}>
        <ProjectProvider>
          <Router>
            <Box sx={{ display: 'flex', minHeight: '100vh', flexDirection: 'column' }}>
              <Header onMenuClick={toggleSidebar} />
              <Box sx={{ display: 'flex', flex: 1, mt: '64px' }}>
                <Sidebar
                  open={sidebarOpen}
                  collapsed={sidebarCollapsed}
                  onClose={handleSidebarClose}
                />
                <Box
                  component="main"
                  sx={{
                    flexGrow: 1,
                    bgcolor: 'background.default',
                    pt: { xs: 2, sm: 3 },
                    pr: { xs: 2, sm: 3 },
                    pb: { xs: 2, sm: 3 },
                    pl: 0,
                    minHeight: 'calc(100vh - 64px)',
                  }}
                >
                  <Routes>
                    <Route path="/" element={<Dashboard />} />
                    <Route path="/projects/*" element={<Projects />} />
                    <Route path="/projects/:projectId/files" element={<FileBrowser />} />
                    <Route path="/tasks" element={<TaskBoard />} />
                    <Route path="/sessions/*" element={<Sessions />} />
                    <Route path="/claude-code-sessions" element={<Navigate to="/sessions/claude-code" replace />} />
                    <Route path="/skills" element={<Skills />} />
                    <Route path="/hooks" element={<Hooks />} />
                    <Route path="/mcp-configs" element={<MCPConfigs />} />
                    <Route path="/mcp-logs" element={<MCPLogs />} />
                    <Route path="/subagents" element={<Subagents />} />
                    <Route path="/settings" element={<Settings />} />
                    <Route path="/settings/cloud-storage" element={<CloudStorageSettings />} />
                  </Routes>
                </Box>
              </Box>
            </Box>
            <ReactQueryDevtools initialIsOpen={false} />
          </Router>
        </ProjectProvider>
      </QueryClientProvider>
    </ThemeProvider>
  );
}

export default App;
