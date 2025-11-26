# Agent Skills System

Comprehensive guide to the agent skills integration system in the Claude Code Feature Framework.

## Overview

The Agent Skills System enables framework agents to have **mandatory skills** that they must invoke before performing their specialized tasks. This system ensures agents leverage structured knowledge modules for consistent, high-quality outputs.

## Architecture

### Agent File Structure

Every framework agent now includes a `skills` field in its YAML frontmatter:

```yaml
---
name: documentation-updater-agent
description: Automatically update, create, and manage project documentation
tools: Read, Write, Edit, Glob, Grep, Bash
skills: documentation-writer, technical-design, git-workflow
---
```

### Mandatory Skills Section

All agents include a standardized "MANDATORY: Use Assigned Skills" section after the frontmatter:

```markdown
## 🎯 MANDATORY: Use Assigned Skills

**IMPORTANT**: You MUST use the following skills during your work:

**Skills to invoke**: `documentation-writer, technical-design, git-workflow`

### How to Use Skills

Before starting your task, invoke each assigned skill using the Skill tool:

```
Skill: "documentation-writer"
Skill: "technical-design"
Skill: "git-workflow"
```

### Assigned Skills Details

#### Documentation Writer (`documentation-writer`)
**Category**: Documentation

Comprehensive skill for creating professional, clear, and maintainable technical documentation

#### Technical Design (`technical-design`)
**Category**: Architecture

Comprehensive document formats and templates for technical architecture design and test cases

#### Git Workflow (`git-workflow`)
**Category**: DevOps

Comprehensive guidance for advanced Git workflow management with branching strategies and collaboration patterns
```

## Skills Assignment Strategy

### By Agent Category

**Development Agents** (Frontend, Backend, Python, Mobile):
- `architecture-patterns` - Design patterns and principles
- `debug-helper` - Systematic debugging assistance
- Language-specific refactoring skills (`python-refactor`, `react-refactor`)
- `documentation-writer` - Code documentation standards

**Analysis Agents** (Business, Requirements, Systems):
- `usecase-writer` - Requirements documentation
- `technical-design` - Architecture design templates
- `documentation-writer` - Analysis documentation
- `toon-format` - Structured data representation

**Architecture Agents** (System, Backend, Frontend, DevOps):
- `architecture-patterns` - Software architecture guidance
- `technical-design` - Design documentation
- `git-workflow` - Branching and versioning strategies
- Domain-specific patterns

**Testing Agents** (Quality Engineer, Web Tester):
- `unit-testing` - Unit test best practices
- `integration-testing` - Integration test strategies
- `ui-testing` - Browser automation and Playwright
- `debug-helper` - Test debugging

**Quality Agents** (Code Reviewer, Refactoring Expert):
- Language-specific refactoring skills
- `architecture-patterns` - Code quality patterns
- `debug-helper` - Issue analysis
- `documentation-writer` - Quality documentation

**DevOps Agents** (DevOps Engineer, DevOps Architect):
- `git-workflow` - Advanced Git operations
- `docker-patterns` - Container best practices
- `ci-cd-patterns` - Pipeline design (when available)
- `technical-design` - Infrastructure documentation

**Documentation Agents** (Technical Writer, Docs Generator, Documentation Updater):
- `documentation-writer` - **PRIMARY SKILL**
- `technical-design` - Design documentation
- `toon-format` - Data structure documentation
- `git-workflow` - Documentation versioning

**Security Agents** (Security Engineer):
- `security-patterns` - Security best practices (when available)
- `architecture-patterns` - Secure design patterns
- `debug-helper` - Security issue analysis
- `documentation-writer` - Security documentation

**Specialized Agents** (Agent Creator, Skills Creator, Hook Creator):
- `documentation-writer` - Documentation standards
- `toon-format` - Structured formats
- `technical-design` - System design
- Agent-specific skills

## Skills Integration Workflow

### 1. Agent Invocation

When an orchestrator delegates work to an agent:

```markdown
Task tool with documentation-updater-agent:
"Update API documentation after endpoint changes.

Changes:
- New /api/sessions/{id}/messages endpoint
- Added JSONL parsing functionality
- Updated security validation

Please update docs/api/endpoints/claude-sessions.md"
```

### 2. Skill Loading

The agent **MUST** invoke assigned skills before starting work:

```
Skill: "documentation-writer"
Skill: "technical-design"
Skill: "git-workflow"
```

### 3. Skill Application

Agent applies skill knowledge to the task:

- **Documentation Writer**: Markdown standards, code examples, structure
- **Technical Design**: API documentation templates, schema formats
- **Git Workflow**: Commit message formats, branching strategies

### 4. Task Execution

Agent executes task using skill-guided approach:

```markdown
# UPDATE: docs/api/endpoints/claude-sessions.md

- Endpoint path and parameters documented
- Security validation explained
- Working code examples provided
- OpenAPI 3.0 schema format used
- Commit message: "docs: Update session messages endpoint [skip-hook]"
```

## Benefits

### For Agents

1. **Structured Knowledge**: Access to organized, comprehensive skill documentation
2. **Consistency**: All agents follow same skill-based patterns
3. **Quality Assurance**: Skills enforce best practices automatically
4. **Reduced Errors**: Skills provide debugging and validation guidance
5. **Faster Execution**: Pre-structured templates and patterns

### For Orchestrators

1. **Predictable Outputs**: Skill-guided agents produce consistent results
2. **Delegation Confidence**: Know agents have proper knowledge loaded
3. **Quality Control**: Skills act as quality gates for agent work
4. **Specialization**: Agents equipped with domain-specific expertise

### For Projects

1. **Documentation Quality**: Documentation agents produce standardized docs
2. **Code Quality**: Development agents follow architectural patterns
3. **Test Coverage**: Testing agents apply comprehensive strategies
4. **Security Compliance**: Security agents enforce security patterns

## Skill Categories and Common Assignments

### Development Skills
- `python-refactor` - Python Clean Architecture refactoring
- `react-refactor` - React component refactoring patterns
- `architecture-patterns` - SOLID, DDD, microservices
- `debug-helper` - Root cause analysis and debugging

### Testing Skills
- `unit-testing` - TDD, AAA pattern, FIRST principles
- `integration-testing` - API testing, database testing
- `ui-testing` - Playwright, Selenium, component testing

### Documentation Skills
- `documentation-writer` - **CORE SKILL** for all documentation
- `technical-design` - Architecture diagrams, design docs
- `usecase-writer` - Requirements and use case documentation
- `toon-format` - Structured data representation

### DevOps Skills
- `git-workflow` - Branching, merging, conflict resolution
- `docker-patterns` - Container best practices (when available)
- `merge-skill` - Advanced Git merge strategies

### Architecture Skills
- `architecture-patterns` - Design patterns and principles
- `technical-design` - System design documentation
- Domain-specific patterns

## Agent Skills Matrix

### Frontend Developers
```yaml
skills: architecture-patterns, react-refactor, debug-helper, documentation-writer
```

**Use Cases**:
- Component development with Clean Architecture
- React optimization and refactoring
- UI debugging and troubleshooting
- Component documentation

### Backend Architects
```yaml
skills: architecture-patterns, python-refactor, technical-design, git-workflow
```

**Use Cases**:
- API design with SOLID principles
- Database schema design
- Backend architecture documentation
- Git branching strategies

### Quality Engineers
```yaml
skills: unit-testing, integration-testing, debug-helper, documentation-writer
```

**Use Cases**:
- Comprehensive test suite creation
- Integration test setup
- Test debugging and optimization
- Test documentation

### Documentation Updater
```yaml
skills: documentation-writer, technical-design, git-workflow
```

**Use Cases**:
- API documentation updates
- Architecture documentation
- Documentation versioning
- Git hook integration

### Business Analysts
```yaml
skills: usecase-writer, technical-design, documentation-writer, toon-format
```

**Use Cases**:
- Requirements documentation
- Use case specifications
- Acceptance criteria definition
- Structured data representation

## Skills Enforcement

### Mandatory Invocation

Agents **MUST** invoke assigned skills before starting work. This is enforced through:

1. **Frontmatter Declaration**: `skills` field in YAML
2. **Instructions Section**: Explicit skill invocation instructions
3. **Agent Training**: Agents instructed to use skills first
4. **Quality Gates**: Orchestrators verify skill usage

### Skill Invocation Syntax

```
Skill: "<skill-name>"
```

**Examples**:
```
Skill: "documentation-writer"
Skill: "unit-testing"
Skill: "architecture-patterns"
```

### Multiple Skills

Agents invoke all assigned skills:

```
Skill: "documentation-writer"
Skill: "technical-design"
Skill: "git-workflow"
```

## Framework Agent Updates

### All Agents Updated (2025-11-25)

**Total Agents**: 34 framework agents

**Update Applied**:
1. Added `skills` field to YAML frontmatter
2. Added "MANDATORY: Use Assigned Skills" section
3. Listed assigned skills with descriptions
4. Provided skill invocation instructions

**Example Agents**:
- `documentation-updater-agent.md` - Skills: documentation-writer, technical-design, git-workflow
- `ai-implementation-expert.md` - Skills: architecture-patterns, debug-helper, documentation-writer, python-refactor
- `frontend-developer.md` - Skills: architecture-patterns, react-refactor, debug-helper, documentation-writer
- `quality-engineer.md` - Skills: unit-testing, integration-testing, debug-helper, documentation-writer

### Agent File Location

**Framework Agents**: `framework-assets/claude-agents/*.md`

**Total Files**: 34 agent markdown files

## Skills File Storage

### Default Skills
**Location**: `framework-assets/claude-skills/*/SKILL.md`

**Total Default Skills**: 24 skills

**Categories**:
- Testing (3): unit-testing, integration-testing, ui-testing
- Documentation (3): documentation-writer, technical-design, usecase-writer
- Development (4): python-refactor, react-refactor, architecture-patterns, debug-helper
- Data (1): toon-format
- DevOps (2): git-workflow, merge-skill
- Others (11): Various specialized skills

### Custom Skills
**Location**: `.claude/skills/*/SKILL.md` (project-specific)

**Database**: `custom_skills` table

## Skill Synchronization

### Agent Skill Assignment

When skills are assigned to an agent via API:

```bash
PUT /api/projects/{project_id}/subagents/{agent_id}/skills
{
  "skill_ids": [1, 5, 8],
  "skill_types": ["default", "default", "default"]
}
```

**Synchronization Process**:
1. Database records created in `subagent_skills` table
2. Skill files copied to `.claudetask/agents/{agent_name}/skills/`
3. Agent markdown updated with skill references
4. Skills available for immediate use

### Skill File Structure

```
.claudetask/agents/backend-architect/
├── AGENT.md                    # Agent with skill references
├── skills/
│   ├── architecture-patterns/
│   │   ├── SKILL.md
│   │   ├── docs/
│   │   ├── examples/
│   │   ├── templates/
│   │   └── reference/
│   ├── python-refactor/
│   │   ├── SKILL.md
│   │   ├── docs/
│   │   ├── examples/
│   │   └── templates/
│   └── technical-design/
│       ├── SKILL.md
│       ├── docs/
│       ├── examples/
│       └── templates/
```

## API Integration

### Skills API Endpoints

**Get Agent Skills**:
```
GET /api/projects/{project_id}/subagents/{agent_id}/skills
```

**Assign Skill**:
```
POST /api/projects/{project_id}/subagents/{agent_id}/skills/assign?skill_id={id}&skill_type=default
```

**Set All Skills**:
```
PUT /api/projects/{project_id}/subagents/{agent_id}/skills
```

**Unassign Skill**:
```
POST /api/projects/{project_id}/subagents/{agent_id}/skills/unassign?skill_id={id}
```

See [Subagents API Documentation](../api/endpoints/subagents.md) for complete API reference.

## Best Practices

### For Agent Creators

1. **Assign Relevant Skills**: Only assign skills directly relevant to agent's domain
2. **Limit Skill Count**: 2-5 skills per agent (avoid overloading)
3. **Core Skills First**: Prioritize fundamental skills (e.g., documentation-writer for docs agents)
4. **Domain-Specific**: Include specialized skills for agent's expertise area

### For Orchestrators

1. **Verify Skill Invocation**: Check that delegated agents invoke assigned skills
2. **Skill Context**: Provide context that aligns with agent's skills
3. **Quality Checks**: Validate outputs match skill-guided standards
4. **Feedback Loop**: Report skill usage effectiveness

### For Skill Creators

1. **Comprehensive Coverage**: Skills should be complete reference guides
2. **Practical Examples**: Include copy-pasteable code examples
3. **Clear Structure**: Follow skill template structure
4. **Regular Updates**: Keep skills current with best practices

## Future Enhancements

### Planned Features

1. **Dynamic Skill Loading**: Load skills on-demand based on task context
2. **Skill Dependencies**: Skills can reference other skills
3. **Skill Versioning**: Track skill versions and updates
4. **Skill Analytics**: Track skill usage and effectiveness
5. **Skill Recommendations**: AI-suggested skills for agents
6. **Skill Composition**: Combine multiple skills into composite skills

### Potential Skills

1. **CI/CD Patterns** - Pipeline design and automation
2. **Database Patterns** - Database design and optimization
3. **API Design** - RESTful API best practices
4. **Security Patterns** - Application security guidance
5. **Performance Optimization** - Performance tuning strategies
6. **Monitoring Patterns** - Observability and logging

## Related Documentation

- [Skills System](../skills/skills-system.md) - Complete skills documentation
- [Subagents API](../api/endpoints/subagents.md) - Subagent and skill management API
- [Skills API](../api/endpoints/skills.md) - Skills management endpoints
- [Agent Selection Guide](../../.claudetask/instructions/agent-selection-guide.md) - Choosing the right agent

---

**Last Updated**: 2025-11-26
**Version**: 1.0.0

**Version History**:
- **v1.0.0** (2025-11-26): Initial documentation of agent skills system
  - All 34 framework agents updated with skills field
  - Mandatory skills section added to all agents
  - Comprehensive skill assignment strategy documented
  - API integration and synchronization explained
