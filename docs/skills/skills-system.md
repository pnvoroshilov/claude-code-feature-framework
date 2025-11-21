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

### 1. Architecture Patterns

**Purpose**: Comprehensive software architecture guidance

**Location**: `framework-assets/claude-configs/skills/architecture-patterns/`

**Content**:
- SOLID principles with practical examples
- DRY, KISS, YAGNI principles
- Clean Architecture layers
- Domain-Driven Design (DDD)
- Design Patterns (Creational, Structural, Behavioral)
- Anti-patterns to avoid
- Backend Python examples
- Frontend React examples

**When to use**:
- Designing system architecture
- Refactoring existing code
- Code review for architectural quality
- Teaching architectural concepts

### 2. Requirements Analysis

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

### 3. Technical Design

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

### 4. TOON Format

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

### 5. UseCase Writer

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

### 6. API Development

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

### 7. API Integration

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

### 8. UI Component Development

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

### 9. Code Review

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

### 10. Database Migration

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

### 11. Debug Helper

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

### 12. Deployment Helper

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

### 13. Documentation Writer

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

### 14. Git Workflow

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

### 15. Refactoring

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

### 16. Test Runner

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

**Last Updated**: 2025-11-21
**Version**: 1.0.0
**Total Default Skills**: 16
**Total Categories**: 5
