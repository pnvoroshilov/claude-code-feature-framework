# File Browser API Endpoints

## Overview

The File Browser API provides secure file system access within project boundaries, allowing users to browse directories, read file contents, save changes, and retrieve recursive file trees. All operations are scoped to the project directory with built-in security protections against path traversal attacks.

## Base URL

```
/api/projects/{project_id}/files
```

## Authentication

Currently no authentication required (local desktop application). All operations are restricted to the project directory scope.

## Security Features

- **Path Traversal Protection**: All paths validated against project root
- **File Size Limits**: 10MB maximum for file read operations
- **Hidden File Filtering**: Automatically excludes hidden files and common ignore patterns
- **Permission Checking**: Handles permission errors gracefully
- **Project Scoping**: All operations restricted to project directory

## Endpoints

### 1. Browse Files

Browse files and directories in a project path.

#### Request

```http
GET /api/projects/{project_id}/files/browse?path={relative_path}
```

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `project_id` | string | Yes | Project UUID |
| `path` | string | No | Relative path from project root (default: "") |

**Example:**
```bash
GET /api/projects/abc-123/files/browse?path=src/components
```

#### Response

**Success (200 OK):**

```json
{
  "success": true,
  "project_name": "My Project",
  "current_path": "src/components",
  "items": [
    {
      "name": "Header.tsx",
      "path": "src/components/Header.tsx",
      "type": "file",
      "size": 2048,
      "modified": "1699564800.0",
      "extension": "tsx"
    },
    {
      "name": "utils",
      "path": "src/components/utils",
      "type": "directory"
    }
  ],
  "breadcrumbs": [
    {
      "name": "My Project",
      "path": ""
    },
    {
      "name": "src",
      "path": "src"
    },
    {
      "name": "components",
      "path": "src/components"
    }
  ]
}
```

**Response Fields:**

| Field | Type | Description |
|-------|------|-------------|
| `success` | boolean | Operation success indicator |
| `project_name` | string | Project display name |
| `current_path` | string | Current relative path (empty string for root) |
| `items` | array | List of files and directories |
| `items[].name` | string | File or directory name |
| `items[].path` | string | Relative path from project root |
| `items[].type` | string | "file" or "directory" |
| `items[].size` | number | File size in bytes (files only) |
| `items[].modified` | string | Unix timestamp as string (files only) |
| `items[].extension` | string | File extension without dot (files only) |
| `breadcrumbs` | array | Navigation breadcrumb trail |
| `breadcrumbs[].name` | string | Breadcrumb display name |
| `breadcrumbs[].path` | string | Breadcrumb path |

**Error Responses:**

```json
// Project not found (404)
{
  "detail": "Project abc-123 not found"
}

// Path not found (404)
{
  "detail": "Path not found"
}

// Access denied - path traversal attempt (403)
{
  "detail": "Access denied"
}

// Permission error (403)
{
  "detail": "Permission denied"
}

// Path is not a directory (400)
{
  "detail": "Path is not a directory"
}

// Server error (500)
{
  "detail": "Failed to browse files: <error_details>"
}
```

**Filtering Rules:**

Files and directories matching the following patterns are automatically excluded:
- Hidden files (names starting with `.`)
- `node_modules/`
- `__pycache__/`
- `venv/`
- `.git/`

**Sorting:**

Items are sorted with:
1. Directories first
2. Alphabetically by name (case-insensitive)

---

### 2. Read File

Read the content of a specific file.

#### Request

```http
GET /api/projects/{project_id}/files/read?path={file_path}
```

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `project_id` | string | Yes | Project UUID |
| `path` | string | Yes | Relative file path from project root |

**Example:**
```bash
GET /api/projects/abc-123/files/read?path=src/App.tsx
```

#### Response

**Success (200 OK):**

```json
{
  "success": true,
  "path": "src/App.tsx",
  "content": "import React from 'react';\n\nconst App = () => {\n  return <div>Hello World</div>;\n};\n\nexport default App;",
  "mime_type": "text/plain",
  "size": 120,
  "extension": "tsx"
}
```

**Response Fields:**

| Field | Type | Description |
|-------|------|-------------|
| `success` | boolean | Operation success indicator |
| `path` | string | Relative file path |
| `content` | string | Complete file contents |
| `mime_type` | string | MIME type (guessed from extension) |
| `size` | number | File size in bytes |
| `extension` | string | File extension without dot |

**Error Responses:**

```json
// Project not found (404)
{
  "detail": "Project abc-123 not found"
}

// File not found (404)
{
  "detail": "File not found"
}

// Access denied - path traversal attempt (403)
{
  "detail": "Access denied"
}

// Path is not a file (400)
{
  "detail": "Path is not a file"
}

// File too large (413)
{
  "detail": "File too large (max 10MB)"
}

// Binary file not supported (415)
{
  "detail": "Binary file not supported"
}

// Server error (500)
{
  "detail": "Failed to read file: <error_details>"
}
```

**Encoding Handling:**

1. First attempts UTF-8 encoding
2. Falls back to Latin-1 encoding on UnicodeDecodeError
3. Returns 415 error if both encodings fail

**File Size Limit:**

Maximum file size: **10MB** (10,485,760 bytes)

Files exceeding this limit will return a 413 error to prevent memory exhaustion.

---

### 3. Save File

Save content to a file (creates file if doesn't exist).

#### Request

```http
POST /api/projects/{project_id}/files/save
Content-Type: application/json
```

**Parameters:**

| Parameter | Type | Location | Required | Description |
|-----------|------|----------|----------|-------------|
| `project_id` | string | Path | Yes | Project UUID |
| `path` | string | Body | Yes | Relative file path from project root |
| `content` | string | Body | Yes | Complete file content to save |

**Request Body:**

```json
{
  "path": "src/App.tsx",
  "content": "import React from 'react';\n\nconst App = () => {\n  return <div>Hello World!</div>;\n};\n\nexport default App;"
}
```

**Example:**
```bash
curl -X POST http://localhost:3333/api/projects/abc-123/files/save \
  -H "Content-Type: application/json" \
  -d '{
    "path": "src/App.tsx",
    "content": "// Updated content"
  }'
```

#### Response

**Success (200 OK):**

```json
{
  "success": true,
  "path": "src/App.tsx",
  "size": 125,
  "message": "File saved successfully"
}
```

**Response Fields:**

| Field | Type | Description |
|-------|------|-------------|
| `success` | boolean | Operation success indicator |
| `path` | string | Relative file path that was saved |
| `size` | number | Final file size in bytes |
| `message` | string | Success message |

**Error Responses:**

```json
// Project not found (404)
{
  "detail": "Project abc-123 not found"
}

// Access denied - path traversal attempt (403)
{
  "detail": "Access denied"
}

// Server error (500)
{
  "detail": "Failed to save file: <error_details>"
}
```

**Behavior:**

- **File doesn't exist**: Creates new file with provided content
- **File exists**: Overwrites existing content completely
- **Parent directories missing**: Creates parent directories automatically
- **Encoding**: Always saves as UTF-8

---

### 4. Get File Tree

Retrieve a recursive file tree structure.

#### Request

```http
GET /api/projects/{project_id}/files/tree?path={relative_path}&max_depth={depth}
```

**Parameters:**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `project_id` | string | Yes | - | Project UUID |
| `path` | string | No | "" | Relative path to start from |
| `max_depth` | integer | No | 3 | Maximum depth to recurse |

**Example:**
```bash
GET /api/projects/abc-123/files/tree?path=src&max_depth=2
```

#### Response

**Success (200 OK):**

```json
{
  "success": true,
  "project_name": "My Project",
  "root_path": "src",
  "tree": [
    {
      "name": "components",
      "path": "src/components",
      "type": "directory",
      "children": [
        {
          "name": "Header.tsx",
          "path": "src/components/Header.tsx",
          "type": "file",
          "extension": "tsx"
        },
        {
          "name": "Footer.tsx",
          "path": "src/components/Footer.tsx",
          "type": "file",
          "extension": "tsx"
        }
      ]
    },
    {
      "name": "App.tsx",
      "path": "src/App.tsx",
      "type": "file",
      "extension": "tsx"
    }
  ]
}
```

**Response Fields:**

| Field | Type | Description |
|-------|------|-------------|
| `success` | boolean | Operation success indicator |
| `project_name` | string | Project display name |
| `root_path` | string | Starting path for tree |
| `tree` | array | Recursive file tree structure |
| `tree[].name` | string | File or directory name |
| `tree[].path` | string | Full relative path |
| `tree[].type` | string | "file" or "directory" |
| `tree[].extension` | string | File extension (files only) |
| `tree[].children` | array | Nested items (directories only) |

**Error Responses:**

```json
// Project not found (404)
{
  "detail": "Project abc-123 not found"
}

// Access denied (403)
{
  "detail": "Access denied"
}

// Invalid path (403)
{
  "detail": "Invalid path"
}

// Server error (500)
{
  "detail": "Failed to get file tree: <error_details>"
}
```

**Filtering:**

Same filtering rules as browse endpoint:
- Hidden files excluded
- `node_modules/`, `__pycache__/`, `venv/`, `.git/` excluded

**Performance:**

- Default `max_depth=3` provides reasonable performance
- Deeper trees may take longer to generate
- Permission errors on subdirectories are silently skipped

---

### 5. Create File or Directory

Create a new file or directory in the project.

#### Request

```http
POST /api/projects/{project_id}/files/create
Content-Type: application/json
```

**Parameters:**

| Parameter | Type | Location | Required | Description |
|-----------|------|----------|----------|-------------|
| `project_id` | string | Path | Yes | Project UUID |
| `path` | string | Body | Yes | Relative path for new item |
| `type` | string | Body | Yes | Item type: "file" or "directory" |
| `content` | string | Body | No | Initial file content (files only, default: "") |

**Request Body:**

```json
{
  "path": "src/utils/helper.ts",
  "type": "file",
  "content": "// Helper utilities\nexport const helper = () => {};"
}
```

**Example:**
```bash
curl -X POST http://localhost:3333/api/projects/abc-123/files/create \
  -H "Content-Type: application/json" \
  -d '{
    "path": "src/utils/helper.ts",
    "type": "file",
    "content": "// New file"
  }'
```

#### Response

**Success (200 OK):**

```json
{
  "success": true,
  "path": "src/utils/helper.ts",
  "type": "file",
  "message": "File created successfully"
}
```

**Response Fields:**

| Field | Type | Description |
|-------|------|-------------|
| `success` | boolean | Operation success indicator |
| `path` | string | Relative path of created item |
| `type` | string | Type of item created ("file" or "directory") |
| `message` | string | Success message |

**Error Responses:**

```json
// Project not found (404)
{
  "detail": "Project abc-123 not found"
}

// Access denied (403)
{
  "detail": "Access denied"
}

// Item already exists (409)
{
  "detail": "File already exists"
}

// Invalid type (400)
{
  "detail": "Invalid type. Must be 'file' or 'directory'"
}

// Server error (500)
{
  "detail": "Failed to create file: <error_details>"
}
```

**Behavior:**

- **Parent directories**: Created automatically if they don't exist
- **File creation**: Creates empty file or file with provided content
- **Directory creation**: Creates directory and any necessary parent directories
- **Encoding**: Files always created with UTF-8 encoding

---

### 6. Rename File or Directory

Rename or move a file or directory within the project.

#### Request

```http
POST /api/projects/{project_id}/files/rename
Content-Type: application/json
```

**Parameters:**

| Parameter | Type | Location | Required | Description |
|-----------|------|----------|----------|-------------|
| `project_id` | string | Path | Yes | Project UUID |
| `old_path` | string | Body | Yes | Current relative path |
| `new_path` | string | Body | Yes | New relative path |

**Request Body:**

```json
{
  "old_path": "src/component.tsx",
  "new_path": "src/components/Component.tsx"
}
```

**Example:**
```bash
curl -X POST http://localhost:3333/api/projects/abc-123/files/rename \
  -H "Content-Type: application/json" \
  -d '{
    "old_path": "src/old-name.ts",
    "new_path": "src/new-name.ts"
  }'
```

#### Response

**Success (200 OK):**

```json
{
  "success": true,
  "old_path": "src/component.tsx",
  "new_path": "src/components/Component.tsx",
  "message": "Renamed successfully"
}
```

**Response Fields:**

| Field | Type | Description |
|-------|------|-------------|
| `success` | boolean | Operation success indicator |
| `old_path` | string | Original path |
| `new_path` | string | New path after rename |
| `message` | string | Success message |

**Error Responses:**

```json
// Project not found (404)
{
  "detail": "Project abc-123 not found"
}

// Source not found (404)
{
  "detail": "File or directory not found"
}

// Access denied (403)
{
  "detail": "Access denied"
}

// Destination exists (409)
{
  "detail": "Destination already exists"
}

// Server error (500)
{
  "detail": "Failed to rename: <error_details>"
}
```

**Behavior:**

- **Move operation**: Can move files/directories to different paths
- **Parent directories**: Created for new path if they don't exist
- **Atomic operation**: Rename is atomic (all or nothing)
- **Preserves content**: File content and directory structure preserved

---

### 7. Delete File or Directory

Delete a file or directory (including all contents if directory).

#### Request

```http
POST /api/projects/{project_id}/files/delete
Content-Type: application/json
```

**Parameters:**

| Parameter | Type | Location | Required | Description |
|-----------|------|----------|----------|-------------|
| `project_id` | string | Path | Yes | Project UUID |
| `path` | string | Body | Yes | Relative path to delete |

**Request Body:**

```json
{
  "path": "src/old-component.tsx"
}
```

**Example:**
```bash
curl -X POST http://localhost:3333/api/projects/abc-123/files/delete \
  -H "Content-Type: application/json" \
  -d '{
    "path": "src/old-file.ts"
  }'
```

#### Response

**Success (200 OK):**

```json
{
  "success": true,
  "path": "src/old-component.tsx",
  "message": "File deleted successfully"
}
```

**Response Fields:**

| Field | Type | Description |
|-------|------|-------------|
| `success` | boolean | Operation success indicator |
| `path` | string | Path that was deleted |
| `message` | string | Success message |

**Error Responses:**

```json
// Project not found (404)
{
  "detail": "Project abc-123 not found"
}

// Path not found (404)
{
  "detail": "File or directory not found"
}

// Access denied (403)
{
  "detail": "Access denied"
}

// Server error (500)
{
  "detail": "Failed to delete: <error_details>"
}
```

**Behavior:**

- **File deletion**: Removes file immediately
- **Directory deletion**: Recursively removes directory and all contents
- **Permanent**: No recycle bin or trash (deletion is permanent)
- **No confirmation**: Backend does not prompt for confirmation (handled by frontend)

---

### 8. Copy File or Directory

Copy a file or directory to a new location within the project.

#### Request

```http
POST /api/projects/{project_id}/files/copy
Content-Type: application/json
```

**Parameters:**

| Parameter | Type | Location | Required | Description |
|-----------|------|----------|----------|-------------|
| `project_id` | string | Path | Yes | Project UUID |
| `source_path` | string | Body | Yes | Source relative path |
| `destination_path` | string | Body | Yes | Destination relative path |

**Request Body:**

```json
{
  "source_path": "src/template.tsx",
  "destination_path": "src/components/NewComponent.tsx"
}
```

**Example:**
```bash
curl -X POST http://localhost:3333/api/projects/abc-123/files/copy \
  -H "Content-Type: application/json" \
  -d '{
    "source_path": "src/component.tsx",
    "destination_path": "src/component_copy.tsx"
  }'
```

#### Response

**Success (200 OK):**

```json
{
  "success": true,
  "source_path": "src/template.tsx",
  "destination_path": "src/components/NewComponent.tsx",
  "message": "File copied successfully"
}
```

**Response Fields:**

| Field | Type | Description |
|-------|------|-------------|
| `success` | boolean | Operation success indicator |
| `source_path` | string | Source path |
| `destination_path` | string | Destination path |
| `message` | string | Success message |

**Error Responses:**

```json
// Project not found (404)
{
  "detail": "Project abc-123 not found"
}

// Source not found (404)
{
  "detail": "Source not found"
}

// Access denied (403)
{
  "detail": "Access denied"
}

// Destination exists (409)
{
  "detail": "Destination already exists"
}

// Server error (500)
{
  "detail": "Failed to copy: <error_details>"
}
```

**Behavior:**

- **File copy**: Copies file content and metadata (timestamps, permissions)
- **Directory copy**: Recursively copies directory and all contents
- **Parent directories**: Created for destination if they don't exist
- **Metadata preservation**: Uses `shutil.copy2()` to preserve timestamps

---

## Data Models

### FileItem

```typescript
interface FileItem {
  name: string;           // File or directory name
  path: string;           // Relative path from project root
  type: 'file' | 'directory';
  size?: number;          // File size in bytes (files only)
  modified?: string;      // Unix timestamp as string (files only)
  extension?: string;     // File extension without dot (files only)
}
```

### Breadcrumb

```typescript
interface Breadcrumb {
  name: string;           // Display name for breadcrumb
  path: string;           // Relative path from project root
}
```

### FileBrowserResponse

```typescript
interface FileBrowserResponse {
  success: boolean;
  project_name: string;
  current_path: string;
  items: FileItem[];
  breadcrumbs: Breadcrumb[];
}
```

### FileContentResponse

```typescript
interface FileContentResponse {
  success: boolean;
  path: string;
  content: string;
  mime_type: string;
  size: number;
  extension?: string;
}
```

### FileSaveRequest

```typescript
interface FileSaveRequest {
  path: string;           // Relative file path
  content: string;        // Complete file content
}
```

### FileCreateRequest

```typescript
interface FileCreateRequest {
  path: string;           // Relative path for new item
  type: 'file' | 'directory';
  content?: string;       // Initial content (files only)
}
```

### FileRenameRequest

```typescript
interface FileRenameRequest {
  old_path: string;       // Current relative path
  new_path: string;       // New relative path
}
```

### FileDeleteRequest

```typescript
interface FileDeleteRequest {
  path: string;           // Relative path to delete
}
```

### FileCopyRequest

```typescript
interface FileCopyRequest {
  source_path: string;    // Source relative path
  destination_path: string; // Destination relative path
}
```

### FileTreeNode

```typescript
interface FileTreeNode {
  name: string;
  path: string;
  type: 'file' | 'directory';
  extension?: string;     // Files only
  children?: FileTreeNode[]; // Directories only
}
```

## Error Codes

| HTTP Status | Error Code | Description |
|-------------|------------|-------------|
| 200 | OK | Request successful |
| 400 | Bad Request | Invalid request (e.g., path is not a file/directory, invalid type) |
| 403 | Forbidden | Access denied or path traversal attempt |
| 404 | Not Found | Project, file, or path not found |
| 409 | Conflict | Resource already exists (create, rename, copy operations) |
| 413 | Payload Too Large | File exceeds 10MB limit |
| 415 | Unsupported Media Type | Binary file cannot be read as text |
| 500 | Internal Server Error | Server-side error occurred |

## Security Considerations

### Path Traversal Prevention

All endpoints validate paths to prevent directory traversal attacks:

```python
# Security check example
full_path = full_path.resolve()
project_path = project_path.resolve()
if not str(full_path).startswith(str(project_path)):
    raise HTTPException(status_code=403, detail="Access denied")
```

Blocked patterns:
- `../` (parent directory)
- Absolute paths outside project
- Symlinks outside project scope

### File Access Restrictions

- **Read-only access** to system files
- **No access** to files outside project directory
- **Permission checks** on all file operations
- **File size limits** prevent resource exhaustion

### Hidden File Protection

Sensitive files are automatically filtered:
- `.env` files
- `.git/` directory
- SSH keys (`.ssh/`)
- Other dotfiles

## Usage Examples

### Frontend Integration

#### Browse Files

```typescript
import { browseFiles } from '../services/api';

const loadFiles = async (projectId: string, path: string = '') => {
  try {
    const response = await browseFiles(projectId, path);
    console.log('Current path:', response.current_path);
    console.log('Files:', response.items);
    return response;
  } catch (error) {
    console.error('Failed to browse files:', error);
    throw error;
  }
};
```

#### Read File

```typescript
import { readFile } from '../services/api';

const loadFileContent = async (projectId: string, filePath: string) => {
  try {
    const response = await readFile(projectId, filePath);
    console.log('Content:', response.content);
    console.log('Size:', response.size, 'bytes');
    return response.content;
  } catch (error) {
    console.error('Failed to read file:', error);
    throw error;
  }
};
```

#### Save File

```typescript
import { saveFile } from '../services/api';

const saveFileContent = async (
  projectId: string,
  filePath: string,
  content: string
) => {
  try {
    const response = await saveFile(projectId, filePath, content);
    console.log('Saved successfully:', response.message);
    console.log('New size:', response.size, 'bytes');
    return response;
  } catch (error) {
    console.error('Failed to save file:', error);
    throw error;
  }
};
```

#### Create File or Directory

```typescript
import { createFileOrDirectory } from '../services/api';

const createNewFile = async (projectId: string, filePath: string) => {
  try {
    const response = await createFileOrDirectory(
      projectId,
      filePath,
      'file',
      '// New file content'
    );
    console.log('Created:', response.message);
    return response;
  } catch (error) {
    console.error('Failed to create file:', error);
    throw error;
  }
};

const createNewDirectory = async (projectId: string, dirPath: string) => {
  try {
    const response = await createFileOrDirectory(projectId, dirPath, 'directory');
    console.log('Created:', response.message);
    return response;
  } catch (error) {
    console.error('Failed to create directory:', error);
    throw error;
  }
};
```

#### Rename File or Directory

```typescript
import { renameFileOrDirectory } from '../services/api';

const renameItem = async (
  projectId: string,
  oldPath: string,
  newPath: string
) => {
  try {
    const response = await renameFileOrDirectory(projectId, oldPath, newPath);
    console.log('Renamed:', response.message);
    return response;
  } catch (error) {
    console.error('Failed to rename:', error);
    throw error;
  }
};
```

#### Delete File or Directory

```typescript
import { deleteFileOrDirectory } from '../services/api';

const deleteItem = async (projectId: string, path: string) => {
  try {
    const response = await deleteFileOrDirectory(projectId, path);
    console.log('Deleted:', response.message);
    return response;
  } catch (error) {
    console.error('Failed to delete:', error);
    throw error;
  }
};
```

#### Copy File or Directory

```typescript
import { copyFileOrDirectory } from '../services/api';

const copyItem = async (
  projectId: string,
  sourcePath: string,
  destPath: string
) => {
  try {
    const response = await copyFileOrDirectory(projectId, sourcePath, destPath);
    console.log('Copied:', response.message);
    return response;
  } catch (error) {
    console.error('Failed to copy:', error);
    throw error;
  }
};
```

### cURL Examples

#### Browse Root Directory

```bash
curl http://localhost:3333/api/projects/abc-123/files/browse
```

#### Browse Subdirectory

```bash
curl "http://localhost:3333/api/projects/abc-123/files/browse?path=src/components"
```

#### Read File

```bash
curl "http://localhost:3333/api/projects/abc-123/files/read?path=README.md"
```

#### Save File

```bash
curl -X POST http://localhost:3333/api/projects/abc-123/files/save \
  -H "Content-Type: application/json" \
  -d '{
    "path": "src/config.json",
    "content": "{\"version\": \"1.0.0\"}"
  }'
```

#### Get File Tree

```bash
curl "http://localhost:3333/api/projects/abc-123/files/tree?max_depth=2"
```

#### Create File

```bash
curl -X POST http://localhost:3333/api/projects/abc-123/files/create \
  -H "Content-Type: application/json" \
  -d '{
    "path": "src/new-file.ts",
    "type": "file",
    "content": "// New TypeScript file"
  }'
```

#### Create Directory

```bash
curl -X POST http://localhost:3333/api/projects/abc-123/files/create \
  -H "Content-Type: application/json" \
  -d '{
    "path": "src/new-directory",
    "type": "directory"
  }'
```

#### Rename File

```bash
curl -X POST http://localhost:3333/api/projects/abc-123/files/rename \
  -H "Content-Type: application/json" \
  -d '{
    "old_path": "src/old-name.ts",
    "new_path": "src/new-name.ts"
  }'
```

#### Delete File

```bash
curl -X POST http://localhost:3333/api/projects/abc-123/files/delete \
  -H "Content-Type: application/json" \
  -d '{
    "path": "src/file-to-delete.ts"
  }'
```

#### Copy File

```bash
curl -X POST http://localhost:3333/api/projects/abc-123/files/copy \
  -H "Content-Type: application/json" \
  -d '{
    "source_path": "src/template.ts",
    "destination_path": "src/new-file.ts"
  }'
```

## Performance Considerations

### Optimization Strategies

1. **Lazy Loading**: Load directories on-demand
2. **Caching**: Cache file lists for recently accessed directories
3. **Depth Limiting**: Restrict tree depth to prevent deep recursion
4. **Size Limits**: Reject large files early to save bandwidth

### Response Times

Typical response times on modern hardware:

| Operation | Items | Response Time |
|-----------|-------|---------------|
| Browse (small dir) | < 50 files | < 50ms |
| Browse (large dir) | 500+ files | 100-200ms |
| Read small file | < 100KB | < 20ms |
| Read medium file | 1-5MB | 100-500ms |
| Save file | Any size | 50-100ms |
| Tree (depth 3) | < 1000 files | 200-500ms |

## Rate Limiting

Currently no rate limiting implemented (local application).

For production deployment, consider:
- Request throttling per IP
- File size quotas per project
- Concurrent request limits

## Related Documentation

- [FileBrowser Component](../../components/FileBrowser.md)
- [Project Management API](./projects.md)
- [Architecture Overview](../../architecture/overview.md)

## API Version History

### Version 2.0 - File Management Operations (2025-11-18)
- Added `POST /create` - Create files and directories
- Added `POST /rename` - Rename/move files and directories
- Added `POST /delete` - Delete files and directories
- Added `POST /copy` - Copy files and directories
- Added HTTP 409 Conflict status for resource conflicts
- Enhanced security validation for all new operations

### Version 1.0 - Initial Release
- Browse files endpoint
- Read file endpoint
- Save file endpoint
- Get file tree endpoint

---

**Last Updated**: 2025-11-18
**API Version**: 2.0.0
**Backend Router**: `claudetask/backend/app/routers/file_browser.py`
