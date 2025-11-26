#!/bin/bash

# Memory File Edit Capture Hook
# Saves information about file edits/writes to project memory via backend API
#
# Hook event: PostToolUse (Edit, Write, MultiEdit, Update)
#
# Input (via stdin): JSON with tool result data
# - tool_name: name of the tool used
# - tool_input: input parameters to the tool
# - tool_result: result from the tool

PROJECT_ROOT="$(pwd)"
LOGDIR="$PROJECT_ROOT/.claudetask/logs/hooks"
LOGFILE="$LOGDIR/hooks.log"

# Create log directory
mkdir -p "$LOGDIR" 2>/dev/null

# Read input from stdin
INPUT=$(cat)

# Debug: log raw input
echo "$(date '+%Y-%m-%d %H:%M:%S') | memory-file-edit | DEBUG | Raw input: ${INPUT:0:500}" >> "$LOGFILE"

# Get backend URL (default to localhost)
BACKEND_URL="${CLAUDETASK_BACKEND_URL:-http://localhost:3333}"

# Get project ID from .mcp.json (check both framework root and current project)
MCP_JSON=""
if [ -f "$PROJECT_ROOT/.mcp.json" ]; then
    MCP_JSON="$PROJECT_ROOT/.mcp.json"
fi

if [ -n "$MCP_JSON" ]; then
    PROJECT_ID=$(python3 -c "import json; data=json.load(open('$MCP_JSON')); print(data.get('mcpServers', {}).get('claudetask', {}).get('env', {}).get('CLAUDETASK_PROJECT_ID', ''))" 2>/dev/null)
fi

# Fallback: try to get from environment
if [ -z "$PROJECT_ID" ]; then
    PROJECT_ID="${CLAUDETASK_PROJECT_ID:-}"
fi

# If no project ID, skip with logging
if [ -z "$PROJECT_ID" ]; then
    echo "$(date '+%Y-%m-%d %H:%M:%S') | memory-file-edit | SKIPPED | No project ID found, skipping memory capture" >> "$LOGFILE"
    echo '{}'
    exit 0
fi

log_message() {
    local status="$1"
    local message="$2"
    echo "$(date '+%Y-%m-%d %H:%M:%S') | memory-file-edit | $status | $message" >> "$LOGFILE"
}

# Extract tool info and create memory entry
MEMORY_CONTENT=$(echo "$INPUT" | python3 -c "
import json
import sys

try:
    d = json.load(sys.stdin)
    tool_name = d.get('tool_name', '')
    tool_input = d.get('tool_input', {})
    tool_result = d.get('tool_result', '')
    session_id = d.get('session_id', '')

    # Only process Edit, Write, MultiEdit, Update tools
    if tool_name not in ['Edit', 'Write', 'MultiEdit', 'Update']:
        print('')
        sys.exit(0)

    # Extract file path
    file_path = tool_input.get('file_path', 'unknown')

    # Create meaningful summary based on tool type
    if tool_name == 'Edit':
        old_str = tool_input.get('old_string', '')[:100]
        new_str = tool_input.get('new_string', '')[:100]
        summary = f'Edited {file_path}: replaced \"{old_str}...\" with \"{new_str}...\"'
    elif tool_name == 'Write':
        content_preview = tool_input.get('content', '')[:200]
        summary = f'Wrote file {file_path}: {content_preview}...'
    elif tool_name == 'MultiEdit':
        edits = tool_input.get('edits', [])
        summary = f'Multi-edited {file_path}: {len(edits)} changes'
    elif tool_name == 'Update':
        old_str = tool_input.get('old_string', '')[:100]
        new_str = tool_input.get('new_string', '')[:100]
        summary = f'Updated {file_path}: replaced \"{old_str}...\" with \"{new_str}...\"'
    else:
        summary = f'{tool_name} on {file_path}'

    # Output JSON for saving
    output = {
        'content': summary,
        'file_path': file_path,
        'tool_name': tool_name,
        'session_id': session_id
    }
    print(json.dumps(output))

except Exception as e:
    print('')
" 2>/dev/null)

# If no content extracted, skip
if [ -z "$MEMORY_CONTENT" ] || [ "$MEMORY_CONTENT" = "" ]; then
    log_message "SKIPPED" "Not a file edit tool or failed to extract info"
    echo '{}'
    exit 0
fi

# Parse extracted info
CONTENT=$(echo "$MEMORY_CONTENT" | python3 -c "import json,sys; d=json.load(sys.stdin); print(d.get('content', ''))" 2>/dev/null)
FILE_PATH=$(echo "$MEMORY_CONTENT" | python3 -c "import json,sys; d=json.load(sys.stdin); print(d.get('file_path', ''))" 2>/dev/null)
TOOL_NAME=$(echo "$MEMORY_CONTENT" | python3 -c "import json,sys; d=json.load(sys.stdin); print(d.get('tool_name', ''))" 2>/dev/null)
SESSION_ID=$(echo "$MEMORY_CONTENT" | python3 -c "import json,sys; d=json.load(sys.stdin); print(d.get('session_id', ''))" 2>/dev/null)

if [ -z "$CONTENT" ]; then
    log_message "SKIPPED" "Empty content extracted"
    echo '{}'
    exit 0
fi

# Escape content for JSON
ESCAPED_CONTENT=$(echo "$CONTENT" | python3 -c "import json,sys; print(json.dumps(sys.stdin.read()))" 2>/dev/null | sed 's/^"//;s/"$//')

# Build JSON payload with metadata
PAYLOAD="{\"message_type\": \"assistant\", \"content\": \"$ESCAPED_CONTENT\", \"metadata\": {\"event_type\": \"file_edit\", \"tool_name\": \"$TOOL_NAME\", \"file_path\": \"$FILE_PATH\"}"
if [ -n "$SESSION_ID" ]; then
    PAYLOAD="$PAYLOAD, \"session_id\": \"$SESSION_ID\""
fi
PAYLOAD="$PAYLOAD}"

# Send to backend API
log_message "START" "Saving file edit to memory: $TOOL_NAME on $FILE_PATH"

response=$(curl -s -X POST "$BACKEND_URL/api/projects/$PROJECT_ID/memory/messages" \
    -H "Content-Type: application/json" \
    -d "$PAYLOAD" \
    --connect-timeout 5 \
    --max-time 10 \
    2>/dev/null)

if [ $? -eq 0 ]; then
    log_message "SUCCESS" "Saved file edit to memory: $TOOL_NAME on $FILE_PATH"
else
    log_message "ERROR" "Failed to save file edit: $response"
fi

# Return empty JSON to approve without modification
echo '{}'
