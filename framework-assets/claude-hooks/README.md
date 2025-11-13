# Claude Code Hooks Library

This directory contains pre-configured hooks for Claude Code that can be installed into your projects.

## What are Hooks?

Hooks are shell commands that execute at specific points in Claude Code's workflow. They provide deterministic control over Claude's behavior, ensuring certain actions always happen rather than relying on the AI to choose to run them.

## Available Hooks

### 1. Bash Command Logger
**Category:** Logging
**Description:** Logs all bash commands executed by Claude to `~/.claude/bash_commands.log`
**Use Case:** Audit trail, compliance, debugging
**Dependencies:** jq

### 2. Auto Code Formatter
**Category:** Formatting
**Description:** Automatically formats code after edits using appropriate formatters (Prettier, Black, gofmt)
**Use Case:** Code consistency, automatic formatting
**Dependencies:** jq, prettier (optional), black (optional), gofmt (optional)

### 3. Desktop Notifications
**Category:** Notifications
**Description:** Shows desktop notifications when Claude needs input or completes tasks
**Use Case:** Stay informed without watching terminal
**Dependencies:** osascript (macOS) or notify-send (Linux)

### 4. File Protection
**Category:** Security
**Description:** Prevents editing sensitive files (.env, credentials, SSH keys)
**Use Case:** Security, prevent accidental secret exposure
**Dependencies:** jq

### 5. Git Auto Commit
**Category:** Version Control
**Description:** Automatically commits file changes with descriptive messages
**Use Case:** Automatic version control, change tracking
**Dependencies:** git, jq

## Hook Configuration Format

Each hook is stored as a JSON file with the following structure:

```json
{
  "name": "Hook Name",
  "description": "What the hook does",
  "category": "category-name",
  "hook_config": {
    "EventName": [
      {
        "matcher": "ToolName",
        "hooks": [
          {
            "type": "command",
            "command": "shell command here"
          }
        ]
      }
    ]
  },
  "setup_instructions": "How to setup/configure",
  "dependencies": ["dep1", "dep2"]
}
```

## Available Hook Events

- **PreToolUse** - Before tool execution (can block actions)
- **PostToolUse** - After tool completion
- **UserPromptSubmit** - When users submit prompts
- **Notification** - When Claude sends notifications
- **Stop** - When Claude finishes responding
- **SubagentStop** - When subagent tasks complete
- **PreCompact** - Before compaction operations
- **SessionStart** - At session initialization
- **SessionEnd** - At session termination

## Installing Hooks

Hooks from this directory can be installed into your projects through the ClaudeTask Framework UI:

1. Go to the **Hooks** tab in the UI
2. Browse available default hooks
3. Click **Enable** on the hook you want to use
4. The hook will be copied to your project's `.claude/settings.json`

## Creating Custom Hooks

Use the `/create-hook` command to create custom hooks with AI assistance:

```bash
/create-hook "My Custom Hook" "Description of what it should do"
```

The `hook-creator` agent will help you build a custom hook configuration.

## Security Considerations

**IMPORTANT:** Hooks run automatically with your environment's credentials. Always:
- Review hook commands before enabling
- Understand what each command does
- Be cautious with hooks from untrusted sources
- Test hooks in safe environments first

## Common Dependencies

Many hooks require these tools:
- **jq** - JSON parsing in bash (install: `brew install jq` or `apt-get install jq`)
- **git** - Version control (usually pre-installed)
- **prettier** - JavaScript/TypeScript formatter (install: `npm install -g prettier`)
- **black** - Python formatter (install: `pip install black`)

## More Information

- [Claude Code Hooks Documentation](https://code.claude.com/docs/en/hooks-guide)
- [Hook Examples and Use Cases](https://code.claude.com/docs/en/hooks-guide#examples)
