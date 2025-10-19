# Task Indexing in RAG System

## Overview

The RAG system automatically indexes completed tasks to enable historical learning and similarity search. This allows agents to learn from past implementations when analyzing new tasks.

## How It Works

### 1. Automatic Indexing Trigger

Tasks are **automatically indexed** when their status changes to **"Done"**:

```python
# In claudetask_mcp_bridge.py -> _update_status()

if status == "Done" and self.rag_initialized:
    await self.rag_service.index_task(task)
```

**Trigger Point**: `mcp:update_status <task_id> "Done"`

### 2. Task Data Indexed

The following task information is indexed:

```python
task_text = f"""
Title: {task.title}
Type: {task.task_type}
Priority: {task.priority}
Description: {task.description}
Analysis: {task.analysis}
"""
```

**Stored Metadata**:
- `task_id`: Unique task identifier
- `title`: Task title
- `task_type`: Feature/Bug/Enhancement/etc.
- `priority`: High/Medium/Low
- `status`: "Done" (always for indexed tasks)

### 3. Vector Embeddings

- **Model**: `all-MiniLM-L6-v2` (384 dimensions)
- **Storage**: ChromaDB `task_history` collection
- **Search Type**: Semantic similarity (not keyword matching)

### 4. Similarity Search

Agents can find similar past tasks using:

```python
# MCP Tool
mcp__claudetask__find_similar_tasks(
    task_description="Need to implement OAuth2 authentication",
    top_k=10
)
```

**Returns**:
- `task_id`: Original task ID
- `title`: Task title
- `task_type`, `priority`, `status`: Task metadata
- `content`: Full task text (title + description + analysis)
- `similarity`: Relevance score (0.0-1.0, higher is better)

## Usage Example

### Scenario: New Authentication Task

1. **New Task Created**: "Implement two-factor authentication"
   - Status: Backlog → Analysis

2. **Agent Searches History**:
   ```python
   results = mcp__claudetask__find_similar_tasks(
       "two-factor authentication 2FA security",
       top_k=5
   )
   ```

3. **RAG Returns**:
   - Task #42: "Implement OAuth2 Social Login" (similarity: 0.75)
   - Task #38: "Add JWT Token Validation" (similarity: 0.68)
   - Task #29: "Implement Session Security" (similarity: 0.62)

4. **Agent Learns**:
   - OAuth2 pattern used successfully before
   - JWT tokens already implemented
   - Can extend existing auth middleware
   - Avoids reinventing security patterns

## Database Structure

### Collection: `task_history`

```
ChromaDB Location: .claudetask/chromadb/
Collection Name: task_history
Embedding Model: all-MiniLM-L6-v2 (384 dims)

Document Format:
{
    "id": "task_42_uuid",
    "embedding": [0.123, -0.456, ...],  # 384 dimensions
    "document": "Title: ...\nDescription: ...",
    "metadata": {
        "task_id": 42,
        "title": "...",
        "task_type": "Feature",
        "priority": "High",
        "status": "Done"
    }
}
```

## Benefits

### 1. **Historical Context**
Agents learn from past implementations:
- What worked well
- Technical decisions made
- Patterns established

### 2. **Avoid Reinvention**
Discover existing:
- Similar features
- Reusable patterns
- Architectural decisions

### 3. **Better Estimates**
Base effort on similar past tasks:
- Complexity comparison
- Time estimates
- Resource requirements

### 4. **Consistency**
Follow established patterns:
- Code conventions
- Architecture styles
- Integration approaches

## Integration Points

### 1. Requirements Analysis Agent

```python
# requirements-analyst uses RAG for historical context

# Find similar requirements
similar_tasks = mcp__claudetask__find_similar_tasks(
    task_description="user notification system",
    top_k=10
)

# Learn from past:
# - How notifications were implemented before
# - What challenges arose
# - What patterns worked
```

### 2. Systems Analyst Agent

```python
# systems-analyst uses RAG to understand codebase

# Search for authentication code
auth_code = mcp__claudetask__search_codebase(
    query="authentication JWT middleware",
    top_k=30
)

# Find similar architectural decisions
similar = mcp__claudetask__find_similar_tasks(
    "authentication system design",
    top_k=5
)
```

### 3. Context Analyzer Agent

```python
# context-analyzer uses both RAG tools

# Step 1: Find similar past tasks
history = mcp__claudetask__find_similar_tasks(
    "payment processing integration",
    top_k=15
)

# Step 2: Find relevant code
code = mcp__claudetask__search_codebase(
    "payment transaction API endpoints",
    top_k=40
)

# Combined analysis with historical and current context
```

## Performance

### Indexing Speed
- **Single Task**: ~50-100ms
- **Embedding Generation**: ~30-50ms
- **ChromaDB Insert**: ~20-50ms

### Search Speed
- **Query Embedding**: ~30-50ms
- **Vector Search**: ~10-30ms (depends on collection size)
- **Total**: ~50-100ms for typical search

### Storage
- **Per Task**: ~5-10 KB (embedding + metadata + text)
- **100 Tasks**: ~500 KB - 1 MB
- **1000 Tasks**: ~5-10 MB

Very efficient for typical project sizes (hundreds of tasks).

## Maintenance

### Manual Reindexing

If needed, tasks can be manually reindexed:

```python
# In RAGService
await rag_service.index_task(task_dict)
```

### Collection Reset

To clear task history:

```python
# Delete collection
client.delete_collection("task_history")

# Recreate
await rag_service._initialize_collections()
```

## Future Enhancements

### Potential Improvements

1. **Task Outcomes**
   - Store whether task succeeded/failed
   - Track bugs found after completion
   - Record user feedback

2. **Time Tracking**
   - Store actual time taken
   - Compare estimates vs actuals
   - Improve future estimates

3. **Code Quality Metrics**
   - Lines of code changed
   - Test coverage achieved
   - Review comments count

4. **Dependency Tracking**
   - Related tasks
   - Blocked by / blocks
   - Prerequisite tasks

5. **Tag/Category Search**
   - Filter by task type
   - Filter by technology (React/Python/etc)
   - Filter by priority

## Testing

Comprehensive test suite available:

```bash
# Run task indexing tests
python claudetask/mcp_server/test_rag_task_indexing.py
```

Tests verify:
- ✅ Tasks indexed correctly when marked as Done
- ✅ Semantic search finds relevant tasks
- ✅ Metadata stored properly
- ✅ Similarity scores work correctly
- ✅ Different task types ranked appropriately

## Troubleshooting

### Task Not Indexed

**Symptom**: Task marked as Done, but not found in searches

**Causes**:
1. RAG not initialized: Check MCP server logs
2. Indexing error: Check for exceptions in logs
3. ChromaDB path issue: Verify `.claudetask/chromadb/` exists

**Solution**:
```bash
# Check ChromaDB
python -c "import chromadb; client = chromadb.PersistentClient('.claudetask/chromadb'); print(client.get_collection('task_history').count())"
```

### Poor Search Results

**Symptom**: Similar tasks not ranked highly

**Causes**:
1. Query too vague: Use more specific terms
2. No similar tasks exist: Check task history
3. Different terminology: Use synonyms

**Solution**:
```python
# Use descriptive queries with context
mcp__claudetask__find_similar_tasks(
    "OAuth2 social login authentication Google Facebook JWT tokens",
    top_k=20  # Increase results
)
```

## Summary

The RAG task indexing system:

1. ✅ **Automatically** indexes tasks when marked as Done
2. ✅ **Stores** title, description, analysis, and metadata
3. ✅ **Enables** semantic similarity search
4. ✅ **Helps** agents learn from past work
5. ✅ **Improves** future task analysis and estimation

This creates an organizational memory that grows over time, making the system smarter with each completed task!
