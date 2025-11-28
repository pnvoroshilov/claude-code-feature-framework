#!/bin/bash

# Memory Conversation Capture Hook (with Summarization)
# Saves user messages and assistant responses to project memory via backend API
# Also triggers intelligent summarization when 30+ messages accumulated
#
# Hook events: UserPromptSubmit, Stop
#
# Input (via stdin): JSON with hook-specific data
# - UserPromptSubmit: { "userPrompt": "...", "sessionId": "..." }
# - Stop: { "transcript": [...], "sessionId": "..." }

# Read input from stdin FIRST (before sourcing logger which might read stdin)
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
    init_hook_log "memory-capture"
else
    # Fallback if hook-logger not available
    log_hook() { echo "[$(date '+%Y-%m-%d %H:%M:%S')] memory-capture | INFO | $1" >&2; }
    log_hook_success() { echo "[$(date '+%Y-%m-%d %H:%M:%S')] memory-capture | SUCCESS | $1" >&2; }
    log_hook_error() { echo "[$(date '+%Y-%m-%d %H:%M:%S')] memory-capture | ERROR | $1" >&2; }
    log_hook_skip() { echo "[$(date '+%Y-%m-%d %H:%M:%S')] memory-capture | SKIPPED | $1" >&2; }
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

# ============================================================
# SAVE MESSAGE FUNCTION
# ============================================================
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

# ============================================================
# SUMMARIZATION FUNCTION (triggered on Stop if threshold reached)
# ============================================================
check_and_trigger_summarization() {
    # Check if summarization is needed (threshold = 30 messages)
    SHOULD_SUMMARIZE=$(curl -s "$BACKEND_URL/api/projects/$PROJECT_ID/memory/should-summarize?threshold=30" 2>/dev/null)

    if [ -z "$SHOULD_SUMMARIZE" ]; then
        log_hook_skip "Summarization check failed - backend not available"
        return
    fi

    NEED_SUMMARY=$(echo "$SHOULD_SUMMARIZE" | python3 -c "import json,sys; d=json.load(sys.stdin); print('true' if d.get('should_summarize') else 'false')" 2>/dev/null)
    MESSAGES_SINCE=$(echo "$SHOULD_SUMMARIZE" | python3 -c "import json,sys; d=json.load(sys.stdin); print(d.get('messages_since_last_summary', 0))" 2>/dev/null)

    if [ "$NEED_SUMMARY" != "true" ]; then
        log_hook_skip "Summarization not needed ($MESSAGES_SINCE messages, threshold: 30)"
        return
    fi

    log_hook "Triggering summarization - $MESSAGES_SINCE messages since last summary"

    # Check throttle file to prevent too frequent summarization attempts
    THROTTLE_FILE="/tmp/claudetask_summarize_throttle_$PROJECT_ID"
    if [ -f "$THROTTLE_FILE" ]; then
        LAST_ATTEMPT=$(cat "$THROTTLE_FILE" 2>/dev/null)
        NOW=$(date +%s)
        # Throttle: at least 5 minutes between attempts
        if [ -n "$LAST_ATTEMPT" ] && [ $((NOW - LAST_ATTEMPT)) -lt 300 ]; then
            log_hook_skip "Summarization throttled - last attempt was $((NOW - LAST_ATTEMPT))s ago (min: 300s)"
            return
        fi
    fi
    # Update throttle timestamp
    date +%s > "$THROTTLE_FILE"

    # Get latest message ID for potential counter reset
    LATEST_MSG=$(curl -s "$BACKEND_URL/api/projects/$PROJECT_ID/memory/messages?limit=1" 2>/dev/null)
    LATEST_MSG_ID=$(echo "$LATEST_MSG" | python3 -c "import json,sys; d=json.load(sys.stdin); msgs=d.get('messages',[]); print(msgs[0].get('id','') if msgs else '')" 2>/dev/null)

    # URL encode project directory (handle spaces and special characters)
    PROJECT_DIR_ENCODED=$(printf '%s' "$PROJECT_ROOT" | jq -sRr @uri)

    # Call execute-command API to trigger /summarize-project
    API_URL="$BACKEND_URL/api/claude-sessions/execute-command?command=/summarize-project&project_dir=${PROJECT_DIR_ENCODED}"

    log_hook "Calling /summarize-project via Claude Code"

    # Make API call with longer timeout (20s for MCP initialization + processing)
    API_RESPONSE=$(curl -s --max-time 25 -X POST "$API_URL" \
        -H "Content-Type: application/json" \
        2>&1)

    API_STATUS=$?

    if [ $API_STATUS -eq 0 ]; then
        SUCCESS=$(echo "$API_RESPONSE" | python3 -c "import json,sys; d=json.load(sys.stdin); print('true' if d.get('success') else 'false')" 2>/dev/null)
        SESSION_ID=$(echo "$API_RESPONSE" | python3 -c "import json,sys; d=json.load(sys.stdin); print(d.get('session_id', 'unknown'))" 2>/dev/null)

        if [ "$SUCCESS" = "true" ]; then
            log_hook_success "Summarization triggered (session: $SESSION_ID)"
            # Reset counter ONLY on success
            if [ -n "$LATEST_MSG_ID" ] && [ "$LATEST_MSG_ID" != "" ]; then
                curl -s -X POST "$BACKEND_URL/api/projects/$PROJECT_ID/memory/summary/reset-counter?last_summarized_message_id=$LATEST_MSG_ID" \
                    --connect-timeout 3 \
                    --max-time 5 \
                    2>/dev/null > /dev/null
                log_hook "Reset message counter to ID: $LATEST_MSG_ID"
            fi
        else
            log_hook_error "Failed to trigger summarization: $API_RESPONSE"
        fi
    elif [ $API_STATUS -eq 28 ]; then
        # Timeout - assume it started in background
        log_hook_success "Summarization started (running in background)"
        # Reset counter on timeout too (command was sent)
        if [ -n "$LATEST_MSG_ID" ] && [ "$LATEST_MSG_ID" != "" ]; then
            curl -s -X POST "$BACKEND_URL/api/projects/$PROJECT_ID/memory/summary/reset-counter?last_summarized_message_id=$LATEST_MSG_ID" \
                --connect-timeout 3 \
                --max-time 5 \
                2>/dev/null > /dev/null
            log_hook "Reset message counter to ID: $LATEST_MSG_ID"
        fi
    else
        log_hook_error "Summarization API failed with status: $API_STATUS"
        # Do NOT reset counter on failure - will retry on next Stop event
    fi
}

# ============================================================
# MAIN LOGIC
# ============================================================
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
        # Stop event - save assistant's last response + check summarization
        TRANSCRIPT_PATH=$(echo "$INPUT" | python3 -c "import json,sys; d=json.load(sys.stdin); print(d.get('transcript_path', ''))" 2>/dev/null)
        SESSION_ID=$(echo "$INPUT" | python3 -c "import json,sys; d=json.load(sys.stdin); print(d.get('session_id', d.get('sessionId', '')))" 2>/dev/null)

        if [ -z "$TRANSCRIPT_PATH" ] || [ ! -f "$TRANSCRIPT_PATH" ]; then
            log_hook_skip "Stop hook - no transcript_path or file not found"
            echo '{}'
            exit 0
        fi

        # Extract meaningful assistant text messages from transcript file (JSONL format)
        # Filters out tool summaries and collects substantive responses
        LAST_ASSISTANT=$(python3 -c "
import json
import re

# Patterns to filter out (tool summaries, not real conversation)
SKIP_PATTERNS = [
    r'^Edited\s+/',           # Edit tool summaries
    r'^Wrote\s+(file\s+)?/',  # Write tool summaries
    r'^Read\s+/',             # Read tool summaries (rarely useful)
    r'^Created\s+/',          # Create summaries
    r'^Deleted\s+/',          # Delete summaries
    r'^Ran\s+command',        # Bash summaries
    r'^Found\s+\d+\s+files',  # Glob summaries
    r'^Grep\s+results',       # Grep summaries
    r'^<system-',             # System messages
]

def is_meaningful(text):
    '''Check if text is meaningful conversation vs tool output'''
    if not text or len(text) < 20:
        return False
    for pattern in SKIP_PATTERNS:
        if re.match(pattern, text, re.IGNORECASE):
            return False
    # Skip if it's just a file path
    if text.startswith('/') and '\n' not in text and len(text) < 200:
        return False
    return True

try:
    all_texts = []
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
                        content = msg.get('content', '')
                        if isinstance(content, list):
                            for c in content:
                                if c.get('type') == 'text':
                                    text = c.get('text', '').strip()
                                    if is_meaningful(text):
                                        all_texts.append(text)
                        elif isinstance(content, str):
                            text = content.strip()
                            if is_meaningful(text):
                                all_texts.append(text)
            except:
                continue

    if all_texts:
        # Join meaningful texts, limit to 4000 chars
        result = '\n---\n'.join(all_texts)
        print(result[:4000])
except Exception as e:
    pass
" 2>/dev/null)

        if [ -n "$LAST_ASSISTANT" ]; then
            log_hook "Stop hook - saving assistant response (session: ${SESSION_ID:-unknown})"
            save_message "assistant" "$LAST_ASSISTANT" "$SESSION_ID"
        else
            log_hook_skip "Stop hook - no assistant message found in transcript"
        fi

        # After saving message, check if summarization is needed
        check_and_trigger_summarization
        ;;

    *)
        log_hook_skip "Unknown hook type, input: ${INPUT:0:200}"
        ;;
esac

# Return empty JSON to approve without modification
echo '{}'
