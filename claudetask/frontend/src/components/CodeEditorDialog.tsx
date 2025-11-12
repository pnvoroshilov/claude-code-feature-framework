import React, { useState, useEffect } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  TextField,
  Box,
  Alert,
  CircularProgress,
  Tabs,
  Tab,
  Typography,
} from '@mui/material';
import Editor from '@monaco-editor/react';
import AutoFixHighIcon from '@mui/icons-material/AutoFixHigh';
import SaveIcon from '@mui/icons-material/Save';

interface CodeEditorDialogProps {
  open: boolean;
  onClose: () => void;
  title: string;
  itemName: string;
  itemType: 'agent' | 'skill';
  projectId: string;
  onSave: () => void;
}

const API_BASE_URL = (process.env.REACT_APP_API_URL || 'http://localhost:3333').replace(/\/api$/, '');

const CodeEditorDialog: React.FC<CodeEditorDialogProps> = ({
  open,
  onClose,
  title,
  itemName,
  itemType,
  projectId,
  onSave,
}) => {
  const [activeTab, setActiveTab] = useState(0);
  const [content, setContent] = useState('');
  const [originalContent, setOriginalContent] = useState('');
  const [editInstructions, setEditInstructions] = useState('');
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  // Fetch content when dialog opens
  useEffect(() => {
    if (open && itemName && projectId) {
      fetchContent();
    }
  }, [open, itemName, projectId]);

  const fetchContent = async () => {
    setLoading(true);
    setError(null);

    try {
      const endpoint = itemType === 'agent'
        ? `${API_BASE_URL}/api/projects/${projectId}/editor/agent/${encodeURIComponent(itemName)}/content`
        : `${API_BASE_URL}/api/projects/${projectId}/editor/skill/${encodeURIComponent(itemName)}/content`;

      const response = await fetch(endpoint);
      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || 'Failed to fetch content');
      }

      setContent(data.content);
      setOriginalContent(data.content);
    } catch (err: any) {
      setError('Failed to load content: ' + err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleSave = async () => {
    if (!content.trim()) {
      setError('Content cannot be empty');
      return;
    }

    setSaving(true);
    setError(null);
    setSuccess(null);

    try {
      const endpoint = itemType === 'agent'
        ? `${API_BASE_URL}/api/projects/${projectId}/editor/agent/save`
        : `${API_BASE_URL}/api/projects/${projectId}/editor/skill/save`;

      const response = await fetch(endpoint, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          name: itemName,
          content: content,
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || 'Failed to save');
      }

      setSuccess(data.message || 'Saved successfully!');
      setOriginalContent(content);

      // Notify parent to refresh data
      setTimeout(() => {
        onSave();
        onClose();
      }, 1000);

    } catch (err: any) {
      setError('Failed to save: ' + err.message);
    } finally {
      setSaving(false);
    }
  };

  const handleEditWithClaude = async () => {
    if (!editInstructions.trim()) {
      setError('Please provide edit instructions');
      return;
    }

    setSaving(true);
    setError(null);
    setSuccess(null);

    try {
      const endpoint = itemType === 'agent'
        ? `${API_BASE_URL}/api/projects/${projectId}/editor/agent/edit`
        : `${API_BASE_URL}/api/projects/${projectId}/editor/skill/edit`;

      const response = await fetch(endpoint, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          name: itemName,
          instructions: editInstructions,
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || 'Failed to edit with Claude');
      }

      setSuccess(data.message || 'Edited successfully with Claude!');
      setEditInstructions('');

      // Reload content to show changes
      await fetchContent();

      // Notify parent to refresh data
      setTimeout(() => {
        onSave();
      }, 1000);

    } catch (err: any) {
      setError('Failed to edit with Claude: ' + err.message);
    } finally {
      setSaving(false);
    }
  };

  const handleClose = () => {
    if (content !== originalContent) {
      if (window.confirm('You have unsaved changes. Are you sure you want to close?')) {
        onClose();
      }
    } else {
      onClose();
    }
  };

  const hasChanges = content !== originalContent;

  return (
    <Dialog
      open={open}
      onClose={handleClose}
      maxWidth="lg"
      fullWidth
      PaperProps={{
        sx: { height: '90vh' }
      }}
    >
      <DialogTitle>
        {title}
        {hasChanges && (
          <Typography variant="caption" color="warning.main" sx={{ ml: 2 }}>
            (Unsaved changes)
          </Typography>
        )}
      </DialogTitle>

      <DialogContent dividers>
        {error && (
          <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError(null)}>
            {error}
          </Alert>
        )}

        {success && (
          <Alert severity="success" sx={{ mb: 2 }} onClose={() => setSuccess(null)}>
            {success}
          </Alert>
        )}

        {loading ? (
          <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
            <CircularProgress />
          </Box>
        ) : (
          <>
            <Tabs value={activeTab} onChange={(_, newValue) => setActiveTab(newValue)} sx={{ mb: 2 }}>
              <Tab label="Code Editor" />
              <Tab label="Edit with Claude" />
            </Tabs>

            {/* Manual Editor Tab */}
            {activeTab === 0 && (
              <Box sx={{ height: 'calc(90vh - 280px)', border: '1px solid', borderColor: 'divider', borderRadius: 1 }}>
                <Editor
                  height="100%"
                  defaultLanguage="markdown"
                  value={content}
                  onChange={(value) => setContent(value || '')}
                  theme="vs-dark"
                  options={{
                    minimap: { enabled: true },
                    fontSize: 14,
                    wordWrap: 'on',
                    scrollBeyondLastLine: false,
                    automaticLayout: true,
                  }}
                />
              </Box>
            )}

            {/* Edit with Claude Tab */}
            {activeTab === 1 && (
              <Box>
                <Alert severity="info" sx={{ mb: 2 }}>
                  <Typography variant="body2" gutterBottom>
                    Describe what you want to change, add, or improve. Claude will intelligently edit the {itemType} while preserving its structure.
                  </Typography>
                  <Typography variant="body2" sx={{ mt: 1 }}>
                    <strong>Examples:</strong>
                  </Typography>
                  <Typography variant="body2" component="div">
                    <ul style={{ marginTop: 4, marginBottom: 0 }}>
                      <li>"Add examples for React Server Components"</li>
                      <li>"Update to use TypeScript 5 features"</li>
                      <li>"Add section on error handling best practices"</li>
                      <li>"Remove deprecated API references"</li>
                    </ul>
                  </Typography>
                </Alert>

                <TextField
                  fullWidth
                  multiline
                  rows={8}
                  variant="outlined"
                  label="Edit Instructions"
                  placeholder="Describe the changes you want Claude to make..."
                  value={editInstructions}
                  onChange={(e) => setEditInstructions(e.target.value)}
                  disabled={saving}
                  sx={{ mb: 2 }}
                />

                <Button
                  variant="contained"
                  startIcon={saving ? <CircularProgress size={20} /> : <AutoFixHighIcon />}
                  onClick={handleEditWithClaude}
                  disabled={!editInstructions.trim() || saving}
                  fullWidth
                  size="large"
                >
                  {saving ? 'Editing with Claude...' : 'Edit with Claude'}
                </Button>

                <Typography variant="caption" color="text.secondary" sx={{ mt: 1, display: 'block' }}>
                  Note: This will execute the /{itemType === 'agent' ? 'edit-agent' : 'edit-skill'} command with your instructions.
                  Changes will be applied automatically and you can review them in the Code Editor tab.
                </Typography>
              </Box>
            )}
          </>
        )}
      </DialogContent>

      <DialogActions>
        <Button onClick={handleClose} disabled={saving}>
          Close
        </Button>
        {activeTab === 0 && (
          <Button
            variant="contained"
            startIcon={saving ? <CircularProgress size={20} /> : <SaveIcon />}
            onClick={handleSave}
            disabled={!hasChanges || saving || loading}
          >
            {saving ? 'Saving...' : 'Save Changes'}
          </Button>
        )}
      </DialogActions>
    </Dialog>
  );
};

export default CodeEditorDialog;
