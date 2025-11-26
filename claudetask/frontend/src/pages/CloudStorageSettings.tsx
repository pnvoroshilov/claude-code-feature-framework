import React, { useState, useEffect } from 'react';
import {
  Container,
  Typography,
  TextField,
  Button,
  Box,
  Alert,
  AlertTitle,
  CircularProgress,
  Paper,
  Stack,
  alpha,
  useTheme,
  Divider,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Chip,
  Snackbar,
} from '@mui/material';
import {
  Cloud as CloudIcon,
  CheckCircle as CheckCircleIcon,
  Cancel as CancelIcon,
  Storage as StorageIcon,
  Security as SecurityIcon,
  Speed as SpeedIcon,
} from '@mui/icons-material';
import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:3333/api';

interface TestResult {
  success: boolean;
  data?: {
    mongodb_connected: boolean;
    voyage_ai_valid: boolean;
    database_writable: boolean;
  };
  error?: string;
}

const CloudStorageSettings: React.FC = () => {
  const theme = useTheme();

  const [connectionString, setConnectionString] = useState('');
  const [databaseName, setDatabaseName] = useState('claudetask');
  const [voyageApiKey, setVoyageApiKey] = useState('');

  const [testing, setTesting] = useState(false);
  const [saving, setSaving] = useState(false);
  const [testResult, setTestResult] = useState<TestResult | null>(null);
  const [snackbar, setSnackbar] = useState<{ open: boolean; message: string; severity: 'success' | 'error' }>({
    open: false,
    message: '',
    severity: 'success',
  });

  // Load existing config on mount
  useEffect(() => {
    axios
      .get(`${API_BASE_URL}/settings/cloud-storage/config`)
      .then((response) => {
        if (response.data.configured) {
          setConnectionString(response.data.connection_string || '');
          setDatabaseName(response.data.database_name || 'claudetask');
          // API key is masked, don't populate
        }
      })
      .catch(() => {
        // Not configured yet, use defaults
      });
  }, []);

  const handleTestConnection = async () => {
    setTesting(true);
    setTestResult(null);

    try {
      const response = await axios.post(`${API_BASE_URL}/settings/cloud-storage/test`, {
        connection_string: connectionString,
        database_name: databaseName,
        voyage_api_key: voyageApiKey,
      });

      setTestResult({
        success: true,
        data: response.data,
      });
    } catch (error: any) {
      setTestResult({
        success: false,
        error: error.response?.data?.detail || error.message,
      });
    } finally {
      setTesting(false);
    }
  };

  const handleSaveConfiguration = async () => {
    setSaving(true);

    try {
      await axios.post(`${API_BASE_URL}/settings/cloud-storage/save`, {
        connection_string: connectionString,
        database_name: databaseName,
        voyage_api_key: voyageApiKey,
      });

      setSnackbar({
        open: true,
        message: 'Configuration saved successfully. Restart required for changes to take effect.',
        severity: 'success',
      });
    } catch (error: any) {
      setSnackbar({
        open: true,
        message: 'Failed to save configuration: ' + (error.response?.data?.detail || error.message),
        severity: 'error',
      });
    } finally {
      setSaving(false);
    }
  };

  const isFormValid = connectionString.trim() !== '' && databaseName.trim() !== '' && voyageApiKey.trim() !== '';

  return (
    <Container maxWidth="md" sx={{ py: 4 }}>
      {/* Header Section */}
      <Box sx={{ mb: 4 }}>
        <Box display="flex" alignItems="center" gap={2} mb={2}>
          <Box
            sx={{
              p: 1.5,
              borderRadius: 2,
              background: `linear-gradient(135deg, ${alpha(theme.palette.primary.main, 0.2)}, ${alpha(
                theme.palette.primary.main,
                0.1
              )})`,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
            }}
          >
            <CloudIcon sx={{ color: theme.palette.primary.main, fontSize: 32 }} />
          </Box>
          <Box>
            <Typography
              variant="h3"
              component="h1"
              sx={{
                fontWeight: 700,
                background: `linear-gradient(135deg, ${theme.palette.primary.main}, ${theme.palette.primary.light})`,
                WebkitBackgroundClip: 'text',
                WebkitTextFillColor: 'transparent',
                mb: 0.5,
              }}
            >
              Cloud Storage Configuration
            </Typography>
            <Typography
              variant="body1"
              sx={{
                color: alpha(theme.palette.text.secondary, 0.8),
              }}
            >
              Configure MongoDB Atlas and Voyage AI for cloud-based persistence
            </Typography>
          </Box>
        </Box>
      </Box>

      {/* Benefits Section */}
      <Paper
        sx={{
          p: 3,
          mb: 3,
          borderRadius: 2,
          background: `linear-gradient(145deg, ${alpha(theme.palette.info.main, 0.05)}, ${alpha(
            theme.palette.info.main,
            0.02
          )})`,
          border: `1px solid ${alpha(theme.palette.info.main, 0.15)}`,
        }}
      >
        <Typography variant="h6" gutterBottom sx={{ color: theme.palette.text.primary, fontWeight: 600 }}>
          Benefits of Cloud Storage
        </Typography>
        <List dense>
          <ListItem>
            <ListItemIcon>
              <StorageIcon sx={{ color: theme.palette.info.main }} />
            </ListItemIcon>
            <ListItemText
              primary="Cloud-based persistence with automatic backups"
              primaryTypographyProps={{ variant: 'body2', color: 'text.primary' }}
            />
          </ListItem>
          <ListItem>
            <ListItemIcon>
              <SpeedIcon sx={{ color: theme.palette.info.main }} />
            </ListItemIcon>
            <ListItemText
              primary="Enhanced vector search with 1024d embeddings (vs 384d local)"
              primaryTypographyProps={{ variant: 'body2', color: 'text.primary' }}
            />
          </ListItem>
          <ListItem>
            <ListItemIcon>
              <SecurityIcon sx={{ color: theme.palette.info.main }} />
            </ListItemIcon>
            <ListItemText
              primary="Centralized data access across multiple machines"
              primaryTypographyProps={{ variant: 'body2', color: 'text.primary' }}
            />
          </ListItem>
        </List>
      </Paper>

      {/* Configuration Form */}
      <Paper
        sx={{
          p: 4,
          borderRadius: 2,
          background: alpha(theme.palette.background.paper, 0.6),
          border: `1px solid ${alpha(theme.palette.divider, 0.1)}`,
        }}
      >
        <Stack spacing={3}>
          <TextField
            fullWidth
            type="password"
            label="MongoDB Connection String"
            placeholder="mongodb+srv://username:password@cluster.mongodb.net/"
            value={connectionString}
            onChange={(e) => setConnectionString(e.target.value)}
            sx={{
              '& .MuiOutlinedInput-root': {
                color: theme.palette.text.primary,
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
              '& .MuiInputLabel-root': {
                color: alpha(theme.palette.text.secondary, 0.7),
                '&.Mui-focused': { color: theme.palette.primary.main },
              },
              '& .MuiFormHelperText-root': {
                color: alpha(theme.palette.text.secondary, 0.6),
              },
            }}
            helperText="Format: mongodb+srv://user:password@cluster.mongodb.net/"
          />

          <TextField
            fullWidth
            label="Database Name"
            placeholder="claudetask"
            value={databaseName}
            onChange={(e) => setDatabaseName(e.target.value)}
            sx={{
              '& .MuiOutlinedInput-root': {
                color: theme.palette.text.primary,
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
              '& .MuiInputLabel-root': {
                color: alpha(theme.palette.text.secondary, 0.7),
                '&.Mui-focused': { color: theme.palette.primary.main },
              },
              '& .MuiFormHelperText-root': {
                color: alpha(theme.palette.text.secondary, 0.6),
              },
            }}
            helperText="Default: claudetask"
          />

          <TextField
            fullWidth
            type="password"
            label="Voyage AI API Key"
            placeholder="vo-..."
            value={voyageApiKey}
            onChange={(e) => setVoyageApiKey(e.target.value)}
            sx={{
              '& .MuiOutlinedInput-root': {
                color: theme.palette.text.primary,
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
              '& .MuiInputLabel-root': {
                color: alpha(theme.palette.text.secondary, 0.7),
                '&.Mui-focused': { color: theme.palette.primary.main },
              },
              '& .MuiFormHelperText-root': {
                color: alpha(theme.palette.text.secondary, 0.6),
              },
            }}
            helperText="Required for voyage-3-large embeddings (1024 dimensions)"
          />

          <Divider sx={{ my: 2 }} />

          <Box sx={{ display: 'flex', gap: 2 }}>
            <Button
              variant="outlined"
              onClick={handleTestConnection}
              disabled={!isFormValid || testing}
              startIcon={testing ? <CircularProgress size={16} /> : null}
              sx={{
                color: theme.palette.primary.main,
                border: `1px solid ${alpha(theme.palette.primary.main, 0.3)}`,
                textTransform: 'none',
                fontWeight: 600,
                py: 1.5,
                px: 3,
                borderRadius: 2,
                '&:hover': {
                  backgroundColor: alpha(theme.palette.primary.main, 0.1),
                  borderColor: theme.palette.primary.main,
                },
                '&:disabled': {
                  borderColor: alpha(theme.palette.action.disabled, 0.3),
                  color: alpha(theme.palette.text.disabled, 0.5),
                },
              }}
            >
              {testing ? 'Testing Connection...' : 'Test Connection'}
            </Button>

            <Button
              variant="contained"
              onClick={handleSaveConfiguration}
              disabled={!testResult?.success || saving}
              startIcon={saving ? <CircularProgress size={16} /> : null}
              sx={{
                background: `linear-gradient(135deg, ${theme.palette.primary.main}, ${theme.palette.primary.dark})`,
                color: '#fff',
                fontWeight: 600,
                textTransform: 'none',
                py: 1.5,
                px: 3,
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
                  transform: 'none',
                },
              }}
            >
              {saving ? 'Saving Configuration...' : 'Save Configuration'}
            </Button>
          </Box>

          {/* Test Result Display */}
          {testResult && (
            <Alert
              severity={testResult.success ? 'success' : 'error'}
              sx={{
                mt: 2,
                backgroundColor: alpha(
                  testResult.success ? theme.palette.success.main : theme.palette.error.main,
                  0.1
                ),
                border: `1px solid ${alpha(
                  testResult.success ? theme.palette.success.main : theme.palette.error.main,
                  0.3
                )}`,
                borderRadius: 2,
                '& .MuiAlert-icon': {
                  color: testResult.success ? theme.palette.success.main : theme.palette.error.main,
                },
              }}
            >
              <AlertTitle>{testResult.success ? 'Connection Successful' : 'Connection Failed'}</AlertTitle>
              {testResult.success && testResult.data ? (
                <Box>
                  <Stack spacing={1}>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                      <Typography variant="body2" sx={{ fontWeight: 600 }}>
                        MongoDB:
                      </Typography>
                      {testResult.data.mongodb_connected ? (
                        <Chip
                          label="Connected"
                          size="small"
                          icon={<CheckCircleIcon />}
                          sx={{
                            backgroundColor: alpha(theme.palette.success.main, 0.15),
                            color: theme.palette.success.main,
                            border: `1px solid ${alpha(theme.palette.success.main, 0.3)}`,
                            fontWeight: 600,
                          }}
                        />
                      ) : (
                        <Chip
                          label="Failed"
                          size="small"
                          icon={<CancelIcon />}
                          sx={{
                            backgroundColor: alpha(theme.palette.error.main, 0.15),
                            color: theme.palette.error.main,
                            border: `1px solid ${alpha(theme.palette.error.main, 0.3)}`,
                            fontWeight: 600,
                          }}
                        />
                      )}
                    </Box>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                      <Typography variant="body2" sx={{ fontWeight: 600 }}>
                        Voyage AI:
                      </Typography>
                      {testResult.data.voyage_ai_valid ? (
                        <Chip
                          label="Valid"
                          size="small"
                          icon={<CheckCircleIcon />}
                          sx={{
                            backgroundColor: alpha(theme.palette.success.main, 0.15),
                            color: theme.palette.success.main,
                            border: `1px solid ${alpha(theme.palette.success.main, 0.3)}`,
                            fontWeight: 600,
                          }}
                        />
                      ) : (
                        <Chip
                          label="Invalid"
                          size="small"
                          icon={<CancelIcon />}
                          sx={{
                            backgroundColor: alpha(theme.palette.error.main, 0.15),
                            color: theme.palette.error.main,
                            border: `1px solid ${alpha(theme.palette.error.main, 0.3)}`,
                            fontWeight: 600,
                          }}
                        />
                      )}
                    </Box>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                      <Typography variant="body2" sx={{ fontWeight: 600 }}>
                        Database Writable:
                      </Typography>
                      {testResult.data.database_writable ? (
                        <Chip
                          label="Yes"
                          size="small"
                          icon={<CheckCircleIcon />}
                          sx={{
                            backgroundColor: alpha(theme.palette.success.main, 0.15),
                            color: theme.palette.success.main,
                            border: `1px solid ${alpha(theme.palette.success.main, 0.3)}`,
                            fontWeight: 600,
                          }}
                        />
                      ) : (
                        <Chip
                          label="No"
                          size="small"
                          icon={<CancelIcon />}
                          sx={{
                            backgroundColor: alpha(theme.palette.error.main, 0.15),
                            color: theme.palette.error.main,
                            border: `1px solid ${alpha(theme.palette.error.main, 0.3)}`,
                            fontWeight: 600,
                          }}
                        />
                      )}
                    </Box>
                  </Stack>
                </Box>
              ) : (
                <Typography variant="body2">{testResult.error}</Typography>
              )}
            </Alert>
          )}

          {/* Info Alert */}
          <Alert
            severity="info"
            sx={{
              backgroundColor: alpha(theme.palette.info.main, 0.1),
              border: `1px solid ${alpha(theme.palette.info.main, 0.3)}`,
              borderRadius: 2,
              '& .MuiAlert-icon': { color: theme.palette.info.main },
            }}
          >
            <AlertTitle>Configuration Storage</AlertTitle>
            <Typography variant="body2">
              Configuration will be saved to the <code>.env</code> file. After saving, restart the backend
              server for changes to take effect.
            </Typography>
          </Alert>
        </Stack>
      </Paper>

      {/* Snackbar for notifications */}
      <Snackbar
        open={snackbar.open}
        autoHideDuration={6000}
        onClose={() => setSnackbar({ ...snackbar, open: false })}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}
      >
        <Alert
          onClose={() => setSnackbar({ ...snackbar, open: false })}
          severity={snackbar.severity}
          sx={{ width: '100%' }}
        >
          {snackbar.message}
        </Alert>
      </Snackbar>
    </Container>
  );
};

export default CloudStorageSettings;
