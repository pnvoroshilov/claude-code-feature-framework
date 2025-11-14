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
        sx: {
          height: '90vh',
          backgroundColor: '#1e293b',
          backgroundImage: 'none',
          border: '1px solid #334155',
        }
      }}
    >
      <DialogTitle
        sx={{
          backgroundColor: '#0f172a',
          borderBottom: '1px solid #334155',
          color: '#e2e8f0',
        }}
      >
        {title}
        {hasChanges && (
          <Typography variant="caption" sx={{ ml: 2, color: '#f59e0b' }}>
            (Unsaved changes)
          </Typography>
        )}
      </DialogTitle>

      <DialogContent
        dividers
        sx={{
          backgroundColor: '#1e293b',
          borderColor: '#334155',
        }}
      >
        {error && (
          <Alert
            severity="error"
            sx={{
              mb: 2,
              backgroundColor: 'rgba(239, 68, 68, 0.1)',
              border: '1px solid rgba(239, 68, 68, 0.3)',
              color: '#f87171',
              '& .MuiAlert-icon': {
                color: '#f87171',
              }
            }}
            onClose={() => setError(null)}
          >
            {error}
          </Alert>
        )}

        {success && (
          <Alert
            severity="success"
            sx={{
              mb: 2,
              backgroundColor: 'rgba(16, 185, 129, 0.1)',
              border: '1px solid rgba(16, 185, 129, 0.3)',
              color: '#34d399',
              '& .MuiAlert-icon': {
                color: '#34d399',
              }
            }}
            onClose={() => setSuccess(null)}
          >
            {success}
          </Alert>
        )}

        {loading ? (
          <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
            <CircularProgress sx={{ color: '#6366f1' }} />
          </Box>
        ) : (
          <>
            <Tabs
              value={activeTab}
              onChange={(_, newValue) => setActiveTab(newValue)}
              sx={{
                mb: 2,
                '& .MuiTab-root': {
                  color: '#94a3b8',
                  textTransform: 'none',
                  fontWeight: 500,
                  '&.Mui-selected': {
                    color: '#6366f1',
                  }
                },
                '& .MuiTabs-indicator': {
                  backgroundColor: '#6366f1',
                }
              }}
            >
              <Tab label="Code Editor" />
              <Tab label="Edit with Claude" />
            </Tabs>

            {/* Manual Editor Tab */}
            {activeTab === 0 && (
              <Box
                sx={{
                  height: 'calc(90vh - 280px)',
                  border: '1px solid #334155',
                  borderRadius: 1,
                  overflow: 'hidden',
                  backgroundColor: '#0f172a',
                }}
              >
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
                <Alert
                  severity="info"
                  sx={{
                    mb: 2,
                    backgroundColor: 'rgba(59, 130, 246, 0.1)',
                    border: '1px solid rgba(59, 130, 246, 0.3)',
                    color: '#60a5fa',
                    '& .MuiAlert-icon': {
                      color: '#60a5fa',
                    }
                  }}
                >
                  <Typography variant="body2" gutterBottom sx={{ color: '#e2e8f0' }}>
                    Describe what you want to change, add, or improve. Claude will intelligently edit the {itemType} while preserving its structure.
                  </Typography>
                  <Typography variant="body2" sx={{ mt: 1, color: '#e2e8f0' }}>
                    <strong>Examples:</strong>
                  </Typography>
                  <Typography variant="body2" component="div" sx={{ color: '#94a3b8' }}>
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
                  sx={{
                    mb: 2,
                    '& .MuiOutlinedInput-root': {
                      color: '#e2e8f0',
                      backgroundColor: '#0f172a',
                      '& fieldset': {
                        borderColor: '#334155',
                      },
                      '&:hover fieldset': {
                        borderColor: '#475569',
                      },
                      '&.Mui-focused fieldset': {
                        borderColor: '#6366f1',
                      }
                    },
                    '& .MuiInputLabel-root': {
                      color: '#94a3b8',
                      '&.Mui-focused': {
                        color: '#6366f1',
                      }
                    }
                  }}
                />

                <Button
                  variant="contained"
                  startIcon={saving ? <CircularProgress size={20} /> : <AutoFixHighIcon />}
                  onClick={handleEditWithClaude}
                  disabled={!editInstructions.trim() || saving}
                  fullWidth
                  size="large"
                  sx={{
                    backgroundColor: '#6366f1',
                    color: '#ffffff',
                    fontWeight: 600,
                    textTransform: 'none',
                    py: 1.5,
                    '&:hover': {
                      backgroundColor: '#4f46e5',
                    },
                    '&:disabled': {
                      backgroundColor: '#334155',
                      color: '#64748b',
                    }
                  }}
                >
                  {saving ? 'Editing with Claude...' : 'Edit with Claude'}
                </Button>

                <Typography variant="caption" sx={{ mt: 1, display: 'block', color: '#94a3b8' }}>
                  Note: This will execute the /{itemType === 'agent' ? 'edit-agent' : 'edit-skill'} command with your instructions.
                  Changes will be applied automatically and you can review them in the Code Editor tab.
                </Typography>
              </Box>
            )}
          </>
        )}
      </DialogContent>

      <DialogActions
        sx={{
          backgroundColor: '#0f172a',
          borderTop: '1px solid #334155',
          px: 3,
          py: 2,
        }}
      >
        <Button
          onClick={handleClose}
          disabled={saving}
          sx={{
            color: '#94a3b8',
            textTransform: 'none',
            fontWeight: 500,
            '&:hover': {
              backgroundColor: 'rgba(148, 163, 184, 0.1)',
            }
          }}
        >
          Close
        </Button>
        {activeTab === 0 && (
          <Button
            variant="contained"
            startIcon={saving ? <CircularProgress size={20} /> : <SaveIcon />}
            onClick={handleSave}
            disabled={!hasChanges || saving || loading}
            sx={{
              backgroundColor: '#6366f1',
              color: '#ffffff',
              fontWeight: 600,
              textTransform: 'none',
              px: 3,
              '&:hover': {
                backgroundColor: '#4f46e5',
              },
              '&:disabled': {
                backgroundColor: '#334155',
                color: '#64748b',
              }
            }}
          >
            {saving ? 'Saving...' : 'Save Changes'}
          </Button>
        )}
      </DialogActions>
    </Dialog>
  );
};

export default CodeEditorDialog;
