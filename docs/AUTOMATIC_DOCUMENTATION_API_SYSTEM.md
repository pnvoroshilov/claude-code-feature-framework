# Automatic Documentation Update System (API-Driven)

## Overview

API-driven system that automatically triggers documentation updates when code is pushed to the main branch. The system uses backend API endpoints to queue Claude Code slash commands for execution.

## Architecture

### Component 1: Backend API Endpoint
**File**: `claudetask/backend/app/api/claude_sessions.py`

**Endpoint**: `POST /api/claude-sessions/execute-command`

**Parameters**:
- `command` (required): Claude Code slash command (e.g., `/update-documentation`)
- `project_dir` (optional): Project directory path

**Function**:
1. Validates command format (must start with `/`)
2. Checks if Claude Code is running for the project
3. If Claude running: Attempts to send command directly (future enhancement)
4. If Claude not running: Queues command in `.claude/logs/command_queue.txt`
5. Returns execution status and command details

**Response Example**:
```json
{
  "success": true,
  "message": "Command /update-documentation queued for execution",
  "command": "/update-documentation",
  "queue_file": "/path/to/.claude/logs/command_queue.txt",
  "note": "Command will be picked up by Claude Code on next prompt"
}
```

### Component 2: PostToolUse Hook
**File**: `.claude/hooks/post-push-docs.sh`

**Triggers**: After any Bash tool execution

**Function**:
1. Monitors bash commands for `git push origin main/master`
2. When detected:
   - Calls backend API: `POST /api/claude-sessions/execute-command`
   - Passes `/update-documentation` command
   - Passes project directory path
3. Logs API call status and response
4. **Fallback**: If API unavailable, creates marker file for UserPromptSubmit hook
5. Outputs success message to stderr (visible in Claude Code)

**API Call**:
```bash
API_URL="http://localhost:3333/api/claude-sessions/execute-command"
COMMAND="/update-documentation"
PROJECT_ROOT="$(pwd)"

curl -s -X POST "$API_URL?command=${COMMAND}&project_dir=${PROJECT_ROOT}" \
    -H "Content-Type: application/json"
```

### Component 3: Documentation Update Command
**File**: `.claude/commands/update-documentation.md`

**Updates**:
- Analyzes ONLY recent changes: `git log origin/main..HEAD`
- Compares files: `git diff origin/main..HEAD`
- Updates documentation ONLY for changed code
- Does NOT rebuild entire documentation

**Agent**: `documentation-updater-agent`

**Workflow**:
1. Analyze commits since last sync with origin/main
2. Identify affected files and features
3. Update docs ONLY for changed components
4. Create docs ONLY for new features
5. Delete docs ONLY for removed features

### Component 4: Fallback System (UserPromptSubmit Hook)
**File**: `.claude/hooks/inject-docs-update.sh`

**Purpose**: Backup mechanism when API is unavailable

**Function**:
1. Checks for marker file (`.claude/logs/hooks/.docs-update-pending`)
2. If marker exists:
   - Removes marker (one-time trigger)
   - Injects critical instruction into Claude's context
   - Claude sees instruction and executes command
3. If no marker: Returns empty JSON (normal operation)

## Workflow

### Primary Workflow (API Available):
```
1. Developer: git push origin main
   ↓
2. PostToolUse Hook: Detects push
   ↓
3. Hook → Backend API: POST /execute-command
   ↓
4. Backend API: Queues /update-documentation
   ↓
5. Claude Code: Picks up queued command
   ↓
6. Claude: Executes /update-documentation
   ↓
7. documentation-updater-agent: Updates ONLY changed docs
```

### Fallback Workflow (API Unavailable):
```
1. Developer: git push origin main
   ↓
2. PostToolUse Hook: API call fails
   ↓
3. Hook: Creates marker file (.docs-update-pending)
   ↓
4. User: Types next message
   ↓
5. UserPromptSubmit Hook: Detects marker
   ↓
6. Hook: Injects instruction into context
   ↓
7. Claude: Sees instruction → Executes /update-documentation
   ↓
8. documentation-updater-agent: Updates ONLY changed docs
```

## Configuration

### Backend API (FastAPI)
**Port**: 3333 (default)
**Base URL**: `http://localhost:3333`
**Endpoint**: `/api/claude-sessions/execute-command`

### Hook Configuration (`.claude/settings.json`):
```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": ".claude/hooks/post-push-docs.sh"
          }
        ]
      }
    ],
    "UserPromptSubmit": [
      {
        "matcher": "*",
        "hooks": [
          {
            "type": "command",
            "command": ".claude/hooks/inject-docs-update.sh"
          }
        ]
      }
    ]
  }
}
```

## Key Features

### 1. Incremental Documentation Updates
**Critical improvement**: Documentation is updated ONLY for changed code

```bash
# Agent analyzes ONLY recent changes
git log origin/main..HEAD --oneline
git diff origin/main..HEAD --name-only

# Updates ONLY affected documentation
# Does NOT rebuild entire docs folder
```

**Benefits**:
- ✅ Faster updates (only changed files)
- ✅ No unnecessary rewrites
- ✅ Preserves manual documentation edits (if unrelated to changes)
- ✅ Reduces git noise in documentation files

### 2. API-Driven Execution
**How it works**:
- Hook calls HTTP API instead of creating files
- API queues commands for Claude to execute
- Clean separation of concerns

**Benefits**:
- ✅ True automation (no dependency on user prompts)
- ✅ Immediate command queuing
- ✅ Scalable architecture
- ✅ Can be extended to other commands

### 3. Reliable Fallback Mechanism
**Two-tier reliability**:
1. **Primary**: API-driven command queuing
2. **Fallback**: Marker file + UserPromptSubmit hook

**Benefits**:
- ✅ Works even if backend is down
- ✅ No missed documentation updates
- ✅ Graceful degradation

### 4. Full Audit Trail
**Log files**:
- `.claude/logs/hooks/post-merge-doc-YYYYMMDD.log` - Hook execution logs
- `.claude/logs/hooks/user-prompt-YYYYMMDD.log` - UserPromptSubmit logs
- Backend logs - API call logs

## Testing

### Test Primary Workflow (API Available):

1. **Start backend**:
```bash
cd claudetask/backend
source venv/bin/activate
python -m uvicorn app.main:app --port 3333
```

2. **Make changes and push**:
```bash
# Make code changes
git add .
git commit -m "feat: Add new feature"
git push origin main
```

3. **Check logs**:
```bash
# Hook should show successful API call
tail -20 .claude/logs/hooks/post-merge-doc-$(date +%Y%m%d).log

# Should see:
# [TIMESTAMP] API call successful
# [TIMESTAMP] Response: {"success":true,...}
```

4. **Check command queue**:
```bash
cat .claude/logs/command_queue.txt
# Should contain: /update-documentation
```

### Test Fallback Workflow (API Unavailable):

1. **Stop backend** (if running)

2. **Make changes and push**:
```bash
git add .
git commit -m "feat: Add new feature"
git push origin main
```

3. **Check logs**:
```bash
tail -20 .claude/logs/hooks/post-merge-doc-$(date +%Y%m%d).log

# Should see:
# [TIMESTAMP] API call failed with status: 3
# [TIMESTAMP] Fallback: Created marker file for UserPromptSubmit hook
```

4. **Check marker file**:
```bash
cat .claude/logs/hooks/.docs-update-pending
# Should contain timestamp
```

5. **Type any message to Claude**:
- UserPromptSubmit hook will inject instruction
- Claude will execute /update-documentation

## Skipping Automatic Updates

Add `[skip-hook]` to commit message:
```bash
git commit -m "docs: Fix typo [skip-hook]"
git push origin main
```

Hook will detect tag and skip documentation update.

## Troubleshooting

### API Call Failing
**Symptom**: Logs show "API call failed"
**Causes**:
1. Backend not running
2. Wrong port (not 3333)
3. API endpoint changed

**Solution**:
```bash
# Check if backend is running
curl http://localhost:3333/health

# Start backend
cd claudetask/backend
source venv/bin/activate
python -m uvicorn app.main:app --port 3333
```

### Documentation Not Updating
**Symptom**: No documentation changes after push
**Debugging**:
1. Check hook logs:
```bash
tail -50 .claude/logs/hooks/post-merge-doc-$(date +%Y%m%d).log
```

2. Check marker file:
```bash
ls -la .claude/logs/hooks/.docs-update-pending
```

3. Check command queue:
```bash
cat .claude/logs/command_queue.txt 2>/dev/null
```

4. Verify `/update-documentation` command exists:
```bash
ls -la .claude/commands/update-documentation.md
```

### Clearing Pending Updates
```bash
# Remove marker file
rm -f .claude/logs/hooks/.docs-update-pending

# Clear command queue
rm -f .claude/logs/command_queue.txt
```

## File Locations

| File | Purpose |
|------|---------|
| `claudetask/backend/app/api/claude_sessions.py` | API endpoint for command execution |
| `.claude/hooks/post-push-docs.sh` | PostToolUse hook (detects push, calls API) |
| `.claude/hooks/inject-docs-update.sh` | UserPromptSubmit hook (fallback) |
| `.claude/commands/update-documentation.md` | Documentation update command definition |
| `.claude/settings.json` | Hook configuration |
| `.claude/logs/hooks/.docs-update-pending` | Marker file (fallback mechanism) |
| `.claude/logs/command_queue.txt` | Command queue (API writes here) |
| `.claude/logs/hooks/post-merge-doc-YYYYMMDD.log` | Hook execution logs |
| `.claude/logs/hooks/user-prompt-YYYYMMDD.log` | UserPromptSubmit logs |

## Benefits Over Previous Approaches

### vs. Direct Hook Execution
- ✅ Cleaner architecture (API handles complexity)
- ✅ Extensible (can add more commands)
- ✅ Better error handling
- ✅ Full audit trail

### vs. UserPromptSubmit Only
- ✅ Immediate execution (no wait for user prompt)
- ✅ True automation
- ✅ No dependency on user interaction

### vs. Full Documentation Rebuild
- ✅ **Much faster** (only changed files)
- ✅ **Less git noise** (fewer file changes)
- ✅ **Preserves manual edits** (if unrelated)
- ✅ **Targeted updates** (focused on actual changes)

## Future Enhancements

- [ ] Real-time command execution (send to Claude stdin directly)
- [ ] Support for command parameters (e.g., `/update-documentation api`)
- [ ] Multiple command queue (FIFO processing)
- [ ] Command execution status tracking
- [ ] Web UI for command management
- [ ] Notification when update completes

---

**Last Updated**: 2025-11-14
**Version**: 2.0.0 (API-Driven)
