#!/bin/bash

# Post-push documentation update hook
# Triggers /update-documentation after successful push to main/master

# Use absolute path for logs to ensure they're created
PROJECT_ROOT="$(pwd)"
LOGDIR="$PROJECT_ROOT/.claude/logs/hooks"
LOGFILE="$LOGDIR/post-merge-doc-$(date +%Y%m%d).log"
LOCKFILE="$LOGDIR/.hook-running"

# Create log directory
mkdir -p "$LOGDIR" 2>/dev/null

# Read JSON input from stdin
HOOK_INPUT=$(cat)

# Debug output to stderr (visible in Claude Code)
echo "🔍 Hook triggered at $(date '+%H:%M:%S')" >&2

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
        # Check for [skip-hook] tag in last commit
        LAST_COMMIT_MSG=$(git log -1 --pretty=%B 2>/dev/null)
        if echo "$LAST_COMMIT_MSG" | grep -q '\[skip-hook\]'; then
            echo "[$(date '+%Y-%m-%d %H:%M:%S')] [skip-hook] tag detected, skipping" >> "$LOGFILE"
            exit 0
        fi

        # Create lock file
        touch "$LOCKFILE"

        echo "[$(date '+%Y-%m-%d %H:%M:%S')] ✓ Main branch update detected - triggering /update-documentation" >> "$LOGFILE"

        # Call backend API to execute /update-documentation command
        API_URL="http://localhost:3333/api/claude-sessions/execute-command"
        COMMAND="/update-documentation"

        echo "[$(date '+%Y-%m-%d %H:%M:%S')] Calling API to execute command: $COMMAND" >> "$LOGFILE"

        # Make API call
        API_RESPONSE=$(curl -s -X POST "$API_URL?command=${COMMAND}&project_dir=${PROJECT_ROOT}" \
            -H "Content-Type: application/json" \
            2>&1)

        API_STATUS=$?

        if [ $API_STATUS -eq 0 ]; then
            echo "[$(date '+%Y-%m-%d %H:%M:%S')] API call successful" >> "$LOGFILE"
            echo "[$(date '+%Y-%m-%d %H:%M:%S')] Response: $API_RESPONSE" >> "$LOGFILE"

            # Output success message to stderr (visible in Claude Code)
            cat << EOF >&2

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ AUTOMATIC DOCUMENTATION UPDATE TRIGGERED
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📚 Main branch updated - documentation sync initiated

🤖 Command: $COMMAND

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
EOF
        else
            echo "[$(date '+%Y-%m-%d %H:%M:%S')] API call failed with status: $API_STATUS" >> "$LOGFILE"
            echo "[$(date '+%Y-%m-%d %H:%M:%S')] Error: $API_RESPONSE" >> "$LOGFILE"

            # Fallback: Create marker file for manual trigger
            MARKER_FILE="$LOGDIR/.docs-update-pending"
            echo "$(date '+%Y-%m-%d %H:%M:%S')" > "$MARKER_FILE"
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
