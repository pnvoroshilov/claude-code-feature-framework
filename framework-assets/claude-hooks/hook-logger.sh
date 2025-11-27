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
#
# Storage modes:
#   - local: writes to .claudetask/logs/hooks/hooks.log
#   - mongodb: sends logs to backend API

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
HOOK_START_TIME=""
STORAGE_MODE=""
BACKEND_URL="${CLAUDETASK_BACKEND_URL:-http://localhost:3333}"

# Get storage mode from backend API
get_storage_mode() {
    if [[ -n "$STORAGE_MODE" ]]; then
        echo "$STORAGE_MODE"
        return
    fi

    # Try to get from backend
    local response
    response=$(curl -s --max-time 2 "$BACKEND_URL/api/projects/active" 2>/dev/null)
    if [[ $? -eq 0 && -n "$response" ]]; then
        STORAGE_MODE=$(echo "$response" | grep -o '"storage_mode":"[^"]*"' | cut -d'"' -f4)
    fi

    # Default to local if can't determine
    STORAGE_MODE="${STORAGE_MODE:-local}"
    echo "$STORAGE_MODE"
}

# Send log to MongoDB via API
send_to_mongodb() {
    local hook_name="$1"
    local status="$2"
    local message="$3"
    local error="$4"
    local duration_ms="$5"

    # Build query params
    local params="hook_name=$(printf '%s' "$hook_name" | sed 's/ /%20/g')&status=$status"
    [[ -n "$message" ]] && params="$params&message=$(printf '%s' "$message" | sed 's/ /%20/g')"
    [[ -n "$error" ]] && params="$params&error=$(printf '%s' "$error" | sed 's/ /%20/g')"
    [[ -n "$duration_ms" ]] && params="$params&duration_ms=$duration_ms"

    # Send async (don't wait for response)
    curl -s --max-time 2 -X POST "$BACKEND_URL/api/mcp-logs/ingest/hook?$params" >/dev/null 2>&1 &
}

# Get current time in milliseconds
get_time_ms() {
    if [[ "$(uname)" == "Darwin" ]]; then
        # macOS - use python for milliseconds
        python3 -c 'import time; print(int(time.time() * 1000))' 2>/dev/null || date +%s000
    else
        date +%s%3N
    fi
}

# Initialize hook logging
init_hook_log() {
    HOOK_NAME="${1:-unknown}"
    HOOK_START_TIME=$(get_time_ms)

    # Get storage mode (cached after first call)
    local mode=$(get_storage_mode)

    if [[ "$mode" == "mongodb" ]]; then
        # Send start log to MongoDB
        send_to_mongodb "$HOOK_NAME" "running" "HOOK START: $HOOK_NAME"
    else
        # Create log directory if it doesn't exist
        mkdir -p "$HOOK_LOG_DIR"
        # Log start to file
        local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
        echo "$timestamp | $HOOK_NAME | START | HOOK START: $HOOK_NAME" >> "$HOOK_LOG_FILE"
    fi
}

# Log a message
log_hook() {
    local message="$1"
    local mode=$(get_storage_mode)

    if [[ "$mode" == "mongodb" ]]; then
        send_to_mongodb "$HOOK_NAME" "running" "$message"
    else
        local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
        echo "$timestamp | $HOOK_NAME | INFO | $message" >> "$HOOK_LOG_FILE"
    fi
}

# Log success
log_hook_success() {
    local message="${1:-Hook completed successfully}"
    local mode=$(get_storage_mode)
    local duration_ms=""

    if [[ -n "$HOOK_START_TIME" ]]; then
        local end_time=$(get_time_ms)
        duration_ms=$((end_time - HOOK_START_TIME))
    fi

    if [[ "$mode" == "mongodb" ]]; then
        send_to_mongodb "$HOOK_NAME" "success" "HOOK END: $HOOK_NAME - $message" "" "$duration_ms"
    else
        local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
        echo "$timestamp | $HOOK_NAME | SUCCESS | HOOK END: $HOOK_NAME - $message (${duration_ms}ms)" >> "$HOOK_LOG_FILE"
    fi
}

# Log error
log_hook_error() {
    local message="${1:-Hook failed}"
    local mode=$(get_storage_mode)
    local duration_ms=""

    if [[ -n "$HOOK_START_TIME" ]]; then
        local end_time=$(get_time_ms)
        duration_ms=$((end_time - HOOK_START_TIME))
    fi

    if [[ "$mode" == "mongodb" ]]; then
        send_to_mongodb "$HOOK_NAME" "error" "" "$message" "$duration_ms"
    else
        local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
        echo "$timestamp | $HOOK_NAME | ERROR | HOOK ERROR: $HOOK_NAME - $message (${duration_ms}ms)" >> "$HOOK_LOG_FILE"
    fi
}

# Log skip (when hook decides not to run)
log_hook_skip() {
    local reason="${1:-Skipped}"
    local mode=$(get_storage_mode)

    if [[ "$mode" == "mongodb" ]]; then
        send_to_mongodb "$HOOK_NAME" "skipped" "HOOK SKIP: $HOOK_NAME - $reason"
    else
        local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
        echo "$timestamp | $HOOK_NAME | SKIPPED | HOOK SKIP: $HOOK_NAME - $reason" >> "$HOOK_LOG_FILE"
    fi
}

# Export functions
export -f find_project_root
export -f get_storage_mode
export -f get_time_ms
export -f send_to_mongodb
export -f init_hook_log
export -f log_hook
export -f log_hook_success
export -f log_hook_error
export -f log_hook_skip
