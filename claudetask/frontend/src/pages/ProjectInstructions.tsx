import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Button,
  TextField,
  Alert,
  CircularProgress,
  Stack,
  Container,
  alpha,
  useTheme,
  Paper,
} from '@mui/material';
import SaveIcon from '@mui/icons-material/Save';
import DescriptionIcon from '@mui/icons-material/Description';
import InfoIcon from '@mui/icons-material/Info';
import axios from 'axios';
import { useProject } from '../context/ProjectContext';

const API_BASE_URL = (process.env.REACT_APP_API_URL || 'http://localhost:3333').replace(/\/api$/, '');

const ProjectInstructions: React.FC = () => {
  const theme = useTheme();
  const { selectedProject } = useProject();
  const [instructions, setInstructions] = useState('');
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);

  useEffect(() => {
    if (selectedProject?.id) {
      fetchInstructions();
    }
  }, [selectedProject?.id]);

  const fetchInstructions = async () => {
    if (!selectedProject?.id) return;

    setLoading(true);
    setError(null);
    try {
      const response = await axios.get(
        `${API_BASE_URL}/api/projects/${selectedProject.id}/instructions/`
      );
      setInstructions(response.data.custom_instructions || '');
    } catch (err: any) {
      setError('Failed to fetch project instructions: ' + (err.response?.data?.detail || err.message));
    } finally {
      setLoading(false);
    }
  };

  const handleSave = async () => {
    if (!selectedProject?.id) return;

    setSaving(true);
    setError(null);
    setSuccessMessage(null);
    try {
      await axios.put(
        `${API_BASE_URL}/api/projects/${selectedProject.id}/instructions/`,
        {
          custom_instructions: instructions
        }
      );
      setSuccessMessage('Instructions saved successfully!');
      setTimeout(() => setSuccessMessage(null), 3000);
    } catch (err: any) {
      setError('Failed to save instructions: ' + (err.response?.data?.detail || err.message));
    } finally {
      setSaving(false);
    }
  };

  if (!selectedProject) {
    return (
      <Container maxWidth="xl" sx={{ py: 4 }}>
        <Box sx={{ mb: 5 }}>
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
            Project Instructions
          </Typography>
          <Typography
            variant="body1"
            sx={{
              color: alpha(theme.palette.text.secondary, 0.8),
              maxWidth: '600px',
            }}
          >
            Custom instructions for Claude when working on this project
          </Typography>
        </Box>
        <Alert
          severity="info"
          sx={{
            backgroundColor: alpha(theme.palette.info.main, 0.1),
            border: `1px solid ${alpha(theme.palette.info.main, 0.3)}`,
            borderRadius: 2,
            '& .MuiAlert-icon': { color: theme.palette.info.main },
          }}
        >
          Please select a project to edit instructions.
        </Alert>
      </Container>
    );
  }

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress sx={{ color: theme.palette.primary.main }} />
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
              Project Instructions
            </Typography>
            <Typography
              variant="body1"
              sx={{
                color: alpha(theme.palette.text.secondary, 0.8),
                maxWidth: '600px',
              }}
            >
              Custom instructions for Claude when working on{' '}
              <Typography
                component="span"
                sx={{
                  fontWeight: 600,
                  color: theme.palette.primary.main,
                }}
              >
                {selectedProject.name}
              </Typography>
            </Typography>
          </Box>
          <Button
            variant="contained"
            startIcon={saving ? <CircularProgress size={20} sx={{ color: '#fff' }} /> : <SaveIcon />}
            onClick={handleSave}
            disabled={saving}
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
            {saving ? 'Saving...' : 'Save Instructions'}
          </Button>
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

      {successMessage && (
        <Alert
          severity="success"
          sx={{
            mb: 3,
            backgroundColor: alpha(theme.palette.success.main, 0.1),
            border: `1px solid ${alpha(theme.palette.success.main, 0.3)}`,
            borderRadius: 2,
            '& .MuiAlert-icon': { color: theme.palette.success.main },
          }}
          onClose={() => setSuccessMessage(null)}
        >
          {successMessage}
        </Alert>
      )}

      {/* Main Editor Card */}
      <Paper
        sx={{
          p: 4,
          mb: 3,
          borderRadius: 2,
          background: alpha(theme.palette.background.paper, 0.6),
          border: `1px solid ${alpha(theme.palette.divider, 0.1)}`,
        }}
      >
        <Stack spacing={3}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
            <Box
              sx={{
                p: 1.5,
                borderRadius: 2,
                background: `linear-gradient(135deg, ${alpha(theme.palette.primary.main, 0.2)}, ${alpha(theme.palette.primary.main, 0.1)})`,
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
              }}
            >
              <DescriptionIcon sx={{ color: theme.palette.primary.main, fontSize: 28 }} />
            </Box>
            <Box>
              <Typography
                variant="h5"
                sx={{
                  fontWeight: 600,
                  color: theme.palette.text.primary,
                  mb: 0.5,
                }}
              >
                Custom Instructions
              </Typography>
              <Typography
                variant="body2"
                sx={{
                  color: alpha(theme.palette.text.secondary, 0.7),
                }}
              >
                These instructions will be referenced in CLAUDE.md and take priority over defaults
              </Typography>
            </Box>
          </Box>

          <TextField
            fullWidth
            multiline
            rows={20}
            value={instructions}
            onChange={(e) => setInstructions(e.target.value)}
            placeholder="Enter custom instructions for Claude...

Example:
- Always use TypeScript strict mode
- Follow our coding conventions in docs/CONVENTIONS.md
- Run tests before committing
- Use Material-UI for all UI components"
            variant="outlined"
            sx={{
              '& .MuiOutlinedInput-root': {
                color: theme.palette.text.primary,
                backgroundColor: alpha(theme.palette.background.default, 0.5),
                fontFamily: 'monospace',
                fontSize: '0.875rem',
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
        </Stack>
      </Paper>

      {/* Info Card */}
      <Paper
        sx={{
          p: 3,
          borderRadius: 2,
          background: `linear-gradient(145deg, ${alpha(theme.palette.info.main, 0.05)}, ${alpha(theme.palette.info.main, 0.02)})`,
          border: `1px solid ${alpha(theme.palette.info.main, 0.15)}`,
        }}
      >
        <Stack direction="row" spacing={2} alignItems="flex-start">
          <Box
            sx={{
              p: 1.5,
              borderRadius: 2,
              background: `linear-gradient(135deg, ${alpha(theme.palette.info.main, 0.2)}, ${alpha(theme.palette.info.main, 0.1)})`,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
            }}
          >
            <InfoIcon sx={{ color: theme.palette.info.main, fontSize: 28 }} />
          </Box>
          <Box sx={{ flex: 1 }}>
            <Typography
              variant="h6"
              sx={{
                fontWeight: 600,
                color: theme.palette.text.primary,
                mb: 1.5,
              }}
            >
              How It Works
            </Typography>
            <Stack spacing={1.5}>
              {[
                'Custom instructions are stored in the database for this project',
                'CLAUDE.md file will reference these instructions automatically',
                'Claude will prioritize these custom instructions when working on tasks',
                'Use this for project-specific guidelines, coding standards, or workflows',
              ].map((text, index) => (
                <Box key={index} sx={{ display: 'flex', alignItems: 'flex-start', gap: 1.5 }}>
                  <Box
                    sx={{
                      width: 6,
                      height: 6,
                      borderRadius: '50%',
                      backgroundColor: theme.palette.info.main,
                      mt: 1,
                    }}
                  />
                  <Typography
                    variant="body2"
                    sx={{
                      color: alpha(theme.palette.text.secondary, 0.8),
                      flex: 1,
                    }}
                  >
                    {text}
                  </Typography>
                </Box>
              ))}
            </Stack>
          </Box>
        </Stack>
      </Paper>
    </Container>
  );
};

export default ProjectInstructions;
