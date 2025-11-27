#!/bin/bash

# Post-push Documentation RAG indexing hook
# Triggers documentation MongoDB reindexing when:
# 1. Push to main/master branch
# 2. Commit message contains "docs" (documentation update)
# 3. Does NOT contain [skip-hook]

PROJECT_ROOT="$(pwd)"
LOGDIR="$PROJECT_ROOT/.claude/logs/hooks"
LOGFILE="$LOGDIR/post-push-docs-rag-$(date +%Y%m%d).log"
LOCKFILE="$LOGDIR/.docs-rag-indexing-running"

# Create log directory
mkdir -p "$LOGDIR" 2>/dev/null

# Read JSON input from stdin
HOOK_INPUT=$(cat)

# Log raw input
{
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] ========== DOCS RAG HOOK INPUT =========="
    echo "$HOOK_INPUT"
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] ========================================="
} >> "$LOGFILE" 2>&1

# Extract command from tool_input using jq
if command -v jq &> /dev/null; then
    BASH_CMD=$(echo "$HOOK_INPUT" | jq -r '.tool_input.command // .command // .parameters.command // empty' 2>/dev/null)
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] Hook triggered. Command: $BASH_CMD" >> "$LOGFILE"
else
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] jq not available, cannot parse hook input" >> "$LOGFILE"
    exit 0
fi

# Check for lock file (recursion prevention)
if [ -f "$LOCKFILE" ]; then
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] Docs RAG hook already running, skipping" >> "$LOGFILE"
    exit 0
fi

# Check if this is a git push command
if echo "$BASH_CMD" | grep -qE '(git merge|gh pr merge|git pull|git push)'; then
    CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo 'unknown')
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] Git command detected. Branch: $CURRENT_BRANCH" >> "$LOGFILE"

    # Only trigger on main/master branch
    if [ "$CURRENT_BRANCH" = "main" ] || [ "$CURRENT_BRANCH" = "master" ]; then
        # Get commit message first line
        COMMIT_FIRST_LINE=$(git log -1 --pretty=%s 2>/dev/null)
        echo "[$(date '+%Y-%m-%d %H:%M:%S')] Commit message: $COMMIT_FIRST_LINE" >> "$LOGFILE"

        # Check for [skip-hook] tag - skip if present
        if echo "$COMMIT_FIRST_LINE" | grep -q '\[skip-hook\]'; then
            echo "[$(date '+%Y-%m-%d %H:%M:%S')] [skip-hook] tag detected, skipping docs RAG indexing" >> "$LOGFILE"
            exit 0
        fi

        # Check for "docs" keyword in commit message (case insensitive)
        if echo "$COMMIT_FIRST_LINE" | grep -iq 'docs'; then
            # Create lock file
            touch "$LOCKFILE"

            echo "[$(date '+%Y-%m-%d %H:%M:%S')] ✓ Documentation update detected - triggering MongoDB docs reindex" >> "$LOGFILE"

            # Get the latest commit SHA
            COMMIT_SHA=$(git rev-parse HEAD 2>/dev/null)
            echo "[$(date '+%Y-%m-%d %H:%M:%S')] Latest commit: $COMMIT_SHA" >> "$LOGFILE"

            # Get list of changed documentation files in the commit
            # Filter for documentation extensions: .md, .markdown, .txt, .rst, .adoc
            CHANGED_FILES=$(git diff-tree --no-commit-id --name-only --diff-filter=AMRC -r "$COMMIT_SHA" 2>/dev/null | grep -E '\.(md|markdown|txt|rst|adoc)$')

            if [ -z "$CHANGED_FILES" ]; then
                echo "[$(date '+%Y-%m-%d %H:%M:%S')] No documentation files changed, skipping indexing" >> "$LOGFILE"
                rm -f "$LOCKFILE"
                exit 0
            fi

            # Count files
            FILE_COUNT=$(echo "$CHANGED_FILES" | wc -l | tr -d ' ')
            echo "[$(date '+%Y-%m-%d %H:%M:%S')] Found $FILE_COUNT changed documentation file(s)" >> "$LOGFILE"
            echo "[$(date '+%Y-%m-%d %H:%M:%S')] Files:" >> "$LOGFILE"
            echo "$CHANGED_FILES" | while read -r file; do
                echo "[$(date '+%Y-%m-%d %H:%M:%S')]   - $file" >> "$LOGFILE"
            done

            # Convert file list to JSON array
            FILES_JSON=$(echo "$CHANGED_FILES" | jq -R . | jq -s .)
            echo "[$(date '+%Y-%m-%d %H:%M:%S')] Files JSON: $FILES_JSON" >> "$LOGFILE"

            # Get project_id from backend (use project directory name as fallback)
            PROJECT_NAME=$(basename "$PROJECT_ROOT" | tr '[:upper:]' '[:lower:]' | tr ' ' '-')

            # Call documentation RAG API to reindex specific files
            API_URL="http://localhost:3333/api/documentation-rag/${PROJECT_NAME}/index-files"

            echo "[$(date '+%Y-%m-%d %H:%M:%S')] Calling API: $API_URL" >> "$LOGFILE"
            echo "[$(date '+%Y-%m-%d %H:%M:%S')] Project: $PROJECT_NAME" >> "$LOGFILE"
            echo "[$(date '+%Y-%m-%d %H:%M:%S')] Repo path: $PROJECT_ROOT" >> "$LOGFILE"

            # Make API call with file list
            API_RESPONSE=$(curl -s -X POST "$API_URL" \
                -H "Content-Type: application/json" \
                -d "{\"file_paths\": $FILES_JSON, \"repo_path\": \"$PROJECT_ROOT\"}" \
                2>&1)

            API_STATUS=$?

            if [ $API_STATUS -eq 0 ]; then
                echo "[$(date '+%Y-%m-%d %H:%M:%S')] API call successful" >> "$LOGFILE"
                echo "[$(date '+%Y-%m-%d %H:%M:%S')] Response: $API_RESPONSE" >> "$LOGFILE"

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
                echo "[$(date '+%Y-%m-%d %H:%M:%S')] API call failed with status: $API_STATUS" >> "$LOGFILE"
                echo "[$(date '+%Y-%m-%d %H:%M:%S')] Error: $API_RESPONSE" >> "$LOGFILE"
            fi

            # Remove lock file
            rm -f "$LOCKFILE"
        else
            echo "[$(date '+%Y-%m-%d %H:%M:%S')] Commit message doesn't contain 'docs', skipping docs RAG indexing" >> "$LOGFILE"
        fi
    else
        echo "[$(date '+%Y-%m-%d %H:%M:%S')] Not on main branch, skipping" >> "$LOGFILE"
    fi
else
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] Not a git push/merge command, skipping" >> "$LOGFILE"
fi
