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
} from '@mui/material';
import AddIcon from '@mui/icons-material/Add';
import DeleteIcon from '@mui/icons-material/Delete';
import InfoIcon from '@mui/icons-material/Info';
import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:3333';

interface Skill {
  id: number;
  name: string;
  description: string;
  skill_type: 'default' | 'custom';
  category: string;
  file_path?: string;
  is_enabled: boolean;
  status?: string;
  created_by?: string;
  created_at: string;
  updated_at: string;
}

interface SkillsResponse {
  enabled: Skill[];
  available_default: Skill[];
  custom: Skill[];
}

const Skills: React.FC = () => {
  const [activeTab, setActiveTab] = useState(0);
  const [skills, setSkills] = useState<SkillsResponse>({
    enabled: [],
    available_default: [],
    custom: [],
  });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [createDialogOpen, setCreateDialogOpen] = useState(false);
  const [newSkillName, setNewSkillName] = useState('');
  const [newSkillDescription, setNewSkillDescription] = useState('');
  const [creating, setCreating] = useState(false);
  const [activeProjectId, setActiveProjectId] = useState<string | null>(null);

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

  // Fetch skills when project is loaded
  useEffect(() => {
    if (activeProjectId) {
      fetchSkills();
    }
  }, [activeProjectId]);

  const fetchSkills = async () => {
    if (!activeProjectId) return;

    setLoading(true);
    setError(null);
    try {
      const response = await axios.get<SkillsResponse>(
        `${API_BASE_URL}/api/projects/${activeProjectId}/skills/`
      );
      setSkills(response.data);
    } catch (err: any) {
      setError('Failed to fetch skills: ' + (err.response?.data?.detail || err.message));
    } finally {
      setLoading(false);
    }
  };

  const handleEnableSkill = async (skillId: number) => {
    if (!activeProjectId) return;

    try {
      await axios.post(
        `${API_BASE_URL}/api/projects/${activeProjectId}/skills/enable/${skillId}`
      );
      await fetchSkills(); // Refresh skills list
    } catch (err: any) {
      setError('Failed to enable skill: ' + (err.response?.data?.detail || err.message));
    }
  };

  const handleDisableSkill = async (skillId: number) => {
    if (!activeProjectId) return;

    try {
      await axios.post(
        `${API_BASE_URL}/api/projects/${activeProjectId}/skills/disable/${skillId}`
      );
      await fetchSkills(); // Refresh skills list
    } catch (err: any) {
      setError('Failed to disable skill: ' + (err.response?.data?.detail || err.message));
    }
  };

  const handleCreateSkill = async () => {
    if (!activeProjectId) return;

    setCreating(true);
    setError(null);
    try {
      await axios.post(
        `${API_BASE_URL}/api/projects/${activeProjectId}/skills/create`,
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
      setError('Failed to create skill: ' + (err.response?.data?.detail || err.message));
    } finally {
      setCreating(false);
    }
  };

  const handleDeleteSkill = async (skillId: number) => {
    if (!activeProjectId) return;
    if (!window.confirm('Are you sure you want to delete this custom skill?')) return;

    try {
      await axios.delete(
        `${API_BASE_URL}/api/projects/${activeProjectId}/skills/${skillId}`
      );
      await fetchSkills(); // Refresh skills list
    } catch (err: any) {
      setError('Failed to delete skill: ' + (err.response?.data?.detail || err.message));
    }
  };

  const SkillCard: React.FC<{ skill: Skill; showToggle?: boolean; showDelete?: boolean }> = ({
    skill,
    showToggle = false,
    showDelete = false,
  }) => (
    <Card sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      <CardContent sx={{ flexGrow: 1 }}>
        <Box display="flex" justifyContent="space-between" alignItems="start" mb={1}>
          <Box flexGrow={1}>
            <Typography variant="h6" component="div" gutterBottom>
              {skill.name}
            </Typography>
            <Chip
              label={skill.category}
              size="small"
              color="primary"
              variant="outlined"
              sx={{ mb: 1 }}
            />
          </Box>
          <Box display="flex" gap={1} alignItems="center">
            {skill.status && skill.status !== 'active' && (
              <Chip
                label={skill.status}
                size="small"
                color={skill.status === 'creating' ? 'info' : 'error'}
              />
            )}
            {showDelete && (
              <IconButton
                size="small"
                color="error"
                onClick={() => handleDeleteSkill(skill.id)}
              >
                <DeleteIcon />
              </IconButton>
            )}
          </Box>
        </Box>

        <Typography variant="body2" color="text.secondary" paragraph>
          {skill.description}
        </Typography>

        {skill.is_enabled && (
          <Chip
            label="Enabled"
            size="small"
            color="success"
            sx={{ mt: 1 }}
          />
        )}

        {showToggle && (
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
              />
            }
            label={skill.is_enabled ? 'Enabled' : 'Enable'}
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
        <Typography variant="h4">Skills Management</Typography>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={() => setCreateDialogOpen(true)}
          disabled={!activeProjectId}
        >
          Create Custom Skill
        </Button>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}

      {!activeProjectId && (
        <Alert severity="warning" sx={{ mb: 2 }}>
          No active project found. Please go to Projects and activate a project first.
        </Alert>
      )}

      <Tabs value={activeTab} onChange={(_, newValue) => setActiveTab(newValue)} sx={{ mb: 3 }}>
        <Tab label={`Default Skills (${skills.available_default.length})`} />
        <Tab label={`Custom Skills (${skills.custom.length})`} />
        <Tab label={`Enabled Skills (${skills.enabled.length})`} />
      </Tabs>

      {/* Default Skills Tab */}
      {activeTab === 0 && (
        <Grid container spacing={3}>
          {skills.available_default.length === 0 ? (
            <Grid item xs={12}>
              <Alert severity="info">
                No default skills available. Skills will be seeded on backend startup.
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
        <Grid container spacing={3}>
          {skills.custom.length === 0 ? (
            <Grid item xs={12}>
              <Alert severity="info">
                No custom skills created yet. Click "Create Custom Skill" to add your own.
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
        <Grid container spacing={3}>
          {skills.enabled.length === 0 ? (
            <Grid item xs={12}>
              <Alert severity="info">
                No skills enabled yet. Enable default or custom skills from their respective tabs.
              </Alert>
            </Grid>
          ) : (
            skills.enabled.map((skill) => (
              <Grid item xs={12} md={6} lg={4} key={skill.id}>
                <SkillCard skill={skill} />
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
      >
        <DialogTitle>Create Custom Skill</DialogTitle>
        <DialogContent>
          <Alert severity="info" sx={{ mb: 2 }}>
            <Typography variant="body2">
              This will create a new skill using Claude Code's /createSkill command.
              The skill will be created in your project's .claude/skills/ directory.
            </Typography>
          </Alert>
          <TextField
            autoFocus
            margin="dense"
            label="Skill Name"
            fullWidth
            variant="outlined"
            value={newSkillName}
            onChange={(e) => setNewSkillName(e.target.value)}
            disabled={creating}
            helperText="e.g., 'Database Migration Helper'"
            sx={{ mb: 2 }}
          />
          <TextField
            margin="dense"
            label="Description"
            fullWidth
            multiline
            rows={4}
            variant="outlined"
            value={newSkillDescription}
            onChange={(e) => setNewSkillDescription(e.target.value)}
            disabled={creating}
            helperText="Describe what this skill does and when to use it"
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setCreateDialogOpen(false)} disabled={creating}>
            Cancel
          </Button>
          <Button
            onClick={handleCreateSkill}
            variant="contained"
            disabled={!newSkillName || !newSkillDescription || creating}
          >
            {creating ? <CircularProgress size={24} /> : 'Create'}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default Skills;
