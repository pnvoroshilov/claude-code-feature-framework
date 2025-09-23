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
    <Dialog open={open} onClose={onClose} maxWidth="md" fullWidth>
      <DialogTitle>
        <Box display="flex" alignItems="center" justifyContent="space-between">
          <Typography variant="h6">Select Project Directory</Typography>
          <Box>
            <IconButton onClick={handleGoHome} disabled={loading} title="Go to Home">
              <HomeIcon />
            </IconButton>
            <IconButton onClick={handleGoBack} disabled={!parentPath || loading} title="Go Back">
              <BackIcon />
            </IconButton>
          </Box>
        </Box>
        
        {/* Breadcrumbs */}
        <Box sx={{ mt: 1 }}>
          <Breadcrumbs maxItems={3} itemsAfterCollapse={1}>
            {pathParts.map((part, index) => (
              <Typography key={index} color="text.secondary" variant="body2">
                {part}
              </Typography>
            ))}
          </Breadcrumbs>
        </Box>
      </DialogTitle>

      <DialogContent dividers>
        {loading && (
          <Box display="flex" justifyContent="center" py={3}>
            <CircularProgress />
          </Box>
        )}

        {error && (
          <Box py={2}>
            <Typography color="error">{error}</Typography>
          </Box>
        )}

        {!loading && !error && (
          <List>
            {directories.length === 0 ? (
              <ListItem>
                <ListItemText secondary="No subdirectories found" />
              </ListItem>
            ) : (
              directories.map((dir) => (
                <ListItem
                  key={dir.path}
                  button
                  onClick={() => handleSelectDirectory(dir)}
                  sx={{
                    '&:hover': {
                      bgcolor: 'action.hover',
                    },
                  }}
                >
                  <ListItemIcon>
                    <FolderIcon />
                  </ListItemIcon>
                  <ListItemText
                    primary={dir.name}
                    secondary={dir.path}
                  />
                  {dir.is_git && (
                    <Chip
                      icon={<GitIcon />}
                      label="Git"
                      size="small"
                      color="primary"
                      variant="outlined"
                    />
                  )}
                </ListItem>
              ))
            )}
          </List>
        )}

        <Box sx={{ mt: 2, p: 2, bgcolor: 'grey.100', borderRadius: 1 }}>
          <Typography variant="body2" color="text.secondary">
            <strong>Current Path:</strong>
          </Typography>
          <Typography variant="body2" sx={{ wordBreak: 'break-all' }}>
            {currentPath || 'Not selected'}
          </Typography>
        </Box>
      </DialogContent>

      <DialogActions>
        <Button onClick={onClose}>Cancel</Button>
        <Button
          onClick={handleSelectCurrent}
          variant="contained"
          disabled={!currentPath}
        >
          Select This Directory
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default DirectoryBrowser;