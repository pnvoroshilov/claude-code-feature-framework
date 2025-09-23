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
  InputAdornment,
  IconButton,
  FormControlLabel,
  Checkbox,
} from '@mui/material';
import {
  Folder as FolderIcon,
  CheckCircle as CheckIcon,
  Warning as WarningIcon,
  FolderOpen as FolderOpenIcon,
} from '@mui/icons-material';
import { useMutation, useQueryClient } from 'react-query';
import { initializeProject, InitializeProjectRequest } from '../services/api';
import DirectoryBrowser from '../components/DirectoryBrowser';

const steps = ['Project Configuration', 'Initialize', 'Setup Complete'];

const ProjectSetup: React.FC = () => {
  const [activeStep, setActiveStep] = useState(0);
  const [projectData, setProjectData] = useState<InitializeProjectRequest>({
    project_path: '',
    project_name: '',
    github_repo: '',
    force_reinitialize: false,
  });
  const [initResult, setInitResult] = useState<any>(null);
  const [browserOpen, setBrowserOpen] = useState(false);

  const queryClient = useQueryClient();

  // Auto-populate project name from path
  const handlePathChange = (path: string) => {
    // Remove trailing slash if present
    const cleanPath = path.endsWith('/') ? path.slice(0, -1) : path;
    setProjectData({ 
      ...projectData, 
      project_path: cleanPath,
      // Auto-populate project name from folder name if name is empty
      project_name: projectData.project_name || cleanPath.split('/').filter(Boolean).pop() || ''
    });
  };

  // Handle folder selection from browser
  const handleFolderSelect = async () => {
    // Check if File System Access API is supported
    if ('showDirectoryPicker' in window) {
      try {
        // Use native File System Access API
        const dirHandle = await (window as any).showDirectoryPicker({
          startIn: 'desktop',
          mode: 'read'
        });
        
        // Get the folder name
        const folderName = dirHandle.name;
        
        // Unfortunately we still can't get the full path due to security
        // But we can at least get the folder name
        alert(`Selected folder: "${folderName}"\n\nNote: Due to browser security, the full path cannot be obtained. Please enter the full path manually or use the Browse button for server-side folder selection.`);
        
        setProjectData({
          ...projectData,
          project_name: folderName
        });
      } catch (err) {
        console.log('User cancelled or error:', err);
        // Fallback to custom browser
        setBrowserOpen(true);
      }
    } else {
      // Fallback to custom browser for older browsers
      setBrowserOpen(true);
    }
  };
  
  const handlePathSelected = (path: string) => {
    handlePathChange(path);
    setBrowserOpen(false);
  };

  // Handle server-side folder picker
  const handleServerFolderPick = async () => {
    try {
      const response = await fetch('http://localhost:3333/api/pick-folder');
      const data = await response.json();
      
      if (data.success && data.path) {
        handlePathChange(data.path);
      } else if (data.message) {
        alert(data.message);
      }
    } catch (error) {
      console.error('Error picking folder:', error);
      alert('Failed to open folder picker. Please enter path manually.');
    }
  };

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
    setProjectData({ project_path: '', project_name: '', github_repo: '', force_reinitialize: false });
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
              
              <Alert severity="info" sx={{ mb: 2 }}>
                <Typography variant="body2" sx={{ mb: 1 }}>
                  <strong>Path Examples:</strong>
                </Typography>
                <Typography variant="body2" component="div">
                  • macOS: <code>/Users/username/projects/my-app</code><br/>
                  • Linux: <code>/home/username/projects/my-app</code><br/>
                  • Windows: <code>C:\Users\username\projects\my-app</code>
                </Typography>
              </Alert>
              
              <TextField
                fullWidth
                label="Project Path"
                placeholder="/path/to/your/project"
                value={projectData.project_path}
                onChange={(e) => handlePathChange(e.target.value)}
                sx={{ mb: 2 }}
                helperText="Enter the absolute path to your project directory, or use the Browse button to select a folder."
                autoFocus
                InputProps={{
                  startAdornment: (
                    <InputAdornment position="start">
                      <FolderOpenIcon color="action" />
                    </InputAdornment>
                  ),
                  endAdornment: (
                    <InputAdornment position="end">
                      <Button
                        variant="outlined"
                        size="small"
                        onClick={handleServerFolderPick}
                        startIcon={<FolderOpenIcon />}
                        title="Open system folder picker"
                      >
                        Browse
                      </Button>
                    </InputAdornment>
                  ),
                }}
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
                sx={{ mb: 2 }}
                helperText="Link to your GitHub repository"
              />
              
              <FormControlLabel
                control={
                  <Checkbox
                    checked={projectData.force_reinitialize || false}
                    onChange={(e) => setProjectData({ ...projectData, force_reinitialize: e.target.checked })}
                  />
                }
                label="Force reinitialize (remove existing configuration)"
                sx={{ mb: 2 }}
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
      
      <DirectoryBrowser
        open={browserOpen}
        onClose={() => setBrowserOpen(false)}
        onSelectPath={handlePathSelected}
        initialPath={projectData.project_path}
      />
    </Box>
  );
};

export default ProjectSetup;