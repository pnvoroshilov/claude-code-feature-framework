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
} from '@mui/icons-material';
import Editor from '@monaco-editor/react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import rehypeHighlight from 'rehype-highlight';
import 'highlight.js/styles/github-dark.css';
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
  const [viewMode, setViewMode] = useState<'edit' | 'preview'>('edit');

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
      setViewMode('edit');
    }
  };

  // Check if file is markdown
  const isMarkdownFile = (filename: string | null): boolean => {
    if (!filename) return false;
    const ext = filename.split('.').pop()?.toLowerCase();
    return ext === 'md' || ext === 'markdown';
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
                sx={{ mr: 2 }}
              >
                <ToggleButton value="edit" sx={{ px: 2 }}>
                  <CodeIcon sx={{ mr: 1, fontSize: 18 }} />
                  Edit
                </ToggleButton>
                <ToggleButton value="preview" sx={{ px: 2 }}>
                  <VisibilityIcon sx={{ mr: 1, fontSize: 18 }} />
                  Preview
                </ToggleButton>
              </ToggleButtonGroup>
            )}

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
            <List sx={{ p: 0 }}>
              {browseData?.items.map((item, index) => (
                <React.Fragment key={index}>
                  <ListItem disablePadding>
                    <ListItemButton
                      onClick={() => handleItemClick(item)}
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
          )}
        </Box>

        {/* Editor/Preview - Only visible when file is selected */}
        {selectedFile && (
          <Box sx={{ flex: 1, overflow: 'hidden', backgroundColor: theme.palette.background.paper }}>
            {isLoadingFile ? (
              <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100%' }}>
                <CircularProgress />
              </Box>
            ) : (
              <>
                {/* Monaco Editor - Show in edit mode or for non-markdown files */}
                {(viewMode === 'edit' || !isMarkdownFile(selectedFile)) && (
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
        )}
      </Box>
    </Box>
  );
};

export default FileBrowser;
