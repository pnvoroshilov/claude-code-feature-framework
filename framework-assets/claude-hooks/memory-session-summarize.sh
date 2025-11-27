#!/bin/bash

# Memory Session Summarizer Hook
# Checks if summarization is needed (every 30 messages) and updates project summary
#
# Hook event: Stop
#
# Input (via stdin): JSON with Stop event data including transcript

# Read input from stdin first
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

LOGDIR="$PROJECT_ROOT/.claude/logs/hooks"
LOGFILE="$LOGDIR/memory-summarize-$(date +%Y%m%d).log"

# Create log directory
mkdir -p "$LOGDIR" 2>/dev/null

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
    echo '{}'
    exit 0
fi

log_message() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" >> "$LOGFILE"
}

# Check if summarization is needed (threshold = 30 messages)
SHOULD_SUMMARIZE=$(curl -s "$BACKEND_URL/api/projects/$PROJECT_ID/memory/should-summarize?threshold=30" 2>/dev/null)

if [ -z "$SHOULD_SUMMARIZE" ]; then
    log_message "Failed to check summarization status - backend not available"
    echo '{}'
    exit 0
fi

NEED_SUMMARY=$(echo "$SHOULD_SUMMARIZE" | python3 -c "import json,sys; d=json.load(sys.stdin); print('true' if d.get('should_summarize') else 'false')" 2>/dev/null)
MESSAGES_SINCE=$(echo "$SHOULD_SUMMARIZE" | python3 -c "import json,sys; d=json.load(sys.stdin); print(d.get('messages_since_last_summary', 0))" 2>/dev/null)

if [ "$NEED_SUMMARY" != "true" ]; then
    log_message "Skipping summarization - only $MESSAGES_SINCE messages since last summary (threshold: 30)"
    echo '{}'
    exit 0
fi

log_message "Starting summarization - $MESSAGES_SINCE messages since last summary"

# Get transcript_path from input JSON
TRANSCRIPT_PATH=$(echo "$INPUT" | python3 -c "import json,sys; d=json.load(sys.stdin); print(d.get('transcript_path', ''))" 2>/dev/null)

log_message "Transcript path: $TRANSCRIPT_PATH"

# Extract summary from transcript file (JSONL format - one JSON per line)
SUMMARY=$(python3 -c "
import json
import sys

transcript_path = '$TRANSCRIPT_PATH'

if not transcript_path:
    print('Session work completed')
    sys.exit(0)

try:
    files_modified = set()
    key_activities = []
    user_requests = []

    # Parse JSONL file (one JSON object per line)
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

            # Get user requests for context
            if msg_type == 'user':
                content = entry.get('message', {}).get('content', '')
                if isinstance(content, str) and len(content) > 10 and len(content) < 200:
                    text = content.strip()
                    # Skip system messages and hooks
                    if not text.startswith('[') and not text.startswith('<') and not text.startswith('/'):
                        user_requests.append(text[:80])

            # Get assistant tool uses
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
                            elif tool == 'Bash':
                                cmd = tool_input.get('command', '')
                                if 'git commit' in cmd:
                                    key_activities.append('Git commit')
                                elif 'git push' in cmd:
                                    key_activities.append('Git push')
                                elif 'npm' in cmd or 'pip' in cmd:
                                    key_activities.append('Pkg install')
                                elif 'pytest' in cmd or 'npm test' in cmd:
                                    key_activities.append('Tests')
                            elif tool == 'Task':
                                desc = tool_input.get('description', '')
                                if desc:
                                    key_activities.append(f'Agent:{desc[:20]}')

    # Build meaningful summary
    summary_parts = []

    # Add last user request
    if user_requests:
        last_req = user_requests[-1]
        summary_parts.append(f'Task: {last_req}')

    # Add modified files count
    if files_modified:
        flist = list(files_modified)[:5]
        summary_parts.append(f'Files({len(files_modified)}): {chr(44).join(flist)}')

    # Add key activities
    if key_activities:
        unique = list(dict.fromkeys(key_activities))[:3]
        summary_parts.append(f'Actions: {chr(44).join(unique)}')

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

# Build JSON payload - only include last_summarized_message_id if we have a valid ID
if [ -n "$LAST_MSG_ID" ] && [ "$LAST_MSG_ID" != "0" ] && [ "$LAST_MSG_ID" != "None" ]; then
    JSON_PAYLOAD="{\"trigger\": \"session_end\", \"new_insights\": $ESCAPED_SUMMARY, \"last_summarized_message_id\": \"$LAST_MSG_ID\"}"
else
    JSON_PAYLOAD="{\"trigger\": \"session_end\", \"new_insights\": $ESCAPED_SUMMARY}"
fi

# Update project summary
RESPONSE=$(curl -s -X POST "$BACKEND_URL/api/projects/$PROJECT_ID/memory/summary/update" \
    -H "Content-Type: application/json" \
    -d "$JSON_PAYLOAD" \
    --connect-timeout 5 \
    --max-time 10 \
    2>/dev/null)

if [ $? -eq 0 ]; then
    log_message "Summary updated successfully ($MESSAGES_SINCE messages): $SUMMARY"
else
    log_message "Failed to update summary: $RESPONSE"
fi

# Return empty JSON to approve without modification
echo '{}'
