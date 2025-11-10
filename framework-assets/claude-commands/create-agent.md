---
allowed-tools: [Task, AskUserQuestion]
argument-hint: [agent-name] [agent-description]
description: Create production-ready Claude Code agent with proper YAML frontmatter and configuration
---

# Create Claude Code Agent

I'll create a production-ready agent for Claude Code's Task tool by delegating to the agent-creator specialist.

## Workflow

### Step 1: Gather Agent Requirements

**If arguments provided:**
- Argument 1: Agent name (e.g., "FastAPI Expert")
- Argument 2: Agent description (e.g., "Specialized in building production-ready FastAPI applications")

**If no arguments provided:**
Ask user for:
1. Agent name (will be converted to kebab-case)
2. Brief description of what the agent should specialize in

### Step 2: Delegate to Agent Creator

Once I have the agent information, I'll immediately delegate to the `agent-creator` agent:

```
Task tool with subagent_type=agent-creator:
"Create a production-ready Claude Code agent.

🎯 **AGENT DETAILS**:
- **Name**: [AGENT NAME]
- **Description**: [AGENT DESCRIPTION]

🔴 **YOUR TASK**:
Create a complete agent file in .claude/agents/ with:

1. **Proper YAML frontmatter**:
   ```yaml
   ---
   name: agent-name-kebab-case
   description: One-line agent description
   tools: Tool1, Tool2, Tool3
   ---
   ```

2. **Complete agent content**:
   - Role and expertise section
   - Core capabilities (5-10 specific capabilities)
   - Responsibilities with clear boundaries
   - Step-by-step workflow approach
   - Best practices for the domain
   - Tool usage guidelines
   - Example invocations
   - Quality standards
   - Common pitfalls to avoid

3. **File location**: .claude/agents/[agent-name-kebab-case].md

4. **Tool selection**: Choose appropriate tools based on:
   - Development agents: Read, Write, Edit, MultiEdit, Bash, Grep
   - Analysis agents: Read, Grep, Glob, Bash
   - Testing agents: Bash, Read, Write, Grep
   - Documentation agents: Read, Write, Edit, Bash

Provide a completion report with agent name, file path, tools, and example usage."
```

### Step 3: Report Completion

The agent-creator will:
1. Generate proper YAML frontmatter
2. Create comprehensive agent content
3. Save file in `.claude/agents/`
4. Validate configuration
5. Report completion with usage example

I'll relay the completion report when the agent finishes.

## What to Expect

The agent-creator will create an agent file with:
- **YAML frontmatter** with name, description, and tools
- **Role section** explaining expertise (50-100 lines)
- **Core capabilities** listing (5-10 capabilities)
- **Workflow steps** with actionable guidance
- **Best practices** relevant to the domain
- **Example invocations** showing typical usage
- **Quality standards** for deliverables
- **Total size**: 150-300 lines of production-ready content

## Example Usage

**With arguments:**
```
/create-agent "Database Migration Expert" "Specialized in database schema design and migration management with Alembic"
```

**Without arguments (interactive):**
```
/create-agent
```
I'll ask you for the agent name and description, then delegate to the agent-creator.

## After Creation

Once created, your agent will be immediately available for use:

```
Task tool with subagent_type="your-agent-name":
"Your task description here"
```

## Timeline

Agent creation typically takes 2-5 minutes. You'll receive a completion report with the agent name, file path, configured tools, and example usage.

---

Let me gather the agent requirements and delegate to the agent-creator...
