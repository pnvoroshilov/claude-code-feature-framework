# Automatic Documentation Update System

## Overview

This system automatically triggers documentation updates whenever code is pushed to the main branch using a two-phase hook mechanism.

## Architecture

### Phase 1: PostToolUse Hook (Detection)
**File**: `.claude/hooks/post-push-docs.sh`

**Triggers**: After any Bash tool execution

**Function**:
1. Monitors all bash commands executed by Claude
2. Detects `git push origin main/master` commands
3. Verifies the current branch is main/master
4. Checks for `[skip-hook]` tag in commit message
5. Creates marker file at `.claude/logs/hooks/.docs-update-pending`
6. Logs the event

**Why this approach?**
- Hooks cannot directly call Claude slash commands
- We need to signal that an update is pending
- Marker file acts as persistent state between hook phases

### Phase 2: UserPromptSubmit Hook (Injection)
**File**: `.claude/hooks/inject-docs-update.sh`

**Triggers**: Before every user prompt is processed by Claude

**Function**:
1. Checks for existence of marker file
2. If marker exists:
   - Removes marker file (one-time trigger)
   - Outputs JSON with `additionalContext`
   - Context includes CRITICAL instruction to run `/update-documentation`
3. If no marker:
   - Returns empty JSON (normal operation)

**Why UserPromptSubmit?**
- This is the ONLY hook type that can inject context into Claude's conversation
- The `additionalContext` field adds text to Claude's context
- Claude will see the instruction and execute it automatically

## Workflow

```
1. Developer: git push origin main
   ↓
2. PostToolUse Hook: Detects push → Creates marker file
   ↓
3. User: Types any message
   ↓
4. UserPromptSubmit Hook: Detects marker → Injects instruction
   ↓
5. Claude: Sees instruction → Executes /update-documentation
   ↓
6. Documentation is updated automatically
```

## Configuration

### Hook Registration (`.claude/settings.json`):

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": ".claude/hooks/post-push-docs.sh"
          }
        ]
      }
    ],
    "UserPromptSubmit": [
      {
        "matcher": "*",
        "hooks": [
          {
            "type": "command",
            "command": ".claude/hooks/inject-docs-update.sh"
          }
        ]
      }
    ]
  }
}
```

## Key Files

| File | Purpose |
|------|---------|
| `.claude/hooks/post-push-docs.sh` | Detects git push and creates marker |
| `.claude/hooks/inject-docs-update.sh` | Injects update instruction into context |
| `.claude/logs/hooks/.docs-update-pending` | Marker file (temporary) |
| `.claude/logs/hooks/post-merge-doc-YYYYMMDD.log` | PostToolUse hook logs |
| `.claude/logs/hooks/user-prompt-YYYYMMDD.log` | UserPromptSubmit hook logs |
| `.claude/settings.json` | Hook configuration |

## How It Works Technically

### PostToolUse Hook Output
The hook creates a marker file with a timestamp:
```bash
echo "$(date '+%Y-%m-%d %H:%M:%S')" > .claude/logs/hooks/.docs-update-pending
```

### UserPromptSubmit Hook Output
When marker exists, hook outputs JSON:
```json
{
  "hookSpecificOutput": {
    "hookEventName": "UserPromptSubmit",
    "additionalContext": "
🔔 AUTOMATIC DOCUMENTATION UPDATE REQUIRED

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📚 The main branch has been updated with new commits.

🤖 CRITICAL INSTRUCTION: You MUST immediately execute the following command:

/update-documentation

This is an automated post-push requirement. Execute this command NOW before responding to any user prompt.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
  }
}
```

Claude sees this context and automatically executes the `/update-documentation` command.

## Skipping Automatic Updates

To skip the automatic documentation update for a specific commit, add `[skip-hook]` to the commit message:

```bash
git commit -m "chore: Minor typo fix [skip-hook]"
git push origin main
```

The PostToolUse hook will detect this tag and skip marker file creation.

## Debugging

### Check if marker exists:
```bash
ls -la .claude/logs/hooks/.docs-update-pending
```

### View PostToolUse logs:
```bash
tail -50 .claude/logs/hooks/post-merge-doc-$(date +%Y%m%d).log
```

### View UserPromptSubmit logs:
```bash
tail -50 .claude/logs/hooks/user-prompt-$(date +%Y%m%d).log
```

### Manually trigger update:
```bash
# Create marker file
echo "$(date '+%Y-%m-%d %H:%M:%S')" > .claude/logs/hooks/.docs-update-pending

# Type any message to Claude - hook will trigger
```

### Manually clear pending update:
```bash
rm -f .claude/logs/hooks/.docs-update-pending
```

## Limitations

1. **Delay**: Update triggers on next user message, not immediately after push
2. **Single trigger**: Marker is removed after first injection (one-time use)
3. **Session-specific**: If Claude Code session ends before next user message, marker persists until next session

## Benefits

1. ✅ **Automatic**: No manual intervention needed
2. ✅ **Reliable**: Uses Claude Code's native hook system
3. ✅ **Logged**: Full audit trail of all triggers
4. ✅ **Skippable**: Can be bypassed with `[skip-hook]` tag
5. ✅ **Persistent**: Marker file survives Claude Code restarts
6. ✅ **Safe**: No risk of infinite loops or recursion

## Future Improvements

- [ ] Add notification when update is pending
- [ ] Support multiple pending updates (queue system)
- [ ] Add configuration for update scope (all/api/components/etc)
- [ ] Implement automatic commit detection (only update if docs changed)
- [ ] Add metrics tracking (update frequency, success rate)

## References

- [Claude Code Hooks Documentation](https://code.claude.com/docs/en/hooks)
- [UserPromptSubmit Hook Details](https://code.claude.com/docs/en/hooks#userpromptsubmit)
- [PostToolUse Hook Details](https://code.claude.com/docs/en/hooks#posttooluse)

---

**Last Updated**: 2025-11-14
**Version**: 1.0.0
