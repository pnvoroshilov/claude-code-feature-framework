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
  Badge,
  InputAdornment,
  Paper,
} from '@mui/material';
import AddIcon from '@mui/icons-material/Add';
import DeleteIcon from '@mui/icons-material/Delete';
import InfoIcon from '@mui/icons-material/Info';
import SmartToyIcon from '@mui/icons-material/SmartToy';
import StarIcon from '@mui/icons-material/Star';
import StarBorderIcon from '@mui/icons-material/StarBorder';
import EditIcon from '@mui/icons-material/Edit';
import FilterListIcon from '@mui/icons-material/FilterList';
import SearchIcon from '@mui/icons-material/Search';
import BuildIcon from '@mui/icons-material/Build';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import CategoryIcon from '@mui/icons-material/Category';
import axios from 'axios';
import { useProject } from '../context/ProjectContext';
import CodeEditorDialog from '../components/CodeEditorDialog';

// Remove /api suffix if present, since we add it manually in request paths
const API_BASE_URL = (process.env.REACT_APP_API_URL || 'http://localhost:3333').replace(/\/api$/, '');

interface Subagent {
  id: number;
  name: string;
  description: string;
  subagent_kind: 'default' | 'custom';
  subagent_type: string;
  category: string;
  tools_available?: string[];
  recommended_for?: string[];
  is_enabled: boolean;
  is_favorite?: boolean;
  status?: string;
  created_by?: string;
  created_at: string;
  updated_at: string;
}

interface SubagentsResponse {
  enabled: Subagent[];
  available_default: Subagent[];
  custom: Subagent[];
  favorites: Subagent[];
}

type FilterType = 'all' | 'default' | 'custom' | 'favorite' | 'enabled';

const Subagents: React.FC = () => {
  const theme = useTheme();
  const { selectedProject } = useProject();
  const [activeFilter, setActiveFilter] = useState<FilterType>('all');
  const [searchQuery, setSearchQuery] = useState('');
  const [subagents, setSubagents] = useState<SubagentsResponse>({
    enabled: [],
    available_default: [],
    custom: [],
    favorites: [],
  });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [createDialogOpen, setCreateDialogOpen] = useState(false);
  const [viewSubagentDialogOpen, setViewSubagentDialogOpen] = useState(false);
  const [editDialogOpen, setEditDialogOpen] = useState(false);
  const [selectedSubagent, setSelectedSubagent] = useState<Subagent | null>(null);
  const [editingSubagent, setEditingSubagent] = useState<Subagent | null>(null);
  const [newSubagentName, setNewSubagentName] = useState('');
  const [newSubagentDescription, setNewSubagentDescription] = useState('');
  const [creating, setCreating] = useState(false);

  // Categories for subagents
  const categories = [
    'Development',
    'Analysis',
    'Testing',
    'Architecture',
    'DevOps',
    'Security',
    'Documentation',
    'Quality',
    'Performance',
    'Custom',
  ];

  // Fetch subagents when project changes
  useEffect(() => {
    if (selectedProject?.id) {
      fetchSubagents();
    }
  }, [selectedProject?.id]);

  const fetchSubagents = async () => {
    if (!selectedProject?.id) return;

    setLoading(true);
    setError(null);
    try {
      const response = await axios.get<SubagentsResponse>(
        `${API_BASE_URL}/api/projects/${selectedProject?.id}/subagents/`
      );
      setSubagents(response.data);
    } catch (err: any) {
      setError('Failed to fetch subagents: ' + (err.response?.data?.detail || err.message));
    } finally {
      setLoading(false);
    }
  };

  const handleEnableSubagent = async (subagentId: number, subagentKind: 'default' | 'custom') => {
    if (!selectedProject?.id) return;

    try {
      await axios.post(
        `${API_BASE_URL}/api/projects/${selectedProject?.id}/subagents/enable/${subagentId}?subagent_kind=${subagentKind}`
      );
      await fetchSubagents();
    } catch (err: any) {
      setError('Failed to enable subagent: ' + (err.response?.data?.detail || err.message));
    }
  };

  const handleDisableSubagent = async (subagentId: number) => {
    if (!selectedProject?.id) return;

    try {
      await axios.post(
        `${API_BASE_URL}/api/projects/${selectedProject?.id}/subagents/disable/${subagentId}`
      );
      await fetchSubagents();
    } catch (err: any) {
      setError('Failed to disable subagent: ' + (err.response?.data?.detail || err.message));
    }
  };

  const handleCreateSubagent = async () => {
    if (!selectedProject?.id) return;

    setCreating(true);
    setError(null);
    try {
      await axios.post(
        `${API_BASE_URL}/api/projects/${selectedProject?.id}/subagents/create`,
        {
          name: newSubagentName,
          description: newSubagentDescription,
          category: 'Custom',
          subagent_type: newSubagentName.toLowerCase().replace(/\s+/g, '-'),
          config: null,
          tools_available: null,
        }
      );
      setCreateDialogOpen(false);
      setNewSubagentName('');
      setNewSubagentDescription('');
      await fetchSubagents();
    } catch (err: any) {
      setError('Failed to create agent: ' + (err.response?.data?.detail || err.message));
    } finally {
      setCreating(false);
    }
  };

  const handleDeleteSubagent = async (subagentId: number) => {
    if (!selectedProject?.id) return;
    if (!window.confirm('Are you sure you want to delete this custom subagent?')) return;

    try {
      await axios.delete(
        `${API_BASE_URL}/api/projects/${selectedProject?.id}/subagents/${subagentId}`
      );
      await fetchSubagents();
    } catch (err: any) {
      setError('Failed to delete subagent: ' + (err.response?.data?.detail || err.message));
    }
  };

  const handleSaveToFavorites = async (subagentId: number, subagentName: string, subagentKind: 'default' | 'custom') => {
    if (!selectedProject?.id) return;

    try {
      await axios.post(
        `${API_BASE_URL}/api/projects/${selectedProject?.id}/subagents/favorites/${subagentId}?subagent_kind=${subagentKind}`
      );
      await fetchSubagents();
    } catch (err: any) {
      setError('Failed to save to favorites: ' + (err.response?.data?.detail || err.message));
    }
  };

  const handleRemoveFromFavorites = async (subagentId: number, subagentName: string, subagentKind: 'default' | 'custom') => {
    if (!selectedProject?.id) return;

    try {
      await axios.delete(
        `${API_BASE_URL}/api/projects/${selectedProject?.id}/subagents/favorites/${subagentId}?subagent_kind=${subagentKind}`
      );
      await fetchSubagents();
    } catch (err: any) {
      setError('Failed to remove from favorites: ' + (err.response?.data?.detail || err.message));
    }
  };

  const handleViewSubagent = (subagent: Subagent) => {
    setSelectedSubagent(subagent);
    setViewSubagentDialogOpen(true);
  };

  // Filter subagents based on active filter and search query
  const getFilteredSubagents = (): Subagent[] => {
    let filtered: Subagent[] = [];

    switch (activeFilter) {
      case 'default':
        filtered = subagents.available_default;
        break;
      case 'custom':
        filtered = subagents.custom;
        break;
      case 'favorite':
        filtered = subagents.favorites;
        break;
      case 'enabled':
        filtered = subagents.enabled;
        break;
      case 'all':
      default:
        const allSubagents = [
          ...subagents.available_default,
          ...subagents.custom,
        ];
        filtered = allSubagents.filter(
          (subagent, index, self) => self.findIndex(s => s.id === subagent.id && s.subagent_kind === subagent.subagent_kind) === index
        );
    }

    // Apply search filter
    if (searchQuery.trim()) {
      const query = searchQuery.toLowerCase();
      filtered = filtered.filter(
        (agent) =>
          agent.name.toLowerCase().includes(query) ||
          agent.description.toLowerCase().includes(query) ||
          agent.category.toLowerCase().includes(query) ||
          agent.subagent_type.toLowerCase().includes(query)
      );
    }

    return filtered;
  };

  const filteredSubagents = getFilteredSubagents();

  // Statistics
  const stats = {
    total: subagents.available_default.length + subagents.custom.length,
    enabled: subagents.enabled.length,
    favorites: subagents.favorites.length,
    custom: subagents.custom.length,
  };

  const SubagentCard: React.FC<{
    subagent: Subagent;
    showToggle?: boolean;
    showDelete?: boolean;
    showSaveToFavorites?: boolean;
    showRemoveFromFavorites?: boolean;
  }> = ({
    subagent,
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
          background: subagent.is_enabled
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
                background: `linear-gradient(135deg, ${alpha(theme.palette.primary.main, 0.2)}, ${alpha(theme.palette.primary.light, 0.1)})`,
                border: `1px solid ${alpha(theme.palette.primary.main, 0.2)}`,
              }}
            >
              <SmartToyIcon sx={{ color: theme.palette.primary.main, fontSize: 28 }} />
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
                {subagent.name}
                {subagent.is_enabled && (
                  <Tooltip title="Enabled">
                    <CheckCircleIcon sx={{ fontSize: 18, color: theme.palette.success.main }} />
                  </Tooltip>
                )}
              </Typography>
              <Stack direction="row" spacing={0.5} flexWrap="wrap">
                <Chip
                  label={subagent.category}
                  size="small"
                  icon={<CategoryIcon sx={{ fontSize: 14 }} />}
                  sx={{
                    height: 22,
                    fontSize: '0.7rem',
                    fontWeight: 500,
                    background: `linear-gradient(135deg, ${alpha(theme.palette.primary.main, 0.15)}, ${alpha(theme.palette.primary.main, 0.05)})`,
                    border: `1px solid ${alpha(theme.palette.primary.main, 0.2)}`,
                    color: theme.palette.primary.main,
                  }}
                />
                <Chip
                  label={subagent.subagent_kind === 'default' ? 'Default' : 'Custom'}
                  size="small"
                  sx={{
                    height: 22,
                    fontSize: '0.7rem',
                    fontWeight: 500,
                    background: subagent.subagent_kind === 'default'
                      ? `linear-gradient(135deg, ${alpha(theme.palette.success.main, 0.15)}, ${alpha(theme.palette.success.main, 0.05)})`
                      : `linear-gradient(135deg, ${alpha(theme.palette.info.main, 0.15)}, ${alpha(theme.palette.info.main, 0.05)})`,
                    border: `1px solid ${alpha(
                      subagent.subagent_kind === 'default' ? theme.palette.success.main : theme.palette.info.main,
                      0.2
                    )}`,
                    color: subagent.subagent_kind === 'default' ? theme.palette.success.main : theme.palette.info.main,
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
                  onClick={() => handleSaveToFavorites(subagent.id, subagent.name, subagent.subagent_kind)}
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
                  onClick={() => handleRemoveFromFavorites(subagent.id, subagent.name, subagent.subagent_kind)}
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
            <Tooltip title="Edit agent code">
              <IconButton
                size="small"
                onClick={() => {
                  setEditingSubagent(subagent);
                  setEditDialogOpen(true);
                }}
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
            {showDelete && subagent.subagent_kind === 'custom' && (
              <Tooltip title="Delete custom subagent">
                <IconButton
                  size="small"
                  onClick={() => handleDeleteSubagent(subagent.id)}
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
                onClick={() => handleViewSubagent(subagent)}
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
          {subagent.description}
        </Typography>

        <Divider sx={{ my: 2 }} />

        {/* Metadata */}
        <Stack spacing={1}>
          <Typography variant="caption" color="text.secondary" sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
            <BuildIcon sx={{ fontSize: 14 }} />
            Type: <strong>{subagent.subagent_type}</strong>
          </Typography>
          {subagent.tools_available && subagent.tools_available.length > 0 && (
            <Box>
              <Typography variant="caption" color="text.secondary" display="block" mb={0.5}>
                Tools Available:
              </Typography>
              <Stack direction="row" spacing={0.5} flexWrap="wrap" useFlexGap>
                {subagent.tools_available.slice(0, 3).map((tool) => (
                  <Chip
                    key={tool}
                    label={tool}
                    size="small"
                    variant="outlined"
                    sx={{
                      height: 20,
                      fontSize: '0.65rem',
                      borderColor: alpha(theme.palette.text.secondary, 0.2),
                    }}
                  />
                ))}
                {subagent.tools_available.length > 3 && (
                  <Chip
                    label={`+${subagent.tools_available.length - 3} more`}
                    size="small"
                    variant="outlined"
                    sx={{
                      height: 20,
                      fontSize: '0.65rem',
                      borderColor: alpha(theme.palette.text.secondary, 0.2),
                    }}
                  />
                )}
              </Stack>
            </Box>
          )}
        </Stack>

        {/* Toggle switch */}
        {showToggle && (
          <Box mt={2}>
            <FormControlLabel
              control={
                <Switch
                  checked={subagent.is_enabled}
                  onChange={(e) => {
                    if (e.target.checked) {
                      handleEnableSubagent(subagent.id, subagent.subagent_kind);
                    } else {
                      handleDisableSubagent(subagent.id);
                    }
                  }}
                  color="primary"
                />
              }
              label={
                <Typography variant="body2" fontWeight={500}>
                  {subagent.is_enabled ? 'Enabled' : 'Disabled'}
                </Typography>
              }
            />
          </Box>
        )}
      </CardContent>
    </Card>
  );

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
                Agent Management
              </Typography>
              <Typography variant="body1" color="text.secondary">
                Manage and configure AI agents for your project
              </Typography>
            </Box>
            <Button
              variant="contained"
              size="large"
              startIcon={<AddIcon />}
              onClick={() => setCreateDialogOpen(true)}
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
              Create Custom Agent
            </Button>
          </Stack>

          {/* Statistics Cards */}
          <Grid container spacing={2} mb={3}>
            {[
              { label: 'Total Agents', value: stats.total, color: theme.palette.primary.main },
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

          {/* Search and Filter Bar */}
          <Paper
            sx={{
              p: 2,
              mb: 3,
              borderRadius: 2,
              background: alpha(theme.palette.background.paper, 0.8),
              backdropFilter: 'blur(10px)',
              border: `1px solid ${alpha(theme.palette.primary.main, 0.1)}`,
            }}
          >
            <Stack direction={{ xs: 'column', md: 'row' }} spacing={2} alignItems="center">
              {/* Search */}
              <TextField
                fullWidth
                placeholder="Search agents by name, description, or category..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                InputProps={{
                  startAdornment: (
                    <InputAdornment position="start">
                      <SearchIcon color="action" />
                    </InputAdornment>
                  ),
                }}
                sx={{
                  '& .MuiOutlinedInput-root': {
                    borderRadius: 2,
                  },
                }}
              />

              {/* Filter Toggle */}
              <ToggleButtonGroup
                value={activeFilter}
                exclusive
                onChange={(e, newFilter) => {
                  if (newFilter !== null) {
                    setActiveFilter(newFilter);
                  }
                }}
                sx={{
                  flexShrink: 0,
                  '& .MuiToggleButton-root': {
                    borderRadius: 2,
                    px: 2,
                    py: 1,
                    textTransform: 'none',
                    fontWeight: 500,
                    '&.Mui-selected': {
                      background: `linear-gradient(135deg, ${theme.palette.primary.main}, ${theme.palette.primary.dark})`,
                      color: theme.palette.primary.contrastText,
                      '&:hover': {
                        background: `linear-gradient(135deg, ${theme.palette.primary.dark}, ${theme.palette.primary.main})`,
                      },
                    },
                  },
                }}
              >
                <ToggleButton value="all">
                  All <Badge badgeContent={stats.total} color="primary" sx={{ ml: 1 }} />
                </ToggleButton>
                <ToggleButton value="default">
                  Default <Badge badgeContent={subagents.available_default.length} color="success" sx={{ ml: 1 }} />
                </ToggleButton>
                <ToggleButton value="custom">
                  Custom <Badge badgeContent={stats.custom} color="info" sx={{ ml: 1 }} />
                </ToggleButton>
                <ToggleButton value="favorite">
                  Favorites <Badge badgeContent={stats.favorites} color="warning" sx={{ ml: 1 }} />
                </ToggleButton>
                <ToggleButton value="enabled">
                  Enabled <Badge badgeContent={stats.enabled} color="success" sx={{ ml: 1 }} />
                </ToggleButton>
              </ToggleButtonGroup>
            </Stack>
          </Paper>
        </Box>

        {/* Agents Grid */}
        {loading ? (
          <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
            <CircularProgress size={48} />
          </Box>
        ) : (
          <Grid container spacing={3}>
            {filteredSubagents.length === 0 ? (
              <Grid item xs={12}>
                <Paper
                  sx={{
                    p: 6,
                    textAlign: 'center',
                    borderRadius: 2,
                    background: alpha(theme.palette.background.paper, 0.5),
                  }}
                >
                  <SmartToyIcon sx={{ fontSize: 64, color: theme.palette.text.disabled, mb: 2 }} />
                  <Typography variant="h6" gutterBottom>
                    No agents found
                  </Typography>
                  <Typography variant="body2" color="text.secondary" mb={3}>
                    {searchQuery
                      ? 'Try adjusting your search query'
                      : activeFilter !== 'all'
                      ? 'Try changing the filter or create a custom agent'
                      : 'Create a custom agent to get started'}
                  </Typography>
                  {!searchQuery && (
                    <Button variant="contained" startIcon={<AddIcon />} onClick={() => setCreateDialogOpen(true)}>
                      Create Custom Agent
                    </Button>
                  )}
                </Paper>
              </Grid>
            ) : (
              filteredSubagents.map((subagent) => (
                <Grid item xs={12} sm={6} lg={4} key={`${subagent.subagent_kind}-${subagent.id}`}>
                  <SubagentCard
                    subagent={subagent}
                    showToggle={true}
                    showDelete={subagent.subagent_kind === 'custom' && activeFilter !== 'enabled'}
                    showSaveToFavorites={!subagent.is_favorite && activeFilter !== 'enabled' && activeFilter !== 'favorite'}
                    showRemoveFromFavorites={subagent.is_favorite && activeFilter !== 'enabled'}
                  />
                </Grid>
              ))
            )}
          </Grid>
        )}
      </Container>

      {/* Create Custom Agent Dialog */}
      <Dialog
        open={createDialogOpen}
        onClose={() => setCreateDialogOpen(false)}
        maxWidth="sm"
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
            Create Custom Agent
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Define a new specialized AI agent for your project
          </Typography>
        </DialogTitle>
        <DialogContent>
          <Stack spacing={3} mt={2}>
            <TextField
              label="Agent Name"
              value={newSubagentName}
              onChange={(e) => setNewSubagentName(e.target.value)}
              fullWidth
              required
              placeholder="e.g., Database Migration Expert"
              helperText="A descriptive name for your custom agent"
            />
            <TextField
              label="Agent Description"
              value={newSubagentDescription}
              onChange={(e) => setNewSubagentDescription(e.target.value)}
              fullWidth
              required
              multiline
              rows={4}
              placeholder="e.g., Specialized in database schema design and migration management with Alembic"
              helperText="Describe what this agent specializes in and what tasks it handles"
            />
            <Alert
              severity="info"
              icon={<InfoIcon />}
              sx={{
                borderRadius: 2,
                '& .MuiAlert-message': {
                  fontSize: '0.875rem',
                },
              }}
            >
              The agent file will be automatically created in <code>.claude/agents/</code> with proper YAML frontmatter and configuration.
            </Alert>
          </Stack>
        </DialogContent>
        <DialogActions sx={{ px: 3, pb: 3 }}>
          <Button onClick={() => setCreateDialogOpen(false)} sx={{ borderRadius: 2 }}>
            Cancel
          </Button>
          <Button
            onClick={handleCreateSubagent}
            variant="contained"
            disabled={creating || !newSubagentName || !newSubagentDescription}
            sx={{
              borderRadius: 2,
              px: 3,
              background: `linear-gradient(135deg, ${theme.palette.primary.main}, ${theme.palette.primary.dark})`,
            }}
          >
            {creating ? <CircularProgress size={24} /> : 'Create Agent'}
          </Button>
        </DialogActions>
      </Dialog>

      {/* View Subagent Details Dialog */}
      <Dialog
        open={viewSubagentDialogOpen}
        onClose={() => setViewSubagentDialogOpen(false)}
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
            Agent Details
          </Typography>
        </DialogTitle>
        <DialogContent>
          {selectedSubagent && (
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
                    background: `linear-gradient(135deg, ${alpha(theme.palette.primary.main, 0.2)}, ${alpha(theme.palette.primary.light, 0.1)})`,
                    border: `1px solid ${alpha(theme.palette.primary.main, 0.2)}`,
                  }}
                >
                  <SmartToyIcon sx={{ color: theme.palette.primary.main, fontSize: 36 }} />
                </Box>
                <Box flexGrow={1}>
                  <Typography variant="h5" fontWeight={600} gutterBottom>
                    {selectedSubagent.name}
                  </Typography>
                  <Stack direction="row" spacing={1}>
                    <Chip label={selectedSubagent.category} size="small" color="primary" />
                    <Chip
                      label={selectedSubagent.subagent_kind === 'default' ? 'Default' : 'Custom'}
                      size="small"
                      color={selectedSubagent.subagent_kind === 'default' ? 'success' : 'info'}
                    />
                    {selectedSubagent.is_enabled && (
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
                <Typography variant="body1">{selectedSubagent.description}</Typography>
              </Box>

              {/* Type */}
              <Box>
                <Typography variant="subtitle2" color="text.secondary" gutterBottom>
                  Subagent Type
                </Typography>
                <Chip label={selectedSubagent.subagent_type} variant="outlined" />
              </Box>

              {/* Tools */}
              {selectedSubagent.tools_available && selectedSubagent.tools_available.length > 0 && (
                <Box>
                  <Typography variant="subtitle2" color="text.secondary" gutterBottom>
                    Available Tools
                  </Typography>
                  <Stack direction="row" spacing={1} flexWrap="wrap" useFlexGap>
                    {selectedSubagent.tools_available.map((tool) => (
                      <Chip key={tool} label={tool} size="small" variant="outlined" />
                    ))}
                  </Stack>
                </Box>
              )}

              {/* Recommended For */}
              {selectedSubagent.recommended_for && selectedSubagent.recommended_for.length > 0 && (
                <Box>
                  <Typography variant="subtitle2" color="text.secondary" gutterBottom>
                    Recommended For
                  </Typography>
                  <Stack direction="row" spacing={1} flexWrap="wrap" useFlexGap>
                    {selectedSubagent.recommended_for.map((rec) => (
                      <Chip key={rec} label={rec} size="small" variant="outlined" color="secondary" />
                    ))}
                  </Stack>
                </Box>
              )}

              {/* Metadata */}
              <Box>
                <Typography variant="caption" color="text.secondary" display="block">
                  Created: {new Date(selectedSubagent.created_at).toLocaleString()}
                </Typography>
                <Typography variant="caption" color="text.secondary" display="block">
                  Last Updated: {new Date(selectedSubagent.updated_at).toLocaleString()}
                </Typography>
              </Box>
            </Stack>
          )}
        </DialogContent>
        <DialogActions sx={{ px: 3, pb: 3 }}>
          <Button onClick={() => setViewSubagentDialogOpen(false)} variant="contained" sx={{ borderRadius: 2 }}>
            Close
          </Button>
        </DialogActions>
      </Dialog>

      {/* Code Editor Dialog */}
      {editingSubagent && (
        <CodeEditorDialog
          open={editDialogOpen}
          onClose={() => {
            setEditDialogOpen(false);
            setEditingSubagent(null);
          }}
          title={`Edit Agent: ${editingSubagent.name}`}
          itemName={editingSubagent.name}
          itemType="agent"
          projectId={selectedProject?.id || ''}
          onSave={() => {
            fetchSubagents();
          }}
        />
      )}
    </Box>
  );
};

export default Subagents;
