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
- **File Operations**: Complete file management including create, read, save, rename, delete, and copy
- **Context Menu**: Right-click context menu for file and directory operations
- **Clipboard Support**: Copy and paste files and directories with auto-generated unique names
- **Breadcrumb Navigation**: Easy navigation through directory hierarchy
- **Security**: Path traversal protection and project-scope enforcement

### User Interface
- **Compact Single-Line Header**: Optimized header layout with back button, project name, breadcrumbs, and file actions aligned on one line
- **Responsive Layout**: Smart visibility toggles ensure buttons don't wrap or disappear when files are opened
- **Dual-Pane Layout**: File list on left, editor/preview on right
- **File Type Icons**: Visual indicators for directories and files
- **File Metadata**: Size, modification time, and extension display
- **Loading States**: Smooth loading indicators for async operations
- **Success/Error Notifications**: User feedback for all file operations
- **Modal Dialogs**: Confirmation dialogs for create, rename, and delete operations
- **Context Menus**: Right-click menus for quick file operations
- **Stable Editor Panel**: Fixed-width editor panel that maintains layout consistency

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

// Create file or directory mutation
const createMutation = useMutation(
  ({ path, type, content }: { path: string; type: 'file' | 'directory'; content?: string }) =>
    createFileOrDirectory(projectId!, path, type, content),
  {
    onSuccess: () => refetch()
  }
);

// Rename mutation
const renameMutation = useMutation(
  ({ oldPath, newPath }: { oldPath: string; newPath: string }) =>
    renameFileOrDirectory(projectId!, oldPath, newPath),
  {
    onSuccess: () => refetch()
  }
);

// Delete mutation
const deleteMutation = useMutation(
  (path: string) => deleteFileOrDirectory(projectId!, path),
  {
    onSuccess: () => {
      refetch();
      // Clear selected file if it was deleted
      if (selectedFile === path) {
        setSelectedFile(null);
      }
    }
  }
);

// Copy mutation
const copyMutation = useMutation(
  ({ sourcePath, destPath }: { sourcePath: string; destPath: string }) =>
    copyFileOrDirectory(projectId!, sourcePath, destPath),
  {
    onSuccess: () => refetch()
  }
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

#### 4. Create File or Directory
```typescript
POST /api/projects/{projectId}/files/create
Body: {
  path: string;
  type: 'file' | 'directory';
  content?: string;
}

Response: {
  success: boolean;
  path: string;
  type: string;
  message: string;
}
```

#### 5. Rename File or Directory
```typescript
POST /api/projects/{projectId}/files/rename
Body: {
  old_path: string;
  new_path: string;
}

Response: {
  success: boolean;
  old_path: string;
  new_path: string;
  message: string;
}
```

#### 6. Delete File or Directory
```typescript
POST /api/projects/{projectId}/files/delete
Body: {
  path: string;
}

Response: {
  success: boolean;
  path: string;
  message: string;
}
```

#### 7. Copy File or Directory
```typescript
POST /api/projects/{projectId}/files/copy
Body: {
  source_path: string;
  destination_path: string;
}

Response: {
  success: boolean;
  source_path: string;
  destination_path: string;
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
┌─────────────────────────────────────────────────────────────┐
│ Header (Single Compact Line)                                │
│ [← Back] [Project Name] / path / to / file  [Save] [Edit/Preview] │
├────────────────────┬────────────────────────────────────────┤
│                    │                                         │
│  File List         │  Editor / Preview                      │
│  (Left Panel)      │  (Right Panel - Fixed Width)           │
│                    │                                         │
│  📁 src            │  ┌──────────────────────────────────┐  │
│  📁 docs           │  │                                  │  │
│  📄 README.md      │  │  Monaco Editor                   │  │
│  📄 package.json   │  │  or                              │  │
│                    │  │  Markdown Preview                │  │
│                    │  │                                  │  │
│                    │  └──────────────────────────────────┘  │
│                    │                                         │
└────────────────────┴────────────────────────────────────────┘
```

### Header Layout Details

The header uses a sophisticated flex layout to ensure all elements remain visible and properly aligned:

```tsx
<Stack direction="row" alignItems="center" spacing={1} sx={{ flexWrap: 'nowrap' }}>
  {/* Left section: Back button + Project name + Breadcrumbs */}
  <Stack direction="row" sx={{ flexGrow: 1, minWidth: 0, overflow: 'hidden' }}>
    {/* Fixed width elements */}
    <IconButton>Back</IconButton>
    <Typography>Project Name</Typography>

    {/* Flexible breadcrumbs with overflow handling */}
    <Box sx={{ flexShrink: 1, minWidth: 0 }}>
      <Breadcrumbs maxWidth="80px" />
    </Box>
  </Stack>

  {/* Right section: File actions with visibility toggle */}
  <Stack
    sx={{
      flexShrink: 0,
      minWidth: selectedFile ? 'fit-content' : '200px',
      visibility: selectedFile ? 'visible' : 'hidden',
      opacity: selectedFile ? 1 : 0,
      transition: 'opacity 0.2s',
    }}
  >
    {/* Edit/Preview toggle, Unsaved chip, Save button */}
  </Stack>
</Stack>
```

**Key Layout Features:**
- **No Wrapping**: `flexWrap: 'nowrap'` ensures all elements stay on one line
- **Smart Visibility**: File actions use visibility toggle instead of conditional rendering to maintain consistent layout
- **Minimum Width**: Button container has minimum width when hidden to prevent layout shifts
- **Smooth Transitions**: Opacity transitions for better UX
- **Fixed Editor Width**: Editor panel maintains consistent width regardless of file selection state

### Component Hierarchy

```
FileBrowser
├── Header (Box)
│   └── Stack (Single row, no wrap)
│       ├── Left Section (Stack - flexGrow: 1)
│       │   ├── Back Button (IconButton)
│       │   ├── Project Name (Typography)
│       │   └── Breadcrumbs (Box with overflow handling)
│       └── Right Section (Stack - flexShrink: 0)
│           ├── View Mode Toggle (ToggleButtonGroup)
│           ├── Unsaved Chip (Chip)
│           └── Save Button (Button)
├── Main Content (Grid)
│   ├── File List (Grid item - 4 columns)
│   │   ├── Loading State (CircularProgress)
│   │   ├── Error State (Alert)
│   │   └── File Items (List)
│   │       └── ListItemButton (with context menu)
│   │           ├── Icon (FolderIcon / FileIcon)
│   │           ├── Name (ListItemText)
│   │           └── Metadata (Typography)
│   └── Editor Panel (Grid item - 8 columns, fixed width)
│       ├── No File Selected (Alert - hidden state)
│       ├── Loading State (CircularProgress)
│       ├── Edit Mode
│       │   └── Monaco Editor
│       └── Preview Mode
│           └── ReactMarkdown
├── Context Menu (Menu)
│   ├── New File (MenuItem)
│   ├── New Folder (MenuItem)
│   ├── Rename (MenuItem)
│   ├── Delete (MenuItem)
│   ├── Copy (MenuItem)
│   └── Paste (MenuItem)
├── Create Dialog (Dialog)
├── Rename Dialog (Dialog)
└── Delete Dialog (Dialog)
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

### Layout Optimizations

**Breadcrumb Overflow Handling:**
```tsx
<Breadcrumbs
  sx={{
    '& .MuiBreadcrumbs-ol': {
      flexWrap: 'nowrap',
    }
  }}
>
  <Link sx={{
    maxWidth: '80px',
    overflow: 'hidden',
    textOverflow: 'ellipsis',
    whiteSpace: 'nowrap',
  }}>
    {crumb.name}
  </Link>
</Breadcrumbs>
```

**Button Container Stability:**
```tsx
<Stack
  sx={{
    // Use visibility toggle instead of conditional rendering
    visibility: selectedFile ? 'visible' : 'hidden',
    opacity: selectedFile ? 1 : 0,
    // Maintain minimum space even when hidden
    minWidth: selectedFile ? 'fit-content' : '200px',
    // Prevent shrinking to maintain layout
    flexShrink: 0,
  }}
>
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

### File Management Flow

1. **Create New File/Directory**: Right-click in file list → Select "New File" or "New Folder" → Enter name → Confirm
2. **Rename Item**: Right-click on file/directory → Select "Rename" → Enter new name → Confirm
3. **Delete Item**: Right-click on file/directory → Select "Delete" → Confirm deletion
   - Deleting currently selected file automatically clears the selection and closes the editor
4. **Copy Item**: Right-click on file/directory → Select "Copy" → Navigate to destination → Right-click → Select "Paste"
5. **Auto-naming**: Paste operations automatically generate unique names (e.g., "file.txt" → "file (1).txt" → "file (2).txt")

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
  "react-query": "^3.39.3",
  "@mui/material": "^5.x.x",
  "@mui/icons-material": "^5.x.x"
}
```

### Backend Dependencies
```python
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from pathlib import Path
import mimetypes
import shutil
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
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

### Layout Performance
- Visibility toggles instead of conditional rendering prevent layout reflows
- Fixed flex properties maintain stable layout dimensions
- Smooth opacity transitions provide better perceived performance

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

### Safe Delete Operations
```tsx
// Clear selection when deleting currently selected file
const deleteMutation = useMutation(
  (path: string) => deleteFileOrDirectory(projectId!, path),
  {
    onSuccess: () => {
      refetch();
      // Prevent editing deleted file
      if (selectedFile === path) {
        setSelectedFile(null);
      }
    }
  }
);
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

## Recent Changes

### Version 2.0.1 - UI/UX Refinements (2025-11-19)
- Fixed editor panel layout consistency on first file open
- Improved header button alignment and visibility
- Replaced conditional rendering with visibility toggles to prevent layout shifts
- Added minimum width to button container for stable layout
- Fixed breadcrumb overflow handling with proper truncation
- Ensured file action buttons never wrap or disappear
- Added null check for selectedFile in editor component
- Improved flex layout with proper shrink/grow values
- Fixed button alignment to right edge with margin adjustments
- Enhanced delete operation to clear selected file automatically

### Version 2.0 - Comprehensive File Management (2025-11-18)
- Added file and directory creation with modal dialogs
- Implemented rename functionality with validation
- Added delete operations with confirmation dialogs
- Implemented copy/paste with clipboard support
- Added context menus for right-click operations
- Auto-generated unique names for paste operations to prevent conflicts
- Enhanced user feedback with success/error notifications for all operations

### Version 1.0 - Initial Release
- GitHub-style file browser
- Monaco Editor integration
- Markdown preview mode
- Basic file read/save operations

## Completed Features

### v2.0.1 - UI/UX Improvements
- [x] Fixed editor panel layout consistency
- [x] Improved header button alignment and visibility
- [x] Smart visibility toggles for stable layout
- [x] Breadcrumb overflow handling
- [x] Auto-clear selection on file delete
- [x] Null safety checks for editor

### v2.0 - File Management
- [x] File/directory creation with modal dialogs
- [x] File/directory deletion with confirmation
- [x] File/directory rename with validation
- [x] File/directory copy with clipboard
- [x] Context menu for file operations
- [x] Auto-generated unique names for paste operations
- [x] Right-click context menus

## Future Enhancements

### Planned Features
- [ ] File upload support (drag and drop)
- [ ] Multi-file editing (tabs)
- [ ] Search within files
- [ ] Git diff visualization
- [ ] File tree view (recursive sidebar)
- [ ] Syntax validation
- [ ] Auto-formatting
- [ ] Collaborative editing
- [ ] File move (drag and drop)

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

### Issue: Buttons Disappearing or Wrapping
**Symptom**: Header buttons not visible after opening file

**Solutions**:
1. This was fixed in v2.0.1 with visibility toggles
2. Ensure you're using the latest version
3. Clear browser cache if using older version
4. Check flexbox layout properties haven't been overridden

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
- [ ] Create new file
- [ ] Create new directory
- [ ] Rename file
- [ ] Rename directory
- [ ] Delete file
- [ ] Delete directory (verify selection clears)
- [ ] Delete currently selected file (verify editor closes)
- [ ] Copy file
- [ ] Copy directory
- [ ] Paste with auto-generated unique name

#### Editor Features
- [ ] Syntax highlighting works for different languages
- [ ] Monaco Editor loads properly
- [ ] Markdown preview renders correctly
- [ ] Toggle between edit and preview modes

#### Layout Stability
- [ ] Header layout remains single line
- [ ] Buttons don't wrap or disappear when file opens
- [ ] Breadcrumbs truncate properly with ellipsis
- [ ] Editor panel maintains consistent width
- [ ] File actions appear/disappear smoothly

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
- [ ] Smooth transitions and animations

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

### Implementing Stable Layout with Visibility Toggles

```tsx
// GOOD: Use visibility toggle to maintain layout
<Stack
  sx={{
    visibility: selectedFile ? 'visible' : 'hidden',
    opacity: selectedFile ? 1 : 0,
    minWidth: selectedFile ? 'fit-content' : '200px',
    flexShrink: 0,
  }}
>
  <Button>Save</Button>
</Stack>

// BAD: Conditional rendering causes layout shifts
{selectedFile && (
  <Stack>
    <Button>Save</Button>
  </Stack>
)}
```

---

**Last Updated**: 2025-11-19
**Version**: 2.0.1
**Status**: Active - Production Ready
**Related Documentation**:
- [File Browser API Endpoints](../api/endpoints/file-browser.md)
- [Project Manager Component](./ProjectManager.md)
- [Architecture Overview](../architecture/overview.md)
