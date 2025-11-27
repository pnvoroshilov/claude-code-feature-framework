#!/bin/bash

# Memory Conversation Capture Hook
# Saves user messages and assistant responses to project memory via backend API
#
# Hook events: UserPromptSubmit, Stop
#
# Input (via stdin): JSON with hook-specific data
# - UserPromptSubmit: { "userPrompt": "...", "sessionId": "..." }
# - Stop: { "transcript": [...], "sessionId": "..." }

# Source hook logger for proper logging based on storage_mode
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
if [ -f "$SCRIPT_DIR/hook-logger.sh" ]; then
    source "$SCRIPT_DIR/hook-logger.sh"
    init_hook_log "memory-capture"
else
    # Fallback if hook-logger not available
    log_hook() { echo "[$(date '+%Y-%m-%d %H:%M:%S')] memory-capture | INFO | $1" >&2; }
    log_hook_success() { echo "[$(date '+%Y-%m-%d %H:%M:%S')] memory-capture | SUCCESS | $1" >&2; }
    log_hook_error() { echo "[$(date '+%Y-%m-%d %H:%M:%S')] memory-capture | ERROR | $1" >&2; }
    log_hook_skip() { echo "[$(date '+%Y-%m-%d %H:%M:%S')] memory-capture | SKIPPED | $1" >&2; }
fi

PROJECT_ROOT="$(pwd)"

# Read input from stdin
INPUT=$(cat)

# Debug: log raw input (truncated)
log_hook "Raw input: ${INPUT:0:300}"

# Get backend URL (default to localhost)
BACKEND_URL="${CLAUDETASK_BACKEND_URL:-http://localhost:3333}"

# Get project ID from .mcp.json
get_project_id() {
    local mcp_json=""
    local current_dir="$PROJECT_ROOT"

    # Walk up to find .mcp.json
    while [ "$current_dir" != "/" ]; do
        if [ -f "$current_dir/.mcp.json" ]; then
            mcp_json="$current_dir/.mcp.json"
            break
        fi
        current_dir="$(dirname "$current_dir")"
    done

    if [ -n "$mcp_json" ]; then
        python3 -c "import json; data=json.load(open('$mcp_json')); print(data.get('mcpServers', {}).get('claudetask', {}).get('env', {}).get('CLAUDETASK_PROJECT_ID', ''))" 2>/dev/null
    fi
}

PROJECT_ID=$(get_project_id)

# Fallback: try to get from environment
if [ -z "$PROJECT_ID" ]; then
    PROJECT_ID="${CLAUDETASK_PROJECT_ID:-}"
fi

# If no project ID, skip with logging
if [ -z "$PROJECT_ID" ]; then
    log_hook_skip "No project ID found, skipping memory capture"
    echo '{}'
    exit 0
fi

# Determine hook type from input
HOOK_TYPE=$(echo "$INPUT" | python3 -c "
import json, sys
d = json.load(sys.stdin)
event_name = d.get('hook_event_name', '')
if event_name == 'UserPromptSubmit' or 'prompt' in d or 'userPrompt' in d:
    print('user')
elif event_name == 'Stop' or 'transcript_path' in d:
    print('stop')
else:
    print('unknown')
" 2>/dev/null)

save_message() {
    local msg_type="$1"
    local content="$2"
    local session_id="$3"

    # Escape content for JSON
    local escaped_content=$(echo "$content" | python3 -c "import json,sys; print(json.dumps(sys.stdin.read()))" 2>/dev/null | sed 's/^"//;s/"$//')

    # Build JSON payload with optional session_id
    local payload="{\"message_type\": \"$msg_type\", \"content\": \"$escaped_content\""
    if [ -n "$session_id" ]; then
        payload="$payload, \"session_id\": \"$session_id\""
    fi
    payload="$payload}"

    # Send to backend API
    response=$(curl -s -X POST "$BACKEND_URL/api/projects/$PROJECT_ID/memory/messages" \
        -H "Content-Type: application/json" \
        -d "$payload" \
        --connect-timeout 5 \
        --max-time 10 \
        2>/dev/null)

    if [ $? -eq 0 ]; then
        log_hook_success "Saved $msg_type message to memory (session: ${session_id:-none})"
    else
        log_hook_error "Failed to save $msg_type message: $response"
    fi
}

case "$HOOK_TYPE" in
    "user")
        # UserPromptSubmit - save user message
        USER_PROMPT=$(echo "$INPUT" | python3 -c "import json,sys; d=json.load(sys.stdin); print(d.get('prompt', d.get('userPrompt', '')))" 2>/dev/null)
        SESSION_ID=$(echo "$INPUT" | python3 -c "import json,sys; d=json.load(sys.stdin); print(d.get('session_id', d.get('sessionId', '')))" 2>/dev/null)

        if [ -n "$USER_PROMPT" ]; then
            log_hook "UserPromptSubmit - saving user message (session: ${SESSION_ID:-unknown})"
            save_message "user" "$USER_PROMPT" "$SESSION_ID"
        else
            log_hook_skip "UserPromptSubmit - empty prompt"
        fi
        ;;

    "stop")
        # Stop event - save assistant's last response
        TRANSCRIPT_PATH=$(echo "$INPUT" | python3 -c "import json,sys; d=json.load(sys.stdin); print(d.get('transcript_path', ''))" 2>/dev/null)
        SESSION_ID=$(echo "$INPUT" | python3 -c "import json,sys; d=json.load(sys.stdin); print(d.get('session_id', d.get('sessionId', '')))" 2>/dev/null)

        if [ -z "$TRANSCRIPT_PATH" ] || [ ! -f "$TRANSCRIPT_PATH" ]; then
            log_hook_skip "Stop hook - no transcript_path or file not found"
            echo '{}'
            exit 0
        fi

        # Extract last assistant message from transcript file (JSONL format)
        LAST_ASSISTANT=$(python3 -c "
import json

try:
    messages = []
    with open('$TRANSCRIPT_PATH', 'r') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
                if obj.get('type') == 'assistant':
                    msg = obj.get('message', {})
                    if msg.get('role') == 'assistant':
                        messages.append(msg)
            except:
                continue

    if messages:
        msg = messages[-1]
        content = msg.get('content', '')
        if isinstance(content, list):
            texts = [c.get('text', '') for c in content if c.get('type') == 'text']
            result = ' '.join(texts)[:2000]
            if result:
                print(result)
        elif isinstance(content, str):
            print(content[:2000])
except Exception as e:
    pass
" 2>/dev/null)

        if [ -n "$LAST_ASSISTANT" ]; then
            log_hook "Stop hook - saving assistant response (session: ${SESSION_ID:-unknown})"
            save_message "assistant" "$LAST_ASSISTANT" "$SESSION_ID"
        else
            log_hook_skip "Stop hook - no assistant message found in transcript"
        fi
        ;;

    *)
        log_hook_skip "Unknown hook type, input: ${INPUT:0:200}"
        ;;
esac

# Return empty JSON to approve without modification
echo '{}'
