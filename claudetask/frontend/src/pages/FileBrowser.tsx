import React, { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  Box,
  Typography,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  ListItemButton,
  Breadcrumbs,
  Link,
  IconButton,
  Button,
  Divider,
  Alert,
  CircularProgress,
  useTheme,
  alpha,
  Stack,
  Chip,
} from '@mui/material';
import {
  Folder as FolderIcon,
  InsertDriveFile as FileIcon,
  Home as HomeIcon,
  NavigateNext as NavigateNextIcon,
  Save as SaveIcon,
  Close as CloseIcon,
  ArrowBack as ArrowBackIcon,
} from '@mui/icons-material';
import Editor from '@monaco-editor/react';
import { useQuery, useMutation, useQueryClient } from 'react-query';
import { browseFiles, readFile, saveFile, FileItem, FileBrowserResponse } from '../services/api';

const FileBrowser: React.FC = () => {
  const theme = useTheme();
  const { projectId } = useParams<{ projectId: string }>();
  const navigate = useNavigate();
  const queryClient = useQueryClient();

  const [currentPath, setCurrentPath] = useState('');
  const [selectedFile, setSelectedFile] = useState<string | null>(null);
  const [fileContent, setFileContent] = useState('');
  const [originalContent, setOriginalContent] = useState('');
  const [hasUnsavedChanges, setHasUnsavedChanges] = useState(false);
  const [saveError, setSaveError] = useState<string | null>(null);
  const [saveSuccess, setSaveSuccess] = useState(false);

  // Browse files query
  const { data: browseData, isLoading, error, refetch } = useQuery<FileBrowserResponse>(
    ['files', projectId, currentPath],
    () => browseFiles(projectId!, currentPath),
    {
      enabled: !!projectId,
      onError: (err: any) => {
        console.error('Failed to browse files:', err);
      }
    }
  );

  // Read file query
  const { data: fileData, isLoading: isLoadingFile } = useQuery(
    ['file-content', projectId, selectedFile],
    () => readFile(projectId!, selectedFile!),
    {
      enabled: !!projectId && !!selectedFile,
      onSuccess: (data) => {
        setFileContent(data.content);
        setOriginalContent(data.content);
        setHasUnsavedChanges(false);
      }
    }
  );

  // Save file mutation
  const saveMutation = useMutation(
    () => saveFile(projectId!, selectedFile!, fileContent),
    {
      onSuccess: () => {
        setOriginalContent(fileContent);
        setHasUnsavedChanges(false);
        setSaveSuccess(true);
        setSaveError(null);
        setTimeout(() => setSaveSuccess(false), 3000);
        queryClient.invalidateQueries(['file-content', projectId, selectedFile]);
      },
      onError: (error: any) => {
        setSaveError(error.response?.data?.detail || 'Failed to save file');
        setTimeout(() => setSaveError(null), 5000);
      }
    }
  );

  // Handle content change
  const handleEditorChange = (value: string | undefined) => {
    const newContent = value || '';
    setFileContent(newContent);
    setHasUnsavedChanges(newContent !== originalContent);
  };

  // Navigate to directory
  const handleNavigate = (path: string) => {
    if (hasUnsavedChanges) {
      if (!window.confirm('You have unsaved changes. Are you sure you want to leave?')) {
        return;
      }
    }
    setSelectedFile(null);
    setCurrentPath(path);
    setHasUnsavedChanges(false);
  };

  // Handle file/folder click
  const handleItemClick = (item: FileItem) => {
    if (item.type === 'directory') {
      handleNavigate(item.path);
    } else {
      if (hasUnsavedChanges) {
        if (!window.confirm('You have unsaved changes. Are you sure you want to open another file?')) {
          return;
        }
      }
      setSelectedFile(item.path);
      setHasUnsavedChanges(false);
    }
  };

  // Get language for Monaco Editor based on file extension
  const getLanguage = (filename: string): string => {
    const ext = filename.split('.').pop()?.toLowerCase();
    const languageMap: Record<string, string> = {
      js: 'javascript',
      jsx: 'javascript',
      ts: 'typescript',
      tsx: 'typescript',
      py: 'python',
      json: 'json',
      html: 'html',
      css: 'css',
      scss: 'scss',
      md: 'markdown',
      yaml: 'yaml',
      yml: 'yaml',
      xml: 'xml',
      sql: 'sql',
      sh: 'shell',
      bash: 'shell',
    };
    return languageMap[ext || ''] || 'plaintext';
  };

  // Get icon for file type
  const getFileIcon = (item: FileItem) => {
    if (item.type === 'directory') {
      return <FolderIcon sx={{ color: theme.palette.primary.main }} />;
    }
    return <FileIcon sx={{ color: theme.palette.text.secondary }} />;
  };

  // Format file size
  const formatFileSize = (bytes: number | undefined): string => {
    if (!bytes) return '';
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
  };

  if (!projectId) {
    return (
      <Box sx={{ p: 4 }}>
        <Alert severity="error">Project ID is required</Alert>
      </Box>
    );
  }

  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', height: 'calc(100vh - 64px)', overflow: 'hidden' }}>
      {/* Header */}
      <Box sx={{
        p: 2,
        backgroundColor: theme.palette.background.paper,
        borderBottom: `1px solid ${theme.palette.divider}`,
      }}>
        <Stack direction="row" spacing={2} alignItems="center" sx={{ mb: 2 }}>
          <IconButton
            onClick={() => navigate('/projects')}
            size="small"
            sx={{
              color: theme.palette.text.secondary,
              '&:hover': {
                backgroundColor: alpha(theme.palette.primary.main, 0.1),
                color: theme.palette.primary.main,
              }
            }}
          >
            <ArrowBackIcon />
          </IconButton>
          <Typography variant="h5" sx={{ fontWeight: 700, color: theme.palette.text.primary }}>
            {browseData?.project_name || 'File Browser'}
          </Typography>
          {selectedFile && (
            <Chip
              label={selectedFile.split('/').pop()}
              size="small"
              sx={{
                backgroundColor: alpha(theme.palette.primary.main, 0.1),
                color: theme.palette.primary.main,
                fontWeight: 600,
              }}
            />
          )}
        </Stack>

        {/* Breadcrumbs */}
        <Breadcrumbs separator={<NavigateNextIcon fontSize="small" />} sx={{ mb: 1 }}>
          {browseData?.breadcrumbs.map((crumb, index) => (
            <Link
              key={index}
              component="button"
              variant="body2"
              onClick={() => handleNavigate(crumb.path)}
              sx={{
                color: theme.palette.text.secondary,
                textDecoration: 'none',
                cursor: 'pointer',
                '&:hover': {
                  color: theme.palette.primary.main,
                  textDecoration: 'underline',
                }
              }}
            >
              {index === 0 ? <HomeIcon sx={{ fontSize: 16, mr: 0.5, verticalAlign: 'middle' }} /> : null}
              {crumb.name}
            </Link>
          ))}
        </Breadcrumbs>

        {/* Action buttons when file is open */}
        {selectedFile && (
          <Stack direction="row" spacing={2} sx={{ mt: 2 }}>
            <Button
              variant="contained"
              startIcon={<SaveIcon />}
              onClick={() => saveMutation.mutate()}
              disabled={!hasUnsavedChanges || saveMutation.isLoading}
              sx={{
                backgroundColor: theme.palette.primary.main,
                '&:hover': { backgroundColor: theme.palette.primary.dark },
              }}
            >
              {saveMutation.isLoading ? 'Saving...' : 'Save'}
            </Button>
            <Button
              variant="outlined"
              startIcon={<CloseIcon />}
              onClick={() => {
                if (hasUnsavedChanges) {
                  if (window.confirm('You have unsaved changes. Are you sure?')) {
                    setSelectedFile(null);
                    setHasUnsavedChanges(false);
                  }
                } else {
                  setSelectedFile(null);
                }
              }}
            >
              Close File
            </Button>
            {hasUnsavedChanges && (
              <Chip
                label="Unsaved changes"
                color="warning"
                size="small"
                sx={{ alignSelf: 'center' }}
              />
            )}
          </Stack>
        )}

        {/* Alerts */}
        {saveSuccess && (
          <Alert severity="success" sx={{ mt: 2 }}>
            File saved successfully!
          </Alert>
        )}
        {saveError && (
          <Alert severity="error" sx={{ mt: 2 }} onClose={() => setSaveError(null)}>
            {saveError}
          </Alert>
        )}
      </Box>

      {/* Content */}
      <Box sx={{ display: 'flex', flex: 1, overflow: 'hidden' }}>
        {/* File List Sidebar */}
        {!selectedFile && (
          <Box sx={{
            width: '100%',
            overflow: 'auto',
            backgroundColor: theme.palette.background.default,
          }}>
            {isLoading ? (
              <Box sx={{ display: 'flex', justifyContent: 'center', p: 4 }}>
                <CircularProgress />
              </Box>
            ) : error ? (
              <Alert severity="error" sx={{ m: 2 }}>
                Failed to load files. Please try again.
              </Alert>
            ) : (
              <List sx={{ p: 0 }}>
                {browseData?.items.map((item, index) => (
                  <React.Fragment key={index}>
                    <ListItem disablePadding>
                      <ListItemButton
                        onClick={() => handleItemClick(item)}
                        sx={{
                          py: 1.5,
                          px: 3,
                          '&:hover': {
                            backgroundColor: alpha(theme.palette.primary.main, 0.08),
                          }
                        }}
                      >
                        <ListItemIcon sx={{ minWidth: 40 }}>
                          {getFileIcon(item)}
                        </ListItemIcon>
                        <ListItemText
                          primary={item.name}
                          secondary={item.type === 'file' ? formatFileSize(item.size) : null}
                          primaryTypographyProps={{
                            fontWeight: item.type === 'directory' ? 600 : 400,
                            color: theme.palette.text.primary,
                          }}
                          secondaryTypographyProps={{
                            color: theme.palette.text.secondary,
                            fontSize: '0.75rem',
                          }}
                        />
                        {item.extension && (
                          <Chip
                            label={item.extension}
                            size="small"
                            sx={{
                              backgroundColor: alpha(theme.palette.primary.main, 0.1),
                              color: theme.palette.text.secondary,
                              fontSize: '0.7rem',
                              height: 20,
                            }}
                          />
                        )}
                      </ListItemButton>
                    </ListItem>
                    {index < (browseData?.items.length || 0) - 1 && <Divider />}
                  </React.Fragment>
                ))}
                {browseData?.items.length === 0 && (
                  <Box sx={{ p: 4, textAlign: 'center' }}>
                    <Typography color="text.secondary">
                      This directory is empty
                    </Typography>
                  </Box>
                )}
              </List>
            )}
          </Box>
        )}

        {/* Editor */}
        {selectedFile && (
          <Box sx={{ flex: 1, overflow: 'hidden', backgroundColor: theme.palette.background.paper }}>
            {isLoadingFile ? (
              <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100%' }}>
                <CircularProgress />
              </Box>
            ) : (
              <Editor
                height="100%"
                language={getLanguage(selectedFile)}
                value={fileContent}
                onChange={handleEditorChange}
                theme={theme.palette.mode === 'dark' ? 'vs-dark' : 'light'}
                options={{
                  minimap: { enabled: true },
                  fontSize: 14,
                  lineNumbers: 'on',
                  scrollBeyondLastLine: false,
                  automaticLayout: true,
                  tabSize: 2,
                  wordWrap: 'on',
                }}
              />
            )}
          </Box>
        )}
      </Box>
    </Box>
  );
};

export default FileBrowser;
