# FileBrowser Component

## Purpose

FileBrowser is a GitHub-style file browser and code editor component that allows users to browse project files, view file contents, and edit files directly within the ClaudeTask Framework interface. It provides a complete file management experience with Monaco Editor integration for code editing and markdown preview capabilities.

## Location

**Component:** `claudetask/frontend/src/pages/FileBrowser.tsx`
**API Service:** `claudetask/frontend/src/services/api.ts`
**Backend Router:** `claudetask/backend/app/routers/file_browser.py`

## Features

### Core Functionality
- **File System Navigation**: Browse directories and files within project scope
- **Code Editor**: Monaco Editor integration for syntax-highlighted code editing
- **Markdown Preview**: Live preview mode for markdown files with GitHub-flavored markdown support
- **File Operations**: Read and save file contents with real-time change detection
- **Breadcrumb Navigation**: Easy navigation through directory hierarchy
- **Security**: Path traversal protection and project-scope enforcement

### User Interface
- **Compact Header**: Single-line header with back button, project name, breadcrumbs, and actions
- **Dual-Pane Layout**: File list on left, editor/preview on right
- **File Type Icons**: Visual indicators for directories and files
- **File Metadata**: Size, modification time, and extension display
- **Loading States**: Smooth loading indicators for async operations
- **Success/Error Notifications**: User feedback for save operations

### Code Editing
- **Syntax Highlighting**: Supports 15+ programming languages
- **Auto-save Indicators**: Shows unsaved changes with visual cues
- **Edit/Preview Toggle**: Switch between edit and preview modes for markdown
- **File Size Limits**: Safety checks for large files (10MB limit)
- **Encoding Support**: UTF-8 and Latin-1 encoding fallback

## Component Props

```tsx
interface FileBrowserProps {
  // No direct props - uses URL params
}

// URL Parameters (via react-router)
interface RouteParams {
  projectId: string;  // Project ID from route
}
```

## State Management

### Local State

```tsx
// Navigation state
const [currentPath, setCurrentPath] = useState<string>('');
const [selectedFile, setSelectedFile] = useState<string | null>(null);

// Editor state
const [fileContent, setFileContent] = useState<string>('');
const [originalContent, setOriginalContent] = useState<string>('');
const [hasUnsavedChanges, setHasUnsavedChanges] = useState<boolean>(false);
const [viewMode, setViewMode] = useState<'edit' | 'preview'>('edit');

// UI state
const [saveError, setSaveError] = useState<string | null>(null);
const [saveSuccess, setSaveSuccess] = useState<boolean>(false);
```

### React Query Integration

```tsx
// Browse files query
const { data: browseData, isLoading, error, refetch } = useQuery<FileBrowserResponse>(
  ['files', projectId, currentPath],
  () => browseFiles(projectId!, currentPath)
);

// Read file query
const { data: fileData, isLoading: isLoadingFile } = useQuery(
  ['file-content', projectId, selectedFile],
  () => readFile(projectId!, selectedFile!)
);

// Save file mutation
const saveMutation = useMutation(
  () => saveFile(projectId!, selectedFile!, fileContent)
);
```

## API Integration

### Endpoints Used

#### 1. Browse Files
```typescript
GET /api/projects/{projectId}/files/browse?path={relativePath}

Response: {
  success: boolean;
  project_name: string;
  current_path: string;
  items: FileItem[];
  breadcrumbs: Array<{ name: string; path: string }>;
}
```

#### 2. Read File
```typescript
GET /api/projects/{projectId}/files/read?path={filePath}

Response: {
  success: boolean;
  path: string;
  content: string;
  mime_type: string;
  size: number;
  extension?: string;
}
```

#### 3. Save File
```typescript
POST /api/projects/{projectId}/files/save
Body: {
  path: string;
  content: string;
}

Response: {
  success: boolean;
  path: string;
  size: number;
  message: string;
}
```

## Usage Example

### Integration with Project Manager

```tsx
import { useNavigate } from 'react-router-dom';

const ProjectManager: React.FC = () => {
  const navigate = useNavigate();

  const openFileBrowser = (projectId: string) => {
    navigate(`/projects/${projectId}/files`);
  };

  return (
    <Button onClick={() => openFileBrowser(project.id)}>
      Browse Files
    </Button>
  );
};
```

### Route Configuration

```tsx
// In App.tsx
<Route path="/projects/:projectId/files" element={<FileBrowser />} />
```

## Supported Languages

The Monaco Editor supports the following languages with full syntax highlighting:

| Extension | Language | Monaco Language ID |
|-----------|----------|-------------------|
| `.js` | JavaScript | javascript |
| `.jsx` | JavaScript React | javascript |
| `.ts` | TypeScript | typescript |
| `.tsx` | TypeScript React | typescript |
| `.py` | Python | python |
| `.json` | JSON | json |
| `.html` | HTML | html |
| `.css` | CSS | css |
| `.scss` | SCSS | scss |
| `.md` | Markdown | markdown |
| `.yaml`, `.yml` | YAML | yaml |
| `.xml` | XML | xml |
| `.sql` | SQL | sql |
| `.sh`, `.bash` | Shell | shell |

## Security Features

### Path Traversal Protection
- All paths are resolved and validated against project root
- Prevents access to files outside project directory
- Blocks directory traversal attacks (`../`, etc.)

### File Size Limits
- 10MB maximum file size for reading
- Prevents memory exhaustion on large binary files
- Graceful error handling for oversized files

### Ignored Files/Directories
The following are automatically hidden from file browser:
- Hidden files (starting with `.`)
- `node_modules/`
- `__pycache__/`
- `venv/`
- `.git/`

## Component Architecture

### Layout Structure

```
┌─────────────────────────────────────────────────────┐
│ Header (Compact Single Line)                        │
│ [← Back] [Project Name] / path / to / file          │
│                          [Save Button] [Preview/Edit]│
├──────────────────┬──────────────────────────────────┤
│                  │                                   │
│  File List       │  Editor / Preview                │
│  (Left Panel)    │  (Right Panel)                   │
│                  │                                   │
│  📁 src          │  ┌────────────────────────────┐ │
│  📁 docs         │  │                            │ │
│  📄 README.md    │  │  Monaco Editor             │ │
│  📄 package.json │  │  or                        │ │
│                  │  │  Markdown Preview          │ │
│                  │  │                            │ │
│                  │  └────────────────────────────┘ │
│                  │                                   │
└──────────────────┴──────────────────────────────────┘
```

### Component Hierarchy

```
FileBrowser
├── Header (Box)
│   ├── Back Button (IconButton)
│   ├── Project Name (Typography)
│   ├── Breadcrumbs (Breadcrumbs)
│   ├── Save Button (Button)
│   └── View Mode Toggle (ToggleButtonGroup)
├── Main Content (Grid)
│   ├── File List (Grid item - 4 columns)
│   │   ├── Loading State (CircularProgress)
│   │   ├── Error State (Alert)
│   │   └── File Items (List)
│   │       └── ListItemButton
│   │           ├── Icon (FolderIcon / FileIcon)
│   │           ├── Name (ListItemText)
│   │           └── Metadata (Typography)
│   └── Editor Panel (Grid item - 8 columns)
│       ├── No File Selected (Alert)
│       ├── Loading State (CircularProgress)
│       ├── Edit Mode
│       │   └── Monaco Editor
│       └── Preview Mode
│           └── ReactMarkdown
```

## Styling

### Theme Integration

```tsx
import { useTheme, alpha } from '@mui/material';

const theme = useTheme();

// Primary colors for directories
sx={{ color: theme.palette.primary.main }}

// Hover states with alpha transparency
sx={{
  '&:hover': {
    backgroundColor: alpha(theme.palette.primary.main, 0.1),
  }
}}

// Selected file highlighting
sx={{
  backgroundColor: alpha(theme.palette.primary.main, 0.15),
}}
```

### Responsive Design

```tsx
// File list panel - 4 columns on desktop, full width on mobile
<Grid item xs={12} md={4}>
  {/* File list */}
</Grid>

// Editor panel - 8 columns on desktop, full width on mobile
<Grid item xs={12} md={8}>
  {/* Editor */}
</Grid>
```

## User Interactions

### Navigation Flow

1. **Enter File Browser**: User clicks "Browse Files" button in Project Manager
2. **View Root Directory**: FileBrowser loads and displays project root files
3. **Navigate Folders**: User clicks folder name to enter directory
4. **Breadcrumb Navigation**: User clicks breadcrumb to jump to parent directory
5. **Select File**: User clicks file name to open in editor
6. **Edit File**: User modifies content in Monaco Editor
7. **Save Changes**: User clicks Save button to persist changes
8. **Preview Markdown**: User toggles to preview mode for markdown files

### Keyboard Shortcuts

- **Ctrl/Cmd + S**: Save file (Monaco Editor built-in)
- **Esc**: Close file editor and return to file list

## Error Handling

### Common Error Scenarios

#### File Not Found
```tsx
if (!full_path.exists()) {
  raise HTTPException(status_code=404, detail="File not found")
}
```

#### Permission Denied
```tsx
try {
  for item in full_path.iterdir():
    // ...
} catch PermissionError {
  raise HTTPException(status_code=403, detail="Permission denied")
}
```

#### File Too Large
```tsx
if (file_size > 10 * 1024 * 1024) {
  raise HTTPException(status_code=413, detail="File too large (max 10MB)")
}
```

#### Binary File Not Supported
```tsx
try {
  with open(full_path, 'r', encoding='utf-8') as f:
    content = f.read()
} catch UnicodeDecodeError {
  // Try latin-1 encoding, or return error
}
```

### User Feedback

```tsx
// Success notification
{saveSuccess && (
  <Alert severity="success" sx={{ mb: 2 }}>
    File saved successfully!
  </Alert>
)}

// Error notification
{saveError && (
  <Alert severity="error" sx={{ mb: 2 }}>
    {saveError}
  </Alert>
)}
```

## Dependencies

### Frontend Dependencies
```json
{
  "@monaco-editor/react": "^4.6.0",
  "react-markdown": "^9.0.0",
  "remark-gfm": "^4.0.0",
  "rehype-highlight": "^7.0.0",
  "highlight.js": "^11.9.0",
  "react-query": "^3.39.3"
}
```

### Backend Dependencies
```python
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from pathlib import Path
import mimetypes
from sqlalchemy.ext.asyncio import AsyncSession
```

## Performance Optimizations

### React Query Caching
- File list cached by `['files', projectId, currentPath]`
- File content cached by `['file-content', projectId, selectedFile]`
- Automatic cache invalidation on successful save

### Lazy Loading
- Files loaded on-demand when directory opened
- Editor only loads when file selected
- Monaco Editor uses code splitting for language support

### File Size Protection
- 10MB file size limit prevents memory issues
- Large files rejected before content load
- Binary files detected and rejected early

## Best Practices

### Safe File Operations
```tsx
// Always check for unsaved changes before navigation
const handleNavigate = () => {
  if (hasUnsavedChanges) {
    if (window.confirm('You have unsaved changes. Continue?')) {
      navigate('/projects');
    }
  } else {
    navigate('/projects');
  }
};
```

### Error Recovery
```tsx
// Auto-clear error notifications
setTimeout(() => setSaveError(null), 5000);

// Provide retry options
{error && (
  <Alert severity="error">
    Failed to load files.
    <Button onClick={refetch}>Retry</Button>
  </Alert>
)}
```

## Future Enhancements

### Planned Features
- [ ] File upload support
- [ ] File/directory creation
- [ ] File/directory deletion
- [ ] File/directory rename
- [ ] Multi-file editing (tabs)
- [ ] Search within files
- [ ] Git diff visualization
- [ ] File tree view (recursive)
- [ ] Syntax validation
- [ ] Auto-formatting
- [ ] Collaborative editing

### Potential Improvements
- [ ] WebSocket for real-time file watching
- [ ] Vim/Emacs keybindings
- [ ] Code snippets library
- [ ] File history and undo/redo
- [ ] Split view for comparing files
- [ ] Integrated terminal
- [ ] Git operations from file browser

## Related Components

- **ProjectManager**: Parent component that launches FileBrowser
- **MonacoEditor**: External editor component for code editing
- **ReactMarkdown**: Markdown rendering for preview mode

## Troubleshooting

### Issue: Monaco Editor Not Loading
**Symptom**: Editor area shows blank or loading indefinitely

**Solutions**:
1. Check browser console for errors
2. Verify Monaco Editor CDN is accessible
3. Clear browser cache and reload
4. Check for JavaScript errors in browser console

### Issue: Files Not Displaying
**Symptom**: File list is empty or shows error

**Solutions**:
1. Verify project path is correct in database
2. Check backend logs for permission errors
3. Ensure project directory exists and is accessible
4. Verify CORS settings allow API requests

### Issue: Save Failed
**Symptom**: Save button doesn't work or shows error

**Solutions**:
1. Check file permissions (write access)
2. Verify disk space availability
3. Check for file locks by other processes
4. Review backend logs for detailed error

### Issue: Preview Not Rendering
**Symptom**: Markdown preview shows raw markdown

**Solutions**:
1. Verify `react-markdown` package is installed
2. Check for CSS conflicts
3. Ensure `remark-gfm` and `rehype-highlight` are loaded
4. Clear browser cache

## Testing

### Manual Testing Checklist

#### Navigation
- [ ] Browse to root directory
- [ ] Navigate into subdirectories
- [ ] Use breadcrumbs to navigate up
- [ ] Back button returns to project manager

#### File Operations
- [ ] Open text file
- [ ] Edit file content
- [ ] Save changes successfully
- [ ] Cancel unsaved changes

#### Editor Features
- [ ] Syntax highlighting works for different languages
- [ ] Monaco Editor loads properly
- [ ] Markdown preview renders correctly
- [ ] Toggle between edit and preview modes

#### Error Handling
- [ ] Large file rejected gracefully
- [ ] Binary file handled appropriately
- [ ] Permission denied shows error
- [ ] Network errors handled

#### UI/UX
- [ ] Loading states display correctly
- [ ] Success notifications appear and disappear
- [ ] Error messages are clear
- [ ] Responsive on mobile devices

## Code Examples

### Opening a Specific File Directly

```tsx
// Navigate to file browser with pre-selected file
const openFile = (projectId: string, filePath: string) => {
  navigate(`/projects/${projectId}/files`, {
    state: { initialFile: filePath }
  });
};
```

### Customizing Monaco Editor Theme

```tsx
<Editor
  theme="vs-dark"  // Use dark theme
  options={{
    fontSize: 14,
    minimap: { enabled: false },
    lineNumbers: 'on',
    scrollBeyondLastLine: false,
  }}
/>
```

### Filtering File List

```tsx
const filteredItems = browseData?.items.filter(item =>
  !item.name.startsWith('.') &&
  item.name !== 'node_modules'
);
```

---

**Last Updated**: 2025-11-18
**Version**: 1.0.0
**Status**: Active - New Feature
**Related Documentation**:
- [File Browser API Endpoints](../api/endpoints/file-browser.md)
- [Project Manager Component](./ProjectManager.md)
- [Architecture Overview](../architecture/overview.md)
