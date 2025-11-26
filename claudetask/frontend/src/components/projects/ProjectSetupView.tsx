import React, { useState } from 'react';
import {
  Box,
  Typography,
  TextField,
  Button,
  Alert,
  CircularProgress,
  Step,
  Stepper,
  StepLabel,
  Chip,
  InputAdornment,
  FormControlLabel,
  Checkbox,
  alpha,
  useTheme,
  Paper,
  Stack,
  Radio,
  RadioGroup,
  FormControl,
  FormLabel,
} from '@mui/material';
import {
  Folder as FolderIcon,
  CheckCircle as CheckIcon,
  FolderOpen as FolderOpenIcon,
  Settings as SettingsIcon,
  Info as InfoIcon,
} from '@mui/icons-material';
import { useMutation, useQueryClient } from 'react-query';
import { initializeProject, InitializeProjectRequest } from '../../services/api';
import DirectoryBrowser from '../DirectoryBrowser';

const steps = ['Project Configuration', 'Initialize', 'Setup Complete'];

const ProjectSetupView: React.FC = () => {
  const theme = useTheme();
  const [activeStep, setActiveStep] = useState(0);
  const [projectData, setProjectData] = useState<InitializeProjectRequest>({
    project_path: '',
    project_name: '',
    github_repo: '',
    force_reinitialize: false,
    project_mode: 'simple',
  });
  const [initResult, setInitResult] = useState<any>(null);
  const [browserOpen, setBrowserOpen] = useState(false);

  const queryClient = useQueryClient();

  const handlePathChange = (path: string) => {
    const cleanPath = path.endsWith('/') ? path.slice(0, -1) : path;
    setProjectData({
      ...projectData,
      project_path: cleanPath,
      project_name: projectData.project_name || cleanPath.split('/').filter(Boolean).pop() || ''
    });
  };

  const handleFolderSelect = async () => {
    if ('showDirectoryPicker' in window) {
      try {
        const dirHandle = await (window as any).showDirectoryPicker({
          startIn: 'desktop',
          mode: 'read'
        });

        const folderName = dirHandle.name;
        alert(`Selected folder: "${folderName}"\n\nNote: Due to browser security, the full path cannot be obtained. Please enter the full path manually or use the Browse button for server-side folder selection.`);

        setProjectData({
          ...projectData,
          project_name: folderName
        });
      } catch (err) {
        console.log('User cancelled or error:', err);
        setBrowserOpen(true);
      }
    } else {
      setBrowserOpen(true);
    }
  };

  const handlePathSelected = (path: string) => {
    handlePathChange(path);
    setBrowserOpen(false);
  };

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
          <Paper
            sx={{
              p: 4,
              borderRadius: 2,
              background: alpha(theme.palette.background.paper, 0.6),
              border: `1px solid ${alpha(theme.palette.divider, 0.1)}`,
            }}
          >
            <Stack spacing={3}>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                <Box
                  sx={{
                    p: 1.5,
                    borderRadius: 2,
                    background: `linear-gradient(135deg, ${alpha(theme.palette.primary.main, 0.2)}, ${alpha(theme.palette.primary.main, 0.1)})`,
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                  }}
                >
                  <SettingsIcon sx={{ color: theme.palette.primary.main, fontSize: 28 }} />
                </Box>
                <Box>
                  <Typography
                    variant="h5"
                    sx={{
                      fontWeight: 600,
                      color: theme.palette.text.primary,
                      mb: 0.5,
                    }}
                  >
                    Project Configuration
                  </Typography>
                  <Typography
                    variant="body2"
                    sx={{
                      color: alpha(theme.palette.text.secondary, 0.7),
                    }}
                  >
                    Configure your project to work with ClaudeTask and set up MCP integration
                  </Typography>
                </Box>
              </Box>

              <Alert
                severity="info"
                sx={{
                  backgroundColor: alpha(theme.palette.info.main, 0.1),
                  border: `1px solid ${alpha(theme.palette.info.main, 0.3)}`,
                  borderRadius: 2,
                  '& .MuiAlert-icon': { color: theme.palette.info.main },
                }}
              >
                <Typography variant="body2" sx={{ mb: 1, fontWeight: 600 }}>
                  Path Examples:
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
                sx={{
                  '& .MuiOutlinedInput-root': {
                    color: theme.palette.text.primary,
                    backgroundColor: alpha(theme.palette.background.default, 0.5),
                    borderRadius: 2,
                    '& fieldset': {
                      borderColor: alpha(theme.palette.divider, 0.1),
                    },
                    '&:hover fieldset': {
                      borderColor: alpha(theme.palette.primary.main, 0.3),
                    },
                    '&.Mui-focused fieldset': {
                      borderColor: theme.palette.primary.main,
                    },
                  },
                  '& .MuiInputLabel-root': {
                    color: alpha(theme.palette.text.secondary, 0.7),
                    '&.Mui-focused': { color: theme.palette.primary.main },
                  },
                  '& .MuiFormHelperText-root': {
                    color: alpha(theme.palette.text.secondary, 0.6),
                  },
                }}
                helperText="Enter the absolute path to your project directory, or use the Browse button"
                autoFocus
                InputProps={{
                  startAdornment: (
                    <InputAdornment position="start">
                      <FolderOpenIcon sx={{ color: alpha(theme.palette.text.secondary, 0.5) }} />
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
                        sx={{
                          color: theme.palette.primary.main,
                          border: `1px solid ${alpha(theme.palette.primary.main, 0.3)}`,
                          textTransform: 'none',
                          fontWeight: 500,
                          '&:hover': {
                            backgroundColor: alpha(theme.palette.primary.main, 0.1),
                            borderColor: theme.palette.primary.main,
                          },
                        }}
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
                sx={{
                  '& .MuiOutlinedInput-root': {
                    color: theme.palette.text.primary,
                    backgroundColor: alpha(theme.palette.background.default, 0.5),
                    borderRadius: 2,
                    '& fieldset': {
                      borderColor: alpha(theme.palette.divider, 0.1),
                    },
                    '&:hover fieldset': {
                      borderColor: alpha(theme.palette.primary.main, 0.3),
                    },
                    '&.Mui-focused fieldset': {
                      borderColor: theme.palette.primary.main,
                    },
                  },
                  '& .MuiInputLabel-root': {
                    color: alpha(theme.palette.text.secondary, 0.7),
                    '&.Mui-focused': { color: theme.palette.primary.main },
                  },
                  '& .MuiFormHelperText-root': {
                    color: alpha(theme.palette.text.secondary, 0.6),
                  },
                }}
                helperText="Display name for your project"
              />

              <TextField
                fullWidth
                label="GitHub Repository (Optional)"
                placeholder="https://github.com/user/repo"
                value={projectData.github_repo}
                onChange={(e) => setProjectData({ ...projectData, github_repo: e.target.value })}
                sx={{
                  '& .MuiOutlinedInput-root': {
                    color: theme.palette.text.primary,
                    backgroundColor: alpha(theme.palette.background.default, 0.5),
                    borderRadius: 2,
                    '& fieldset': {
                      borderColor: alpha(theme.palette.divider, 0.1),
                    },
                    '&:hover fieldset': {
                      borderColor: alpha(theme.palette.primary.main, 0.3),
                    },
                    '&.Mui-focused fieldset': {
                      borderColor: theme.palette.primary.main,
                    },
                  },
                  '& .MuiInputLabel-root': {
                    color: alpha(theme.palette.text.secondary, 0.7),
                    '&.Mui-focused': { color: theme.palette.primary.main },
                  },
                  '& .MuiFormHelperText-root': {
                    color: alpha(theme.palette.text.secondary, 0.6),
                  },
                }}
                helperText="Link to your GitHub repository"
              />

              <FormControl component="fieldset" sx={{ mb: 3 }}>
                <FormLabel
                  component="legend"
                  sx={{
                    color: theme.palette.text.primary,
                    fontWeight: 600,
                    mb: 2,
                    '&.Mui-focused': { color: theme.palette.primary.main }
                  }}
                >
                  Project Mode
                </FormLabel>
                <RadioGroup
                  value={projectData.project_mode || 'simple'}
                  onChange={(e) => setProjectData({ ...projectData, project_mode: e.target.value as 'simple' | 'development' })}
                >
                  <FormControlLabel
                    value="simple"
                    control={
                      <Radio
                        sx={{
                          color: alpha(theme.palette.text.secondary, 0.7),
                          '&.Mui-checked': {
                            color: theme.palette.primary.main,
                          },
                        }}
                      />
                    }
                    label={
                      <Box>
                        <Typography variant="body1" sx={{ color: theme.palette.text.primary, fontWeight: 500 }}>
                          Simple Mode
                        </Typography>
                        <Typography variant="body2" sx={{ color: alpha(theme.palette.text.secondary, 0.7) }}>
                          3 columns: Backlog → In Progress → Done. Direct work, no branches or PRs.
                        </Typography>
                      </Box>
                    }
                  />
                  <FormControlLabel
                    value="development"
                    control={
                      <Radio
                        sx={{
                          color: alpha(theme.palette.text.secondary, 0.7),
                          '&.Mui-checked': {
                            color: theme.palette.primary.main,
                          },
                        }}
                      />
                    }
                    label={
                      <Box>
                        <Typography variant="body1" sx={{ color: theme.palette.text.primary, fontWeight: 500 }}>
                          Development Mode
                        </Typography>
                        <Typography variant="body2" sx={{ color: alpha(theme.palette.text.secondary, 0.7) }}>
                          Full workflow with Git integration, worktrees, testing, code review, and PRs.
                        </Typography>
                      </Box>
                    }
                  />
                </RadioGroup>
              </FormControl>

              <FormControlLabel
                control={
                  <Checkbox
                    checked={projectData.force_reinitialize || false}
                    onChange={(e) => setProjectData({ ...projectData, force_reinitialize: e.target.checked })}
                    sx={{
                      color: alpha(theme.palette.text.secondary, 0.7),
                      '&.Mui-checked': {
                        color: theme.palette.primary.main,
                      },
                    }}
                  />
                }
                label="Force reinitialize (remove existing configuration)"
                sx={{ color: theme.palette.text.primary }}
              />

              <Paper
                sx={{
                  p: 3,
                  borderRadius: 2,
                  background: `linear-gradient(145deg, ${alpha(theme.palette.info.main, 0.05)}, ${alpha(theme.palette.info.main, 0.02)})`,
                  border: `1px solid ${alpha(theme.palette.info.main, 0.15)}`,
                }}
              >
                <Stack direction="row" spacing={2} alignItems="flex-start">
                  <InfoIcon sx={{ color: theme.palette.info.main, fontSize: 24, mt: 0.5 }} />
                  <Box sx={{ flex: 1 }}>
                    <Typography variant="body2" sx={{ fontWeight: 600, color: theme.palette.text.primary, mb: 1.5 }}>
                      What happens during initialization:
                    </Typography>
                    <Stack spacing={1}>
                      {[
                        { icon: <FolderIcon fontSize="small" />, text: 'Creates .claudetask/ directory in your project' },
                        { icon: <CheckIcon fontSize="small" />, text: 'Generates CLAUDE.md configuration' },
                        { icon: <CheckIcon fontSize="small" />, text: 'Sets up default agents' },
                        { icon: <CheckIcon fontSize="small" />, text: 'Creates .mcp.json for Claude Code integration' },
                      ].map((item, index) => (
                        <Box key={index} sx={{ display: 'flex', alignItems: 'center', gap: 1.5 }}>
                          <Box sx={{ color: theme.palette.info.main }}>{item.icon}</Box>
                          <Typography variant="body2" sx={{ color: alpha(theme.palette.text.secondary, 0.8) }}>
                            {item.text}
                          </Typography>
                        </Box>
                      ))}
                    </Stack>
                  </Box>
                </Stack>
              </Paper>

              <Button
                variant="contained"
                onClick={handleNext}
                disabled={!projectData.project_path || !projectData.project_name}
                fullWidth
                sx={{
                  background: `linear-gradient(135deg, ${theme.palette.primary.main}, ${theme.palette.primary.dark})`,
                  color: '#fff',
                  fontWeight: 600,
                  textTransform: 'none',
                  py: 1.5,
                  borderRadius: 2,
                  boxShadow: `0 4px 12px ${alpha(theme.palette.primary.main, 0.3)}`,
                  transition: 'all 0.3s ease',
                  '&:hover': {
                    background: `linear-gradient(135deg, ${theme.palette.primary.dark}, ${theme.palette.primary.main})`,
                    transform: 'translateY(-2px)',
                    boxShadow: `0 6px 20px ${alpha(theme.palette.primary.main, 0.4)}`,
                  },
                  '&:disabled': {
                    background: alpha(theme.palette.action.disabledBackground, 0.3),
                    color: alpha(theme.palette.text.disabled, 0.5),
                    transform: 'none',
                  },
                }}
              >
                Initialize Project
              </Button>
            </Stack>
          </Paper>
        );

      case 1:
        return (
          <Paper
            sx={{
              p: 6,
              borderRadius: 2,
              background: alpha(theme.palette.background.paper, 0.6),
              border: `1px solid ${alpha(theme.palette.divider, 0.1)}`,
            }}
          >
            <Box display="flex" flexDirection="column" alignItems="center">
              <CircularProgress size={60} sx={{ mb: 3, color: theme.palette.primary.main }} />
              <Typography
                variant="h5"
                gutterBottom
                sx={{
                  color: theme.palette.text.primary,
                  fontWeight: 600,
                  mb: 1,
                }}
              >
                Initializing Project...
              </Typography>
              <Typography
                variant="body1"
                sx={{
                  color: alpha(theme.palette.text.secondary, 0.8),
                  textAlign: 'center',
                }}
              >
                Setting up ClaudeTask configuration for {projectData.project_name}
              </Typography>
            </Box>

            {initializeMutation.error && (
              <Alert
                severity="error"
                sx={{
                  mt: 3,
                  backgroundColor: alpha(theme.palette.error.main, 0.1),
                  border: `1px solid ${alpha(theme.palette.error.main, 0.3)}`,
                  borderRadius: 2,
                  '& .MuiAlert-icon': { color: theme.palette.error.main },
                }}
              >
                Initialization failed: {(initializeMutation.error as any)?.response?.data?.detail || 'Unknown error'}
              </Alert>
            )}
          </Paper>
        );

      case 2:
        return (
          <Paper
            sx={{
              p: 4,
              borderRadius: 2,
              background: alpha(theme.palette.background.paper, 0.6),
              border: `1px solid ${alpha(theme.palette.divider, 0.1)}`,
            }}
          >
            <Stack spacing={4}>
              <Box display="flex" flexDirection="column" alignItems="center">
                <Box
                  sx={{
                    p: 2,
                    borderRadius: '50%',
                    background: `linear-gradient(135deg, ${alpha(theme.palette.success.main, 0.2)}, ${alpha(theme.palette.success.main, 0.1)})`,
                    mb: 2,
                  }}
                >
                  <CheckIcon sx={{ fontSize: 48, color: theme.palette.success.main }} />
                </Box>
                <Typography
                  variant="h5"
                  gutterBottom
                  sx={{
                    color: theme.palette.success.main,
                    fontWeight: 600,
                  }}
                >
                  Project Initialized Successfully!
                </Typography>
              </Box>

              {initResult && (
                <Stack spacing={3}>
                  <Box>
                    <Typography variant="h6" gutterBottom sx={{ color: theme.palette.text.primary, fontWeight: 600, mb: 2 }}>
                      Configuration Details
                    </Typography>
                    <Stack spacing={2}>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5 }}>
                        <Typography variant="body2" sx={{ color: alpha(theme.palette.text.secondary, 0.8) }}>
                          Project ID:
                        </Typography>
                        <Chip
                          label={initResult.project_id}
                          size="small"
                          sx={{
                            background: `linear-gradient(135deg, ${alpha(theme.palette.primary.main, 0.2)}, ${alpha(theme.palette.primary.main, 0.1)})`,
                            color: theme.palette.primary.main,
                            border: `1px solid ${alpha(theme.palette.primary.main, 0.3)}`,
                            fontWeight: 600,
                          }}
                        />
                      </Box>

                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5 }}>
                        <Typography variant="body2" sx={{ color: alpha(theme.palette.text.secondary, 0.8) }}>
                          MCP Configured:
                        </Typography>
                        <Chip
                          label={initResult.mcp_configured ? "Yes" : "No"}
                          size="small"
                          sx={{
                            background: initResult.mcp_configured
                              ? `linear-gradient(135deg, ${alpha(theme.palette.success.main, 0.2)}, ${alpha(theme.palette.success.main, 0.1)})`
                              : `linear-gradient(135deg, ${alpha(theme.palette.error.main, 0.2)}, ${alpha(theme.palette.error.main, 0.1)})`,
                            color: initResult.mcp_configured ? theme.palette.success.main : theme.palette.error.main,
                            border: `1px solid ${alpha(initResult.mcp_configured ? theme.palette.success.main : theme.palette.error.main, 0.3)}`,
                            fontWeight: 600,
                          }}
                        />
                      </Box>
                    </Stack>
                  </Box>

                  <Box>
                    <Typography variant="h6" gutterBottom sx={{ color: theme.palette.text.primary, fontWeight: 600, mb: 2 }}>
                      Files Created
                    </Typography>
                    <Stack spacing={1}>
                      {initResult.files_created.map((file: string, index: number) => (
                        <Box key={index} sx={{ display: 'flex', alignItems: 'center', gap: 1.5 }}>
                          <CheckIcon fontSize="small" sx={{ color: theme.palette.success.main }} />
                          <Typography variant="body2" sx={{ color: alpha(theme.palette.text.secondary, 0.8), fontFamily: 'monospace' }}>
                            {file}
                          </Typography>
                        </Box>
                      ))}
                    </Stack>
                  </Box>

                  {initResult.claude_restart_required && (
                    <Alert
                      severity="warning"
                      sx={{
                        backgroundColor: alpha(theme.palette.warning.main, 0.1),
                        border: `1px solid ${alpha(theme.palette.warning.main, 0.3)}`,
                        borderRadius: 2,
                        '& .MuiAlert-icon': { color: theme.palette.warning.main },
                      }}
                    >
                      <Typography variant="body2">
                        <strong>Important:</strong> You need to restart Claude Code for the MCP configuration to take effect.
                        The .mcp.json file has been created in your project root.
                      </Typography>
                    </Alert>
                  )}

                  <Alert
                    severity="success"
                    sx={{
                      backgroundColor: alpha(theme.palette.success.main, 0.1),
                      border: `1px solid ${alpha(theme.palette.success.main, 0.3)}`,
                      borderRadius: 2,
                      '& .MuiAlert-icon': { color: theme.palette.success.main },
                    }}
                  >
                    <Typography variant="body2">
                      Your project is now ready for ClaudeTask! You can start creating tasks and let Claude handle the implementation.
                    </Typography>
                  </Alert>
                </Stack>
              )}

              <Button
                variant="outlined"
                onClick={handleReset}
                fullWidth
                sx={{
                  color: theme.palette.primary.main,
                  border: `1px solid ${alpha(theme.palette.primary.main, 0.3)}`,
                  textTransform: 'none',
                  fontWeight: 600,
                  py: 1.5,
                  borderRadius: 2,
                  '&:hover': {
                    backgroundColor: alpha(theme.palette.primary.main, 0.1),
                    borderColor: theme.palette.primary.main,
                  },
                }}
              >
                Initialize Another Project
              </Button>
            </Stack>
          </Paper>
        );

      default:
        return null;
    }
  };

  return (
    <Box>
      {/* Stepper */}
      <Paper
        sx={{
          p: 4,
          mb: 4,
          borderRadius: 2,
          background: alpha(theme.palette.background.paper, 0.6),
          border: `1px solid ${alpha(theme.palette.divider, 0.1)}`,
        }}
      >
        <Stepper
          activeStep={activeStep}
          sx={{
            '& .MuiStepLabel-root .Mui-completed': {
              color: theme.palette.success.main,
            },
            '& .MuiStepLabel-label.Mui-completed.MuiStepLabel-alternativeLabel': {
              color: alpha(theme.palette.text.secondary, 0.7),
            },
            '& .MuiStepLabel-root .Mui-active': {
              color: theme.palette.primary.main,
            },
            '& .MuiStepLabel-label.Mui-active.MuiStepLabel-alternativeLabel': {
              color: theme.palette.text.primary,
              fontWeight: 600,
            },
            '& .MuiStepLabel-root .Mui-active .MuiStepIcon-text': {
              fill: '#ffffff',
            },
            '& .MuiStepLabel-label': {
              color: alpha(theme.palette.text.secondary, 0.5),
            },
            '& .MuiStepConnector-line': {
              borderColor: alpha(theme.palette.divider, 0.2),
            },
          }}
        >
          {steps.map((label) => (
            <Step key={label}>
              <StepLabel>{label}</StepLabel>
            </Step>
          ))}
        </Stepper>
      </Paper>

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

export default ProjectSetupView;
