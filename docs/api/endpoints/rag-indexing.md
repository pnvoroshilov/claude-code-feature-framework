# RAG Indexing API

This document describes the new indexing functions added to the RAG MCP system.

## Overview

Two new MCP tools have been added to provide more control over the RAG indexing process:

1. **`index_codebase`** - Index the entire codebase from scratch
2. **`index_files`** - Index or re-index specific files

## MCP Tools

### 1. `index_codebase`

Index the entire codebase for RAG semantic search. Use this for initial indexing or when you want to rebuild the entire index from scratch.

**Parameters:** None

**Example Usage:**
```python
# Via MCP
await mcp.call_tool("index_codebase", {})
```

**Response:**
```
✅ Codebase indexing completed successfully

Total chunks indexed: 1380
```

**Use Cases:**
- Initial setup of RAG index
- Complete rebuild after major codebase changes
- Recovery from corrupted index

---

### 2. `index_files`

Index or re-index specific files for RAG semantic search. Useful for updating the index after modifying specific files.

**Parameters:**
- `file_paths` (required): Array of file paths to index (absolute or relative to project root)

**Example Usage:**
```python
# Via MCP
await mcp.call_tool("index_files", {
    "file_paths": [
        "claudetask/mcp_server/rag/rag_service.py",
        "claudetask/backend/app/models.py"
    ]
})
```

**Response:**
```
✅ File indexing completed successfully

Files indexed: 2
Files skipped: 0
Total chunks: 58
```

**Use Cases:**
- Update index after file modifications
- Add newly created files to the index
- Re-index files with errors
- Selective indexing for testing

---

## RAG Service Methods

### `rag_service.index_codebase(repo_path: str)`

Low-level method that indexes the entire codebase.

**Parameters:**
- `repo_path`: Path to repository root

**Behavior:**
- Walks through entire repository
- Skips directories: `node_modules`, `venv`, `__pycache__`, `.git`, `dist`, `build`, `.next`, `target`, `bin`, `obj`, `.claudetask`, `worktrees`
- Supports file types: `.py`, `.js`, `.ts`, `.tsx`, `.jsx`, `.java`, `.cs`, `.go`, `.rs`, `.cpp`, `.c`, `.rb`, `.php`, `.swift`, `.kt`
- Creates semantic chunks with summaries
- Generates embeddings using SentenceTransformer
- Stores in ChromaDB

**Example:**
```python
await rag_service.index_codebase("/path/to/project")
```

---

### `rag_service.index_files(file_paths: List[str], repo_path: str)`

Low-level method that indexes specific files.

**Parameters:**
- `file_paths`: List of file paths (absolute or relative to repo_path)
- `repo_path`: Path to repository root

**Returns:**
```python
{
    'indexed_files': int,      # Number of successfully indexed files
    'skipped_files': int,      # Number of skipped files
    'total_chunks': int        # Total chunks created
}
```

**Behavior:**
- Accepts both absolute and relative paths
- Validates file existence
- Checks file extension support
- **Removes existing chunks before re-indexing** (prevents duplicates)
- Handles errors gracefully (continues with other files)
- Returns detailed statistics

**Example:**
```python
result = await rag_service.index_files(
    ["src/main.py", "lib/utils.py"],
    "/path/to/project"
)
print(f"Indexed {result['indexed_files']} files")
```

---

## Features

### 1. **Idempotent Re-indexing**
When re-indexing existing files, old chunks are automatically removed before adding new ones. This prevents duplicates and ensures the index stays clean.

### 2. **Error Handling**
- Non-existent files are skipped with warning
- Unsupported file types are skipped
- File-level errors don't stop the entire operation
- Detailed statistics in response

### 3. **Supported File Types**
- Python: `.py`
- JavaScript/TypeScript: `.js`, `.ts`, `.tsx`, `.jsx`
- Java: `.java`
- C#: `.cs`
- Go: `.go`
- Rust: `.rs`
- C/C++: `.c`, `.cpp`
- Ruby: `.rb`
- PHP: `.php`
- Swift: `.swift`
- Kotlin: `.kt`

### 4. **Automatic Language Detection**
File language is automatically detected from extension and stored in metadata.

---

## Testing

Comprehensive test suite available in `test_rag_indexing.py`:

```bash
cd claudetask/mcp_server
python test_rag_indexing.py
```

**Test Coverage:**
- ✅ Full codebase indexing
- ✅ Specific file indexing
- ✅ Re-indexing existing files (no duplicates)
- ✅ Non-existent files
- ✅ Unsupported file types
- ✅ Empty file lists
- ✅ Mixed valid/invalid files

---

## Performance Notes

### `index_codebase`
- Duration: ~5-30 seconds for medium projects (depends on codebase size)
- Memory: ~100-500MB (depends on embedding model)
- I/O: Reads all supported files

### `index_files`
- Duration: ~100-500ms per file
- Memory: Minimal (only processes specified files)
- I/O: Only reads specified files

---

## Implementation Details

### Chunking Strategy
Uses `GenericChunker` with:
- Chunk size: 500 tokens
- Chunk overlap: 50 tokens
- Semantic boundaries (respects functions, classes, blocks)

### Embedding Model
- Model: `all-MiniLM-L6-v2` (SentenceTransformer)
- Dimension: 384
- Speed: ~100 chunks/second

### Storage
- Vector DB: ChromaDB
- Persistence: Framework root `.claude/data/chromadb` (centralized, shared across all projects)
- Collection: `codebase_chunks`
- **Note**: As of 2025-11-25, ChromaDB storage is centralized in the framework root directory, not per-project

---

## Examples

### Example 1: Initial Project Setup
```python
# First time setup
await mcp.call_tool("index_codebase", {})
```

### Example 2: After File Modifications
```python
# Re-index modified files
await mcp.call_tool("index_files", {
    "file_paths": [
        "src/feature.py",
        "tests/test_feature.py"
    ]
})
```

### Example 3: Add New Files
```python
# Index newly created files
await mcp.call_tool("index_files", {
    "file_paths": [
        "src/new_module.py",
        "src/new_helper.py"
    ]
})
```

### Example 4: Selective Testing
```python
# Index only test-related files
await mcp.call_tool("index_files", {
    "file_paths": [
        "tests/test_auth.py",
        "tests/test_api.py",
        "src/auth.py",
        "src/api.py"
    ]
})
```

---

## Best Practices

1. **Use `index_files` for incremental updates** - Faster and more efficient than full reindex
2. **Use `index_codebase` sparingly** - Only for initial setup or major refactoring
3. **Re-index after major changes** - Keep the index fresh for better search results
4. **Index related files together** - Helps maintain context
5. **Monitor index size** - Large codebases may need index cleanup

---

## Future Enhancements

Potential improvements:
- [ ] Support for markdown documentation files
- [ ] Automatic index updates on file changes (file watcher)
- [ ] Partial chunk updates (instead of full file re-indexing)
- [ ] Index compression for large codebases
- [ ] Multi-language summaries
- [ ] Custom chunking strategies per file type
