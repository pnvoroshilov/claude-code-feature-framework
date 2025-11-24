#!/bin/bash

# Memory Session Summarizer Hook
# Updates project summary with session insights on Stop event
#
# Hook events: Stop
#
# Input (via stdin): JSON with hook-specific data
# - Stop: { "transcript": [...], "sessionId": "...", "stopHookInput": {...} }

PROJECT_ROOT="$(pwd)"
LOGDIR="$PROJECT_ROOT/.claudetask/logs/hooks"
LOGFILE="$LOGDIR/hooks.log"

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

log_message() {
    local status="$1"
    local message="$2"
    echo "$(date '+%Y-%m-%d %H:%M:%S') | session-summarize | $status | $message" >> "$LOGFILE"
}

# If no project ID, skip with logging
if [ -z "$PROJECT_ID" ]; then
    log_message "SKIPPED" "No project ID found, skipping session summarization"
    echo '{}'
    exit 0
fi

log_message "START" "Analyzing session for summary update"

# Get transcript path from input
TRANSCRIPT_PATH=$(echo "$INPUT" | python3 -c "import json,sys; d=json.load(sys.stdin); print(d.get('transcript_path', ''))" 2>/dev/null)

if [ -z "$TRANSCRIPT_PATH" ] || [ ! -f "$TRANSCRIPT_PATH" ]; then
    log_message "SKIPPED" "No transcript_path or file not found"
    echo '{}'
    exit 0
fi

# Extract session summary from transcript file (JSONL format)
# Look for key activities: file edits, commands run, decisions made
SESSION_SUMMARY=$(python3 -c "
import json

try:
    # Read JSONL file - each line is a separate JSON object
    messages = []
    with open('$TRANSCRIPT_PATH', 'r') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
                if obj.get('type') in ('user', 'assistant'):
                    messages.append(obj)
            except:
                continue

    # Collect key activities
    activities = []
    files_modified = set()
    commands_run = []

    for entry in messages:
        msg = entry.get('message', {})
        content = msg.get('content', '')

        # Handle content as list of blocks (assistant messages)
        if isinstance(content, list):
            for block in content:
                if block.get('type') == 'tool_use':
                    tool = block.get('name', '')
                    tool_input = block.get('input', {})

                    if tool in ['Edit', 'Write', 'MultiEdit']:
                        file_path = tool_input.get('file_path', '')
                        if file_path:
                            files_modified.add(file_path.split('/')[-1])
                    elif tool == 'Bash':
                        cmd = tool_input.get('command', '')[:50]
                        if cmd:
                            commands_run.append(cmd)
                    elif tool == 'Task':
                        desc = tool_input.get('description', '')
                        if desc:
                            activities.append(f'Delegated: {desc}')

    # Build summary
    summary_parts = []

    if files_modified:
        summary_parts.append(f\"Files modified: {', '.join(list(files_modified)[:5])}\")

    if commands_run:
        summary_parts.append(f\"Commands: {len(commands_run)} executed\")

    if activities:
        summary_parts.append(f\"Activities: {'; '.join(activities[:3])}\")

    # Get last user request for context
    for entry in reversed(messages):
        msg = entry.get('message', {})
        if msg.get('role') == 'user':
            user_content = msg.get('content', '')
            if isinstance(user_content, str) and len(user_content) > 10:
                summary_parts.append(f\"Task: {user_content[:100]}...\")
                break

    if summary_parts:
        print(' | '.join(summary_parts))
    else:
        print('Session completed with no significant changes')

except Exception as e:
    pass
" 2>/dev/null)

# Only update if we have a meaningful summary
if [ -n "$SESSION_SUMMARY" ] && [ "$SESSION_SUMMARY" != "Session completed with no significant changes" ]; then
    log_message "INFO" "Summary: $SESSION_SUMMARY"

    # Escape content for JSON
    ESCAPED_SUMMARY=$(echo "$SESSION_SUMMARY" | python3 -c "import json,sys; print(json.dumps(sys.stdin.read()))" 2>/dev/null | sed 's/^"//;s/"$//')

    # Send to backend API to update project summary
    response=$(curl -s -X POST "$BACKEND_URL/api/projects/$PROJECT_ID/memory/summary" \
        -H "Content-Type: application/json" \
        -d "{\"trigger\": \"session_end\", \"new_insights\": \"$ESCAPED_SUMMARY\"}" \
        --connect-timeout 5 \
        --max-time 10 \
        2>/dev/null)

    if [ $? -eq 0 ]; then
        log_message "SUCCESS" "Updated project summary"
    else
        log_message "ERROR" "Failed to update summary: $response"
    fi
else
    log_message "SKIPPED" "No significant activities to summarize"
fi

# Return empty JSON to approve without modification
echo '{}'
