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
  alpha,
  useTheme,
} from '@mui/material';
import AddIcon from '@mui/icons-material/Add';
import DeleteIcon from '@mui/icons-material/Delete';
import InfoIcon from '@mui/icons-material/Info';
import StarIcon from '@mui/icons-material/Star';
import StarBorderIcon from '@mui/icons-material/StarBorder';
import EditIcon from '@mui/icons-material/Edit';
import CodeIcon from '@mui/icons-material/Code';
import AutoAwesomeIcon from '@mui/icons-material/AutoAwesome';
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

const Skills: React.FC = () => {
  const { selectedProject } = useProject();
  const theme = useTheme();
  const [activeTab, setActiveTab] = useState(0);
  const [skills, setSkills] = useState<SkillsResponse>({
    enabled: [],
    available_default: [],
    custom: [],
    favorites: [],
  });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [createDialogOpen, setCreateDialogOpen] = useState(false);
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

  const handleEnableSkill = async (skillId: number) => {
    if (!selectedProject?.id) return;

    try {
      await axios.post(
        `${API_BASE_URL}/api/projects/${selectedProject.id}/skills/enable/${skillId}`
      );
      await fetchSkills(); // Refresh skills list
    } catch (err: any) {
      setError('Failed to enable skill: ' + formatErrorMessage(err));
    }
  };

  const handleDisableSkill = async (skillId: number) => {
    if (!selectedProject?.id) return;

    try {
      await axios.post(
        `${API_BASE_URL}/api/projects/${selectedProject.id}/skills/disable/${skillId}`
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

  const SkillCard: React.FC<{ skill: Skill; showToggle?: boolean; showDelete?: boolean }> = ({
    skill,
    showToggle = false,
    showDelete = false,
  }) => {
    const getCategoryColor = (category: string) => {
      const colors: Record<string, string> = {
        'project': theme.palette.primary.main,
        'managed': theme.palette.secondary.main,
        'development': theme.palette.info.main,
        'testing': theme.palette.success.main,
        'documentation': theme.palette.warning.main,
      };
      return colors[category.toLowerCase()] || theme.palette.grey[500];
    };

    const getCategoryGradient = (category: string) => {
      const color = getCategoryColor(category);
      return `linear-gradient(135deg, ${alpha(color, 0.15)} 0%, ${alpha(color, 0.05)} 100%)`;
    };

    return (
      <Card
        sx={{
          height: '100%',
          display: 'flex',
          flexDirection: 'column',
          position: 'relative',
          overflow: 'visible',
          transition: 'all 0.4s cubic-bezier(0.34, 1.56, 0.64, 1)',
          background: skill.is_favorite
            ? `linear-gradient(135deg, ${alpha(theme.palette.warning.main, 0.08)} 0%, ${alpha(theme.palette.background.paper, 1)} 50%, ${alpha(theme.palette.warning.light, 0.05)} 100%)`
            : `linear-gradient(135deg, ${theme.palette.background.paper} 0%, ${alpha(theme.palette.background.paper, 0.95)} 100%)`,
          border: skill.is_favorite
            ? `2px solid ${alpha(theme.palette.warning.main, 0.4)}`
            : `1px solid ${alpha(theme.palette.divider, 0.12)}`,
          borderRadius: '16px',
          boxShadow: skill.is_favorite
            ? `0 8px 32px ${alpha(theme.palette.warning.main, 0.2)}, 0 2px 8px ${alpha(theme.palette.common.black, 0.05)}`
            : `0 4px 16px ${alpha(theme.palette.common.black, 0.04)}, 0 1px 4px ${alpha(theme.palette.common.black, 0.02)}`,
          backdropFilter: 'blur(8px)',
          '&:hover': {
            transform: 'translateY(-8px) scale(1.01)',
            boxShadow: skill.is_favorite
              ? `0 16px 48px ${alpha(theme.palette.warning.main, 0.3)}, 0 4px 16px ${alpha(theme.palette.common.black, 0.1)}`
              : `0 12px 40px ${alpha(theme.palette.primary.main, 0.15)}, 0 4px 12px ${alpha(theme.palette.common.black, 0.08)}`,
            border: `2px solid ${alpha(theme.palette.primary.main, 0.5)}`,
            background: skill.is_favorite
              ? `linear-gradient(135deg, ${alpha(theme.palette.warning.main, 0.12)} 0%, ${alpha(theme.palette.background.paper, 1)} 50%, ${alpha(theme.palette.warning.light, 0.08)} 100%)`
              : `linear-gradient(135deg, ${alpha(theme.palette.primary.main, 0.03)} 0%, ${theme.palette.background.paper} 100%)`,
          },
          '&::before': {
            content: '""',
            position: 'absolute',
            top: 0,
            left: 0,
            right: 0,
            height: '4px',
            background: getCategoryGradient(skill.category),
            borderRadius: '16px 16px 0 0',
            opacity: 0.8,
          },
        }}
      >
        {skill.is_favorite && (
          <Box
            sx={{
              position: 'absolute',
              top: -12,
              right: 20,
              background: `linear-gradient(135deg, ${theme.palette.warning.main} 0%, ${theme.palette.warning.light} 100%)`,
              borderRadius: '12px',
              padding: '6px 16px',
              display: 'flex',
              alignItems: 'center',
              gap: 0.75,
              boxShadow: `0 6px 20px ${alpha(theme.palette.warning.main, 0.5)}, 0 2px 8px ${alpha(theme.palette.common.black, 0.15)}`,
              zIndex: 1,
              animation: 'pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite',
              '@keyframes pulse': {
                '0%, 100%': {
                  opacity: 1,
                  transform: 'scale(1)',
                },
                '50%': {
                  opacity: 0.9,
                  transform: 'scale(1.05)',
                },
              },
            }}
          >
            <AutoAwesomeIcon sx={{ fontSize: 16, color: 'white', filter: 'drop-shadow(0 2px 4px rgba(0,0,0,0.2))' }} />
            <Typography variant="caption" sx={{ color: 'white', fontWeight: 700, fontSize: '0.75rem', letterSpacing: '0.5px' }}>
              FAVORITE
            </Typography>
          </Box>
        )}

        <CardContent sx={{ flexGrow: 1, p: 3.5, pt: skill.is_favorite ? 4 : 3.5 }}>
          <Box display="flex" justifyContent="space-between" alignItems="start" mb={2.5}>
            <Box flexGrow={1}>
              <Typography
                variant="h6"
                component="div"
                gutterBottom
                sx={{
                  fontWeight: 700,
                  fontSize: '1.25rem',
                  mb: 1.5,
                  lineHeight: 1.3,
                  background: `linear-gradient(135deg, ${theme.palette.text.primary} 0%, ${alpha(theme.palette.primary.main, 0.9)} 100%)`,
                  backgroundClip: 'text',
                  WebkitBackgroundClip: 'text',
                  WebkitTextFillColor: 'transparent',
                  letterSpacing: '-0.02em',
                }}
              >
                {skill.name}
              </Typography>
              <Box display="flex" gap={1} alignItems="center" flexWrap="wrap">
                <Chip
                  label={skill.category}
                  size="small"
                  icon={<CodeIcon sx={{ fontSize: 14 }} />}
                  sx={{
                    background: getCategoryGradient(skill.category),
                    border: `1.5px solid ${alpha(getCategoryColor(skill.category), 0.4)}`,
                    color: getCategoryColor(skill.category),
                    fontWeight: 700,
                    fontSize: '0.7rem',
                    height: 26,
                    borderRadius: '8px',
                    textTransform: 'uppercase',
                    letterSpacing: '0.5px',
                    transition: 'all 0.3s',
                    '& .MuiChip-icon': {
                      color: getCategoryColor(skill.category),
                    },
                    '&:hover': {
                      background: `linear-gradient(135deg, ${alpha(getCategoryColor(skill.category), 0.25)} 0%, ${alpha(getCategoryColor(skill.category), 0.1)} 100%)`,
                      transform: 'scale(1.05)',
                    },
                  }}
                />
                {skill.skill_type === 'custom' && (
                  <Chip
                    label="Custom"
                    size="small"
                    sx={{
                      height: 26,
                      fontSize: '0.7rem',
                      fontWeight: 700,
                      borderRadius: '8px',
                      background: `linear-gradient(135deg, ${alpha(theme.palette.secondary.main, 0.15)} 0%, ${alpha(theme.palette.secondary.main, 0.05)} 100%)`,
                      border: `1.5px solid ${alpha(theme.palette.secondary.main, 0.4)}`,
                      color: theme.palette.secondary.main,
                      textTransform: 'uppercase',
                      letterSpacing: '0.5px',
                    }}
                  />
                )}
              </Box>
            </Box>
            <Box display="flex" gap={0.5} alignItems="center" ml={1.5} flexShrink={0}>
              {skill.status && skill.status !== 'active' && (
                <Chip
                  label={skill.status}
                  size="small"
                  color={skill.status === 'creating' ? 'info' : 'error'}
                  sx={{
                    height: 26,
                    fontSize: '0.7rem',
                    fontWeight: 700,
                    borderRadius: '8px',
                    textTransform: 'uppercase',
                    letterSpacing: '0.5px',
                  }}
                />
              )}
              <Tooltip
                title={skill.is_favorite ? 'Remove from favorites' : 'Add to favorites'}
                arrow
                placement="top"
              >
                <IconButton
                  size="small"
                  sx={{
                    width: 36,
                    height: 36,
                    color: skill.is_favorite ? theme.palette.warning.main : theme.palette.action.disabled,
                    transition: 'all 0.3s cubic-bezier(0.34, 1.56, 0.64, 1)',
                    background: skill.is_favorite
                      ? alpha(theme.palette.warning.main, 0.1)
                      : 'transparent',
                    '&:hover': {
                      color: theme.palette.warning.main,
                      transform: 'scale(1.2) rotate(15deg)',
                      background: alpha(theme.palette.warning.main, 0.15),
                    },
                  }}
                  onClick={() => {
                    if (skill.is_favorite) {
                      handleRemoveFromFavorites(skill.id, skill.skill_type);
                    } else {
                      handleSaveToFavorites(skill.id, skill.skill_type);
                    }
                  }}
                >
                  {skill.is_favorite ? <StarIcon /> : <StarBorderIcon />}
                </IconButton>
              </Tooltip>
              <Tooltip title="Edit skill code" arrow placement="top">
                <IconButton
                  size="small"
                  sx={{
                    width: 36,
                    height: 36,
                    color: theme.palette.primary.main,
                    transition: 'all 0.3s cubic-bezier(0.34, 1.56, 0.64, 1)',
                    '&:hover': {
                      transform: 'scale(1.2)',
                      background: alpha(theme.palette.primary.main, 0.15),
                    },
                  }}
                  onClick={() => {
                    setEditingSkill(skill);
                    setEditDialogOpen(true);
                  }}
                >
                  <EditIcon />
                </IconButton>
              </Tooltip>
              {showDelete && (
                <Tooltip title="Delete skill" arrow placement="top">
                  <IconButton
                    size="small"
                    sx={{
                      width: 36,
                      height: 36,
                      color: theme.palette.error.main,
                      transition: 'all 0.3s cubic-bezier(0.34, 1.56, 0.64, 1)',
                      '&:hover': {
                        transform: 'scale(1.2)',
                        background: alpha(theme.palette.error.main, 0.15),
                      },
                    }}
                    onClick={() => handleDeleteSkill(skill.id)}
                  >
                    <DeleteIcon />
                  </IconButton>
                </Tooltip>
              )}
            </Box>
          </Box>

          <Typography
            variant="body2"
            color="text.secondary"
            paragraph
            sx={{
              lineHeight: 1.8,
              mb: 2.5,
              fontSize: '0.9rem',
              letterSpacing: '0.01em',
            }}
          >
            {skill.description}
          </Typography>

          {showToggle && (
            <Box
              sx={{
                mt: 'auto',
                pt: 2.5,
                borderTop: `1px solid ${alpha(theme.palette.divider, 0.15)}`,
              }}
            >
              <FormControlLabel
                control={
                  <Switch
                    checked={skill.is_enabled}
                    onChange={(e) => {
                      if (e.target.checked) {
                        handleEnableSkill(skill.id);
                      } else {
                        handleDisableSkill(skill.id);
                      }
                    }}
                    disabled={skill.status === 'creating'}
                    sx={{
                      '& .MuiSwitch-switchBase.Mui-checked': {
                        color: theme.palette.success.main,
                      },
                      '& .MuiSwitch-switchBase.Mui-checked + .MuiSwitch-track': {
                        backgroundColor: theme.palette.success.main,
                      },
                      '& .MuiSwitch-track': {
                        borderRadius: 12,
                      },
                      '& .MuiSwitch-thumb': {
                        boxShadow: `0 2px 8px ${alpha(theme.palette.common.black, 0.2)}`,
                      },
                    }}
                  />
                }
                label={
                  <Typography
                    variant="body2"
                    sx={{
                      fontWeight: 600,
                      fontSize: '0.85rem',
                      letterSpacing: '0.02em',
                      color: skill.is_enabled ? theme.palette.success.main : theme.palette.text.secondary,
                      transition: 'all 0.3s',
                    }}
                  >
                    {skill.is_enabled ? '✓ Enabled' : 'Enable Skill'}
                  </Typography>
                }
              />
            </Box>
          )}
        </CardContent>
      </Card>
    );
  };

  if (loading) {
    return (
      <Box
        display="flex"
        flexDirection="column"
        justifyContent="center"
        alignItems="center"
        minHeight="400px"
        gap={3}
      >
        <Box
          sx={{
            position: 'relative',
            width: 80,
            height: 80,
          }}
        >
          <CircularProgress
            size={80}
            thickness={3}
            sx={{
              color: theme.palette.primary.main,
              position: 'absolute',
              animationDuration: '1.5s',
            }}
          />
          <Box
            sx={{
              position: 'absolute',
              top: '50%',
              left: '50%',
              transform: 'translate(-50%, -50%)',
              width: 48,
              height: 48,
              borderRadius: '50%',
              background: `linear-gradient(135deg, ${alpha(theme.palette.primary.main, 0.2)} 0%, ${alpha(theme.palette.secondary.main, 0.2)} 100%)`,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
            }}
          >
            <CodeIcon sx={{ fontSize: 28, color: theme.palette.primary.main }} />
          </Box>
        </Box>
        <Typography
          variant="h6"
          sx={{
            fontWeight: 600,
            color: theme.palette.text.secondary,
            letterSpacing: '0.02em',
          }}
        >
          Loading Skills...
        </Typography>
      </Box>
    );
  }

  return (
    <Box>
      {/* Header Section */}
      <Box
        sx={{
          mb: 4,
          p: 4,
          borderRadius: 3,
          background: `linear-gradient(135deg, ${alpha(theme.palette.primary.main, 0.1)} 0%, ${alpha(theme.palette.secondary.main, 0.1)} 50%, ${alpha(theme.palette.primary.main, 0.05)} 100%)`,
          border: `1px solid ${alpha(theme.palette.divider, 0.15)}`,
          position: 'relative',
          overflow: 'hidden',
          '&::before': {
            content: '""',
            position: 'absolute',
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            background: `radial-gradient(circle at top right, ${alpha(theme.palette.secondary.main, 0.1)} 0%, transparent 60%)`,
            pointerEvents: 'none',
          },
        }}
      >
        <Box display="flex" justifyContent="space-between" alignItems="center" position="relative" zIndex={1}>
          <Box>
            <Typography
              variant="h3"
              sx={{
                fontWeight: 800,
                mb: 1.5,
                background: `linear-gradient(135deg, ${theme.palette.primary.main} 0%, ${theme.palette.secondary.main} 100%)`,
                backgroundClip: 'text',
                WebkitBackgroundClip: 'text',
                WebkitTextFillColor: 'transparent',
                letterSpacing: '-0.03em',
                fontSize: { xs: '2rem', md: '2.5rem' },
              }}
            >
              Skills Management
            </Typography>
            <Typography
              variant="body1"
              sx={{
                color: theme.palette.text.secondary,
                fontSize: '1rem',
                letterSpacing: '0.01em',
                display: 'flex',
                alignItems: 'center',
                gap: 1,
              }}
            >
              <CodeIcon sx={{ fontSize: 18 }} />
              Manage and configure your Claude Code skills
            </Typography>
          </Box>
          <Button
            variant="contained"
            size="large"
            startIcon={<AddIcon />}
            onClick={() => setCreateDialogOpen(true)}
            disabled={!selectedProject?.id}
            sx={{
              background: `linear-gradient(135deg, ${theme.palette.primary.main} 0%, ${theme.palette.primary.dark} 100%)`,
              boxShadow: `0 6px 20px ${alpha(theme.palette.primary.main, 0.4)}`,
              transition: 'all 0.4s cubic-bezier(0.34, 1.56, 0.64, 1)',
              borderRadius: 2,
              px: 3,
              py: 1.5,
              fontSize: '1rem',
              fontWeight: 700,
              letterSpacing: '0.02em',
              textTransform: 'none',
              '&:hover': {
                background: `linear-gradient(135deg, ${theme.palette.primary.dark} 0%, ${theme.palette.primary.main} 100%)`,
                boxShadow: `0 8px 28px ${alpha(theme.palette.primary.main, 0.6)}`,
                transform: 'translateY(-3px) scale(1.02)',
              },
              '&:disabled': {
                background: theme.palette.action.disabledBackground,
                boxShadow: 'none',
              },
            }}
          >
            Create Custom Skill
          </Button>
        </Box>
      </Box>

      {error && (
        <Alert
          severity="error"
          sx={{
            mb: 2,
            borderRadius: 2,
            border: `1px solid ${alpha(theme.palette.error.main, 0.3)}`,
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
            mb: 2,
            borderRadius: 2,
            border: `1px solid ${alpha(theme.palette.warning.main, 0.3)}`,
          }}
        >
          No active project found. Please go to Projects and activate a project first.
        </Alert>
      )}

      {/* Tabs Section */}
      <Box
        sx={{
          mb: 4,
          borderRadius: 3,
          background: `linear-gradient(135deg, ${alpha(theme.palette.background.paper, 0.8)} 0%, ${alpha(theme.palette.background.paper, 0.6)} 100%)`,
          backdropFilter: 'blur(20px)',
          border: `1px solid ${alpha(theme.palette.divider, 0.15)}`,
          boxShadow: `0 4px 16px ${alpha(theme.palette.common.black, 0.04)}`,
          overflow: 'hidden',
        }}
      >
        <Tabs
          value={activeTab}
          onChange={(_, newValue) => setActiveTab(newValue)}
          sx={{
            '& .MuiTabs-indicator': {
              height: 4,
              borderRadius: '4px 4px 0 0',
              background: `linear-gradient(90deg, ${theme.palette.primary.main} 0%, ${theme.palette.secondary.main} 100%)`,
              boxShadow: `0 -2px 12px ${alpha(theme.palette.primary.main, 0.4)}`,
            },
            '& .MuiTab-root': {
              textTransform: 'none',
              fontWeight: 700,
              fontSize: '1rem',
              minHeight: 64,
              transition: 'all 0.4s cubic-bezier(0.34, 1.56, 0.64, 1)',
              px: 3,
              '&:hover': {
                background: `linear-gradient(135deg, ${alpha(theme.palette.primary.main, 0.1)} 0%, ${alpha(theme.palette.secondary.main, 0.05)} 100%)`,
                transform: 'translateY(-2px)',
              },
              '&.Mui-selected': {
                color: theme.palette.primary.main,
                background: `linear-gradient(180deg, ${alpha(theme.palette.primary.main, 0.08)} 0%, transparent 100%)`,
              },
            },
          }}
        >
          <Tab
            label={
              <Box display="flex" alignItems="center" gap={1.5}>
                <Typography sx={{ fontSize: '1rem', fontWeight: 700, letterSpacing: '0.01em' }}>
                  Default Skills
                </Typography>
                <Chip
                  label={skills.available_default.length}
                  size="small"
                  sx={{
                    height: 24,
                    fontSize: '0.75rem',
                    fontWeight: 700,
                    borderRadius: '8px',
                    background: activeTab === 0
                      ? `linear-gradient(135deg, ${alpha(theme.palette.primary.main, 0.3)} 0%, ${alpha(theme.palette.primary.main, 0.2)} 100%)`
                      : alpha(theme.palette.action.active, 0.12),
                    border: activeTab === 0
                      ? `1.5px solid ${alpha(theme.palette.primary.main, 0.4)}`
                      : 'none',
                    transition: 'all 0.3s',
                  }}
                />
              </Box>
            }
          />
          <Tab
            label={
              <Box display="flex" alignItems="center" gap={1.5}>
                <Typography sx={{ fontSize: '1rem', fontWeight: 700, letterSpacing: '0.01em' }}>
                  Custom Skills
                </Typography>
                <Chip
                  label={skills.custom.length}
                  size="small"
                  sx={{
                    height: 24,
                    fontSize: '0.75rem',
                    fontWeight: 700,
                    borderRadius: '8px',
                    background: activeTab === 1
                      ? `linear-gradient(135deg, ${alpha(theme.palette.secondary.main, 0.3)} 0%, ${alpha(theme.palette.secondary.main, 0.2)} 100%)`
                      : alpha(theme.palette.action.active, 0.12),
                    border: activeTab === 1
                      ? `1.5px solid ${alpha(theme.palette.secondary.main, 0.4)}`
                      : 'none',
                    transition: 'all 0.3s',
                  }}
                />
              </Box>
            }
          />
          <Tab
            label={
              <Box display="flex" alignItems="center" gap={1.5}>
                <Typography sx={{ fontSize: '1rem', fontWeight: 700, letterSpacing: '0.01em' }}>
                  Enabled Skills
                </Typography>
                <Chip
                  label={skills.enabled.length}
                  size="small"
                  sx={{
                    height: 24,
                    fontSize: '0.75rem',
                    fontWeight: 700,
                    borderRadius: '8px',
                    background: activeTab === 2
                      ? `linear-gradient(135deg, ${alpha(theme.palette.success.main, 0.3)} 0%, ${alpha(theme.palette.success.main, 0.2)} 100%)`
                      : alpha(theme.palette.action.active, 0.12),
                    border: activeTab === 2
                      ? `1.5px solid ${alpha(theme.palette.success.main, 0.4)}`
                      : 'none',
                    transition: 'all 0.3s',
                  }}
                />
              </Box>
            }
          />
          <Tab
            label={
              <Box display="flex" alignItems="center" gap={1.5}>
                <StarIcon
                  sx={{
                    fontSize: 20,
                    color: activeTab === 3 ? theme.palette.warning.main : theme.palette.action.active,
                    transition: 'all 0.3s',
                  }}
                />
                <Typography sx={{ fontSize: '1rem', fontWeight: 700, letterSpacing: '0.01em' }}>
                  Favorites
                </Typography>
                <Chip
                  label={skills.favorites.length}
                  size="small"
                  sx={{
                    height: 24,
                    fontSize: '0.75rem',
                    fontWeight: 700,
                    borderRadius: '8px',
                    background: activeTab === 3
                      ? `linear-gradient(135deg, ${alpha(theme.palette.warning.main, 0.3)} 0%, ${alpha(theme.palette.warning.main, 0.2)} 100%)`
                      : alpha(theme.palette.action.active, 0.12),
                    border: activeTab === 3
                      ? `1.5px solid ${alpha(theme.palette.warning.main, 0.4)}`
                      : 'none',
                    transition: 'all 0.3s',
                  }}
                />
              </Box>
            }
          />
        </Tabs>
      </Box>

      {/* Default Skills Tab */}
      {activeTab === 0 && (
        <Grid container spacing={3} sx={{
          '& .MuiGrid-item': {
            animation: 'fadeInUp 0.4s ease-out',
            '@keyframes fadeInUp': {
              from: {
                opacity: 0,
                transform: 'translateY(20px)',
              },
              to: {
                opacity: 1,
                transform: 'translateY(0)',
              },
            },
          },
        }}>
          {skills.available_default.length === 0 ? (
            <Grid item xs={12}>
              <Alert
                severity="info"
                sx={{
                  borderRadius: 3,
                  background: `linear-gradient(135deg, ${alpha(theme.palette.info.main, 0.08)} 0%, ${alpha(theme.palette.info.light, 0.05)} 100%)`,
                  border: `2px solid ${alpha(theme.palette.info.main, 0.2)}`,
                  boxShadow: `0 4px 16px ${alpha(theme.palette.info.main, 0.1)}`,
                  '& .MuiAlert-icon': {
                    fontSize: 28,
                  },
                }}
              >
                <Typography variant="body1" sx={{ fontWeight: 600, mb: 0.5 }}>
                  No Default Skills Available
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Skills will be automatically seeded on backend startup. Please restart the backend service.
                </Typography>
              </Alert>
            </Grid>
          ) : (
            skills.available_default.map((skill) => (
              <Grid item xs={12} md={6} lg={4} key={skill.id}>
                <SkillCard skill={skill} showToggle={true} />
              </Grid>
            ))
          )}
        </Grid>
      )}

      {/* Custom Skills Tab */}
      {activeTab === 1 && (
        <Grid container spacing={3} sx={{
          '& .MuiGrid-item': {
            animation: 'fadeInUp 0.4s ease-out',
            '@keyframes fadeInUp': {
              from: {
                opacity: 0,
                transform: 'translateY(20px)',
              },
              to: {
                opacity: 1,
                transform: 'translateY(0)',
              },
            },
          },
        }}>
          {skills.custom.length === 0 ? (
            <Grid item xs={12}>
              <Alert
                severity="info"
                sx={{
                  borderRadius: 3,
                  background: `linear-gradient(135deg, ${alpha(theme.palette.secondary.main, 0.08)} 0%, ${alpha(theme.palette.secondary.light, 0.05)} 100%)`,
                  border: `2px solid ${alpha(theme.palette.secondary.main, 0.2)}`,
                  boxShadow: `0 4px 16px ${alpha(theme.palette.secondary.main, 0.1)}`,
                  '& .MuiAlert-icon': {
                    fontSize: 28,
                  },
                }}
              >
                <Typography variant="body1" sx={{ fontWeight: 600, mb: 0.5 }}>
                  No Custom Skills Created
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Click the "Create Custom Skill" button above to add your own custom skills to the project.
                </Typography>
              </Alert>
            </Grid>
          ) : (
            skills.custom.map((skill) => (
              <Grid item xs={12} md={6} lg={4} key={skill.id}>
                <SkillCard skill={skill} showToggle={true} showDelete={true} />
              </Grid>
            ))
          )}
        </Grid>
      )}

      {/* Enabled Skills Tab */}
      {activeTab === 2 && (
        <Grid container spacing={3} sx={{
          '& .MuiGrid-item': {
            animation: 'fadeInUp 0.4s ease-out',
            '@keyframes fadeInUp': {
              from: {
                opacity: 0,
                transform: 'translateY(20px)',
              },
              to: {
                opacity: 1,
                transform: 'translateY(0)',
              },
            },
          },
        }}>
          {skills.enabled.length === 0 ? (
            <Grid item xs={12}>
              <Alert
                severity="info"
                sx={{
                  borderRadius: 3,
                  background: `linear-gradient(135deg, ${alpha(theme.palette.success.main, 0.08)} 0%, ${alpha(theme.palette.success.light, 0.05)} 100%)`,
                  border: `2px solid ${alpha(theme.palette.success.main, 0.2)}`,
                  boxShadow: `0 4px 16px ${alpha(theme.palette.success.main, 0.1)}`,
                  '& .MuiAlert-icon': {
                    fontSize: 28,
                  },
                }}
              >
                <Typography variant="body1" sx={{ fontWeight: 600, mb: 0.5 }}>
                  No Skills Enabled
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Enable default or custom skills from their respective tabs to see them here.
                </Typography>
              </Alert>
            </Grid>
          ) : (
            skills.enabled.map((skill) => (
              <Grid item xs={12} md={6} lg={4} key={skill.id}>
                <SkillCard skill={skill} showToggle={true} />
              </Grid>
            ))
          )}
        </Grid>
      )}

      {/* Favorites Tab */}
      {activeTab === 3 && (
        <Grid container spacing={3} sx={{
          '& .MuiGrid-item': {
            animation: 'fadeInUp 0.4s ease-out',
            '@keyframes fadeInUp': {
              from: {
                opacity: 0,
                transform: 'translateY(20px)',
              },
              to: {
                opacity: 1,
                transform: 'translateY(0)',
              },
            },
          },
        }}>
          {skills.favorites.length === 0 ? (
            <Grid item xs={12}>
              <Alert
                severity="info"
                icon={<StarBorderIcon sx={{ fontSize: 28 }} />}
                sx={{
                  borderRadius: 3,
                  background: `linear-gradient(135deg, ${alpha(theme.palette.warning.main, 0.08)} 0%, ${alpha(theme.palette.warning.light, 0.05)} 100%)`,
                  border: `2px solid ${alpha(theme.palette.warning.main, 0.2)}`,
                  boxShadow: `0 4px 16px ${alpha(theme.palette.warning.main, 0.1)}`,
                  '& .MuiAlert-icon': {
                    fontSize: 28,
                  },
                }}
              >
                <Typography variant="body1" sx={{ fontWeight: 600, mb: 0.5 }}>
                  No Favorite Skills Yet
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Click the star icon on any skill card to add it to your favorites for quick access.
                </Typography>
              </Alert>
            </Grid>
          ) : (
            skills.favorites.map((skill) => (
              <Grid item xs={12} md={6} lg={4} key={`${skill.skill_type}-${skill.id}`}>
                <SkillCard skill={skill} showToggle={true} />
              </Grid>
            ))
          )}
        </Grid>
      )}

      {/* Create Custom Skill Dialog */}
      <Dialog
        open={createDialogOpen}
        onClose={() => !creating && setCreateDialogOpen(false)}
        maxWidth="sm"
        fullWidth
        PaperProps={{
          sx: {
            borderRadius: 4,
            background: `linear-gradient(135deg, ${alpha(theme.palette.background.paper, 0.98)} 0%, ${alpha(theme.palette.background.paper, 1)} 100%)`,
            backdropFilter: 'blur(20px)',
            boxShadow: `0 24px 48px ${alpha(theme.palette.common.black, 0.2)}`,
          },
        }}
      >
        <DialogTitle
          sx={{
            background: `linear-gradient(135deg, ${alpha(theme.palette.primary.main, 0.1)} 0%, ${alpha(theme.palette.secondary.main, 0.1)} 50%, ${alpha(theme.palette.primary.main, 0.05)} 100%)`,
            borderBottom: `1px solid ${alpha(theme.palette.divider, 0.15)}`,
            pb: 3,
            pt: 3,
          }}
        >
          <Box display="flex" alignItems="center" gap={2}>
            <Box
              sx={{
                width: 56,
                height: 56,
                borderRadius: 3,
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                background: `linear-gradient(135deg, ${theme.palette.primary.main} 0%, ${theme.palette.primary.dark} 100%)`,
                boxShadow: `0 8px 24px ${alpha(theme.palette.primary.main, 0.4)}`,
              }}
            >
              <AddIcon sx={{ color: 'white', fontSize: 32 }} />
            </Box>
            <Box>
              <Typography variant="h5" sx={{ fontWeight: 800, mb: 0.5, letterSpacing: '-0.02em' }}>
                Create Custom Skill
              </Typography>
              <Typography variant="body2" sx={{ color: theme.palette.text.secondary, fontSize: '0.95rem' }}>
                Add a new skill to your project
              </Typography>
            </Box>
          </Box>
        </DialogTitle>
        <DialogContent sx={{ mt: 3, px: 3, pb: 2 }}>
          <Alert
            severity="info"
            icon={<InfoIcon sx={{ fontSize: 24 }} />}
            sx={{
              mb: 3,
              borderRadius: 2.5,
              background: `linear-gradient(135deg, ${alpha(theme.palette.info.main, 0.08)} 0%, ${alpha(theme.palette.info.light, 0.05)} 100%)`,
              border: `2px solid ${alpha(theme.palette.info.main, 0.25)}`,
              boxShadow: `0 4px 12px ${alpha(theme.palette.info.main, 0.1)}`,
            }}
          >
            <Typography variant="body2" sx={{ fontWeight: 500, mb: 0.5 }}>
              About Skill Creation
            </Typography>
            <Typography variant="body2" color="text.secondary" sx={{ fontSize: '0.875rem' }}>
              This will create a new skill using Claude Code's /createSkill command.
              The skill will be created in your project's .claude/skills/ directory.
            </Typography>
          </Alert>
          <TextField
            autoFocus
            margin="dense"
            label="Skill Name"
            placeholder="e.g., Database Migration Helper"
            fullWidth
            variant="outlined"
            value={newSkillName}
            onChange={(e) => setNewSkillName(e.target.value)}
            disabled={creating}
            helperText="Choose a descriptive name for your skill"
            sx={{
              mb: 2.5,
              '& .MuiOutlinedInput-root': {
                borderRadius: 2.5,
                fontSize: '1rem',
                '& fieldset': {
                  borderWidth: 2,
                  borderColor: alpha(theme.palette.divider, 0.2),
                },
                '&:hover fieldset': {
                  borderColor: theme.palette.primary.main,
                },
                '&.Mui-focused fieldset': {
                  borderWidth: 2.5,
                  borderColor: theme.palette.primary.main,
                },
              },
              '& .MuiInputLabel-root': {
                fontWeight: 600,
              },
            }}
          />
          <TextField
            margin="dense"
            label="Description"
            placeholder="Describe what this skill does and when to use it..."
            fullWidth
            multiline
            rows={5}
            variant="outlined"
            value={newSkillDescription}
            onChange={(e) => setNewSkillDescription(e.target.value)}
            disabled={creating}
            helperText={`${newSkillDescription.length}/2000 characters - Provide a clear description of the skill's purpose and usage`}
            error={newSkillDescription.length > 2000}
            inputProps={{ maxLength: 2000 }}
            sx={{
              '& .MuiOutlinedInput-root': {
                borderRadius: 2.5,
                fontSize: '1rem',
                '& fieldset': {
                  borderWidth: 2,
                  borderColor: alpha(theme.palette.divider, 0.2),
                },
                '&:hover fieldset': {
                  borderColor: theme.palette.primary.main,
                },
                '&.Mui-focused fieldset': {
                  borderWidth: 2.5,
                  borderColor: theme.palette.primary.main,
                },
              },
              '& .MuiInputLabel-root': {
                fontWeight: 600,
              },
            }}
          />
        </DialogContent>
        <DialogActions
          sx={{
            p: 3,
            pt: 2.5,
            borderTop: `1px solid ${alpha(theme.palette.divider, 0.15)}`,
            gap: 1.5,
          }}
        >
          <Button
            onClick={() => setCreateDialogOpen(false)}
            disabled={creating}
            size="large"
            sx={{
              borderRadius: 2.5,
              textTransform: 'none',
              fontWeight: 700,
              fontSize: '1rem',
              px: 3,
              py: 1.25,
              color: theme.palette.text.secondary,
              '&:hover': {
                background: alpha(theme.palette.action.active, 0.08),
              },
            }}
          >
            Cancel
          </Button>
          <Button
            onClick={handleCreateSkill}
            variant="contained"
            size="large"
            disabled={!newSkillName || !newSkillDescription || creating}
            sx={{
              borderRadius: 2.5,
              textTransform: 'none',
              fontWeight: 700,
              fontSize: '1rem',
              px: 4,
              py: 1.25,
              background: `linear-gradient(135deg, ${theme.palette.primary.main} 0%, ${theme.palette.primary.dark} 100%)`,
              boxShadow: `0 6px 20px ${alpha(theme.palette.primary.main, 0.4)}`,
              minWidth: 120,
              transition: 'all 0.3s',
              '&:hover': {
                background: `linear-gradient(135deg, ${theme.palette.primary.dark} 0%, ${theme.palette.primary.main} 100%)`,
                boxShadow: `0 8px 28px ${alpha(theme.palette.primary.main, 0.6)}`,
                transform: 'translateY(-2px)',
              },
              '&:disabled': {
                background: theme.palette.action.disabledBackground,
                boxShadow: 'none',
              },
            }}
          >
            {creating ? (
              <Box display="flex" alignItems="center" gap={1.5}>
                <CircularProgress size={20} sx={{ color: 'white' }} />
                <span>Creating...</span>
              </Box>
            ) : (
              'Create Skill'
            )}
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
