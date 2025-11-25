# Skills System

Complete guide to the Skills system in the Claude Code Feature Framework.

## Overview

The Skills system provides modular, reusable knowledge modules that extend Claude Code's capabilities. Skills are structured documentation bundles that Claude Code can reference to perform specialized tasks.

## Architecture

### Skill Types

1. **Default Skills**: Framework-provided skills in `framework-assets/claude-skills/`
2. **Custom Skills**: Project-specific skills in `.claude/skills/`
3. **Enabled Skills**: Skills active in a specific project (tracked in database)

### Skill Structure

Each skill follows a standardized structure:

```
skill-name/
├── SKILL.md                      # Main skill file with frontmatter
├── README.md                     # Quick start and overview
├── docs/                         # Documentation
│   ├── core-concepts.md
│   ├── best-practices.md
│   ├── patterns.md
│   ├── advanced-topics.md
│   ├── troubleshooting.md
│   └── api-reference.md
├── examples/                     # Practical examples
│   ├── basic/
│   ├── intermediate/
│   └── advanced/
├── templates/                    # Code templates
├── scripts/                      # Helper scripts
└── reference/                    # Reference material
```

## Database Schema

### Skills Tables

```sql
CREATE TABLE default_skills (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(100) NOT NULL UNIQUE,
    description TEXT NOT NULL,
    category VARCHAR(50) NOT NULL,
    file_name VARCHAR(100) NOT NULL,
    skill_content TEXT,
    metadata JSON,
    is_active BOOLEAN DEFAULT TRUE,
    is_favorite BOOLEAN DEFAULT FALSE,
    created_at DATETIME,
    updated_at DATETIME
);

CREATE TABLE custom_skills (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id VARCHAR REFERENCES projects(id),
    name VARCHAR(100) NOT NULL,
    description TEXT NOT NULL,
    category VARCHAR(50) NOT NULL,
    file_name VARCHAR(100) NOT NULL,
    skill_content TEXT,
    metadata JSON,
    status VARCHAR(20) DEFAULT 'active',
    error_message TEXT,
    created_by VARCHAR(100),
    is_favorite BOOLEAN DEFAULT FALSE,
    created_at DATETIME,
    updated_at DATETIME
);

CREATE TABLE project_skills (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id VARCHAR REFERENCES projects(id),
    skill_id INTEGER NOT NULL,
    skill_type VARCHAR(10) NOT NULL,  -- 'default' or 'custom'
    enabled_at DATETIME,
    enabled_by VARCHAR(100)
);
```

## Available Default Skills

### 1. Unit Testing (NEW - 2025-11-25)

**Purpose**: Comprehensive unit testing best practices across multiple languages and frameworks

**Location**: `framework-assets/claude-skills/unit-testing/`

**Category**: `testing`

**Content**:
- Test-Driven Development (TDD) workflow
- AAA pattern (Arrange-Act-Assert)
- FIRST principles (Fast, Independent, Repeatable, Self-validating, Timely)
- Test fixture management and setup/teardown
- Mocking strategies (objects, functions, modules)
- Test coverage analysis and improvement
- Parameterized and data-driven testing
- Edge case identification and testing
- Test organization and naming conventions
- Framework-specific guides:
  - Python: pytest, unittest
  - JavaScript/TypeScript: Jest, Vitest, Mocha
  - Comprehensive examples and templates

**Documentation Structure**:
- `README.md` - Overview and quick start
- `SKILL.md` - Complete unit testing guide with TOON format tables
- `examples/python-pytest.md` - Python/pytest examples
- `examples/javascript-jest.md` - JavaScript/Jest examples
- `examples/typescript-vitest.md` - TypeScript/Vitest examples
- `examples/language-examples.md` - Multi-language examples

**Key Features**:
- TOON format tables for structured knowledge
- Copy-pasteable code examples
- Framework comparison matrices
- Best practices checklists
- Anti-patterns to avoid

**When to use**:
- Writing unit tests for new features
- Improving test coverage
- Refactoring tests
- Teaching TDD practices
- Setting up testing frameworks
- Debugging test failures

### 2. Integration Testing (NEW - 2025-11-25)

**Purpose**: End-to-end API and integration testing strategies

**Location**: `framework-assets/claude-skills/integration-testing/`

**Category**: `testing`

**Content**:
- Integration test architecture and patterns
- Test environment setup and isolation
- Database testing strategies (fixtures, seeds, cleanup)
- API endpoint testing (REST, GraphQL, WebSocket)
- Third-party service mocking and stubbing
- Docker-based test environments (Testcontainers, Docker Compose)
- Test data management and factories
- Transaction management and rollback strategies
- CI/CD integration testing pipelines
- Framework-specific guides:
  - Python: pytest with FastAPI/Flask
  - JavaScript: Jest/Supertest with Express
  - Docker Compose test configurations

**Documentation Structure**:
- `README.md` - Integration testing overview
- `SKILL.md` - Complete integration testing guide
- `examples/python-fastapi.md` - FastAPI integration tests with real examples
- `examples/javascript-express.md` - Express integration tests
- `templates/docker-compose.test.yml` - Docker test setup
- `templates/pytest-config.py` - pytest configuration with fixtures
- `templates/jest-config.js` - Jest configuration
- `reference/advanced-patterns.md` - Advanced testing patterns

**Key Features**:
- Test pyramid placement guidance
- Environment setup options comparison
- Transaction rollback pattern
- Test containers pattern
- Factory pattern for test data
- Parallel execution strategies

**When to use**:
- Testing API endpoints
- Setting up integration test suites
- Testing database interactions
- Mocking external services
- CI/CD test pipeline setup
- Database migration testing

### 3. UI Testing (NEW - 2025-11-25)

**Purpose**: Automated UI and browser testing with modern frameworks

**Location**: `framework-assets/claude-skills/ui-testing/`

**Category**: `testing`

**Content**:
- Browser automation with Playwright/Selenium
- Component testing strategies
- Page Object Model (POM) pattern
- Visual regression testing
- Accessibility testing (a11y)
- Cross-browser testing approaches
- Test data management for UI tests
- Screenshot comparison and diffing
- Mobile and responsive testing
- CI/CD integration for UI tests
- Performance testing basics
- Framework-specific guides:
  - Playwright for modern web apps (recommended)
  - React Testing Library for components
  - Cypress for E2E testing
- **NEW**: Playwright MCP Server configuration for AI agents

**Documentation Structure**:
- `README.md` - UI testing overview
- `SKILL.md` - Complete UI testing guide with framework comparison
- `examples/playwright-basic.ts` - Basic Playwright examples
- `examples/page-object-model.ts` - POM pattern implementation
- `examples/visual-regression.ts` - Visual testing examples
- `templates/playwright-config.ts` - Playwright configuration
- `reference/selectors-guide.md` - CSS/XPath selector strategies

**Key Features**:
- Framework comparison matrix (Playwright vs Cypress vs Selenium)
- Playwright MCP configuration for Claude Code
- Test pyramid placement for E2E tests
- When to use vs avoid E2E tests
- Stable selector strategies (data-testid)
- Auto-wait and retry mechanisms

**Playwright MCP Configuration**:
```json
{
  "mcpServers": {
    "playwright": {
      "command": "npx",
      "args": ["@playwright/mcp", "--isolated"]
    }
  }
}
```

**When to use**:
- Writing E2E tests for web applications
- Setting up visual regression testing
- Testing component interactions
- Cross-browser compatibility testing
- Accessibility compliance testing
- Smoke testing after deployment
- Critical user flow validation

### 4. Security Best Practices (NEW - 2025-11-25)

**Purpose**: Application security testing and secure coding practices

**Location**: `framework-assets/claude-skills/security-best-practices/`

**Category**: `security`

**Content**:
- OWASP Top 10 vulnerabilities
- Authentication and authorization patterns
- Input validation and sanitization
- SQL injection prevention
- XSS (Cross-Site Scripting) prevention
- CSRF protection strategies
- Secure session management
- Password hashing and storage (bcrypt, Argon2)
- API security (rate limiting, CORS, JWT)
- Security testing checklist
- Code review security guidelines
- Dependency security scanning

**Documentation Structure**:
- `README.md` - Security overview and quick start
- `SKILL.md` - Complete security guide
- `examples/jwt-authentication.md` - JWT implementation with best practices
- `examples/sql-injection-prevention.md` - SQL injection defense
- `examples/xss-prevention.md` - XSS defense patterns
- `examples/csrf-protection.md` - CSRF token implementation
- `reference/owasp-top-10.md` - OWASP vulnerabilities explained
- `reference/authentication.md` - Auth patterns and JWT security
- `reference/input-validation.md` - Input validation strategies
- `templates/code-review-checklist.md` - Security review checklist

**Key Features**:
- OWASP Top 10 coverage
- Framework-specific examples (FastAPI, Express)
- Security testing methodologies
- Common vulnerability patterns
- Mitigation strategies
- Code review checklists

**When to use**:
- Implementing authentication systems
- Security code reviews
- Preventing common vulnerabilities
- Setting up secure APIs
- Auditing existing code for security issues
- Penetration testing preparation

### 5. Python Refactor (NEW - 2025-11-25)

**Purpose**: Expert Python refactoring using Clean Architecture, DDD, and SOLID principles

**Location**: `framework-assets/claude-skills/refactoring/`

**Category**: `refactoring`

**Content**:
- Legacy code analysis and refactoring opportunities
- Clean Architecture implementation for Python
- Domain-Driven Design patterns (Entities, Value Objects, Aggregates)
- Repository pattern for data access abstraction
- Dependency injection (framework-agnostic with Dishka)
- SOLID principles applied to Python code
- Strangler Fig pattern for incremental migration
- Testing strategy (unit, integration, E2E)
- FastAPI integration with clean architecture
- SQLAlchemy isolation in Infrastructure layer
- **NEW**: Scalability patterns for growing applications

**Documentation Structure**:
- `SKILL.md` - Main refactoring guide
- `reference/clean-architecture.md` - Layered architecture guide
- `reference/domain-modeling.md` - DDD entities and value objects
- `reference/repository-pattern.md` - Data access abstraction
- `reference/dependency-injection.md` - DI patterns in Python
- `reference/strangler-fig.md` - Incremental refactoring strategy
- `docs/scalability-patterns.md` - **NEW**: Performance and scaling strategies
- `examples/fastapi-clean-arch.md` - FastAPI clean architecture example
- `examples/legacy-refactoring.md` - Step-by-step legacy code refactoring
- `templates/entity-template.py` - Domain entity template
- `templates/repository-template.py` - Repository implementation template
- `templates/use-case-template.py` - Use case/service layer template

**Scalability Patterns (NEW)**:
- Database optimization (indexing, query optimization, connection pooling)
- Caching strategies (Redis, in-memory caching)
- Async processing with Celery
- Load balancing and horizontal scaling
- Database sharding and read replicas
- Event-driven architecture

**When to use**:
- Refactoring legacy Python code
- Implementing clean architecture in Python
- Applying DDD patterns
- Isolating database logic from business logic
- Setting up dependency injection
- Migrating monoliths incrementally
- Structuring FastAPI applications
- Planning scalability improvements

### 6. React Refactor (NEW - 2025-11-25)

**Purpose**: Expert React refactoring using Clean Architecture and modern hooks

**Location**: `framework-assets/claude-skills/react-refactor/`

**Category**: `refactoring`

**Content**:
- Legacy React component analysis
- Clean Architecture for React applications
- Component pattern migration (HOC/Render Props to Hooks)
- State management refactoring (Context, Redux, Zustand, Jotai)
- Performance optimization (memo, useMemo, useCallback, virtualization)
- TypeScript integration with React
- Class to functional component conversion
- Testing strategy with React Testing Library and Jest
- Design system and component library patterns
- Next.js clean architecture

**Documentation Structure**:
- `SKILL.md` - React refactoring guide
- `reference/clean-architecture.md` - React layered architecture
- `reference/component-patterns.md` - Modern component patterns
- `reference/state-management.md` - State management solutions
- `reference/performance.md` - Performance optimization techniques
- `reference/testing-patterns.md` - RTL and Jest patterns
- `examples/nextjs-clean-arch.md` - Next.js clean architecture example
- `examples/legacy-migration.md` - Class to functional migration
- `templates/component-template.tsx` - Component structure template
- `templates/hook-template.tsx` - Custom hook template
- `templates/context-template.tsx` - Context provider template

**When to use**:
- Refactoring legacy React code
- Converting class components to functional
- Implementing clean architecture in React
- Fixing prop drilling issues
- Optimizing React performance
- Adding TypeScript to React projects
- Structuring Next.js applications
- Creating design systems

### 7. Merge Skill

**Purpose**: Comprehensive Git branch merging strategies and conflict resolution

**Location**: `framework-assets/claude-skills/merge-skill/`

**Category**: `git`

**Content**:
- Branch merging strategies (fast-forward, 3-way merge, rebase, squash)
- Pre-merge validation checklist
- Conflict detection and markers analysis
- Manual conflict resolution techniques
- Tool-assisted resolution (mergetool, diff3)
- Complex scenarios (renamed files, binary conflicts, submodules)
- Large refactoring merge strategies
- Recovery techniques (abort, revert, cherry-pick)
- Best practices for team collaboration

**Documentation Structure**:
- `SKILL.md` - Main merge skill guide
- `docs/best-practices.md` - Professional merge workflows
- `docs/merge-strategies.md` - Different merge approaches
- `docs/conflict-resolution.md` - Resolving conflicts step-by-step
- `docs/complex-scenarios.md` - Advanced merge situations
- `docs/recovery.md` - Undo and recovery techniques
- `examples/simple-merge.md` - Basic merge workflows
- `examples/text-conflicts.md` - Text conflict resolution examples

**When to use**:
- Merging feature branches into main
- Resolving merge conflicts
- Handling complex merge scenarios
- Planning large-scale merges
- Teaching Git merge best practices
- Reviewing merge strategies

### 8. Architecture Patterns (ENHANCED - 2025-11-25)

**Purpose**: Comprehensive software architecture guidance with infrastructure and scalability patterns

**Location**: `framework-assets/claude-skills/architecture-patterns/`

**Category**: `architecture`

**Content**:
- SOLID principles with practical examples
- DRY, KISS, YAGNI principles
- Clean Architecture layers
- Domain-Driven Design (DDD)
- Design Patterns (Creational, Structural, Behavioral)
- Anti-patterns to avoid
- Backend Python examples
- Frontend React examples
- **NEW**: Decision frameworks - Practical decision trees for architecture choices
- **NEW**: Infrastructure patterns - Microservices, Docker, Kubernetes, high availability
- **NEW**: Scalability patterns - Load balancing, caching strategies, database optimization

**Documentation Structure**:
- `SKILL.md` - Core architecture patterns guide
- `reference/decision-frameworks.md` - **NEW**: Decision trees for optimization, caching, scaling
- `reference/infrastructure-patterns.md` - **NEW**: Microservices, containerization, orchestration

**Decision Frameworks (NEW)**:
- When to optimize (traffic thresholds, response time targets)
- Caching strategy selection (Redis, CDN, application-level)
- Database scaling decisions (vertical vs horizontal, sharding)
- Microservices vs monolith decision tree
- Event-driven architecture patterns

**Infrastructure Patterns (NEW)**:
- Microservices architecture (API Gateway, Service Mesh)
- Containerization with Docker
- Orchestration with Kubernetes
- High availability patterns (load balancing, failover)
- Message queues (RabbitMQ, Kafka)
- API Gateway patterns

**When to use**:
- Designing system architecture
- Refactoring existing code
- Code review for architectural quality
- Teaching architectural concepts
- Planning infrastructure and scalability
- Making optimization decisions
- Migrating to microservices
- Implementing event-driven systems

### 9. Requirements Analysis

**Purpose**: Business requirements gathering and documentation

**Location**: `framework-assets/claude-configs/skills/requirements-analysis/`

**Category**: `analysis`

**Content**:
- Discovery questions framework
- User story templates
- Acceptance criteria patterns
- Non-functional requirements
- Business requirements documentation
- Stakeholder communication patterns

**When to use**:
- Starting new features or projects
- Gathering business requirements
- Writing user stories
- Defining acceptance criteria
- Planning sprint work

### 10. Technical Design

**Purpose**: Technical specification and system design

**Location**: `framework-assets/claude-configs/skills/technical-design/`

**Category**: `design`

**Content**:
- System architecture documentation
- API design patterns
- Database schema design
- Component interaction diagrams
- Technical decision records (ADRs)

**When to use**:
- Designing new features
- Creating technical specifications
- Documenting architecture decisions
- Planning system integrations

## Skill Assignment to Subagents

Skills can be automatically assigned to subagents based on their role:

### API Endpoint

**POST** `/api/projects/{project_id}/subagents/{subagent_id}/skills`

**Request Body**:
```json
{
  "skill_ids": [1, 2, 3],
  "skill_type": "default"
}
```

**Behavior**:
1. Assigns skills to subagent in database
2. Copies skill files to subagent's `.claude/skills/` directory
3. Syncs skills whenever subagent launches

### File Synchronization

When a subagent task launches:
```python
# Automatically sync skills to subagent's .claude/skills/
subagent_service.sync_skills_to_subagent(subagent_id, worktree_path)
```

**Skill File Structure in Worktree**:
```
worktrees/{task_id}/.claude/skills/
├── unit-testing/
│   ├── SKILL.md
│   ├── README.md
│   └── examples/
├── integration-testing/
│   └── ...
└── security-best-practices/
    └── ...
```

## Skill Categories

| Category | Purpose | Example Skills |
|----------|---------|----------------|
| `testing` | Testing methodologies and tools | Unit Testing, Integration Testing, UI Testing |
| `security` | Security practices and vulnerabilities | Security Best Practices, OWASP Top 10 |
| `refactoring` | Code improvement and architecture | Python Refactor, React Refactor |
| `architecture` | System design and patterns | Architecture Patterns, Design Patterns |
| `git` | Version control workflows | Merge Skill, Git Best Practices |
| `analysis` | Requirements and planning | Requirements Analysis, User Stories |
| `design` | Technical specifications | Technical Design, API Design |

## TOON Format

Skills use TOON (Table-Oriented Object Notation) for structured knowledge representation:

```
skill_categories[3]{category,purpose,example_skills}:
testing,Testing methodologies and tools,Unit Testing Integration Testing UI Testing
security,Security practices and vulnerabilities,Security Best Practices OWASP Top 10
refactoring,Code improvement and architecture,Python Refactor React Refactor
```

**Benefits**:
- Compact representation
- Easy parsing by AI
- Clear structure
- Type information
- Relationship mapping

## Skill Frontmatter

Each skill's main file includes YAML frontmatter:

```yaml
---
name: unit-testing
description: Comprehensive unit testing best practices
version: 1.0.0
tags: [testing, unit-tests, tdd, quality, pytest, jest]
---
```

## Migration: Add Testing Skills

**Migration**: `claudetask/backend/migrations/add_testing_skills.py`

**Adds**:
1. Unit Testing skill
2. Integration Testing skill
3. UI Testing skill
4. Security Best Practices skill

**Updates**:
1. Architecture Patterns skill (adds decision frameworks and infrastructure patterns)
2. Python Refactor skill (adds scalability patterns)

## Testing Configuration Fields

**Migration**: `011_add_testing_config_fields.sql`

**New columns in `project_settings`**:
- `test_directory`: Default test directory (default: 'tests')
- `test_framework`: Default test framework (default: 'pytest')
- `auto_merge_tests`: Auto-merge test files from staging (default: true)
- `test_staging_dir`: Staging directory for test files (default: 'tests/staging')

**API Endpoints**:
```
GET /api/projects/{project_id}/settings
PUT /api/projects/{project_id}/settings
```

## Skill Usage Patterns

### 1. Testing Workflow with Skills

```
1. Enable "Unit Testing" skill for project
2. Assign skill to backend subagent
3. Create task: "Add unit tests for UserService"
4. Subagent receives unit testing knowledge
5. Implements tests following skill guidelines
6. Uses pytest patterns from skill examples
```

### 2. Security Review with Skills

```
1. Enable "Security Best Practices" skill
2. Create task: "Security audit of authentication"
3. Agent references OWASP Top 10 from skill
4. Applies JWT security patterns from examples
5. Generates security review checklist
```

### 3. Refactoring with Skills

```
1. Enable "Python Refactor" skill
2. Create task: "Refactor payment service to Clean Architecture"
3. Agent follows clean architecture layers
4. Implements repository pattern from templates
5. Uses dependency injection patterns
6. References scalability patterns for optimization
```

## Best Practices

### Skill Organization

1. **Modular Structure**: Keep skills focused on single responsibility
2. **Comprehensive Examples**: Include copy-pasteable code examples
3. **TOON Format**: Use tables for structured knowledge
4. **Clear Documentation**: Maintain README and SKILL.md consistency
5. **Version Control**: Track skill changes with version numbers

### Skill Assignment

1. **Role-Based**: Assign skills based on subagent role
2. **Selective**: Don't assign all skills to all agents
3. **Project-Specific**: Enable only relevant skills per project
4. **Sync on Launch**: Skills auto-sync when subagent starts

### Skill Maintenance

1. **Regular Updates**: Keep examples current with framework versions
2. **Deprecation**: Mark outdated patterns as deprecated
3. **Migration Paths**: Provide upgrade guides for major changes
4. **Testing**: Validate examples in CI/CD

## Future Enhancements

1. **Skill Dependencies**: Skills can require other skills
2. **Skill Versioning**: Track skill versions and auto-update
3. **Skill Analytics**: Track skill usage and effectiveness
4. **Skill Marketplace**: Community-contributed skills
5. **Skill Composition**: Combine multiple skills into workflows
6. **AI-Generated Skills**: Generate skills from codebases
