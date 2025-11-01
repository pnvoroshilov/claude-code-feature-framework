# Core Concepts

Essential database migration fundamentals that every developer needs to understand before working with schema changes, migration tools, and database versioning.

## Table of Contents

- [What Are Database Migrations?](#what-are-database-migrations)
- [Migration Systems Overview](#migration-systems-overview)
- [Alembic Architecture](#alembic-architecture)
- [SQLAlchemy Integration](#sqlalchemy-integration)
- [Version Control for Schemas](#version-control-for-schemas)
- [Migration File Anatomy](#migration-file-anatomy)
- [Upgrade and Downgrade Functions](#upgrade-and-downgrade-functions)
- [Revision Identifiers](#revision-identifiers)
- [Database State Management](#database-state-management)
- [Idempotency](#idempotency)
- [Transaction Management](#transaction-management)
- [Schema vs Data Migrations](#schema-vs-data-migrations)

## What Are Database Migrations?

### Definition

**Database migrations** are version-controlled scripts that evolve your database schema over time in a trackable, reproducible way. They allow you to:

- Apply schema changes incrementally
- Share database schema changes with your team
- Deploy database updates alongside application code
- Roll back problematic changes
- Maintain consistency across environments (dev, staging, production)

### Why Migrations Matter

**Without migrations**, database changes are chaotic:
```sql
-- Developer 1 manually runs:
ALTER TABLE users ADD COLUMN last_login TIMESTAMP;

-- Developer 2 doesn't know about this change
-- Production database is out of sync
-- No record of when or why the change was made
-- No way to rollback
```

**With migrations**, changes are controlled:
```python
# Migration file: 20250131_add_last_login.py
def upgrade():
    op.add_column('users', sa.Column('last_login', sa.DateTime()))

def downgrade():
    op.drop_column('users', 'last_login')
```

### Key Benefits

1. **Version Control**: Database schema tracked in git alongside code
2. **Reproducibility**: Same migrations apply consistently everywhere
3. **Collaboration**: Team members see and review schema changes
4. **Deployment Automation**: Migrations run automatically in CI/CD
5. **Reversibility**: Downgrade functions enable rollback
6. **Documentation**: Migration files document schema history

## Migration Systems Overview

### Popular Migration Tools

#### Alembic (Python/SQLAlchemy)
```python
# Most popular Python migration tool
# Tight SQLAlchemy integration
# Auto-generate migrations from models
alembic revision --autogenerate -m "Add users table"
alembic upgrade head
```

**Pros**:
- Excellent SQLAlchemy integration
- Autogenerate feature saves time
- Pure Python, flexible scripting
- Strong community support

**Cons**:
- Python-only ecosystem
- Autogenerate needs review
- Learning curve for complex scenarios

#### Flyway (Java/Multi-language)
```sql
-- V1__create_users_table.sql
CREATE TABLE users (
    id INT PRIMARY KEY,
    email VARCHAR(255) NOT NULL
);
```

**Pros**:
- Language-agnostic (raw SQL)
- Simple versioning scheme
- Enterprise features
- Multiple database support

**Cons**:
- Less flexible than code-based tools
- No autogenerate
- Rollback requires manual scripts

#### Liquibase (Java/Multi-language)
```xml
<changeSet id="1" author="developer">
    <createTable tableName="users">
        <column name="id" type="int" autoIncrement="true">
            <constraints primaryKey="true"/>
        </column>
    </createTable>
</changeSet>
```

**Pros**:
- Database-independent XML/YAML/JSON
- Enterprise-grade features
- Extensive tooling
- Complex rollback support

**Cons**:
- XML verbosity
- Steeper learning curve
- Heavy for simple projects

#### Django Migrations (Python/Django)
```python
# Built into Django framework
class Migration(migrations.Migration):
    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(primary_key=True)),
                ('email', models.EmailField()),
            ],
        ),
    ]
```

**Pros**:
- Integrated with Django
- Automatic detection
- Excellent for Django projects

**Cons**:
- Django-specific
- Can't use outside Django

### Choosing Alembic

Alembic is ideal when:
- ✅ You're using Python and SQLAlchemy
- ✅ You want autogenerate capability
- ✅ You need flexible, code-based migrations
- ✅ You want tight ORM integration
- ✅ You value pure Python migrations

## Alembic Architecture

### Core Components

```
Your Project
├── alembic/                    # Alembic directory
│   ├── versions/               # Migration files
│   │   ├── 20250131_abc123.py  # Individual migrations
│   │   └── 20250201_def456.py
│   ├── env.py                  # Environment configuration
│   └── script.py.mako          # Template for new migrations
├── alembic.ini                 # Alembic configuration
└── models.py                   # Your SQLAlchemy models
```

### Component Roles

**alembic.ini**: Configuration file
```ini
[alembic]
script_location = alembic
sqlalchemy.url = postgresql://user:pass@localhost/mydb

[loggers]
# Logging configuration
```

**env.py**: Environment setup
```python
# Loads your models
# Configures database connection
# Sets up autogenerate context
from myapp.models import Base

target_metadata = Base.metadata
```

**versions/**: Migration scripts directory
```
Each file represents one schema change
Files are linked in a chain (revision history)
Alembic tracks which migrations have been applied
```

**script.py.mako**: Template for new migrations
```python
# Template used when creating new migration files
# Customizable for your project needs
"""${message}

Revision ID: ${up_revision}
Revises: ${down_revision | comma,n}
Create Date: ${create_date}
"""
```

### Migration File Naming

Alembic generates names like:
```
abc123def456_add_users_table.py
  │         │   └─ Description
  │         └─ Unique revision hash
  └─ Short hash prefix
```

You can customize with:
```python
# alembic.ini
file_template = %%(year)d%%(month).2d%%(day).2d_%%(rev)s_%%(slug)s
# Produces: 20250131_abc123_add_users_table.py
```

## SQLAlchemy Integration

### Models Drive Migrations

Alembic's autogenerate compares your SQLAlchemy models to the current database schema:

```python
# models.py - Define your schema
from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    email = Column(String(255), unique=True, nullable=False)
    username = Column(String(100), nullable=False)
```

```python
# env.py - Link models to Alembic
from models import Base

target_metadata = Base.metadata
```

```bash
# Generate migration from model differences
$ alembic revision --autogenerate -m "Add users table"
# Alembic detects your User model and generates migration
```

### Autogenerate Detection

**What Alembic CAN detect**:
- ✅ New tables and columns
- ✅ Removed tables and columns
- ✅ Column type changes
- ✅ Nullable changes
- ✅ Server defaults
- ✅ Index changes
- ✅ Foreign key constraints

**What Alembic CANNOT detect**:
- ❌ Table or column renames (sees as drop + add)
- ❌ Constraint names changes
- ❌ Check constraints (database-specific)
- ❌ Some column type changes (e.g., VARCHAR size increase)
- ❌ Partial indexes or functional indexes

For undetected changes, write manual migrations.

### Model-First vs Database-First

**Model-First** (Recommended):
```python
# 1. Define/update SQLAlchemy models
class User(Base):
    __tablename__ = 'users'
    email = Column(String(255))

# 2. Generate migration
alembic revision --autogenerate -m "Change"

# 3. Review and apply
alembic upgrade head
```

**Database-First**:
```python
# 1. Manually write migration
def upgrade():
    op.add_column('users', sa.Column('email', sa.String(255)))

# 2. Apply migration
alembic upgrade head

# 3. Update models to match
class User(Base):
    email = Column(String(255))
```

Model-first is preferred because:
- Models are your source of truth
- Autogenerate reduces errors
- Code and database stay in sync
- Easier for teams to review changes

## Version Control for Schemas

### Git Workflow

```bash
# 1. Create feature branch
git checkout -b feature/add-user-email

# 2. Update models
# Edit models.py

# 3. Generate migration
alembic revision --autogenerate -m "Add email to users"

# 4. Review generated migration
# Edit alembic/versions/xxx_add_email_to_users.py

# 5. Test migration locally
alembic upgrade head
# Test your application
alembic downgrade -1  # Test rollback
alembic upgrade head  # Re-apply

# 6. Commit migration with code
git add alembic/versions/xxx_add_email_to_users.py
git add models.py
git commit -m "Add email field to User model"

# 7. Push and create PR
git push origin feature/add-user-email
```

### Migration History

Migrations form a linear chain:
```
None → abc123 → def456 → ghi789 → head
       ↓        ↓        ↓
     Create   Add col  Add index
     users    email
```

You can navigate this chain:
```bash
# Show current version
alembic current

# Show migration history
alembic history

# Upgrade to specific version
alembic upgrade abc123

# Downgrade to specific version
alembic downgrade def456

# Show what would change
alembic upgrade head --sql
```

## Migration File Anatomy

### Standard Migration Structure

```python
"""Add email column to users table

Revision ID: abc123def456
Revises: prev123revision
Create Date: 2025-01-31 10:30:15.123456
"""

# Imports
from alembic import op
import sqlalchemy as sa

# Revision identifiers
revision = 'abc123def456'      # This migration's ID
down_revision = 'prev123'      # Parent migration
branch_labels = None           # For branching
depends_on = None              # For dependencies

def upgrade():
    """Apply the migration"""
    op.add_column(
        'users',
        sa.Column('email', sa.String(255), nullable=True)
    )

def downgrade():
    """Revert the migration"""
    op.drop_column('users', 'email')
```

### Key Components

**Docstring**: Describes the migration
```python
"""Add email column to users table

Detailed description of what this migration does
and why it's needed.
"""
```

**Revision Identifiers**: Link migrations
```python
revision = 'abc123def456'      # Unique ID for this migration
down_revision = 'prev123'      # Points to previous migration
```

**upgrade()**: Forward migration
```python
def upgrade():
    # Operations to apply schema changes
    op.add_column(...)
    op.create_index(...)
```

**downgrade()**: Reverse migration
```python
def downgrade():
    # Operations to revert changes
    # Should undo everything in upgrade()
    op.drop_index(...)
    op.drop_column(...)
```

## Upgrade and Downgrade Functions

### Writing upgrade()

```python
def upgrade():
    """
    Apply schema changes.
    Should be idempotent when possible.
    Should succeed or fail atomically.
    """

    # Create table
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('email', sa.String(255), nullable=False)
    )

    # Add index
    op.create_index('ix_users_email', 'users', ['email'])

    # Add column to existing table
    op.add_column('orders', sa.Column('user_id', sa.Integer()))

    # Add foreign key
    op.create_foreign_key(
        'fk_orders_user_id',
        'orders', 'users',
        ['user_id'], ['id']
    )
```

### Writing downgrade()

```python
def downgrade():
    """
    Revert all changes from upgrade().
    Order is typically reverse of upgrade().
    """

    # Drop foreign key first
    op.drop_constraint('fk_orders_user_id', 'orders')

    # Drop column
    op.drop_column('orders', 'user_id')

    # Drop index
    op.drop_index('ix_users_email')

    # Drop table
    op.drop_table('users')
```

### Reversibility Considerations

**Reversible migrations**:
```python
def upgrade():
    op.add_column('users', sa.Column('nickname', sa.String(50)))

def downgrade():
    op.drop_column('users', 'nickname')
    # Safe: no data loss if nickname was optional
```

**Irreversible migrations** (data loss):
```python
def upgrade():
    op.drop_column('users', 'old_password_hash')

def downgrade():
    raise NotImplementedError(
        "Cannot recover dropped password hashes. "
        "Restore from backup if needed."
    )
```

**Partially reversible** (data transformation loss):
```python
def upgrade():
    # Combine first_name and last_name into full_name
    op.add_column('users', sa.Column('full_name', sa.String(200)))
    op.execute("""
        UPDATE users
        SET full_name = first_name || ' ' || last_name
    """)
    op.drop_column('users', 'first_name')
    op.drop_column('users', 'last_name')

def downgrade():
    # Can split full_name, but not perfectly
    op.add_column('users', sa.Column('first_name', sa.String(100)))
    op.add_column('users', sa.Column('last_name', sa.String(100)))
    op.execute("""
        UPDATE users
        SET first_name = split_part(full_name, ' ', 1),
            last_name = split_part(full_name, ' ', 2)
    """)
    op.drop_column('users', 'full_name')
    # Note: Loses middle names and complex name structures
```

## Revision Identifiers

### Revision Hash

Each migration has a unique identifier:
```python
revision = 'abc123def456'
```

Generated by Alembic using:
- Timestamp
- Random component
- Ensures global uniqueness

### Revision Chain

Migrations link together:
```python
# First migration
revision = 'abc123'
down_revision = None  # No parent

# Second migration
revision = 'def456'
down_revision = 'abc123'  # Points to first

# Third migration
revision = 'ghi789'
down_revision = 'def456'  # Points to second
```

### Special Revision Names

```bash
# head: Latest migration
alembic upgrade head

# base: Before any migrations
alembic downgrade base

# +1: One step forward
alembic upgrade +1

# -1: One step back
alembic downgrade -1

# Specific revision
alembic upgrade abc123
```

## Database State Management

### alembic_version Table

Alembic tracks applied migrations in a special table:
```sql
CREATE TABLE alembic_version (
    version_num VARCHAR(32) NOT NULL PRIMARY KEY
);

-- After applying abc123 migration:
INSERT INTO alembic_version VALUES ('abc123');

-- After applying def456:
UPDATE alembic_version SET version_num = 'def456';
```

**Important**: Only one row exists, containing current revision.

### Checking Current Version

```bash
# Show current database version
$ alembic current
abc123 (head)

# Show pending migrations
$ alembic history
abc123 -> def456 (head), Add email column
abc123, Create users table
```

```python
# Programmatically check version
from alembic import command
from alembic.config import Config

config = Config("alembic.ini")
command.current(config)
```

## Idempotency

### What Is Idempotency?

**Idempotent operations** can be applied multiple times with the same result:

```python
# Idempotent (can run multiple times safely)
def upgrade():
    # Check if column exists before adding
    conn = op.get_bind()
    result = conn.execute("""
        SELECT column_name
        FROM information_schema.columns
        WHERE table_name='users' AND column_name='email'
    """)

    if not result.fetchone():
        op.add_column('users', sa.Column('email', sa.String(255)))
```

```python
# Non-idempotent (fails on second run)
def upgrade():
    # Will error if column already exists
    op.add_column('users', sa.Column('email', sa.String(255)))
```

### Why Idempotency Matters

**Problem without idempotency**:
- Migration fails halfway through
- Some operations succeeded
- Re-running fails on already-applied operations
- Requires manual database fixes

**Solution with idempotency**:
- Migration can be safely re-run
- Skips already-applied operations
- Completes remaining operations
- Self-healing on retry

### Alembic's Built-in Protection

Alembic tracks applied migrations, providing idempotency at the **migration file level**:

```bash
# First run: applies migration
$ alembic upgrade head
Running upgrade abc123 -> def456

# Second run: does nothing
$ alembic upgrade head
# No output - already at head
```

Within a migration, Alembic does NOT protect individual operations.

## Transaction Management

### Default Behavior

Alembic wraps each migration in a transaction:

```python
def upgrade():
    op.add_column('users', sa.Column('email', sa.String(255)))
    op.create_index('ix_users_email', 'users', ['email'])
    # If index creation fails, column addition is rolled back
```

### Transaction Per Migration

```python
# alembic.ini
[alembic]
transaction_per_migration = true  # Default
```

**Pros**:
- Atomic migrations (all-or-nothing)
- Automatic rollback on error
- Database consistency guaranteed

**Cons**:
- Some operations can't run in transactions (e.g., CREATE INDEX CONCURRENTLY)
- Long migrations hold locks

### Disabling Transactions

```python
# alembic.ini
[alembic]
transaction_per_migration = false
```

Or per-migration:
```python
def upgrade():
    # Disable transaction for this migration
    op.execute("SET statement_timeout = 0")
    op.execute("CREATE INDEX CONCURRENTLY ix_users_email ON users(email)")
```

### Manual Transaction Control

```python
def upgrade():
    # Get database connection
    conn = op.get_bind()

    # Manual transaction
    trans = conn.begin()
    try:
        conn.execute("INSERT INTO users ...")
        conn.execute("UPDATE settings ...")
        trans.commit()
    except:
        trans.rollback()
        raise
```

## Schema vs Data Migrations

### Schema Migrations

Change database structure:
```python
def upgrade():
    # Add table
    op.create_table('users', ...)

    # Add column
    op.add_column('orders', sa.Column('status', sa.String(20)))

    # Add index
    op.create_index('ix_orders_status', 'orders', ['status'])

    # Add constraint
    op.create_foreign_key('fk_orders_user', 'orders', 'users', ...)
```

**Characteristics**:
- Change schema definition
- Usually fast (except on large tables)
- Reversible (mostly)
- No data content changes

### Data Migrations

Transform existing data:
```python
def upgrade():
    # Add new column
    op.add_column('users', sa.Column('full_name', sa.String(200)))

    # Populate from existing data
    op.execute("""
        UPDATE users
        SET full_name = first_name || ' ' || last_name
        WHERE full_name IS NULL
    """)

    # Now safe to drop old columns
    op.drop_column('users', 'first_name')
    op.drop_column('users', 'last_name')
```

**Characteristics**:
- Transform data content
- Can be slow on large tables
- Often irreversible
- Requires careful testing

### Combining Schema and Data

**Best practice**: Separate schema and data migrations

```python
# Migration 1: Schema changes (fast, reversible)
def upgrade():
    op.add_column('users', sa.Column('full_name', sa.String(200)))

def downgrade():
    op.drop_column('users', 'full_name')
```

```python
# Migration 2: Data transformation (slow, irreversible)
def upgrade():
    op.execute("""
        UPDATE users
        SET full_name = first_name || ' ' || last_name
    """)

def downgrade():
    # Optionally restore, but may lose data
    pass
```

```python
# Migration 3: Cleanup (fast, partially reversible)
def upgrade():
    op.drop_column('users', 'first_name')
    op.drop_column('users', 'last_name')

def downgrade():
    op.add_column('users', sa.Column('first_name', sa.String(100)))
    op.add_column('users', sa.Column('last_name', sa.String(100)))
    # Note: data already lost from migration 2
```

This separation allows:
- Deploying schema change first (fast)
- Running data migration separately (slow, monitored)
- Easier rollback of individual steps

## Next Steps

Now that you understand core concepts:

1. **Learn Best Practices**: Read [best-practices.md](best-practices.md) to avoid common mistakes
2. **Study Patterns**: See [patterns.md](patterns.md) for real-world scenarios
3. **Try Examples**: Walk through [examples/basic/](../examples/basic/) tutorials
4. **Explore Advanced**: Dive into [advanced-topics.md](advanced-topics.md) when ready

Remember: Migrations are powerful but dangerous. Understanding these core concepts is essential before making production schema changes.
