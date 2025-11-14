import React, { useState, useEffect } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Button,
  IconButton,
  Typography,
  Box,
  CircularProgress,
  Breadcrumbs,
  Link,
  Chip,
} from '@mui/material';
import {
  Folder as FolderIcon,
  FolderOpen as FolderOpenIcon,
  Home as HomeIcon,
  NavigateBefore as BackIcon,
  GitHub as GitIcon,
} from '@mui/icons-material';

interface DirectoryItem {
  name: string;
  path: string;
  is_git: boolean;
}

interface BrowseResult {
  current_path: string;
  parent_path: string | null;
  directories: DirectoryItem[];
  home_path: string;
  error?: string;
}

interface DirectoryBrowserProps {
  open: boolean;
  onClose: () => void;
  onSelectPath: (path: string) => void;
  initialPath?: string;
}

const DirectoryBrowser: React.FC<DirectoryBrowserProps> = ({
  open,
  onClose,
  onSelectPath,
  initialPath = '',
}) => {
  const [currentPath, setCurrentPath] = useState(initialPath);
  const [directories, setDirectories] = useState<DirectoryItem[]>([]);
  const [parentPath, setParentPath] = useState<string | null>(null);
  const [homePath, setHomePath] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const browseDirectory = async (path: string = '') => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetch('http://localhost:3333/api/browse-directory', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ path }),
      });

      const data: BrowseResult = await response.json();
      
      if (data.error) {
        setError(data.error);
        setDirectories([]);
      } else {
        setCurrentPath(data.current_path);
        setDirectories(data.directories);
        setParentPath(data.parent_path);
        setHomePath(data.home_path);
      }
    } catch (err) {
      setError('Failed to browse directory');
      console.error('Browse error:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (open) {
      browseDirectory(initialPath);
    }
  }, [open]);

  const handleSelectDirectory = (dir: DirectoryItem) => {
    browseDirectory(dir.path);
  };

  const handleGoBack = () => {
    if (parentPath) {
      browseDirectory(parentPath);
    }
  };

  const handleGoHome = () => {
    browseDirectory(homePath);
  };

  const handleSelectCurrent = () => {
    onSelectPath(currentPath);
    onClose();
  };

  const pathParts = currentPath.split('/').filter(Boolean);

  return (
    <Dialog
      open={open}
      onClose={onClose}
      maxWidth="md"
      fullWidth
      PaperProps={{
        sx: {
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
        }}
      >
        <Box display="flex" alignItems="center" justifyContent="space-between">
          <Typography variant="h6" sx={{ color: '#e2e8f0', fontWeight: 600 }}>
            Select Project Directory
          </Typography>
          <Box>
            <IconButton
              onClick={handleGoHome}
              disabled={loading}
              title="Go to Home"
              sx={{
                color: '#94a3b8',
                '&:hover': {
                  backgroundColor: 'rgba(99, 102, 241, 0.1)',
                  color: '#6366f1',
                },
                '&:disabled': {
                  color: '#475569',
                }
              }}
            >
              <HomeIcon />
            </IconButton>
            <IconButton
              onClick={handleGoBack}
              disabled={!parentPath || loading}
              title="Go Back"
              sx={{
                color: '#94a3b8',
                '&:hover': {
                  backgroundColor: 'rgba(99, 102, 241, 0.1)',
                  color: '#6366f1',
                },
                '&:disabled': {
                  color: '#475569',
                }
              }}
            >
              <BackIcon />
            </IconButton>
          </Box>
        </Box>

        {/* Breadcrumbs */}
        <Box sx={{ mt: 1 }}>
          <Breadcrumbs maxItems={3} itemsAfterCollapse={1}>
            {pathParts.map((part, index) => (
              <Typography key={index} variant="body2" sx={{ color: '#94a3b8' }}>
                {part}
              </Typography>
            ))}
          </Breadcrumbs>
        </Box>
      </DialogTitle>

      <DialogContent
        dividers
        sx={{
          backgroundColor: '#1e293b',
          borderColor: '#334155',
        }}
      >
        {loading && (
          <Box display="flex" justifyContent="center" py={3}>
            <CircularProgress sx={{ color: '#6366f1' }} />
          </Box>
        )}

        {error && (
          <Box py={2}>
            <Typography sx={{ color: '#f87171' }}>{error}</Typography>
          </Box>
        )}

        {!loading && !error && (
          <List>
            {directories.length === 0 ? (
              <ListItem>
                <ListItemText
                  secondary="No subdirectories found"
                  secondaryTypographyProps={{
                    sx: { color: '#94a3b8' }
                  }}
                />
              </ListItem>
            ) : (
              directories.map((dir) => (
                <ListItem
                  key={dir.path}
                  button
                  onClick={() => handleSelectDirectory(dir)}
                  sx={{
                    '&:hover': {
                      backgroundColor: 'rgba(99, 102, 241, 0.1)',
                    },
                    borderRadius: 1,
                    mb: 0.5,
                  }}
                >
                  <ListItemIcon>
                    <FolderIcon sx={{ color: '#6366f1' }} />
                  </ListItemIcon>
                  <ListItemText
                    primary={dir.name}
                    secondary={dir.path}
                    primaryTypographyProps={{
                      sx: { color: '#e2e8f0', fontWeight: 500 }
                    }}
                    secondaryTypographyProps={{
                      sx: { color: '#94a3b8' }
                    }}
                  />
                  {dir.is_git && (
                    <Chip
                      icon={<GitIcon />}
                      label="Git"
                      size="small"
                      variant="outlined"
                      sx={{
                        borderColor: '#10b981',
                        color: '#10b981',
                        backgroundColor: 'rgba(16, 185, 129, 0.1)',
                        '& .MuiChip-icon': {
                          color: '#10b981',
                        }
                      }}
                    />
                  )}
                </ListItem>
              ))
            )}
          </List>
        )}

        <Box
          sx={{
            mt: 2,
            p: 2,
            backgroundColor: '#0f172a',
            border: '1px solid #334155',
            borderRadius: 1,
          }}
        >
          <Typography variant="body2" sx={{ color: '#94a3b8', mb: 0.5 }}>
            <strong>Current Path:</strong>
          </Typography>
          <Typography variant="body2" sx={{ wordBreak: 'break-all', color: '#e2e8f0' }}>
            {currentPath || 'Not selected'}
          </Typography>
        </Box>
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
          onClick={onClose}
          sx={{
            color: '#94a3b8',
            textTransform: 'none',
            fontWeight: 500,
            '&:hover': {
              backgroundColor: 'rgba(148, 163, 184, 0.1)',
            }
          }}
        >
          Cancel
        </Button>
        <Button
          onClick={handleSelectCurrent}
          variant="contained"
          disabled={!currentPath}
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
          Select This Directory
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default DirectoryBrowser;