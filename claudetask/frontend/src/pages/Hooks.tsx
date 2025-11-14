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
  Collapse,
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
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import ExpandLessIcon from '@mui/icons-material/ExpandLess';
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

// Category colors
const getCategoryColor = (category: string): 'primary' | 'secondary' | 'success' | 'error' | 'warning' | 'info' => {
  const categoryMap: { [key: string]: 'primary' | 'secondary' | 'success' | 'error' | 'warning' | 'info' } = {
    logging: 'info',
    formatting: 'primary',
    notifications: 'warning',
    security: 'error',
    'version-control': 'success',
  };
  return categoryMap[category] || 'secondary';
};

const Hooks: React.FC = () => {
  const { selectedProject } = useProject();
  const [activeTab, setActiveTab] = useState(0);
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

  const HookCard: React.FC<{ hook: Hook; showToggle?: boolean; showDelete?: boolean; showEdit?: boolean }> = ({
    hook,
    showToggle = false,
    showDelete = false,
    showEdit = false,
  }) => {
    const [expandedSetup, setExpandedSetup] = useState(false);
    const [expandedConfig, setExpandedConfig] = useState(false);

    // Check if hook data is valid
    if (!hook || !hook.name) {
      return null;
    }

    return (
      <Card
        sx={{
          height: '100%',
          display: 'flex',
          flexDirection: 'column',
          transition: 'all 0.3s ease',
          '&:hover': {
            transform: 'translateY(-4px)',
            boxShadow: 6,
          }
        }}
      >
        <CardContent sx={{ flexGrow: 1, py: 2, px: 2 }}>
          <Box display="flex" justifyContent="space-between" alignItems="start" mb={1}>
          <Box flexGrow={1}>
              <Typography variant="subtitle1" component="div" fontWeight="600" gutterBottom sx={{ mb: 0.5 }}>
                {hook.name}
              </Typography>
              <Chip
                label={hook.category}
                size="small"
                color={getCategoryColor(hook.category)}
                variant="outlined"
                sx={{ height: '20px', fontSize: '0.7rem' }}
              />
            </Box>
            <Box display="flex" gap={1} alignItems="center">
              {hook.status && hook.status !== 'active' && (
                <Chip
                  label={hook.status}
                  size="small"
                  color={hook.status === 'creating' ? 'info' : 'error'}
                />
              )}
              <Tooltip title={hook.is_favorite ? 'Remove from favorites' : 'Add to favorites'}>
                <IconButton
                  size="small"
                  color={hook.is_favorite ? 'warning' : 'default'}
                  onClick={() => {
                    if (hook.is_favorite) {
                      handleRemoveFromFavorites(hook.id, hook.hook_type);
                    } else {
                      handleSaveToFavorites(hook.id, hook.hook_type);
                    }
                  }}
                >
                  {hook.is_favorite ? <StarIcon /> : <StarBorderIcon />}
                </IconButton>
              </Tooltip>
              {showEdit && (
                <Tooltip title="Edit hook">
                  <IconButton
                    size="small"
                    color="primary"
                    onClick={() => openEditDialog(hook)}
                  >
                    <EditIcon />
                  </IconButton>
                </Tooltip>
              )}
              {showDelete && (
                <IconButton
                  size="small"
                  color="error"
                  onClick={() => handleDeleteHook(hook.id)}
                >
                  <DeleteIcon />
                </IconButton>
              )}
            </Box>
          </Box>

          <Typography variant="body2" color="text.secondary" sx={{ mb: 1.5, fontSize: '0.875rem', lineHeight: 1.4 }}>
            {hook.description}
          </Typography>

          {/* Dependencies */}
          {hook.dependencies && hook.dependencies.length > 0 && (
            <Box mb={1}>
              <Typography variant="caption" color="text.secondary" fontWeight="bold" sx={{ fontSize: '0.7rem' }}>
                Dependencies:
              </Typography>
              <Box display="flex" gap={0.5} flexWrap="wrap" mt={0.5}>
                {hook.dependencies.map((dep, idx) => (
                  <Chip key={idx} label={dep} size="small" variant="outlined" sx={{ height: '18px', fontSize: '0.65rem' }} />
                ))}
              </Box>
            </Box>
          )}

          {/* Setup Instructions */}
          {hook.setup_instructions && (
            <Box mb={1}>
              <Button
                size="small"
                onClick={() => setExpandedSetup(!expandedSetup)}
                endIcon={expandedSetup ? <ExpandLessIcon /> : <ExpandMoreIcon />}
                sx={{ textTransform: 'none', p: 0, fontSize: '0.75rem', minHeight: 0 }}
              >
                Setup
              </Button>
              <Collapse in={expandedSetup}>
                <Box
                  sx={{
                    mt: 0.5,
                    p: 1,
                    bgcolor: 'grey.100',
                    borderRadius: 1,
                    fontSize: '0.75rem',
                    fontFamily: 'monospace',
                    whiteSpace: 'pre-wrap',
                    overflowX: 'auto',
                    maxHeight: '150px',
                    overflow: 'auto',
                  }}
                >
                  {hook.setup_instructions}
                </Box>
              </Collapse>
            </Box>
          )}

          {/* Hook Configuration */}
          <Box mb={1}>
            <Button
              size="small"
              onClick={() => setExpandedConfig(!expandedConfig)}
              endIcon={expandedConfig ? <ExpandLessIcon /> : <ExpandMoreIcon />}
              sx={{ textTransform: 'none', p: 0, fontSize: '0.75rem', minHeight: 0 }}
            >
              Config
            </Button>
            <Collapse in={expandedConfig}>
              <Box
                sx={{
                  mt: 0.5,
                  p: 1,
                  bgcolor: 'grey.900',
                  color: 'grey.100',
                  borderRadius: 1,
                  fontSize: '0.7rem',
                  fontFamily: 'monospace',
                  whiteSpace: 'pre',
                  overflowX: 'auto',
                  maxHeight: '200px',
                  overflow: 'auto',
                }}
              >
                {JSON.stringify(hook.hook_config, null, 2)}
              </Box>
            </Collapse>
          </Box>

          {showToggle && (
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
                />
              }
              label={hook.is_enabled ? 'Enabled' : 'Enable'}
              sx={{ mt: 1 }}
            />
          )}
        </CardContent>
      </Card>
    );
  };

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
        <Typography variant="h4">Hooks Management</Typography>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={() => setCreateDialogOpen(true)}
          disabled={!selectedProject?.id}
        >
          Create Custom Hook
        </Button>
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

      <Tabs value={activeTab} onChange={(_, newValue) => setActiveTab(newValue)} sx={{ mb: 3 }}>
        <Tab label={`Enabled (${hooks.enabled.length})`} />
        <Tab label={`Default (${hooks.available_default.length})`} />
        <Tab label={`Custom (${hooks.custom.length})`} />
        <Tab label={`Favorites (${hooks.favorites.length})`} />
      </Tabs>

      {/* Enabled Hooks Tab */}
      {activeTab === 0 && (
        <Grid container spacing={3}>
          {hooks.enabled.length === 0 ? (
            <Grid item xs={12}>
              <Alert severity="info">
                No hooks enabled yet. Enable default or custom hooks from their respective tabs.
              </Alert>
            </Grid>
          ) : (
            hooks.enabled.map((hook) => (
              <Grid item xs={12} md={6} key={`enabled-${hook.id}`}>
                <HookCard hook={hook} showToggle={true} showEdit={false} showDelete={false} />
              </Grid>
            ))
          )}
        </Grid>
      )}

      {/* Default Hooks Tab */}
      {activeTab === 1 && (
        <Grid container spacing={3}>
          {hooks.available_default.length === 0 ? (
            <Grid item xs={12}>
              <Alert severity="info">
                No default hooks available. Hooks will be seeded on backend startup.
              </Alert>
            </Grid>
          ) : (
            hooks.available_default.map((hook) => (
              <Grid item xs={12} md={6} key={`default-${hook.id}`}>
                <HookCard hook={hook} showToggle={true} showEdit={false} showDelete={false} />
              </Grid>
            ))
          )}
        </Grid>
      )}

      {/* Custom Hooks Tab */}
      {activeTab === 2 && (
        <Grid container spacing={3}>
          {hooks.custom.length === 0 ? (
            <Grid item xs={12}>
              <Alert severity="info">
                No custom hooks created yet. Click "Create Custom Hook" to add your own.
              </Alert>
            </Grid>
          ) : (
            hooks.custom.map((hook) => (
              <Grid item xs={12} md={6} key={`custom-${hook.id}`}>
                <HookCard hook={hook} showToggle={true} showEdit={false} showDelete={false} />
              </Grid>
            ))
          )}
        </Grid>
      )}

      {/* Favorites Tab */}
      {activeTab === 3 && (
        <Grid container spacing={3}>
          {hooks.favorites.length === 0 ? (
            <Grid item xs={12}>
              <Alert severity="info">
                No favorite hooks yet. Click the star icon on any hook to add it to favorites.
              </Alert>
            </Grid>
          ) : (
            hooks.favorites.map((hook) => (
              <Grid item xs={12} md={6} key={`${hook.hook_type}-${hook.id}`}>
                <HookCard hook={hook} showToggle={true} showEdit={false} showDelete={false} />
              </Grid>
            ))
          )}
        </Grid>
      )}

      {/* Create Custom Hook Dialog */}
      <Dialog
        open={createDialogOpen}
        onClose={() => !creating && setCreateDialogOpen(false)}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>Create Custom Hook</DialogTitle>
        <DialogContent>
          <Alert severity="info" sx={{ mb: 2 }}>
            <Typography variant="body2">
              This will create a new custom hook for this project.
              Hooks allow you to execute custom logic at various points in the task lifecycle.
            </Typography>
          </Alert>
          <TextField
            autoFocus
            margin="dense"
            label="Hook Name"
            fullWidth
            variant="outlined"
            value={newHook.name}
            onChange={(e) => setNewHook({ ...newHook, name: e.target.value })}
            disabled={creating}
            helperText="e.g., 'Slack Notification Hook'"
            sx={{ mb: 2 }}
          />
          <TextField
            margin="dense"
            label="Description"
            fullWidth
            multiline
            rows={2}
            variant="outlined"
            value={newHook.description}
            onChange={(e) => setNewHook({ ...newHook, description: e.target.value })}
            disabled={creating}
            helperText="Describe what this hook does"
            sx={{ mb: 2 }}
          />
          <FormControl fullWidth margin="dense" sx={{ mb: 2 }}>
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
            margin="dense"
            label="Hook Configuration (JSON)"
            fullWidth
            multiline
            rows={6}
            variant="outlined"
            value={newHook.hook_config}
            onChange={(e) => setNewHook({ ...newHook, hook_config: e.target.value })}
            disabled={creating}
            helperText="JSON object with hook configuration (e.g., trigger events, actions)"
            sx={{ mb: 2, fontFamily: 'monospace' }}
          />
          <TextField
            margin="dense"
            label="Setup Instructions (Optional)"
            fullWidth
            multiline
            rows={3}
            variant="outlined"
            value={newHook.setup_instructions}
            onChange={(e) => setNewHook({ ...newHook, setup_instructions: e.target.value })}
            disabled={creating}
            helperText="Instructions for setting up this hook"
            sx={{ mb: 2 }}
          />
          <TextField
            margin="dense"
            label="Dependencies (Optional)"
            fullWidth
            variant="outlined"
            value={newHook.dependencies}
            onChange={(e) => setNewHook({ ...newHook, dependencies: e.target.value })}
            disabled={creating}
            helperText="Comma-separated list of dependencies (e.g., 'requests, slack-sdk')"
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setCreateDialogOpen(false)} disabled={creating}>
            Cancel
          </Button>
          <Button
            onClick={handleCreateHook}
            variant="contained"
            disabled={!newHook.name || !newHook.description || !newHook.hook_config || creating}
          >
            {creating ? <CircularProgress size={24} /> : 'Create'}
          </Button>
        </DialogActions>
      </Dialog>

      {/* Edit Custom Hook Dialog */}
      <Dialog
        open={editDialogOpen}
        onClose={() => !editing && setEditDialogOpen(false)}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>Edit Hook</DialogTitle>
        <DialogContent>
          <Alert severity="info" sx={{ mb: 2 }}>
            <Typography variant="body2">
              Edit the hook configuration. Changes will be applied to the project's .claude/settings.json.
            </Typography>
          </Alert>
          <TextField
            autoFocus
            margin="dense"
            label="Hook Name"
            fullWidth
            variant="outlined"
            value={editedHook.name}
            onChange={(e) => setEditedHook({ ...editedHook, name: e.target.value })}
            disabled={editing}
            helperText="e.g., 'Slack Notification Hook'"
            sx={{ mb: 2 }}
          />
          <TextField
            margin="dense"
            label="Description"
            fullWidth
            multiline
            rows={2}
            variant="outlined"
            value={editedHook.description}
            onChange={(e) => setEditedHook({ ...editedHook, description: e.target.value })}
            disabled={editing}
            helperText="Describe what this hook does"
            sx={{ mb: 2 }}
          />
          <FormControl fullWidth margin="dense" sx={{ mb: 2 }}>
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
            margin="dense"
            label="Hook Configuration (JSON)"
            fullWidth
            multiline
            rows={6}
            variant="outlined"
            value={editedHook.hook_config}
            onChange={(e) => setEditedHook({ ...editedHook, hook_config: e.target.value })}
            disabled={editing}
            helperText="JSON object with hook configuration (e.g., trigger events, actions)"
            sx={{ mb: 2, fontFamily: 'monospace' }}
          />
          <TextField
            margin="dense"
            label="Setup Instructions (Optional)"
            fullWidth
            multiline
            rows={3}
            variant="outlined"
            value={editedHook.setup_instructions}
            onChange={(e) => setEditedHook({ ...editedHook, setup_instructions: e.target.value })}
            disabled={editing}
            helperText="Instructions for setting up this hook"
            sx={{ mb: 2 }}
          />
          <TextField
            margin="dense"
            label="Dependencies (Optional)"
            fullWidth
            variant="outlined"
            value={editedHook.dependencies}
            onChange={(e) => setEditedHook({ ...editedHook, dependencies: e.target.value })}
            disabled={editing}
            helperText="Comma-separated list of dependencies (e.g., 'requests, slack-sdk')"
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setEditDialogOpen(false)} disabled={editing}>
            Cancel
          </Button>
          <Button
            onClick={handleEditHook}
            variant="contained"
            disabled={!editedHook.name || !editedHook.description || !editedHook.hook_config || editing}
          >
            {editing ? <CircularProgress size={24} /> : 'Save Changes'}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default Hooks;
