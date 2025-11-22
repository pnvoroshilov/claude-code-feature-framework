#!/bin/bash

# UserPromptSubmit hook - Inject RAG indexing instruction
# Checks for pending RAG indexing marker and triggers re-indexing via API

PROJECT_ROOT="$(pwd)"
LOGDIR="$PROJECT_ROOT/.claude/logs/hooks"
MARKER_FILE="$LOGDIR/.rag-indexing-pending"
LOGFILE="$LOGDIR/user-prompt-$(date +%Y%m%d).log"

# Create log directory
mkdir -p "$LOGDIR" 2>/dev/null

# Log hook execution
echo "[$(date '+%Y-%m-%d %H:%M:%S')] UserPromptSubmit hook triggered (RAG indexing)" >> "$LOGFILE"

# Check if RAG indexing is pending
if [ -f "$MARKER_FILE" ]; then
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] RAG indexing marker found - retrying API call" >> "$LOGFILE"

    # Read file paths from marker file
    FILES_JSON=$(cat "$MARKER_FILE")

    # Remove marker file (one-time trigger)
    rm -f "$MARKER_FILE"

    # Retry API call
    API_URL="http://localhost:3333/api/rag/index-commit-files"

    # URL encode project directory
    PROJECT_DIR_ENCODED=$(printf %s "$PROJECT_ROOT" | jq -sRr @uri)

    echo "[$(date '+%Y-%m-%d %H:%M:%S')] Retrying API call with project: $PROJECT_ROOT" >> "$LOGFILE"
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] Files JSON: $FILES_JSON" >> "$LOGFILE"

    # Make API call
    API_RESPONSE=$(curl -s -X POST "$API_URL?project_dir=${PROJECT_DIR_ENCODED}" \
        -H "Content-Type: application/json" \
        -d "{\"file_paths\": $FILES_JSON}" \
        2>&1)

    API_STATUS=$?

    if [ $API_STATUS -eq 0 ]; then
        echo "[$(date '+%Y-%m-%d %H:%M:%S')] API call successful: $API_RESPONSE" >> "$LOGFILE"

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
        echo "[$(date '+%Y-%m-%d %H:%M:%S')] API call failed again: $API_RESPONSE" >> "$LOGFILE"

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

    echo "[$(date '+%Y-%m-%d %H:%M:%S')] RAG indexing retry completed" >> "$LOGFILE"
else
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] No RAG indexing pending - proceeding normally" >> "$LOGFILE"
    # Return empty JSON to approve without modification
    echo '{}'
fi
