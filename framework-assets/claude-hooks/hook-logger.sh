#!/bin/bash
# Hook Logger - Utility script for logging hook executions
# Usage: source this file at the beginning of your hook scripts
#
# Example:
#   #!/bin/bash
#   source "$(dirname "$0")/hook-logger.sh"
#   init_hook_log "my-hook-name"
#
#   log_hook "Starting processing..."
#   # ... do work ...
#   log_hook_success "Completed successfully"
#   # or
#   log_hook_error "Failed: reason"

# Find project root (where .claudetask folder should be)
find_project_root() {
    local dir="$PWD"
    while [[ "$dir" != "/" ]]; do
        if [[ -d "$dir/.claudetask" ]]; then
            echo "$dir"
            return 0
        fi
        dir="$(dirname "$dir")"
    done
    # Fallback to current directory
    echo "$PWD"
}

PROJECT_ROOT=$(find_project_root)
HOOK_LOG_DIR="$PROJECT_ROOT/.claudetask/logs/hooks"
HOOK_LOG_FILE="$HOOK_LOG_DIR/hooks.log"
HOOK_NAME=""

# Initialize hook logging
init_hook_log() {
    HOOK_NAME="${1:-unknown}"

    # Create log directory if it doesn't exist
    mkdir -p "$HOOK_LOG_DIR"

    # Log start
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo "$timestamp | $HOOK_NAME | START | HOOK START: $HOOK_NAME" >> "$HOOK_LOG_FILE"
}

# Log a message
log_hook() {
    local message="$1"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo "$timestamp | $HOOK_NAME | INFO | $message" >> "$HOOK_LOG_FILE"
}

# Log success
log_hook_success() {
    local message="${1:-Hook completed successfully}"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo "$timestamp | $HOOK_NAME | SUCCESS | HOOK END: $HOOK_NAME - $message" >> "$HOOK_LOG_FILE"
}

# Log error
log_hook_error() {
    local message="${1:-Hook failed}"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo "$timestamp | $HOOK_NAME | ERROR | HOOK ERROR: $HOOK_NAME - $message" >> "$HOOK_LOG_FILE"
}

# Log skip (when hook decides not to run)
log_hook_skip() {
    local reason="${1:-Skipped}"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo "$timestamp | $HOOK_NAME | SKIPPED | HOOK SKIP: $HOOK_NAME - $reason" >> "$HOOK_LOG_FILE"
}

# Export functions
export -f find_project_root
export -f init_hook_log
export -f log_hook
export -f log_hook_success
export -f log_hook_error
export -f log_hook_skip
