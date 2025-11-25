import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Button,
  Grid,
  Switch,
  FormControlLabel,
  TextField,
  Alert,
  Container,
  alpha,
  useTheme,
  Divider,
  Stack,
  Paper,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  IconButton,
  Tooltip,
  CircularProgress,
} from '@mui/material';
import SettingsIcon from '@mui/icons-material/Settings';
import PaletteIcon from '@mui/icons-material/Palette';
import NotificationsIcon from '@mui/icons-material/Notifications';
import FolderIcon from '@mui/icons-material/Folder';
import TuneIcon from '@mui/icons-material/Tune';
import SaveIcon from '@mui/icons-material/Save';
import InfoIcon from '@mui/icons-material/Info';
import LightModeIcon from '@mui/icons-material/LightMode';
import DarkModeIcon from '@mui/icons-material/DarkMode';
import AutoModeIcon from '@mui/icons-material/AutoMode';
import RateReviewIcon from '@mui/icons-material/RateReview';
import { useProject } from '../context/ProjectContext';
import { getProjectSettings, updateProjectSettings, ProjectSettings as ProjectSettingsType } from '../services/api';

const Settings: React.FC = () => {
  const theme = useTheme();
  const { selectedProject } = useProject();

  // Settings state
  const [generalSettings, setGeneralSettings] = useState({
    projectName: '',
    autoSave: true,
    confirmActions: true,
  });

  const [appearanceSettings, setAppearanceSettings] = useState({
    theme: 'system',
    density: 'comfortable',
    animations: true,
  });

  const [notificationSettings, setNotificationSettings] = useState({
    taskUpdates: true,
    agentStatus: true,
    errors: true,
    soundEnabled: false,
  });

  const [projectSettings, setProjectSettings] = useState({
    defaultPriority: 'Medium',
    autoAssign: true,
    branchNaming: 'task-{id}-{title}',
  });

  const [advancedSettings, setAdvancedSettings] = useState({
    debugMode: false,
    apiTimeout: 30,
    maxRetries: 3,
  });

  // Backend Project Settings state
  const [backendSettings, setBackendSettings] = useState<ProjectSettingsType | null>(null);
  const [loadingSettings, setLoadingSettings] = useState(false);

  const [saveSuccess, setSaveSuccess] = useState(false);
  const [saveError, setSaveError] = useState<string | null>(null);

  // Load settings from localStorage
  useEffect(() => {
    const savedSettings = localStorage.getItem('claudetask-settings');
    if (savedSettings) {
      try {
        const parsed = JSON.parse(savedSettings);
        setGeneralSettings(parsed.general || generalSettings);
        setAppearanceSettings(parsed.appearance || appearanceSettings);
        setNotificationSettings(parsed.notifications || notificationSettings);
        setProjectSettings(parsed.project || projectSettings);
        setAdvancedSettings(parsed.advanced || advancedSettings);
      } catch (e) {
        console.error('Failed to load settings:', e);
      }
    }
  }, []);

  // Load backend project settings when project changes
  useEffect(() => {
    const loadBackendSettings = async () => {
      if (!selectedProject) {
        setBackendSettings(null);
        return;
      }

      setLoadingSettings(true);
      try {
        const settings = await getProjectSettings(selectedProject.id);
        setBackendSettings(settings);
      } catch (error) {
        console.error('Failed to load project settings:', error);
        setSaveError('Failed to load project settings from backend');
      } finally {
        setLoadingSettings(false);
      }
    };

    loadBackendSettings();
  }, [selectedProject]);

  const handleSaveSettings = async () => {
    try {
      // Save UI settings to localStorage
      const allSettings = {
        general: generalSettings,
        appearance: appearanceSettings,
        notifications: notificationSettings,
        project: projectSettings,
        advanced: advancedSettings,
      };
      localStorage.setItem('claudetask-settings', JSON.stringify(allSettings));

      // Save backend project settings if available
      if (selectedProject && backendSettings) {
        await updateProjectSettings(selectedProject.id, backendSettings);
      }

      setSaveSuccess(true);
      setSaveError(null);
      setTimeout(() => setSaveSuccess(false), 3000);
    } catch (e) {
      setSaveError('Failed to save settings. Please try again.');
      console.error('Failed to save settings:', e);
    }
  };

  const SettingRow: React.FC<{
    label: string;
    description?: string;
    control: React.ReactNode;
  }> = ({ label, description, control }) => (
    <Box
      sx={{
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        py: 2,
        '&:not(:last-child)': {
          borderBottom: `1px solid ${alpha(theme.palette.divider, 0.1)}`,
        },
      }}
    >
      <Box flex={1}>
        <Typography variant="body1" fontWeight={500} gutterBottom={!!description}>
          {label}
        </Typography>
        {description && (
          <Typography variant="body2" color="text.secondary" sx={{ fontSize: '0.875rem' }}>
            {description}
          </Typography>
        )}
      </Box>
      <Box>{control}</Box>
    </Box>
  );

  const SettingSection: React.FC<{
    title: string;
    description: string;
    icon: React.ReactNode;
    children: React.ReactNode;
  }> = ({ title, description, icon, children }) => (
    <Card
      sx={{
        position: 'relative',
        overflow: 'visible',
        background: theme.palette.mode === 'dark'
          ? `linear-gradient(145deg, ${alpha(theme.palette.background.paper, 0.9)}, ${alpha(theme.palette.background.paper, 0.95)})`
          : theme.palette.background.paper,
        border: `1px solid ${alpha(theme.palette.primary.main, 0.1)}`,
        transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
        '&:hover': {
          border: `1px solid ${alpha(theme.palette.primary.main, 0.3)}`,
          boxShadow: theme.palette.mode === 'dark'
            ? `0 8px 16px -4px ${alpha(theme.palette.primary.main, 0.2)}`
            : `0 8px 16px -4px ${alpha(theme.palette.primary.main, 0.1)}`,
        },
      }}
    >
      {/* Gradient top border */}
      <Box
        sx={{
          position: 'absolute',
          top: 0,
          left: 0,
          right: 0,
          height: 4,
          background: `linear-gradient(90deg, ${theme.palette.primary.main}, ${theme.palette.primary.light})`,
          borderTopLeftRadius: 12,
          borderTopRightRadius: 12,
        }}
      />

      <CardContent sx={{ pt: 3 }}>
        {/* Section Header */}
        <Box display="flex" alignItems="start" gap={2} mb={3}>
          <Box
            sx={{
              width: 48,
              height: 48,
              borderRadius: 2,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              background: `linear-gradient(135deg, ${alpha(theme.palette.primary.main, 0.2)}, ${alpha(theme.palette.primary.light, 0.1)})`,
              border: `1px solid ${alpha(theme.palette.primary.main, 0.2)}`,
            }}
          >
            {icon}
          </Box>
          <Box>
            <Typography
              variant="h6"
              sx={{
                fontWeight: 600,
                mb: 0.5,
              }}
            >
              {title}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              {description}
            </Typography>
          </Box>
        </Box>

        <Divider sx={{ mb: 2 }} />

        {/* Settings Content */}
        {children}
      </CardContent>
    </Card>
  );

  return (
    <Box sx={{ minHeight: '100vh', pb: 4 }}>
      <Container maxWidth="lg">
        {/* Hero Header */}
        <Box py={4}>
          <Stack direction="row" justifyContent="space-between" alignItems="center" mb={3}>
            <Box>
              <Typography
                variant="h3"
                component="h1"
                sx={{
                  fontWeight: 700,
                  background: `linear-gradient(135deg, ${theme.palette.primary.main}, ${theme.palette.primary.light})`,
                  WebkitBackgroundClip: 'text',
                  WebkitTextFillColor: 'transparent',
                  mb: 1,
                }}
              >
                Settings
              </Typography>
              <Typography variant="body1" color="text.secondary">
                Configure your ClaudeTask experience
              </Typography>
            </Box>
            <Button
              variant="contained"
              size="large"
              startIcon={<SaveIcon />}
              onClick={handleSaveSettings}
              sx={{
                borderRadius: 2,
                px: 3,
                py: 1.5,
                background: `linear-gradient(135deg, ${theme.palette.primary.main}, ${theme.palette.primary.dark})`,
                boxShadow: `0 8px 16px ${alpha(theme.palette.primary.main, 0.3)}`,
                '&:hover': {
                  background: `linear-gradient(135deg, ${theme.palette.primary.dark}, ${theme.palette.primary.main})`,
                  transform: 'translateY(-2px)',
                  boxShadow: `0 12px 20px ${alpha(theme.palette.primary.main, 0.4)}`,
                },
              }}
            >
              Save Changes
            </Button>
          </Stack>

          {/* Status Messages */}
          {saveSuccess && (
            <Alert severity="success" sx={{ mb: 3, borderRadius: 2 }} onClose={() => setSaveSuccess(false)}>
              Settings saved successfully!
            </Alert>
          )}
          {saveError && (
            <Alert severity="error" sx={{ mb: 3, borderRadius: 2 }} onClose={() => setSaveError(null)}>
              {saveError}
            </Alert>
          )}

          {/* Project Info Card */}
          {selectedProject && (
            <Paper
              sx={{
                p: 2.5,
                mb: 3,
                borderRadius: 2,
                background: `linear-gradient(145deg, ${alpha(theme.palette.info.main, 0.05)}, ${alpha(theme.palette.info.main, 0.02)})`,
                border: `1px solid ${alpha(theme.palette.info.main, 0.15)}`,
              }}
            >
              <Stack direction="row" spacing={2} alignItems="center">
                <FolderIcon sx={{ color: theme.palette.info.main, fontSize: 32 }} />
                <Box>
                  <Typography variant="body2" color="text.secondary">
                    Current Project
                  </Typography>
                  <Typography variant="h6" sx={{ fontWeight: 600 }}>
                    {selectedProject.name}
                  </Typography>
                  <Typography variant="caption" color="text.secondary">
                    {selectedProject.path}
                  </Typography>
                </Box>
              </Stack>
            </Paper>
          )}
        </Box>

        {/* Settings Sections */}
        <Stack spacing={3}>
          {/* General Settings */}
          <SettingSection
            title="General"
            description="Basic application settings and preferences"
            icon={<SettingsIcon sx={{ color: theme.palette.primary.main, fontSize: 28 }} />}
          >
            <SettingRow
              label="Project Name"
              description="Display name for this project"
              control={
                <TextField
                  size="small"
                  value={generalSettings.projectName}
                  onChange={(e) => setGeneralSettings({ ...generalSettings, projectName: e.target.value })}
                  placeholder={selectedProject?.name || 'Enter project name'}
                  sx={{ width: 250 }}
                />
              }
            />
            <SettingRow
              label="Auto-save"
              description="Automatically save changes as you work"
              control={
                <Switch
                  checked={generalSettings.autoSave}
                  onChange={(e) => setGeneralSettings({ ...generalSettings, autoSave: e.target.checked })}
                  color="primary"
                />
              }
            />
            <SettingRow
              label="Confirm Actions"
              description="Show confirmation dialogs for important actions"
              control={
                <Switch
                  checked={generalSettings.confirmActions}
                  onChange={(e) => setGeneralSettings({ ...generalSettings, confirmActions: e.target.checked })}
                  color="primary"
                />
              }
            />
          </SettingSection>

          {/* Appearance Settings */}
          <SettingSection
            title="Appearance"
            description="Customize the look and feel of the interface"
            icon={<PaletteIcon sx={{ color: theme.palette.primary.main, fontSize: 28 }} />}
          >
            <SettingRow
              label="Theme"
              description="Choose your preferred color scheme"
              control={
                <Stack direction="row" spacing={1}>
                  <Tooltip title="Light Mode">
                    <IconButton
                      onClick={() => setAppearanceSettings({ ...appearanceSettings, theme: 'light' })}
                      sx={{
                        border: appearanceSettings.theme === 'light' ? `2px solid ${theme.palette.primary.main}` : `1px solid ${alpha(theme.palette.divider, 0.2)}`,
                        background: appearanceSettings.theme === 'light' ? alpha(theme.palette.primary.main, 0.1) : 'transparent',
                      }}
                    >
                      <LightModeIcon />
                    </IconButton>
                  </Tooltip>
                  <Tooltip title="Dark Mode">
                    <IconButton
                      onClick={() => setAppearanceSettings({ ...appearanceSettings, theme: 'dark' })}
                      sx={{
                        border: appearanceSettings.theme === 'dark' ? `2px solid ${theme.palette.primary.main}` : `1px solid ${alpha(theme.palette.divider, 0.2)}`,
                        background: appearanceSettings.theme === 'dark' ? alpha(theme.palette.primary.main, 0.1) : 'transparent',
                      }}
                    >
                      <DarkModeIcon />
                    </IconButton>
                  </Tooltip>
                  <Tooltip title="System Default">
                    <IconButton
                      onClick={() => setAppearanceSettings({ ...appearanceSettings, theme: 'system' })}
                      sx={{
                        border: appearanceSettings.theme === 'system' ? `2px solid ${theme.palette.primary.main}` : `1px solid ${alpha(theme.palette.divider, 0.2)}`,
                        background: appearanceSettings.theme === 'system' ? alpha(theme.palette.primary.main, 0.1) : 'transparent',
                      }}
                    >
                      <AutoModeIcon />
                    </IconButton>
                  </Tooltip>
                </Stack>
              }
            />
            <SettingRow
              label="Density"
              description="Adjust spacing and component sizes"
              control={
                <FormControl size="small" sx={{ width: 150 }}>
                  <Select
                    value={appearanceSettings.density}
                    onChange={(e) => setAppearanceSettings({ ...appearanceSettings, density: e.target.value })}
                  >
                    <MenuItem value="compact">Compact</MenuItem>
                    <MenuItem value="comfortable">Comfortable</MenuItem>
                    <MenuItem value="spacious">Spacious</MenuItem>
                  </Select>
                </FormControl>
              }
            />
            <SettingRow
              label="Animations"
              description="Enable smooth transitions and animations"
              control={
                <Switch
                  checked={appearanceSettings.animations}
                  onChange={(e) => setAppearanceSettings({ ...appearanceSettings, animations: e.target.checked })}
                  color="primary"
                />
              }
            />
          </SettingSection>

          {/* Notification Settings */}
          <SettingSection
            title="Notifications"
            description="Manage how and when you receive notifications"
            icon={<NotificationsIcon sx={{ color: theme.palette.primary.main, fontSize: 28 }} />}
          >
            <SettingRow
              label="Task Updates"
              description="Notify when tasks change status or are updated"
              control={
                <Switch
                  checked={notificationSettings.taskUpdates}
                  onChange={(e) => setNotificationSettings({ ...notificationSettings, taskUpdates: e.target.checked })}
                  color="primary"
                />
              }
            />
            <SettingRow
              label="Agent Status"
              description="Notify about agent activities and completions"
              control={
                <Switch
                  checked={notificationSettings.agentStatus}
                  onChange={(e) => setNotificationSettings({ ...notificationSettings, agentStatus: e.target.checked })}
                  color="primary"
                />
              }
            />
            <SettingRow
              label="Error Alerts"
              description="Show alerts when errors occur"
              control={
                <Switch
                  checked={notificationSettings.errors}
                  onChange={(e) => setNotificationSettings({ ...notificationSettings, errors: e.target.checked })}
                  color="primary"
                />
              }
            />
            <SettingRow
              label="Sound Effects"
              description="Play sounds for notifications"
              control={
                <Switch
                  checked={notificationSettings.soundEnabled}
                  onChange={(e) => setNotificationSettings({ ...notificationSettings, soundEnabled: e.target.checked })}
                  color="primary"
                />
              }
            />
          </SettingSection>

          {/* Project Settings */}
          <SettingSection
            title="Project Settings"
            description="Configure project-specific behavior and defaults"
            icon={<FolderIcon sx={{ color: theme.palette.primary.main, fontSize: 28 }} />}
          >
            {loadingSettings ? (
              <Box display="flex" justifyContent="center" py={4}>
                <CircularProgress />
              </Box>
            ) : backendSettings ? (
              <>
                <SettingRow
                  label="Git Worktrees"
                  description="Use isolated Git worktrees for each task (requires Development mode)"
                  control={
                    <Switch
                      checked={backendSettings.worktree_enabled}
                      onChange={(e) => setBackendSettings({ ...backendSettings, worktree_enabled: e.target.checked })}
                      color="primary"
                      disabled={selectedProject?.project_mode === 'simple'}
                    />
                  }
                />
                <SettingRow
                  label="Test Command"
                  description="Command to run project tests"
                  control={
                    <TextField
                      size="small"
                      value={backendSettings.test_command || ''}
                      onChange={(e) => setBackendSettings({ ...backendSettings, test_command: e.target.value })}
                      placeholder="npm test"
                      sx={{ width: 250 }}
                    />
                  }
                />
                <SettingRow
                  label="Build Command"
                  description="Command to build the project"
                  control={
                    <TextField
                      size="small"
                      value={backendSettings.build_command || ''}
                      onChange={(e) => setBackendSettings({ ...backendSettings, build_command: e.target.value })}
                      placeholder="npm run build"
                      sx={{ width: 250 }}
                    />
                  }
                />
                <SettingRow
                  label="Lint Command"
                  description="Command to run code linting"
                  control={
                    <TextField
                      size="small"
                      value={backendSettings.lint_command || ''}
                      onChange={(e) => setBackendSettings({ ...backendSettings, lint_command: e.target.value })}
                      placeholder="npm run lint"
                      sx={{ width: 250 }}
                    />
                  }
                />

                {/* Testing Configuration Section */}
                <Divider sx={{ my: 2 }} />
                <Typography variant="subtitle2" color="text.secondary" sx={{ mb: 2 }}>
                  Testing Configuration (AUTO Mode)
                </Typography>

                <SettingRow
                  label="Test Directory"
                  description="Main directory for project tests"
                  control={
                    <TextField
                      size="small"
                      value={backendSettings.test_directory || 'tests'}
                      onChange={(e) => setBackendSettings({ ...backendSettings, test_directory: e.target.value })}
                      placeholder="tests"
                      sx={{ width: 250 }}
                    />
                  }
                />
                <SettingRow
                  label="Test Framework"
                  description="Testing framework used in project"
                  control={
                    <FormControl size="small" sx={{ width: 150 }}>
                      <Select
                        value={backendSettings.test_framework || 'pytest'}
                        onChange={(e) => setBackendSettings({ ...backendSettings, test_framework: e.target.value as any })}
                      >
                        <MenuItem value="pytest">pytest</MenuItem>
                        <MenuItem value="jest">Jest</MenuItem>
                        <MenuItem value="vitest">Vitest</MenuItem>
                        <MenuItem value="mocha">Mocha</MenuItem>
                        <MenuItem value="unittest">unittest</MenuItem>
                        <MenuItem value="custom">Custom</MenuItem>
                      </Select>
                    </FormControl>
                  }
                />
                <SettingRow
                  label="Test Staging Directory"
                  description="Directory for new task tests before merge"
                  control={
                    <TextField
                      size="small"
                      value={backendSettings.test_staging_dir || 'tests/staging'}
                      onChange={(e) => setBackendSettings({ ...backendSettings, test_staging_dir: e.target.value })}
                      placeholder="tests/staging"
                      sx={{ width: 250 }}
                    />
                  }
                />
                <SettingRow
                  label="Auto-Merge Tests"
                  description="Automatically merge new tests into main test suite after PR approval"
                  control={
                    <Switch
                      checked={backendSettings.auto_merge_tests ?? true}
                      onChange={(e) => setBackendSettings({ ...backendSettings, auto_merge_tests: e.target.checked })}
                      color="primary"
                    />
                  }
                />
              </>
            ) : (
              <Alert severity="info">
                Please select a project to configure project settings
              </Alert>
            )}

            <Divider sx={{ my: 2 }} />

            {/* UI-only project settings */}
            <Typography variant="subtitle2" color="text.secondary" sx={{ mb: 2, mt: 2 }}>
              UI Preferences
            </Typography>
            <SettingRow
              label="Default Priority"
              description="Default priority for new tasks"
              control={
                <FormControl size="small" sx={{ width: 150 }}>
                  <Select
                    value={projectSettings.defaultPriority}
                    onChange={(e) => setProjectSettings({ ...projectSettings, defaultPriority: e.target.value })}
                  >
                    <MenuItem value="Low">Low</MenuItem>
                    <MenuItem value="Medium">Medium</MenuItem>
                    <MenuItem value="High">High</MenuItem>
                  </Select>
                </FormControl>
              }
            />
            <SettingRow
              label="Auto-assign Tasks"
              description="Automatically assign tasks to appropriate agents"
              control={
                <Switch
                  checked={projectSettings.autoAssign}
                  onChange={(e) => setProjectSettings({ ...projectSettings, autoAssign: e.target.checked })}
                  color="primary"
                />
              }
            />
            <SettingRow
              label="Branch Naming"
              description="Pattern for Git branch names (use {id} and {title})"
              control={
                <TextField
                  size="small"
                  value={projectSettings.branchNaming}
                  onChange={(e) => setProjectSettings({ ...projectSettings, branchNaming: e.target.value })}
                  placeholder="task-{id}-{title}"
                  sx={{ width: 250 }}
                />
              }
            />
          </SettingSection>

          {/* Advanced Settings */}
          <SettingSection
            title="Advanced"
            description="Advanced settings for power users"
            icon={<TuneIcon sx={{ color: theme.palette.primary.main, fontSize: 28 }} />}
          >
            <Alert
              severity="warning"
              icon={<InfoIcon />}
              sx={{
                mb: 2,
                borderRadius: 2,
                background: alpha(theme.palette.warning.main, 0.1),
                border: `1px solid ${alpha(theme.palette.warning.main, 0.2)}`,
              }}
            >
              Modifying advanced settings may affect application performance
            </Alert>
            <SettingRow
              label="Debug Mode"
              description="Enable detailed logging and debugging information"
              control={
                <Switch
                  checked={advancedSettings.debugMode}
                  onChange={(e) => setAdvancedSettings({ ...advancedSettings, debugMode: e.target.checked })}
                  color="primary"
                />
              }
            />
            <SettingRow
              label="API Timeout"
              description="Maximum time to wait for API responses (seconds)"
              control={
                <TextField
                  type="number"
                  size="small"
                  value={advancedSettings.apiTimeout}
                  onChange={(e) => setAdvancedSettings({ ...advancedSettings, apiTimeout: parseInt(e.target.value) || 30 })}
                  inputProps={{ min: 5, max: 300 }}
                  sx={{ width: 100 }}
                />
              }
            />
            <SettingRow
              label="Max Retries"
              description="Number of times to retry failed API requests"
              control={
                <TextField
                  type="number"
                  size="small"
                  value={advancedSettings.maxRetries}
                  onChange={(e) => setAdvancedSettings({ ...advancedSettings, maxRetries: parseInt(e.target.value) || 3 })}
                  inputProps={{ min: 0, max: 10 }}
                  sx={{ width: 100 }}
                />
              }
            />
          </SettingSection>
        </Stack>

        {/* Footer with Save Button */}
        <Box mt={4} display="flex" justifyContent="center">
          <Button
            variant="contained"
            size="large"
            startIcon={<SaveIcon />}
            onClick={handleSaveSettings}
            sx={{
              borderRadius: 2,
              px: 4,
              py: 1.5,
              background: `linear-gradient(135deg, ${theme.palette.primary.main}, ${theme.palette.primary.dark})`,
              boxShadow: `0 8px 16px ${alpha(theme.palette.primary.main, 0.3)}`,
              '&:hover': {
                background: `linear-gradient(135deg, ${theme.palette.primary.dark}, ${theme.palette.primary.main})`,
                transform: 'translateY(-2px)',
                boxShadow: `0 12px 20px ${alpha(theme.palette.primary.main, 0.4)}`,
              },
            }}
          >
            Save All Settings
          </Button>
        </Box>
      </Container>
    </Box>
  );
};

export default Settings;
