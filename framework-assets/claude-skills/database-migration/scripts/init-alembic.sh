#!/bin/bash

################################################################################
# init-alembic.sh - Initialize Alembic in a Project
################################################################################
#
# DESCRIPTION:
#   Bootstrap Alembic in a new or existing project with best-practice
#   configuration. Supports PostgreSQL, MySQL, and SQLite databases with
#   automatic connection validation and multi-environment setup.
#
# USAGE:
#   ./init-alembic.sh [OPTIONS]
#
# OPTIONS:
#   -p, --path DIR           Alembic directory path (default: ./alembic)
#   -d, --database TYPE      Database type: postgresql, mysql, sqlite
#   -u, --url URL            Database connection URL
#   -e, --environments ENVS  Comma-separated environment names (dev,staging,prod)
#   -t, --template NAME      Alembic template: generic, async, multidb
#   -h, --help               Show this help message
#
# EXAMPLES:
#   # Initialize with PostgreSQL
#   ./init-alembic.sh -d postgresql -u postgres://user:pass@localhost/dbname
#
#   # Initialize with custom location
#   ./init-alembic.sh -p ./migrations -d postgresql
#
#   # Initialize with multi-environment support
#   ./init-alembic.sh -d postgresql -e "dev,staging,production"
#
# EXIT CODES:
#   0 - Initialization successful
#   1 - Configuration error
#   2 - Alembic already initialized
#   3 - Database connection failed
#
################################################################################

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Default configuration
ALEMBIC_PATH="./alembic"
DATABASE_TYPE=""
DATABASE_URL=""
ENVIRONMENTS=""
TEMPLATE="generic"

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

show_help() {
    sed -n '/^# USAGE:/,/^################################################################################/p' "$0" | sed 's/^# //g' | head -n -1
    exit 0
}

check_tool() {
    local tool=$1
    if ! command -v "$tool" &> /dev/null; then
        print_error "Tool '$tool' not found. Please install it first."
        print_info "Install with: pip install alembic sqlalchemy"
        exit 1
    fi
}

test_database_connection() {
    local db_url=$1
    local db_type=$2

    print_info "Testing database connection..."

    # Create a simple Python script to test connection
    python3 -c "
import sys
from sqlalchemy import create_engine

try:
    engine = create_engine('$db_url')
    conn = engine.connect()
    conn.close()
    print('Connection successful')
    sys.exit(0)
except Exception as e:
    print(f'Connection failed: {e}', file=sys.stderr)
    sys.exit(3)
" 2>&1

    if [ $? -eq 0 ]; then
        print_success "Database connection verified"
        return 0
    else
        print_error "Database connection failed"
        return 3
    fi
}

create_env_py() {
    local alembic_dir=$1
    local env_file="$alembic_dir/env.py"

    print_info "Creating enhanced env.py with best practices..."

    cat > "$env_file" << 'EOF'
"""
Alembic Environment Configuration

This file is responsible for:
- Loading SQLAlchemy models
- Configuring the database connection
- Running migrations in online/offline mode
"""

from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context
import os

# This is the Alembic Config object
config = context.config

# Interpret the config file for Python logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Import your models' metadata here
# from myapp.models import Base
# target_metadata = Base.metadata
target_metadata = None

# Support for environment variable override
def get_url():
    """Get database URL from environment or config."""
    return os.getenv("DATABASE_URL", config.get_main_option("sqlalchemy.url"))

def run_migrations_offline() -> None:
    """
    Run migrations in 'offline' mode.

    This configures the context with just a URL and not an Engine.
    Calls to context.execute() here emit the given string to the script output.
    """
    url = get_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online() -> None:
    """
    Run migrations in 'online' mode.

    Creates an Engine and associates a connection with the context.
    """
    configuration = config.get_section(config.config_ini_section)
    configuration["sqlalchemy.url"] = get_url()

    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()

# Determine which mode to run
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
EOF

    print_success "Created enhanced env.py"
}

create_script_py_mako() {
    local alembic_dir=$1
    local template_file="$alembic_dir/script.py.mako"

    print_info "Creating migration template..."

    cat > "$template_file" << 'EOF'
"""${message}

Revision ID: ${up_revision}
Revises: ${down_revision | comma,n}
Create Date: ${create_date}

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
${imports if imports else ""}

# revision identifiers, used by Alembic.
revision: str = ${repr(up_revision)}
down_revision: Union[str, None] = ${repr(down_revision)}
branch_labels: Union[str, Sequence[str], None] = ${repr(branch_labels)}
depends_on: Union[str, Sequence[str], None] = ${repr(depends_on)}


def upgrade() -> None:
    """Apply migration changes."""
    ${upgrades if upgrades else "pass"}


def downgrade() -> None:
    """Revert migration changes."""
    ${downgrades if downgrades else "pass"}
EOF

    print_success "Created migration template"
}

################################################################################
# Main Execution
################################################################################

parse_arguments() {
    while [[ $# -gt 0 ]]; do
        case $1 in
            -p|--path)
                ALEMBIC_PATH="$2"
                shift 2
                ;;
            -d|--database)
                DATABASE_TYPE="$2"
                shift 2
                ;;
            -u|--url)
                DATABASE_URL="$2"
                shift 2
                ;;
            -e|--environments)
                ENVIRONMENTS="$2"
                shift 2
                ;;
            -t|--template)
                TEMPLATE="$2"
                shift 2
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

    print_header "Alembic Initialization"

    # Check if Alembic is installed
    check_tool "alembic"

    # Check if already initialized
    if [ -d "$ALEMBIC_PATH" ]; then
        print_warning "Alembic directory already exists: $ALEMBIC_PATH"
        read -p "Do you want to reinitialize? This will backup existing directory. (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            print_info "Initialization cancelled"
            exit 2
        fi

        # Backup existing directory
        BACKUP_DIR="${ALEMBIC_PATH}_backup_$(date +%Y%m%d_%H%M%S)"
        mv "$ALEMBIC_PATH" "$BACKUP_DIR"
        print_warning "Backed up existing directory to: $BACKUP_DIR"
    fi

    # Initialize Alembic
    print_info "Running alembic init..."
    alembic init "$ALEMBIC_PATH" -t "$TEMPLATE"

    # Configure database URL if provided
    if [ -n "$DATABASE_URL" ]; then
        print_info "Configuring database URL..."

        # Update alembic.ini
        INI_FILE="alembic.ini"
        if [ -f "$INI_FILE" ]; then
            # Replace sqlalchemy.url
            sed -i.bak "s|sqlalchemy.url = .*|sqlalchemy.url = $DATABASE_URL|" "$INI_FILE"
            rm -f "${INI_FILE}.bak"
            print_success "Updated database URL in alembic.ini"

            # Test connection
            test_database_connection "$DATABASE_URL" "$DATABASE_TYPE" || exit 3
        fi
    else
        print_warning "No database URL provided. Please update alembic.ini manually."
    fi

    # Enhance configuration files
    create_env_py "$ALEMBIC_PATH"
    create_script_py_mako "$ALEMBIC_PATH"

    # Create environment-specific configs if requested
    if [ -n "$ENVIRONMENTS" ]; then
        print_info "Setting up multi-environment support..."
        IFS=',' read -ra ENV_ARRAY <<< "$ENVIRONMENTS"

        for env in "${ENV_ARRAY[@]}"; do
            ENV_FILE="alembic_${env}.ini"
            cp alembic.ini "$ENV_FILE"
            print_success "Created environment config: $ENV_FILE"
            print_info "Update $ENV_FILE with ${env} database URL"
        done
    fi

    # Create README
    README_FILE="$ALEMBIC_PATH/README.md"
    cat > "$README_FILE" << 'EOF'
# Alembic Migrations

This directory contains database migrations managed by Alembic.

## Quick Start

### Generate a new migration
```bash
alembic revision --autogenerate -m "Add users table"
```

### Apply migrations
```bash
alembic upgrade head
```

### Rollback migrations
```bash
alembic downgrade -1
```

### Check current revision
```bash
alembic current
```

### View migration history
```bash
alembic history --verbose
```

## Best Practices

1. Always review autogenerated migrations
2. Test migrations locally before production
3. Write reversible downgrade functions
4. Create database backup before applying migrations
5. Use descriptive migration messages

## Environment Variables

You can override the database URL using:
```bash
export DATABASE_URL="postgresql://user:pass@localhost/dbname"
alembic upgrade head
```
EOF

    print_success "Created README.md in $ALEMBIC_PATH"

    # Final summary
    print_header "Initialization Complete"
    print_success "Alembic initialized at: $ALEMBIC_PATH"

    if [ -n "$DATABASE_URL" ]; then
        print_success "Database connection: Verified"
    fi

    echo ""
    print_info "Next steps:"
    echo "  1. Update $ALEMBIC_PATH/env.py with your models"
    echo "  2. Generate your first migration: alembic revision --autogenerate -m 'Initial schema'"
    echo "  3. Review the generated migration"
    echo "  4. Apply migration: alembic upgrade head"
    echo ""

    exit 0
}

# Run main function
main "$@"
