---
name: database-migration
description: Expert database schema design and migration management with Alembic, SQLAlchemy, and advanced migration patterns
version: 1.0.0
tags: [database, migration, schema, alembic, sqlalchemy, backend, postgres, mysql]
---

# Database Migration Skill

Comprehensive database migration management expertise covering schema design, migration generation, version control, deployment strategies, rollback procedures, and zero-downtime migrations using industry-standard tools.

## Overview

This skill provides expert-level guidance for database migrations across all phases of application development, from initial schema design through production deployments. Whether you're creating your first migration, managing a complex multi-tenant schema, or executing zero-downtime deployments, this skill delivers battle-tested patterns and practices.

**Core Focus Areas:**
- Migration generation and management with Alembic
- SQLAlchemy model design and best practices
- Schema versioning and branching strategies
- Production deployment and rollback procedures
- Zero-downtime migration techniques
- Data migration and transformation
- Multi-database and multi-tenant architectures
- Performance optimization and indexing strategies

## Quick Start

### Basic Migration Workflow

```python
# 1. Initialize Alembic in your project
alembic init alembic

# 2. Configure database connection in alembic.ini
sqlalchemy.url = postgresql://user:pass@localhost/dbname

# 3. Create a migration
alembic revision --autogenerate -m "Add users table"

# 4. Review the generated migration
# Edit alembic/versions/xxxx_add_users_table.py

# 5. Apply the migration
alembic upgrade head

# 6. Rollback if needed
alembic downgrade -1
```

### Simple Model-to-Migration Example

```python
# models.py - Define your SQLAlchemy model
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    username = Column(String(100), unique=True, nullable=False)
    created_at = Column(DateTime, nullable=False, server_default='NOW()')

# Generate migration
# $ alembic revision --autogenerate -m "Create users table"
```

## Core Capabilities

This skill provides comprehensive expertise in:

### 1. Migration Management
- **Alembic Configuration**: Setup, initialization, and configuration best practices
- **Migration Generation**: Auto-generate migrations from SQLAlchemy models
- **Manual Migration Authoring**: Write complex migrations that autogenerate can't handle
- **Version Control Integration**: Git workflows for migration files
- **Branch Management**: Handle migration branches and merges
- **Migration History**: Track and visualize migration lineage

### 2. Schema Design
- **Table Design**: Optimal table structure for your use case
- **Column Types**: Choose correct data types for PostgreSQL, MySQL, SQLite
- **Constraints**: Primary keys, foreign keys, unique constraints, check constraints
- **Indexes**: Performance indexes, covering indexes, partial indexes
- **Relationships**: One-to-many, many-to-many, polymorphic associations
- **Normalization**: Apply 1NF, 2NF, 3NF, BCNF appropriately

### 3. Data Migrations
- **Bulk Data Transformations**: Transform existing data during migrations
- **Data Seeding**: Populate initial or reference data
- **Type Conversions**: Change column types without data loss
- **Data Validation**: Ensure data integrity during transformations
- **Large Dataset Handling**: Batch processing for millions of rows
- **Reversibility**: Make data migrations reversible when possible

### 4. Production Deployments
- **Deployment Strategies**: Online vs offline migrations
- **Zero-Downtime Migrations**: Multi-phase deployment patterns
- **Rollback Procedures**: Safe rollback with data preservation
- **Smoke Testing**: Verify migrations in production
- **Monitoring**: Track migration performance and impact
- **Disaster Recovery**: Backup and restore strategies

### 5. Advanced Patterns
- **Multi-Tenancy**: Schema-per-tenant, shared schema patterns
- **Sharding**: Horizontal partitioning strategies
- **Materialized Views**: Create and maintain views
- **Full-Text Search**: PostgreSQL full-text indexes
- **JSON/JSONB Columns**: Semi-structured data handling
- **Temporal Tables**: Track historical data changes
- **Soft Deletes**: Implement deletion markers
- **Audit Trails**: Track all table changes

### 6. Database-Specific Features
- **PostgreSQL**: Arrays, JSONB, full-text search, ranges, custom types
- **MySQL/MariaDB**: Specific constraints and storage engines
- **SQLite**: Limitations and workarounds
- **Multi-Database Support**: Abstract migrations for multiple backends

### 7. Testing & Validation
- **Migration Testing**: Unit test your migrations
- **Schema Validation**: Verify schema matches models
- **Data Integrity Tests**: Ensure constraints are enforced
- **Performance Testing**: Benchmark migration execution time
- **Rollback Testing**: Verify downgrade functions work

### 8. Troubleshooting
- **Failed Migrations**: Recovery procedures
- **Deadlock Resolution**: Handle concurrent migration issues
- **Constraint Violations**: Fix data before adding constraints
- **Performance Issues**: Optimize slow migrations
- **Version Conflicts**: Resolve migration branch conflicts

### 9. Team Collaboration
- **Migration Workflows**: Team processes for creating migrations
- **Code Review**: What to review in migration PRs
- **Conflict Resolution**: Handle concurrent migration development
- **Documentation**: Document complex migrations
- **Communication**: When to notify team about schema changes

### 10. Security & Compliance
- **Access Control**: Database permissions for migrations
- **Sensitive Data**: Handle PII during migrations
- **Compliance**: GDPR, HIPAA-compliant schema design
- **Encryption**: Column-level encryption strategies
- **Audit Requirements**: Regulatory compliance tracking

## Documentation

Comprehensive documentation organized by topic:

### Core Concepts
**[Core Concepts](docs/core-concepts.md)** - Essential database migration fundamentals
- Migration systems overview (Alembic, Flyway, Liquibase)
- SQLAlchemy ORM integration
- Version control for database schemas
- Migration file structure and anatomy
- Upgrade and downgrade functions
- Revision identifiers and chains
- Database state management
- Idempotency and safety principles

### Best Practices
**[Best Practices](docs/best-practices.md)** - Industry-standard migration practices
- Migration naming conventions
- When to use autogenerate vs manual
- Reviewing generated migrations
- Making migrations reversible
- Atomic migrations and transactions
- Index creation without locking
- Testing migrations before deployment
- Documenting complex changes
- Team collaboration workflows

### Patterns
**[Patterns](docs/patterns.md)** - Common migration patterns and anti-patterns
- Adding columns with defaults
- Dropping columns safely
- Renaming columns and tables
- Changing column types
- Adding constraints to existing data
- Migrating enum types
- Splitting and merging tables
- Multi-phase migrations for zero downtime
- Data backfill strategies
- Anti-patterns to avoid

### Advanced Topics
**[Advanced Topics](docs/advanced-topics.md)** - Expert-level migration techniques
- Zero-downtime deployment strategies
- Large-scale data migrations (millions of rows)
- Concurrent index creation
- Table partitioning
- Schema migrations vs data migrations
- Multi-tenant migration strategies
- Cross-database migration patterns
- Custom migration commands
- Performance optimization techniques
- Disaster recovery and backup strategies

### Troubleshooting
**[Troubleshooting](docs/troubleshooting.md)** - Common issues and solutions
- Failed migration recovery
- Constraint violation resolution
- Deadlock handling
- Migration conflicts and merges
- Slow migration optimization
- Rollback failures
- Data loss prevention
- Version skew problems
- Testing environment mismatches

### API Reference
**[API Reference](docs/api-reference.md)** - Complete Alembic and SQLAlchemy reference
- Alembic commands (upgrade, downgrade, revision, etc.)
- Migration operations API
- SQLAlchemy column types
- Constraint definitions
- Index creation
- Configuration options
- Environment setup
- Custom migration scripts

## Examples

### Basic Examples
Foundational migration patterns for common scenarios:

1. **[Create Tables](examples/basic/create-tables.md)** - Creating basic tables with columns and constraints
   - Define SQLAlchemy models
   - Generate table creation migrations
   - Add primary keys, foreign keys, and unique constraints
   - Set up proper indexes

2. **[Add Columns](examples/basic/add-columns.md)** - Adding new columns to existing tables
   - Add nullable columns
   - Add columns with defaults
   - Add columns to populated tables
   - Handle backwards compatibility

3. **[Create Indexes](examples/basic/create-indexes.md)** - Creating database indexes for performance
   - Single-column indexes
   - Multi-column composite indexes
   - Unique indexes
   - Partial indexes with conditions

### Intermediate Examples
More complex real-world migration scenarios:

4. **[Rename Columns](examples/intermediate/rename-columns.md)** - Safely renaming columns
   - Rename with zero downtime
   - Update application code coordination
   - Handle foreign key references
   - Maintain index integrity

5. **[Change Column Types](examples/intermediate/change-column-types.md)** - Changing column data types
   - String to integer conversion
   - Expanding varchar limits
   - Changing to enum types
   - Using USING clause for complex transformations

6. **[Data Migration](examples/intermediate/data-migration.md)** - Transforming existing data
   - Bulk update patterns
   - Batch processing for large tables
   - Data validation and cleanup
   - Reversible data transformations

7. **[Add Constraints](examples/intermediate/add-constraints.md)** - Adding constraints to existing tables
   - Add NOT NULL to nullable columns
   - Add unique constraints
   - Add check constraints
   - Add foreign keys with existing data

### Advanced Examples
Production-grade patterns for complex scenarios:

8. **[Zero Downtime Migration](examples/advanced/zero-downtime-migration.md)** - Deploy without service interruption
   - Multi-phase deployment strategy
   - Dual-write patterns
   - Blue-green database migrations
   - Backward-compatible schema changes

9. **[Large Table Migration](examples/advanced/large-table-migration.md)** - Migrate tables with millions of rows
   - Partitioned table migrations
   - Batched data processing
   - Progress tracking and resumability
   - Minimal lock time strategies

10. **[Multi-Tenant Schema](examples/advanced/multi-tenant-schema.md)** - Migrations for multi-tenant systems
    - Schema-per-tenant approach
    - Shared schema with tenant_id
    - Migrating all tenants safely
    - Tenant isolation patterns

## Templates

Ready-to-use migration templates you can copy and customize:

### [Basic CRUD Schema Template](templates/basic-crud-schema.md)
Complete schema for a typical CRUD application with users, authentication, and audit trails
- User management tables
- Authentication and sessions
- Role-based access control
- Audit logging tables
- Soft delete patterns

### [E-Commerce Schema Template](templates/ecommerce-schema.md)
Production-ready e-commerce database schema
- Product catalog with variants
- Shopping cart and orders
- Payment processing
- Inventory management
- Customer data and addresses

### [Multi-Tenant SaaS Template](templates/multi-tenant-saas.md)
Complete multi-tenant SaaS schema with organization hierarchy
- Organization and workspace tables
- User-organization relationships
- Tenant isolation patterns
- Feature flags per tenant
- Billing and subscription tracking

## Resources

### [Checklists](resources/checklists.md)
Quality assurance checklists for migrations:
- Pre-deployment migration checklist
- Production deployment checklist
- Post-deployment verification checklist
- Rollback decision checklist
- Code review checklist for migrations
- Performance optimization checklist

### [Glossary](resources/glossary.md)
Complete terminology guide:
- Migration system concepts
- Database terminology
- Alembic-specific terms
- SQLAlchemy ORM terms
- Schema design concepts

### [References](resources/references.md)
External resources and documentation:
- Official Alembic documentation
- SQLAlchemy documentation
- Database-specific references (PostgreSQL, MySQL)
- Migration best practices articles
- Video tutorials and courses
- Community resources

### [Workflows](resources/workflows.md)
Step-by-step procedures with checklists:
- Local development migration workflow
- Creating and testing a new migration
- Reviewing migration pull requests
- Deploying migrations to staging
- Deploying migrations to production
- Rolling back a failed migration
- Handling migration conflicts

## Common Use Cases

### Scenario: Adding a new feature requiring database changes
1. **Design**: Plan your schema changes (see [docs/core-concepts.md](docs/core-concepts.md))
2. **Model**: Update SQLAlchemy models (see [examples/basic/create-tables.md](examples/basic/create-tables.md))
3. **Generate**: Create migration with autogenerate
4. **Review**: Check generated migration (see [docs/best-practices.md](docs/best-practices.md))
5. **Test**: Test locally and write rollback (see [docs/troubleshooting.md](docs/troubleshooting.md))
6. **Deploy**: Follow production deployment workflow (see [resources/workflows.md](resources/workflows.md))

### Scenario: Modifying existing tables in production
1. **Analyze Impact**: Determine if zero-downtime is needed
2. **Plan Phases**: Break into backward-compatible steps (see [examples/advanced/zero-downtime-migration.md](examples/advanced/zero-downtime-migration.md))
3. **Coordinate**: Align migrations with code deployments
4. **Monitor**: Track migration performance and errors
5. **Verify**: Confirm data integrity post-migration

### Scenario: Fixing a failed production migration
1. **Stop**: Halt any ongoing migrations
2. **Assess**: Determine failure point (see [docs/troubleshooting.md](docs/troubleshooting.md))
3. **Decide**: Fix forward or rollback
4. **Execute**: Follow recovery procedures
5. **Verify**: Confirm database state is consistent
6. **Document**: Record incident and prevention steps

## Integration with Other Skills

This skill works seamlessly with:

- **Backend Architecture**: Design database schemas that match your API architecture
- **Python API Development**: SQLAlchemy models integrate with FastAPI/Flask
- **DevOps**: Automate migration deployments in CI/CD pipelines
- **Testing**: Write tests for migrations and schema changes
- **Performance Optimization**: Index strategies and query optimization

## Getting Started Paths

### For Beginners
1. Start with [Core Concepts](docs/core-concepts.md) to understand fundamentals
2. Follow [Create Tables](examples/basic/create-tables.md) example
3. Learn [Best Practices](docs/best-practices.md) early
4. Use [Workflows](resources/workflows.md) for step-by-step guidance

### For Intermediate Users
1. Review [Patterns](docs/patterns.md) for common scenarios
2. Study [Data Migration](examples/intermediate/data-migration.md) techniques
3. Learn [Zero Downtime Migration](examples/advanced/zero-downtime-migration.md)
4. Master [Troubleshooting](docs/troubleshooting.md) techniques

### For Advanced Users
1. Explore [Advanced Topics](docs/advanced-topics.md) for expert techniques
2. Study [Large Table Migration](examples/advanced/large-table-migration.md)
3. Implement [Multi-Tenant Schema](examples/advanced/multi-tenant-schema.md)
4. Customize templates for your architecture

## Safety and Reliability

Database migrations are critical operations that can cause data loss or downtime if done incorrectly. This skill emphasizes:

- ✅ **Test Everything**: Always test migrations locally and in staging
- ✅ **Backup First**: Create database backups before production migrations
- ✅ **Reversible Migrations**: Write downgrade functions that actually work
- ✅ **Atomic Operations**: Use transactions to ensure all-or-nothing changes
- ✅ **Progressive Rollout**: Deploy to small percentage of systems first
- ✅ **Monitor Closely**: Watch for errors, performance degradation, and data issues
- ✅ **Have Rollback Plan**: Know how to revert before you deploy
- ✅ **Document Changes**: Explain complex migrations for future reference

## Performance Considerations

Migrations can impact application performance. Key considerations:

- **Lock Time**: Minimize table locks during migrations
- **Index Creation**: Use CONCURRENTLY for PostgreSQL to avoid blocking
- **Batch Processing**: Process large datasets in chunks
- **Timing**: Schedule long migrations during low-traffic periods
- **Resources**: Ensure adequate disk space and memory
- **Monitoring**: Track query performance before and after

## Version Compatibility

This skill covers:
- **Alembic**: 1.7.0+ (latest features), compatible with 1.0+
- **SQLAlchemy**: 2.0+ (latest), with 1.4 compatibility notes
- **PostgreSQL**: 12, 13, 14, 15, 16
- **MySQL/MariaDB**: 5.7, 8.0
- **SQLite**: 3.x (with limitations noted)

## Support and Feedback

This skill is continuously updated with:
- New migration patterns as they emerge
- Database-specific optimizations
- Real-world troubleshooting scenarios
- Community-contributed examples
- Updates for new Alembic/SQLAlchemy versions

## Next Steps

1. **Start Simple**: Begin with [Create Tables](examples/basic/create-tables.md) if you're new
2. **Understand Concepts**: Read [Core Concepts](docs/core-concepts.md) thoroughly
3. **Practice Locally**: Create a test project and experiment with migrations
4. **Use Templates**: Start with templates and modify for your needs
5. **Follow Checklists**: Use checklists to avoid common mistakes
6. **Join Community**: Learn from others' migration experiences

Remember: Good database migrations are careful, tested, reversible, and documented. This skill provides everything you need to achieve migration excellence.
