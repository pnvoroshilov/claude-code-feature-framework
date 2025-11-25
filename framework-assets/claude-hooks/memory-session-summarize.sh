#!/bin/bash

# Memory Session Summarizer Hook
# Checks if summarization is needed (every 30 messages) and updates project summary
#
# Hook event: Stop
#
# Input (via stdin): JSON with Stop event data including transcript

PROJECT_ROOT="$(pwd)"
LOGDIR="$PROJECT_ROOT/.claude/logs/hooks"
LOGFILE="$LOGDIR/memory-summarize-$(date +%Y%m%d).log"

# Create log directory
mkdir -p "$LOGDIR" 2>/dev/null

# Read input from stdin
INPUT=$(cat)

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

# Extract summary from transcript
# Look for: files modified, commands run, tasks completed, key decisions
SUMMARY=$(echo "$INPUT" | python3 -c "
import json
import sys
import re

try:
    data = json.load(sys.stdin)
    transcript = data.get('transcript', [])

    files_modified = set()
    commands_run = []
    key_activities = []

    for msg in transcript:
        content = msg.get('content', '')
        if isinstance(content, list):
            for block in content:
                if isinstance(block, dict):
                    if block.get('type') == 'tool_use':
                        tool = block.get('name', '')
                        tool_input = block.get('input', {})

                        if tool in ['Edit', 'Write', 'MultiEdit']:
                            file_path = tool_input.get('file_path', '')
                            if file_path:
                                files_modified.add(file_path.split('/')[-1])
                        elif tool == 'Bash':
                            cmd = tool_input.get('command', '')[:50]
                            if 'git commit' in cmd or 'git push' in cmd:
                                key_activities.append('Git commit/push')
                        elif tool == 'Task':
                            desc = tool_input.get('description', '')
                            if desc:
                                key_activities.append(f'Delegated: {desc[:30]}')
                    elif block.get('type') == 'text':
                        text = block.get('text', '')
                        if 'completed' in text.lower() and len(text) < 200:
                            key_activities.append('Task completed')

    # Build summary
    summary_parts = []

    if files_modified:
        summary_parts.append(f\"Files: {', '.join(list(files_modified)[:8])}\")

    if key_activities:
        unique_activities = list(dict.fromkeys(key_activities))[:4]
        summary_parts.append(f\"Activities: {'; '.join(unique_activities)}\")

    if summary_parts:
        print(' | '.join(summary_parts))
    else:
        print('Session work completed')

except Exception as e:
    print(f'Session summary')
" 2>/dev/null)

if [ -z "$SUMMARY" ]; then
    SUMMARY="Session work completed"
fi

# Get last message ID for tracking
LAST_MSG_ID=$(curl -s "$BACKEND_URL/api/projects/$PROJECT_ID/memory/messages?limit=1" 2>/dev/null | python3 -c "import json,sys; msgs=json.load(sys.stdin); print(msgs[0]['id'] if msgs else 0)" 2>/dev/null)

if [ -z "$LAST_MSG_ID" ] || [ "$LAST_MSG_ID" = "0" ]; then
    LAST_MSG_ID=0
fi

# Escape summary for JSON
ESCAPED_SUMMARY=$(echo "$SUMMARY" | python3 -c "import json,sys; print(json.dumps(sys.stdin.read().strip()))" 2>/dev/null)

# Update project summary
RESPONSE=$(curl -s -X POST "$BACKEND_URL/api/projects/$PROJECT_ID/memory/summary/update" \
    -H "Content-Type: application/json" \
    -d "{\"trigger\": \"auto_summarize_30\", \"new_insights\": $ESCAPED_SUMMARY, \"last_summarized_message_id\": $LAST_MSG_ID}" \
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
