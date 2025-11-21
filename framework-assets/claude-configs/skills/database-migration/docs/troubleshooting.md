# Troubleshooting

Common database migration issues, their root causes, and step-by-step solutions for recovery and prevention.

## Table of Contents

- [Failed Migration Recovery](#failed-migration-recovery)
- [Constraint Violations](#constraint-violations)
- [Deadlock Handling](#deadlock-handling)
- [Migration Conflicts](#migration-conflicts)
- [Slow Migrations](#slow-migrations)
- [Rollback Failures](#rollback-failures)
- [Data Loss Prevention](#data-loss-prevention)
- [Version Skew Problems](#version-skew-problems)
- [Environment Mismatches](#environment-mismatches)

## Failed Migration Recovery

### Symptom: Migration Fails Halfway

```
ERROR: column "email" of relation "users" already exists
Migration failed at step 3 of 5
```

### Root Cause

- Migration partially applied before error
- Alembic version table not updated
- Database in inconsistent state

### Solution

**Step 1**: Check current database state
```sql
-- Check which operations completed
SELECT column_name FROM information_schema.columns
WHERE table_name = 'users';

-- Check Alembic version
SELECT * FROM alembic_version;
```

**Step 2**: Identify what succeeded
```python
# Review migration file to see which operations ran
def upgrade():
    op.create_table('orders', ...)  # ✓ Succeeded
    op.add_column('users', ...)     # ✓ Succeeded
    op.create_index(...)            # ✗ Failed here
    op.create_foreign_key(...)      # Not executed
```

**Step 3**: Manual cleanup if needed
```sql
-- Drop partially created objects
DROP INDEX IF EXISTS ix_users_email;

-- Or complete the operation manually
CREATE INDEX ix_users_email ON users(email);
```

**Step 4**: Fix migration file
```python
def upgrade():
    # Add existence check
    connection = op.get_bind()
    result = connection.execute(sa.text("""
        SELECT column_name FROM information_schema.columns
        WHERE table_name = 'users' AND column_name = 'email'
    """))

    if not result.fetchone():
        op.add_column('users', sa.Column('email', sa.String(255)))
```

**Step 5**: Retry or mark as applied
```bash
# If fixed manually, mark migration as applied
alembic stamp head

# Or retry migration
alembic upgrade head
```

### Prevention

```python
# Make operations idempotent
def upgrade():
    # Check before creating
    if not table_exists('orders'):
        op.create_table('orders', ...)

    if not column_exists('users', 'email'):
        op.add_column('users', ...)

def table_exists(table_name):
    connection = op.get_bind()
    result = connection.execute(sa.text(f"""
        SELECT EXISTS (
            SELECT FROM information_schema.tables
            WHERE table_name = '{table_name}'
        )
    """))
    return result.scalar()

def column_exists(table_name, column_name):
    connection = op.get_bind()
    result = connection.execute(sa.text(f"""
        SELECT EXISTS (
            SELECT FROM information_schema.columns
            WHERE table_name = '{table_name}' AND column_name = '{column_name}'
        )
    """))
    return result.scalar()
```

## Constraint Violations

### Symptom: NOT NULL Constraint Fails

```
ERROR: column "email" contains null values
Cannot add NOT NULL constraint
```

### Root Cause

Existing data has NULL values in column.

### Solution

**Step 1**: Check NULL counts
```sql
SELECT COUNT(*) FROM users WHERE email IS NULL;
```

**Step 2**: Decide on backfill strategy
```python
def upgrade():
    # Option A: Set default value
    connection = op.get_bind()
    connection.execute(sa.text("""
        UPDATE users
        SET email = username || '@noemail.com'
        WHERE email IS NULL
    """))

    # Option B: Delete rows (if acceptable)
    connection.execute(sa.text("DELETE FROM users WHERE email IS NULL"))

    # Option C: Fail if NULLs exist
    result = connection.execute(sa.text("SELECT COUNT(*) FROM users WHERE email IS NULL"))
    if result.scalar() > 0:
        raise Exception("Cannot add NOT NULL: NULL values exist. Clean data first.")

    # Now safe to add constraint
    op.alter_column('users', 'email', nullable=False)
```

### Symptom: Unique Constraint Fails

```
ERROR: duplicate key value violates unique constraint "uq_users_email"
Key (email)=(john@example.com) already exists.
```

### Root Cause

Duplicate values exist in column.

### Solution

**Step 1**: Find duplicates
```sql
SELECT email, COUNT(*)
FROM users
GROUP BY email
HAVING COUNT(*) > 1;
```

**Step 2**: Resolve duplicates
```python
def upgrade():
    connection = op.get_bind()

    # Strategy: Keep oldest, suffix duplicates
    connection.execute(sa.text("""
        WITH ranked AS (
            SELECT id, email,
                   ROW_NUMBER() OVER (PARTITION BY email ORDER BY created_at) as rn
            FROM users
        )
        UPDATE users
        SET email = users.email || '_dup_' || ranked.id
        FROM ranked
        WHERE users.id = ranked.id AND ranked.rn > 1
    """))

    # Now safe to add unique constraint
    op.create_unique_constraint('uq_users_email', 'users', ['email'])
```

### Symptom: Foreign Key Violation

```
ERROR: insert or update on table "orders" violates foreign key constraint "fk_orders_user_id"
Key (user_id)=(999) is not present in table "users".
```

### Root Cause

Data references non-existent parent records.

### Solution

**Step 1**: Find orphaned records
```sql
SELECT COUNT(*)
FROM orders o
LEFT JOIN users u ON o.user_id = u.id
WHERE o.user_id IS NOT NULL AND u.id IS NULL;
```

**Step 2**: Clean up orphans
```python
def upgrade():
    connection = op.get_bind()

    # Option A: Delete orphaned orders
    connection.execute(sa.text("""
        DELETE FROM orders
        WHERE user_id NOT IN (SELECT id FROM users)
    """))

    # Option B: Set orphaned references to NULL
    op.alter_column('orders', 'user_id', nullable=True)
    connection.execute(sa.text("""
        UPDATE orders SET user_id = NULL
        WHERE user_id NOT IN (SELECT id FROM users)
    """))

    # Now add foreign key
    op.create_foreign_key('fk_orders_user_id', 'orders', 'users', ['user_id'], ['id'])
```

## Deadlock Handling

### Symptom: Migration Times Out or Deadlocks

```
ERROR: deadlock detected
Process 12345 waits for AccessExclusiveLock on relation "users"
Process 67890 waits for RowExclusiveLock on relation "users"
```

### Root Cause

- Migration holds locks that conflict with application queries
- Multiple migrations running simultaneously
- Long-running transactions

### Solution

**Step 1**: Stop conflicting processes
```sql
-- Find blocking queries
SELECT pid, query, state, wait_event_type
FROM pg_stat_activity
WHERE state != 'idle' AND query NOT LIKE '%pg_stat_activity%';

-- Terminate if necessary
SELECT pg_terminate_backend(12345);
```

**Step 2**: Use shorter transactions
```python
def upgrade():
    # Bad: Long transaction
    connection = op.get_bind()
    connection.execute(sa.text("UPDATE users SET status = 'active'"))  # Locks entire table

    # Good: Batch with commits
    batch_size = 1000
    offset = 0

    while True:
        result = connection.execute(sa.text(f"""
            UPDATE users SET status = 'active'
            WHERE id IN (
                SELECT id FROM users WHERE status IS NULL
                ORDER BY id LIMIT {batch_size}
            )
        """))

        if result.rowcount == 0:
            break

        connection.commit()  # Release locks between batches
```

**Step 3**: Use lock timeouts
```python
def upgrade():
    connection = op.get_bind()

    # Set statement timeout
    connection.execute(sa.text("SET statement_timeout = '30s'"))

    # Set lock timeout (fail fast if can't acquire lock)
    connection.execute(sa.text("SET lock_timeout = '5s'"))

    try:
        op.add_column('users', sa.Column('email', sa.String(255)))
    except Exception as e:
        print(f"Failed to acquire lock: {e}")
        print("Retry during low-traffic period")
        raise
```

### Prevention

- Run migrations during maintenance windows
- Use CONCURRENTLY for index creation
- Break large migrations into smaller batches
- Monitor lock waits during migration

## Migration Conflicts

### Symptom: Branched Migration History

```
ERROR: Multiple head revisions found
  abc123 (branch 1)
  def456 (branch 2)
```

### Root Cause

Two developers created migrations with same parent revision.

### Solution

**Step 1**: Identify branches
```bash
$ alembic branches
abc123 -> None (branch 1)
def456 -> None (branch 2)
```

**Step 2**: Create merge migration
```bash
$ alembic merge -m "merge parallel migrations" abc123 def456
```

This creates:
```python
"""merge parallel migrations

Revision ID: ghi789
Revises: abc123, def456
Create Date: 2025-01-31 10:30:00
"""

revision = 'ghi789'
down_revision = ('abc123', 'def456')  # Both parents

def upgrade():
    pass  # No operations needed for simple merge

def downgrade():
    pass
```

**Step 3**: Test merge migration
```bash
$ alembic upgrade head
```

### Prevention

- Pull latest changes before creating migrations
- Communicate about schema changes
- Use feature branches
- Resolve conflicts quickly

## Slow Migrations

### Symptom: Migration Takes Hours

```
Migrating 10 million rows...
Still running after 2 hours...
```

### Root Cause

- Operating on entire table at once
- Missing indexes for data migration queries
- Full table scans

### Solution

**Step 1**: Analyze slow queries
```sql
-- PostgreSQL: Enable slow query logging
ALTER SYSTEM SET log_min_duration_statement = 1000;  -- Log queries > 1s
SELECT pg_reload_conf();

-- Check slow queries during migration
SELECT query, mean_exec_time, calls
FROM pg_stat_statements
ORDER BY mean_exec_time DESC
LIMIT 10;
```

**Step 2**: Add temporary indexes
```python
def upgrade():
    # Add temporary index to speed up migration
    op.create_index('tmp_ix_users_old_email', 'users', ['old_email'])

    # Perform data migration (now faster)
    connection = op.get_bind()
    connection.execute(sa.text("""
        UPDATE users
        SET email = LOWER(old_email)
        WHERE email IS NULL
    """))

    # Drop temporary index
    op.drop_index('tmp_ix_users_old_email')
```

**Step 3**: Batch processing
```python
def upgrade():
    connection = op.get_bind()
    batch_size = 10000

    while True:
        result = connection.execute(sa.text(f"""
            WITH batch AS (
                SELECT id FROM users WHERE email IS NULL
                ORDER BY id LIMIT {batch_size}
            )
            UPDATE users
            SET email = LOWER(old_email)
            WHERE id IN (SELECT id FROM batch)
        """))

        if result.rowcount == 0:
            break

        connection.commit()
```

**Step 4**: Parallel processing
```python
def upgrade():
    from concurrent.futures import ThreadPoolExecutor

    # Split table into chunks by ID ranges
    connection = op.get_bind()
    result = connection.execute(sa.text("SELECT MIN(id), MAX(id) FROM users"))
    min_id, max_id = result.fetchone()

    chunk_size = 100000
    chunks = range(min_id, max_id + 1, chunk_size)

    def process_chunk(start_id):
        end_id = start_id + chunk_size
        engine = sa.create_engine(connection.engine.url)
        with engine.begin() as conn:
            conn.execute(sa.text(f"""
                UPDATE users
                SET email = LOWER(old_email)
                WHERE id >= {start_id} AND id < {end_id}
            """))

    # Process 4 chunks in parallel
    with ThreadPoolExecutor(max_workers=4) as executor:
        executor.map(process_chunk, chunks)
```

## Rollback Failures

### Symptom: Downgrade Fails

```
ERROR: Cannot drop column "email" because other objects depend on it
Detail: constraint fk_orders_email depends on column users.email
```

### Root Cause

Downgrade operations not in correct order.

### Solution

**Step 1**: Fix downgrade order
```python
def upgrade():
    op.add_column('users', sa.Column('email', sa.String(255)))
    op.create_index('ix_users_email', 'users', ['email'])
    op.create_foreign_key('fk_orders_email', 'orders', 'users', ['user_email'], ['email'])

def downgrade():
    # Reverse order: drop FK, then index, then column
    op.drop_constraint('fk_orders_email', 'orders')
    op.drop_index('ix_users_email')
    op.drop_column('users', 'email')
```

**Step 2**: Handle irreversible operations
```python
def downgrade():
    # Some operations can't be truly reversed
    raise NotImplementedError(
        "This migration cannot be reversed without data loss. "
        "Restore from backup if rollback is necessary."
    )
```

**Step 3**: Best-effort downgrade
```python
def downgrade():
    """
    Partial downgrade: Restores schema but loses data.
    """
    # Can restore column structure but not data
    op.add_column('users', sa.Column('old_field', sa.String(100)))
    # Data is lost - document this clearly
```

## Data Loss Prevention

### Symptom: Accidentally Deleted Data

```
ERROR: Oops, dropped wrong column!
1 million user emails just deleted!
```

### Prevention

**Always backup before risky operations**:
```python
def upgrade():
    # Create backup table first
    op.execute("CREATE TABLE users_backup_20250131 AS SELECT * FROM users")

    # Perform risky operation
    op.drop_column('users', 'old_email')

    # Keep backup for 30 days, then:
    # DROP TABLE users_backup_20250131;
```

**Use soft deletes**:
```python
def upgrade():
    # Instead of dropping column, rename it
    op.alter_column('users', 'old_field', new_column_name='deprecated_old_field_backup')

    # Drop it later after verification period
```

**Test on copy first**:
```bash
# Create database copy
createdb myapp_migration_test --template myapp_prod

# Test migration on copy
SQLALCHEMY_URL=postgresql://localhost/myapp_migration_test alembic upgrade head

# Verify results
psql myapp_migration_test

# If successful, run on production
```

## Version Skew Problems

### Symptom: Application and Database Out of Sync

```
ERROR: relation "users.new_column" does not exist
Application expects column that doesn't exist yet
```

### Root Cause

Application deployed before migration, or vice versa.

### Solution

**Use backward-compatible migrations**:
```python
# Phase 1: Add column (nullable)
def upgrade():
    op.add_column('users', sa.Column('email', sa.String(255), nullable=True))

# Deploy app that handles both NULL and populated email
# Then run phase 2

# Phase 2: Backfill data
def upgrade():
    connection = op.get_bind()
    connection.execute(sa.text("UPDATE users SET email = username || '@example.com' WHERE email IS NULL"))

# Phase 3: Make required
def upgrade():
    op.alter_column('users', 'email', nullable=False)
```

**Coordinate deployments**:
```
1. Deploy backward-compatible schema change
2. Deploy new application version
3. Deploy forward-only schema change
```

## Environment Mismatches

### Symptom: Migration Works Locally But Fails in Production

```
Local: SUCCESS
Staging: SUCCESS
Production: ERROR: relation already exists
```

### Root Cause

- Production schema differs from expected state
- Previous manual changes not tracked
- Migration history diverged

### Solution

**Step 1**: Compare schemas
```bash
# Export schemas
pg_dump --schema-only myapp_local > schema_local.sql
pg_dump --schema-only myapp_prod > schema_prod.sql

# Compare
diff schema_local.sql schema_prod.sql
```

**Step 2**: Align schemas
```python
def upgrade():
    # Check environment state
    connection = op.get_bind()

    # Skip if already applied
    result = connection.execute(sa.text("""
        SELECT EXISTS (
            SELECT FROM information_schema.columns
            WHERE table_name = 'users' AND column_name = 'email'
        )
    """))

    if result.scalar():
        print("Column already exists, skipping")
        return

    op.add_column('users', sa.Column('email', sa.String(255)))
```

**Step 3**: Stamp migration history
```bash
# If manual changes were made, mark migrations as applied
alembic stamp head

# Or specific revision
alembic stamp abc123
```

### Prevention

- Never make manual schema changes in production
- Use migrations exclusively
- Keep all environments in sync
- Test migrations in staging first

## Next Steps

- Review [best-practices.md](best-practices.md) to avoid these issues
- Check [advanced-topics.md](advanced-topics.md) for recovery strategies
- Use [resources/checklists.md](../resources/checklists.md) for pre-deployment validation
