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
} from '@mui/material';
import SaveIcon from '@mui/icons-material/Save';
import axios from 'axios';
import { useProject } from '../context/ProjectContext';

// Remove /api suffix if present, since we add it manually in request paths
const API_BASE_URL = (process.env.REACT_APP_API_URL || 'http://localhost:3333').replace(/\/api$/, '');

const ProjectInstructions: React.FC = () => {
  const { selectedProject } = useProject();
  const [instructions, setInstructions] = useState('');
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);

  // Fetch instructions when project changes
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
      // Auto-hide success message after 3 seconds
      setTimeout(() => setSuccessMessage(null), 3000);
    } catch (err: any) {
      setError('Failed to save instructions: ' + (err.response?.data?.detail || err.message));
    } finally {
      setSaving(false);
    }
  };

  if (!selectedProject) {
    return (
      <Box>
        <Typography variant="h4" gutterBottom>
          Project Instructions
        </Typography>
        <Alert severity="info">
          Please select a project to edit instructions.
        </Alert>
      </Box>
    );
  }

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Project Instructions
      </Typography>

      <Typography variant="body2" color="text.secondary" gutterBottom sx={{ mb: 2 }}>
        Custom instructions for Claude when working on this project. These instructions will be
        referenced in CLAUDE.md and will take priority over default instructions.
      </Typography>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}

      {successMessage && (
        <Alert severity="success" sx={{ mb: 2 }} onClose={() => setSuccessMessage(null)}>
          {successMessage}
        </Alert>
      )}

      <Card>
        <CardContent>
          <Stack spacing={2}>
            <Typography variant="h6" gutterBottom>
              Custom Instructions for {selectedProject.name}
            </Typography>

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
                  fontFamily: 'monospace',
                  fontSize: '0.875rem',
                }
              }}
            />

            <Box display="flex" justifyContent="flex-end" gap={1}>
              <Button
                variant="contained"
                color="primary"
                startIcon={saving ? <CircularProgress size={20} /> : <SaveIcon />}
                onClick={handleSave}
                disabled={saving}
              >
                {saving ? 'Saving...' : 'Save Instructions'}
              </Button>
            </Box>
          </Stack>
        </CardContent>
      </Card>

      <Card sx={{ mt: 2 }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            How It Works
          </Typography>
          <Typography variant="body2" color="text.secondary" component="div">
            <ul>
              <li>Custom instructions are stored in the database for this project</li>
              <li>CLAUDE.md file will reference these instructions automatically</li>
              <li>Claude will prioritize these custom instructions when working on tasks</li>
              <li>Use this for project-specific guidelines, coding standards, or workflows</li>
            </ul>
          </Typography>
        </CardContent>
      </Card>
    </Box>
  );
};

export default ProjectInstructions;
