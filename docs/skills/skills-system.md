# Skills System

Complete guide to the Skills system in the Claude Code Feature Framework.

## Overview

The Skills system provides modular, reusable knowledge modules that extend Claude Code's capabilities. Skills are structured documentation bundles that Claude Code can reference to perform specialized tasks.

## Architecture

### Skill Types

1. **Default Skills**: Framework-provided skills in `framework-assets/claude-configs/skills/`
2. **Custom Skills**: Project-specific skills in `.claude/skills/`
3. **Enabled Skills**: Skills active in a specific project (tracked in database)

### Skill Structure

Each skill follows a standardized structure:

```
skill-name/
├── SKILL.md                      # Main skill file with frontmatter
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

## Available Default Skills

### 1. Merge Skill (NEW)

**Purpose**: Comprehensive Git branch merging strategies and conflict resolution

**Location**: `framework-assets/claude-skills/merge-skill/`

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

### 2. Python Refactor Skill (NEW)

**Purpose**: Expert Python refactoring using Clean Architecture, DDD, and SOLID principles

**Location**: `framework-assets/claude-skills/python-refactor/`

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

**Documentation Structure**:
- `reference/clean-architecture.md` - Layered architecture guide
- `reference/domain-modeling.md` - DDD entities and value objects
- `reference/repository-pattern.md` - Data access abstraction
- `reference/dependency-injection.md` - DI patterns in Python
- `reference/strangler-fig.md` - Incremental refactoring strategy
- `examples/fastapi-clean-arch.md` - FastAPI clean architecture example
- `examples/legacy-refactoring.md` - Step-by-step legacy code refactoring
- `templates/entity-template.py` - Domain entity template
- `templates/repository-template.py` - Repository implementation template
- `templates/use-case-template.py` - Use case/service layer template

**When to use**:
- Refactoring legacy Python code
- Implementing clean architecture in Python
- Applying DDD patterns
- Isolating database logic from business logic
- Setting up dependency injection
- Migrating monoliths incrementally
- Structuring FastAPI applications

### 3. React Refactor Skill (NEW)

**Purpose**: Expert React refactoring using Clean Architecture and modern hooks

**Location**: `framework-assets/claude-skills/react-refactor/`

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

### 4. Unit Testing Skill (NEW)

**Purpose**: Comprehensive unit testing across multiple languages and frameworks

**Location**: `framework-assets/claude-skills/unit-testing/`

**Content**:
- Test-Driven Development (TDD) workflow
- AAA pattern (Arrange-Act-Assert)
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
- `SKILL.md` - Complete unit testing guide
- `examples/python-pytest.md` - Python/pytest examples
- `examples/javascript-jest.md` - JavaScript/Jest examples
- `examples/typescript-vitest.md` - TypeScript/Vitest examples
- `templates/test-template.py` - Unit test templates

**When to use**:
- Writing unit tests for new features
- Improving test coverage
- Refactoring tests
- Teaching TDD practices
- Setting up testing frameworks

### 5. Integration Testing Skill (NEW)

**Purpose**: End-to-end API and integration testing strategies

**Location**: `framework-assets/claude-skills/integration-testing/`

**Content**:
- Integration test architecture and patterns
- Test environment setup and isolation
- Database testing strategies (fixtures, seeds, cleanup)
- API endpoint testing (REST, GraphQL, WebSocket)
- Third-party service mocking and stubbing
- Docker-based test environments
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
- `examples/python-fastapi.md` - FastAPI integration tests
- `examples/javascript-express.md` - Express integration tests
- `templates/docker-compose.test.yml` - Docker test setup
- `templates/pytest-config.py` - pytest configuration
- `templates/jest-config.js` - Jest configuration
- `reference/advanced-patterns.md` - Advanced testing patterns

**When to use**:
- Testing API endpoints
- Setting up integration test suites
- Testing database interactions
- Mocking external services
- CI/CD test pipeline setup

### 6. UI Testing Skill (NEW)

**Purpose**: Automated UI and browser testing with modern frameworks

**Location**: `framework-assets/claude-skills/ui-testing/`

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
  - Playwright for modern web apps
  - React Testing Library for components
  - Cypress for E2E testing

**Documentation Structure**:
- `README.md` - UI testing overview
- `SKILL.md` - Complete UI testing guide
- `examples/playwright-basic.ts` - Basic Playwright examples
- `examples/page-object-model.ts` - POM pattern implementation
- `examples/visual-regression.ts` - Visual testing examples
- `templates/playwright-config.ts` - Playwright configuration
- `reference/selectors-guide.md` - CSS/XPath selector strategies

**When to use**:
- Writing E2E tests for web applications
- Setting up visual regression testing
- Testing component interactions
- Cross-browser compatibility testing
- Accessibility compliance testing

### 7. Security Best Practices Skill (NEW)

**Purpose**: Application security testing and secure coding practices

**Location**: `framework-assets/claude-skills/security-best-practices/`

**Content**:
- OWASP Top 10 vulnerabilities
- Authentication and authorization patterns
- Input validation and sanitization
- SQL injection prevention
- XSS (Cross-Site Scripting) prevention
- CSRF protection strategies
- Secure session management
- Password hashing and storage
- API security (rate limiting, CORS)
- Security testing checklist
- Code review security guidelines

**Documentation Structure**:
- `README.md` - Security overview
- `SKILL.md` - Complete security guide
- `examples/jwt-authentication.md` - JWT implementation
- `examples/sql-injection-prevention.md` - SQL injection defense
- `examples/xss-prevention.md` - XSS defense patterns
- `examples/csrf-protection.md` - CSRF token implementation
- `reference/owasp-top-10.md` - OWASP vulnerabilities
- `reference/authentication.md` - Auth patterns
- `reference/input-validation.md` - Input validation strategies
- `templates/code-review-checklist.md` - Security review checklist

**When to use**:
- Implementing authentication systems
- Security code reviews
- Preventing common vulnerabilities
- Setting up secure APIs
- Auditing existing code for security issues

### 8. Architecture Patterns (ENHANCED)

**Purpose**: Comprehensive software architecture guidance with infrastructure and scalability patterns

**Location**: `framework-assets/claude-skills/architecture-patterns/`

**Content**:
- SOLID principles with practical examples
- DRY, KISS, YAGNI principles
- Clean Architecture layers
- Domain-Driven Design (DDD)
- Design Patterns (Creational, Structural, Behavioral)
- Anti-patterns to avoid
- Backend Python examples
- Frontend React examples
- **NEW: Decision frameworks** - Practical decision trees for architecture choices
- **NEW: Infrastructure patterns** - Microservices, Docker, Kubernetes, high availability
- **NEW: Scalability patterns** - Load balancing, caching strategies, database optimization

**Documentation Structure**:
- `SKILL.md` - Core architecture patterns guide
- `reference/decision-frameworks.md` - Decision trees for optimization, caching, scaling
- `reference/infrastructure-patterns.md` - Microservices, containerization, orchestration

**When to use**:
- Designing system architecture
- Refactoring existing code
- Code review for architectural quality
- Teaching architectural concepts
- Planning infrastructure and scalability
- Making optimization decisions

### 9. Requirements Analysis

**Purpose**: Business requirements gathering and documentation

**Location**: `framework-assets/claude-configs/skills/requirements-analysis/`

**Content**:
- Discovery questions framework
- User story templates
- Acceptance criteria patterns
- Non-functional requirements
- Business requirements documentation

**When to use**:
- Starting new feature development
- Gathering requirements from stakeholders
- Creating comprehensive requirements documentation

### 10. Technical Design

**Purpose**: Technical specification and architecture documentation

**Location**: `framework-assets/claude-configs/skills/technical-design/`

**Content**:
- System architecture patterns
- Component design
- API design
- Database design
- Integration patterns

**When to use**:
- Creating technical specifications
- Designing system components
- Planning implementation approach

### 11. TOON Format

**Purpose**: Token-efficient data serialization

**Location**: `framework-assets/claude-configs/skills/toon-format/`

**Content**:
- TOON (Token-Optimized Object Notation) syntax
- 30-60% token savings vs JSON/XML
- Compact data representation
- Examples and reference

**When to use**:
- Serializing large data structures
- Optimizing token usage
- Storing structured data compactly

### 12. UseCase Writer

**Purpose**: Professional use case documentation

**Location**: `framework-assets/claude-configs/skills/usecase-writer/`

**Content**:
- UML use case diagrams
- Cockburn use case format
- IEEE 830 compliance
- Actor-goal-outcome patterns

**When to use**:
- Creating formal use case documentation
- Requirements engineering
- System behavior specification

### 13. API Development

**Purpose**: RESTful API design and implementation

**Location**: `framework-assets/claude-configs/skills/api-development/`

**Content**:
- REST API design principles
- FastAPI best practices
- Endpoint patterns
- Request/response schemas
- Error handling
- API documentation

**When to use**:
- Building new API endpoints
- Designing API architecture
- API documentation

### 14. API Integration

**Purpose**: Third-party API integration patterns

**Location**: `framework-assets/claude-configs/skills/api-integration/`

**Content**:
- HTTP client patterns
- Authentication strategies
- Rate limiting handling
- Error handling and retries
- Testing API integrations

**When to use**:
- Integrating external APIs
- Building API clients
- Handling API errors

### 15. UI Component Development

**Purpose**: React component development patterns

**Location**: `framework-assets/claude-configs/skills/ui-component/`

**Content**:
- React component architecture
- TypeScript patterns
- Styling guide (Material-UI)
- Accessibility standards
- Performance optimization
- Testing strategies

**When to use**:
- Building React components
- UI/UX implementation
- Frontend architecture

### 16. Code Review

**Purpose**: Comprehensive code review guidelines

**Location**: `framework-assets/claude-configs/skills/code-review/`

**Content**:
- Code quality checklist
- Security review
- Performance review
- Best practices validation
- Review templates

**When to use**:
- Reviewing pull requests
- Code quality assessment
- Mentoring developers

### 17. Database Migration

**Purpose**: Database schema evolution

**Location**: `framework-assets/claude-configs/skills/database-migration/`

**Content**:
- Migration patterns
- Alembic usage
- Schema versioning
- Data migration strategies
- Rollback procedures

**When to use**:
- Creating database migrations
- Evolving database schema
- Data migration tasks

### 18. Debug Helper

**Purpose**: Debugging strategies and tools

**Location**: `framework-assets/claude-configs/skills/debug-helper/`

**Content**:
- Debugging techniques
- Logging best practices
- Error analysis
- Performance profiling
- Common debugging patterns

**When to use**:
- Troubleshooting bugs
- Performance issues
- System behavior analysis

### 19. Deployment Helper

**Purpose**: Deployment and DevOps guidance

**Location**: `framework-assets/claude-configs/skills/deployment-helper/`

**Content**:
- Deployment strategies
- CI/CD patterns
- Environment configuration
- Health checks
- Monitoring setup

**When to use**:
- Setting up deployments
- CI/CD configuration
- Production environment setup

### 20. Documentation Writer

**Purpose**: Technical documentation creation

**Location**: `framework-assets/claude-configs/skills/documentation-writer/`

**Content**:
- Documentation templates
- API documentation
- User guides
- Architecture documentation
- Code comments

**When to use**:
- Writing documentation
- Creating API docs
- User guide creation

### 21. Git Workflow

**Purpose**: Git version control patterns

**Location**: `framework-assets/claude-configs/skills/git-workflow/`

**Content**:
- Branching strategies
- Commit message conventions
- Merge strategies
- Conflict resolution
- Git worktrees

**When to use**:
- Managing git repositories
- Resolving conflicts
- Branch management

### 18. Refactoring

**Purpose**: Code refactoring strategies

**Location**: `framework-assets/claude-configs/skills/refactoring/`

**Content**:
- Refactoring patterns
- Code smell detection
- Safety checks
- Testing during refactoring
- Incremental refactoring

**When to use**:
- Improving code quality
- Reducing technical debt
- Code cleanup

### 19. Test Runner

**Purpose**: Testing strategies and execution

**Location**: `framework-assets/claude-configs/skills/test-runner/`

**Content**:
- Unit testing patterns
- Integration testing
- Test automation
- Coverage analysis
- Test organization

**When to use**:
- Writing tests
- Running test suites
- Test automation setup

## Skill Management

### Enabling Skills

**UI Method**:
1. Navigate to Skills page
2. Find skill in "Available Default" or "Custom" list
3. Click "Enable" button
4. Skill files copied to `.claude/skills/`
5. Skill registered in project_skills database table

**API Method**:
```bash
POST /api/projects/{project_id}/skills/enable/{skill_id}
```

**Result**:
- Skill files copied to `.claude/skills/[skill-name]/`
- Database record created in project_skills table
- Skill available to Claude Code in this project

### Disabling Skills

**UI Method**:
1. Navigate to Skills page
2. Find skill in "Enabled" list
3. Click "Disable" button
4. Skill files removed from `.claude/skills/`
5. Database record removed from project_skills table

**API Method**:
```bash
POST /api/projects/{project_id}/skills/disable/{skill_id}
```

**Result**:
- Skill files deleted from `.claude/skills/[skill-name]/`
- Database record removed (skill remains in default_skills or custom_skills)

### Creating Custom Skills

**Manual Method**:
1. Create directory: `.claude/skills/my-skill/`
2. Create main file: `.claude/skills/my-skill/SKILL.md`
3. Add frontmatter:
```markdown
---
name: my-skill
description: Brief description
category: custom
tags: [tag1, tag2]
---

# My Custom Skill

Skill content here...
```
4. Add supporting files (docs/, examples/, templates/)
5. Register via Skills page "Create Custom Skill" button

**Slash Command Method**:
```
/create-skill my-skill
```

Automatically creates skill template in `.claude/skills/my-skill/`

## Skill Frontmatter

All skill files must include frontmatter:

```yaml
---
name: skill-name
description: Brief description of skill purpose
category: architecture | development | testing | deployment | documentation
tags: [tag1, tag2, tag3]
version: 1.0.0
author: Author name (optional)
dependencies: [other-skill-name] (optional)
---
```

## Skill Categories

- **Architecture**: System design, patterns, principles
- **Development**: Coding, implementation, debugging
- **Testing**: Test strategies, automation, coverage
- **Deployment**: CI/CD, infrastructure, monitoring
- **Documentation**: Technical writing, API docs, guides

## Using Skills in Claude Code

### Implicit Usage

When a skill is enabled, Claude Code automatically has access to its content:

```
User: "Design a new REST API endpoint following best practices"

Claude Code:
- Reads api-development skill
- Applies REST principles
- Uses FastAPI patterns
- Implements proper error handling
```

### Explicit Reference

Reference specific skills in prompts:

```
User: "Using the Architecture Patterns skill, refactor this component to follow SOLID principles"

Claude Code:
- Reads architecture-patterns skill
- Focuses on SOLID principles
- Applies refactoring patterns
- Provides specific recommendations
```

### Agent Access

Specialized agents have automatic access to relevant skills:

```python
# System Architect agent has access to:
- architecture-patterns skill
- technical-design skill
- api-development skill

# Frontend Developer agent has access to:
- ui-component skill
- architecture-patterns skill
```

## Best Practices

### For Skill Authors

1. **Clear Structure**: Follow standard skill directory structure
2. **Comprehensive Docs**: Include all standard doc files
3. **Practical Examples**: Provide working code examples
4. **Version Control**: Track skill versions in frontmatter
5. **Dependencies**: Document skill dependencies clearly

### For Skill Users

1. **Enable Selectively**: Only enable skills you need
2. **Review Content**: Read skill docs before using
3. **Provide Context**: Reference specific skills when needed
4. **Update Regularly**: Keep skills updated with framework
5. **Report Issues**: Flag outdated or incorrect content

### For Project Maintainers

1. **Curate Skills**: Enable relevant default skills for your project
2. **Create Custom**: Build project-specific custom skills
3. **Share Knowledge**: Document team patterns as skills
4. **Keep Current**: Update skills as patterns evolve
5. **Clean Up**: Disable unused skills

## Skill Development

### Creating a New Default Skill

1. **Create structure**:
```bash
mkdir -p framework-assets/claude-configs/skills/my-skill/{docs,examples,templates,scripts}
touch framework-assets/claude-configs/skills/my-skill/SKILL.md
```

2. **Write SKILL.md**:
```markdown
---
name: my-skill
description: My new skill
category: development
tags: [python, fastapi]
version: 1.0.0
---

# My New Skill

## Purpose
[Clear statement of skill purpose]

## When to Use
[Specific scenarios where this skill applies]

## Core Concepts
[Key concepts and principles]

## Practical Guide
[Step-by-step usage instructions]

## Examples
See examples/ directory for working code.
```

3. **Add documentation**:
```bash
touch framework-assets/claude-configs/skills/my-skill/docs/core-concepts.md
touch framework-assets/claude-configs/skills/my-skill/docs/best-practices.md
touch framework-assets/claude-configs/skills/my-skill/docs/patterns.md
```

4. **Add examples**:
```bash
mkdir -p framework-assets/claude-configs/skills/my-skill/examples/{basic,intermediate,advanced}
```

5. **Register in database**:
```sql
INSERT INTO default_skills (name, description, category, file_path)
VALUES ('my-skill', 'My new skill', 'development', 'framework-assets/claude-configs/skills/my-skill/SKILL.md');
```

## Troubleshooting

### Skill Not Available

**Symptom**: Enabled skill not accessible to Claude Code

**Solutions**:
- Verify skill files exist in `.claude/skills/`
- Check database record in project_skills table
- Restart Claude Code session
- Re-enable skill via UI

### Skill Content Outdated

**Symptom**: Skill provides outdated guidance

**Solutions**:
- Check skill version in frontmatter
- Compare with latest framework version
- Update skill files from framework-assets
- Report issue to maintainers

### Conflicting Skills

**Symptom**: Two skills provide contradictory guidance

**Solutions**:
- Review both skills
- Identify contradiction
- Follow more specific skill
- Disable less relevant skill

## Related Documentation

- [TOON Format Skill](./toon-format.md) - Token-efficient serialization
- [UseCase Writer Skill](./usecase-writer.md) - Use case documentation
- [Skills API](../api/endpoints/skills.md) - Skills management API

---

**Last Updated**: 2025-11-25
**Version**: 2.1.0
**Total Default Skills**: 21
**Total Categories**: 5
**Latest Additions**: Unit Testing, Integration Testing, UI Testing, Security Best Practices, enhanced Architecture Patterns with infrastructure patterns and decision frameworks
