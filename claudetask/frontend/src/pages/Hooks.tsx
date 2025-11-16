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
  Stack,
  Container,
  alpha,
  useTheme,
  Divider,
  InputAdornment,
  Paper,
  MenuItem,
  Select,
  FormControl,
  InputLabel,
} from '@mui/material';
import AddIcon from '@mui/icons-material/Add';
import DeleteIcon from '@mui/icons-material/Delete';
import EditIcon from '@mui/icons-material/Edit';
import StarIcon from '@mui/icons-material/Star';
import StarBorderIcon from '@mui/icons-material/StarBorder';
import HooksIcon from '@mui/icons-material/Webhook';
import SearchIcon from '@mui/icons-material/Search';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import CategoryIcon from '@mui/icons-material/Category';
import CodeIcon from '@mui/icons-material/Code';
import PlayArrowIcon from '@mui/icons-material/PlayArrow';
import InfoIcon from '@mui/icons-material/Info';
import CloseIcon from '@mui/icons-material/Close';
import axios from 'axios';
import { useProject } from '../context/ProjectContext';

// Remove /api suffix if present, since we add it manually in request paths
const API_BASE_URL = (process.env.REACT_APP_API_URL || 'http://localhost:3333').replace(/\/api$/, '');

interface Hook {
  id: number;
  name: string;
  description: string;
  hook_type: 'default' | 'custom';
  category: string;
  hook_config: object;
  setup_instructions?: string;
  dependencies?: string[];
  is_enabled: boolean;
  is_favorite: boolean;
  status?: string;
  created_by?: string;
  created_at: string;
  updated_at: string;
}

interface HooksResponse {
  enabled: Hook[];
  available_default: Hook[];
  custom: Hook[];
  favorites: Hook[];
}

type FilterType = 'all' | 'default' | 'custom' | 'favorite' | 'enabled';

// Category colors
const getCategoryColor = (category: string) => {
  const categoryMap: { [key: string]: string } = {
    logging: '#3B82F6',
    formatting: '#8B5CF6',
    notifications: '#F59E0B',
    security: '#EF4444',
    'version-control': '#10B981',
  };
  return categoryMap[category] || '#6B7280';
};

const Hooks: React.FC = () => {
  const theme = useTheme();
  const { selectedProject } = useProject();
  const [activeFilter, setActiveFilter] = useState<FilterType>('all');
  const [searchQuery, setSearchQuery] = useState('');
  const [hooks, setHooks] = useState<HooksResponse>({
    enabled: [],
    available_default: [],
    custom: [],
    favorites: [],
  });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [createDialogOpen, setCreateDialogOpen] = useState(false);
  const [editDialogOpen, setEditDialogOpen] = useState(false);
  const [viewDialogOpen, setViewDialogOpen] = useState(false);
  const [selectedHook, setSelectedHook] = useState<Hook | null>(null);
  const [editingHook, setEditingHook] = useState<Hook | null>(null);
  const [newHook, setNewHook] = useState({
    name: '',
    description: '',
    category: 'logging',
    hook_config: '{}',
    setup_instructions: '',
    dependencies: '',
  });
  const [editedHook, setEditedHook] = useState({
    name: '',
    description: '',
    category: 'logging',
    hook_config: '{}',
    setup_instructions: '',
    dependencies: '',
  });
  const [creating, setCreating] = useState(false);
  const [editing, setEditing] = useState(false);

  // Fetch hooks when project changes
  useEffect(() => {
    if (selectedProject?.id) {
      fetchHooks();
    }
  }, [selectedProject?.id]);

  const fetchHooks = async () => {
    if (!selectedProject?.id) return;

    setLoading(true);
    setError(null);
    try {
      const response = await axios.get<HooksResponse>(
        `${API_BASE_URL}/api/projects/${selectedProject.id}/hooks/?t=${Date.now()}`,
        {
          headers: {
            'Cache-Control': 'no-cache',
            'Pragma': 'no-cache'
          }
        }
      );
      setHooks(response.data);
    } catch (err: any) {
      setError('Failed to fetch hooks: ' + (err.response?.data?.detail || err.message));
    } finally {
      setLoading(false);
    }
  };

  const handleEnableHook = async (hookId: number) => {
    if (!selectedProject?.id) return;

    try {
      await axios.post(
        `${API_BASE_URL}/api/projects/${selectedProject.id}/hooks/enable/${hookId}`
      );
      await fetchHooks();
    } catch (err: any) {
      setError('Failed to enable hook: ' + (err.response?.data?.detail || err.message));
    }
  };

  const handleDisableHook = async (hookId: number) => {
    if (!selectedProject?.id) return;

    try {
      await axios.post(
        `${API_BASE_URL}/api/projects/${selectedProject.id}/hooks/disable/${hookId}`
      );
      await fetchHooks();
    } catch (err: any) {
      setError('Failed to disable hook: ' + (err.response?.data?.detail || err.message));
    }
  };

  const handleCreateHook = async () => {
    if (!selectedProject?.id) return;

    setCreating(true);
    setError(null);
    try {
      // Validate JSON config
      let configObj;
      try {
        configObj = JSON.parse(newHook.hook_config);
      } catch (e) {
        setError('Invalid JSON in hook configuration');
        setCreating(false);
        return;
      }

      // Parse dependencies
      const dependenciesArray = newHook.dependencies
        ? newHook.dependencies.split(',').map(d => d.trim()).filter(d => d)
        : [];

      await axios.post(
        `${API_BASE_URL}/api/projects/${selectedProject.id}/hooks/create`,
        {
          name: newHook.name,
          description: newHook.description,
          category: newHook.category,
          hook_config: configObj,
          setup_instructions: newHook.setup_instructions || undefined,
          dependencies: dependenciesArray.length > 0 ? dependenciesArray : undefined,
        }
      );
      setCreateDialogOpen(false);
      setNewHook({
        name: '',
        description: '',
        category: 'logging',
        hook_config: '{}',
        setup_instructions: '',
        dependencies: '',
      });
      await fetchHooks();
    } catch (err: any) {
      setError('Failed to create hook: ' + (err.response?.data?.detail || err.message));
    } finally {
      setCreating(false);
    }
  };

  const handleDeleteHook = async (hookId: number) => {
    if (!selectedProject?.id) return;
    if (!window.confirm('Are you sure you want to delete this custom hook?')) return;

    try {
      await axios.delete(
        `${API_BASE_URL}/api/projects/${selectedProject.id}/hooks/${hookId}`
      );
      await fetchHooks();
    } catch (err: any) {
      setError('Failed to delete hook: ' + (err.response?.data?.detail || err.message));
    }
  };

  const handleSaveToFavorites = async (hookId: number, hookType: string) => {
    if (!selectedProject?.id) return;

    try {
      await axios.post(
        `${API_BASE_URL}/api/projects/${selectedProject.id}/hooks/favorites/save`,
        null,
        {
          params: {
            hook_id: hookId,
            hook_type: hookType,
          },
        }
      );
      await fetchHooks();
    } catch (err: any) {
      setError('Failed to save to favorites: ' + (err.response?.data?.detail || err.message));
    }
  };

  const handleRemoveFromFavorites = async (hookId: number, hookType: string) => {
    if (!selectedProject?.id) return;

    try {
      await axios.post(
        `${API_BASE_URL}/api/projects/${selectedProject.id}/hooks/favorites/remove`,
        null,
        {
          params: {
            hook_id: hookId,
            hook_type: hookType,
          },
        }
      );
      await fetchHooks();
    } catch (err: any) {
      setError('Failed to remove from favorites: ' + (err.response?.data?.detail || err.message));
    }
  };

  const openEditDialog = (hook: Hook) => {
    setEditingHook(hook);
    setEditedHook({
      name: hook.name,
      description: hook.description,
      category: hook.category,
      hook_config: JSON.stringify(hook.hook_config, null, 2),
      setup_instructions: hook.setup_instructions || '',
      dependencies: hook.dependencies?.join(', ') || '',
    });
    setEditDialogOpen(true);
  };

  const handleEditHook = async () => {
    if (!selectedProject?.id || !editingHook) return;

    setEditing(true);
    setError(null);
    try {
      // Validate JSON config
      let configObj;
      try {
        configObj = JSON.parse(editedHook.hook_config);
      } catch (e) {
        setError('Invalid JSON in hook configuration');
        setEditing(false);
        return;
      }

      // Parse dependencies
      const dependenciesArray = editedHook.dependencies
        ? editedHook.dependencies.split(',').map(d => d.trim()).filter(d => d)
        : [];

      await axios.put(
        `${API_BASE_URL}/api/projects/${selectedProject.id}/hooks/${editingHook.id}`,
        {
          name: editedHook.name,
          description: editedHook.description,
          category: editedHook.category,
          hook_config: configObj,
          setup_instructions: editedHook.setup_instructions || undefined,
          dependencies: dependenciesArray.length > 0 ? dependenciesArray : undefined,
        }
      );
      setEditDialogOpen(false);
      setEditingHook(null);
      await fetchHooks();
    } catch (err: any) {
      setError('Failed to edit hook: ' + (err.response?.data?.detail || err.message));
    } finally {
      setEditing(false);
    }
  };

  // Filter hooks based on active filter and search query
  const getFilteredHooks = (): Hook[] => {
    let filtered: Hook[] = [];

    switch (activeFilter) {
      case 'default':
        filtered = hooks.available_default;
        break;
      case 'custom':
        filtered = hooks.custom;
        break;
      case 'favorite':
        filtered = hooks.favorites;
        break;
      case 'enabled':
        filtered = hooks.enabled;
        break;
      case 'all':
      default:
        const allHooks = [
          ...hooks.available_default,
          ...hooks.custom,
        ];
        filtered = allHooks.filter(
          (hook, index, self) => self.findIndex(h => h.id === hook.id && h.hook_type === hook.hook_type) === index
        );
    }

    // Apply search filter
    if (searchQuery.trim()) {
      const query = searchQuery.toLowerCase();
      filtered = filtered.filter(
        (hook) =>
          hook.name.toLowerCase().includes(query) ||
          hook.description.toLowerCase().includes(query) ||
          hook.category.toLowerCase().includes(query)
      );
    }

    return filtered;
  };

  const filteredHooks = getFilteredHooks();

  // Statistics
  const stats = {
    total: hooks.available_default.length + hooks.custom.length,
    enabled: hooks.enabled.length,
    favorites: hooks.favorites.length,
    custom: hooks.custom.length,
  };

  const HookCard: React.FC<{
    hook: Hook;
    showToggle?: boolean;
    showDelete?: boolean;
    showSaveToFavorites?: boolean;
    showRemoveFromFavorites?: boolean;
  }> = ({
    hook,
    showToggle = false,
    showDelete = false,
    showSaveToFavorites = false,
    showRemoveFromFavorites = false,
  }) => {
    // Check if hook data is valid
    if (!hook || !hook.name) {
      return null;
    }

    const categoryColor = getCategoryColor(hook.category);

    return (
      <Card
        sx={{
          height: '100%',
          display: 'flex',
          flexDirection: 'column',
          position: 'relative',
          overflow: 'visible',
          background: theme.palette.mode === 'dark'
            ? `linear-gradient(145deg, ${alpha(theme.palette.background.paper, 0.9)}, ${alpha(theme.palette.background.paper, 0.95)})`
            : theme.palette.background.paper,
          border: `1px solid ${alpha(theme.palette.primary.main, 0.1)}`,
          transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
          '&:hover': {
            transform: 'translateY(-4px)',
            boxShadow: theme.palette.mode === 'dark'
              ? `0 12px 24px -6px ${alpha(theme.palette.primary.main, 0.3)}`
              : `0 12px 24px -6px ${alpha(theme.palette.primary.main, 0.15)}`,
            border: `1px solid ${alpha(theme.palette.primary.main, 0.3)}`,
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
            background: hook.is_enabled
              ? `linear-gradient(90deg, ${theme.palette.success.main}, ${theme.palette.success.light})`
              : `linear-gradient(90deg, ${theme.palette.grey[600]}, ${theme.palette.grey[400]})`,
            borderTopLeftRadius: 12,
            borderTopRightRadius: 12,
          }}
        />

        <CardContent sx={{ flexGrow: 1, pt: 3 }}>
          {/* Header with icon and actions */}
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
                  background: `linear-gradient(135deg, ${alpha(categoryColor, 0.2)}, ${alpha(categoryColor, 0.1)})`,
                  border: `1px solid ${alpha(categoryColor, 0.2)}`,
                }}
              >
                <HooksIcon sx={{ color: categoryColor, fontSize: 28 }} />
              </Box>
              <Box flexGrow={1}>
                <Typography
                  variant="h6"
                  component="div"
                  sx={{
                    fontWeight: 600,
                    fontSize: '1.1rem',
                    mb: 0.5,
                    display: 'flex',
                    alignItems: 'center',
                    gap: 1,
                  }}
                >
                  {hook.name}
                  {hook.is_enabled && (
                    <Tooltip title="Enabled">
                      <CheckCircleIcon sx={{ fontSize: 18, color: theme.palette.success.main }} />
                    </Tooltip>
                  )}
                </Typography>
                <Stack direction="row" spacing={0.5} flexWrap="wrap">
                  <Chip
                    label={hook.category}
                    size="small"
                    icon={<CategoryIcon sx={{ fontSize: 14 }} />}
                    sx={{
                      height: 22,
                      fontSize: '0.7rem',
                      fontWeight: 500,
                      background: `linear-gradient(135deg, ${alpha(categoryColor, 0.15)}, ${alpha(categoryColor, 0.05)})`,
                      border: `1px solid ${alpha(categoryColor, 0.2)}`,
                      color: categoryColor,
                    }}
                  />
                  <Chip
                    label={hook.hook_type === 'default' ? 'Default' : 'Custom'}
                    size="small"
                    sx={{
                      height: 22,
                      fontSize: '0.7rem',
                      fontWeight: 500,
                      background: hook.hook_type === 'default'
                        ? `linear-gradient(135deg, ${alpha(theme.palette.success.main, 0.15)}, ${alpha(theme.palette.success.main, 0.05)})`
                        : `linear-gradient(135deg, ${alpha(theme.palette.info.main, 0.15)}, ${alpha(theme.palette.info.main, 0.05)})`,
                      border: `1px solid ${alpha(
                        hook.hook_type === 'default' ? theme.palette.success.main : theme.palette.info.main,
                        0.2
                      )}`,
                      color: hook.hook_type === 'default' ? theme.palette.success.main : theme.palette.info.main,
                    }}
                  />
                </Stack>
              </Box>
            </Box>

            {/* Action buttons */}
            <Stack direction="row" spacing={0.5}>
              {showSaveToFavorites && (
                <Tooltip title="Add to Favorites">
                  <IconButton
                    size="small"
                    onClick={() => handleSaveToFavorites(hook.id, hook.hook_type)}
                    sx={{
                      color: theme.palette.warning.main,
                      '&:hover': {
                        background: alpha(theme.palette.warning.main, 0.1),
                      },
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
                    onClick={() => handleRemoveFromFavorites(hook.id, hook.hook_type)}
                    sx={{
                      color: theme.palette.warning.main,
                      '&:hover': {
                        background: alpha(theme.palette.warning.main, 0.1),
                      },
                    }}
                  >
                    <StarIcon fontSize="small" />
                  </IconButton>
                </Tooltip>
              )}
              <Tooltip title="Edit hook">
                <IconButton
                  size="small"
                  onClick={() => openEditDialog(hook)}
                  sx={{
                    color: theme.palette.primary.main,
                    '&:hover': {
                      background: alpha(theme.palette.primary.main, 0.1),
                    },
                  }}
                >
                  <EditIcon fontSize="small" />
                </IconButton>
              </Tooltip>
              {showDelete && hook.hook_type === 'custom' && (
                <Tooltip title="Delete custom hook">
                  <IconButton
                    size="small"
                    onClick={() => handleDeleteHook(hook.id)}
                    sx={{
                      color: theme.palette.error.main,
                      '&:hover': {
                        background: alpha(theme.palette.error.main, 0.1),
                      },
                    }}
                  >
                    <DeleteIcon fontSize="small" />
                  </IconButton>
                </Tooltip>
              )}
              <Tooltip title="View details">
                <IconButton
                  size="small"
                  onClick={() => {
                    setSelectedHook(hook);
                    setViewDialogOpen(true);
                  }}
                  sx={{
                    color: theme.palette.info.main,
                    '&:hover': {
                      background: alpha(theme.palette.info.main, 0.1),
                    },
                  }}
                >
                  <InfoIcon fontSize="small" />
                </IconButton>
              </Tooltip>
            </Stack>
          </Box>

          {/* Description */}
          <Typography
            variant="body2"
            color="text.secondary"
            sx={{
              mb: 2,
              lineHeight: 1.6,
              display: '-webkit-box',
              WebkitLineClamp: 3,
              WebkitBoxOrient: 'vertical',
              overflow: 'hidden',
            }}
          >
            {hook.description}
          </Typography>

          <Divider sx={{ my: 2 }} />

          {/* Command Preview */}
          <Box mb={2}>
            <Typography variant="caption" color="text.secondary" display="block" mb={0.5}>
              Configuration:
            </Typography>
            <Box
              sx={{
                p: 1.5,
                bgcolor: theme.palette.mode === 'dark' ? alpha(theme.palette.background.default, 0.5) : alpha(theme.palette.grey[100], 0.8),
                borderRadius: 1,
                fontFamily: 'monospace',
                fontSize: '0.7rem',
                border: `1px solid ${alpha(theme.palette.divider, 0.1)}`,
                maxHeight: 80,
                overflow: 'hidden',
                position: 'relative',
                '&::after': {
                  content: '""',
                  position: 'absolute',
                  bottom: 0,
                  left: 0,
                  right: 0,
                  height: 30,
                  background: `linear-gradient(transparent, ${theme.palette.mode === 'dark' ? alpha(theme.palette.background.default, 0.9) : alpha(theme.palette.grey[100], 0.9)})`,
                },
              }}
            >
              <code>{JSON.stringify(hook.hook_config, null, 2)}</code>
            </Box>
          </Box>

          {/* Dependencies */}
          {hook.dependencies && hook.dependencies.length > 0 && (
            <Box mb={2}>
              <Typography variant="caption" color="text.secondary" display="block" mb={0.5}>
                Dependencies:
              </Typography>
              <Stack direction="row" spacing={0.5} flexWrap="wrap" useFlexGap>
                {hook.dependencies.map((dep, idx) => (
                  <Chip
                    key={idx}
                    label={dep}
                    size="small"
                    variant="outlined"
                    sx={{
                      height: 20,
                      fontSize: '0.65rem',
                      borderColor: alpha(theme.palette.text.secondary, 0.2),
                    }}
                  />
                ))}
              </Stack>
            </Box>
          )}

          {/* Toggle switch */}
          {showToggle && (
            <Box mt={2}>
              <FormControlLabel
                control={
                  <Switch
                    checked={hook.is_enabled}
                    onChange={(e) => {
                      if (e.target.checked) {
                        handleEnableHook(hook.id);
                      } else {
                        handleDisableHook(hook.id);
                      }
                    }}
                    disabled={hook.status === 'creating'}
                    color="primary"
                  />
                }
                label={
                  <Typography variant="body2" fontWeight={500}>
                    {hook.is_enabled ? 'Enabled' : 'Disabled'}
                  </Typography>
                }
              />
            </Box>
          )}
        </CardContent>
      </Card>
    );
  };

  return (
    <Box sx={{ minHeight: '100vh', pb: 4 }}>
      <Container maxWidth="xl">
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
                Hooks Management
              </Typography>
              <Typography variant="body1" color="text.secondary">
                Manage lifecycle hooks and automation for your project
              </Typography>
            </Box>
            <Button
              variant="contained"
              size="large"
              startIcon={<AddIcon />}
              onClick={() => setCreateDialogOpen(true)}
              disabled={!selectedProject?.id}
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
              Create Custom Hook
            </Button>
          </Stack>

          {/* Statistics Cards */}
          <Grid container spacing={2} mb={3}>
            {[
              { label: 'Total Hooks', value: stats.total, color: theme.palette.primary.main },
              { label: 'Enabled', value: stats.enabled, color: theme.palette.success.main },
              { label: 'Favorites', value: stats.favorites, color: theme.palette.warning.main },
              { label: 'Custom', value: stats.custom, color: theme.palette.info.main },
            ].map((stat) => (
              <Grid item xs={12} sm={6} md={3} key={stat.label}>
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
                  <Typography variant="body2" color="text.secondary" gutterBottom>
                    {stat.label}
                  </Typography>
                  <Typography variant="h3" sx={{ fontWeight: 700, color: stat.color }}>
                    {stat.value}
                  </Typography>
                </Paper>
              </Grid>
            ))}
          </Grid>

          {error && (
            <Alert severity="error" sx={{ mb: 3, borderRadius: 2 }} onClose={() => setError(null)}>
              {error}
            </Alert>
          )}

          {!selectedProject?.id && (
            <Alert severity="warning" sx={{ mb: 3, borderRadius: 2 }}>
              No active project found. Please go to Projects and activate a project first.
            </Alert>
          )}

          {/* Search and Filter Bar */}
          <Paper
            sx={{
              p: 3,
              mb: 3,
              borderRadius: 2,
              background: alpha(theme.palette.background.paper, 0.6),
              border: `1px solid ${alpha(theme.palette.divider, 0.1)}`,
            }}
          >
            <Stack spacing={3}>
              {/* Search */}
              <TextField
                fullWidth
                placeholder="Search hooks by name, description, or category..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                InputProps={{
                  startAdornment: (
                    <InputAdornment position="start">
                      <SearchIcon sx={{ color: alpha(theme.palette.text.secondary, 0.5) }} />
                    </InputAdornment>
                  ),
                  endAdornment: searchQuery && (
                    <InputAdornment position="end">
                      <IconButton
                        size="small"
                        onClick={() => setSearchQuery('')}
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
                  aria-label="hook filter"
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
                    All ({stats.total})
                  </ToggleButton>
                  <ToggleButton value="default" aria-label="default">
                    Default ({hooks.available_default.length})
                  </ToggleButton>
                  <ToggleButton value="custom" aria-label="custom">
                    Custom ({stats.custom})
                  </ToggleButton>
                  <ToggleButton value="favorite" aria-label="favorite">
                    Favorites ({stats.favorites})
                  </ToggleButton>
                  <ToggleButton value="enabled" aria-label="enabled">
                    Enabled ({stats.enabled})
                  </ToggleButton>
                </ToggleButtonGroup>
              </Box>
            </Stack>
          </Paper>
        </Box>

        {/* Hooks Grid */}
        {loading ? (
          <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
            <CircularProgress size={48} />
          </Box>
        ) : (
          <Grid container spacing={3}>
            {filteredHooks.length === 0 ? (
              <Grid item xs={12}>
                <Paper
                  sx={{
                    p: 6,
                    textAlign: 'center',
                    borderRadius: 2,
                    background: alpha(theme.palette.background.paper, 0.5),
                  }}
                >
                  <HooksIcon sx={{ fontSize: 64, color: theme.palette.text.disabled, mb: 2 }} />
                  <Typography variant="h6" gutterBottom>
                    No hooks found
                  </Typography>
                  <Typography variant="body2" color="text.secondary" mb={3}>
                    {searchQuery
                      ? 'Try adjusting your search query'
                      : activeFilter !== 'all'
                      ? 'Try changing the filter or create a custom hook'
                      : 'Create a custom hook to get started'}
                  </Typography>
                  {!searchQuery && (
                    <Button variant="contained" startIcon={<AddIcon />} onClick={() => setCreateDialogOpen(true)}>
                      Create Custom Hook
                    </Button>
                  )}
                </Paper>
              </Grid>
            ) : (
              filteredHooks.map((hook) => (
                <Grid item xs={12} sm={6} lg={4} key={`${hook.hook_type}-${hook.id}`}>
                  <HookCard
                    hook={hook}
                    showToggle={true}
                    showDelete={hook.hook_type === 'custom' && activeFilter !== 'enabled'}
                    showSaveToFavorites={!hook.is_favorite && activeFilter !== 'enabled' && activeFilter !== 'favorite'}
                    showRemoveFromFavorites={hook.is_favorite && activeFilter !== 'enabled'}
                  />
                </Grid>
              ))
            )}
          </Grid>
        )}
      </Container>

      {/* Create Custom Hook Dialog */}
      <Dialog
        open={createDialogOpen}
        onClose={() => !creating && setCreateDialogOpen(false)}
        maxWidth="md"
        fullWidth
        PaperProps={{
          sx: {
            borderRadius: 3,
            background: theme.palette.background.paper,
          },
        }}
      >
        <DialogTitle sx={{ pb: 1 }}>
          <Typography variant="h5" fontWeight={600}>
            Create Custom Hook
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Define a new lifecycle hook for automated project tasks
          </Typography>
        </DialogTitle>
        <DialogContent>
          <Stack spacing={3} mt={2}>
            <TextField
              autoFocus
              label="Hook Name"
              fullWidth
              variant="outlined"
              value={newHook.name}
              onChange={(e) => setNewHook({ ...newHook, name: e.target.value })}
              disabled={creating}
              helperText="e.g., 'Pre-commit Code Formatter'"
            />
            <TextField
              label="Description"
              fullWidth
              multiline
              rows={2}
              variant="outlined"
              value={newHook.description}
              onChange={(e) => setNewHook({ ...newHook, description: e.target.value })}
              disabled={creating}
              helperText="Describe what this hook does"
            />
            <FormControl fullWidth>
              <InputLabel>Category</InputLabel>
              <Select
                value={newHook.category}
                label="Category"
                onChange={(e) => setNewHook({ ...newHook, category: e.target.value })}
                disabled={creating}
              >
                <MenuItem value="logging">Logging</MenuItem>
                <MenuItem value="formatting">Formatting</MenuItem>
                <MenuItem value="notifications">Notifications</MenuItem>
                <MenuItem value="security">Security</MenuItem>
                <MenuItem value="version-control">Version Control</MenuItem>
              </Select>
            </FormControl>
            <TextField
              label="Hook Configuration (JSON)"
              fullWidth
              multiline
              rows={6}
              variant="outlined"
              value={newHook.hook_config}
              onChange={(e) => setNewHook({ ...newHook, hook_config: e.target.value })}
              disabled={creating}
              helperText="JSON object with hook configuration (e.g., trigger events, actions)"
              sx={{ fontFamily: 'monospace' }}
            />
            <TextField
              label="Setup Instructions (Optional)"
              fullWidth
              multiline
              rows={3}
              variant="outlined"
              value={newHook.setup_instructions}
              onChange={(e) => setNewHook({ ...newHook, setup_instructions: e.target.value })}
              disabled={creating}
              helperText="Instructions for setting up this hook"
            />
            <TextField
              label="Dependencies (Optional)"
              fullWidth
              variant="outlined"
              value={newHook.dependencies}
              onChange={(e) => setNewHook({ ...newHook, dependencies: e.target.value })}
              disabled={creating}
              helperText="Comma-separated list of dependencies (e.g., 'requests, slack-sdk')"
            />
          </Stack>
        </DialogContent>
        <DialogActions sx={{ px: 3, pb: 3 }}>
          <Button onClick={() => setCreateDialogOpen(false)} disabled={creating} sx={{ borderRadius: 2 }}>
            Cancel
          </Button>
          <Button
            onClick={handleCreateHook}
            variant="contained"
            disabled={!newHook.name || !newHook.description || !newHook.hook_config || creating}
            sx={{
              borderRadius: 2,
              px: 3,
              background: `linear-gradient(135deg, ${theme.palette.primary.main}, ${theme.palette.primary.dark})`,
            }}
          >
            {creating ? <CircularProgress size={24} /> : 'Create Hook'}
          </Button>
        </DialogActions>
      </Dialog>

      {/* Edit Hook Dialog */}
      <Dialog
        open={editDialogOpen}
        onClose={() => !editing && setEditDialogOpen(false)}
        maxWidth="md"
        fullWidth
        PaperProps={{
          sx: {
            borderRadius: 3,
            background: theme.palette.background.paper,
          },
        }}
      >
        <DialogTitle sx={{ pb: 1 }}>
          <Typography variant="h5" fontWeight={600}>
            Edit Hook
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Modify hook configuration and settings
          </Typography>
        </DialogTitle>
        <DialogContent>
          <Stack spacing={3} mt={2}>
            <TextField
              autoFocus
              label="Hook Name"
              fullWidth
              variant="outlined"
              value={editedHook.name}
              onChange={(e) => setEditedHook({ ...editedHook, name: e.target.value })}
              disabled={editing}
            />
            <TextField
              label="Description"
              fullWidth
              multiline
              rows={2}
              variant="outlined"
              value={editedHook.description}
              onChange={(e) => setEditedHook({ ...editedHook, description: e.target.value })}
              disabled={editing}
            />
            <FormControl fullWidth>
              <InputLabel>Category</InputLabel>
              <Select
                value={editedHook.category}
                label="Category"
                onChange={(e) => setEditedHook({ ...editedHook, category: e.target.value })}
                disabled={editing}
              >
                <MenuItem value="logging">Logging</MenuItem>
                <MenuItem value="formatting">Formatting</MenuItem>
                <MenuItem value="notifications">Notifications</MenuItem>
                <MenuItem value="security">Security</MenuItem>
                <MenuItem value="version-control">Version Control</MenuItem>
              </Select>
            </FormControl>
            <TextField
              label="Hook Configuration (JSON)"
              fullWidth
              multiline
              rows={6}
              variant="outlined"
              value={editedHook.hook_config}
              onChange={(e) => setEditedHook({ ...editedHook, hook_config: e.target.value })}
              disabled={editing}
              sx={{ fontFamily: 'monospace' }}
            />
            <TextField
              label="Setup Instructions (Optional)"
              fullWidth
              multiline
              rows={3}
              variant="outlined"
              value={editedHook.setup_instructions}
              onChange={(e) => setEditedHook({ ...editedHook, setup_instructions: e.target.value })}
              disabled={editing}
            />
            <TextField
              label="Dependencies (Optional)"
              fullWidth
              variant="outlined"
              value={editedHook.dependencies}
              onChange={(e) => setEditedHook({ ...editedHook, dependencies: e.target.value })}
              disabled={editing}
            />
          </Stack>
        </DialogContent>
        <DialogActions sx={{ px: 3, pb: 3 }}>
          <Button onClick={() => setEditDialogOpen(false)} disabled={editing} sx={{ borderRadius: 2 }}>
            Cancel
          </Button>
          <Button
            onClick={handleEditHook}
            variant="contained"
            disabled={!editedHook.name || !editedHook.description || !editedHook.hook_config || editing}
            sx={{
              borderRadius: 2,
              px: 3,
              background: `linear-gradient(135deg, ${theme.palette.primary.main}, ${theme.palette.primary.dark})`,
            }}
          >
            {editing ? <CircularProgress size={24} /> : 'Save Changes'}
          </Button>
        </DialogActions>
      </Dialog>

      {/* View Hook Details Dialog */}
      <Dialog
        open={viewDialogOpen}
        onClose={() => setViewDialogOpen(false)}
        maxWidth="md"
        fullWidth
        PaperProps={{
          sx: {
            borderRadius: 3,
            background: theme.palette.background.paper,
          },
        }}
      >
        <DialogTitle sx={{ pb: 1 }}>
          <Typography variant="h5" fontWeight={600}>
            Hook Details
          </Typography>
        </DialogTitle>
        <DialogContent>
          {selectedHook && (
            <Stack spacing={3} mt={2}>
              {/* Header */}
              <Box display="flex" alignItems="start" gap={2}>
                <Box
                  sx={{
                    width: 64,
                    height: 64,
                    borderRadius: 2,
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    background: `linear-gradient(135deg, ${alpha(getCategoryColor(selectedHook.category), 0.2)}, ${alpha(getCategoryColor(selectedHook.category), 0.1)})`,
                    border: `1px solid ${alpha(getCategoryColor(selectedHook.category), 0.2)}`,
                  }}
                >
                  <HooksIcon sx={{ color: getCategoryColor(selectedHook.category), fontSize: 36 }} />
                </Box>
                <Box flexGrow={1}>
                  <Typography variant="h5" fontWeight={600} gutterBottom>
                    {selectedHook.name}
                  </Typography>
                  <Stack direction="row" spacing={1}>
                    <Chip label={selectedHook.category} size="small" />
                    <Chip
                      label={selectedHook.hook_type === 'default' ? 'Default' : 'Custom'}
                      size="small"
                      color={selectedHook.hook_type === 'default' ? 'success' : 'info'}
                    />
                    {selectedHook.is_enabled && (
                      <Chip label="Enabled" size="small" color="success" icon={<CheckCircleIcon />} />
                    )}
                  </Stack>
                </Box>
              </Box>

              <Divider />

              {/* Description */}
              <Box>
                <Typography variant="subtitle2" color="text.secondary" gutterBottom>
                  Description
                </Typography>
                <Typography variant="body1">{selectedHook.description}</Typography>
              </Box>

              {/* Configuration */}
              <Box>
                <Typography variant="subtitle2" color="text.secondary" gutterBottom>
                  Configuration
                </Typography>
                <Box
                  sx={{
                    p: 2,
                    bgcolor: theme.palette.mode === 'dark' ? alpha(theme.palette.background.default, 0.5) : alpha(theme.palette.grey[100], 0.8),
                    borderRadius: 1,
                    fontFamily: 'monospace',
                    fontSize: '0.85rem',
                    border: `1px solid ${alpha(theme.palette.divider, 0.1)}`,
                    maxHeight: 300,
                    overflow: 'auto',
                  }}
                >
                  <pre>{JSON.stringify(selectedHook.hook_config, null, 2)}</pre>
                </Box>
              </Box>

              {/* Setup Instructions */}
              {selectedHook.setup_instructions && (
                <Box>
                  <Typography variant="subtitle2" color="text.secondary" gutterBottom>
                    Setup Instructions
                  </Typography>
                  <Box
                    sx={{
                      p: 2,
                      bgcolor: alpha(theme.palette.info.main, 0.05),
                      borderRadius: 1,
                      border: `1px solid ${alpha(theme.palette.info.main, 0.2)}`,
                    }}
                  >
                    <Typography variant="body2" sx={{ whiteSpace: 'pre-wrap' }}>
                      {selectedHook.setup_instructions}
                    </Typography>
                  </Box>
                </Box>
              )}

              {/* Dependencies */}
              {selectedHook.dependencies && selectedHook.dependencies.length > 0 && (
                <Box>
                  <Typography variant="subtitle2" color="text.secondary" gutterBottom>
                    Dependencies
                  </Typography>
                  <Stack direction="row" spacing={1} flexWrap="wrap" useFlexGap>
                    {selectedHook.dependencies.map((dep) => (
                      <Chip key={dep} label={dep} size="small" variant="outlined" />
                    ))}
                  </Stack>
                </Box>
              )}

              {/* Metadata */}
              <Box>
                <Typography variant="caption" color="text.secondary" display="block">
                  Created: {new Date(selectedHook.created_at).toLocaleString()}
                </Typography>
                <Typography variant="caption" color="text.secondary" display="block">
                  Last Updated: {new Date(selectedHook.updated_at).toLocaleString()}
                </Typography>
              </Box>
            </Stack>
          )}
        </DialogContent>
        <DialogActions sx={{ px: 3, pb: 3 }}>
          <Button onClick={() => setViewDialogOpen(false)} variant="contained" sx={{ borderRadius: 2 }}>
            Close
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default Hooks;
