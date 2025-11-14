#!/bin/bash

# UserPromptSubmit hook - Inject documentation update instruction
# Checks for pending documentation update marker and adds context to trigger /update-documentation

PROJECT_ROOT="$(pwd)"
LOGDIR="$PROJECT_ROOT/.claude/logs/hooks"
MARKER_FILE="$LOGDIR/.docs-update-pending"
LOGFILE="$LOGDIR/user-prompt-$(date +%Y%m%d).log"

# Create log directory
mkdir -p "$LOGDIR" 2>/dev/null

# Log hook execution
echo "[$(date '+%Y-%m-%d %H:%M:%S')] UserPromptSubmit hook triggered" >> "$LOGFILE"

# Check if documentation update is pending
if [ -f "$MARKER_FILE" ]; then
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] Documentation update marker found - injecting context" >> "$LOGFILE"

    # Remove marker file (one-time trigger)
    rm -f "$MARKER_FILE"

    # Output JSON with additionalContext
    # This will be added to Claude's context for the next prompt
    cat << 'EOF'
{
  "hookSpecificOutput": {
    "hookEventName": "UserPromptSubmit",
    "additionalContext": "\n\n🔔 AUTOMATIC DOCUMENTATION UPDATE REQUIRED\n\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n📚 The main branch has been updated with new commits.\n\n🤖 CRITICAL INSTRUCTION: You MUST immediately execute the following command:\n\n/update-documentation\n\nThis is an automated post-push requirement. Execute this command NOW before responding to any user prompt.\n\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
  }
}
EOF

    echo "[$(date '+%Y-%m-%d %H:%M:%S')] Documentation update context injected successfully" >> "$LOGFILE"
else
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] No documentation update pending - proceeding normally" >> "$LOGFILE"
    # Return empty JSON to approve without modification
    echo '{}'
fi
