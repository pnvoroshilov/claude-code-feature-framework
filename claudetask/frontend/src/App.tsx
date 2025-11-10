import React, { useState } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { Box } from '@mui/material';
import { QueryClient, QueryClientProvider } from 'react-query';
import { ReactQueryDevtools } from 'react-query/devtools';

import Header from './components/Header';
import Sidebar from './components/Sidebar';
import Dashboard from './pages/Dashboard';
import ProjectSetup from './pages/ProjectSetup';
import ProjectManager from './pages/ProjectManager';
import TaskBoard from './pages/TaskBoard';
import ClaudeSessions from './pages/ClaudeSessions';
import Skills from './pages/Skills';
import MCPConfigs from './pages/MCPConfigs';
import Subagents from './pages/Subagents';
import Settings from './pages/Settings';
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
            <Box sx={{ display: 'flex', minHeight: '100vh' }}>
              <Header onMenuClick={toggleSidebar} />
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
                  mt: 8,
                  minHeight: 'calc(100vh - 64px)',
                }}
              >
                <Routes>
                  <Route path="/" element={<Dashboard />} />
                  <Route path="/setup" element={<ProjectSetup />} />
                  <Route path="/projects" element={<ProjectManager />} />
                  <Route path="/tasks" element={<TaskBoard />} />
                  <Route path="/sessions" element={<ClaudeSessions />} />
                  <Route path="/skills" element={<Skills />} />
                  <Route path="/mcp-configs" element={<MCPConfigs />} />
                  <Route path="/subagents" element={<Subagents />} />
                  <Route path="/settings" element={<Settings />} />
                </Routes>
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