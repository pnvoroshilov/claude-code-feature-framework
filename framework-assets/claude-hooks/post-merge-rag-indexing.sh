#!/bin/bash

# Post-merge RAG indexing hook
# Triggers RAG indexing for changed files after successful push/merge to main/master

# Use absolute path for logs to ensure they're created
PROJECT_ROOT="$(pwd)"
LOGDIR="$PROJECT_ROOT/.claude/logs/hooks"
LOGFILE="$LOGDIR/post-merge-rag-$(date +%Y%m%d).log"
LOCKFILE="$LOGDIR/.rag-indexing-running"

# Create log directory
mkdir -p "$LOGDIR" 2>/dev/null

# Read JSON input from stdin
HOOK_INPUT=$(cat)

# Debug output to stderr (visible in Claude Code)
echo "🔍 RAG Indexing Hook triggered at $(date '+%H:%M:%S')" >&2

# Log raw input for debugging - FORCE WRITE
{
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] ========== RAW HOOK INPUT =========="
    echo "$HOOK_INPUT"
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] ===================================="
} >> "$LOGFILE" 2>&1

# Extract command from tool_input using jq
if command -v jq &> /dev/null; then
    # Try multiple possible JSON paths
    BASH_CMD=$(echo "$HOOK_INPUT" | jq -r '.tool_input.command // .command // .parameters.command // empty' 2>/dev/null)

    # Log full hook input for debugging
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] Hook triggered. Tool: $(echo "$HOOK_INPUT" | jq -r '.tool_name // "unknown"')" >> "$LOGFILE"
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] Command: $BASH_CMD" >> "$LOGFILE"
else
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] jq not available, cannot parse hook input" >> "$LOGFILE"
    exit 0
fi

# Check for lock file (recursion prevention)
if [ -f "$LOCKFILE" ]; then
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] Hook already running, skipping to prevent recursion" >> "$LOGFILE"
    exit 0
fi

# Check if this is a git push/merge/pull command
if echo "$BASH_CMD" | grep -qE '(git merge|gh pr merge|git pull.*origin.*(main|master)|git push.*origin.*(main|master))'; then
    CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo 'unknown')
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] Git command detected. Branch: $CURRENT_BRANCH" >> "$LOGFILE"

    # Only trigger on main/master branch
    if [ "$CURRENT_BRANCH" = "main" ] || [ "$CURRENT_BRANCH" = "master" ]; then
        # Check for [skip-hook] tag in FIRST LINE of last commit message
        # This prevents false positives when [skip-hook] appears in commit body
        COMMIT_FIRST_LINE=$(git log -1 --pretty=%s 2>/dev/null)
        if echo "$COMMIT_FIRST_LINE" | grep -q '\[skip-hook\]'; then
            echo "[$(date '+%Y-%m-%d %H:%M:%S')] [skip-hook] tag detected in commit title, skipping" >> "$LOGFILE"
            exit 0
        fi

        # Create lock file
        touch "$LOCKFILE"

        echo "[$(date '+%Y-%m-%d %H:%M:%S')] ✓ Main branch update detected - extracting changed files" >> "$LOGFILE"

        # Get the latest commit SHA
        COMMIT_SHA=$(git rev-parse HEAD 2>/dev/null)
        echo "[$(date '+%Y-%m-%d %H:%M:%S')] Latest commit: $COMMIT_SHA" >> "$LOGFILE"

        # Get list of changed files in the commit
        # Using --diff-filter to exclude deleted files (A=added, M=modified, R=renamed, C=copied)
        CHANGED_FILES=$(git diff-tree --no-commit-id --name-only --diff-filter=AMRC -r "$COMMIT_SHA" 2>/dev/null)

        if [ -z "$CHANGED_FILES" ]; then
            echo "[$(date '+%Y-%m-%d %H:%M:%S')] No changed files detected, skipping indexing" >> "$LOGFILE"
            rm -f "$LOCKFILE"
            exit 0
        fi

        # Count files
        FILE_COUNT=$(echo "$CHANGED_FILES" | wc -l | tr -d ' ')
        echo "[$(date '+%Y-%m-%d %H:%M:%S')] Found $FILE_COUNT changed file(s)" >> "$LOGFILE"
        echo "[$(date '+%Y-%m-%d %H:%M:%S')] Files:" >> "$LOGFILE"
        echo "$CHANGED_FILES" | while read -r file; do
            echo "[$(date '+%Y-%m-%d %H:%M:%S')]   - $file" >> "$LOGFILE"
        done

        # Convert file list to JSON array
        FILES_JSON=$(echo "$CHANGED_FILES" | jq -R . | jq -s .)
        echo "[$(date '+%Y-%m-%d %H:%M:%S')] Files JSON: $FILES_JSON" >> "$LOGFILE"

        # Call backend API to index files
        API_URL="http://localhost:3333/api/rag/index-commit-files"

        # 🔴 CRITICAL: URL encode project directory (handle spaces and special characters)
        PROJECT_DIR_ENCODED=$(printf %s "$PROJECT_ROOT" | jq -sRr @uri)

        echo "[$(date '+%Y-%m-%d %H:%M:%S')] Calling API to index files" >> "$LOGFILE"
        echo "[$(date '+%Y-%m-%d %H:%M:%S')] Project dir: $PROJECT_ROOT" >> "$LOGFILE"
        echo "[$(date '+%Y-%m-%d %H:%M:%S')] Project dir encoded: $PROJECT_DIR_ENCODED" >> "$LOGFILE"

        # Make API call with file list in body
        API_RESPONSE=$(curl -s -X POST "$API_URL?project_dir=${PROJECT_DIR_ENCODED}" \
            -H "Content-Type: application/json" \
            -d "{\"file_paths\": $FILES_JSON}" \
            2>&1)

        API_STATUS=$?

        if [ $API_STATUS -eq 0 ]; then
            echo "[$(date '+%Y-%m-%d %H:%M:%S')] API call successful" >> "$LOGFILE"
            echo "[$(date '+%Y-%m-%d %H:%M:%S')] Response: $API_RESPONSE" >> "$LOGFILE"

            # Output success message to stderr (visible in Claude Code)
            cat << EOF >&2

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ AUTOMATIC RAG INDEXING TRIGGERED
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📚 Main branch updated - indexing $FILE_COUNT file(s)

🔍 Files indexed for semantic search

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
EOF
        else
            echo "[$(date '+%Y-%m-%d %H:%M:%S')] API call failed with status: $API_STATUS" >> "$LOGFILE"
            echo "[$(date '+%Y-%m-%d %H:%M:%S')] Error: $API_RESPONSE" >> "$LOGFILE"

            # Fallback: Create marker file for manual trigger
            MARKER_FILE="$LOGDIR/.rag-indexing-pending"
            echo "$FILES_JSON" > "$MARKER_FILE"
            echo "[$(date '+%Y-%m-%d %H:%M:%S')] Fallback: Created marker file for UserPromptSubmit hook" >> "$LOGFILE"
        fi

        # Remove lock file
        rm -f "$LOCKFILE"
    else
        echo "[$(date '+%Y-%m-%d %H:%M:%S')] Not on main branch, skipping" >> "$LOGFILE"
    fi
else
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] Not a merge/push/pull command, skipping" >> "$LOGFILE"
fi
