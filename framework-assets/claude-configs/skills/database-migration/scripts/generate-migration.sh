#!/bin/bash

################################################################################
# generate-migration.sh - Generate Database Migrations
################################################################################
#
# DESCRIPTION:
#   Create new Alembic migrations with automatic or manual mode. Includes
#   pre-generation validation, naming conventions, and post-generation review.
#
# USAGE:
#   ./generate-migration.sh [OPTIONS]
#
# OPTIONS:
#   -m, --message MSG      Migration message (required)
#   -a, --auto             Use autogenerate from models
#   -h, --head REV         Base revision (default: head)
#   -r, --review-only      Review pending changes without generating
#   -v, --verbose          Verbose output
#   --help                 Show this help message
#
# EXAMPLES:
#   # Autogenerate migration
#   ./generate-migration.sh -m "Add users table" --auto
#
#   # Create empty migration for manual editing
#   ./generate-migration.sh -m "Custom data migration"
#
#   # Generate with specific revision
#   ./generate-migration.sh -m "Add indexes" --auto --head abc123
#
#   # Review-only mode (no generation)
#   ./generate-migration.sh --review-only
#
# EXIT CODES:
#   0 - Migration generated successfully
#   1 - Generation failed
#   2 - Invalid arguments
#   3 - No model changes detected
#
################################################################################

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Default configuration
MESSAGE=""
AUTO_GENERATE=false
HEAD_REVISION="head"
REVIEW_ONLY=false
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
        print_error "Tool '$tool' not found. Please install it first."
        exit 1
    fi
}

check_alembic_initialized() {
    if [ ! -d "alembic" ] && [ ! -f "alembic.ini" ]; then
        print_error "Alembic not initialized. Run 'alembic init alembic' first."
        exit 1
    fi
}

validate_message() {
    local msg=$1

    # Check message is not empty
    if [ -z "$msg" ]; then
        print_error "Migration message cannot be empty"
        return 1
    fi

    # Check message length
    if [ ${#msg} -lt 5 ]; then
        print_warning "Migration message is very short. Consider a more descriptive message."
    fi

    # Check for common anti-patterns
    if [[ "$msg" =~ ^[Ff]ix$ ]] || [[ "$msg" =~ ^[Uu]pdate$ ]]; then
        print_warning "Generic message detected. Consider being more specific."
    fi

    return 0
}

review_pending_changes() {
    print_header "Reviewing Pending Changes"

    print_info "Checking for model changes..."

    # Run alembic with autogenerate in dry-run mode
    if alembic revision --autogenerate -m "temp_review" --sql 2>&1 | grep -q "No changes in schema detected"; then
        print_warning "No schema changes detected"
        return 3
    else
        print_success "Schema changes detected"

        # Show what would be generated
        print_info "Preview of changes (run with --auto to generate):"
        alembic upgrade head --sql 2>&1 | tail -n 20
    fi

    return 0
}

generate_migration() {
    local message=$1
    local auto=$2
    local head=$3

    print_header "Generating Migration"

    # Validate message
    validate_message "$message" || exit 2

    # Build alembic command
    local cmd="alembic revision"

    if [ "$auto" = true ]; then
        cmd="$cmd --autogenerate"
        print_info "Using autogenerate mode"
    else
        print_info "Creating empty migration template"
    fi

    cmd="$cmd -m \"$message\""

    if [ "$head" != "head" ]; then
        cmd="$cmd --head $head"
        log_verbose "Using base revision: $head"
    fi

    # Execute migration generation
    log_verbose "Running: $cmd"

    local output
    output=$(eval $cmd 2>&1)
    local exit_code=$?

    echo "$output"

    if [ $exit_code -ne 0 ]; then
        print_error "Migration generation failed"
        exit 1
    fi

    # Extract generated file path
    local migration_file
    migration_file=$(echo "$output" | grep -o "alembic/versions/.*\.py" | head -1)

    if [ -n "$migration_file" ]; then
        print_success "Migration generated: $migration_file"

        # Check if autogenerate found changes
        if [ "$auto" = true ]; then
            if grep -q "def upgrade():" "$migration_file"; then
                local upgrade_content
                upgrade_content=$(sed -n '/def upgrade():/,/def downgrade():/p' "$migration_file" | head -n -1)

                if echo "$upgrade_content" | grep -q "pass"; then
                    print_warning "No changes detected in autogenerated migration"
                    print_info "The migration file was created but contains no operations"
                    return 3
                else
                    print_success "Migration contains operations"
                fi
            fi
        fi

        # Post-generation checks
        print_header "Post-Generation Review"

        print_info "Migration file: $migration_file"

        # Check for common issues
        if grep -q "DROP TABLE" "$migration_file"; then
            print_warning "⚠️  DESTRUCTIVE: Migration contains DROP TABLE"
        fi

        if grep -q "DROP COLUMN" "$migration_file"; then
            print_warning "⚠️  DESTRUCTIVE: Migration contains DROP COLUMN"
        fi

        if ! grep -q "def downgrade():" "$migration_file" || grep -A 5 "def downgrade():" "$migration_file" | grep -q "pass"; then
            print_warning "⚠️  Migration has no downgrade implementation"
        fi

        # Prompt to review
        echo ""
        print_info "Next steps:"
        echo "  1. Review the migration: cat $migration_file"
        echo "  2. Edit if needed: vim $migration_file"
        echo "  3. Test migration: alembic upgrade head"
        echo "  4. Test rollback: alembic downgrade -1"
        echo ""

    else
        print_error "Could not determine migration file path"
        exit 1
    fi

    return 0
}

################################################################################
# Main Execution
################################################################################

parse_arguments() {
    while [[ $# -gt 0 ]]; do
        case $1 in
            -m|--message)
                MESSAGE="$2"
                shift 2
                ;;
            -a|--auto)
                AUTO_GENERATE=true
                shift
                ;;
            -h|--head)
                HEAD_REVISION="$2"
                shift 2
                ;;
            -r|--review-only)
                REVIEW_ONLY=true
                shift
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
    check_tool "alembic"
    check_alembic_initialized

    # Review-only mode
    if [ "$REVIEW_ONLY" = true ]; then
        review_pending_changes
        exit $?
    fi

    # Validate required arguments
    if [ -z "$MESSAGE" ]; then
        print_error "Migration message is required"
        echo ""
        show_help
    fi

    # Generate migration
    generate_migration "$MESSAGE" "$AUTO_GENERATE" "$HEAD_REVISION"
    exit_code=$?

    if [ $exit_code -eq 0 ]; then
        print_success "Migration generation complete!"
    elif [ $exit_code -eq 3 ]; then
        print_warning "Migration generated but no changes detected"
    fi

    exit $exit_code
}

# Run main function
main "$@"
