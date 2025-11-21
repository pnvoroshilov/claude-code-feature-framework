# Advanced Topics

Expert-level database migration techniques for production systems, large-scale deployments, and complex scenarios.

## Table of Contents

- [Zero-Downtime Deployments](#zero-downtime-deployments)
- [Large-Scale Data Migrations](#large-scale-data-migrations)
- [Concurrent Index Creation](#concurrent-index-creation)
- [Table Partitioning](#table-partitioning)
- [Multi-Tenant Migrations](#multi-tenant-migrations)
- [Cross-Database Patterns](#cross-database-patterns)
- [Custom Migration Commands](#custom-migration-commands)
- [Performance Optimization](#performance-optimization)
- [Disaster Recovery](#disaster-recovery)

## Zero-Downtime Deployments

### The Challenge

Traditional migrations require downtime:
```
1. Stop application
2. Run migration
3. Deploy new code
4. Start application
```

Zero-downtime requires backward compatibility at every step.

### Expand-Contract Pattern

**Phase 1: Expand** - Add new schema without breaking old code
```python
def upgrade():
    # Add new column (nullable)
    op.add_column('users', sa.Column('full_name', sa.String(200), nullable=True))
```

```python
# Application v1.5: Dual-write to both columns
user.name = "John Doe"  # Old column
user.full_name = "John Doe"  # New column (if exists)
```

**Phase 2: Migrate** - Backfill data
```python
def upgrade():
    # Backfill existing rows
    connection = op.get_bind()
    connection.execute(sa.text("""
        UPDATE users SET full_name = name WHERE full_name IS NULL
    """))
```

**Phase 3: Contract** - Remove old schema
```python
def upgrade():
    # Drop old column
    op.drop_column('users', 'name')
```

```python
# Application v2.0: Only use new column
user.full_name = "John Doe"
```

### Blue-Green Database Migrations

Maintain two database versions during migration:

**Setup**:
```python
# Blue database: current schema
# Green database: new schema

# Application reads from blue, writes to both
# After verification, switch reads to green
```

**Implementation**:
```python
class User(Base):
    __tablename__ = 'users'

    # Read from blue
    @classmethod
    def get_name(cls, user_id):
        if use_green_db():
            # Read from new schema
            return session.query(cls.full_name).filter_by(id=user_id).scalar()
        else:
            # Read from old schema
            return session.query(cls.name).filter_by(id=user_id).scalar()
```

## Large-Scale Data Migrations

### Batch Processing Strategy

```python
def upgrade():
    connection = op.get_bind()
    batch_size = 10000
    total_processed = 0

    # Get total count for progress tracking
    result = connection.execute(sa.text("SELECT COUNT(*) FROM users WHERE email IS NULL"))
    total_rows = result.scalar()

    print(f"Processing {total_rows} rows in batches of {batch_size}")

    while True:
        # Process batch
        result = connection.execute(sa.text(f"""
            WITH batch AS (
                SELECT id FROM users
                WHERE email IS NULL
                ORDER BY id
                LIMIT {batch_size}
            )
            UPDATE users
            SET email = username || '@migrated.com'
            WHERE id IN (SELECT id FROM batch)
        """))

        rows_updated = result.rowcount
        if rows_updated == 0:
            break

        total_processed += rows_updated
        progress = (total_processed / total_rows) * 100
        print(f"Progress: {total_processed}/{total_rows} ({progress:.1f}%)")

        connection.commit()  # Commit each batch

        # Optional: Rate limiting
        import time
        time.sleep(0.1)  # 100ms between batches
```

### Parallel Processing

```python
def upgrade():
    from concurrent.futures import ThreadPoolExecutor, as_completed

    connection = op.get_bind()

    # Partition data by ID ranges
    result = connection.execute(sa.text("SELECT MIN(id), MAX(id) FROM users"))
    min_id, max_id = result.fetchone()

    # Create chunks
    chunk_size = 100000
    chunks = []
    for start in range(min_id, max_id + 1, chunk_size):
        end = min(start + chunk_size - 1, max_id)
        chunks.append((start, end))

    def process_chunk(start_id, end_id):
        """Process a chunk of IDs"""
        # Create new connection for this thread
        engine = sa.create_engine(connection.engine.url)
        with engine.begin() as conn:
            conn.execute(sa.text(f"""
                UPDATE users
                SET email = username || '@migrated.com'
                WHERE id BETWEEN {start_id} AND {end_id}
                AND email IS NULL
            """))
        return end_id - start_id + 1

    # Process chunks in parallel
    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = {
            executor.submit(process_chunk, start, end): (start, end)
            for start, end in chunks
        }

        for future in as_completed(futures):
            start, end = futures[future]
            try:
                rows = future.result()
                print(f"Processed IDs {start}-{end} ({rows} rows)")
            except Exception as e:
                print(f"Error processing {start}-{end}: {e}")
                raise
```

### Progress Tracking Table

```python
def upgrade():
    # Create progress tracking
    op.create_table(
        'migration_tracking',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('migration_name', sa.String(100)),
        sa.Column('started_at', sa.DateTime(), server_default=sa.text('NOW()')),
        sa.Column('last_processed_id', sa.Integer()),
        sa.Column('total_processed', sa.Integer(), server_default='0'),
        sa.Column('completed_at', sa.DateTime()),
        sa.Column('status', sa.String(20))
    )

    connection = op.get_bind()

    # Log migration start
    connection.execute(sa.text("""
        INSERT INTO migration_tracking (migration_name, status)
        VALUES ('backfill_emails', 'running')
    """))

    # Perform migration with checkpoints
    batch_size = 5000
    last_id = 0

    while True:
        result = connection.execute(sa.text(f"""
            UPDATE users
            SET email = username || '@migrated.com'
            WHERE id > {last_id} AND email IS NULL
            AND id IN (
                SELECT id FROM users
                WHERE id > {last_id} AND email IS NULL
                ORDER BY id LIMIT {batch_size}
            )
            RETURNING id
        """))

        ids = [row[0] for row in result.fetchall()]
        if not ids:
            break

        last_id = max(ids)

        # Update progress
        connection.execute(sa.text(f"""
            UPDATE migration_tracking
            SET last_processed_id = {last_id},
                total_processed = total_processed + {len(ids)}
            WHERE migration_name = 'backfill_emails'
        """))

        connection.commit()

    # Mark complete
    connection.execute(sa.text("""
        UPDATE migration_tracking
        SET completed_at = NOW(), status = 'completed'
        WHERE migration_name = 'backfill_emails'
    """))

    # Cleanup
    op.drop_table('migration_tracking')
```

## Concurrent Index Creation

### PostgreSQL CONCURRENTLY

```python
def upgrade():
    # Must run outside transaction
    connection = op.get_bind()
    connection.execute('COMMIT')

    # Create index without blocking writes
    connection.execute("""
        CREATE INDEX CONCURRENTLY ix_users_email_lower
        ON users(LOWER(email))
    """)

def downgrade():
    connection = op.get_bind()
    connection.execute('COMMIT')
    connection.execute('DROP INDEX CONCURRENTLY ix_users_email_lower')
```

### Handling Concurrent Failures

```python
def upgrade():
    connection = op.get_bind()
    connection.execute('COMMIT')

    # Check if index already exists (from previous failed attempt)
    result = connection.execute(sa.text("""
        SELECT indexname FROM pg_indexes
        WHERE tablename = 'users' AND indexname = 'ix_users_email'
    """))

    if result.fetchone():
        print("Index already exists, skipping creation")
        return

    # Create index
    try:
        connection.execute("""
            CREATE INDEX CONCURRENTLY ix_users_email ON users(email)
        """)
    except Exception as e:
        print(f"Index creation failed: {e}")
        # Invalid indexes must be dropped before retry
        connection.execute("DROP INDEX IF EXISTS ix_users_email")
        raise
```

## Table Partitioning

### Range Partitioning by Date

```python
def upgrade():
    # Create partitioned table
    op.execute("""
        CREATE TABLE events (
            id BIGSERIAL,
            user_id INTEGER NOT NULL,
            event_type VARCHAR(50) NOT NULL,
            created_at TIMESTAMP NOT NULL,
            data JSONB
        ) PARTITION BY RANGE (created_at)
    """)

    # Create partitions for each month
    import datetime
    start_date = datetime.date(2024, 1, 1)
    for i in range(12):
        month = start_date.month + i
        year = start_date.year + (month - 1) // 12
        month = ((month - 1) % 12) + 1

        partition_name = f"events_y{year}m{month:02d}"
        start = f"{year}-{month:02d}-01"
        next_month = month % 12 + 1
        next_year = year if month < 12 else year + 1
        end = f"{next_year}-{next_month:02d}-01"

        op.execute(f"""
            CREATE TABLE {partition_name} PARTITION OF events
            FOR VALUES FROM ('{start}') TO ('{end}')
        """)

    # Create indexes on partitions
    op.create_index('ix_events_user_id', 'events', ['user_id'])
    op.create_index('ix_events_created_at', 'events', ['created_at'])

def downgrade():
    op.drop_table('events')  # Drops all partitions
```

### Migrating Existing Table to Partitioned

```python
def upgrade():
    # Step 1: Rename existing table
    op.rename_table('events', 'events_old')

    # Step 2: Create partitioned table
    op.execute("""
        CREATE TABLE events (
            id BIGINT PRIMARY KEY,
            user_id INTEGER NOT NULL,
            event_type VARCHAR(50) NOT NULL,
            created_at TIMESTAMP NOT NULL,
            data JSONB
        ) PARTITION BY RANGE (created_at)
    """)

    # Step 3: Create partitions (see above)

    # Step 4: Copy data in batches
    connection = op.get_bind()
    batch_size = 50000
    offset = 0

    while True:
        result = connection.execute(sa.text(f"""
            INSERT INTO events
            SELECT * FROM events_old
            ORDER BY id
            LIMIT {batch_size} OFFSET {offset}
        """))

        if result.rowcount == 0:
            break

        offset += batch_size
        print(f"Migrated {offset} events")

    # Step 5: Verify counts match
    result = connection.execute(sa.text("""
        SELECT
            (SELECT COUNT(*) FROM events) as new_count,
            (SELECT COUNT(*) FROM events_old) as old_count
    """))
    new_count, old_count = result.fetchone()

    if new_count != old_count:
        raise Exception(f"Count mismatch: {new_count} vs {old_count}")

    # Step 6: Drop old table
    op.drop_table('events_old')
```

## Multi-Tenant Migrations

### Schema-Per-Tenant Approach

```python
def upgrade():
    connection = op.get_bind()

    # Get all tenant schemas
    result = connection.execute(sa.text("""
        SELECT schema_name FROM information_schema.schemata
        WHERE schema_name LIKE 'tenant_%'
    """))
    tenant_schemas = [row[0] for row in result.fetchall()]

    # Apply migration to each tenant
    for schema in tenant_schemas:
        print(f"Migrating schema: {schema}")

        # Set search path to tenant schema
        connection.execute(sa.text(f"SET search_path TO {schema}"))

        # Run migration operations
        op.add_column(
            'users',
            sa.Column('email', sa.String(255)),
            schema=schema
        )

        # Reset search path
        connection.execute(sa.text("SET search_path TO public"))

def downgrade():
    connection = op.get_bind()
    result = connection.execute(sa.text("""
        SELECT schema_name FROM information_schema.schemata
        WHERE schema_name LIKE 'tenant_%'
    """))

    for schema in [row[0] for row in result.fetchall()]:
        connection.execute(sa.text(f"SET search_path TO {schema}"))
        op.drop_column('users', 'email', schema=schema)
        connection.execute(sa.text("SET search_path TO public"))
```

### Shared Schema with Tenant ID

```python
def upgrade():
    # Add tenant_id to existing table
    op.add_column('users', sa.Column('tenant_id', sa.Integer()))

    # Backfill tenant_id based on existing relationships
    connection = op.get_bind()
    connection.execute(sa.text("""
        UPDATE users u
        SET tenant_id = o.tenant_id
        FROM organizations o
        WHERE u.organization_id = o.id
    """))

    # Make tenant_id required
    op.alter_column('users', 'tenant_id', nullable=False)

    # Add composite index for tenant isolation
    op.create_index(
        'ix_users_tenant_id_id',
        'users',
        ['tenant_id', 'id']
    )

    # Add partial unique constraint per tenant
    op.create_unique_constraint(
        'uq_users_tenant_email',
        'users',
        ['tenant_id', 'email']
    )
```

## Cross-Database Patterns

### Database-Agnostic Migrations

```python
def upgrade():
    connection = op.get_bind()
    dialect = connection.dialect.name

    if dialect == 'postgresql':
        # PostgreSQL-specific: JSONB, arrays, full-text search
        op.add_column('users', sa.Column('preferences', sa.dialects.postgresql.JSONB()))
        op.execute("CREATE INDEX ix_users_preferences ON users USING GIN (preferences)")

    elif dialect == 'mysql':
        # MySQL-specific: JSON (not JSONB)
        op.add_column('users', sa.Column('preferences', sa.JSON()))
        # MySQL 5.7+ supports JSON indexes
        op.execute("ALTER TABLE users ADD INDEX ix_users_preferences ((CAST(preferences AS CHAR(255))))")

    elif dialect == 'sqlite':
        # SQLite: Use TEXT for JSON
        op.add_column('users', sa.Column('preferences', sa.Text()))
        # SQLite has limited JSON support

    else:
        raise Exception(f"Unsupported database: {dialect}")
```

### Migrating Between Database Systems

```python
def upgrade():
    """Migrate from MySQL to PostgreSQL"""
    import pymysql
    import psycopg2

    # Connect to both databases
    mysql_conn = pymysql.connect(host='old-db', user='root', password='***', db='myapp')
    pg_conn = psycopg2.connect(host='new-db', user='postgres', password='***', dbname='myapp')

    mysql_cur = mysql_conn.cursor()
    pg_cur = pg_conn.cursor()

    # Migrate data table by table
    tables = ['users', 'orders', 'products']

    for table in tables:
        print(f"Migrating {table}...")

        # Get data from MySQL
        mysql_cur.execute(f"SELECT * FROM {table}")
        rows = mysql_cur.fetchall()

        # Get column names
        mysql_cur.execute(f"DESCRIBE {table}")
        columns = [row[0] for row in mysql_cur.fetchall()]

        # Insert into PostgreSQL in batches
        batch_size = 1000
        for i in range(0, len(rows), batch_size):
            batch = rows[i:i+batch_size]
            placeholders = ','.join(['%s'] * len(columns))
            query = f"INSERT INTO {table} ({','.join(columns)}) VALUES ({placeholders})"

            pg_cur.executemany(query, batch)
            pg_conn.commit()

            print(f"  Migrated {i+len(batch)} rows")

    mysql_conn.close()
    pg_conn.close()
```

## Custom Migration Commands

### Custom Alembic Command

```python
# alembic/custom_commands.py
from alembic import op
import sqlalchemy as sa

def validate_migration():
    """Custom validation before migration"""
    connection = op.get_bind()

    # Check database size
    result = connection.execute(sa.text("""
        SELECT pg_size_pretty(pg_database_size(current_database()))
    """))
    db_size = result.scalar()
    print(f"Database size: {db_size}")

    # Check table sizes
    result = connection.execute(sa.text("""
        SELECT tablename, pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename))
        FROM pg_tables
        WHERE schemaname = 'public'
        ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC
        LIMIT 10
    """))

    print("Largest tables:")
    for table, size in result.fetchall():
        print(f"  {table}: {size}")
```

```python
# Use in migration
from alembic_custom_commands import validate_migration

def upgrade():
    validate_migration()

    # Proceed with migration
    op.add_column(...)
```

## Performance Optimization

### Analyze Query Plans

```python
def upgrade():
    connection = op.get_bind()

    # Create index
    op.create_index('ix_orders_user_id', 'orders', ['user_id'])

    # Analyze query performance
    result = connection.execute(sa.text("""
        EXPLAIN ANALYZE
        SELECT * FROM orders WHERE user_id = 123
    """))

    print("Query plan:")
    for row in result.fetchall():
        print(row[0])

    # Update statistics
    connection.execute(sa.text("ANALYZE orders"))
```

### Vacuum and Reindex

```python
def upgrade():
    connection = op.get_bind()

    # After large data migration, vacuum to reclaim space
    connection.execute('COMMIT')  # Exit transaction
    connection.execute('VACUUM ANALYZE users')

    # Reindex to rebuild indexes
    connection.execute('REINDEX TABLE users')
```

## Disaster Recovery

### Backup Before Migration

```python
def upgrade():
    """Always backup before risky migrations"""
    import subprocess
    import datetime

    timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_file = f"/backups/pre_migration_{timestamp}.sql"

    # PostgreSQL backup
    result = subprocess.run([
        'pg_dump',
        '-h', 'localhost',
        '-U', 'postgres',
        '-d', 'myapp',
        '-f', backup_file
    ], capture_output=True)

    if result.returncode != 0:
        raise Exception(f"Backup failed: {result.stderr.decode()}")

    print(f"Backup created: {backup_file}")

    # Proceed with migration
    op.add_column(...)
```

### Restore from Backup

```bash
# If migration fails, restore from backup
psql -h localhost -U postgres -d myapp < /backups/pre_migration_20250131_123456.sql
```

### Migration Rollback Safety

```python
def upgrade():
    connection = op.get_bind()

    # Create rollback savepoint
    connection.execute('SAVEPOINT before_risky_operation')

    try:
        # Risky operation
        connection.execute(sa.text("""
            UPDATE users SET email = LOWER(email)
        """))

        # Validate
        result = connection.execute(sa.text("""
            SELECT COUNT(*) FROM users WHERE email ~ '[A-Z]'
        """))
        if result.scalar() > 0:
            raise Exception("Uppercase emails still exist")

        connection.execute('RELEASE SAVEPOINT before_risky_operation')

    except Exception as e:
        print(f"Operation failed: {e}")
        connection.execute('ROLLBACK TO SAVEPOINT before_risky_operation')
        raise
```

## Next Steps

- See [troubleshooting.md](troubleshooting.md) for issue resolution
- Check [examples/advanced/](../examples/advanced/) for working code
- Review [resources/checklists.md](../resources/checklists.md) for pre-deployment checks
