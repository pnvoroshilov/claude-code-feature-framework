import React, { useState } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  TextField,
  Button,
  Alert,
  CircularProgress,
  Step,
  Stepper,
  StepLabel,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Chip,
} from '@mui/material';
import {
  Folder as FolderIcon,
  CheckCircle as CheckIcon,
  Warning as WarningIcon,
} from '@mui/icons-material';
import { useMutation, useQueryClient } from 'react-query';
import { initializeProject, InitializeProjectRequest } from '../services/api';

const steps = ['Project Configuration', 'Initialize', 'Setup Complete'];

const ProjectSetup: React.FC = () => {
  const [activeStep, setActiveStep] = useState(0);
  const [projectData, setProjectData] = useState<InitializeProjectRequest>({
    project_path: '',
    project_name: '',
    github_repo: '',
  });
  const [initResult, setInitResult] = useState<any>(null);

  const queryClient = useQueryClient();

  const initializeMutation = useMutation(initializeProject, {
    onSuccess: (result) => {
      setInitResult(result);
      setActiveStep(2);
      queryClient.invalidateQueries('activeProject');
    },
    onError: (error: any) => {
      console.error('Initialization failed:', error);
    },
  });

  const handleNext = () => {
    if (activeStep === 0) {
      if (projectData.project_path && projectData.project_name) {
        setActiveStep(1);
        initializeMutation.mutate(projectData);
      }
    }
  };

  const handleReset = () => {
    setActiveStep(0);
    setProjectData({ project_path: '', project_name: '', github_repo: '' });
    setInitResult(null);
  };

  const renderStepContent = () => {
    switch (activeStep) {
      case 0:
        return (
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Project Configuration
              </Typography>
              <Typography variant="body2" color="text.secondary" paragraph>
                Configure your project to work with ClaudeTask. This will create the necessary
                configuration files and set up MCP integration.
              </Typography>
              
              <TextField
                fullWidth
                label="Project Path"
                placeholder="/path/to/your/project"
                value={projectData.project_path}
                onChange={(e) => setProjectData({ ...projectData, project_path: e.target.value })}
                sx={{ mb: 2 }}
                helperText="Absolute path to your project directory"
              />
              
              <TextField
                fullWidth
                label="Project Name"
                placeholder="My Awesome Project"
                value={projectData.project_name}
                onChange={(e) => setProjectData({ ...projectData, project_name: e.target.value })}
                sx={{ mb: 2 }}
                helperText="Display name for your project"
              />
              
              <TextField
                fullWidth
                label="GitHub Repository (Optional)"
                placeholder="https://github.com/user/repo"
                value={projectData.github_repo}
                onChange={(e) => setProjectData({ ...projectData, github_repo: e.target.value })}
                sx={{ mb: 3 }}
                helperText="Link to your GitHub repository"
              />

              <Alert severity="info" sx={{ mb: 2 }}>
                <Typography variant="body2">
                  <strong>What happens during initialization:</strong>
                </Typography>
                <List dense>
                  <ListItem>
                    <ListItemIcon><FolderIcon fontSize="small" /></ListItemIcon>
                    <ListItemText primary="Creates .claudetask/ directory in your project" />
                  </ListItem>
                  <ListItem>
                    <ListItemIcon><CheckIcon fontSize="small" /></ListItemIcon>
                    <ListItemText primary="Generates CLAUDE.md configuration" />
                  </ListItem>
                  <ListItem>
                    <ListItemIcon><CheckIcon fontSize="small" /></ListItemIcon>
                    <ListItemText primary="Sets up default agents" />
                  </ListItem>
                  <ListItem>
                    <ListItemIcon><CheckIcon fontSize="small" /></ListItemIcon>
                    <ListItemText primary="Creates .mcp.json for Claude Code integration" />
                  </ListItem>
                </List>
              </Alert>

              <Button
                variant="contained"
                onClick={handleNext}
                disabled={!projectData.project_path || !projectData.project_name}
                fullWidth
              >
                Initialize Project
              </Button>
            </CardContent>
          </Card>
        );

      case 1:
        return (
          <Card>
            <CardContent>
              <Box display="flex" flexDirection="column" alignItems="center" py={4}>
                <CircularProgress size={60} sx={{ mb: 2 }} />
                <Typography variant="h6" gutterBottom>
                  Initializing Project...
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Setting up ClaudeTask configuration for {projectData.project_name}
                </Typography>
              </Box>
              
              {initializeMutation.error && (
                <Alert severity="error" sx={{ mt: 2 }}>
                  Initialization failed: {(initializeMutation.error as any)?.response?.data?.detail || 'Unknown error'}
                </Alert>
              )}
            </CardContent>
          </Card>
        );

      case 2:
        return (
          <Card>
            <CardContent>
              <Box display="flex" flexDirection="column" alignItems="center" py={2}>
                <CheckIcon color="success" sx={{ fontSize: 60, mb: 2 }} />
                <Typography variant="h6" gutterBottom color="success.main">
                  Project Initialized Successfully!
                </Typography>
              </Box>

              {initResult && (
                <Box>
                  <Typography variant="subtitle1" gutterBottom>
                    Configuration Details:
                  </Typography>
                  
                  <Box sx={{ mb: 2 }}>
                    <Typography variant="body2" color="text.secondary">
                      Project ID: <Chip label={initResult.project_id} size="small" />
                    </Typography>
                  </Box>

                  <Box sx={{ mb: 2 }}>
                    <Typography variant="body2" color="text.secondary">
                      MCP Configured: {initResult.mcp_configured ? 
                        <Chip label="Yes" color="success" size="small" /> : 
                        <Chip label="No" color="error" size="small" />
                      }
                    </Typography>
                  </Box>

                  <Typography variant="subtitle2" gutterBottom>
                    Files Created:
                  </Typography>
                  <List dense>
                    {initResult.files_created.map((file: string, index: number) => (
                      <ListItem key={index}>
                        <ListItemIcon>
                          <CheckIcon fontSize="small" color="success" />
                        </ListItemIcon>
                        <ListItemText primary={file} />
                      </ListItem>
                    ))}
                  </List>

                  {initResult.claude_restart_required && (
                    <Alert severity="warning" sx={{ mt: 2 }}>
                      <Typography variant="body2">
                        <strong>Important:</strong> You need to restart Claude Code for the MCP configuration to take effect.
                        The .mcp.json file has been created in your project root.
                      </Typography>
                    </Alert>
                  )}

                  <Alert severity="success" sx={{ mt: 2 }}>
                    <Typography variant="body2">
                      Your project is now ready for ClaudeTask! You can start creating tasks and let Claude handle the implementation.
                    </Typography>
                  </Alert>
                </Box>
              )}

              <Button
                variant="outlined"
                onClick={handleReset}
                fullWidth
                sx={{ mt: 3 }}
              >
                Initialize Another Project
              </Button>
            </CardContent>
          </Card>
        );

      default:
        return null;
    }
  };

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Project Setup
      </Typography>
      
      <Typography variant="body1" color="text.secondary" paragraph>
        Initialize your project to work with ClaudeTask and Claude Code.
      </Typography>

      <Stepper activeStep={activeStep} sx={{ mb: 4 }}>
        {steps.map((label) => (
          <Step key={label}>
            <StepLabel>{label}</StepLabel>
          </Step>
        ))}
      </Stepper>

      {renderStepContent()}
    </Box>
  );
};

export default ProjectSetup;