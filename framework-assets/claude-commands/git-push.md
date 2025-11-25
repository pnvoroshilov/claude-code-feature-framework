---
allowed-tools: [Bash, Read, Glob, Grep]
description: Commit all changes and push to origin remote
---

# /git-push Command - Commit and Push Changes

You've been asked to commit all staged and unstaged changes and push them to the origin remote.

## EXECUTE THESE STEPS IN ORDER:

### 1. Check Current Git Status

First, understand the current state:

```bash
git status
git diff --stat
git log --oneline -3
```

Review:
- Which files are modified
- Which files are untracked
- Current branch name
- Recent commit style

### 2. Stage All Changes

Add all modified and untracked files:

```bash
git add -A
```

### 3. Generate Commit Message

Analyze the changes and create an appropriate commit message:

1. **Determine commit type** based on changes:
   - `feat:` - New feature or functionality
   - `fix:` - Bug fix
   - `docs:` - Documentation only
   - `style:` - Formatting, no code change
   - `refactor:` - Code change that neither fixes bug nor adds feature
   - `test:` - Adding tests
   - `chore:` - Maintenance, dependencies, config

2. **Write concise summary** (50 chars max for first line)

3. **Add details** if needed (wrap at 72 chars)

### 4. Create Commit

Create the commit with generated message:

```bash
git commit -m "$(cat <<'EOF'
<type>: <concise summary>

<optional body with more details>

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>
EOF
)"
```

### 5. Push to Origin

Push changes to the remote:

```bash
git push
```

If the branch doesn't have an upstream, use:

```bash
git push -u origin <current-branch>
```

### 6. Verify Success

Confirm the push was successful:

```bash
git status
git log --oneline -1
```

## Completion Message

After successful push, report:

```
✅ Changes committed and pushed!

📝 Commit: <commit-hash>
📌 Message: <commit-message-summary>
🌿 Branch: <branch-name>
📁 Files changed: <count>
🚀 Pushed to: origin/<branch>
```

## Error Handling

### If there are no changes:
```
ℹ️ No changes to commit. Working tree is clean.
```

### If push is rejected (remote has new commits):
```bash
git pull --rebase origin <branch>
git push
```

### If push fails due to permissions:
Report the error to the user and suggest checking repository access.

## Security Notes

⚠️ **Before committing, verify:**
- No secrets or credentials in changes (.env, API keys, passwords)
- No sensitive files being committed
- .gitignore is properly configured

If sensitive files are detected, **DO NOT COMMIT**. Alert the user instead.
