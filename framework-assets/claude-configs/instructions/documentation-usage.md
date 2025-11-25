# Documentation Usage Guide

## Overview

Every project using this framework should maintain up-to-date documentation in the `docs/` directory at the project root. This documentation is the **primary source of truth** for understanding the project.

## When to Use Documentation

**Always consult `docs/` when:**
- Starting work on a new task
- Understanding project architecture
- Learning about existing features
- Looking for API specifications
- Checking coding conventions
- Understanding business logic

## How to Access Documentation

### Option 1: Direct Reading (Recommended for Specific Topics)

When you know what you're looking for:

```bash
# List available documentation
ls docs/

# Read specific documentation file
Read docs/architecture.md
Read docs/api.md
Read docs/features/authentication.md
```

### Option 2: RAG Search (Recommended for Exploration)

When searching for information across documentation:

```bash
mcp__claudetask__search_codebase \
  --query="authentication flow" \
  --top_k=10
```

RAG will search across all indexed files including documentation.

## Documentation Priority

When gathering context for a task:

1. **First**: Check `docs/` for relevant documentation
2. **Second**: Use RAG to search codebase and docs
3. **Third**: Explore code directly if docs are insufficient

## For Agents

When delegating to specialized agents, **always mention** that they should:
- Check `docs/` directory for project documentation
- Use RAG search for relevant context
- Reference documentation in their analysis

**Example delegation prompt:**
```
Analyze the authentication feature for task #123.

IMPORTANT: Check docs/ directory for existing documentation.
Use RAG search: mcp__claudetask__search_codebase --query="authentication"

Provide analysis with references to documentation where applicable.
```

## Documentation Structure (Recommended)

Projects should organize `docs/` as follows:

```
docs/
├── README.md           # Documentation index
├── architecture.md     # System architecture
├── api.md             # API documentation
├── database.md        # Database schema
├── features/          # Feature-specific docs
│   ├── auth.md
│   └── ...
├── guides/            # How-to guides
│   ├── setup.md
│   └── deployment.md
└── decisions/         # Architecture Decision Records
    └── ADR-001-*.md
```

## Key Principle

**Documentation is not optional.** Before making architectural decisions or implementing features, verify your understanding against existing documentation. This prevents:
- Duplicate implementations
- Conflicting approaches
- Breaking existing contracts
- Wasted effort

## Integration with Analysis Phase

During the Analysis phase, analysts should:
1. **Read** all relevant docs in `docs/`
2. **Reference** existing documentation in requirements.md
3. **Update** documentation if gaps are found
4. **Create** new docs for new features

See [analysis-phase.md](./analysis-phase.md) for full analysis workflow.
