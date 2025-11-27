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
  Stack,
  Container,
  alpha,
  useTheme,
  Paper,
  Badge,
} from '@mui/material';
import AddIcon from '@mui/icons-material/Add';
import DeleteIcon from '@mui/icons-material/Delete';
import CodeIcon from '@mui/icons-material/Code';
import StarIcon from '@mui/icons-material/Star';
import StarBorderIcon from '@mui/icons-material/StarBorder';
import SearchIcon from '@mui/icons-material/Search';
import CloseIcon from '@mui/icons-material/Close';
import SettingsIcon from '@mui/icons-material/Settings';
import CloudIcon from '@mui/icons-material/Cloud';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
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
  const theme = useTheme();
  const [activeFilter, setActiveFilter] = useState<FilterType>('all');
  const [filterQuery, setFilterQuery] = useState('');
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

  const handleDisableConfig = async (configId: number, configType: 'default' | 'custom') => {
    if (!selectedProject?.id) return;

    try {
      await axios.post(
        `${API_BASE_URL}/api/projects/${selectedProject.id}/mcp-configs/disable/${configId}?mcp_config_type=${configType}`
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

  const handleEnableAll = async () => {
    if (!selectedProject?.id) return;

    setLoading(true);
    setError(null);
    try {
      const response = await axios.post(
        `${API_BASE_URL}/api/projects/${selectedProject.id}/mcp-configs/enable-all`
      );
      await fetchMCPConfigs();
      if (response.data.errors && response.data.errors.length > 0) {
        setError(`Enabled ${response.data.enabled_count} MCP configs with some errors: ${response.data.errors.join(', ')}`);
      }
    } catch (err: any) {
      setError('Failed to enable all MCP configs: ' + (err.response?.data?.detail || err.message));
    } finally {
      setLoading(false);
    }
  };

  const handleDisableAll = async () => {
    if (!selectedProject?.id) return;
    if (!window.confirm('Are you sure you want to disable all enabled MCP configs?')) return;

    setLoading(true);
    setError(null);
    try {
      const response = await axios.post(
        `${API_BASE_URL}/api/projects/${selectedProject.id}/mcp-configs/disable-all`
      );
      await fetchMCPConfigs();
      if (response.data.errors && response.data.errors.length > 0) {
        setError(`Disabled ${response.data.disabled_count} MCP configs with some errors: ${response.data.errors.join(', ')}`);
      }
    } catch (err: any) {
      setError('Failed to disable all MCP configs: ' + (err.response?.data?.detail || err.message));
    } finally {
      setLoading(false);
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
    let filtered: MCPConfig[] = [];

    switch (activeFilter) {
      case 'default':
        filtered = configs.available_default;
        break;
      case 'custom':
        filtered = configs.custom;
        break;
      case 'favorite':
        filtered = configs.favorites;
        break;
      case 'enabled':
        filtered = configs.enabled;
        break;
      case 'all':
      default:
        // Combine all unique configs (avoiding duplicates by id)
        const allConfigs = [
          ...configs.available_default,
          ...configs.custom,
        ];
        // Remove duplicates by id
        filtered = allConfigs.filter(
          (config, index, self) => self.findIndex(c => c.id === config.id && c.mcp_config_type === config.mcp_config_type) === index
        );
    }

    // Apply search filter
    if (filterQuery.trim()) {
      const query = filterQuery.toLowerCase();
      filtered = filtered.filter(
        config =>
          config.name.toLowerCase().includes(query) ||
          config.description.toLowerCase().includes(query) ||
          config.category.toLowerCase().includes(query)
      );
    }

    return filtered;
  };

  const filteredConfigs = getFilteredConfigs();

  // Statistics
  const stats = {
    total: configs.available_default.length + configs.custom.length,
    enabled: configs.enabled.length,
    favorites: configs.favorites.length,
    custom: configs.custom.length,
  };

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
    <Card
      sx={{
        height: '100%',
        display: 'flex',
        flexDirection: 'column',
        position: 'relative',
        overflow: 'visible',
        background: `linear-gradient(145deg, ${alpha(theme.palette.background.paper, 0.9)}, ${alpha(theme.palette.background.paper, 0.7)})`,
        border: `1px solid ${alpha(theme.palette.primary.main, 0.1)}`,
        borderRadius: 3,
        transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
        '&:hover': {
          transform: 'translateY(-8px)',
          borderColor: alpha(theme.palette.primary.main, 0.3),
          boxShadow: `0 20px 40px ${alpha(theme.palette.primary.main, 0.15)}`,
        },
      }}
    >
      {/* Status indicator bar */}
      <Box
        sx={{
          position: 'absolute',
          top: 0,
          left: 0,
          right: 0,
          height: 4,
          background: config.is_enabled
            ? `linear-gradient(90deg, ${theme.palette.success.main}, ${theme.palette.success.light})`
            : `linear-gradient(90deg, ${alpha(theme.palette.text.disabled, 0.3)}, ${alpha(theme.palette.text.disabled, 0.1)})`,
          borderTopLeftRadius: 12,
          borderTopRightRadius: 12,
        }}
      />

      <CardContent sx={{ flexGrow: 1, pt: 3 }}>
        {/* Header */}
        <Box display="flex" justifyContent="space-between" alignItems="start" mb={2}>
          <Box display="flex" alignItems="start" gap={1.5} flexGrow={1}>
            <Box
              sx={{
                width: 48,
                height: 48,
                borderRadius: 2,
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                background: `linear-gradient(135deg, ${alpha(theme.palette.primary.main, 0.15)}, ${alpha(theme.palette.primary.main, 0.05)})`,
                border: `1px solid ${alpha(theme.palette.primary.main, 0.2)}`,
              }}
            >
              <SettingsIcon sx={{ color: theme.palette.primary.main, fontSize: 28 }} />
            </Box>
            <Box flexGrow={1}>
              <Typography
                variant="h6"
                component="div"
                sx={{
                  fontWeight: 700,
                  fontSize: '1.1rem',
                  mb: 0.5,
                  color: theme.palette.text.primary,
                  display: 'flex',
                  alignItems: 'center',
                  gap: 1,
                }}
              >
                {config.name}
                {config.is_enabled && (
                  <Tooltip title="Enabled">
                    <CheckCircleIcon sx={{ fontSize: 20, color: theme.palette.success.main }} />
                  </Tooltip>
                )}
              </Typography>
              <Stack direction="row" spacing={0.5} flexWrap="wrap">
                <Chip
                  label={config.category}
                  size="small"
                  sx={{
                    height: 22,
                    fontSize: '0.7rem',
                    fontWeight: 600,
                    background: `linear-gradient(135deg, ${alpha(theme.palette.primary.main, 0.1)}, ${alpha(theme.palette.primary.main, 0.05)})`,
                    border: `1px solid ${alpha(theme.palette.primary.main, 0.2)}`,
                    color: theme.palette.primary.main,
                  }}
                />
                <Chip
                  label={config.mcp_config_type === 'default' ? 'Default' : 'Custom'}
                  size="small"
                  sx={{
                    height: 22,
                    fontSize: '0.7rem',
                    fontWeight: 500,
                    bgcolor: alpha(theme.palette.info.main, 0.1),
                    color: theme.palette.info.main,
                    border: `1px solid ${alpha(theme.palette.info.main, 0.2)}`,
                  }}
                />
              </Stack>
            </Box>
          </Box>

          {/* Action Icons */}
          <Stack direction="row" spacing={0.5}>
            {config.status && config.status !== 'active' && (
              <Chip
                label={config.status}
                size="small"
                sx={{
                  height: 22,
                  fontSize: '0.7rem',
                  fontWeight: 600,
                  ...(config.status === 'creating' ? {
                    backgroundColor: alpha(theme.palette.info.main, 0.15),
                    color: theme.palette.info.light,
                  } : {
                    backgroundColor: alpha(theme.palette.error.main, 0.15),
                    color: theme.palette.error.light,
                  })
                }}
              />
            )}
            <Tooltip title="View Config JSON">
              <IconButton
                size="small"
                onClick={() => handleViewConfig(config)}
                sx={{
                  color: theme.palette.primary.main,
                  transition: 'all 0.2s ease',
                  '&:hover': {
                    backgroundColor: alpha(theme.palette.primary.main, 0.1),
                    transform: 'scale(1.1)',
                  }
                }}
              >
                <CodeIcon fontSize="small" />
              </IconButton>
            </Tooltip>
            {showSaveToFavorites && (
              <Tooltip title="Add to Favorites">
                <IconButton
                  size="small"
                  onClick={() => handleSaveToFavorites(config.id, config.name, config.mcp_config_type as 'default' | 'custom')}
                  sx={{
                    color: theme.palette.warning.main,
                    transition: 'all 0.2s ease',
                    '&:hover': {
                      backgroundColor: alpha(theme.palette.warning.main, 0.1),
                      transform: 'scale(1.1)',
                    }
                  }}
                >
                  <StarBorderIcon fontSize="small" />
                </IconButton>
              </Tooltip>
            )}
            {showRemoveFromFavorites && (
              <Tooltip title="Remove from Favorites">
                <IconButton
                  size="small"
                  onClick={() => handleRemoveFromFavorites(config.id, config.name, config.mcp_config_type as 'default' | 'custom')}
                  sx={{
                    color: theme.palette.warning.main,
                    transition: 'all 0.2s ease',
                    '&:hover': {
                      backgroundColor: alpha(theme.palette.warning.main, 0.1),
                      transform: 'scale(1.1)',
                    }
                  }}
                >
                  <StarIcon fontSize="small" />
                </IconButton>
              </Tooltip>
            )}
            {showDelete && (
              <Tooltip title="Delete Config">
                <IconButton
                  size="small"
                  onClick={() => handleDeleteConfig(config.id)}
                  sx={{
                    color: theme.palette.error.main,
                    transition: 'all 0.2s ease',
                    '&:hover': {
                      backgroundColor: alpha(theme.palette.error.main, 0.1),
                      transform: 'scale(1.1)',
                    }
                  }}
                >
                  <DeleteIcon fontSize="small" />
                </IconButton>
              </Tooltip>
            )}
          </Stack>
        </Box>

        <Divider sx={{ my: 2, borderColor: alpha(theme.palette.divider, 0.5) }} />

        {/* Description */}
        <Typography
          variant="body2"
          sx={{
            color: theme.palette.text.secondary,
            mb: 2,
            lineHeight: 1.6,
            minHeight: '48px',
            display: '-webkit-box',
            WebkitLineClamp: 2,
            WebkitBoxOrient: 'vertical',
            overflow: 'hidden',
          }}
        >
          {config.description}
        </Typography>

        {/* Toggle Switch */}
        {showToggle && (
          <FormControlLabel
            control={
              <Switch
                checked={config.is_enabled}
                onChange={(e) => {
                  if (e.target.checked) {
                    handleEnableConfig(config.id, config.mcp_config_type);
                  } else {
                    handleDisableConfig(config.id, config.mcp_config_type);
                  }
                }}
                disabled={config.status === 'creating'}
                sx={{
                  '& .MuiSwitch-switchBase.Mui-checked': {
                    color: theme.palette.success.main,
                  },
                  '& .MuiSwitch-switchBase.Mui-checked + .MuiSwitch-track': {
                    backgroundColor: theme.palette.success.main,
                  },
                }}
              />
            }
            label={
              <Typography variant="body2" fontWeight={600} color={config.is_enabled ? 'success.main' : 'text.secondary'}>
                {config.is_enabled ? 'Enabled' : 'Enable'}
              </Typography>
            }
            sx={{ mt: 1 }}
          />
        )}
      </CardContent>
    </Card>
  );

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress sx={{ color: '#6366f1' }} />
      </Box>
    );
  }

  return (
    <Container maxWidth="xl" sx={{ py: 4 }}>
      {/* Header Section */}
      <Box sx={{ mb: 5 }}>
        <Box display="flex" justifyContent="space-between" alignItems="flex-start" mb={2}>
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
              MCP Configurations
            </Typography>
            <Typography
              variant="body1"
              sx={{
                color: alpha(theme.palette.text.secondary, 0.8),
                maxWidth: '600px',
              }}
            >
              Manage Model Context Protocol servers for enhanced AI capabilities
            </Typography>
          </Box>
          <Stack direction="row" spacing={2}>
            <Button
              variant="outlined"
              size="large"
              startIcon={<CheckCircleIcon />}
              onClick={handleEnableAll}
              disabled={!selectedProject?.id || loading}
              sx={{
                borderRadius: 2,
                px: 2,
                py: 1.5,
                borderColor: theme.palette.success.main,
                color: theme.palette.success.main,
                '&:hover': {
                  borderColor: theme.palette.success.dark,
                  backgroundColor: alpha(theme.palette.success.main, 0.08),
                  transform: 'translateY(-2px)',
                },
                '&:disabled': {
                  borderColor: theme.palette.action.disabledBackground,
                  color: theme.palette.action.disabled,
                },
              }}
            >
              Enable All
            </Button>
            <Button
              variant="outlined"
              size="large"
              startIcon={<CloseIcon />}
              onClick={handleDisableAll}
              disabled={!selectedProject?.id || loading}
              sx={{
                borderRadius: 2,
                px: 2,
                py: 1.5,
                borderColor: theme.palette.error.main,
                color: theme.palette.error.main,
                '&:hover': {
                  borderColor: theme.palette.error.dark,
                  backgroundColor: alpha(theme.palette.error.main, 0.08),
                  transform: 'translateY(-2px)',
                },
                '&:disabled': {
                  borderColor: theme.palette.action.disabledBackground,
                  color: theme.palette.action.disabled,
                },
              }}
            >
              Disable All
            </Button>
            <Button
              variant="contained"
              startIcon={<AddIcon />}
              onClick={(e) => setAddMenuAnchor(e.currentTarget)}
              disabled={!selectedProject?.id}
              sx={{
                background: `linear-gradient(135deg, ${theme.palette.primary.main}, ${theme.palette.primary.dark})`,
                color: '#fff',
                fontWeight: 600,
                textTransform: 'none',
                px: 3,
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
                },
              }}
            >
              Add MCP
            </Button>
          </Stack>
          <Menu
            anchorEl={addMenuAnchor}
            open={Boolean(addMenuAnchor)}
            onClose={() => setAddMenuAnchor(null)}
            PaperProps={{
              sx: {
                backgroundColor: theme.palette.background.paper,
                border: `1px solid ${alpha(theme.palette.divider, 0.1)}`,
                borderRadius: 2,
                mt: 1,
                '& .MuiMenuItem-root': {
                  color: theme.palette.text.primary,
                  borderRadius: 1,
                  mx: 1,
                  my: 0.5,
                  '&:hover': {
                    backgroundColor: alpha(theme.palette.primary.main, 0.1),
                  },
                },
              },
            }}
          >
            <MenuItem
              onClick={() => {
                setAddMenuAnchor(null);
                setSearchDialogOpen(true);
              }}
            >
              <SearchIcon sx={{ mr: 1.5, color: theme.palette.primary.main }} />
              Search from mcp.so
            </MenuItem>
            <MenuItem
              onClick={() => {
                setAddMenuAnchor(null);
                setCreateDialogOpen(true);
              }}
            >
              <AddIcon sx={{ mr: 1.5, color: theme.palette.primary.main }} />
              Create Custom
            </MenuItem>
          </Menu>
        </Box>
      </Box>

      {/* Alerts */}
      {error && (
        <Alert
          severity="error"
          sx={{
            mb: 3,
            backgroundColor: alpha(theme.palette.error.main, 0.1),
            border: `1px solid ${alpha(theme.palette.error.main, 0.3)}`,
            borderRadius: 2,
            '& .MuiAlert-icon': { color: theme.palette.error.main },
          }}
          onClose={() => setError(null)}
        >
          {error}
        </Alert>
      )}

      {!selectedProject?.id && (
        <Alert
          severity="warning"
          sx={{
            mb: 3,
            backgroundColor: alpha(theme.palette.warning.main, 0.1),
            border: `1px solid ${alpha(theme.palette.warning.main, 0.3)}`,
            borderRadius: 2,
            '& .MuiAlert-icon': { color: theme.palette.warning.main },
          }}
        >
          No active project found. Please go to Projects and activate a project first.
        </Alert>
      )}

      <Alert
        severity="info"
        sx={{
          mb: 4,
          backgroundColor: alpha(theme.palette.info.main, 0.1),
          border: `1px solid ${alpha(theme.palette.info.main, 0.3)}`,
          borderRadius: 2,
          '& .MuiAlert-icon': { color: theme.palette.info.main },
        }}
      >
        <Typography variant="body2">
          <strong>Note:</strong> After enabling/disabling MCP configs, you need to restart Claude Code for changes to take effect.
          The configurations are merged into your project's .mcp.json file.
        </Typography>
      </Alert>

      {/* Statistics Cards */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        {[
          { label: 'Total MCPs', value: stats.total, color: theme.palette.primary.main, icon: <CloudIcon /> },
          { label: 'Enabled', value: stats.enabled, color: theme.palette.success.main, icon: <CheckCircleIcon /> },
          { label: 'Favorites', value: stats.favorites, color: theme.palette.warning.main, icon: <StarIcon /> },
          { label: 'Custom', value: stats.custom, color: theme.palette.info.main, icon: <SettingsIcon /> },
        ].map((stat, index) => (
          <Grid item xs={12} sm={6} md={3} key={index}>
            <Paper
              sx={{
                p: 2.5,
                borderRadius: 2,
                background: `linear-gradient(145deg, ${alpha(stat.color, 0.05)}, ${alpha(stat.color, 0.02)})`,
                border: `1px solid ${alpha(stat.color, 0.15)}`,
                transition: 'all 0.3s ease',
                '&:hover': {
                  transform: 'translateY(-4px)',
                  boxShadow: `0 8px 16px ${alpha(stat.color, 0.2)}`,
                },
              }}
            >
              <Stack direction="row" alignItems="center" spacing={2}>
                <Box
                  sx={{
                    p: 1.5,
                    borderRadius: 2,
                    background: `linear-gradient(135deg, ${alpha(stat.color, 0.2)}, ${alpha(stat.color, 0.1)})`,
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                  }}
                >
                  {React.cloneElement(stat.icon as React.ReactElement, {
                    sx: { color: stat.color, fontSize: 28 },
                  })}
                </Box>
                <Box sx={{ flex: 1 }}>
                  <Typography
                    variant="h4"
                    sx={{
                      fontWeight: 700,
                      color: stat.color,
                      mb: 0.5,
                    }}
                  >
                    {stat.value}
                  </Typography>
                  <Typography
                    variant="body2"
                    sx={{
                      color: alpha(theme.palette.text.secondary, 0.8),
                      fontWeight: 500,
                    }}
                  >
                    {stat.label}
                  </Typography>
                </Box>
              </Stack>
            </Paper>
          </Grid>
        ))}
      </Grid>

      {/* Search and Filter Bar */}
      <Paper
        sx={{
          p: 3,
          mb: 4,
          borderRadius: 2,
          background: alpha(theme.palette.background.paper, 0.6),
          border: `1px solid ${alpha(theme.palette.divider, 0.1)}`,
        }}
      >
        <Stack spacing={3}>
          {/* Search */}
          <TextField
            fullWidth
            placeholder="Search MCP configs by name, description, or category..."
            value={filterQuery}
            onChange={(e) => setFilterQuery(e.target.value)}
            InputProps={{
              startAdornment: (
                <InputAdornment position="start">
                  <SearchIcon sx={{ color: alpha(theme.palette.text.secondary, 0.5) }} />
                </InputAdornment>
              ),
              endAdornment: filterQuery && (
                <InputAdornment position="end">
                  <IconButton
                    size="small"
                    onClick={() => setFilterQuery('')}
                    sx={{ color: alpha(theme.palette.text.secondary, 0.5) }}
                  >
                    <CloseIcon fontSize="small" />
                  </IconButton>
                </InputAdornment>
              ),
            }}
            sx={{
              '& .MuiOutlinedInput-root': {
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
            }}
          />

          {/* Filter Toggles */}
          <Box sx={{ display: 'flex', justifyContent: 'center' }}>
            <ToggleButtonGroup
              value={activeFilter}
              exclusive
              onChange={(_, newFilter) => newFilter && setActiveFilter(newFilter)}
              aria-label="MCP filter"
              sx={{
                '& .MuiToggleButton-root': {
                  color: alpha(theme.palette.text.secondary, 0.7),
                  borderColor: alpha(theme.palette.divider, 0.1),
                  textTransform: 'none',
                  fontWeight: 500,
                  px: 3,
                  py: 1,
                  borderRadius: 2,
                  '&:hover': {
                    backgroundColor: alpha(theme.palette.primary.main, 0.1),
                    borderColor: alpha(theme.palette.primary.main, 0.3),
                  },
                  '&.Mui-selected': {
                    background: `linear-gradient(135deg, ${alpha(theme.palette.primary.main, 0.2)}, ${alpha(theme.palette.primary.main, 0.1)})`,
                    color: theme.palette.primary.main,
                    borderColor: alpha(theme.palette.primary.main, 0.5),
                    fontWeight: 600,
                    '&:hover': {
                      background: `linear-gradient(135deg, ${alpha(theme.palette.primary.main, 0.3)}, ${alpha(theme.palette.primary.main, 0.15)})`,
                    },
                  },
                },
              }}
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
        </Stack>
      </Paper>

      {/* MCP Configs Grid */}
      <Grid container spacing={3}>
        {filteredConfigs.length === 0 ? (
          <Grid item xs={12}>
            <Paper
              sx={{
                p: 6,
                textAlign: 'center',
                borderRadius: 2,
                background: alpha(theme.palette.background.paper, 0.4),
                border: `1px solid ${alpha(theme.palette.divider, 0.1)}`,
              }}
            >
              <CloudIcon
                sx={{
                  fontSize: 64,
                  color: alpha(theme.palette.text.secondary, 0.3),
                  mb: 2,
                }}
              />
              <Typography
                variant="h6"
                sx={{
                  color: alpha(theme.palette.text.secondary, 0.7),
                  mb: 1,
                }}
              >
                {activeFilter === 'all' && 'No MCP configs available'}
                {activeFilter === 'default' && 'No default MCP configs available'}
                {activeFilter === 'custom' && 'No custom MCP configs created yet'}
                {activeFilter === 'favorite' && 'No favorite MCP configs yet'}
                {activeFilter === 'enabled' && 'No MCP configs enabled yet'}
              </Typography>
              <Typography
                variant="body2"
                sx={{
                  color: alpha(theme.palette.text.secondary, 0.5),
                }}
              >
                {activeFilter === 'custom' && 'Click "Add MCP" to create your own custom configuration'}
                {activeFilter === 'favorite' && 'Add MCP servers to favorites by clicking the star icon'}
                {activeFilter === 'enabled' && 'Enable configs by toggling the switch on any MCP card'}
              </Typography>
            </Paper>
          </Grid>
        ) : (
          filteredConfigs.map((config) => (
            <Grid item xs={12} md={6} lg={4} key={`${config.mcp_config_type}-${config.id}`}>
              <MCPConfigCard
                config={config}
                showToggle={true}
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
        PaperProps={{
          sx: {
            backgroundColor: '#1e293b',
            backgroundImage: 'none',
            border: '1px solid #334155',
          }
        }}
      >
        <DialogTitle sx={{ color: '#e2e8f0' }}>Add Custom MCP Server</DialogTitle>
        <DialogContent>
          <Alert
            severity="info"
            sx={{
              mb: 2,
              backgroundColor: 'rgba(59, 130, 246, 0.1)',
              border: '1px solid rgba(59, 130, 246, 0.3)',
              color: '#60a5fa',
              '& .MuiAlert-icon': { color: '#60a5fa' }
            }}
          >
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
            sx={{
              mb: 2,
              '& .MuiOutlinedInput-root': {
                color: '#e2e8f0',
                backgroundColor: '#0f172a',
                '& fieldset': { borderColor: '#334155' },
                '&:hover fieldset': { borderColor: '#475569' },
                '&.Mui-focused fieldset': { borderColor: '#6366f1' }
              },
              '& .MuiInputLabel-root': {
                color: '#94a3b8',
                '&.Mui-focused': { color: '#6366f1' }
              },
              '& .MuiFormHelperText-root': {
                color: '#64748b'
              }
            }}
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
            sx={{
              mb: 2,
              '& .MuiOutlinedInput-root': {
                color: '#e2e8f0',
                backgroundColor: '#0f172a',
                '& fieldset': { borderColor: '#334155' },
                '&:hover fieldset': { borderColor: '#475569' },
                '&.Mui-focused fieldset': { borderColor: '#6366f1' }
              },
              '& .MuiInputLabel-root': {
                color: '#94a3b8',
                '&.Mui-focused': { color: '#6366f1' }
              },
              '& .MuiFormHelperText-root': {
                color: '#64748b'
              }
            }}
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
            sx={{
              mb: 2,
              '& .MuiOutlinedInput-root': {
                color: '#e2e8f0',
                backgroundColor: '#0f172a',
                '& fieldset': { borderColor: '#334155' },
                '&:hover fieldset': { borderColor: '#475569' },
                '&.Mui-focused fieldset': { borderColor: '#6366f1' }
              },
              '& .MuiInputLabel-root': {
                color: '#94a3b8',
                '&.Mui-focused': { color: '#6366f1' }
              },
              '& .MuiFormHelperText-root': {
                color: '#64748b'
              }
            }}
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
            sx={{
              fontFamily: 'monospace',
              '& .MuiOutlinedInput-root': {
                color: '#e2e8f0',
                backgroundColor: '#0f172a',
                fontFamily: 'monospace',
                '& fieldset': { borderColor: '#334155' },
                '&:hover fieldset': { borderColor: '#475569' },
                '&.Mui-focused fieldset': { borderColor: '#6366f1' }
              },
              '& .MuiInputLabel-root': {
                color: '#94a3b8',
                '&.Mui-focused': { color: '#6366f1' }
              },
              '& .MuiFormHelperText-root': {
                color: '#64748b'
              }
            }}
          />
        </DialogContent>
        <DialogActions>
          <Button
            onClick={() => setCreateDialogOpen(false)}
            disabled={creating}
            sx={{
              color: '#94a3b8',
              textTransform: 'none',
              fontWeight: 500,
              '&:hover': { backgroundColor: 'rgba(148, 163, 184, 0.1)' }
            }}
          >
            Cancel
          </Button>
          <Button
            onClick={handleCreateConfig}
            variant="contained"
            disabled={!newConfigName || !newConfigDescription || !newConfigJson || creating}
            sx={{
              backgroundColor: '#6366f1',
              color: '#ffffff',
              fontWeight: 600,
              textTransform: 'none',
              '&:hover': { backgroundColor: '#4f46e5' },
              '&:disabled': { backgroundColor: '#334155', color: '#64748b' }
            }}
          >
            {creating ? <CircularProgress size={24} sx={{ color: '#ffffff' }} /> : 'Create'}
          </Button>
        </DialogActions>
      </Dialog>

      {/* View Config Dialog */}
      <Dialog
        open={viewConfigDialogOpen}
        onClose={() => setViewConfigDialogOpen(false)}
        maxWidth="md"
        fullWidth
        PaperProps={{
          sx: {
            backgroundColor: '#1e293b',
            backgroundImage: 'none',
            border: '1px solid #334155',
          }
        }}
      >
        <DialogTitle sx={{ color: '#e2e8f0' }}>MCP Configuration: {selectedConfig?.name}</DialogTitle>
        <DialogContent>
          <Typography variant="body2" sx={{ color: '#94a3b8', mb: 2 }}>
            {selectedConfig?.description}
          </Typography>
          <Box sx={{ mb: 2 }}>
            <Chip
              label={selectedConfig?.category}
              size="small"
              sx={{
                mr: 1,
                borderColor: '#6366f1',
                color: '#6366f1',
                backgroundColor: 'rgba(99, 102, 241, 0.1)',
              }}
            />
            <Chip
              label={selectedConfig?.mcp_config_type}
              size="small"
              variant="outlined"
              sx={{
                borderColor: '#334155',
                color: '#94a3b8',
                backgroundColor: 'rgba(51, 65, 85, 0.3)',
              }}
            />
          </Box>
          <Typography variant="subtitle2" gutterBottom sx={{ color: '#e2e8f0', fontWeight: 600 }}>
            Configuration JSON:
          </Typography>
          <Box
            sx={{
              bgcolor: '#0f172a',
              border: '1px solid #334155',
              p: 2,
              borderRadius: 1,
              fontFamily: 'monospace',
              fontSize: '0.875rem',
              overflow: 'auto',
              maxHeight: '400px',
            }}
          >
            <pre style={{ margin: 0, color: '#e2e8f0' }}>
              {JSON.stringify(selectedConfig?.config, null, 2)}
            </pre>
          </Box>
        </DialogContent>
        <DialogActions>
          <Button
            onClick={() => setViewConfigDialogOpen(false)}
            sx={{
              color: '#94a3b8',
              textTransform: 'none',
              fontWeight: 500,
              '&:hover': { backgroundColor: 'rgba(148, 163, 184, 0.1)' }
            }}
          >
            Close
          </Button>
        </DialogActions>
      </Dialog>

      {/* MCP Search Dialog */}
      <Dialog
        open={searchDialogOpen}
        onClose={() => setSearchDialogOpen(false)}
        maxWidth="md"
        fullWidth
        PaperProps={{
          sx: {
            backgroundColor: '#1e293b',
            backgroundImage: 'none',
            border: '1px solid #334155',
          }
        }}
      >
        <DialogTitle sx={{ color: '#e2e8f0' }}>Search MCP Servers from mcp.so</DialogTitle>
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
              sx={{
                '& .MuiOutlinedInput-root': {
                  color: '#e2e8f0',
                  backgroundColor: '#0f172a',
                  '& fieldset': { borderColor: '#334155' },
                  '&:hover fieldset': { borderColor: '#475569' },
                  '&.Mui-focused fieldset': { borderColor: '#6366f1' }
                }
              }}
              InputProps={{
                startAdornment: (
                  <InputAdornment position="start">
                    <SearchIcon sx={{ color: '#94a3b8' }} />
                  </InputAdornment>
                ),
                endAdornment: (
                  <InputAdornment position="end">
                    <Button
                      onClick={handleSearchMCP}
                      disabled={!searchQuery.trim() || searching}
                      sx={{
                        color: '#94a3b8',
                        textTransform: 'none',
                        fontWeight: 500,
                        '&:hover': { backgroundColor: 'rgba(99, 102, 241, 0.1)', color: '#6366f1' },
                        '&:disabled': { color: '#64748b' }
                      }}
                    >
                      {searching ? <CircularProgress size={20} sx={{ color: '#6366f1' }} /> : 'Search'}
                    </Button>
                  </InputAdornment>
                ),
              }}
            />
          </Box>

          {searchError && (
            <Alert
              severity="error"
              sx={{
                mb: 2,
                backgroundColor: 'rgba(239, 68, 68, 0.1)',
                border: '1px solid rgba(239, 68, 68, 0.3)',
                color: '#f87171',
                '& .MuiAlert-icon': { color: '#f87171' }
              }}
              onClose={() => setSearchError(null)}
            >
              {searchError}
            </Alert>
          )}

          {searching && (
            <Box display="flex" justifyContent="center" p={4}>
              <CircularProgress sx={{ color: '#6366f1' }} />
            </Box>
          )}

          {!searching && searchResults.length > 0 && (
            <>
              <Typography variant="subtitle2" gutterBottom sx={{ mt: 2, color: '#e2e8f0', fontWeight: 600 }}>
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
                        backgroundColor: '#0f172a',
                        border: '1px solid #334155',
                        '&:hover': {
                          borderColor: '#6366f1',
                          transform: 'translateY(-4px)',
                          transition: 'all 0.3s ease-in-out',
                          boxShadow: '0 10px 15px -3px rgba(99, 102, 241, 0.1), 0 4px 6px -2px rgba(99, 102, 241, 0.05)'
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
                            <Typography variant="h6" component="div" noWrap sx={{ color: '#e2e8f0', fontWeight: 600 }}>
                              {server.title || server.name}
                            </Typography>
                            {server.author_name && (
                              <Typography variant="caption" sx={{ color: '#94a3b8' }}>
                                by {server.author_name}
                              </Typography>
                            )}
                          </Box>
                        </Box>
                        <CardContent sx={{ pt: 0, width: '100%', flex: 1 }}>
                          <Typography variant="body2" sx={{
                            color: '#94a3b8',
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
            <Alert
              severity="info"
              sx={{
                backgroundColor: 'rgba(59, 130, 246, 0.1)',
                border: '1px solid rgba(59, 130, 246, 0.3)',
                color: '#60a5fa',
                '& .MuiAlert-icon': { color: '#60a5fa' }
              }}
            >
              No results found. Try a different search term.
            </Alert>
          )}
        </DialogContent>
        <DialogActions>
          <Button
            onClick={() => setSearchDialogOpen(false)}
            sx={{
              color: '#94a3b8',
              textTransform: 'none',
              fontWeight: 500,
              '&:hover': { backgroundColor: 'rgba(148, 163, 184, 0.1)' }
            }}
          >
            Close
          </Button>
        </DialogActions>
      </Dialog>

      {/* GitHub Info Dialog - shown when config not found */}
      <Dialog
        open={githubInfoDialogOpen}
        onClose={() => setGithubInfoDialogOpen(false)}
        maxWidth="sm"
        fullWidth
        PaperProps={{
          sx: {
            backgroundColor: '#1e293b',
            backgroundImage: 'none',
            border: '1px solid #334155',
          }
        }}
      >
        <DialogTitle sx={{ color: '#e2e8f0' }}>MCP Configuration Not Found</DialogTitle>
        <DialogContent>
          {selectedServerInfo && (
            <Card
              sx={{
                mt: 2,
                backgroundColor: '#0f172a',
                border: '1px solid #334155',
              }}
            >
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
                    <Typography variant="h6" sx={{ color: '#e2e8f0', fontWeight: 600 }}>
                      {selectedServerInfo.title || selectedServerInfo.name}
                    </Typography>
                    {selectedServerInfo.author_name && (
                      <Typography variant="body2" sx={{ color: '#94a3b8' }}>
                        by {selectedServerInfo.author_name}
                      </Typography>
                    )}
                  </Box>
                </Box>

                <Typography variant="body2" sx={{ color: '#94a3b8', mb: 2 }}>
                  {selectedServerInfo.description}
                </Typography>

                <Alert
                  severity="info"
                  sx={{
                    mb: 2,
                    backgroundColor: 'rgba(59, 130, 246, 0.1)',
                    border: '1px solid rgba(59, 130, 246, 0.3)',
                    color: '#60a5fa',
                    '& .MuiAlert-icon': { color: '#60a5fa' }
                  }}
                >
                  Configuration not available. Please visit the GitHub repository to find installation instructions and configuration details.
                </Alert>

                {selectedServerInfo.github_url && (
                  <Button
                    variant="contained"
                    color="primary"
                    fullWidth
                    startIcon={<CodeIcon />}
                    onClick={() => window.open(selectedServerInfo.github_url, '_blank')}
                    sx={{
                      backgroundColor: '#6366f1',
                      color: '#ffffff',
                      fontWeight: 600,
                      textTransform: 'none',
                      '&:hover': { backgroundColor: '#4f46e5' }
                    }}
                  >
                    Open GitHub Repository
                  </Button>
                )}
              </CardContent>
            </Card>
          )}
        </DialogContent>
        <DialogActions>
          <Button
            onClick={() => setGithubInfoDialogOpen(false)}
            sx={{
              color: '#94a3b8',
              textTransform: 'none',
              fontWeight: 500,
              '&:hover': { backgroundColor: 'rgba(148, 163, 184, 0.1)' }
            }}
          >
            Close
          </Button>
          <Button
            variant="outlined"
            onClick={() => {
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
            sx={{
              color: '#94a3b8',
              border: '1px solid #334155',
              textTransform: 'none',
              fontWeight: 500,
              '&:hover': {
                backgroundColor: 'rgba(99, 102, 241, 0.1)',
                borderColor: '#6366f1',
                color: '#6366f1',
              }
            }}
          >
            Configure Manually
          </Button>
        </DialogActions>
      </Dialog>
    </Container>
  );
};

export default MCPConfigs;
