---
allowed-tools: [Task, AskUserQuestion, Read, Edit]
argument-hint: [hook-name] [edit-instructions]
description: Edit and improve existing Claude Code hook based on instructions
---

# Edit Claude Code Hook

I'll edit an existing Claude Code hook by reading the current configuration and applying your requested changes.

## Workflow

### Step 1: Identify Hook to Edit

**If arguments provided:**
- Argument 1: Hook name (e.g., "bash-command-logger")
- Argument 2: Edit instructions (e.g., "add filtering for error commands only")

**If no arguments provided:**
Ask user for:
1. Which hook to edit (name or file path)
2. What changes to make

### Step 2: Read Current Hook

I'll read the hook file from `framework-assets/claude-hooks/[name].json` to understand current configuration.

### Step 3: Apply Changes

Based on your instructions, I'll modify:
- Hook configuration (events, matchers, commands)
- Shell commands
- Setup instructions
- Dependencies list
- Category or description

### Step 4: Validate & Save

I'll ensure:
- JSON is valid
- Hook structure follows Claude Code spec
- Commands are secure
- Dependencies are updated

## Common Edit Operations

### 1. Change Hook Event
```
/edit-hook "my-hook" "change from PostToolUse to PreToolUse"
```

### 2. Add New Tool Matcher
```
/edit-hook "code-formatter" "also format Write operations, not just Edit"
```

### 3. Modify Shell Command
```
/edit-hook "logger" "log to different file path"
```

### 4. Update Dependencies
```
/edit-hook "formatter" "add support for Go formatting with gofmt"
```

### 5. Add Error Handling
```
/edit-hook "auto-commit" "add check to only commit if in git repo"
```

### 6. Change Category
```
/edit-hook "notifier" "change category from notifications to logging"
```

## Example Usage

**With arguments:**
```
/edit-hook "bash-command-logger" "Filter to only log commands that contain 'docker' keyword"
```

**Without arguments (interactive):**
```
/edit-hook
```
I'll ask you which hook to edit and what changes to make.

## Safety Notes

1. **Backup**: Original hook is preserved until you confirm changes
2. **Validation**: JSON and command syntax validated before saving
3. **Testing**: You should test edited hooks before enabling in production

---

Let me help you edit the hook...
