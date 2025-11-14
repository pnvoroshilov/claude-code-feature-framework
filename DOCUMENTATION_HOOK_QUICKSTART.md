# 🚀 Documentation Hook - Quick Start Guide

## What Was Created

A complete automated documentation system that updates docs after every merge to main.

### Files Created:

1. **Hook**: `framework-assets/claude-hooks/post-merge-documentation.json`
   - Automatically triggers after git merge to main

2. **Slash Command**: `framework-assets/claude-commands/update-documentation.md`
   - Manual trigger: `/update-documentation [scope]`

3. **Agent**: `framework-assets/claude-agents/documentation-updater-agent.md`
   - Performs the actual documentation updates

4. **Documentation Directory**: `docs/`
   - Structured storage for all project documentation

## How It Works

```
Developer merges to main
         ↓
Hook detects merge
         ↓
Triggers /update-documentation
         ↓
Agent analyzes code changes
         ↓
Updates/Creates/Deletes docs
         ↓
Documentation is current!
```

## Usage

### Automatic (After Merge or Push)
```bash
# Option 1: Merge your feature branch to main
git checkout main
git merge feature-branch

# Option 2: Push to main
git push origin main

# Option 3: Pull from main
git pull origin main

# Hook automatically runs and updates docs
# No action needed!
```

### Manual (On Demand)
```bash
# Update all documentation
/update-documentation

# Update specific area only
/update-documentation api
/update-documentation components
/update-documentation architecture
```

## Key Features

✅ **No Duplication** - Each topic documented once
✅ **No Versioning** - Only current state maintained
✅ **Auto-Update** - Existing files overwritten
✅ **Auto-Create** - New features get new docs
✅ **Auto-Delete** - Removed features = removed docs

## Documentation Location

All documentation is in `docs/`:

```
docs/
├── api/              # API documentation
├── components/       # React components
├── architecture/     # System design
├── deployment/       # Setup guides
├── claudetask/       # Task workflow
└── examples/         # Code examples
```

## Principles

### ✅ DO:
- Rely on automatic updates after merges
- Use `/update-documentation` for manual updates
- Keep docs in `docs/` directory structure

### ❌ DON'T:
- Don't create versioned docs (v1/, v2/, old/)
- Don't duplicate content across files
- Don't manually maintain documentation

## Testing the Hook

### Test 1: Verify Hook Exists
```bash
cat framework-assets/claude-hooks/post-merge-documentation.json
```

### Test 2: Manual Update
```bash
/update-documentation api
```

### Test 3: Full Workflow
```bash
# Create test branch
git checkout -b test-docs

# Make a small change
echo "# Test" > test.md
git add test.md
git commit -m "test: Documentation system"

# Merge to main
git checkout main
git merge test-docs

# Hook should auto-trigger!
# Check docs/ for any updates
```

## Configuration

The hook is configured in:
`framework-assets/claude-hooks/post-merge-documentation.json`

To modify trigger conditions, edit the `hook_config.PostToolUse` section.

## Troubleshooting

### Hook Not Triggering?

Check:
1. Are you on `main` or `master` branch?
2. Did you actually run a merge command?
3. Is the hook file in `framework-assets/claude-hooks/`?

### Command Not Found?

Check:
1. Is `/update-documentation` in `framework-assets/claude-commands/`?
2. Is the command properly formatted in Markdown with YAML frontmatter?

### Agent Not Working?

Check:
1. Is `documentation-updater-agent.md` in `framework-assets/claude-agents/`?
2. Does it have proper YAML frontmatter with tools listed?

## More Information

- Full system documentation: `DOCUMENTATION_SYSTEM.md`
- Hook file: `framework-assets/claude-hooks/post-merge-documentation.json`
- Command file: `framework-assets/claude-commands/update-documentation.md`
- Agent file: `framework-assets/claude-agents/documentation-updater-agent.md`
- Docs README: `docs/README.md`

## Benefits

🎯 **Always Current** - Docs never outdated
⚡ **Zero Effort** - Automatic after merge
🧹 **Clean Repo** - No version clutter
📚 **Consistent** - Same format everywhere
🚀 **Developer Focused** - Code first, docs follow

---

**Status**: ✅ Ready to Use
**Created**: 2025-11-13
**Last Updated**: 2025-11-13
