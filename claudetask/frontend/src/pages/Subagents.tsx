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
  MenuItem,
  Select,
  FormControl,
  InputLabel,
} from '@mui/material';
import AddIcon from '@mui/icons-material/Add';
import DeleteIcon from '@mui/icons-material/Delete';
import InfoIcon from '@mui/icons-material/Info';
import SmartToyIcon from '@mui/icons-material/SmartToy';
import axios from 'axios';

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
  status?: string;
  created_by?: string;
  created_at: string;
  updated_at: string;
}

interface SubagentsResponse {
  enabled: Subagent[];
  available_default: Subagent[];
  custom: Subagent[];
}

type FilterType = 'all' | 'default' | 'custom' | 'enabled';

const Subagents: React.FC = () => {
  const [activeFilter, setActiveFilter] = useState<FilterType>('all');
  const [subagents, setSubagents] = useState<SubagentsResponse>({
    enabled: [],
    available_default: [],
    custom: [],
  });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [createDialogOpen, setCreateDialogOpen] = useState(false);
  const [viewSubagentDialogOpen, setViewSubagentDialogOpen] = useState(false);
  const [selectedSubagent, setSelectedSubagent] = useState<Subagent | null>(null);
  const [newSubagentName, setNewSubagentName] = useState('');
  const [newSubagentDescription, setNewSubagentDescription] = useState('');
  const [creating, setCreating] = useState(false);
  const [activeProjectId, setActiveProjectId] = useState<string | null>(null);

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

  // Fetch subagents when project is loaded
  useEffect(() => {
    if (activeProjectId) {
      fetchSubagents();
    }
  }, [activeProjectId]);

  const fetchSubagents = async () => {
    if (!activeProjectId) return;

    setLoading(true);
    setError(null);
    try {
      const response = await axios.get<SubagentsResponse>(
        `${API_BASE_URL}/api/projects/${activeProjectId}/subagents/`
      );
      setSubagents(response.data);
    } catch (err: any) {
      setError('Failed to fetch subagents: ' + (err.response?.data?.detail || err.message));
    } finally {
      setLoading(false);
    }
  };

  const handleEnableSubagent = async (subagentId: number, subagentKind: 'default' | 'custom') => {
    if (!activeProjectId) return;

    try {
      await axios.post(
        `${API_BASE_URL}/api/projects/${activeProjectId}/subagents/enable/${subagentId}?subagent_kind=${subagentKind}`
      );
      await fetchSubagents(); // Refresh subagents list
    } catch (err: any) {
      setError('Failed to enable subagent: ' + (err.response?.data?.detail || err.message));
    }
  };

  const handleDisableSubagent = async (subagentId: number) => {
    if (!activeProjectId) return;

    try {
      await axios.post(
        `${API_BASE_URL}/api/projects/${activeProjectId}/subagents/disable/${subagentId}`
      );
      await fetchSubagents(); // Refresh subagents list
    } catch (err: any) {
      setError('Failed to disable subagent: ' + (err.response?.data?.detail || err.message));
    }
  };

  const handleCreateSubagent = async () => {
    if (!activeProjectId) return;

    setCreating(true);
    setError(null);
    try {
      // Send only name and description, backend will generate the agent file
      await axios.post(
        `${API_BASE_URL}/api/projects/${activeProjectId}/subagents/create`,
        {
          name: newSubagentName,
          description: newSubagentDescription,
          category: 'Custom', // Default category for custom agents
          subagent_type: newSubagentName.toLowerCase().replace(/\s+/g, '-'), // Auto-generate kebab-case type
          config: null, // Will be generated by backend
          tools_available: null, // Will use default tools
        }
      );
      setCreateDialogOpen(false);
      setNewSubagentName('');
      setNewSubagentDescription('');
      await fetchSubagents(); // Refresh subagents list
    } catch (err: any) {
      setError('Failed to create agent: ' + (err.response?.data?.detail || err.message));
    } finally {
      setCreating(false);
    }
  };

  const handleDeleteSubagent = async (subagentId: number) => {
    if (!activeProjectId) return;
    if (!window.confirm('Are you sure you want to delete this custom subagent?')) return;

    try {
      await axios.delete(
        `${API_BASE_URL}/api/projects/${activeProjectId}/subagents/${subagentId}`
      );
      await fetchSubagents(); // Refresh subagents list
    } catch (err: any) {
      setError('Failed to delete subagent: ' + (err.response?.data?.detail || err.message));
    }
  };

  const handleViewSubagent = (subagent: Subagent) => {
    setSelectedSubagent(subagent);
    setViewSubagentDialogOpen(true);
  };

  // Filter subagents based on active filter
  const getFilteredSubagents = (): Subagent[] => {
    switch (activeFilter) {
      case 'default':
        return subagents.available_default;
      case 'custom':
        return subagents.custom;
      case 'enabled':
        return subagents.enabled;
      case 'all':
      default:
        // Combine all unique subagents (avoiding duplicates by id)
        const allSubagents = [
          ...subagents.available_default,
          ...subagents.custom,
        ];
        // Remove duplicates by id
        const uniqueSubagents = allSubagents.filter(
          (subagent, index, self) => self.findIndex(s => s.id === subagent.id && s.subagent_kind === subagent.subagent_kind) === index
        );
        return uniqueSubagents;
    }
  };

  const filteredSubagents = getFilteredSubagents();

  const SubagentCard: React.FC<{
    subagent: Subagent;
    showToggle?: boolean;
    showDelete?: boolean;
  }> = ({
    subagent,
    showToggle = false,
    showDelete = false,
  }) => (
    <Card sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      <CardContent sx={{ flexGrow: 1 }}>
        <Box display="flex" justifyContent="space-between" alignItems="start" mb={1}>
          <Box flexGrow={1}>
            <Typography variant="h6" component="div" gutterBottom>
              <SmartToyIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
              {subagent.name}
            </Typography>
            <Chip
              label={subagent.category}
              size="small"
              sx={{ mr: 1, mb: 1 }}
              color="primary"
              variant="outlined"
            />
            <Chip
              label={subagent.subagent_kind === 'default' ? 'Default' : 'Custom'}
              size="small"
              sx={{ mb: 1 }}
              color={subagent.subagent_kind === 'default' ? 'success' : 'info'}
            />
          </Box>
          <Box>
            {showDelete && subagent.subagent_kind === 'custom' && (
              <Tooltip title="Delete custom subagent">
                <IconButton
                  size="small"
                  color="error"
                  onClick={() => handleDeleteSubagent(subagent.id)}
                >
                  <DeleteIcon />
                </IconButton>
              </Tooltip>
            )}
            <Tooltip title="View details">
              <IconButton
                size="small"
                color="info"
                onClick={() => handleViewSubagent(subagent)}
              >
                <InfoIcon />
              </IconButton>
            </Tooltip>
          </Box>
        </Box>
        <Typography variant="body2" color="text.secondary" paragraph>
          {subagent.description}
        </Typography>
        <Box mt={1}>
          <Typography variant="caption" color="text.secondary" display="block">
            Type: <strong>{subagent.subagent_type}</strong>
          </Typography>
          {subagent.tools_available && subagent.tools_available.length > 0 && (
            <Typography variant="caption" color="text.secondary" display="block">
              Tools: {subagent.tools_available.slice(0, 3).join(', ')}
              {subagent.tools_available.length > 3 && ` +${subagent.tools_available.length - 3} more`}
            </Typography>
          )}
        </Box>
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
              label={subagent.is_enabled ? 'Enabled' : 'Disabled'}
            />
          </Box>
        )}
      </CardContent>
    </Card>
  );

  return (
    <Box p={3}>
      <Box mb={3} display="flex" justifyContent="space-between" alignItems="center">
        <Typography variant="h4" component="h1">
          Subagent Management
        </Typography>
        <Button
          variant="contained"
          color="primary"
          startIcon={<AddIcon />}
          onClick={() => setCreateDialogOpen(true)}
        >
          Create Custom Agent
        </Button>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}

      {/* Filter Buttons */}
      <Box mb={3}>
        <ToggleButtonGroup
          value={activeFilter}
          exclusive
          onChange={(e, newFilter) => {
            if (newFilter !== null) {
              setActiveFilter(newFilter);
            }
          }}
          aria-label="subagent filter"
        >
          <ToggleButton value="all" aria-label="all subagents">
            All ({subagents.available_default.length + subagents.custom.length})
          </ToggleButton>
          <ToggleButton value="default" aria-label="default subagents">
            Default ({subagents.available_default.length})
          </ToggleButton>
          <ToggleButton value="custom" aria-label="custom subagents">
            Custom ({subagents.custom.length})
          </ToggleButton>
          <ToggleButton value="enabled" aria-label="enabled subagents">
            Enabled ({subagents.enabled.length})
          </ToggleButton>
        </ToggleButtonGroup>
      </Box>

      {loading ? (
        <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
          <CircularProgress />
        </Box>
      ) : (
        <Grid container spacing={3}>
          {filteredSubagents.length === 0 ? (
            <Grid item xs={12}>
              <Alert severity="info">
                No subagents found. {activeFilter !== 'all' && 'Try changing the filter or'} Create a custom subagent to get started.
              </Alert>
            </Grid>
          ) : (
            filteredSubagents.map((subagent) => (
              <Grid item xs={12} sm={6} md={4} key={`${subagent.subagent_kind}-${subagent.id}`}>
                <SubagentCard
                  subagent={subagent}
                  showToggle={true}
                  showDelete={true}
                />
              </Grid>
            ))
          )}
        </Grid>
      )}

      {/* Create Custom Agent Dialog */}
      <Dialog
        open={createDialogOpen}
        onClose={() => setCreateDialogOpen(false)}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle>Create Custom Agent</DialogTitle>
        <DialogContent>
          <Box display="flex" flexDirection="column" gap={2} mt={1}>
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
              rows={3}
              placeholder="e.g., Specialized in database schema design and migration management with Alembic"
              helperText="Describe what this agent specializes in and what tasks it handles"
            />
            <Alert severity="info" sx={{ mt: 1 }}>
              The agent file will be automatically created in <code>.claude/agents/</code> with proper YAML frontmatter and configuration.
            </Alert>
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setCreateDialogOpen(false)}>Cancel</Button>
          <Button
            onClick={handleCreateSubagent}
            variant="contained"
            color="primary"
            disabled={
              creating ||
              !newSubagentName ||
              !newSubagentDescription
            }
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
      >
        <DialogTitle>Subagent Details</DialogTitle>
        <DialogContent>
          {selectedSubagent && (
            <Box mt={2}>
              <Typography variant="h6" gutterBottom>
                {selectedSubagent.name}
              </Typography>
              <Box mb={2}>
                <Chip label={selectedSubagent.category} size="small" sx={{ mr: 1 }} color="primary" />
                <Chip
                  label={selectedSubagent.subagent_kind === 'default' ? 'Default' : 'Custom'}
                  size="small"
                  color={selectedSubagent.subagent_kind === 'default' ? 'success' : 'info'}
                />
              </Box>
              <Typography variant="body1" paragraph>
                <strong>Description:</strong> {selectedSubagent.description}
              </Typography>
              <Typography variant="body2" paragraph>
                <strong>Subagent Type:</strong> {selectedSubagent.subagent_type}
              </Typography>
              {selectedSubagent.tools_available && selectedSubagent.tools_available.length > 0 && (
                <Box mb={2}>
                  <Typography variant="body2" gutterBottom>
                    <strong>Available Tools:</strong>
                  </Typography>
                  <Box display="flex" flexWrap="wrap" gap={1}>
                    {selectedSubagent.tools_available.map((tool) => (
                      <Chip key={tool} label={tool} size="small" variant="outlined" />
                    ))}
                  </Box>
                </Box>
              )}
              {selectedSubagent.recommended_for && selectedSubagent.recommended_for.length > 0 && (
                <Box mb={2}>
                  <Typography variant="body2" gutterBottom>
                    <strong>Recommended For:</strong>
                  </Typography>
                  <Box display="flex" flexWrap="wrap" gap={1}>
                    {selectedSubagent.recommended_for.map((rec) => (
                      <Chip key={rec} label={rec} size="small" variant="outlined" color="secondary" />
                    ))}
                  </Box>
                </Box>
              )}
              <Typography variant="caption" color="text.secondary" display="block">
                Status: {selectedSubagent.is_enabled ? 'Enabled' : 'Disabled'}
              </Typography>
              <Typography variant="caption" color="text.secondary" display="block">
                Created: {new Date(selectedSubagent.created_at).toLocaleString()}
              </Typography>
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setViewSubagentDialogOpen(false)}>Close</Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default Subagents;
