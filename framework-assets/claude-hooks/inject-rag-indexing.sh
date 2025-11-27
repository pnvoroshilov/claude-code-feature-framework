#!/bin/bash

# UserPromptSubmit hook - Inject RAG indexing instruction
# Checks for pending RAG indexing marker and triggers re-indexing via API

# Read input from stdin first
INPUT=$(cat)

PROJECT_ROOT="$(pwd)"
LOGDIR="$PROJECT_ROOT/.claude/logs/hooks"
MARKER_FILE="$LOGDIR/.rag-indexing-pending"

# Source hook logger for proper logging based on storage_mode
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
if [ -f "$SCRIPT_DIR/hook-logger.sh" ]; then
    source "$SCRIPT_DIR/hook-logger.sh"
    init_hook_log "inject-rag-indexing"
else
    # Fallback if hook-logger not available
    log_hook() { echo "[$(date '+%Y-%m-%d %H:%M:%S')] inject-rag-indexing | INFO | $1" >&2; }
    log_hook_success() { echo "[$(date '+%Y-%m-%d %H:%M:%S')] inject-rag-indexing | SUCCESS | $1" >&2; }
    log_hook_error() { echo "[$(date '+%Y-%m-%d %H:%M:%S')] inject-rag-indexing | ERROR | $1" >&2; }
    log_hook_skip() { echo "[$(date '+%Y-%m-%d %H:%M:%S')] inject-rag-indexing | SKIPPED | $1" >&2; }
fi

log_hook "UserPromptSubmit hook triggered (RAG indexing check)"

# Check if RAG indexing is pending
if [ -f "$MARKER_FILE" ]; then
    log_hook "RAG indexing marker found - retrying API call"

    # Read file paths from marker file
    FILES_JSON=$(cat "$MARKER_FILE")

    # Remove marker file (one-time trigger)
    rm -f "$MARKER_FILE"

    # Retry API call
    API_URL="http://localhost:3333/api/rag/index-commit-files"

    # URL encode project directory
    PROJECT_DIR_ENCODED=$(printf %s "$PROJECT_ROOT" | jq -sRr @uri)

    log_hook "Retrying API call with project: $PROJECT_ROOT"

    # Make API call
    API_RESPONSE=$(curl -s -X POST "$API_URL?project_dir=${PROJECT_DIR_ENCODED}" \
        -H "Content-Type: application/json" \
        -d "{\"file_paths\": $FILES_JSON}" \
        2>&1)

    API_STATUS=$?

    if [ $API_STATUS -eq 0 ]; then
        log_hook_success "API call successful: $API_RESPONSE"

        # Output notification as additional context
        cat << 'EOF'
{
  "hookSpecificOutput": {
    "hookEventName": "UserPromptSubmit",
    "additionalContext": "\n\n✅ RAG INDEXING COMPLETED\n\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n🔍 Changed files from your recent commit have been indexed for semantic search.\n\nThe RAG database is now up-to-date with the latest changes.\n\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
  }
}
EOF
    else
        log_hook_error "API call failed again: $API_RESPONSE"

        # Recreate marker file for next attempt
        echo "$FILES_JSON" > "$MARKER_FILE"

        # Notify about failure
        cat << 'EOF'
{
  "hookSpecificOutput": {
    "hookEventName": "UserPromptSubmit",
    "additionalContext": "\n\n⚠️  RAG INDEXING FAILED\n\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n⚠️  Automatic RAG indexing failed. Backend API may not be running.\n\nYou can manually trigger indexing later using MCP tools:\nmcp__claudetask__index_files\n\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
  }
}
EOF
    fi
else
    log_hook_skip "No RAG indexing pending - proceeding normally"
    # Return empty JSON to approve without modification
    echo '{}'
fi
