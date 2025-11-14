---
allowed-tools: [Task]
argument-hint: [optional: scope - all|api|components|architecture]
description: Update project documentation automatically using documentation-updater-agent
---

# Update Project Documentation

I'll update the project documentation by delegating to the documentation-updater-agent specialist.

## Workflow

### Step 1: Determine Update Scope

**If arguments provided:**
- Argument 1: Scope (optional) - `all`, `api`, `components`, `architecture`, `deployment`
  - `all` - Update all documentation (default)
  - `api` - Update only API documentation
  - `components` - Update only component documentation
  - `architecture` - Update only architecture documentation
  - `deployment` - Update only deployment documentation

**If no arguments provided:**
- Default to `all` - comprehensive documentation update

### Step 2: Delegate to Documentation Updater Agent

I'll immediately delegate to the `documentation-updater-agent` with the update scope:

```
Task tool with subagent_type=documentation-updater-agent:
"Update project documentation following post-merge workflow.

🎯 **UPDATE SCOPE**: [SCOPE - all/api/components/architecture/deployment]

🔴 **YOUR TASK**:
Follow your autonomous documentation update workflow:
1. Analyze ONLY recent changes pushed to main branch (git log origin/main..HEAD, git diff origin/main..HEAD)
2. Identify what documentation needs updating based ONLY on these changes
3. Update existing documentation files (overwrite if needed) ONLY for changed code
4. Create new documentation ONLY for new features/components in the recent commits
5. Delete documentation ONLY for features/components removed in recent commits
6. Ensure consistency across updated documentation
7. Validate all links and references in updated files

⚠️ **CRITICAL**: Only update documentation for code changes in the most recent commits since last sync with origin/main. Do NOT update documentation for unchanged code!

📁 **DOCUMENTATION STRUCTURE**:
All documentation is stored in `docs/` directory with the following structure:
- `docs/api/` - API documentation (OpenAPI specs, endpoint docs)
- `docs/components/` - React component documentation
- `docs/architecture/` - System architecture and design decisions
- `docs/deployment/` - Setup and deployment guides
- `docs/claudetask/` - ClaudeTask workflow documentation
- `docs/examples/` - Usage examples and tutorials

⚠️ **IMPORTANT RULES**:
- **NO VERSIONING**: Do not create versioned copies of documentation
- **NO DUPLICATION**: Do not duplicate content across files
- **OVERWRITE**: Update existing files by overwriting them completely
- **CREATE NEW**: Create new documentation files for new features
- **DELETE OLD**: Remove documentation files for deleted features
- **SINGLE SOURCE**: Each piece of information should exist in ONE place only

🔍 **DOCUMENTATION STANDARDS**:
- Use Markdown format for all documentation
- Follow OpenAPI 3.0 for API specifications
- Include practical, copy-pasteable code examples
- Focus on mobile-first web application patterns
- Keep documentation concise but comprehensive
- Include troubleshooting sections where relevant

🚀 **OPERATION MODE**:
- Run autonomously without user interaction
- Update documentation incrementally (only changed parts)
- Maintain consistency across all documentation
- Generate working examples from actual application code
- Prioritize core MVP features

Provide a completion report with:
- List of updated files
- List of created files
- List of deleted files
- Summary of changes made
- Any warnings or issues encountered"
```

### Step 3: Monitor and Report

The documentation-updater-agent will:
1. Analyze recent code changes
2. Determine what documentation needs updating
3. Update/create/delete documentation files as needed
4. Validate documentation consistency
5. Generate practical examples
6. Provide completion report

I'll relay the completion report to you when the agent finishes.

## What to Expect

The documentation-updater-agent will:
- **Analyze Changes**: Review git history to find what changed
- **Update Docs**: Overwrite existing documentation with updated content
- **Create New**: Generate documentation for new features/components
- **Remove Old**: Delete documentation for removed features
- **Maintain Quality**: Ensure consistency and accuracy across all docs
- **No Duplicates**: Keep single source of truth for each topic
- **No Versions**: Maintain only current documentation state

## Output Location

All documentation will be in:
```
docs/
├── api/                    # API endpoint documentation
├── components/             # React component docs
├── architecture/           # System design and ADRs
├── deployment/             # Setup and deployment guides
├── claudetask/             # ClaudeTask workflow docs
└── examples/               # Usage examples
```

## Example Usage

**Update all documentation (default):**
```
/update-documentation
```

**Update only API documentation:**
```
/update-documentation api
```

**Update only component documentation:**
```
/update-documentation components
```

## Automatic Trigger

This command is automatically triggered by the `post-merge-documentation` hook after:
- Merging a PR to main branch
- Running `git merge` on main branch
- Pulling changes into main branch

## Important Notes

1. **No User Interaction**: Runs completely autonomously in background
2. **Incremental Updates**: Only updates changed documentation
3. **Single Source**: No versioning or duplication of content
4. **Overwrite Strategy**: Existing files are completely rewritten
5. **Clean Management**: Removes outdated documentation automatically

## Timeline

Documentation update typically takes 3-7 minutes depending on scope of changes. You'll receive a completion report with all changes made.

---

Let me delegate to the documentation-updater-agent to update the project documentation...
