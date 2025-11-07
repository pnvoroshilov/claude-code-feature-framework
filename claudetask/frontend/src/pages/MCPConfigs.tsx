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
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Alert,
  Chip,
  Tab,
  Tabs,
  CircularProgress,
  IconButton,
  Tooltip,
} from '@mui/material';
import AddIcon from '@mui/icons-material/Add';
import DeleteIcon from '@mui/icons-material/Delete';
import CodeIcon from '@mui/icons-material/Code';
import StarIcon from '@mui/icons-material/Star';
import axios from 'axios';

// Remove /api suffix if present, since we add it manually in request paths
const API_BASE_URL = (process.env.REACT_APP_API_URL || 'http://localhost:3333').replace(/\/api$/, '');

interface MCPConfig {
  id: number;
  name: string;
  description: string;
  mcp_config_type: 'default' | 'custom';
  category: string;
  config: Record<string, any>;
  is_enabled: boolean;
  status?: string;
  created_by?: string;
  created_at: string;
  updated_at: string;
}

interface MCPConfigsResponse {
  enabled: MCPConfig[];
  available_default: MCPConfig[];
  custom: MCPConfig[];
}

const MCPConfigs: React.FC = () => {
  const [activeTab, setActiveTab] = useState(0);
  const [configs, setConfigs] = useState<MCPConfigsResponse>({
    enabled: [],
    available_default: [],
    custom: [],
  });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [createDialogOpen, setCreateDialogOpen] = useState(false);
  const [viewConfigDialogOpen, setViewConfigDialogOpen] = useState(false);
  const [selectedConfig, setSelectedConfig] = useState<MCPConfig | null>(null);
  const [newConfigName, setNewConfigName] = useState('');
  const [newConfigDescription, setNewConfigDescription] = useState('');
  const [newConfigCategory, setNewConfigCategory] = useState('custom');
  const [newConfigJson, setNewConfigJson] = useState('{\n  "command": "",\n  "args": [],\n  "env": {}\n}');
  const [creating, setCreating] = useState(false);
  const [activeProjectId, setActiveProjectId] = useState<string | null>(null);

  // Fetch active project
  useEffect(() => {
    const fetchActiveProject = async () => {
      try {
        const response = await axios.get(`${API_BASE_URL}/api/projects`);
        const activeProject = response.data.find((p: any) => p.is_active);
        if (activeProject) {
          setActiveProjectId(activeProject.id);
        } else {
          setError('No active project found. Please activate a project first.');
        }
      } catch (err: any) {
        setError('Failed to fetch active project: ' + (err.response?.data?.detail || err.message));
      }
    };
    fetchActiveProject();
  }, []);

  // Fetch MCP configs when project is loaded
  useEffect(() => {
    if (activeProjectId) {
      fetchMCPConfigs();
    }
  }, [activeProjectId]);

  const fetchMCPConfigs = async () => {
    if (!activeProjectId) return;

    setLoading(true);
    setError(null);
    try {
      const response = await axios.get<MCPConfigsResponse>(
        `${API_BASE_URL}/api/projects/${activeProjectId}/mcp-configs/`
      );
      setConfigs(response.data);
    } catch (err: any) {
      setError('Failed to fetch MCP configs: ' + (err.response?.data?.detail || err.message));
    } finally {
      setLoading(false);
    }
  };

  const handleEnableConfig = async (configId: number, configType: 'default' | 'custom') => {
    if (!activeProjectId) return;

    try {
      await axios.post(
        `${API_BASE_URL}/api/projects/${activeProjectId}/mcp-configs/enable/${configId}?mcp_config_type=${configType}`
      );
      await fetchMCPConfigs(); // Refresh configs list
    } catch (err: any) {
      setError('Failed to enable MCP config: ' + (err.response?.data?.detail || err.message));
    }
  };

  const handleDisableConfig = async (configId: number) => {
    if (!activeProjectId) return;

    try {
      await axios.post(
        `${API_BASE_URL}/api/projects/${activeProjectId}/mcp-configs/disable/${configId}`
      );
      await fetchMCPConfigs(); // Refresh configs list
    } catch (err: any) {
      setError('Failed to disable MCP config: ' + (err.response?.data?.detail || err.message));
    }
  };

  const handleCreateConfig = async () => {
    if (!activeProjectId) return;

    setCreating(true);
    setError(null);
    try {
      // Parse JSON
      const config = JSON.parse(newConfigJson);

      await axios.post(
        `${API_BASE_URL}/api/projects/${activeProjectId}/mcp-configs/create`,
        {
          name: newConfigName,
          description: newConfigDescription,
          category: newConfigCategory,
          config: config,
        }
      );
      setCreateDialogOpen(false);
      setNewConfigName('');
      setNewConfigDescription('');
      setNewConfigCategory('custom');
      setNewConfigJson('{\n  "command": "",\n  "args": [],\n  "env": {}\n}');
      await fetchMCPConfigs(); // Refresh configs list
    } catch (err: any) {
      if (err instanceof SyntaxError) {
        setError('Invalid JSON format: ' + err.message);
      } else {
        setError('Failed to create MCP config: ' + (err.response?.data?.detail || err.message));
      }
    } finally {
      setCreating(false);
    }
  };

  const handleDeleteConfig = async (configId: number) => {
    if (!activeProjectId) return;
    if (!window.confirm('Are you sure you want to delete this custom MCP config?')) return;

    try {
      await axios.delete(
        `${API_BASE_URL}/api/projects/${activeProjectId}/mcp-configs/${configId}`
      );
      await fetchMCPConfigs(); // Refresh configs list
    } catch (err: any) {
      setError('Failed to delete MCP config: ' + (err.response?.data?.detail || err.message));
    }
  };

  const handleSaveToFavorites = async (configId: number, configName: string) => {
    if (!activeProjectId) return;
    if (!window.confirm(`Save "${configName}" to favorites?\n\nThis will make it available for all your projects in the Default MCP Servers catalog.`)) return;

    try {
      await axios.post(
        `${API_BASE_URL}/api/projects/${activeProjectId}/mcp-configs/favorites/${configId}`
      );
      alert(`"${configName}" has been saved to favorites!\n\nYou can now enable it from the Default MCP Servers tab in any project.`);
      await fetchMCPConfigs(); // Refresh configs list
    } catch (err: any) {
      setError('Failed to save to favorites: ' + (err.response?.data?.detail || err.message));
    }
  };

  const handleViewConfig = (config: MCPConfig) => {
    setSelectedConfig(config);
    setViewConfigDialogOpen(true);
  };

  const MCPConfigCard: React.FC<{ config: MCPConfig; showToggle?: boolean; showDelete?: boolean; showSaveToFavorites?: boolean }> = ({
    config,
    showToggle = false,
    showDelete = false,
    showSaveToFavorites = false,
  }) => (
    <Card sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      <CardContent sx={{ flexGrow: 1 }}>
        <Box display="flex" justifyContent="space-between" alignItems="start" mb={1}>
          <Box flexGrow={1}>
            <Typography variant="h6" component="div" gutterBottom>
              {config.name}
            </Typography>
            <Chip
              label={config.category}
              size="small"
              color="primary"
              variant="outlined"
              sx={{ mb: 1 }}
            />
          </Box>
          <Box display="flex" gap={1} alignItems="center">
            {config.status && config.status !== 'active' && (
              <Chip
                label={config.status}
                size="small"
                color={config.status === 'creating' ? 'info' : 'error'}
              />
            )}
            <Tooltip title="View Config JSON">
              <IconButton
                size="small"
                color="primary"
                onClick={() => handleViewConfig(config)}
              >
                <CodeIcon />
              </IconButton>
            </Tooltip>
            {showSaveToFavorites && (
              <Tooltip title="Save to Favorites">
                <IconButton
                  size="small"
                  color="warning"
                  onClick={() => handleSaveToFavorites(config.id, config.name)}
                >
                  <StarIcon />
                </IconButton>
              </Tooltip>
            )}
            {showDelete && (
              <IconButton
                size="small"
                color="error"
                onClick={() => handleDeleteConfig(config.id)}
              >
                <DeleteIcon />
              </IconButton>
            )}
          </Box>
        </Box>

        <Typography variant="body2" color="text.secondary" paragraph>
          {config.description}
        </Typography>

        {showToggle && (
          <FormControlLabel
            control={
              <Switch
                checked={config.is_enabled}
                onChange={(e) => {
                  if (e.target.checked) {
                    handleEnableConfig(config.id, config.mcp_config_type);
                  } else {
                    handleDisableConfig(config.id);
                  }
                }}
                disabled={config.status === 'creating'}
              />
            }
            label={config.is_enabled ? 'Enabled' : 'Enable'}
            sx={{ mt: 1 }}
          />
        )}
      </CardContent>
    </Card>
  );

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4">MCP Configurations</Typography>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={() => setCreateDialogOpen(true)}
          disabled={!activeProjectId}
        >
          Add Custom MCP
        </Button>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}

      {!activeProjectId && (
        <Alert severity="warning" sx={{ mb: 2 }}>
          No active project found. Please go to Projects and activate a project first.
        </Alert>
      )}

      <Alert severity="info" sx={{ mb: 3 }}>
        <Typography variant="body2">
          <strong>Note:</strong> After enabling/disabling MCP configs, you need to restart Claude Code for changes to take effect.
          The configurations are merged into your project's .mcp.json file.
        </Typography>
      </Alert>

      <Tabs value={activeTab} onChange={(_, newValue) => setActiveTab(newValue)} sx={{ mb: 3 }}>
        <Tab label={`Default MCP Servers (${configs.available_default.length})`} />
        <Tab label={`Custom MCP Servers (${configs.custom.length})`} />
        <Tab label={`Enabled MCP Servers (${configs.enabled.length})`} />
      </Tabs>

      {/* Default MCP Configs Tab */}
      {activeTab === 0 && (
        <Grid container spacing={3}>
          {configs.available_default.length === 0 ? (
            <Grid item xs={12}>
              <Alert severity="info">
                No default MCP configs available. They will be seeded on backend startup.
              </Alert>
            </Grid>
          ) : (
            configs.available_default.map((config) => (
              <Grid item xs={12} md={6} lg={4} key={config.id}>
                <MCPConfigCard config={config} showToggle={true} />
              </Grid>
            ))
          )}
        </Grid>
      )}

      {/* Custom MCP Configs Tab */}
      {activeTab === 1 && (
        <Grid container spacing={3}>
          {configs.custom.length === 0 ? (
            <Grid item xs={12}>
              <Alert severity="info">
                No custom MCP configs created yet. Click "Add Custom MCP" to add your own.
              </Alert>
            </Grid>
          ) : (
            configs.custom.map((config) => (
              <Grid item xs={12} md={6} lg={4} key={config.id}>
                <MCPConfigCard config={config} showToggle={true} showDelete={true} showSaveToFavorites={true} />
              </Grid>
            ))
          )}
        </Grid>
      )}

      {/* Enabled MCP Configs Tab */}
      {activeTab === 2 && (
        <Grid container spacing={3}>
          {configs.enabled.length === 0 ? (
            <Grid item xs={12}>
              <Alert severity="info">
                No MCP configs enabled yet. Enable default or custom configs from their respective tabs.
              </Alert>
            </Grid>
          ) : (
            configs.enabled.map((config) => (
              <Grid item xs={12} md={6} lg={4} key={config.id}>
                <MCPConfigCard config={config} />
              </Grid>
            ))
          )}
        </Grid>
      )}

      {/* Create Custom MCP Config Dialog */}
      <Dialog
        open={createDialogOpen}
        onClose={() => !creating && setCreateDialogOpen(false)}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>Add Custom MCP Server</DialogTitle>
        <DialogContent>
          <Alert severity="info" sx={{ mb: 2 }}>
            <Typography variant="body2">
              Add a custom MCP server configuration. The config will be merged into your project's .mcp.json file.
              Make sure to restart Claude Code after enabling/disabling MCP configs.
            </Typography>
          </Alert>
          <TextField
            autoFocus
            margin="dense"
            label="MCP Server Name"
            fullWidth
            variant="outlined"
            value={newConfigName}
            onChange={(e) => setNewConfigName(e.target.value)}
            disabled={creating}
            helperText="e.g., 'my-custom-server' (will be used as key in mcpServers)"
            sx={{ mb: 2 }}
          />
          <TextField
            margin="dense"
            label="Description"
            fullWidth
            variant="outlined"
            value={newConfigDescription}
            onChange={(e) => setNewConfigDescription(e.target.value)}
            disabled={creating}
            helperText="Describe what this MCP server provides"
            sx={{ mb: 2 }}
          />
          <TextField
            margin="dense"
            label="Category"
            fullWidth
            variant="outlined"
            value={newConfigCategory}
            onChange={(e) => setNewConfigCategory(e.target.value)}
            disabled={creating}
            helperText="e.g., 'development', 'testing', 'productivity'"
            sx={{ mb: 2 }}
          />
          <TextField
            margin="dense"
            label="MCP Server Configuration (JSON)"
            fullWidth
            multiline
            rows={10}
            variant="outlined"
            value={newConfigJson}
            onChange={(e) => setNewConfigJson(e.target.value)}
            disabled={creating}
            helperText="MCP server configuration in JSON format (must include 'command' field)"
            sx={{ fontFamily: 'monospace' }}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setCreateDialogOpen(false)} disabled={creating}>
            Cancel
          </Button>
          <Button
            onClick={handleCreateConfig}
            variant="contained"
            disabled={!newConfigName || !newConfigDescription || !newConfigJson || creating}
          >
            {creating ? <CircularProgress size={24} /> : 'Create'}
          </Button>
        </DialogActions>
      </Dialog>

      {/* View Config Dialog */}
      <Dialog
        open={viewConfigDialogOpen}
        onClose={() => setViewConfigDialogOpen(false)}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>MCP Configuration: {selectedConfig?.name}</DialogTitle>
        <DialogContent>
          <Typography variant="body2" color="text.secondary" paragraph>
            {selectedConfig?.description}
          </Typography>
          <Box sx={{ mb: 2 }}>
            <Chip label={selectedConfig?.category} size="small" color="primary" sx={{ mr: 1 }} />
            <Chip label={selectedConfig?.mcp_config_type} size="small" variant="outlined" />
          </Box>
          <Typography variant="subtitle2" gutterBottom>
            Configuration JSON:
          </Typography>
          <Box
            sx={{
              bgcolor: 'grey.100',
              p: 2,
              borderRadius: 1,
              fontFamily: 'monospace',
              fontSize: '0.875rem',
              overflow: 'auto',
              maxHeight: '400px',
            }}
          >
            <pre style={{ margin: 0 }}>
              {JSON.stringify(selectedConfig?.config, null, 2)}
            </pre>
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setViewConfigDialogOpen(false)}>Close</Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default MCPConfigs;
