# Merge Commit Reindexing

## Overview

The RAG system now supports **smart reindexing** after merge operations. Instead of reindexing the entire codebase, it only reindexes files that were changed in the merge commit.

## How It Works

### Traditional Approach (Slow)
```python
# Reindex entire codebase after merge
await rag_service.update_index_incremental(repo_path)
# This checks EVERY file for changes - slow for large codebases
```

### New Approach (Fast)
```python
# Reindex only changed files from merge commit
await rag_service.reindex_merge_commit(repo_path)
# This only processes files that were actually merged - much faster!
```

## Implementation Details

### 1. Git Diff Analysis
The system uses GitPython to analyze the merge commit:

```python
# Get merge commit (default: HEAD)
commit = repo.head.commit

# Compare with first parent (main branch)
parent = commit.parents[0]

# Get diff to find changed files
diffs = parent.diff(commit)
```

### 2. Changed Files Detection
For each diff, the system extracts file paths:

```python
changed_files = set()
for diff in diffs:
    if diff.a_path:
        changed_files.add(diff.a_path)  # Old path
    if diff.b_path:
        changed_files.add(diff.b_path)  # New path
```

### 3. Selective Reindexing
Only changed files are reindexed:

1. **Existing files** → Remove old chunks, add new chunks
2. **New files** → Add chunks
3. **Deleted files** → Remove chunks

```python
for file_path in changed_files:
    if os.path.exists(file_path):
        # Reindex existing/new file
        await self._remove_file_chunks(file_path)
        # ... chunk and reindex ...
    else:
        # File was deleted - remove from index
        await self._remove_file_chunks(file_path)
```

## Usage

### Automatic (After Task Merge)
When a task is merged to main via MCP, RAG automatically reindexes:

```python
# In claudetask_mcp_bridge.py
if result.get("merged") and self.rag_initialized:
    await self.rag_service.reindex_merge_commit(self.project_path)
```

### Manual (Via MCP Tool)
The `reindex_codebase` MCP tool still uses full incremental update for manual reindexing:

```python
# User triggers manual reindex
await rag_service.update_index_incremental(repo_path)
```

## Performance Benefits

### Example: 1000-file codebase, 10 files changed in merge

| Method | Files Checked | Files Reindexed | Time |
|--------|---------------|-----------------|------|
| Full Incremental | 1000 | 10 | ~30s |
| Merge Reindex | 10 | 10 | ~1s |

**Result: 30x faster!**

## Edge Cases Handled

### 1. Non-Merge Commits
If the commit is not a merge commit (single parent), it still works:

```python
if len(commit.parents) < 2:
    logger.warning("Not a merge commit, using regular diff")
    parent = commit.parents[0]
```

### 2. File Renames
Both old and new paths are captured:

```python
if diff.a_path:  # Old name
    changed_files.add(diff.a_path)
if diff.b_path and diff.b_path != diff.a_path:  # New name
    changed_files.add(diff.b_path)
```

### 3. Deleted Files
Files that no longer exist are removed from index:

```python
if not os.path.exists(full_path):
    await self._remove_file_chunks(file_path)
    logger.info(f"Removed deleted file: {file_path}")
```

### 4. Unsupported File Types
Only supported code files are processed:

```python
supported_extensions = {'.py', '.js', '.ts', '.tsx', '.jsx', ...}
if ext not in supported_extensions:
    continue
```

## Testing

Run the merge reindex test:

```bash
cd claudetask/mcp_server
python test_rag_merge.py
```

This test:
1. Creates a git repository
2. Makes commits on feature branch
3. Merges to main
4. Verifies only changed files are reindexed
5. Confirms search works for all files

## API Reference

### `reindex_merge_commit(repo_path, merge_commit_sha=None)`

Reindex only files changed in a merge commit.

**Parameters:**
- `repo_path` (str): Path to git repository
- `merge_commit_sha` (str, optional): SHA of merge commit. Defaults to HEAD.

**Raises:**
- `Exception`: If git operations fail or reindexing encounters errors

**Example:**
```python
# Reindex latest merge (HEAD)
await rag_service.reindex_merge_commit("/path/to/repo")

# Reindex specific merge commit
await rag_service.reindex_merge_commit("/path/to/repo", "abc123def")
```

### `_remove_file_chunks(file_path)`

Remove all chunks for a specific file from the index.

**Parameters:**
- `file_path` (str): Relative path to file

**Internal method** - used by reindexing functions.

## Benefits

1. **⚡ Faster Reindexing** - Only processes changed files
2. **💾 Less Resource Usage** - Fewer embeddings to generate
3. **🎯 Precise Updates** - Only touches what was merged
4. **🔄 Automatic** - Happens automatically after merge
5. **🛡️ Safe** - Handles edge cases (renames, deletes, etc.)

## Future Improvements

Potential enhancements:

1. **Incremental commit tracking** - Track changes across multiple commits
2. **Batch processing** - Group multiple merges for batch reindexing
3. **Conflict detection** - Detect when files have merge conflicts
4. **Statistics tracking** - Log reindexing performance metrics
