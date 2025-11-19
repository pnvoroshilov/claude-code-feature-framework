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
  ToggleButton,
  ToggleButtonGroup,
  Tooltip,
  Menu,
  MenuItem,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
} from '@mui/material';
import {
  Folder as FolderIcon,
  InsertDriveFile as FileIcon,
  Home as HomeIcon,
  NavigateNext as NavigateNextIcon,
  Save as SaveIcon,
  Close as CloseIcon,
  ArrowBack as ArrowBackIcon,
  Visibility as VisibilityIcon,
  Code as CodeIcon,
  CreateNewFolder as CreateFolderIcon,
  NoteAdd as CreateFileIcon,
  Edit as RenameIcon,
  Delete as DeleteIcon,
  ContentCopy as CopyIcon,
  ContentPaste as PasteIcon,
} from '@mui/icons-material';
import Editor from '@monaco-editor/react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import rehypeHighlight from 'rehype-highlight';
import 'highlight.js/styles/github-dark.css';
import { useQuery, useMutation, useQueryClient } from 'react-query';
import {
  browseFiles,
  readFile,
  saveFile,
  createFileOrDirectory,
  renameFileOrDirectory,
  deleteFileOrDirectory,
  copyFileOrDirectory,
  FileItem,
  FileBrowserResponse
} from '../services/api';

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
  const [viewMode, setViewMode] = useState<'edit' | 'preview'>('edit');

  // Context menu state
  const [contextMenu, setContextMenu] = useState<{
    mouseX: number;
    mouseY: number;
    item: FileItem | null;
  } | null>(null);

  // Dialog states
  const [createDialog, setCreateDialog] = useState<{ open: boolean; type: 'file' | 'directory' | null }>({ open: false, type: null });
  const [renameDialog, setRenameDialog] = useState<{ open: boolean; item: FileItem | null }>({ open: false, item: null });
  const [deleteDialog, setDeleteDialog] = useState<{ open: boolean; item: FileItem | null }>({ open: false, item: null });
  const [newItemName, setNewItemName] = useState('');

  // Clipboard state
  const [clipboard, setClipboard] = useState<{ type: 'copy' | 'cut'; item: FileItem } | null>(null);

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

  // Create file or directory mutation
  const createMutation = useMutation(
    ({ path, type, content }: { path: string; type: 'file' | 'directory'; content?: string }) =>
      createFileOrDirectory(projectId!, path, type, content),
    {
      onSuccess: () => {
        refetch();
        setCreateDialog({ open: false, type: null });
        setNewItemName('');
      },
      onError: (error: any) => {
        alert(error.response?.data?.detail || 'Failed to create item');
      }
    }
  );

  // Rename mutation
  const renameMutation = useMutation(
    ({ oldPath, newPath }: { oldPath: string; newPath: string }) =>
      renameFileOrDirectory(projectId!, oldPath, newPath),
    {
      onSuccess: () => {
        refetch();
        setRenameDialog({ open: false, item: null });
        setNewItemName('');
      },
      onError: (error: any) => {
        alert(error.response?.data?.detail || 'Failed to rename item');
      }
    }
  );

  // Delete mutation
  const deleteMutation = useMutation(
    (path: string) => deleteFileOrDirectory(projectId!, path),
    {
      onSuccess: () => {
        // Capture the deleted item path before clearing dialog
        const deletedPath = deleteDialog.item?.path;

        refetch();
        setDeleteDialog({ open: false, item: null });

        // Clear selected file if it was the deleted one
        if (selectedFile === deletedPath) {
          setSelectedFile(null);
        }
      },
      onError: (error: any) => {
        alert(error.response?.data?.detail || 'Failed to delete item');
      }
    }
  );

  // Copy mutation
  const copyMutation = useMutation(
    ({ sourcePath, destinationPath }: { sourcePath: string; destinationPath: string }) =>
      copyFileOrDirectory(projectId!, sourcePath, destinationPath),
    {
      onSuccess: () => {
        refetch();
        setClipboard(null);
      },
      onError: (error: any) => {
        alert(error.response?.data?.detail || 'Failed to copy item');
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
      setViewMode('edit');
    }
  };

  // Check if file is markdown
  const isMarkdownFile = (filename: string | null): boolean => {
    if (!filename) return false;
    const ext = filename.split('.').pop()?.toLowerCase();
    return ext === 'md' || ext === 'markdown';
  };

  // Context menu handlers
  const handleContextMenu = (event: React.MouseEvent, item: FileItem) => {
    event.preventDefault();
    setContextMenu({
      mouseX: event.clientX,
      mouseY: event.clientY,
      item,
    });
  };

  const handleCloseContextMenu = () => {
    setContextMenu(null);
  };

  // File operation handlers
  const handleCreateNew = (type: 'file' | 'directory') => {
    setCreateDialog({ open: true, type });
    handleCloseContextMenu();
  };

  const handleRename = (item: FileItem) => {
    setRenameDialog({ open: true, item });
    setNewItemName(item.name);
    handleCloseContextMenu();
  };

  const handleDelete = (item: FileItem) => {
    setDeleteDialog({ open: true, item });
    handleCloseContextMenu();
  };

  const handleCopy = (item: FileItem) => {
    setClipboard({ type: 'copy', item });
    handleCloseContextMenu();
  };

  const handlePaste = () => {
    if (!clipboard) return;

    const sourcePath = clipboard.item.path;
    const sourcePathParts = sourcePath.split('/');
    const sourceName = sourcePathParts[sourcePathParts.length - 1];

    // Generate unique name if file/folder already exists in current directory
    let destinationName = sourceName;
    let counter = 1;

    // Check if name already exists in current directory
    const existingNames = browseData?.items.map(item => item.name) || [];

    // Parse name and extension
    const lastDotIndex = sourceName.lastIndexOf('.');
    const hasExtension = lastDotIndex > 0 && clipboard.item.type === 'file';
    const baseName = hasExtension ? sourceName.substring(0, lastDotIndex) : sourceName;
    const extension = hasExtension ? sourceName.substring(lastDotIndex) : '';

    // Find unique name
    while (existingNames.includes(destinationName)) {
      if (hasExtension) {
        destinationName = `${baseName} (${counter})${extension}`;
      } else {
        destinationName = `${baseName} (${counter})`;
      }
      counter++;
    }

    // Build full destination path
    const destinationPath = currentPath ? `${currentPath}/${destinationName}` : destinationName;

    copyMutation.mutate({ sourcePath, destinationPath });
    handleCloseContextMenu();
  };

  // Dialog submit handlers
  const handleCreateSubmit = () => {
    if (!newItemName.trim()) return;

    const path = currentPath ? `${currentPath}/${newItemName}` : newItemName;
    createMutation.mutate({
      path,
      type: createDialog.type!,
      content: createDialog.type === 'file' ? '' : undefined
    });
  };

  const handleRenameSubmit = () => {
    if (!newItemName.trim() || !renameDialog.item) return;

    const oldPath = renameDialog.item.path;
    const pathParts = oldPath.split('/');
    pathParts[pathParts.length - 1] = newItemName;
    const newPath = pathParts.join('/');

    renameMutation.mutate({ oldPath, newPath });
  };

  const handleDeleteConfirm = () => {
    if (!deleteDialog.item) return;
    deleteMutation.mutate(deleteDialog.item.path);
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
        {/* Single line: Back button + Project name + Breadcrumbs + File actions */}
        <Stack
          direction="row"
          alignItems="center"
          spacing={1}
          sx={{
            flexWrap: 'nowrap',
            width: '100%',
          }}
        >
          {/* Left: Back button + Project name + Breadcrumbs */}
          <Stack direction="row" alignItems="center" spacing={1} sx={{ flexGrow: 1, minWidth: 0, overflow: 'hidden' }}>
            {/* Back button + Project name */}
            <Stack direction="row" alignItems="center" spacing={0.5} sx={{ flexShrink: 0 }}>
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
              <ArrowBackIcon fontSize="small" />
            </IconButton>
            <Typography
              variant="subtitle1"
              sx={{
                fontWeight: 600,
                color: theme.palette.text.primary,
                whiteSpace: 'nowrap',
                fontSize: '0.95rem',
                maxWidth: '180px',
                overflow: 'hidden',
                textOverflow: 'ellipsis',
              }}
            >
              {browseData?.project_name || 'File Browser'}
            </Typography>
            </Stack>

            {/* Breadcrumbs */}
            <Box
              sx={{
                flexShrink: 1,
                minWidth: 0,
                overflow: 'hidden',
              }}
            >
              <Breadcrumbs
                separator={<NavigateNextIcon fontSize="small" />}
                sx={{
                  '& .MuiBreadcrumbs-ol': {
                    flexWrap: 'nowrap',
                  }
                }}
              >
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
                      fontSize: '0.8rem',
                      whiteSpace: 'nowrap',
                      overflow: 'hidden',
                      textOverflow: 'ellipsis',
                      maxWidth: '80px',
                      '&:hover': {
                        color: theme.palette.primary.main,
                        textDecoration: 'underline',
                      }
                    }}
                  >
                    {index === 0 ? <HomeIcon sx={{ fontSize: 12, mr: 0.3, verticalAlign: 'middle' }} /> : null}
                    {crumb.name}
                  </Link>
                ))}
              </Breadcrumbs>
            </Box>
          </Stack>

          {/* Right: File actions (only when file is open) */}
          <Stack
            direction="row"
            spacing={0.75}
            alignItems="center"
            sx={{
              flexShrink: 0,
              flexGrow: 0,
              flexWrap: 'nowrap',
              minWidth: selectedFile ? 'fit-content' : '200px',
              visibility: selectedFile ? 'visible' : 'hidden',
              opacity: selectedFile ? 1 : 0,
              transition: 'opacity 0.2s ease-in-out',
              mr: 2,
            }}
          >
              {/* View mode toggle for Markdown files */}
              {isMarkdownFile(selectedFile) && (
                <ToggleButtonGroup
                  value={viewMode}
                  exclusive
                  onChange={(e, newMode) => {
                    if (newMode !== null) {
                      setViewMode(newMode);
                    }
                  }}
                  size="small"
                >
                  <ToggleButton value="edit" sx={{ px: 1, py: 0.4, fontSize: '0.8rem' }}>
                    <CodeIcon sx={{ mr: 0.3, fontSize: 14 }} />
                    Edit
                  </ToggleButton>
                  <ToggleButton value="preview" sx={{ px: 1, py: 0.4, fontSize: '0.8rem' }}>
                    <VisibilityIcon sx={{ mr: 0.3, fontSize: 14 }} />
                    Preview
                  </ToggleButton>
                </ToggleButtonGroup>
              )}

              {hasUnsavedChanges && (
                <Chip
                  label="Unsaved"
                  color="warning"
                  size="small"
                  sx={{ height: 22, fontSize: '0.75rem' }}
                />
              )}

              <Tooltip title={saveMutation.isLoading ? 'Saving...' : 'Save'}>
                <span>
                  <IconButton
                    onClick={() => saveMutation.mutate()}
                    disabled={!hasUnsavedChanges || saveMutation.isLoading}
                    size="small"
                    color="primary"
                    sx={{
                      bgcolor: hasUnsavedChanges ? theme.palette.primary.main : 'transparent',
                      color: hasUnsavedChanges ? 'white' : theme.palette.action.disabled,
                      '&:hover': {
                        bgcolor: hasUnsavedChanges ? theme.palette.primary.dark : 'transparent',
                      },
                      '&.Mui-disabled': {
                        bgcolor: 'transparent',
                      }
                    }}
                  >
                    <SaveIcon sx={{ fontSize: 18 }} />
                  </IconButton>
                </span>
              </Tooltip>

              <Tooltip title="Close file">
                <IconButton
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
                  size="small"
                  sx={{
                    color: theme.palette.text.secondary,
                    '&:hover': {
                      color: theme.palette.error.main,
                      bgcolor: alpha(theme.palette.error.main, 0.1),
                    }
                  }}
                >
                  <CloseIcon sx={{ fontSize: 18 }} />
                </IconButton>
              </Tooltip>
          </Stack>
        </Stack>

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
        {/* File List Sidebar - Always visible */}
        <Box sx={{
          width: selectedFile ? 300 : '100%',
          minWidth: selectedFile ? 300 : undefined,
          overflow: 'auto',
          backgroundColor: theme.palette.background.default,
          borderRight: selectedFile ? `1px solid ${theme.palette.divider}` : 'none',
          transition: 'width 0.2s ease',
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
            <>
              {/* Toolbar */}
              <Box sx={{
                p: 1,
                borderBottom: `1px solid ${theme.palette.divider}`,
                backgroundColor: theme.palette.background.paper,
              }}>
                <Stack direction="row" spacing={0.5} flexWrap="wrap">
                  <Tooltip title="New File">
                    <IconButton
                      size="small"
                      onClick={() => handleCreateNew('file')}
                      sx={{
                        color: theme.palette.text.secondary,
                        '&:hover': {
                          backgroundColor: alpha(theme.palette.primary.main, 0.1),
                          color: theme.palette.primary.main,
                        }
                      }}
                    >
                      <CreateFileIcon fontSize="small" />
                    </IconButton>
                  </Tooltip>
                  <Tooltip title="New Folder">
                    <IconButton
                      size="small"
                      onClick={() => handleCreateNew('directory')}
                      sx={{
                        color: theme.palette.text.secondary,
                        '&:hover': {
                          backgroundColor: alpha(theme.palette.primary.main, 0.1),
                          color: theme.palette.primary.main,
                        }
                      }}
                    >
                      <CreateFolderIcon fontSize="small" />
                    </IconButton>
                  </Tooltip>
                  <Divider orientation="vertical" flexItem sx={{ mx: 0.5 }} />
                  <Tooltip title="Paste">
                    <span>
                      <IconButton
                        size="small"
                        onClick={handlePaste}
                        disabled={!clipboard}
                        sx={{
                          color: theme.palette.text.secondary,
                          '&:hover': {
                            backgroundColor: alpha(theme.palette.primary.main, 0.1),
                            color: theme.palette.primary.main,
                          }
                        }}
                      >
                        <PasteIcon fontSize="small" />
                      </IconButton>
                    </span>
                  </Tooltip>
                  {clipboard && (
                    <Chip
                      label={`Copied: ${clipboard.item.name}`}
                      size="small"
                      onDelete={() => setClipboard(null)}
                      sx={{
                        ml: 1,
                        height: 24,
                        fontSize: '0.7rem',
                      }}
                    />
                  )}
                </Stack>
              </Box>

              <List sx={{ p: 0 }}>
              {browseData?.items.map((item, index) => (
                <React.Fragment key={index}>
                  <ListItem disablePadding>
                    <ListItemButton
                      onClick={() => handleItemClick(item)}
                      onContextMenu={(e) => handleContextMenu(e, item)}
                      selected={selectedFile === item.path && item.type === 'file'}
                      sx={{
                        py: 1.5,
                        px: 2,
                        '&:hover': {
                          backgroundColor: alpha(theme.palette.primary.main, 0.08),
                        },
                        '&.Mui-selected': {
                          backgroundColor: alpha(theme.palette.primary.main, 0.12),
                          '&:hover': {
                            backgroundColor: alpha(theme.palette.primary.main, 0.16),
                          }
                        }
                      }}
                    >
                      <ListItemIcon sx={{ minWidth: 36 }}>
                        {getFileIcon(item)}
                      </ListItemIcon>
                      <ListItemText
                        primary={item.name}
                        secondary={item.type === 'file' ? formatFileSize(item.size) : null}
                        primaryTypographyProps={{
                          fontWeight: item.type === 'directory' ? 600 : 400,
                          color: theme.palette.text.primary,
                          fontSize: '0.875rem',
                          noWrap: true,
                        }}
                        secondaryTypographyProps={{
                          color: theme.palette.text.secondary,
                          fontSize: '0.7rem',
                        }}
                      />
                      {item.extension && (
                        <Chip
                          label={item.extension}
                          size="small"
                          sx={{
                            backgroundColor: alpha(theme.palette.primary.main, 0.1),
                            color: theme.palette.text.secondary,
                            fontSize: '0.65rem',
                            height: 18,
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
                  <Typography color="text.secondary" variant="body2">
                    This directory is empty
                  </Typography>
                </Box>
              )}
            </List>
            </>
          )}
        </Box>

        {/* Editor/Preview - Only visible when file is selected */}
        <Box sx={{
          flex: 1,
          overflow: 'hidden',
          backgroundColor: theme.palette.background.paper,
          display: selectedFile ? 'flex' : 'none',
        }}>
          {isLoadingFile ? (
            <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100%' }}>
              <CircularProgress />
            </Box>
          ) : (
            <>
              {/* Monaco Editor - Show in edit mode or for non-markdown files */}
              {selectedFile && (viewMode === 'edit' || !isMarkdownFile(selectedFile)) && (
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
                  loading={<CircularProgress />}
                />
              )}

                {/* Markdown Preview - Show only for markdown files in preview mode */}
                {viewMode === 'preview' && isMarkdownFile(selectedFile) && (
                  <Box
                    sx={{
                      height: '100%',
                      overflow: 'auto',
                      p: 4,
                      backgroundColor: theme.palette.mode === 'dark'
                        ? 'rgba(30, 30, 30, 1)'
                        : 'rgba(255, 255, 255, 1)',
                      '& .markdown-preview': {
                        maxWidth: '900px',
                        margin: '0 auto',
                        fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif',
                        fontSize: '16px',
                        lineHeight: '1.6',
                        color: theme.palette.text.primary,
                        '& h1': {
                          fontSize: '2.5em',
                          fontWeight: 700,
                          marginTop: '24px',
                          marginBottom: '16px',
                          paddingBottom: '0.3em',
                          borderBottom: `1px solid ${theme.palette.divider}`,
                          color: theme.palette.primary.main,
                        },
                        '& h2': {
                          fontSize: '2em',
                          fontWeight: 600,
                          marginTop: '24px',
                          marginBottom: '16px',
                          paddingBottom: '0.3em',
                          borderBottom: `1px solid ${theme.palette.divider}`,
                          color: theme.palette.primary.main,
                        },
                        '& h3': {
                          fontSize: '1.5em',
                          fontWeight: 600,
                          marginTop: '20px',
                          marginBottom: '12px',
                          color: theme.palette.primary.dark,
                        },
                        '& h4': {
                          fontSize: '1.25em',
                          fontWeight: 600,
                          marginTop: '16px',
                          marginBottom: '12px',
                          color: theme.palette.text.primary,
                        },
                        '& h5, & h6': {
                          fontSize: '1em',
                          fontWeight: 600,
                          marginTop: '16px',
                          marginBottom: '12px',
                          color: theme.palette.text.secondary,
                        },
                        '& p': {
                          marginTop: '0',
                          marginBottom: '16px',
                        },
                        '& a': {
                          color: theme.palette.primary.main,
                          textDecoration: 'none',
                          fontWeight: 500,
                          '&:hover': {
                            textDecoration: 'underline',
                          },
                        },
                        '& ul, & ol': {
                          paddingLeft: '2em',
                          marginBottom: '16px',
                        },
                        '& li': {
                          marginTop: '0.25em',
                        },
                        '& code': {
                          backgroundColor: theme.palette.mode === 'dark'
                            ? 'rgba(110, 118, 129, 0.4)'
                            : 'rgba(175, 184, 193, 0.2)',
                          padding: '0.2em 0.4em',
                          borderRadius: '6px',
                          fontSize: '85%',
                          fontFamily: 'ui-monospace, SFMono-Regular, "SF Mono", Menlo, Consolas, "Liberation Mono", monospace',
                        },
                        '& pre': {
                          backgroundColor: theme.palette.mode === 'dark'
                            ? 'rgba(110, 118, 129, 0.2)'
                            : 'rgba(175, 184, 193, 0.1)',
                          padding: '16px',
                          overflow: 'auto',
                          fontSize: '85%',
                          lineHeight: '1.45',
                          borderRadius: '6px',
                          marginBottom: '16px',
                          border: `1px solid ${theme.palette.divider}`,
                        },
                        '& pre code': {
                          backgroundColor: 'transparent',
                          padding: 0,
                          fontSize: '100%',
                        },
                        '& blockquote': {
                          padding: '0 1em',
                          color: theme.palette.text.secondary,
                          borderLeft: `4px solid ${theme.palette.primary.main}`,
                          margin: '0 0 16px 0',
                          fontStyle: 'italic',
                        },
                        '& table': {
                          borderCollapse: 'collapse',
                          width: '100%',
                          marginBottom: '16px',
                          display: 'block',
                          overflow: 'auto',
                        },
                        '& table th, & table td': {
                          padding: '8px 13px',
                          border: `1px solid ${theme.palette.divider}`,
                        },
                        '& table th': {
                          fontWeight: 600,
                          backgroundColor: theme.palette.mode === 'dark'
                            ? 'rgba(110, 118, 129, 0.2)'
                            : 'rgba(175, 184, 193, 0.1)',
                        },
                        '& table tr': {
                          backgroundColor: theme.palette.background.paper,
                          borderTop: `1px solid ${theme.palette.divider}`,
                        },
                        '& table tr:nth-of-type(2n)': {
                          backgroundColor: theme.palette.mode === 'dark'
                            ? 'rgba(110, 118, 129, 0.1)'
                            : 'rgba(175, 184, 193, 0.05)',
                        },
                        '& img': {
                          maxWidth: '100%',
                          boxSizing: 'content-box',
                        },
                        '& hr': {
                          height: '0.25em',
                          padding: 0,
                          margin: '24px 0',
                          backgroundColor: theme.palette.divider,
                          border: 0,
                        },
                      },
                    }}
                  >
                    <Box className="markdown-preview">
                      <ReactMarkdown
                        remarkPlugins={[remarkGfm]}
                        rehypePlugins={[rehypeHighlight]}
                      >
                        {fileContent}
                      </ReactMarkdown>
                    </Box>
                  </Box>
                )}
              </>
            )}
        </Box>
      </Box>

      {/* Context Menu */}
      <Menu
        open={contextMenu !== null}
        onClose={handleCloseContextMenu}
        anchorReference="anchorPosition"
        anchorPosition={
          contextMenu !== null
            ? { top: contextMenu.mouseY, left: contextMenu.mouseX }
            : undefined
        }
      >
        <MenuItem onClick={() => contextMenu?.item && handleRename(contextMenu.item)}>
          <ListItemIcon>
            <RenameIcon fontSize="small" />
          </ListItemIcon>
          <ListItemText>Rename</ListItemText>
        </MenuItem>
        <MenuItem onClick={() => contextMenu?.item && handleCopy(contextMenu.item)}>
          <ListItemIcon>
            <CopyIcon fontSize="small" />
          </ListItemIcon>
          <ListItemText>Copy</ListItemText>
        </MenuItem>
        <Divider />
        <MenuItem
          onClick={() => contextMenu?.item && handleDelete(contextMenu.item)}
          sx={{ color: theme.palette.error.main }}
        >
          <ListItemIcon>
            <DeleteIcon fontSize="small" sx={{ color: theme.palette.error.main }} />
          </ListItemIcon>
          <ListItemText>Delete</ListItemText>
        </MenuItem>
      </Menu>

      {/* Create Dialog */}
      <Dialog
        open={createDialog.open}
        onClose={() => setCreateDialog({ open: false, type: null })}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle>
          Create New {createDialog.type === 'file' ? 'File' : 'Folder'}
        </DialogTitle>
        <DialogContent>
          <TextField
            autoFocus
            margin="dense"
            label="Name"
            type="text"
            fullWidth
            variant="outlined"
            value={newItemName}
            onChange={(e) => setNewItemName(e.target.value)}
            onKeyPress={(e) => {
              if (e.key === 'Enter') {
                handleCreateSubmit();
              }
            }}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setCreateDialog({ open: false, type: null })}>
            Cancel
          </Button>
          <Button onClick={handleCreateSubmit} variant="contained">
            Create
          </Button>
        </DialogActions>
      </Dialog>

      {/* Rename Dialog */}
      <Dialog
        open={renameDialog.open}
        onClose={() => setRenameDialog({ open: false, item: null })}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle>Rename {renameDialog.item?.name}</DialogTitle>
        <DialogContent>
          <TextField
            autoFocus
            margin="dense"
            label="New Name"
            type="text"
            fullWidth
            variant="outlined"
            value={newItemName}
            onChange={(e) => setNewItemName(e.target.value)}
            onKeyPress={(e) => {
              if (e.key === 'Enter') {
                handleRenameSubmit();
              }
            }}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setRenameDialog({ open: false, item: null })}>
            Cancel
          </Button>
          <Button onClick={handleRenameSubmit} variant="contained">
            Rename
          </Button>
        </DialogActions>
      </Dialog>

      {/* Delete Confirmation Dialog */}
      <Dialog
        open={deleteDialog.open}
        onClose={() => setDeleteDialog({ open: false, item: null })}
        maxWidth="sm"
      >
        <DialogTitle>Confirm Delete</DialogTitle>
        <DialogContent>
          <Typography>
            Are you sure you want to delete "{deleteDialog.item?.name}"?
            {deleteDialog.item?.type === 'directory' && (
              <Box sx={{ mt: 1, color: theme.palette.warning.main }}>
                <strong>Warning:</strong> This will delete the directory and all its contents.
              </Box>
            )}
          </Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDeleteDialog({ open: false, item: null })}>
            Cancel
          </Button>
          <Button onClick={handleDeleteConfirm} variant="contained" color="error">
            Delete
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default FileBrowser;
