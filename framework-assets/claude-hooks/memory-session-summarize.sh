#!/bin/bash

# Memory Session Summarizer Hook
# Triggers intelligent summarization via Claude Code when threshold reached
#
# Hook event: Stop
#
# Input (via stdin): JSON with Stop event data including transcript
#
# When 30+ messages accumulated since last summary, this hook:
# 1. Calls /execute-command API to trigger /summarize-project
# 2. Claude Code analyzes recent conversations
# 3. Generates structured summary with key_decisions, tech_stack, patterns, gotchas

# Read input from stdin first (before sourcing logger which might read stdin)
INPUT=$(cat)

# Get project root from input JSON cwd field, or fall back to pwd
PROJECT_ROOT=$(echo "$INPUT" | python3 -c "import json,sys; d=json.load(sys.stdin); print(d.get('cwd', ''))" 2>/dev/null)
if [ -z "$PROJECT_ROOT" ]; then
    PROJECT_ROOT="$(pwd)"
fi

# Walk up to find .mcp.json (project root)
ORIGINAL_ROOT="$PROJECT_ROOT"
while [ ! -f "$PROJECT_ROOT/.mcp.json" ] && [ "$PROJECT_ROOT" != "/" ]; do
    PROJECT_ROOT="$(dirname "$PROJECT_ROOT")"
done

# If no .mcp.json found, use original
if [ ! -f "$PROJECT_ROOT/.mcp.json" ]; then
    PROJECT_ROOT="$ORIGINAL_ROOT"
fi

# Source hook logger for proper logging based on storage_mode
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
if [ -f "$SCRIPT_DIR/hook-logger.sh" ]; then
    source "$SCRIPT_DIR/hook-logger.sh"
    init_hook_log "memory-summarize"
else
    # Fallback if hook-logger not available
    log_hook() { echo "[$(date '+%Y-%m-%d %H:%M:%S')] memory-summarize | INFO | $1" >&2; }
    log_hook_success() { echo "[$(date '+%Y-%m-%d %H:%M:%S')] memory-summarize | SUCCESS | $1" >&2; }
    log_hook_error() { echo "[$(date '+%Y-%m-%d %H:%M:%S')] memory-summarize | ERROR | $1" >&2; }
    log_hook_skip() { echo "[$(date '+%Y-%m-%d %H:%M:%S')] memory-summarize | SKIPPED | $1" >&2; }
fi

# Get backend URL (default to localhost)
BACKEND_URL="${CLAUDETASK_BACKEND_URL:-http://localhost:3333}"

# Get project ID from .mcp.json
if [ -f "$PROJECT_ROOT/.mcp.json" ]; then
    PROJECT_ID=$(python3 -c "import json; data=json.load(open('$PROJECT_ROOT/.mcp.json')); print(data.get('mcpServers', {}).get('claudetask', {}).get('env', {}).get('CLAUDETASK_PROJECT_ID', ''))" 2>/dev/null)
fi

# Fallback: try to get from environment
if [ -z "$PROJECT_ID" ]; then
    PROJECT_ID="${CLAUDETASK_PROJECT_ID:-}"
fi

# If no project ID, skip silently
if [ -z "$PROJECT_ID" ]; then
    log_hook_skip "No project ID found"
    echo '{}'
    exit 0
fi

# Check if summarization is needed (threshold = 30 messages)
SHOULD_SUMMARIZE=$(curl -s "$BACKEND_URL/api/projects/$PROJECT_ID/memory/should-summarize?threshold=30" 2>/dev/null)

if [ -z "$SHOULD_SUMMARIZE" ]; then
    log_hook_error "Failed to check summarization status - backend not available"
    echo '{}'
    exit 0
fi

NEED_SUMMARY=$(echo "$SHOULD_SUMMARIZE" | python3 -c "import json,sys; d=json.load(sys.stdin); print('true' if d.get('should_summarize') else 'false')" 2>/dev/null)
MESSAGES_SINCE=$(echo "$SHOULD_SUMMARIZE" | python3 -c "import json,sys; d=json.load(sys.stdin); print(d.get('messages_since_last_summary', 0))" 2>/dev/null)

if [ "$NEED_SUMMARY" != "true" ]; then
    log_hook_skip "Only $MESSAGES_SINCE messages since last summary (threshold: 30)"
    echo '{}'
    exit 0
fi

log_hook "Starting intelligent summarization - $MESSAGES_SINCE messages since last summary"

# URL encode project directory (handle spaces and special characters)
PROJECT_DIR_ENCODED=$(printf '%s' "$PROJECT_ROOT" | jq -sRr @uri)

# Call execute-command API to trigger /summarize-project
# This will launch an embedded Claude session to perform intelligent summarization
API_URL="$BACKEND_URL/api/claude-sessions/execute-command?command=/summarize-project&project_dir=${PROJECT_DIR_ENCODED}"

log_hook "Triggering intelligent summarization via Claude Code"

# Make async API call (don't wait for response - summarization can take time)
# Use timeout to prevent blocking the hook
API_RESPONSE=$(curl -s --max-time 5 -X POST "$API_URL" \
    -H "Content-Type: application/json" \
    2>&1)

API_STATUS=$?

if [ $API_STATUS -eq 0 ]; then
    # Check if response indicates success
    SUCCESS=$(echo "$API_RESPONSE" | python3 -c "import json,sys; d=json.load(sys.stdin); print('true' if d.get('success') else 'false')" 2>/dev/null)
    SESSION_ID=$(echo "$API_RESPONSE" | python3 -c "import json,sys; d=json.load(sys.stdin); print(d.get('session_id', 'unknown'))" 2>/dev/null)

    if [ "$SUCCESS" = "true" ]; then
        log_hook_success "Intelligent summarization triggered (session: $SESSION_ID)"

        # Output notification to stderr
        cat << EOF >&2

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🧠 INTELLIGENT SUMMARIZATION TRIGGERED
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 $MESSAGES_SINCE messages accumulated
🤖 Claude Code analyzing session...
📝 Updating: summary, key_decisions, tech_stack, patterns, gotchas
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
EOF
    else
        log_hook_error "Failed to trigger summarization: $API_RESPONSE"
    fi
elif [ $API_STATUS -eq 28 ]; then
    # Timeout - this is OK, summarization is running in background
    log_hook_success "Intelligent summarization started (running in background)"
else
    log_hook_error "API call failed with status: $API_STATUS - $API_RESPONSE"

    # Fallback: save basic summary directly
    log_hook "Falling back to basic summary"

    # Get transcript_path from input JSON
    TRANSCRIPT_PATH=$(echo "$INPUT" | python3 -c "import json,sys; d=json.load(sys.stdin); print(d.get('transcript_path', ''))" 2>/dev/null)

    # Extract basic summary from transcript
    SUMMARY=$(python3 -c "
import json
import sys

transcript_path = '$TRANSCRIPT_PATH'

if not transcript_path:
    print('Session work completed')
    sys.exit(0)

try:
    files_modified = set()
    user_requests = []

    with open(transcript_path, 'r') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                entry = json.loads(line)
            except:
                continue

            msg_type = entry.get('type', '')

            if msg_type == 'user':
                content = entry.get('message', {}).get('content', '')
                if isinstance(content, str) and len(content) > 10 and len(content) < 200:
                    text = content.strip()
                    if not text.startswith('[') and not text.startswith('<') and not text.startswith('/'):
                        user_requests.append(text[:80])

            elif msg_type == 'assistant':
                content = entry.get('message', {}).get('content', [])
                if isinstance(content, list):
                    for block in content:
                        if isinstance(block, dict) and block.get('type') == 'tool_use':
                            tool = block.get('name', '')
                            tool_input = block.get('input', {})
                            if tool in ['Edit', 'Write', 'MultiEdit']:
                                file_path = tool_input.get('file_path', '')
                                if file_path:
                                    fname = file_path.split('/')[-1]
                                    files_modified.add(fname)

    summary_parts = []
    if user_requests:
        summary_parts.append(f'Task: {user_requests[-1]}')
    if files_modified:
        flist = list(files_modified)[:5]
        summary_parts.append(f'Files({len(files_modified)}): {chr(44).join(flist)}')

    if summary_parts:
        print(' | '.join(summary_parts))
    else:
        print('Session interaction')

except Exception as e:
    print(f'Error: {str(e)[:40]}')
" 2>/dev/null)

    if [ -z "$SUMMARY" ]; then
        SUMMARY="Session work completed"
    fi

    # Get last message ID for tracking
    LAST_MSG_ID=$(curl -s "$BACKEND_URL/api/projects/$PROJECT_ID/memory/messages?limit=1" 2>/dev/null | python3 -c "import json,sys; d=json.load(sys.stdin); msgs=d.get('messages',[]); print(msgs[0]['id'] if msgs else '')" 2>/dev/null)

    # Escape summary for JSON
    ESCAPED_SUMMARY=$(echo "$SUMMARY" | python3 -c "import json,sys; print(json.dumps(sys.stdin.read().strip()))" 2>/dev/null)

    # Build JSON payload
    if [ -n "$LAST_MSG_ID" ] && [ "$LAST_MSG_ID" != "0" ] && [ "$LAST_MSG_ID" != "None" ]; then
        JSON_PAYLOAD="{\"trigger\": \"session_end\", \"new_insights\": $ESCAPED_SUMMARY, \"last_summarized_message_id\": \"$LAST_MSG_ID\"}"
    else
        JSON_PAYLOAD="{\"trigger\": \"session_end\", \"new_insights\": $ESCAPED_SUMMARY}"
    fi

    # Update project summary (basic fallback)
    curl -s -X POST "$BACKEND_URL/api/projects/$PROJECT_ID/memory/summary/update" \
        -H "Content-Type: application/json" \
        -d "$JSON_PAYLOAD" \
        --connect-timeout 5 \
        --max-time 10 \
        2>/dev/null

    log_hook_success "Basic summary saved (fallback)"
fi

# Return empty JSON to approve without modification
echo '{}'
