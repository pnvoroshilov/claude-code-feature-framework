#!/bin/bash

################################################################################
# check-migration-status.sh - Migration History and Status
################################################################################
#
# DESCRIPTION:
#   Display migration status, history, and pending migrations. Detect branches
#   and divergence in migration chains.
#
# USAGE:
#   ./check-migration-status.sh [OPTIONS]
#
# OPTIONS:
#   -h, --history          Show full migration history
#   -p, --pending          Show only pending migrations
#   -c, --check-branches   Detect migration branches/conflicts
#   -C, --compare ENV      Compare with another environment
#   -v, --verbose          Verbose output
#   --help                 Show this help message
#
# EXAMPLES:
#   # Show current status
#   ./check-migration-status.sh
#
#   # Show full history
#   ./check-migration-status.sh --history
#
#   # Show pending migrations only
#   ./check-migration-status.sh --pending
#
#   # Check for branches/conflicts
#   ./check-migration-status.sh --check-branches
#
#   # Compare with another environment
#   ./check-migration-status.sh --compare staging
#
# EXIT CODES:
#   0 - Status retrieved successfully
#   1 - Database connection failed
#   2 - Configuration error
#
################################################################################

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

# Configuration
SHOW_HISTORY=false
SHOW_PENDING=false
CHECK_BRANCHES=false
COMPARE_ENV=""
VERBOSE=false

################################################################################
# Helper Functions
################################################################################

print_header() {
    echo -e "\n${BLUE}======================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}======================================${NC}\n"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ $1${NC}"
}

log_verbose() {
    if [ "$VERBOSE" = true ]; then
        echo -e "${CYAN}[DEBUG] $1${NC}"
    fi
}

show_help() {
    sed -n '/^# USAGE:/,/^################################################################################/p' "$0" | sed 's/^# //g' | head -n -1
    exit 0
}

check_alembic() {
    if ! command -v alembic &> /dev/null; then
        print_error "Alembic not found"
        exit 1
    fi

    if [ ! -f "alembic.ini" ]; then
        print_error "alembic.ini not found"
        exit 2
    fi
}

show_current_revision() {
    print_header "Current Migration Status"

    local current_output
    current_output=$(alembic current --verbose 2>&1)

    if echo "$current_output" | grep -q "Current revision"; then
        echo "$current_output" | while IFS= read -r line; do
            if [[ $line == *"Current revision"* ]]; then
                echo -e "${GREEN}$line${NC}"
            else
                echo "$line"
            fi
        done
        print_success "Database is migrated"
    else
        print_warning "No current revision (database not yet migrated)"
    fi
}

show_migration_history() {
    print_header "Migration History"

    local history_output
    history_output=$(alembic history --verbose 2>&1)

    # Colorize output
    echo "$history_output" | while IFS= read -r line; do
        if [[ $line == *"->"* ]]; then
            # Revision line
            echo -e "${CYAN}$line${NC}"
        elif [[ $line == *"Rev:"* ]]; then
            echo -e "${GREEN}$line${NC}"
        elif [[ $line == *"Parent:"* ]]; then
            echo -e "${YELLOW}$line${NC}"
        else
            echo "$line"
        fi
    done
}

show_pending_migrations() {
    print_header "Pending Migrations"

    # Get current revision
    local current_rev
    current_rev=$(alembic current 2>/dev/null | grep -o '[a-f0-9]\{12\}' | head -1)

    if [ -z "$current_rev" ]; then
        current_rev="<base>"
    fi

    log_verbose "Current revision: $current_rev"

    # Get all migrations
    local all_revs
    all_revs=$(alembic history --verbose | grep "^Rev:" | awk '{print $2}')

    # Find migrations after current
    local in_pending=false
    local pending_count=0

    while IFS= read -r rev; do
        if [ "$rev" = "$current_rev" ]; then
            in_pending=true
            continue
        fi

        if [ "$in_pending" = true ]; then
            # Show this pending migration
            local migration_info
            migration_info=$(alembic history --verbose | grep -A 5 "^Rev: $rev")

            echo -e "${YELLOW}Pending: $rev${NC}"
            echo "$migration_info"
            echo ""

            ((pending_count++))
        fi
    done <<< "$all_revs"

    if [ $pending_count -eq 0 ]; then
        print_success "No pending migrations - database is up to date"
    else
        print_warning "Found $pending_count pending migration(s)"
    fi
}

check_for_branches() {
    print_header "Checking for Migration Branches"

    # Get all revisions with their parents
    local branches_output
    branches_output=$(alembic branches --verbose 2>&1)

    if echo "$branches_output" | grep -q "Rev:"; then
        print_warning "Migration branches detected!"
        echo "$branches_output"
        print_info "You may need to merge branches with: alembic merge -m 'merge branches' <rev1> <rev2>"
    else
        print_success "No migration branches detected"
    fi
}

compare_environments() {
    local target_env=$1

    print_header "Comparing with $target_env Environment"

    # Check if environment config exists
    if [ ! -f "alembic_${target_env}.ini" ]; then
        print_error "Environment config not found: alembic_${target_env}.ini"
        exit 2
    fi

    # Get current environment revision
    local current_rev
    current_rev=$(alembic current 2>/dev/null | grep -o '[a-f0-9]\{12\}' | head -1)

    # Get target environment revision
    local target_rev
    target_rev=$(alembic -c "alembic_${target_env}.ini" current 2>/dev/null | grep -o '[a-f0-9]\{12\}' | head -1)

    echo "Current environment: ${current_rev:-<none>}"
    echo "Target environment:  ${target_rev:-<none>}"
    echo ""

    if [ "$current_rev" = "$target_rev" ]; then
        print_success "Environments are in sync"
    else
        print_warning "Environments are out of sync"
        print_info "Run migration comparison for details"
    fi
}

################################################################################
# Main Execution
################################################################################

parse_arguments() {
    while [[ $# -gt 0 ]]; do
        case $1 in
            -h|--history)
                SHOW_HISTORY=true
                shift
                ;;
            -p|--pending)
                SHOW_PENDING=true
                shift
                ;;
            -c|--check-branches)
                CHECK_BRANCHES=true
                shift
                ;;
            -C|--compare)
                COMPARE_ENV="$2"
                shift 2
                ;;
            -v|--verbose)
                VERBOSE=true
                shift
                ;;
            --help)
                show_help
                ;;
            *)
                print_error "Unknown option: $1"
                show_help
                ;;
        esac
    done
}

main() {
    parse_arguments "$@"

    # Check prerequisites
    check_alembic

    # If no specific options, show current status
    if [ "$SHOW_HISTORY" = false ] && \
       [ "$SHOW_PENDING" = false ] && \
       [ "$CHECK_BRANCHES" = false ] && \
       [ -z "$COMPARE_ENV" ]; then
        show_current_revision
        exit 0
    fi

    # Show requested information
    if [ "$SHOW_HISTORY" = true ]; then
        show_migration_history
    fi

    if [ "$SHOW_PENDING" = true ]; then
        show_pending_migrations
    fi

    if [ "$CHECK_BRANCHES" = true ]; then
        check_for_branches
    fi

    if [ -n "$COMPARE_ENV" ]; then
        compare_environments "$COMPARE_ENV"
    fi

    exit 0
}

# Run main function
main "$@"
