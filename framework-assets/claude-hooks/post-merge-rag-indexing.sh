#!/bin/bash

# Post-merge RAG indexing hook
# Triggers RAG indexing for changed files after successful push/merge to main/master

# Read JSON input from stdin first
HOOK_INPUT=$(cat)

PROJECT_ROOT="$(pwd)"
LOGDIR="$PROJECT_ROOT/.claude/logs/hooks"
LOCKFILE="$LOGDIR/.rag-indexing-running"

# Source hook logger for proper logging based on storage_mode
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
if [ -f "$SCRIPT_DIR/hook-logger.sh" ]; then
    source "$SCRIPT_DIR/hook-logger.sh"
    init_hook_log "post-merge-rag"
else
    # Fallback if hook-logger not available
    log_hook() { echo "[$(date '+%Y-%m-%d %H:%M:%S')] post-merge-rag | INFO | $1" >&2; }
    log_hook_success() { echo "[$(date '+%Y-%m-%d %H:%M:%S')] post-merge-rag | SUCCESS | $1" >&2; }
    log_hook_error() { echo "[$(date '+%Y-%m-%d %H:%M:%S')] post-merge-rag | ERROR | $1" >&2; }
    log_hook_skip() { echo "[$(date '+%Y-%m-%d %H:%M:%S')] post-merge-rag | SKIPPED | $1" >&2; }
fi

# Create log directory
mkdir -p "$LOGDIR" 2>/dev/null

log_hook "RAG Indexing Hook triggered"

# Extract command from tool_input using jq
if ! command -v jq &> /dev/null; then
    log_hook_skip "jq not available, cannot parse hook input"
    exit 0
fi

# Try multiple possible JSON paths
BASH_CMD=$(echo "$HOOK_INPUT" | jq -r '.tool_input.command // .command // .parameters.command // empty' 2>/dev/null)
log_hook "Command: $BASH_CMD"

# Check for lock file (recursion prevention)
if [ -f "$LOCKFILE" ]; then
    log_hook_skip "Hook already running, preventing recursion"
    exit 0
fi

# Check if this is a git push/merge/pull command
if ! echo "$BASH_CMD" | grep -qE '(git merge|gh pr merge|git pull|git push)'; then
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

# Check for [skip-hook] tag in FIRST LINE of last commit message
COMMIT_FIRST_LINE=$(git log -1 --pretty=%s 2>/dev/null)
if echo "$COMMIT_FIRST_LINE" | grep -q '\[skip-hook\]'; then
    log_hook_skip "[skip-hook] tag detected in commit title"
    exit 0
fi

# Create lock file
touch "$LOCKFILE"

log_hook "Main branch update detected - extracting changed files"

# Get the latest commit SHA
COMMIT_SHA=$(git rev-parse HEAD 2>/dev/null)
log_hook "Latest commit: $COMMIT_SHA"

# Get list of changed files in the commit
# Using --diff-filter to exclude deleted files (A=added, M=modified, R=renamed, C=copied)
CHANGED_FILES=$(git diff-tree --no-commit-id --name-only --diff-filter=AMRC -r "$COMMIT_SHA" 2>/dev/null)

if [ -z "$CHANGED_FILES" ]; then
    log_hook_skip "No changed files detected"
    rm -f "$LOCKFILE"
    exit 0
fi

# Count files
FILE_COUNT=$(echo "$CHANGED_FILES" | wc -l | tr -d ' ')
log_hook "Found $FILE_COUNT changed file(s)"

# Convert file list to JSON array
FILES_JSON=$(echo "$CHANGED_FILES" | jq -R . | jq -s .)

# Call backend API to index files
API_URL="http://localhost:3333/api/rag/index-commit-files"

# URL encode project directory (handle spaces and special characters)
PROJECT_DIR_ENCODED=$(printf %s "$PROJECT_ROOT" | jq -sRr @uri)

log_hook "Calling API to index files"

# Make API call with file list in body
API_RESPONSE=$(curl -s -X POST "$API_URL?project_dir=${PROJECT_DIR_ENCODED}" \
    -H "Content-Type: application/json" \
    -d "{\"file_paths\": $FILES_JSON}" \
    2>&1)

API_STATUS=$?

if [ $API_STATUS -eq 0 ]; then
    log_hook_success "API call successful - indexed $FILE_COUNT files"

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
    log_hook_error "API call failed with status: $API_STATUS - $API_RESPONSE"

    # Fallback: Create marker file for manual trigger
    MARKER_FILE="$LOGDIR/.rag-indexing-pending"
    echo "$FILES_JSON" > "$MARKER_FILE"
    log_hook "Created marker file for UserPromptSubmit hook fallback"
fi

# Remove lock file
rm -f "$LOCKFILE"
