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
} from '@mui/material';
import AddIcon from '@mui/icons-material/Add';
import DeleteIcon from '@mui/icons-material/Delete';
import InfoIcon from '@mui/icons-material/Info';
import StarIcon from '@mui/icons-material/Star';
import StarBorderIcon from '@mui/icons-material/StarBorder';
import EditIcon from '@mui/icons-material/Edit';
import SearchIcon from '@mui/icons-material/Search';
import CodeIcon from '@mui/icons-material/Code';
import AutoAwesomeIcon from '@mui/icons-material/AutoAwesome';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import CategoryIcon from '@mui/icons-material/Category';
import BuildIcon from '@mui/icons-material/Build';
import CloseIcon from '@mui/icons-material/Close';
import axios from 'axios';
import { useProject } from '../context/ProjectContext';
import CodeEditorDialog from '../components/CodeEditorDialog';

// Remove /api suffix if present, since we add it manually in request paths
const API_BASE_URL = (process.env.REACT_APP_API_URL || 'http://localhost:3333').replace(/\/api$/, '');

// Utility to format error messages from API responses
const formatErrorMessage = (err: any): string => {
  const detail = err.response?.data?.detail;
  if (!detail) return err.message || 'Unknown error';
  if (typeof detail === 'string') return detail;
  return JSON.stringify(detail);
};

interface Skill {
  id: number;
  name: string;
  description: string;
  skill_type: 'default' | 'custom';
  category: string;
  file_path?: string;
  is_enabled: boolean;
  is_favorite: boolean;
  status?: string;
  created_by?: string;
  created_at: string;
  updated_at: string;
}

interface SkillsResponse {
  enabled: Skill[];
  available_default: Skill[];
  custom: Skill[];
  favorites: Skill[];
}

type FilterType = 'all' | 'default' | 'custom' | 'favorite' | 'enabled';

const Skills: React.FC = () => {
  const { selectedProject } = useProject();
  const theme = useTheme();
  const [activeFilter, setActiveFilter] = useState<FilterType>('all');
  const [searchQuery, setSearchQuery] = useState('');
  const [skills, setSkills] = useState<SkillsResponse>({
    enabled: [],
    available_default: [],
    custom: [],
    favorites: [],
  });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [createDialogOpen, setCreateDialogOpen] = useState(false);
  const [viewSkillDialogOpen, setViewSkillDialogOpen] = useState(false);
  const [selectedSkill, setSelectedSkill] = useState<Skill | null>(null);
  const [newSkillName, setNewSkillName] = useState('');
  const [newSkillDescription, setNewSkillDescription] = useState('');
  const [creating, setCreating] = useState(false);
  const [editDialogOpen, setEditDialogOpen] = useState(false);
  const [editingSkill, setEditingSkill] = useState<Skill | null>(null);

  // Fetch skills when project changes
  useEffect(() => {
    if (selectedProject?.id) {
      fetchSkills();
    }
  }, [selectedProject?.id]);

  const fetchSkills = async () => {
    if (!selectedProject?.id) return;

    setLoading(true);
    setError(null);
    try {
      const response = await axios.get<SkillsResponse>(
        `${API_BASE_URL}/api/projects/${selectedProject.id}/skills/`
      );
      setSkills(response.data);
    } catch (err: any) {
      setError('Failed to fetch skills: ' + formatErrorMessage(err));
    } finally {
      setLoading(false);
    }
  };

  const handleEnableSkill = async (skillId: number, skillType: 'default' | 'custom') => {
    if (!selectedProject?.id) return;

    try {
      await axios.post(
        `${API_BASE_URL}/api/projects/${selectedProject.id}/skills/enable/${skillId}`,
        null,
        { params: { skill_type: skillType } }
      );
      await fetchSkills(); // Refresh skills list
    } catch (err: any) {
      setError('Failed to enable skill: ' + formatErrorMessage(err));
    }
  };

  const handleDisableSkill = async (skillId: number, skillType: 'default' | 'custom') => {
    if (!selectedProject?.id) return;

    try {
      await axios.post(
        `${API_BASE_URL}/api/projects/${selectedProject.id}/skills/disable/${skillId}`,
        null,
        { params: { skill_type: skillType } }
      );
      await fetchSkills(); // Refresh skills list
    } catch (err: any) {
      setError('Failed to disable skill: ' + formatErrorMessage(err));
    }
  };

  const handleCreateSkill = async () => {
    if (!selectedProject?.id) return;

    setCreating(true);
    setError(null);
    try {
      await axios.post(
        `${API_BASE_URL}/api/projects/${selectedProject.id}/skills/create`,
        {
          name: newSkillName,
          description: newSkillDescription,
        }
      );
      setCreateDialogOpen(false);
      setNewSkillName('');
      setNewSkillDescription('');
      await fetchSkills(); // Refresh skills list
    } catch (err: any) {
      setError('Failed to create skill: ' + formatErrorMessage(err));
    } finally {
      setCreating(false);
    }
  };

  const handleDeleteSkill = async (skillId: number) => {
    if (!selectedProject?.id) return;
    if (!window.confirm('Are you sure you want to delete this custom skill?')) return;

    try {
      await axios.delete(
        `${API_BASE_URL}/api/projects/${selectedProject.id}/skills/${skillId}`
      );
      await fetchSkills(); // Refresh skills list
    } catch (err: any) {
      setError('Failed to delete skill: ' + formatErrorMessage(err));
    }
  };

  const handleSaveToFavorites = async (skillId: number, skillType: string) => {
    if (!selectedProject?.id) return;

    try {
      await axios.post(
        `${API_BASE_URL}/api/projects/${selectedProject.id}/skills/favorites/save`,
        null,
        {
          params: {
            skill_id: skillId,
            skill_type: skillType,
          },
        }
      );
      await fetchSkills(); // Refresh skills list
    } catch (err: any) {
      setError('Failed to save to favorites: ' + formatErrorMessage(err));
    }
  };

  const handleRemoveFromFavorites = async (skillId: number, skillType: string) => {
    if (!selectedProject?.id) return;

    try {
      await axios.post(
        `${API_BASE_URL}/api/projects/${selectedProject.id}/skills/favorites/remove`,
        null,
        {
          params: {
            skill_id: skillId,
            skill_type: skillType,
          },
        }
      );
      await fetchSkills(); // Refresh skills list
    } catch (err: any) {
      setError('Failed to remove from favorites: ' + formatErrorMessage(err));
    }
  };

  const handleViewSkill = (skill: Skill) => {
    setSelectedSkill(skill);
    setViewSkillDialogOpen(true);
  };

  // Filter skills based on active filter and search query
  const getFilteredSkills = (): Skill[] => {
    let filtered: Skill[] = [];

    switch (activeFilter) {
      case 'default':
        filtered = skills.available_default;
        break;
      case 'custom':
        filtered = skills.custom;
        break;
      case 'favorite':
        filtered = skills.favorites;
        break;
      case 'enabled':
        filtered = skills.enabled;
        break;
      case 'all':
      default:
        const allSkills = [
          ...skills.available_default,
          ...skills.custom,
        ];
        filtered = allSkills.filter(
          (skill, index, self) => self.findIndex(s => s.id === skill.id && s.skill_type === skill.skill_type) === index
        );
    }

    // Apply search filter
    if (searchQuery.trim()) {
      const query = searchQuery.toLowerCase();
      filtered = filtered.filter(
        (skill) =>
          skill.name.toLowerCase().includes(query) ||
          skill.description.toLowerCase().includes(query) ||
          skill.category.toLowerCase().includes(query)
      );
    }

    return filtered;
  };

  const filteredSkills = getFilteredSkills();

  // Statistics
  const stats = {
    total: skills.available_default.length + skills.custom.length,
    enabled: skills.enabled.length,
    favorites: skills.favorites.length,
    custom: skills.custom.length,
  };

  const SkillCard: React.FC<{
    skill: Skill;
    showToggle?: boolean;
    showDelete?: boolean;
    showSaveToFavorites?: boolean;
    showRemoveFromFavorites?: boolean;
  }> = ({
    skill,
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
          background: skill.is_enabled
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
              <CodeIcon sx={{ color: theme.palette.primary.main, fontSize: 28 }} />
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
                {skill.name}
                {skill.is_enabled && (
                  <Tooltip title="Enabled">
                    <CheckCircleIcon sx={{ fontSize: 18, color: theme.palette.success.main }} />
                  </Tooltip>
                )}
              </Typography>
              <Stack direction="row" spacing={0.5} flexWrap="wrap">
                <Chip
                  label={skill.category}
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
                  label={skill.skill_type === 'default' ? 'Default' : 'Custom'}
                  size="small"
                  sx={{
                    height: 22,
                    fontSize: '0.7rem',
                    fontWeight: 500,
                    background: skill.skill_type === 'default'
                      ? `linear-gradient(135deg, ${alpha(theme.palette.success.main, 0.15)}, ${alpha(theme.palette.success.main, 0.05)})`
                      : `linear-gradient(135deg, ${alpha(theme.palette.info.main, 0.15)}, ${alpha(theme.palette.info.main, 0.05)})`,
                    border: `1px solid ${alpha(
                      skill.skill_type === 'default' ? theme.palette.success.main : theme.palette.info.main,
                      0.2
                    )}`,
                    color: skill.skill_type === 'default' ? theme.palette.success.main : theme.palette.info.main,
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
                  onClick={() => handleSaveToFavorites(skill.id, skill.skill_type)}
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
                  onClick={() => handleRemoveFromFavorites(skill.id, skill.skill_type)}
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
            <Tooltip title="Edit skill code">
              <IconButton
                size="small"
                onClick={() => {
                  setEditingSkill(skill);
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
            {showDelete && skill.skill_type === 'custom' && (
              <Tooltip title="Delete custom skill">
                <IconButton
                  size="small"
                  onClick={() => handleDeleteSkill(skill.id)}
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
                onClick={() => handleViewSkill(skill)}
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
          {skill.description}
        </Typography>

        <Divider sx={{ my: 2 }} />

        {/* Metadata */}
        <Stack spacing={1}>
          {skill.status && skill.status !== 'active' && (
            <Chip
              label={skill.status}
              size="small"
              color={skill.status === 'creating' ? 'info' : 'error'}
              sx={{
                height: 22,
                fontSize: '0.7rem',
                fontWeight: 500,
                width: 'fit-content',
              }}
            />
          )}
        </Stack>

        {/* Toggle switch */}
        {showToggle && (
          <Box mt={2}>
            <FormControlLabel
              control={
                <Switch
                  checked={skill.is_enabled}
                  onChange={(e) => {
                    if (e.target.checked) {
                      handleEnableSkill(skill.id, skill.skill_type);
                    } else {
                      handleDisableSkill(skill.id, skill.skill_type);
                    }
                  }}
                  disabled={skill.status === 'creating'}
                  color="primary"
                />
              }
              label={
                <Typography variant="body2" fontWeight={500}>
                  {skill.is_enabled ? 'Enabled' : 'Disabled'}
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
                Skills Management
              </Typography>
              <Typography variant="body1" color="text.secondary">
                Manage and configure Claude Code skills for your project
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
                '&:disabled': {
                  background: theme.palette.action.disabledBackground,
                  boxShadow: 'none',
                },
              }}
            >
              Create Custom Skill
            </Button>
          </Stack>

          {/* Statistics Cards */}
          <Grid container spacing={2} mb={3}>
            {[
              { label: 'Total Skills', value: stats.total, color: theme.palette.primary.main },
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
                placeholder="Search skills by name, description, or category..."
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
                  aria-label="skill filter"
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
                    Default ({skills.available_default.length})
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

        {/* Skills Grid */}
        {loading ? (
          <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
            <CircularProgress size={48} />
          </Box>
        ) : (
          <Grid container spacing={3}>
            {filteredSkills.length === 0 ? (
              <Grid item xs={12}>
                <Paper
                  sx={{
                    p: 6,
                    textAlign: 'center',
                    borderRadius: 2,
                    background: alpha(theme.palette.background.paper, 0.5),
                  }}
                >
                  <CodeIcon sx={{ fontSize: 64, color: theme.palette.text.disabled, mb: 2 }} />
                  <Typography variant="h6" gutterBottom>
                    No skills found
                  </Typography>
                  <Typography variant="body2" color="text.secondary" mb={3}>
                    {searchQuery
                      ? 'Try adjusting your search query'
                      : activeFilter !== 'all'
                      ? 'Try changing the filter or create a custom skill'
                      : 'Create a custom skill to get started'}
                  </Typography>
                  {!searchQuery && selectedProject?.id && (
                    <Button variant="contained" startIcon={<AddIcon />} onClick={() => setCreateDialogOpen(true)}>
                      Create Custom Skill
                    </Button>
                  )}
                </Paper>
              </Grid>
            ) : (
              filteredSkills.map((skill) => (
                <Grid item xs={12} sm={6} lg={4} key={`${skill.skill_type}-${skill.id}`}>
                  <SkillCard
                    skill={skill}
                    showToggle={true}
                    showDelete={skill.skill_type === 'custom' && activeFilter !== 'enabled'}
                    showSaveToFavorites={!skill.is_favorite && activeFilter !== 'enabled' && activeFilter !== 'favorite'}
                    showRemoveFromFavorites={skill.is_favorite && activeFilter !== 'enabled'}
                  />
                </Grid>
              ))
            )}
          </Grid>
        )}
      </Container>

      {/* Create Custom Skill Dialog */}
      <Dialog
        open={createDialogOpen}
        onClose={() => !creating && setCreateDialogOpen(false)}
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
            Create Custom Skill
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Define a new specialized skill for your project
          </Typography>
        </DialogTitle>
        <DialogContent>
          <Stack spacing={3} mt={2}>
            <TextField
              autoFocus
              label="Skill Name"
              value={newSkillName}
              onChange={(e) => setNewSkillName(e.target.value)}
              fullWidth
              required
              placeholder="e.g., Database Migration Helper"
              helperText="A descriptive name for your custom skill"
            />
            <TextField
              label="Skill Description"
              value={newSkillDescription}
              onChange={(e) => setNewSkillDescription(e.target.value)}
              fullWidth
              required
              multiline
              rows={4}
              placeholder="e.g., Specialized in database schema design and migration management"
              helperText="Describe what this skill does and when to use it"
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
              This will create a new skill using Claude Code's /createSkill command. The skill will be created in your project's .claude/skills/ directory.
            </Alert>
          </Stack>
        </DialogContent>
        <DialogActions sx={{ px: 3, pb: 3 }}>
          <Button onClick={() => setCreateDialogOpen(false)} disabled={creating} sx={{ borderRadius: 2 }}>
            Cancel
          </Button>
          <Button
            onClick={handleCreateSkill}
            variant="contained"
            disabled={creating || !newSkillName || !newSkillDescription}
            sx={{
              borderRadius: 2,
              px: 3,
              background: `linear-gradient(135deg, ${theme.palette.primary.main}, ${theme.palette.primary.dark})`,
            }}
          >
            {creating ? <CircularProgress size={24} /> : 'Create Skill'}
          </Button>
        </DialogActions>
      </Dialog>

      {/* View Skill Details Dialog */}
      <Dialog
        open={viewSkillDialogOpen}
        onClose={() => setViewSkillDialogOpen(false)}
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
            Skill Details
          </Typography>
        </DialogTitle>
        <DialogContent>
          {selectedSkill && (
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
                  <CodeIcon sx={{ color: theme.palette.primary.main, fontSize: 36 }} />
                </Box>
                <Box flexGrow={1}>
                  <Typography variant="h5" fontWeight={600} gutterBottom>
                    {selectedSkill.name}
                  </Typography>
                  <Stack direction="row" spacing={1}>
                    <Chip label={selectedSkill.category} size="small" color="primary" />
                    <Chip
                      label={selectedSkill.skill_type === 'default' ? 'Default' : 'Custom'}
                      size="small"
                      color={selectedSkill.skill_type === 'default' ? 'success' : 'info'}
                    />
                    {selectedSkill.is_enabled && (
                      <Chip label="Enabled" size="small" color="success" icon={<CheckCircleIcon />} />
                    )}
                    {selectedSkill.is_favorite && (
                      <Chip label="Favorite" size="small" color="warning" icon={<StarIcon />} />
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
                <Typography variant="body1">{selectedSkill.description}</Typography>
              </Box>

              {/* File Path */}
              {selectedSkill.file_path && (
                <Box>
                  <Typography variant="subtitle2" color="text.secondary" gutterBottom>
                    File Path
                  </Typography>
                  <Typography variant="body2" fontFamily="monospace" sx={{ background: alpha(theme.palette.primary.main, 0.05), p: 1, borderRadius: 1 }}>
                    {selectedSkill.file_path}
                  </Typography>
                </Box>
              )}

              {/* Metadata */}
              <Box>
                <Typography variant="caption" color="text.secondary" display="block">
                  Created: {new Date(selectedSkill.created_at).toLocaleString()}
                </Typography>
                <Typography variant="caption" color="text.secondary" display="block">
                  Last Updated: {new Date(selectedSkill.updated_at).toLocaleString()}
                </Typography>
                {selectedSkill.created_by && (
                  <Typography variant="caption" color="text.secondary" display="block">
                    Created By: {selectedSkill.created_by}
                  </Typography>
                )}
              </Box>
            </Stack>
          )}
        </DialogContent>
        <DialogActions sx={{ px: 3, pb: 3 }}>
          <Button onClick={() => setViewSkillDialogOpen(false)} variant="contained" sx={{ borderRadius: 2 }}>
            Close
          </Button>
        </DialogActions>
      </Dialog>

      {/* Code Editor Dialog */}
      {editingSkill && (
        <CodeEditorDialog
          open={editDialogOpen}
          onClose={() => {
            setEditDialogOpen(false);
            setEditingSkill(null);
          }}
          title={`Edit Skill: ${editingSkill.name}`}
          itemName={editingSkill.name}
          itemType="skill"
          projectId={selectedProject?.id || ''}
          onSave={() => {
            fetchSkills();
          }}
        />
      )}
    </Box>
  );
};

export default Skills;
