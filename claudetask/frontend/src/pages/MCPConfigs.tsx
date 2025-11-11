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
  CircularProgress,
  IconButton,
  Tooltip,
  ToggleButtonGroup,
  ToggleButton,
  Menu,
  MenuItem,
  List,
  ListItem,
  ListItemText,
  ListItemButton,
  Divider,
  InputAdornment,
  Avatar,
  CardActionArea,
} from '@mui/material';
import AddIcon from '@mui/icons-material/Add';
import DeleteIcon from '@mui/icons-material/Delete';
import CodeIcon from '@mui/icons-material/Code';
import StarIcon from '@mui/icons-material/Star';
import StarBorderIcon from '@mui/icons-material/StarBorder';
import SearchIcon from '@mui/icons-material/Search';
import axios from 'axios';
import { useProject } from '../context/ProjectContext';

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
  is_favorite?: boolean;
  status?: string;
  created_by?: string;
  created_at: string;
  updated_at: string;
}

interface MCPConfigsResponse {
  enabled: MCPConfig[];
  available_default: MCPConfig[];
  custom: MCPConfig[];
  favorites: MCPConfig[];
}

type FilterType = 'all' | 'default' | 'custom' | 'favorite' | 'enabled';

const MCPConfigs: React.FC = () => {
  const { selectedProject } = useProject();
  const [activeFilter, setActiveFilter] = useState<FilterType>('all');
  const [configs, setConfigs] = useState<MCPConfigsResponse>({
    enabled: [],
    available_default: [],
    custom: [],
    favorites: [],
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

  // MCP Search state
  const [searchDialogOpen, setSearchDialogOpen] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState<any[]>([]);
  const [searching, setSearching] = useState(false);
  const [searchError, setSearchError] = useState<string | null>(null);
  const [addMenuAnchor, setAddMenuAnchor] = useState<null | HTMLElement>(null);

  // GitHub info dialog state
  const [githubInfoDialogOpen, setGithubInfoDialogOpen] = useState(false);
  const [selectedServerInfo, setSelectedServerInfo] = useState<any>(null);

  // Fetch MCP configs when project changes
  useEffect(() => {
    if (selectedProject?.id) {
      fetchMCPConfigs();
    }
  }, [selectedProject?.id]);

  const fetchMCPConfigs = async () => {
    if (!selectedProject?.id) return;

    setLoading(true);
    setError(null);
    try {
      const response = await axios.get<MCPConfigsResponse>(
        `${API_BASE_URL}/api/projects/${selectedProject.id}/mcp-configs/`
      );
      setConfigs(response.data);
    } catch (err: any) {
      setError('Failed to fetch MCP configs: ' + (err.response?.data?.detail || err.message));
    } finally {
      setLoading(false);
    }
  };

  const handleEnableConfig = async (configId: number, configType: 'default' | 'custom') => {
    if (!selectedProject?.id) return;

    try {
      await axios.post(
        `${API_BASE_URL}/api/projects/${selectedProject.id}/mcp-configs/enable/${configId}?mcp_config_type=${configType}`
      );
      await fetchMCPConfigs(); // Refresh configs list
    } catch (err: any) {
      setError('Failed to enable MCP config: ' + (err.response?.data?.detail || err.message));
    }
  };

  const handleDisableConfig = async (configId: number) => {
    if (!selectedProject?.id) return;

    try {
      await axios.post(
        `${API_BASE_URL}/api/projects/${selectedProject.id}/mcp-configs/disable/${configId}`
      );
      await fetchMCPConfigs(); // Refresh configs list
    } catch (err: any) {
      setError('Failed to disable MCP config: ' + (err.response?.data?.detail || err.message));
    }
  };

  const handleCreateConfig = async () => {
    if (!selectedProject?.id) return;

    setCreating(true);
    setError(null);
    try {
      // Parse JSON
      const config = JSON.parse(newConfigJson);

      await axios.post(
        `${API_BASE_URL}/api/projects/${selectedProject.id}/mcp-configs/create`,
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
    if (!selectedProject?.id) return;
    if (!window.confirm('Are you sure you want to delete this custom MCP config?')) return;

    try {
      await axios.delete(
        `${API_BASE_URL}/api/projects/${selectedProject.id}/mcp-configs/${configId}`
      );
      await fetchMCPConfigs(); // Refresh configs list
    } catch (err: any) {
      setError('Failed to delete MCP config: ' + (err.response?.data?.detail || err.message));
    }
  };

  const handleSaveToFavorites = async (configId: number, configName: string, configType: 'default' | 'custom') => {
    if (!selectedProject?.id) return;
    if (!window.confirm(`Save "${configName}" to favorites?\n\nThis will make it appear in the Favorites tab.`)) return;

    try {
      await axios.post(
        `${API_BASE_URL}/api/projects/${selectedProject.id}/mcp-configs/favorites/${configId}?mcp_config_type=${configType}`
      );
      await fetchMCPConfigs(); // Refresh configs list
    } catch (err: any) {
      setError('Failed to save to favorites: ' + (err.response?.data?.detail || err.message));
    }
  };

  const handleRemoveFromFavorites = async (configId: number, configName: string, configType: 'default' | 'custom') => {
    if (!selectedProject?.id) return;
    if (!window.confirm(`Remove "${configName}" from favorites?\n\nIt will no longer appear in the Favorites tab.`)) return;

    try {
      await axios.delete(
        `${API_BASE_URL}/api/projects/${selectedProject.id}/mcp-configs/favorites/${configId}?mcp_config_type=${configType}`
      );
      await fetchMCPConfigs(); // Refresh configs list
    } catch (err: any) {
      setError('Failed to remove from favorites: ' + (err.response?.data?.detail || err.message));
    }
  };

  const handleViewConfig = (config: MCPConfig) => {
    setSelectedConfig(config);
    setViewConfigDialogOpen(true);
  };

  const handleSearchMCP = async () => {
    if (!searchQuery.trim()) return;

    setSearching(true);
    setSearchError(null);
    try {
      const response = await axios.get(
        `${API_BASE_URL}/api/mcp-search/search?q=${encodeURIComponent(searchQuery)}`
      );
      setSearchResults(response.data.results || []);
    } catch (err: any) {
      setSearchError('Failed to search MCP servers: ' + (err.response?.data?.detail || err.message));
    } finally {
      setSearching(false);
    }
  };

  const handleSelectFromSearch = async (server: any) => {
    // Fetch server config details
    try {
      const configResponse = await axios.get(
        `${API_BASE_URL}/api/mcp-search/server-config?url=${encodeURIComponent(server.url)}`
      );

      // Pre-fill create dialog with server info
      setNewConfigName(server.name);
      setNewConfigDescription(configResponse.data.description || server.description);
      setNewConfigCategory('custom');

      // Check if config was found
      if (configResponse.data.config) {
        // Config found - proceed to create dialog
        setNewConfigJson(JSON.stringify(configResponse.data.config, null, 2));
        setSearchDialogOpen(false);
        setCreateDialogOpen(true);
      } else {
        // No config found - show GitHub info dialog
        setSelectedServerInfo({
          ...server,
          github_url: configResponse.data.github_url || server.github_url,
          description: configResponse.data.description || server.description,
          avatar_url: configResponse.data.avatar_url || server.avatar_url
        });
        setSearchDialogOpen(false);
        setGithubInfoDialogOpen(true);
      }
    } catch (err: any) {
      setSearchError('Failed to fetch server config: ' + (err.response?.data?.detail || err.message));
    }
  };

  // Filter configs based on active filter
  const getFilteredConfigs = (): MCPConfig[] => {
    switch (activeFilter) {
      case 'default':
        return configs.available_default;
      case 'custom':
        return configs.custom;
      case 'favorite':
        return configs.favorites;
      case 'enabled':
        return configs.enabled;
      case 'all':
      default:
        // Combine all unique configs (avoiding duplicates by id)
        const allConfigs = [
          ...configs.available_default,
          ...configs.custom,
        ];
        // Remove duplicates by id
        const uniqueConfigs = allConfigs.filter(
          (config, index, self) => self.findIndex(c => c.id === config.id && c.mcp_config_type === config.mcp_config_type) === index
        );
        return uniqueConfigs;
    }
  };

  const filteredConfigs = getFilteredConfigs();

  const MCPConfigCard: React.FC<{
    config: MCPConfig;
    showToggle?: boolean;
    showDelete?: boolean;
    showSaveToFavorites?: boolean;
    showRemoveFromFavorites?: boolean;
  }> = ({
    config,
    showToggle = false,
    showDelete = false,
    showSaveToFavorites = false,
    showRemoveFromFavorites = false,
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
              <Tooltip title="Add to Favorites">
                <IconButton
                  size="small"
                  sx={{ color: 'warning.main' }}
                  onClick={() => handleSaveToFavorites(config.id, config.name, config.mcp_config_type as 'default' | 'custom')}
                >
                  <StarBorderIcon />
                </IconButton>
              </Tooltip>
            )}
            {showRemoveFromFavorites && (
              <Tooltip title="Remove from Favorites">
                <IconButton
                  size="small"
                  color="warning"
                  onClick={() => handleRemoveFromFavorites(config.id, config.name, config.mcp_config_type as 'default' | 'custom')}
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
        <Box>
          <Button
            variant="contained"
            startIcon={<AddIcon />}
            onClick={(e) => setAddMenuAnchor(e.currentTarget)}
            disabled={!selectedProject?.id}
          >
            Add MCP
          </Button>
          <Menu
            anchorEl={addMenuAnchor}
            open={Boolean(addMenuAnchor)}
            onClose={() => setAddMenuAnchor(null)}
          >
            <MenuItem
              onClick={() => {
                setAddMenuAnchor(null);
                setSearchDialogOpen(true);
              }}
            >
              <SearchIcon sx={{ mr: 1 }} />
              Search from mcp.so
            </MenuItem>
            <MenuItem
              onClick={() => {
                setAddMenuAnchor(null);
                setCreateDialogOpen(true);
              }}
            >
              <AddIcon sx={{ mr: 1 }} />
              Create Custom
            </MenuItem>
          </Menu>
        </Box>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}

      {!selectedProject?.id && (
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

      {/* Filter Buttons */}
      <Box sx={{ mb: 3, display: 'flex', justifyContent: 'center' }}>
        <ToggleButtonGroup
          value={activeFilter}
          exclusive
          onChange={(_, newFilter) => newFilter && setActiveFilter(newFilter)}
          aria-label="MCP filter"
        >
          <ToggleButton value="all" aria-label="all">
            All ({configs.available_default.length + configs.custom.length})
          </ToggleButton>
          <ToggleButton value="default" aria-label="default">
            Default ({configs.available_default.length})
          </ToggleButton>
          <ToggleButton value="custom" aria-label="custom">
            Custom ({configs.custom.length})
          </ToggleButton>
          <ToggleButton value="favorite" aria-label="favorite">
            Favorites ({configs.favorites.length})
          </ToggleButton>
          <ToggleButton value="enabled" aria-label="enabled">
            Enabled ({configs.enabled.length})
          </ToggleButton>
        </ToggleButtonGroup>
      </Box>

      {/* MCP Configs Grid */}
      <Grid container spacing={3}>
        {filteredConfigs.length === 0 ? (
          <Grid item xs={12}>
            <Alert severity="info">
              {activeFilter === 'all' && 'No MCP configs available.'}
              {activeFilter === 'default' && 'No default MCP configs available.'}
              {activeFilter === 'custom' && 'No custom MCP configs created yet. Click "Add Custom MCP" to add your own.'}
              {activeFilter === 'favorite' && 'No favorite MCP configs yet. Add MCP servers to favorites by clicking the star icon.'}
              {activeFilter === 'enabled' && 'No MCP configs enabled yet. Enable configs by toggling the switch.'}
            </Alert>
          </Grid>
        ) : (
          filteredConfigs.map((config) => (
            <Grid item xs={12} md={6} lg={4} key={`${config.mcp_config_type}-${config.id}`}>
              <MCPConfigCard
                config={config}
                showToggle={activeFilter !== 'enabled'}
                showDelete={config.mcp_config_type === 'custom' && activeFilter !== 'enabled'}
                showSaveToFavorites={!config.is_favorite && activeFilter !== 'enabled' && activeFilter !== 'favorite'}
                showRemoveFromFavorites={config.is_favorite && activeFilter !== 'enabled'}
              />
            </Grid>
          ))
        )}
      </Grid>

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

      {/* MCP Search Dialog */}
      <Dialog
        open={searchDialogOpen}
        onClose={() => setSearchDialogOpen(false)}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>Search MCP Servers from mcp.so</DialogTitle>
        <DialogContent>
          <Box sx={{ mb: 2 }}>
            <TextField
              fullWidth
              placeholder="Search for MCP servers (e.g., 'postgres', 'filesystem', 'git')"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              onKeyPress={(e) => {
                if (e.key === 'Enter') {
                  handleSearchMCP();
                }
              }}
              InputProps={{
                startAdornment: (
                  <InputAdornment position="start">
                    <SearchIcon />
                  </InputAdornment>
                ),
                endAdornment: (
                  <InputAdornment position="end">
                    <Button
                      onClick={handleSearchMCP}
                      disabled={!searchQuery.trim() || searching}
                    >
                      {searching ? <CircularProgress size={20} /> : 'Search'}
                    </Button>
                  </InputAdornment>
                ),
              }}
            />
          </Box>

          {searchError && (
            <Alert severity="error" sx={{ mb: 2 }} onClose={() => setSearchError(null)}>
              {searchError}
            </Alert>
          )}

          {searching && (
            <Box display="flex" justifyContent="center" p={4}>
              <CircularProgress />
            </Box>
          )}

          {!searching && searchResults.length > 0 && (
            <>
              <Typography variant="subtitle2" gutterBottom sx={{ mt: 2 }}>
                Found {searchResults.length} MCP servers:
              </Typography>
              <Grid container spacing={2} sx={{ maxHeight: '500px', overflow: 'auto', mt: 1 }}>
                {searchResults.map((server, index) => (
                  <Grid item xs={12} sm={6} md={4} key={index}>
                    <Card
                      sx={{
                        height: '100%',
                        display: 'flex',
                        flexDirection: 'column',
                        cursor: 'pointer',
                        '&:hover': {
                          boxShadow: 6,
                          transform: 'translateY(-4px)',
                          transition: 'all 0.3s ease-in-out'
                        }
                      }}
                    >
                      <CardActionArea
                        onClick={() => handleSelectFromSearch(server)}
                        sx={{ height: '100%', display: 'flex', flexDirection: 'column', alignItems: 'flex-start' }}
                      >
                        <Box sx={{ p: 2, display: 'flex', alignItems: 'center', width: '100%' }}>
                          <Avatar
                            src={server.avatar_url}
                            alt={server.title || server.name}
                            sx={{ width: 48, height: 48, mr: 2 }}
                          >
                            {!server.avatar_url && (server.title || server.name).charAt(0).toUpperCase()}
                          </Avatar>
                          <Box sx={{ flex: 1, minWidth: 0 }}>
                            <Typography variant="h6" component="div" noWrap>
                              {server.title || server.name}
                            </Typography>
                            {server.author_name && (
                              <Typography variant="caption" color="text.secondary">
                                by {server.author_name}
                              </Typography>
                            )}
                          </Box>
                        </Box>
                        <CardContent sx={{ pt: 0, width: '100%', flex: 1 }}>
                          <Typography variant="body2" color="text.secondary" sx={{
                            overflow: 'hidden',
                            textOverflow: 'ellipsis',
                            display: '-webkit-box',
                            WebkitLineClamp: 3,
                            WebkitBoxOrient: 'vertical',
                          }}>
                            {server.description}
                          </Typography>
                        </CardContent>
                      </CardActionArea>
                    </Card>
                  </Grid>
                ))}
              </Grid>
            </>
          )}

          {!searching && searchResults.length === 0 && searchQuery && (
            <Alert severity="info">
              No results found. Try a different search term.
            </Alert>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setSearchDialogOpen(false)}>Close</Button>
        </DialogActions>
      </Dialog>

      {/* GitHub Info Dialog - shown when config not found */}
      <Dialog
        open={githubInfoDialogOpen}
        onClose={() => setGithubInfoDialogOpen(false)}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle>MCP Configuration Not Found</DialogTitle>
        <DialogContent>
          {selectedServerInfo && (
            <Card sx={{ mt: 2 }}>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                  <Avatar
                    src={selectedServerInfo.avatar_url}
                    alt={selectedServerInfo.title || selectedServerInfo.name}
                    sx={{ width: 64, height: 64, mr: 2 }}
                  >
                    {!selectedServerInfo.avatar_url && (selectedServerInfo.title || selectedServerInfo.name).charAt(0).toUpperCase()}
                  </Avatar>
                  <Box>
                    <Typography variant="h6">
                      {selectedServerInfo.title || selectedServerInfo.name}
                    </Typography>
                    {selectedServerInfo.author_name && (
                      <Typography variant="body2" color="text.secondary">
                        by {selectedServerInfo.author_name}
                      </Typography>
                    )}
                  </Box>
                </Box>

                <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                  {selectedServerInfo.description}
                </Typography>

                <Alert severity="info" sx={{ mb: 2 }}>
                  Configuration not available. Please visit the GitHub repository to find installation instructions and configuration details.
                </Alert>

                {selectedServerInfo.github_url && (
                  <Button
                    variant="contained"
                    color="primary"
                    fullWidth
                    startIcon={<CodeIcon />}
                    onClick={() => window.open(selectedServerInfo.github_url, '_blank')}
                  >
                    Open GitHub Repository
                  </Button>
                )}
              </CardContent>
            </Card>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setGithubInfoDialogOpen(false)}>Close</Button>
          <Button
            variant="outlined"
            onClick={() => {
              // Provide empty template for manual configuration
              const emptyConfig = {
                command: "npx",
                args: ["-y", `${selectedServerInfo?.name || 'package'}`]
              };
              setNewConfigName(selectedServerInfo?.name || '');
              setNewConfigDescription(selectedServerInfo?.description || '');
              setNewConfigCategory('custom');
              setNewConfigJson(JSON.stringify(emptyConfig, null, 2));
              setGithubInfoDialogOpen(false);
              setCreateDialogOpen(true);
            }}
          >
            Configure Manually
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default MCPConfigs;
