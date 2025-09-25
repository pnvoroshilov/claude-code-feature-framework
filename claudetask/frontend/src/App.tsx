import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import { CssBaseline, Box } from '@mui/material';
import { QueryClient, QueryClientProvider } from 'react-query';
import { ReactQueryDevtools } from 'react-query/devtools';

import Header from './components/Header';
import Sidebar from './components/Sidebar';
import Dashboard from './pages/Dashboard';
import ProjectSetup from './pages/ProjectSetup';
import ProjectManager from './pages/ProjectManager';
import TaskBoard from './pages/TaskBoard';
import ClaudeSessions from './pages/ClaudeSessions';
import Settings from './pages/Settings';
import { ProjectProvider } from './context/ProjectContext';

const theme = createTheme({
  palette: {
    mode: 'light',
    primary: {
      main: '#1976d2',
    },
    secondary: {
      main: '#dc004e',
    },
  },
});

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
    },
  },
});

function App() {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <QueryClientProvider client={queryClient}>
        <ProjectProvider>
          <Router>
            <Box sx={{ display: 'flex' }}>
              <Header />
              <Sidebar />
              <Box
                component="main"
                sx={{
                  flexGrow: 1,
                  bgcolor: 'background.default',
                  p: 3,
                  mt: 8, // Account for header height
                  ml: 30, // Account for sidebar width
                }}
              >
                <Routes>
                  <Route path="/" element={<Dashboard />} />
                  <Route path="/setup" element={<ProjectSetup />} />
                  <Route path="/projects" element={<ProjectManager />} />
                  <Route path="/tasks" element={<TaskBoard />} />
                  <Route path="/sessions" element={<ClaudeSessions />} />
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