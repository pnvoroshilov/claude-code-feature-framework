# Database Migration Scripts

This directory contains automation scripts for database migration workflows using Alembic/SQLAlchemy. These scripts help automate common migration tasks, validation, testing, and deployment procedures.

## Available Scripts

### 1. `init-alembic.sh` - Initialize Alembic in a Project

**Purpose**: Bootstrap Alembic in a new or existing project with best-practice configuration.

**Features**:
- Interactive Alembic initialization
- Auto-configuration for common databases (PostgreSQL, MySQL, SQLite)
- Database connection validation
- Template customization
- Multi-environment support (dev, staging, production)

**Usage**:
```bash
# Initialize with PostgreSQL
./init-alembic.sh -d postgresql -u postgres://user:pass@localhost/dbname

# Initialize with custom location
./init-alembic.sh -p ./migrations -d postgresql

# Initialize with multi-environment support
./init-alembic.sh -d postgresql -e "dev,staging,production"
```

**Options**:
- `-p, --path DIR` - Alembic directory path (default: ./alembic)
- `-d, --database TYPE` - Database type (postgresql, mysql, sqlite)
- `-u, --url URL` - Database connection URL
- `-e, --environments ENVS` - Comma-separated environment names
- `-t, --template NAME` - Alembic template (generic, async, multidb)

**Exit Codes**:
- `0` - Initialization successful
- `1` - Configuration error
- `2` - Alembic already initialized
- `3` - Database connection failed

---

### 2. `generate-migration.sh` - Generate Database Migrations

**Purpose**: Create new Alembic migrations with automatic or manual mode.

**Features**:
- Autogenerate migrations from SQLAlchemy models
- Manual migration scaffolding
- Migration naming conventions
- Pre-generation validation
- Post-generation review prompts
- Automatic detection of common issues

**Usage**:
```bash
# Autogenerate migration
./generate-migration.sh -m "Add users table" --auto

# Create empty migration for manual editing
./generate-migration.sh -m "Custom data migration"

# Generate with specific revision
./generate-migration.sh -m "Add indexes" --auto --head abc123

# Review-only mode (no generation)
./generate-migration.sh --review-only
```

**Options**:
- `-m, --message MSG` - Migration message (required)
- `-a, --auto` - Use autogenerate
- `-h, --head REV` - Base revision (default: head)
- `-r, --review-only` - Review pending changes without generating
- `-v, --verbose` - Verbose output

**Exit Codes**:
- `0` - Migration generated successfully
- `1` - Generation failed
- `2` - Invalid arguments
- `3` - No model changes detected

---

### 3. `validate-migration.py` - Validate Migration Files

**Purpose**: Validates migration files for common issues and best practices.

**Features**:
- Syntax validation
- Upgrade/downgrade function verification
- Destructive operation detection
- Index creation validation (CONCURRENTLY for PostgreSQL)
- Transaction handling verification
- Data loss risk assessment
- Reversibility checking
- Best practice compliance

**Usage**:
```bash
# Validate specific migration
python validate-migration.py -f alembic/versions/abc123_add_users.py

# Validate all migrations
python validate-migration.py -a

# Validate with strict mode (fail on warnings)
python validate-migration.py -a -s

# Generate validation report
python validate-migration.py -a -r validation-report.html
```

**Options**:
- `-f, --file FILE` - Migration file to validate
- `-a, --all` - Validate all migrations
- `-s, --strict` - Fail on warnings
- `-r, --report FILE` - Generate HTML report
- `-v, --verbose` - Verbose output

**Validation Checks**:
- **Syntax**: Python syntax errors
- **Functions**: upgrade() and downgrade() exist
- **Transactions**: Proper transaction handling
- **Destructive Ops**: DROP TABLE/COLUMN detection
- **Indexes**: CONCURRENTLY for PostgreSQL
- **Reversibility**: Downgrade function implementation
- **Data Loss**: Potential data loss operations

**Exit Codes**:
- `0` - All validations passed
- `1` - Validation errors found
- `2` - Critical issues detected

---

### 4. `run-migration.sh` - Execute Migrations with Safety Checks

**Purpose**: Run migrations with pre-flight checks, backups, and rollback capability.

**Features**:
- Database backup before migration
- Dry-run mode
- Pre-migration validation
- Progress monitoring
- Automatic rollback on failure
- Migration history tracking
- Multi-environment support

**Usage**:
```bash
# Upgrade to latest (with backup)
./run-migration.sh upgrade head --backup

# Dry-run to see what will happen
./run-migration.sh upgrade head --dry-run

# Downgrade one revision
./run-migration.sh downgrade -1

# Upgrade to specific revision
./run-migration.sh upgrade abc123 --no-backup

# Production mode (strict validation)
./run-migration.sh upgrade head --env production
```

**Options**:
- `COMMAND` - Alembic command (upgrade, downgrade, current)
- `REVISION` - Target revision (head, -1, +1, specific hash)
- `-b, --backup` - Create database backup before migration
- `-d, --dry-run` - Show SQL without executing
- `-e, --env ENV` - Environment (dev, staging, production)
- `-n, --no-backup` - Skip backup (use with caution)
- `-v, --verbose` - Verbose output

**Exit Codes**:
- `0` - Migration successful
- `1` - Migration failed
- `2` - Pre-flight checks failed
- `3` - Backup failed

---

### 5. `check-migration-status.sh` - Migration History and Status

**Purpose**: Display migration status, history, and pending migrations.

**Features**:
- Current revision display
- Pending migrations list
- Migration history with dates
- Divergence detection
- Branch visualization
- Database connection status

**Usage**:
```bash
# Show current status
./check-migration-status.sh

# Show full history
./check-migration-status.sh --history

# Show pending migrations only
./check-migration-status.sh --pending

# Check for branches/conflicts
./check-migration-status.sh --check-branches

# Compare with another environment
./check-migration-status.sh --compare staging
```

**Options**:
- `-h, --history` - Show full migration history
- `-p, --pending` - Show only pending migrations
- `-c, --check-branches` - Detect migration branches
- `-C, --compare ENV` - Compare with another environment
- `-v, --verbose` - Verbose output

**Exit Codes**:
- `0` - Status retrieved successfully
- `1` - Database connection failed
- `2` - Configuration error

---

### 6. `test-migration.py` - Test Migration Reversibility

**Purpose**: Test migrations by applying and rolling back in a test environment.

**Features**:
- Automated upgrade/downgrade testing
- Data integrity verification
- Performance benchmarking
- Test database creation/cleanup
- Schema comparison before/after
- Idempotency testing (run twice)
- Transaction rollback testing

**Usage**:
```bash
# Test latest migration
python test-migration.py

# Test specific migration
python test-migration.py -r abc123

# Test all pending migrations
python test-migration.py --all

# Test with performance benchmarking
python test-migration.py --benchmark

# Test with custom test database
python test-migration.py --test-db postgresql://localhost/test_db
```

**Options**:
- `-r, --revision REV` - Test specific revision
- `-a, --all` - Test all pending migrations
- `-b, --benchmark` - Measure migration performance
- `-t, --test-db URL` - Test database URL
- `-k, --keep-db` - Keep test database after testing
- `-v, --verbose` - Verbose output

**Test Phases**:
1. Create test database
2. Run upgrade migration
3. Verify schema changes
4. Run downgrade migration
5. Verify schema restored
6. Re-run upgrade (idempotency test)
7. Clean up test database

**Exit Codes**:
- `0` - All tests passed
- `1` - Tests failed
- `2` - Test setup error

---

### 7. `backup-database.sh` - Database Backup Before Migrations

**Purpose**: Create database backups with compression and verification.

**Features**:
- PostgreSQL (pg_dump) support
- MySQL (mysqldump) support
- SQLite file copy
- Compression (gzip, bzip2)
- Backup verification
- Retention policy
- Metadata tracking
- Restore capability

**Usage**:
```bash
# Backup PostgreSQL database
./backup-database.sh -d postgresql -u postgres://user:pass@localhost/db

# Backup with custom output directory
./backup-database.sh -d postgresql -o ./backups

# Backup with compression
./backup-database.sh -d mysql -c gzip

# Restore from backup
./backup-database.sh --restore ./backups/db_backup_20250131.sql.gz
```

**Options**:
- `-d, --database TYPE` - Database type (postgresql, mysql, sqlite)
- `-u, --url URL` - Database connection URL
- `-o, --output DIR` - Backup output directory (default: ./backups)
- `-c, --compress FORMAT` - Compression (gzip, bzip2, none)
- `-r, --restore FILE` - Restore from backup
- `-v, --verbose` - Verbose output

**Exit Codes**:
- `0` - Backup successful
- `1` - Backup failed
- `2` - Invalid configuration
- `3` - Verification failed

---

### 8. `migration-report.py` - Generate Migration Documentation

**Purpose**: Generate comprehensive documentation and reports for migrations.

**Features**:
- Migration timeline visualization
- Schema change summary
- Impact analysis
- Risk assessment
- HTML/Markdown reports
- Dependency graph
- Rollback plan generation

**Usage**:
```bash
# Generate HTML report
python migration-report.py -o migration-report.html

# Generate markdown documentation
python migration-report.py -f markdown -o MIGRATIONS.md

# Generate report for specific date range
python migration-report.py --from 2025-01-01 --to 2025-01-31

# Include risk assessment
python migration-report.py --risk-assessment -o report.html
```

**Options**:
- `-o, --output FILE` - Output report file
- `-f, --format FORMAT` - Report format (html, markdown, json)
- `--from DATE` - Start date (YYYY-MM-DD)
- `--to DATE` - End date (YYYY-MM-DD)
- `--risk-assessment` - Include risk analysis
- `-v, --verbose` - Verbose output

**Exit Codes**:
- `0` - Report generated
- `1` - Report generation failed

---

## Installation & Setup

### Prerequisites

Install required tools:

**Alembic and SQLAlchemy**:
```bash
pip install alembic sqlalchemy
```

**Database Drivers**:
```bash
# PostgreSQL
pip install psycopg2-binary

# MySQL
pip install mysqlclient

# SQLite (built-in with Python)
```

**Optional Tools**:
```bash
# For PostgreSQL backups
sudo apt-get install postgresql-client

# For MySQL backups
sudo apt-get install mysql-client

# For Python scripts
pip install jinja2 colorama click
```

### Make Scripts Executable

```bash
chmod +x init-alembic.sh
chmod +x generate-migration.sh
chmod +x run-migration.sh
chmod +x check-migration-status.sh
chmod +x backup-database.sh
chmod +x validate-migration.py
chmod +x test-migration.py
chmod +x migration-report.py
```

---

## Integration Examples

### CI/CD Integration (GitHub Actions)

```yaml
name: Database Migrations
on: [pull_request]

jobs:
  validate-migrations:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'

      - name: Install Dependencies
        run: pip install alembic sqlalchemy psycopg2-binary

      - name: Validate Migrations
        run: python scripts/validate-migration.py --all --strict

      - name: Test Migrations
        run: python scripts/test-migration.py --all --test-db postgresql://localhost/test_db

      - name: Generate Migration Report
        run: python scripts/migration-report.py -o migration-report.html

      - name: Upload Report
        uses: actions/upload-artifact@v3
        with:
          name: migration-report
          path: migration-report.html
```

### Pre-commit Hook

```bash
#!/bin/sh
# .git/hooks/pre-commit

echo "Validating migrations..."

# Validate new/modified migrations
python scripts/validate-migration.py --all --strict || exit 1

echo "Migration validation passed!"
```

### NPM Scripts Integration

```json
{
  "scripts": {
    "migrate": "./scripts/run-migration.sh upgrade head --backup",
    "migrate:dry-run": "./scripts/run-migration.sh upgrade head --dry-run",
    "migrate:down": "./scripts/run-migration.sh downgrade -1",
    "migrate:status": "./scripts/check-migration-status.sh",
    "migrate:validate": "python scripts/validate-migration.py --all",
    "migrate:test": "python scripts/test-migration.py --all",
    "migrate:backup": "./scripts/backup-database.sh -d postgresql"
  }
}
```

---

## Workflow Examples

### Complete Migration Workflow

```bash
# 1. Check current migration status
./check-migration-status.sh

# 2. Generate new migration
./generate-migration.sh -m "Add user authentication" --auto

# 3. Validate the migration
python validate-migration.py -f alembic/versions/xxx_add_user_authentication.py

# 4. Test migration in development
python test-migration.py -r xxx

# 5. Backup database before applying
./backup-database.sh -d postgresql

# 6. Run migration
./run-migration.sh upgrade head --backup

# 7. Verify migration status
./check-migration-status.sh --history

# 8. Generate documentation
python migration-report.py -o migration-report.html
```

### Production Deployment

```bash
# 1. Validate all migrations
python validate-migration.py --all --strict

# 2. Test migrations in staging
python test-migration.py --all --test-db $STAGING_DB_URL

# 3. Create production backup
./backup-database.sh -d postgresql -u $PROD_DB_URL -c gzip

# 4. Dry-run to review SQL
./run-migration.sh upgrade head --dry-run --env production

# 5. Execute migration with monitoring
./run-migration.sh upgrade head --env production --backup

# 6. Verify migration success
./check-migration-status.sh --verbose
```

### Rollback Procedure

```bash
# 1. Check current status
./check-migration-status.sh --history

# 2. Identify revision to rollback to
# (previous revision is shown in history)

# 3. Dry-run rollback
./run-migration.sh downgrade abc123 --dry-run

# 4. Execute rollback
./run-migration.sh downgrade abc123

# 5. Verify database state
./check-migration-status.sh
```

---

## Troubleshooting

### Common Issues

**"Alembic not initialized" errors**:
```bash
# Initialize Alembic
./init-alembic.sh -d postgresql -u <database_url>
```

**"Database connection failed"**:
- Check database URL in alembic.ini
- Verify database is running
- Check credentials and permissions

**"Migration already exists" errors**:
- Check for duplicate migration files
- Review migration history: `./check-migration-status.sh --history`
- Resolve branch conflicts

**"Downgrade not implemented"**:
- Migrations should have reversible downgrade()
- Use `validate-migration.py` to detect missing downgrades

**Permission denied**:
```bash
chmod +x scripts/*.sh
```

**Python import errors**:
```bash
# Ensure dependencies are installed
pip install alembic sqlalchemy psycopg2-binary jinja2 colorama
```

### Getting Help

Run any script with `-h` or `--help` flag:
```bash
./run-migration.sh --help
python validate-migration.py --help
```

---

## Best Practices

### Migration Development

1. **Always validate**: Run `validate-migration.py` on new migrations
2. **Test reversibility**: Use `test-migration.py` to ensure downgrades work
3. **Review autogenerated**: Manually review autogenerated migrations
4. **Backup before production**: Always backup before applying migrations
5. **Use dry-run**: Preview SQL with `--dry-run` before executing

### Production Deployments

1. **Validate first**: Run validation in strict mode
2. **Test in staging**: Apply migrations to staging environment first
3. **Create backups**: Always backup production database
4. **Monitor execution**: Watch for errors during migration
5. **Verify afterwards**: Check migration status and application health
6. **Have rollback plan**: Know how to rollback before deploying

### Team Collaboration

1. **Communicate changes**: Notify team about schema changes
2. **Review migrations**: Code review for all migration PRs
3. **Resolve conflicts early**: Check for migration branches
4. **Document complex migrations**: Add comments and documentation
5. **Coordinate deployments**: Align migration timing with app deployments

---

## Contributing

To add new scripts or improve existing ones:

1. Follow the existing script structure
2. Include comprehensive help documentation
3. Add examples in this README
4. Test with multiple databases (PostgreSQL, MySQL, SQLite)
5. Handle errors gracefully
6. Provide verbose logging options

---

## License

These scripts are part of the Database Migration skill package and follow the same license as the parent project.
