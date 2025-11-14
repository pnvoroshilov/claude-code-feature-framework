# 📚 Automated Documentation System

This document describes the automated documentation update system for the Claude Code Feature Framework.

## 🎯 Overview

The project uses an **automated documentation system** that keeps documentation synchronized with code changes. After every merge to the main branch, documentation is automatically updated, created, or deleted to reflect the current state of the codebase.

## 🔧 System Components

### 1. Hook: `post-merge-documentation.json`
**Location**: `framework-assets/claude-hooks/post-merge-documentation.json`

**Trigger**: Automatically runs after any of these git commands on the main branch:
- `git merge <branch>`
- `gh pr merge <pr-number>`
- `git pull origin main`
- `git push origin main`

**Action**: Invokes the `/update-documentation` slash command

**Configuration**:
```json
{
  "name": "Post-Merge Documentation Update",
  "category": "version-control",
  "hook_config": {
    "PostToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "Detects merge to main and triggers /update-documentation"
          }
        ]
      }
    ]
  }
}
```

### 2. Slash Command: `/update-documentation`
**Location**: `framework-assets/claude-commands/update-documentation.md`

**Usage**:
```bash
/update-documentation              # Update all documentation
/update-documentation api          # Update only API docs
/update-documentation components   # Update only component docs
/update-documentation architecture # Update only architecture docs
/update-documentation deployment   # Update only deployment docs
```

**Function**: Delegates to the `documentation-updater-agent` with specified scope

**Arguments**:
- `scope` (optional): `all` (default), `api`, `components`, `architecture`, `deployment`

### 3. Agent: `documentation-updater-agent`
**Location**: `framework-assets/claude-agents/documentation-updater-agent.md`

**Capabilities**:
- Analyzes recent code changes via git history
- Updates existing documentation (overwrites completely)
- Creates documentation for new features/components
- Deletes documentation for removed features
- Maintains single source of truth (no duplication)
- No versioning (only current state)

**Tools Available**: Read, Write, Edit, Glob, Grep, Bash

## 📁 Documentation Structure

All documentation is stored in the `docs/` directory:

```
docs/
├── README.md                        # Documentation index
├── api/
│   ├── api-specification.yaml       # OpenAPI 3.0 specification
│   └── endpoints/
│       └── *.md                     # Individual endpoint docs
├── components/
│   ├── README.md                    # Component index
│   └── *.md                         # Individual component docs
├── architecture/
│   ├── overview.md                  # System architecture
│   ├── database-design.md           # Database schema
│   └── adr/
│       └── *.md                     # Architecture Decision Records
├── deployment/
│   ├── setup.md                     # Development setup
│   └── production.md                # Production deployment
├── claudetask/
│   ├── workflow.md                  # Task management workflow
│   ├── mcp-integration.md           # MCP tools usage
│   └── worktree-guide.md            # Worktree management
└── examples/
    ├── api-usage.md                 # API examples
    └── component-usage.md           # Component examples
```

## 🔄 Documentation Workflow

### Automatic Trigger (After Merge/Push/Pull to Main)

```
1. Developer merges/pushes/pulls to main
   ↓
2. Hook detects git command (merge/push/pull)
   ↓
3. Hook checks if on main branch
   ↓
4. Hook invokes /update-documentation
   ↓
5. Command delegates to documentation-updater-agent
   ↓
6. Agent analyzes code changes
   ↓
7. Agent updates/creates/deletes documentation
   ↓
8. Agent provides completion report
```

### Manual Trigger (On Demand)

```bash
# Developer runs command
/update-documentation

# System follows same workflow as automatic trigger
```

## 📋 Documentation Principles

### ✅ DO

1. **Single Source of Truth**
   - Each piece of information exists in EXACTLY ONE place
   - No duplicate content across files

2. **Current State Only**
   - Document only the current codebase state
   - No historical versions maintained

3. **Overwrite Strategy**
   - Existing files are completely rewritten with updated content
   - No append-only or patch-based updates

4. **Clean Management**
   - Create docs for new features
   - Delete docs for removed features
   - Reorganize when structure improves

### ❌ DON'T

1. **No Versioning**
   - Don't create `v1/`, `v2/`, `old/`, `archive/` directories
   - Don't suffix files with versions (`api-v1.md`, `api-v2.md`)

2. **No Duplication**
   - Don't copy content to multiple files
   - Don't maintain redundant documentation

3. **No Manual Versioning**
   - Don't keep old documentation "just in case"
   - Trust git history for past states

## 🧪 Testing the System

### Test 1: Hook Detection
```bash
# Simulate merge command
echo 'git merge feature-branch' | grep -qE '(git merge|gh pr merge|git pull.*origin.*main)'
# Should detect merge command
```

### Test 2: Manual Documentation Update
```bash
# Run documentation update manually
/update-documentation api
# Should update only API documentation
```

### Test 3: Full Workflow
```bash
# 1. Create a feature branch
git checkout -b test-doc-system

# 2. Make code changes (e.g., add a new component)
# ... make changes ...

# 3. Commit and push
git add .
git commit -m "test: Add new component for documentation system test"
git push origin test-doc-system

# 4. Merge to main
git checkout main
git merge test-doc-system

# 5. Hook should automatically trigger /update-documentation
# 6. Check docs/ directory for updates
```

## 🎨 Documentation Standards

### Markdown Files
- Use proper heading hierarchy (h1 → h2 → h3)
- Include code blocks with syntax highlighting
- Use tables for structured data
- Add links to related documentation

### OpenAPI Specification
- Follow OpenAPI 3.0 standard
- Include all endpoints, parameters, and schemas
- Document error responses
- Provide realistic examples

### Code Examples
- Must be copy-pasteable and functional
- Include necessary imports
- Show realistic usage patterns
- Comment complex sections

## 🔍 Agent Operation Details

### Phase 1: Change Analysis
```bash
git log --oneline --since="1 day ago" -n 20
git diff HEAD~5..HEAD --stat
git diff HEAD~5..HEAD --name-only
```

### Phase 2: Documentation Inventory
```bash
find docs/ -type f -name "*.md" -o -name "*.yaml"
```

### Phase 3: Smart Updates
- **API docs**: Extract from FastAPI routers and Pydantic models
- **Component docs**: Parse React components for props and state
- **Architecture docs**: Analyze system structure and database models
- **Deployment docs**: Extract from package.json and requirements.txt

### Phase 4: Quality Checks
- Validate internal links
- Ensure consistent formatting
- Remove orphaned files
- Verify code examples

### Phase 5: Completion Report
```
📝 Documentation Update Complete

✅ UPDATED: 3 files
✨ CREATED: 2 files
🗑️ DELETED: 1 file

Details of changes...
```

## 🚀 Benefits

1. **Always Current**: Documentation never gets outdated
2. **Zero Maintenance**: No manual documentation updates needed
3. **Consistent Quality**: Automated formatting and structure
4. **Single Source**: No duplicate or conflicting information
5. **Clean Repository**: No versioned or archived docs cluttering the repo
6. **Developer Focused**: Developers focus on code, not documentation

## 📝 Maintenance

The documentation system itself requires minimal maintenance:

1. **Hook**: Update trigger conditions if workflow changes
2. **Command**: Modify scope options if new documentation areas added
3. **Agent**: Enhance parsing logic for new patterns or frameworks

## 🔗 Related Files

- Hook configuration: `framework-assets/claude-hooks/post-merge-documentation.json`
- Slash command: `framework-assets/claude-commands/update-documentation.md`
- Agent definition: `framework-assets/claude-agents/documentation-updater-agent.md`
- Documentation root: `docs/README.md`

---

**System Status**: ✅ Active and Operational
**Last Updated**: 2025-11-13
**Maintained By**: Claude Code Feature Framework
