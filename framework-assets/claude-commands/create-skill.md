---
allowed-tools: [Task, AskUserQuestion]
argument-hint: [skill-name] [skill-description]
description: Create Claude Code skill with proper JSON configuration and setup instructions
---

# Create Skill Command

Create a new Claude Code skill package using the skills-creator agent.

## What You should DO

1. Launches the skills-creator agent
2. Bypass parameters skill-name and skill-description
3. Agent creates all skill files using Write tool
4. After work is done you MUST call MCP ClaudeTask to change status of the skill