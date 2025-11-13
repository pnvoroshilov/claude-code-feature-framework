---
allowed-tools: [Task, AskUserQuestion]
argument-hint: [hook-name] [hook-description]
description: Create Claude Code hook with proper JSON configuration and setup instructions
---

# Create Claude Code Hook

I'll create a Claude Code hook by delegating to the hook-creator specialist agent.

## Workflow

### Step 1: Gather Hook Requirements

**If arguments provided:**
- Argument 1: Hook name (e.g., "Bash Command Logger")
- Argument 2: Hook description (e.g., "Logs all bash commands to a file for audit")

**If no arguments provided:**
Ask user for:
1. Hook name
2. Brief description of what the hook should do
3. When should it trigger (which events: PreToolUse, PostToolUse, etc.)
4. What actions should it perform

### Step 2: Delegate to Hook Creator Agent

Once I have the hook information, I'll immediately delegate to the `hook-creator` agent with complete requirements:

```
Task tool with subagent_type=hook-creator:
"Create a Claude Code hook with proper JSON configuration.

🎯 **HOOK DETAILS**:
- **Name**: [HOOK NAME]
- **Description**: [HOOK DESCRIPTION]
- **Events**: [HOOK EVENTS - e.g., PostToolUse, PreToolUse, etc.]
- **Target Tools**: [TOOLS TO HOOK - e.g., Bash, Edit, Write, etc.]

🔴 **YOUR TASK**:
Follow your complete autonomous creation workflow to build a production-ready hook:
- Proper JSON hook configuration with events, matchers, and commands
- Shell command that performs the desired action
- Setup instructions for dependencies and installation
- Security considerations and best practices
- Testing recommendations

📚 **REFERENCE DOCUMENTATION**:
Use official Claude Code hooks guide: https://code.claude.com/docs/en/hooks

**Hook Structure:**
```json
{
  "name": "Hook Name",
  "description": "What it does",
  "category": "logging|formatting|notifications|security|version-control",
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
  "setup_instructions": "How to setup",
  "dependencies": ["dep1", "dep2"]
}
```

**Available Events:**
- PreToolUse - Before tool execution (can block actions)
- PostToolUse - After tool completion
- UserPromptSubmit - When users submit prompts
- Notification - When Claude sends notifications
- Stop - When Claude finishes responding
- SubagentStop - When subagent tasks complete
- PreCompact - Before compaction operations
- SessionStart - At session initialization
- SessionEnd - At session termination

Target location: framework-assets/claude-hooks/[hook-name-kebab-case].json

⚠️ **IMPORTANT**: After creating the hook JSON file, the system will automatically:
1. Apply the hook configuration to `.claude/settings.json` in the hooks section
2. Enable the hook for the current project
3. Make the hook active immediately

Follow ALL phases of your creation workflow and provide a completion report when done."
```

### Step 3: Monitor and Report

The hook-creator agent will:
1. Analyze the hook requirements
2. Design the hook configuration
3. Create the JSON file with proper structure
4. Validate the hook configuration
5. Provide setup instructions and testing recommendations
6. Report completion with the hook file path

I'll relay the completion report to you when the agent finishes.

## What to Expect

The hook-creator agent will create:
- **Complete JSON hook file** with proper structure
- **Hook configuration** with events, matchers, and commands
- **Shell commands** that perform the desired actions
- **Setup instructions** for dependencies and installation
- **Security notes** and best practices
- **Testing recommendations** to verify the hook works

## Example Usage

**With arguments:**
```
/create-hook "Git Auto Commit" "Automatically commits changes after file edits"
```

**Without arguments (interactive):**
```
/create-hook
```
I'll ask you for the hook name, description, and behavior, then delegate to the agent.

## Important Notes

1. **Security First**: Hooks run automatically with your credentials. The agent will ensure proper input validation and security measures.

2. **Dependencies**: The agent will list any required dependencies (jq, git, formatters, etc.)

3. **Testing**: Always test hooks in a safe environment before enabling in production projects.

4. **Documentation**: Review the official Claude Code hooks guide at https://code.claude.com/docs/en/hooks

## Timeline

Hook creation typically takes 5-10 minutes for the agent to complete. You'll receive a detailed completion report with the hook file path and setup instructions.

---

Let me gather the hook requirements and delegate to the hook-creator agent...
