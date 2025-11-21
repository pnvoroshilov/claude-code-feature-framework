# Patterns

Common migration patterns, anti-patterns, and real-world scenarios you'll encounter in database schema evolution. Learn what works, what doesn't, and when to use each approach.

## Table of Contents

- [Adding Columns](#adding-columns)
- [Dropping Columns](#dropping-columns)
- [Renaming Columns](#renaming-columns)
- [Changing Column Types](#changing-column-types)
- [Adding Constraints](#adding-constraints)
- [Enum Type Migrations](#enum-type-migrations)
- [Table Splitting](#table-splitting)
- [Table Merging](#table-merging)
- [Multi-Phase Migrations](#multi-phase-migrations)
- [Data Backfill](#data-backfill)
- [Anti-Patterns to Avoid](#anti-patterns-to-avoid)

## Adding Columns

### Pattern: Add Nullable Column

**Scenario**: Add new column without affecting existing data.

```python
def upgrade():
    op.add_column(
        'users',
        sa.Column('phone_number', sa.String(20), nullable=True)
    )

def downgrade():
    op.drop_column('users', 'phone_number')
```

**When to use**: New optional field, no data migration needed.

**Pros**:
- ✅ Safe for existing data
- ✅ Zero downtime
- ✅ Fully reversible

**Cons**:
- ❌ Allows NULL values (may need cleanup later)

### Pattern: Add Column with Default Value

**Scenario**: Add new column with a default value for existing rows.

```python
def upgrade():
    # PostgreSQL: Use server_default for instant default
    op.add_column(
        'users',
        sa.Column(
            'status',
            sa.String(20),
            nullable=False,
            server_default='active'
        )
    )

    # Optional: Remove server_default after initial population
    op.alter_column('users', 'status', server_default=None)

def downgrade():
    op.drop_column('users', 'status')
```

**When to use**: New required field with sensible default.

**Pros**:
- ✅ Existing rows immediately have valid value
- ✅ Zero downtime
- ✅ Enforces NOT NULL from start

**Cons**:
- ❌ Default value is permanent unless explicitly changed
- ❌ All existing rows get same value (may not be semantically correct)

### Pattern: Add Column in Phases

**Scenario**: Add column that will be required, but can't have default.

**Phase 1**: Add nullable column
```python
def upgrade():
    op.add_column('users', sa.Column('email', sa.String(255), nullable=True))
    op.create_index('ix_users_email', 'users', ['email'])

def downgrade():
    op.drop_index('ix_users_email')
    op.drop_column('users', 'email')
```

**Phase 2** (separate deployment): Application populates email
```python
# Application code prompts users for email
# or backfill from external source
```

**Phase 3**: Make column required
```python
def upgrade():
    # Verify all rows have email
    connection = op.get_bind()
    result = connection.execute(sa.text(
        "SELECT COUNT(*) FROM users WHERE email IS NULL"
    ))
    null_count = result.scalar()

    if null_count > 0:
        raise Exception(f"{null_count} users still have NULL email. Backfill first.")

    # Safe to make NOT NULL
    op.alter_column('users', 'email', nullable=False)

def downgrade():
    op.alter_column('users', 'email', nullable=True)
```

**When to use**: Column will be required but values must come from users/external sources.

### Pattern: Add Column with Index

```python
def upgrade():
    # Add column
    op.add_column('users', sa.Column('email', sa.String(255), nullable=True))

    # Add unique index
    op.create_index(
        'ix_users_email_unique',
        'users',
        ['email'],
        unique=True
    )

def downgrade():
    op.drop_index('ix_users_email_unique')
    op.drop_column('users', 'email')
```

**PostgreSQL**: Use CONCURRENTLY for large tables
```python
def upgrade():
    # Add column
    op.add_column('users', sa.Column('email', sa.String(255)))

    # Exit transaction for CONCURRENTLY
    connection = op.get_bind()
    connection.execute('COMMIT')

    # Create index without blocking writes
    connection.execute(
        'CREATE UNIQUE INDEX CONCURRENTLY ix_users_email ON users(email)'
    )

def downgrade():
    connection = op.get_bind()
    connection.execute('COMMIT')
    connection.execute('DROP INDEX CONCURRENTLY ix_users_email')
    op.drop_column('users', 'email')
```

## Dropping Columns

### Pattern: Simple Column Drop

**Scenario**: Remove unused column.

```python
def upgrade():
    op.drop_column('users', 'old_field')

def downgrade():
    # Can recreate column structure but not data
    op.add_column('users', sa.Column('old_field', sa.String(100)))
```

**When to use**: Column definitely not used.

**Warning**: Irreversible data loss.

### Pattern: Phased Column Removal

**Scenario**: Remove column safely in production.

**Phase 1**: Stop application from using column
```python
# Deploy application v2.0 that doesn't reference old_field
# But column still exists in database
```

**Phase 2**: Verify column not used
```python
# Monitor production for 24-48 hours
# Confirm no errors, no read/write to old_field
```

**Phase 3**: Drop column
```python
def upgrade():
    op.drop_column('users', 'old_field')

def downgrade():
    # Can restore structure from backup if needed
    raise NotImplementedError(
        "Column drop is irreversible. Restore from backup if needed."
    )
```

**When to use**: Production systems where safety is critical.

### Pattern: Soft Delete Column

**Scenario**: Remove column but preserve ability to recover.

**Phase 1**: Rename column (don't drop yet)
```python
def upgrade():
    op.alter_column(
        'users',
        'old_field',
        new_column_name='deprecated_old_field_backup'
    )

def downgrade():
    op.alter_column(
        'users',
        'deprecated_old_field_backup',
        new_column_name='old_field'
    )
```

**Phase 2** (weeks later, after confirmed not needed): Actually drop
```python
def upgrade():
    op.drop_column('users', 'deprecated_old_field_backup')

def downgrade():
    raise NotImplementedError("Cannot restore deleted column")
```

## Renaming Columns

### Pattern: Rename Column (Simple)

**Scenario**: Rename for clarity or consistency.

```python
def upgrade():
    op.alter_column('users', 'name', new_column_name='full_name')

def downgrade():
    op.alter_column('users', 'full_name', new_column_name='name')
```

**When to use**: Small applications, coordinated deployments.

**Pros**:
- ✅ Preserves all data
- ✅ Fully reversible
- ✅ Fast operation

**Cons**:
- ❌ Requires application code update simultaneously
- ❌ Can cause downtime if not coordinated

### Pattern: Zero-Downtime Rename

**Scenario**: Rename column in production without downtime.

**Phase 1**: Add new column, dual-write
```python
def upgrade():
    # Add new column
    op.add_column('users', sa.Column('full_name', sa.String(200)))

    # Copy existing data
    connection = op.get_bind()
    connection.execute(sa.text("UPDATE users SET full_name = name"))

def downgrade():
    op.drop_column('users', 'full_name')
```

```python
# Application v2.0: Write to BOTH columns
user.name = "John Doe"
user.full_name = "John Doe"
```

**Phase 2**: Switch reads to new column
```python
# Application v2.1: Read from full_name, write to both
display_name = user.full_name
user.name = new_name  # Still writing to old column
user.full_name = new_name
```

**Phase 3**: Drop old column
```python
def upgrade():
    op.drop_column('users', 'name')

def downgrade():
    op.add_column('users', sa.Column('name', sa.String(200)))
    connection = op.get_bind()
    connection.execute(sa.text("UPDATE users SET name = full_name"))
```

```python
# Application v2.2: Only use full_name
display_name = user.full_name
user.full_name = new_name
```

**When to use**: High-availability production systems.

## Changing Column Types

### Pattern: Expand String Length

**Scenario**: Increase VARCHAR limit.

**PostgreSQL** (safe in PG 9.2+):
```python
def upgrade():
    # No table rewrite in PostgreSQL
    op.alter_column(
        'users',
        'email',
        type_=sa.String(500),  # Was String(255)
        existing_type=sa.String(255)
    )

def downgrade():
    # Check no data truncation would occur
    connection = op.get_bind()
    result = connection.execute(sa.text("""
        SELECT COUNT(*) FROM users WHERE LENGTH(email) > 255
    """))
    if result.scalar() > 0:
        raise Exception("Cannot downgrade: some emails exceed 255 chars")

    op.alter_column(
        'users',
        'email',
        type_=sa.String(255),
        existing_type=sa.String(500)
    )
```

**When to use**: Need more space, new limit accommodates all data.

### Pattern: Change Column Type with Casting

**Scenario**: Convert compatible types (e.g., string to integer).

```python
def upgrade():
    # PostgreSQL: USING clause for conversion
    op.alter_column(
        'users',
        'age',
        type_=sa.Integer(),
        existing_type=sa.String(10),
        postgresql_using='age::integer'
    )

def downgrade():
    op.alter_column(
        'users',
        'age',
        type_=sa.String(10),
        existing_type=sa.Integer(),
        postgresql_using='age::varchar'
    )
```

**When to use**: All existing data is valid for new type.

### Pattern: Change Type with Validation

**Scenario**: Convert types but some data might be invalid.

```python
def upgrade():
    # Phase 1: Add new column
    op.add_column('users', sa.Column('age_int', sa.Integer()))

    # Phase 2: Convert valid data
    connection = op.get_bind()
    connection.execute(sa.text("""
        UPDATE users
        SET age_int = CAST(age AS INTEGER)
        WHERE age ~ '^[0-9]+$'
    """))

    # Phase 3: Handle invalid data
    connection.execute(sa.text("""
        UPDATE users
        SET age_int = NULL
        WHERE age !~ '^[0-9]+$'
    """))

    # Phase 4: Log invalid conversions
    result = connection.execute(sa.text("""
        SELECT id, age FROM users WHERE age_int IS NULL
    """))
    invalid = result.fetchall()
    if invalid:
        print(f"Warning: {len(invalid)} invalid age values set to NULL")

    # Phase 5: Drop old column, rename new
    op.drop_column('users', 'age')
    op.alter_column('users', 'age_int', new_column_name='age')

def downgrade():
    op.alter_column('users', 'age', new_column_name='age_int')
    op.add_column('users', sa.Column('age', sa.String(10)))
    connection = op.get_bind()
    connection.execute(sa.text("UPDATE users SET age = CAST(age_int AS VARCHAR)"))
    op.drop_column('users', 'age_int')
```

## Adding Constraints

### Pattern: Add NOT NULL to Existing Column

**Scenario**: Make optional column required.

```python
def upgrade():
    # Step 1: Verify no NULL values exist
    connection = op.get_bind()
    result = connection.execute(sa.text(
        "SELECT COUNT(*) FROM users WHERE email IS NULL"
    ))
    null_count = result.scalar()

    if null_count > 0:
        raise Exception(
            f"{null_count} rows have NULL email. "
            "Backfill required before adding NOT NULL constraint."
        )

    # Step 2: Add constraint
    op.alter_column('users', 'email', nullable=False)

def downgrade():
    op.alter_column('users', 'email', nullable=True)
```

**Safe approach** (with backfill):
```python
def upgrade():
    # Backfill NULL values with placeholder
    connection = op.get_bind()
    connection.execute(sa.text("""
        UPDATE users
        SET email = 'noemail_' || id || '@example.com'
        WHERE email IS NULL
    """))

    # Now safe to add constraint
    op.alter_column('users', 'email', nullable=False)
```

### Pattern: Add Unique Constraint

**Scenario**: Enforce uniqueness on column.

```python
def upgrade():
    # Step 1: Check for duplicates
    connection = op.get_bind()
    result = connection.execute(sa.text("""
        SELECT email, COUNT(*)
        FROM users
        GROUP BY email
        HAVING COUNT(*) > 1
    """))
    duplicates = result.fetchall()

    if duplicates:
        raise Exception(
            f"Cannot add unique constraint: {len(duplicates)} duplicate emails found. "
            "Deduplicate first."
        )

    # Step 2: Add unique constraint
    op.create_unique_constraint('uq_users_email', 'users', ['email'])

def downgrade():
    op.drop_constraint('uq_users_email', 'users')
```

**With duplicate handling**:
```python
def upgrade():
    # Deduplicate by keeping oldest user
    connection = op.get_bind()
    connection.execute(sa.text("""
        WITH duplicates AS (
            SELECT id, email,
                   ROW_NUMBER() OVER (PARTITION BY email ORDER BY created_at) as rn
            FROM users
            WHERE email IS NOT NULL
        )
        UPDATE users
        SET email = email || '_duplicate_' || id
        WHERE id IN (SELECT id FROM duplicates WHERE rn > 1)
    """))

    # Now add constraint
    op.create_unique_constraint('uq_users_email', 'users', ['email'])
```

### Pattern: Add Foreign Key Constraint

**Scenario**: Enforce referential integrity.

```python
def upgrade():
    # Verify all references are valid
    connection = op.get_bind()
    result = connection.execute(sa.text("""
        SELECT COUNT(*)
        FROM orders o
        LEFT JOIN users u ON o.user_id = u.id
        WHERE o.user_id IS NOT NULL AND u.id IS NULL
    """))
    invalid_refs = result.scalar()

    if invalid_refs > 0:
        raise Exception(
            f"{invalid_refs} orders reference non-existent users. "
            "Fix data before adding foreign key."
        )

    # Add foreign key
    op.create_foreign_key(
        'fk_orders_user_id',
        'orders', 'users',
        ['user_id'], ['id'],
        ondelete='CASCADE'
    )

def downgrade():
    op.drop_constraint('fk_orders_user_id', 'orders')
```

### Pattern: Add Check Constraint

**Scenario**: Enforce data validation rules.

```python
def upgrade():
    # Verify existing data satisfies constraint
    connection = op.get_bind()
    result = connection.execute(sa.text("""
        SELECT COUNT(*) FROM users
        WHERE age < 0 OR age > 150
    """))
    invalid = result.scalar()

    if invalid > 0:
        # Fix invalid data
        connection.execute(sa.text("""
            UPDATE users
            SET age = NULL
            WHERE age < 0 OR age > 150
        """))
        print(f"Warning: Set {invalid} invalid ages to NULL")

    # Add check constraint
    op.create_check_constraint(
        'ck_users_age_valid',
        'users',
        'age >= 0 AND age <= 150'
    )

def downgrade():
    op.drop_constraint('ck_users_age_valid', 'users')
```

## Enum Type Migrations

### Pattern: Create Enum Type

**PostgreSQL**:
```python
def upgrade():
    # Create enum type
    status_enum = sa.Enum(
        'pending', 'active', 'inactive', 'banned',
        name='user_status'
    )
    status_enum.create(op.get_bind())

    # Add column using enum
    op.add_column(
        'users',
        sa.Column('status', status_enum, nullable=False, server_default='pending')
    )

def downgrade():
    op.drop_column('users', 'status')
    # Drop enum type
    sa.Enum(name='user_status').drop(op.get_bind())
```

### Pattern: Add Value to Enum

**PostgreSQL**:
```python
def upgrade():
    # Add new enum value
    op.execute("ALTER TYPE user_status ADD VALUE 'suspended'")

def downgrade():
    # Cannot remove enum value easily in PostgreSQL
    # Need to recreate enum type
    raise NotImplementedError(
        "Cannot remove enum value. "
        "Requires recreating enum type and updating all columns."
    )
```

### Pattern: Modify Enum Values

**Scenario**: Change enum values (e.g., rename).

```python
def upgrade():
    # Create new enum with updated values
    op.execute("""
        CREATE TYPE user_status_new AS ENUM (
            'active', 'inactive', 'suspended', 'deleted'
        )
    """)

    # Convert column to new enum
    op.execute("""
        ALTER TABLE users
        ALTER COLUMN status TYPE user_status_new
        USING status::text::user_status_new
    """)

    # Drop old enum
    op.execute("DROP TYPE user_status")

    # Rename new enum
    op.execute("ALTER TYPE user_status_new RENAME TO user_status")

def downgrade():
    # Reverse process
    op.execute("""
        CREATE TYPE user_status_old AS ENUM (
            'pending', 'active', 'inactive', 'banned'
        )
    """)

    op.execute("""
        ALTER TABLE users
        ALTER COLUMN status TYPE user_status_old
        USING status::text::user_status_old
    """)

    op.execute("DROP TYPE user_status")
    op.execute("ALTER TYPE user_status_old RENAME TO user_status")
```

## Table Splitting

### Pattern: Vertical Split (Columns to New Table)

**Scenario**: Move rarely-used columns to separate table.

```python
def upgrade():
    # Create new table for extended info
    op.create_table(
        'user_profiles',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id'), unique=True),
        sa.Column('bio', sa.Text()),
        sa.Column('avatar_url', sa.String(500)),
        sa.Column('preferences', sa.JSON())
    )

    # Copy data from users to user_profiles
    connection = op.get_bind()
    connection.execute(sa.text("""
        INSERT INTO user_profiles (user_id, bio, avatar_url, preferences)
        SELECT id, bio, avatar_url, preferences
        FROM users
    """))

    # Drop columns from users table
    op.drop_column('users', 'preferences')
    op.drop_column('users', 'avatar_url')
    op.drop_column('users', 'bio')

def downgrade():
    # Add columns back to users
    op.add_column('users', sa.Column('bio', sa.Text()))
    op.add_column('users', sa.Column('avatar_url', sa.String(500)))
    op.add_column('users', sa.Column('preferences', sa.JSON()))

    # Copy data back
    connection = op.get_bind()
    connection.execute(sa.text("""
        UPDATE users u
        SET bio = p.bio,
            avatar_url = p.avatar_url,
            preferences = p.preferences
        FROM user_profiles p
        WHERE u.id = p.user_id
    """))

    # Drop profiles table
    op.drop_table('user_profiles')
```

## Table Merging

### Pattern: Merge Two Tables

**Scenario**: Combine related tables into one.

```python
def upgrade():
    # Add columns from profiles to users
    op.add_column('users', sa.Column('bio', sa.Text()))
    op.add_column('users', sa.Column('avatar_url', sa.String(500)))

    # Copy data
    connection = op.get_bind()
    connection.execute(sa.text("""
        UPDATE users u
        SET bio = p.bio,
            avatar_url = p.avatar_url
        FROM profiles p
        WHERE u.id = p.user_id
    """))

    # Drop old table
    op.drop_table('profiles')

def downgrade():
    # Recreate profiles table
    op.create_table(
        'profiles',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id')),
        sa.Column('bio', sa.Text()),
        sa.Column('avatar_url', sa.String(500))
    )

    # Copy data back
    connection = op.get_bind()
    connection.execute(sa.text("""
        INSERT INTO profiles (user_id, bio, avatar_url)
        SELECT id, bio, avatar_url
        FROM users
    """))

    # Remove merged columns
    op.drop_column('users', 'avatar_url')
    op.drop_column('users', 'bio')
```

## Multi-Phase Migrations

### Pattern: Three-Phase Deployment

**Scenario**: Add required column with zero downtime.

**Phase 1**: Add column (nullable)
```python
def upgrade():
    op.add_column('users', sa.Column('email', sa.String(255), nullable=True))
    op.create_index('ix_users_email', 'users', ['email'])
```

**Application v1.5**: Start writing email (dual-write)
```python
# Old code path still works with email=NULL
# New code path writes email
```

**Phase 2**: Backfill existing data
```python
def upgrade():
    connection = op.get_bind()

    # Backfill in batches
    batch_size = 1000
    offset = 0

    while True:
        result = connection.execute(sa.text(f"""
            UPDATE users
            SET email = username || '@legacy.com'
            WHERE email IS NULL
            AND id > {offset}
            LIMIT {batch_size}
        """))

        if result.rowcount == 0:
            break

        offset += batch_size
```

**Phase 3**: Make column required
```python
def upgrade():
    op.alter_column('users', 'email', nullable=False)
```

**Application v2.0**: Email is now required
```python
# All code paths require email
```

## Data Backfill

### Pattern: Batch Processing

**Scenario**: Update millions of rows without locking.

```python
def upgrade():
    connection = op.get_bind()
    batch_size = 5000
    total_processed = 0

    while True:
        # Process in batches
        result = connection.execute(sa.text(f"""
            WITH batch AS (
                SELECT id FROM users
                WHERE full_name IS NULL
                ORDER BY id
                LIMIT {batch_size}
            )
            UPDATE users
            SET full_name = first_name || ' ' || last_name
            WHERE id IN (SELECT id FROM batch)
        """))

        rows_updated = result.rowcount
        total_processed += rows_updated

        if rows_updated == 0:
            break

        print(f"Processed {total_processed} rows...")

        # Optional: Add small delay to reduce database load
        # import time
        # time.sleep(0.1)
```

### Pattern: Resumable Backfill

**Scenario**: Long-running backfill that can be interrupted and resumed.

```python
def upgrade():
    connection = op.get_bind()

    # Track progress
    op.create_table(
        'migration_progress',
        sa.Column('migration_name', sa.String(100), primary_key=True),
        sa.Column('last_processed_id', sa.Integer()),
        sa.Column('updated_at', sa.DateTime())
    )

    # Get last checkpoint
    result = connection.execute(sa.text("""
        SELECT last_processed_id FROM migration_progress
        WHERE migration_name = 'backfill_full_name'
    """))
    row = result.fetchone()
    last_id = row[0] if row else 0

    batch_size = 5000

    while True:
        result = connection.execute(sa.text(f"""
            WITH batch AS (
                SELECT id FROM users
                WHERE id > {last_id} AND full_name IS NULL
                ORDER BY id
                LIMIT {batch_size}
            )
            UPDATE users
            SET full_name = first_name || ' ' || last_name
            WHERE id IN (SELECT id FROM batch)
            RETURNING id
        """))

        updated_ids = [row[0] for row in result.fetchall()]

        if not updated_ids:
            break

        last_id = max(updated_ids)

        # Save checkpoint
        connection.execute(sa.text("""
            INSERT INTO migration_progress (migration_name, last_processed_id, updated_at)
            VALUES ('backfill_full_name', :last_id, NOW())
            ON CONFLICT (migration_name)
            DO UPDATE SET last_processed_id = :last_id, updated_at = NOW()
        """), {'last_id': last_id})

        connection.commit()
        print(f"Processed up to ID {last_id}")

    # Cleanup
    op.drop_table('migration_progress')
```

## Anti-Patterns to Avoid

### Anti-Pattern: Mixing Schema and Data

**Bad**:
```python
def upgrade():
    # Schema change
    op.add_column('users', sa.Column('score', sa.Integer()))

    # Immediate data migration (locks table)
    connection = op.get_bind()
    connection.execute(sa.text("UPDATE users SET score = calculate_score(id)"))

    # More schema changes
    op.alter_column('users', 'score', nullable=False)
```

**Good**: Separate migrations
```python
# Migration 1: Schema
def upgrade():
    op.add_column('users', sa.Column('score', sa.Integer()))

# Migration 2: Data (separate deployment)
def upgrade():
    connection = op.get_bind()
    # Batch processing...

# Migration 3: Final schema
def upgrade():
    op.alter_column('users', 'score', nullable=False)
```

### Anti-Pattern: No Downgrade

**Bad**:
```python
def downgrade():
    pass  # TODO: Implement later
```

**Good**:
```python
def downgrade():
    # Even if partially irreversible, do what you can
    op.drop_column('users', 'email')
    # Document limitations in docstring
```

### Anti-Pattern: Large Transactions

**Bad**:
```python
def upgrade():
    # Single transaction updates millions of rows
    connection = op.get_bind()
    connection.execute(sa.text("UPDATE users SET status = 'active'"))  # Locks table for minutes
```

**Good**:
```python
def upgrade():
    connection = op.get_bind()
    batch_size = 5000
    offset = 0

    while True:
        result = connection.execute(sa.text(f"""
            UPDATE users SET status = 'active'
            WHERE id IN (
                SELECT id FROM users
                WHERE status IS NULL
                ORDER BY id
                LIMIT {batch_size}
            )
        """))

        if result.rowcount == 0:
            break
```

### Anti-Pattern: Implicit Type Conversion

**Bad**:
```python
def upgrade():
    # Hope database figures it out
    op.alter_column('users', 'age', type_=sa.Integer())
```

**Good**:
```python
def upgrade():
    # Explicit conversion with validation
    op.alter_column(
        'users',
        'age',
        type_=sa.Integer(),
        postgresql_using='age::integer'
    )
```

### Anti-Pattern: Ignoring Existing Data

**Bad**:
```python
def upgrade():
    # Will fail if any NULL values exist
    op.add_column('users', sa.Column('email', sa.String(255), nullable=False))
```

**Good**:
```python
def upgrade():
    # Add nullable, then backfill, then make required
    op.add_column('users', sa.Column('email', sa.String(255), nullable=True))
    # Next migration will backfill and add constraint
```

## Next Steps

- Review [advanced-topics.md](advanced-topics.md) for production-grade techniques
- Study [examples/](../examples/) for working implementations
- Check [troubleshooting.md](troubleshooting.md) when issues arise
