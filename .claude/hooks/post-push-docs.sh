#!/bin/bash

# Post-push documentation update hook
# Triggers /update-documentation after successful push to main/master
#
# This hook calls the backend API to execute the command in a Claude terminal session.

# Source hook logger for proper logging based on storage_mode
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
if [ -f "$SCRIPT_DIR/hook-logger.sh" ]; then
    source "$SCRIPT_DIR/hook-logger.sh"
    init_hook_log "post-push-docs"
else
    # Fallback if hook-logger not available
    log_hook() { echo "$1" >&2; }
    log_hook_success() { echo "$1" >&2; }
    log_hook_error() { echo "$1" >&2; }
    log_hook_skip() { echo "$1" >&2; }
fi

PROJECT_ROOT="$(pwd)"
LOCKFILE="$PROJECT_ROOT/.claudetask/logs/hooks/.hook-running"
BACKEND_URL="${CLAUDETASK_BACKEND_URL:-http://localhost:3333}"

# Read JSON input from stdin
HOOK_INPUT=$(cat)

# Extract command from tool_input using jq
if ! command -v jq &> /dev/null; then
    log_hook_skip "jq not available"
    exit 0
fi

BASH_CMD=$(echo "$HOOK_INPUT" | jq -r '.tool_input.command // .command // .parameters.command // empty' 2>/dev/null)
log_hook "Command: $BASH_CMD"

# Check for lock file (recursion prevention)
if [ -f "$LOCKFILE" ]; then
    log_hook_skip "Hook already running, preventing recursion"
    exit 0
fi

# Check if this is a git push/merge/pull command
# Use flexible regex to match git commands with flags (e.g., git -C /path push)
if ! echo "$BASH_CMD" | grep -qE '\bgit\b.*(push|pull|merge)|\bgh\s+pr\s+merge\b'; then
    log_hook_skip "Not a merge/push/pull command"
    exit 0
fi

CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo 'unknown')
log_hook "Git command detected. Branch: $CURRENT_BRANCH"

# Only trigger on main/master branch
if [ "$CURRENT_BRANCH" != "main" ] && [ "$CURRENT_BRANCH" != "master" ]; then
    log_hook_skip "Not on main/master branch"
    exit 0
fi

# Check for [skip-hook] tag in commit title
COMMIT_FIRST_LINE=$(git log -1 --pretty=%s 2>/dev/null)
if echo "$COMMIT_FIRST_LINE" | grep -q '\[skip-hook\]'; then
    log_hook_skip "[skip-hook] tag detected in commit title"
    exit 0
fi

# Create lock file
mkdir -p "$(dirname "$LOCKFILE")"
touch "$LOCKFILE"

log_hook "Main branch update detected - triggering /update-documentation"

# Call backend API to execute /update-documentation command
API_URL="$BACKEND_URL/api/claude-sessions/execute-command"
COMMAND="/update-documentation"

# URL encode project directory (handle spaces and special characters)
PROJECT_DIR_ENCODED=$(printf '%s' "$PROJECT_ROOT" | jq -sRr @uri)

log_hook "Calling API: $API_URL"

# Make API call (30s timeout needed - backend waits 15s for Claude MCP initialization)
API_RESPONSE=$(curl -s --max-time 30 -X POST "$API_URL?command=${COMMAND}&project_dir=${PROJECT_DIR_ENCODED}" \
    -H "Content-Type: application/json" 2>&1)

API_STATUS=$?

# Remove lock file
rm -f "$LOCKFILE"

if [ $API_STATUS -eq 0 ] && echo "$API_RESPONSE" | jq -e '.success == true' > /dev/null 2>&1; then
    SESSION_ID=$(echo "$API_RESPONSE" | jq -r '.session_id // "unknown"')
    log_hook_success "Command sent to Claude session $SESSION_ID"

    # Output success message to stderr (visible in Claude Code)
    cat << EOF >&2

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ AUTOMATIC DOCUMENTATION UPDATE TRIGGERED
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📚 Main branch updated - documentation sync initiated
🤖 Command: $COMMAND
🔗 Session: $SESSION_ID
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
EOF
else
    ERROR_MSG="API call failed (status=$API_STATUS): $API_RESPONSE"
    log_hook_error "$ERROR_MSG"

    cat << EOF >&2

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
❌ DOCUMENTATION UPDATE FAILED
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Run manually: /update-documentation
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
EOF
fi
