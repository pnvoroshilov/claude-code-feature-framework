#!/bin/bash

# Post-push Documentation RAG indexing hook
# Triggers documentation MongoDB reindexing when:
# 1. Push to main/master branch
# 2. Commit message contains "docs" (documentation update)
# 3. Does NOT contain [skip-hook]

# Read JSON input from stdin first
HOOK_INPUT=$(cat)

PROJECT_ROOT="$(pwd)"
LOGDIR="$PROJECT_ROOT/.claude/logs/hooks"
LOCKFILE="$LOGDIR/.docs-rag-indexing-running"

# Source hook logger for proper logging based on storage_mode
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
if [ -f "$SCRIPT_DIR/hook-logger.sh" ]; then
    source "$SCRIPT_DIR/hook-logger.sh"
    init_hook_log "post-push-docs-rag"
else
    # Fallback if hook-logger not available
    log_hook() { echo "[$(date '+%Y-%m-%d %H:%M:%S')] post-push-docs-rag | INFO | $1" >&2; }
    log_hook_success() { echo "[$(date '+%Y-%m-%d %H:%M:%S')] post-push-docs-rag | SUCCESS | $1" >&2; }
    log_hook_error() { echo "[$(date '+%Y-%m-%d %H:%M:%S')] post-push-docs-rag | ERROR | $1" >&2; }
    log_hook_skip() { echo "[$(date '+%Y-%m-%d %H:%M:%S')] post-push-docs-rag | SKIPPED | $1" >&2; }
fi

# Create log directory
mkdir -p "$LOGDIR" 2>/dev/null

log_hook "Docs RAG Hook triggered"

# Extract command from tool_input using jq
if ! command -v jq &> /dev/null; then
    log_hook_skip "jq not available, cannot parse hook input"
    exit 0
fi

BASH_CMD=$(echo "$HOOK_INPUT" | jq -r '.tool_input.command // .command // .parameters.command // empty' 2>/dev/null)
log_hook "Command: $BASH_CMD"

# Check for lock file (recursion prevention)
if [ -f "$LOCKFILE" ]; then
    log_hook_skip "Docs RAG hook already running"
    exit 0
fi

# Check if this is a git push command
# Use flexible regex to match git commands with flags (e.g., git -C /path push)
if ! echo "$BASH_CMD" | grep -qE '\bgit\b.*(push|pull|merge)|\bgh\s+pr\s+merge\b'; then
    log_hook_skip "Not a git push/merge command"
    exit 0
fi

CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo 'unknown')
log_hook "Git command detected. Branch: $CURRENT_BRANCH"

# Only trigger on main/master branch
if [ "$CURRENT_BRANCH" != "main" ] && [ "$CURRENT_BRANCH" != "master" ]; then
    log_hook_skip "Not on main/master branch"
    exit 0
fi

# Get commit message first line
COMMIT_FIRST_LINE=$(git log -1 --pretty=%s 2>/dev/null)
log_hook "Commit message: $COMMIT_FIRST_LINE"

# Check for [skip-hook] tag - skip if present
if echo "$COMMIT_FIRST_LINE" | grep -q '\[skip-hook\]'; then
    log_hook_skip "[skip-hook] tag detected"
    exit 0
fi

# Check for "docs" keyword in commit message (case insensitive)
if ! echo "$COMMIT_FIRST_LINE" | grep -iq 'docs'; then
    log_hook_skip "Commit message doesn't contain 'docs'"
    exit 0
fi

# Create lock file
touch "$LOCKFILE"

log_hook "Documentation update detected - triggering MongoDB docs reindex"

# Get the latest commit SHA
COMMIT_SHA=$(git rev-parse HEAD 2>/dev/null)
log_hook "Latest commit: $COMMIT_SHA"

# Get list of changed documentation files in the commit
# Filter for documentation extensions: .md, .markdown, .txt, .rst, .adoc
CHANGED_FILES=$(git diff-tree --no-commit-id --name-only --diff-filter=AMRC -r "$COMMIT_SHA" 2>/dev/null | grep -E '\.(md|markdown|txt|rst|adoc)$')

if [ -z "$CHANGED_FILES" ]; then
    log_hook_skip "No documentation files changed"
    rm -f "$LOCKFILE"
    exit 0
fi

# Count files
FILE_COUNT=$(echo "$CHANGED_FILES" | wc -l | tr -d ' ')
log_hook "Found $FILE_COUNT changed documentation file(s)"

# Convert file list to JSON array
FILES_JSON=$(echo "$CHANGED_FILES" | jq -R . | jq -s .)

# Get project_id from backend (use project directory name as fallback)
PROJECT_NAME=$(basename "$PROJECT_ROOT" | tr '[:upper:]' '[:lower:]' | tr ' ' '-')

# Call documentation RAG API to reindex specific files
API_URL="http://localhost:3333/api/documentation-rag/${PROJECT_NAME}/index-files"

log_hook "Calling API: $API_URL"

# Make API call with file list
API_RESPONSE=$(curl -s -X POST "$API_URL" \
    -H "Content-Type: application/json" \
    -d "{\"file_paths\": $FILES_JSON, \"repo_path\": \"$PROJECT_ROOT\"}" \
    2>&1)

API_STATUS=$?

if [ $API_STATUS -eq 0 ]; then
    log_hook_success "API call successful - indexed $FILE_COUNT docs files"

    # Output success message to stderr (visible in Claude Code)
    cat << EOF >&2

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ DOCUMENTATION RAG INDEXING TRIGGERED
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📚 Documentation update detected - reindexing $FILE_COUNT file(s)

🔍 Files indexed for semantic documentation search

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
EOF
else
    log_hook_error "API call failed with status: $API_STATUS - $API_RESPONSE"
fi

# Remove lock file
rm -f "$LOCKFILE"
