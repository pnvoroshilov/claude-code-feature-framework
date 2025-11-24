#!/bin/bash

# Memory Conversation Capture Hook
# Saves user messages and assistant responses to project memory via backend API
#
# Hook events: UserPromptSubmit, Stop
#
# Input (via stdin): JSON with hook-specific data
# - UserPromptSubmit: { "userPrompt": "...", "sessionId": "..." }
# - Stop: { "transcript": [...], "sessionId": "..." }

PROJECT_ROOT="$(pwd)"
LOGDIR="$PROJECT_ROOT/.claude/logs/hooks"
LOGFILE="$LOGDIR/memory-capture-$(date +%Y%m%d).log"

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
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] No project ID found, skipping memory capture" >> "$LOGFILE"
    echo '{}'
    exit 0
fi

# Determine hook type from input
HOOK_TYPE=$(echo "$INPUT" | python3 -c "import json,sys; d=json.load(sys.stdin); print('user' if 'userPrompt' in d else 'stop' if 'transcript' in d else 'unknown')" 2>/dev/null)

log_message() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" >> "$LOGFILE"
}

save_message() {
    local msg_type="$1"
    local content="$2"

    # Escape content for JSON
    local escaped_content=$(echo "$content" | python3 -c "import json,sys; print(json.dumps(sys.stdin.read()))" 2>/dev/null | sed 's/^"//;s/"$//')

    # Send to backend API
    response=$(curl -s -X POST "$BACKEND_URL/api/projects/$PROJECT_ID/memory/messages" \
        -H "Content-Type: application/json" \
        -d "{\"message_type\": \"$msg_type\", \"content\": \"$escaped_content\"}" \
        --connect-timeout 5 \
        --max-time 10 \
        2>/dev/null)

    if [ $? -eq 0 ]; then
        log_message "Saved $msg_type message to memory"
    else
        log_message "Failed to save $msg_type message: $response"
    fi
}

case "$HOOK_TYPE" in
    "user")
        # UserPromptSubmit - save user message
        USER_PROMPT=$(echo "$INPUT" | python3 -c "import json,sys; d=json.load(sys.stdin); print(d.get('userPrompt', ''))" 2>/dev/null)

        if [ -n "$USER_PROMPT" ]; then
            log_message "UserPromptSubmit hook - saving user message"
            save_message "user" "$USER_PROMPT"
        fi
        ;;

    "stop")
        # Stop event - save assistant's last response
        # Extract last assistant message from transcript
        LAST_ASSISTANT=$(echo "$INPUT" | python3 -c "
import json, sys
d = json.load(sys.stdin)
transcript = d.get('transcript', [])
# Find last assistant message
for msg in reversed(transcript):
    if msg.get('role') == 'assistant':
        content = msg.get('content', '')
        if isinstance(content, list):
            # Content is array of content blocks
            texts = [c.get('text', '') for c in content if c.get('type') == 'text']
            print(' '.join(texts)[:2000])  # Limit to 2000 chars
        else:
            print(str(content)[:2000])
        break
" 2>/dev/null)

        if [ -n "$LAST_ASSISTANT" ]; then
            log_message "Stop hook - saving assistant response"
            save_message "assistant" "$LAST_ASSISTANT"
        fi
        ;;

    *)
        log_message "Unknown hook type, input: ${INPUT:0:200}"
        ;;
esac

# Return empty JSON to approve without modification
echo '{}'
