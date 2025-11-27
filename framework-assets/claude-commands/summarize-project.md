---
allowed-tools: [Bash, Read, Write, mcp__claudetask__complete_hook_session]
description: Intelligent project summarization - analyze session and update project memory with structured insights
---

# Intelligent Project Summarization

This command performs intelligent analysis of recent conversations and updates the project summary with structured insights.

## Workflow

### Step 1: Load Current Context

First, I need to get the current project summary and recent messages from the backend API.

```bash
# Get project ID from .mcp.json
PROJECT_ID=$(python3 -c "import json; data=json.load(open('.mcp.json')); print(data.get('mcpServers', {}).get('claudetask', {}).get('env', {}).get('CLAUDETASK_PROJECT_ID', ''))" 2>/dev/null)

# Get current summary
curl -s "http://localhost:3333/api/projects/$PROJECT_ID/memory/summary"

# Get last 30 messages
curl -s "http://localhost:3333/api/projects/$PROJECT_ID/memory/messages?limit=30"
```

### Step 2: Analyze and Generate Structured Summary

Based on the current summary and recent messages, I will:

1. **Identify Key Decisions** - Extract architectural and implementation decisions:
   - Technology choices (e.g., "Switched from PostgreSQL to MongoDB")
   - Design patterns adopted (e.g., "Using Repository pattern for data access")
   - Important trade-offs made

2. **Update Tech Stack** - Extract technologies mentioned:
   - Programming languages (Python, TypeScript, etc.)
   - Frameworks (FastAPI, React, etc.)
   - Databases (MongoDB, PostgreSQL, etc.)
   - Tools (Docker, Git, etc.)

3. **Identify Patterns** - Coding and architectural patterns:
   - Design patterns used
   - Code organization patterns
   - Testing patterns

4. **Capture Gotchas** - Important warnings and pitfalls:
   - Known issues and workarounds
   - Configuration requirements
   - Common mistakes to avoid

5. **Write New Summary** - Concise narrative of the project:
   - What the project does
   - Current state and progress
   - Recent major changes

### Step 3: Update Project Summary via API

After analyzing, I'll call the API to update the structured summary:

```bash
curl -s -X POST "http://localhost:3333/api/projects/$PROJECT_ID/memory/summary/intelligent-update" \
  -H "Content-Type: application/json" \
  -d '{
    "summary": "New comprehensive summary text...",
    "key_decisions": [
      "Decision 1: Reason",
      "Decision 2: Reason"
    ],
    "tech_stack": ["Python", "FastAPI", "MongoDB", "React"],
    "patterns": ["Repository Pattern", "Hook-based Logging"],
    "gotchas": [
      "Always check storage_mode before logging",
      "Use [skip-hook] tag to prevent infinite loops"
    ]
  }'
```

## Analysis Guidelines

When analyzing conversations, I will:

1. **Merge, don't replace** - Combine new insights with existing ones
2. **Keep it relevant** - Only include project-specific information
3. **Be concise** - Each item should be actionable and clear
4. **Deduplicate** - Don't repeat existing entries
5. **Prioritize recency** - Recent decisions may override old ones

## Output Format

The updated summary will have this structure:

```json
{
  "summary": "Comprehensive project narrative (2-5 paragraphs)",
  "key_decisions": ["Decision: Reason", ...],
  "tech_stack": ["Technology1", "Technology2", ...],
  "patterns": ["Pattern1", "Pattern2", ...],
  "gotchas": ["Warning or pitfall", ...]
}
```

## Automatic Trigger

This command is automatically triggered by the `memory-session-summarize` hook:
- When Stop event occurs (Claude session ends)
- When 30+ messages have accumulated since last summary
- When important decisions are detected

## Example Output

After analysis, the summary might look like:

```
Summary: ClaudeTask Framework is an autonomous task orchestration system
built with Python FastAPI backend and React frontend. It integrates with
Claude Code via MCP protocol for intelligent code assistance. Recent work
focused on migrating memory storage from SQLite to MongoDB Atlas with
Voyage AI embeddings for semantic search.

Key Decisions:
- Migrated to MongoDB Atlas for better scalability
- Adopted hook-based logging system with storage_mode support
- Using Voyage AI for embeddings instead of OpenAI

Tech Stack:
- Python, FastAPI, MongoDB, React, TypeScript, Voyage AI

Patterns:
- Repository pattern for data access
- Hook-logger centralization
- MCP-based tool integration

Gotchas:
- Always source hook-logger.sh in hooks
- Use [skip-hook] tag to prevent infinite loops
- Check storage_mode before logging
```

---

## Session Cleanup (IMPORTANT)

**When this command is triggered by a hook (automatically), you MUST call `mcp__claudetask__complete_hook_session` at the very end to cleanup the session.**

This is critical because:
- Hook-triggered commands run in an embedded Claude session
- Without cleanup, the session process remains running indefinitely
- The MCP tool will gracefully terminate the session

### Final Step (MANDATORY for hook-triggered execution):

After completing all summarization work, call:
```
mcp__claudetask__complete_hook_session
```

This will:
1. Find any active hook sessions
2. Gracefully stop them
3. Free up system resources

---

Let me now analyze the current project state and generate an intelligent summary...
