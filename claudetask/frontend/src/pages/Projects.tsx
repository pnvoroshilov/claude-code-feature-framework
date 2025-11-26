import React, { useState, useEffect } from 'react';
import {
  Box,
  Container,
  Tabs,
  Tab,
  Typography,
  alpha,
  useTheme,
} from '@mui/material';
import { useLocation, useNavigate } from 'react-router-dom';
import ProjectListView from '../components/projects/ProjectListView';
import ProjectInstructionsView from '../components/projects/ProjectInstructionsView';
import ProjectSetupView from '../components/projects/ProjectSetupView';

type TabValue = 'list' | 'instructions' | 'setup';

const Projects: React.FC = () => {
  const theme = useTheme();
  const location = useLocation();
  const navigate = useNavigate();

  const [currentTab, setCurrentTab] = useState<TabValue>('list');

  // URL-based tab state management
  useEffect(() => {
    const path = location.pathname;

    if (path === '/projects' || path === '/projects/') {
      // Default to Projects List
      navigate('/projects/list', { replace: true });
      setCurrentTab('list');
    } else if (path.includes('/list')) {
      setCurrentTab('list');
    } else if (path.includes('/instructions')) {
      setCurrentTab('instructions');
    } else if (path.includes('/setup')) {
      setCurrentTab('setup');
    }
  }, [location.pathname, navigate]);

  // Tab change handler
  const handleTabChange = (_event: React.SyntheticEvent, newValue: TabValue) => {
    setCurrentTab(newValue);
    navigate(`/projects/${newValue}`, { replace: true });
  };

  const tabAccentColor = theme.palette.primary.main;

  return (
    <Container maxWidth="xl" sx={{ py: 4 }}>
      {/* Page Header */}
      <Box sx={{ mb: 4 }}>
        <Typography
          variant="h3"
          component="h1"
          sx={{
            fontWeight: 700,
            background: `linear-gradient(135deg, ${tabAccentColor}, ${alpha(tabAccentColor, 0.7)})`,
            WebkitBackgroundClip: 'text',
            WebkitTextFillColor: 'transparent',
            mb: 1,
          }}
        >
          Projects
        </Typography>
        <Typography
          variant="body1"
          sx={{
            color: alpha(theme.palette.text.secondary, 0.8),
            maxWidth: '600px',
          }}
        >
          Manage ClaudeTask projects, configure instructions, and initialize new projects
        </Typography>
      </Box>

      {/* Tab Navigation */}
      <Tabs
        value={currentTab}
        onChange={handleTabChange}
        variant="scrollable"
        scrollButtons="auto"
        aria-label="Project management navigation"
        sx={{
          mb: 3,
          borderBottom: 1,
          borderColor: 'divider',
          '& .MuiTab-root': {
            minWidth: { xs: 120, md: 160 },
            fontSize: { xs: '0.875rem', md: '1rem' },
            fontWeight: 600,
            textTransform: 'none',
            transition: 'all 0.3s ease',
            '&:hover': {
              color: tabAccentColor,
            },
          },
          '& .Mui-selected': {
            color: `${tabAccentColor} !important`,
          },
          '& .MuiTabs-indicator': {
            backgroundColor: tabAccentColor,
            height: 3,
            borderRadius: '3px 3px 0 0',
          },
        }}
      >
        <Tab
          label="Projects"
          value="list"
          id="tab-list"
          aria-controls="tabpanel-list"
        />
        <Tab
          label="Instructions"
          value="instructions"
          id="tab-instructions"
          aria-controls="tabpanel-instructions"
        />
        <Tab
          label="Setup"
          value="setup"
          id="tab-setup"
          aria-controls="tabpanel-setup"
        />
      </Tabs>

      {/* Tab Panels */}
      <Box
        role="tabpanel"
        hidden={currentTab !== 'list'}
        id="tabpanel-list"
        aria-labelledby="tab-list"
      >
        {currentTab === 'list' && <ProjectListView />}
      </Box>

      <Box
        role="tabpanel"
        hidden={currentTab !== 'instructions'}
        id="tabpanel-instructions"
        aria-labelledby="tab-instructions"
      >
        {currentTab === 'instructions' && <ProjectInstructionsView />}
      </Box>

      <Box
        role="tabpanel"
        hidden={currentTab !== 'setup'}
        id="tabpanel-setup"
        aria-labelledby="tab-setup"
      >
        {currentTab === 'setup' && <ProjectSetupView />}
      </Box>
    </Container>
  );
};

export default Projects;
