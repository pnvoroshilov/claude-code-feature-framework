#!/bin/bash

################################################################################
# run-migration.sh - Execute Migrations with Safety Checks
################################################################################
#
# DESCRIPTION:
#   Run migrations with pre-flight checks, backups, and rollback capability.
#   Supports dry-run mode, automatic backups, and environment-specific configs.
#
# USAGE:
#   ./run-migration.sh COMMAND REVISION [OPTIONS]
#
# ARGUMENTS:
#   COMMAND    Alembic command (upgrade, downgrade, current)
#   REVISION   Target revision (head, -1, +1, specific hash)
#
# OPTIONS:
#   -b, --backup           Create database backup before migration
#   -d, --dry-run          Show SQL without executing
#   -e, --env ENV          Environment (dev, staging, production)
#   -n, --no-backup        Skip backup (use with caution!)
#   -v, --verbose          Verbose output
#   -h, --help             Show this help message
#
# EXAMPLES:
#   # Upgrade to latest (with backup)
#   ./run-migration.sh upgrade head --backup
#
#   # Dry-run to see what will happen
#   ./run-migration.sh upgrade head --dry-run
#
#   # Downgrade one revision
#   ./run-migration.sh downgrade -1
#
#   # Upgrade to specific revision
#   ./run-migration.sh upgrade abc123 --no-backup
#
#   # Production mode (strict validation)
#   ./run-migration.sh upgrade head --env production
#
# EXIT CODES:
#   0 - Migration successful
#   1 - Migration failed
#   2 - Pre-flight checks failed
#   3 - Backup failed
#
################################################################################

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Configuration
COMMAND=""
REVISION=""
CREATE_BACKUP=false
DRY_RUN=false
ENVIRONMENT="dev"
NO_BACKUP=false
VERBOSE=false
BACKUP_DIR="./backups"

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
        echo -e "${BLUE}[DEBUG] $1${NC}"
    fi
}

show_help() {
    sed -n '/^# USAGE:/,/^################################################################################/p' "$0" | sed 's/^# //g' | head -n -1
    exit 0
}

check_tool() {
    local tool=$1
    if ! command -v "$tool" &> /dev/null; then
        print_error "Tool '$tool' not found"
        return 1
    fi
    return 0
}

pre_flight_checks() {
    print_header "Pre-Flight Checks"

    # Check Alembic
    if ! check_tool "alembic"; then
        print_error "Alembic not installed"
        exit 2
    fi
    print_success "Alembic installed"

    # Check alembic.ini
    if [ ! -f "alembic.ini" ]; then
        print_error "alembic.ini not found"
        exit 2
    fi
    print_success "alembic.ini found"

    # Check database connection
    print_info "Testing database connection..."
    if alembic current &> /dev/null; then
        print_success "Database connection OK"
    else
        print_error "Cannot connect to database"
        exit 2
    fi

    # Get current revision
    local current_rev
    current_rev=$(alembic current 2>/dev/null | grep -o '[a-f0-9]\{12\}' | head -1)

    if [ -n "$current_rev" ]; then
        print_info "Current revision: $current_rev"
    else
        print_info "Current revision: None (empty database)"
    fi

    return 0
}

create_backup() {
    print_header "Creating Database Backup"

    mkdir -p "$BACKUP_DIR"

    local timestamp
    timestamp=$(date +%Y%m%d_%H%M%S)
    local backup_file="$BACKUP_DIR/migration_backup_${timestamp}.sql"

    # Get database URL from alembic.ini
    local db_url
    db_url=$(grep "^sqlalchemy.url" alembic.ini | cut -d'=' -f2- | tr -d ' ')

    if [[ $db_url == postgresql* ]]; then
        print_info "Backing up PostgreSQL database..."

        # Extract connection details
        local pg_dump_cmd="pg_dump"

        # Use environment variable if set
        if [ -n "$DATABASE_URL" ]; then
            db_url="$DATABASE_URL"
        fi

        # Run pg_dump
        if $pg_dump_cmd "$db_url" > "$backup_file" 2>&1; then
            print_success "Backup created: $backup_file"

            # Compress backup
            gzip "$backup_file"
            print_success "Backup compressed: ${backup_file}.gz"

            return 0
        else
            print_error "Backup failed"
            return 3
        fi

    elif [[ $db_url == mysql* ]]; then
        print_info "Backing up MySQL database..."

        # MySQL backup logic
        print_warning "MySQL backup not yet implemented"
        return 0

    elif [[ $db_url == sqlite* ]]; then
        print_info "Backing up SQLite database..."

        # Extract database file path
        local db_file
        db_file=$(echo "$db_url" | sed 's/sqlite:\/\/\///')

        if [ -f "$db_file" ]; then
            cp "$db_file" "$backup_file"
            gzip "$backup_file"
            print_success "Backup created: ${backup_file}.gz"
            return 0
        else
            print_error "Database file not found: $db_file"
            return 3
        fi
    else
        print_warning "Unknown database type, skipping backup"
        return 0
    fi
}

run_migration() {
    local cmd=$1
    local rev=$2

    print_header "Running Migration"

    # Build alembic command
    local alembic_cmd="alembic $cmd $rev"

    if [ "$DRY_RUN" = true ]; then
        alembic_cmd="$alembic_cmd --sql"
        print_info "DRY RUN MODE - Showing SQL without executing"
    fi

    # Environment-specific config
    if [ "$ENVIRONMENT" != "dev" ] && [ -f "alembic_${ENVIRONMENT}.ini" ]; then
        alembic_cmd="alembic -c alembic_${ENVIRONMENT}.ini $cmd $rev"
        print_info "Using environment config: alembic_${ENVIRONMENT}.ini"
    fi

    log_verbose "Command: $alembic_cmd"

    # Execute migration
    print_info "Executing: $alembic_cmd"
    echo ""

    if eval "$alembic_cmd"; then
        print_success "Migration completed successfully"
        return 0
    else
        print_error "Migration failed"
        return 1
    fi
}

post_migration_checks() {
    print_header "Post-Migration Verification"

    # Get new revision
    local new_rev
    new_rev=$(alembic current 2>/dev/null | grep -o '[a-f0-9]\{12\}' | head -1)

    if [ -n "$new_rev" ]; then
        print_success "Current revision: $new_rev"
    else
        print_warning "Could not determine current revision"
    fi

    # Check database connection still works
    if alembic current &> /dev/null; then
        print_success "Database connection still OK"
    else
        print_error "Database connection issue after migration"
        return 1
    fi

    return 0
}

################################################################################
# Main Execution
################################################################################

parse_arguments() {
    # First two arguments are command and revision
    if [ $# -lt 2 ]; then
        print_error "Missing required arguments"
        echo ""
        show_help
    fi

    COMMAND=$1
    REVISION=$2
    shift 2

    # Parse options
    while [[ $# -gt 0 ]]; do
        case $1 in
            -b|--backup)
                CREATE_BACKUP=true
                shift
                ;;
            -d|--dry-run)
                DRY_RUN=true
                shift
                ;;
            -e|--env)
                ENVIRONMENT="$2"
                shift 2
                ;;
            -n|--no-backup)
                NO_BACKUP=true
                shift
                ;;
            -v|--verbose)
                VERBOSE=true
                shift
                ;;
            -h|--help)
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

    print_header "Migration Runner"
    print_info "Command: $COMMAND"
    print_info "Revision: $REVISION"
    print_info "Environment: $ENVIRONMENT"

    # Pre-flight checks
    pre_flight_checks || exit $?

    # Create backup (unless explicitly disabled or dry-run)
    if [ "$DRY_RUN" = false ] && [ "$NO_BACKUP" = false ]; then
        if [ "$CREATE_BACKUP" = true ] || [ "$ENVIRONMENT" = "production" ]; then
            create_backup || exit $?
        else
            print_warning "Running without backup (use --backup to create one)"
            read -p "Continue without backup? (y/N): " -n 1 -r
            echo
            if [[ ! $REPLY =~ ^[Yy]$ ]]; then
                print_info "Migration cancelled"
                exit 0
            fi
        fi
    fi

    # Run migration
    run_migration "$COMMAND" "$REVISION" || exit $?

    # Post-migration checks (skip for dry-run)
    if [ "$DRY_RUN" = false ]; then
        post_migration_checks || exit $?
    fi

    # Summary
    print_header "Migration Summary"
    print_success "Migration completed successfully"

    if [ "$DRY_RUN" = false ]; then
        print_info "Check application health and functionality"
    fi

    exit 0
}

# Run main function
main "$@"
