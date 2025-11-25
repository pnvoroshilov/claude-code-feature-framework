# Modular Instruction System

Complete guide to the modular instruction system in the Claude Code Feature Framework.

## Overview

The framework uses a modular instruction system that breaks down the main CLAUDE.md configuration into focused, reusable instruction files. This approach improves:

- **Clarity**: Each instruction file focuses on a single workflow phase
- **Maintainability**: Update specific workflows without touching unrelated content
- **Reusability**: Share instruction modules across multiple projects
- **Discoverability**: Easy to find relevant guidance when needed

## Architecture

### Directory Structure

```
.claudetask/instructions/
├── critical-restrictions.md       # Rules that must NEVER be violated
├── project-modes.md               # SIMPLE vs DEVELOPMENT mode documentation
├── orchestration-role.md          # Coordinator agent responsibilities
├── status-transitions.md          # Task status workflow and transitions
├── agent-selection-guide.md       # Which agent to use for each task type
├── analysis-phase.md              # Requirements and architecture creation
├── testing-workflow.md            # Test environment setup and management
├── resource-cleanup.md            # Task completion and cleanup procedures
├── rag-usage.md                   # Semantic search and RAG patterns
└── mcp-commands.md                # MCP tool reference and examples
```

### Main CLAUDE.md Structure

The main `CLAUDE.md` file acts as an **orchestration hub** that references modular instructions:

```markdown
# ClaudeTask Framework - Autonomous Orchestrator Configuration

## 🔴 CRITICAL INSTRUCTIONS
📖 [CRITICAL RESTRICTIONS](./.claudetask/instructions/critical-restrictions.md)

## 📚 Core Workflow Instructions

### Task Status Management
📖 [Status Transitions](./.claudetask/instructions/status-transitions.md)

### Agent Delegation
📖 [Agent Selection Guide](./.claudetask/instructions/agent-selection-guide.md)

### Specific Phase Workflows
📖 [Analysis Phase](./.claudetask/instructions/analysis-phase.md)
📖 [Testing Workflow](./.claudetask/instructions/testing-workflow.md)
📖 [Resource Cleanup](./.claudetask/instructions/resource-cleanup.md)
```

## Instruction Files

### 1. critical-restrictions.md

**Purpose**: Define absolute rules that must NEVER be violated

**Content**:
- Never delete worktrees without explicit user request
- Never mark tasks as "Done" without explicit user request
- Never transition from "Code Review" to "Done" automatically
- Never do technical work yourself (delegate to agents)

**When to read**: Always, before any action

### 2. project-modes.md

**Purpose**: Explain SIMPLE vs DEVELOPMENT mode workflows

**Content**:
- **SIMPLE mode**: 3-column workflow (Backlog → In Progress → Done)
- **DEVELOPMENT mode**: 6-column workflow with analysis, testing, code review (includes PR)
- Mode detection and appropriate workflow selection
- Worktree toggle in DEVELOPMENT mode

**When to read**: When starting task or determining workflow approach

### 3. orchestration-role.md

**Purpose**: Define coordinator agent responsibilities

**Content**:
- Pure orchestration (no technical work)
- Continuous monitoring loop
- Delegation patterns
- Status update responsibilities
- Never analyze, code, or document directly

**When to read**: At session start to understand role

### 4. status-transitions.md

**Purpose**: Document task status workflow and transition rules

**Content**:
- Status flow: Backlog → Analysis → In Progress → Testing → Code Review → Done
- Auto-transition rules
- Manual transition requirements
- Stage result requirements (mandatory for every transition)
- Transition validation

**When to read**: Before updating any task status

### 5. agent-selection-guide.md

**Purpose**: Guide selection of appropriate specialized agents

**Content**:
- Frontend agents (React, mobile-responsive UI)
- Backend agents (FastAPI, Python)
- Analysis agents (requirements, architecture)
- Review agents (code review, PR creation)
- Agent capabilities and limitations
- Never cross-assign outside agent's domain

**When to read**: Before delegating any work

### 6. analysis-phase.md

**Purpose**: Guide requirements and architecture creation

**Content**:
- Requirements analyst workflow
- System architect workflow
- Output folder structure (Analyse/Requirements/, Analyse/Design/)
- Auto-transition to "In Progress"
- Worktree and branch creation

**When to read**: When task is in "Analysis" status

### 7. testing-workflow.md

**Purpose**: Guide test environment setup and manual testing

**Content**:
- Port finding and server startup
- **MANDATORY**: Testing URL saving with `mcp:set_testing_urls`
- Test plan creation (Tests/test-plan.md)
- Manual testing instructions (no automated testing delegation)
- Test environment cleanup

**When to read**: When task moves to "Testing" status

### 8. resource-cleanup.md

**Purpose**: Guide task completion and resource cleanup

**Content**:
- `mcp:stop_session {task_id}` command usage
- Process termination (test servers)
- Port release
- Testing URL clearing
- Worktree cleanup (optional)
- ONLY when user explicitly requests completion

**When to read**: When user requests task completion

### 9. rag-usage.md

**Purpose**: Document semantic search and RAG patterns

**Content**:
- When to use RAG tools
- Agents have built-in RAG access
- Optional RAG context for delegation
- Search patterns and best practices

**When to read**: When gathering context or searching codebase

### 10. mcp-commands.md

**Purpose**: Complete MCP tool reference

**Content**:
- Task management commands
- Status update commands
- Stage result commands
- Testing URL commands
- Session management commands
- RAG search commands

**When to read**: When using MCP tools

## Usage Patterns

### Just-in-Time Reading

The modular system supports **just-in-time reading**:

```python
# Coordinator agent workflow
while True:
    tasks = mcp:get_task_queue()

    for task in tasks:
        if task.status == "Analysis":
            # Read analysis-phase.md NOW (not before)
            instructions = read("analysis-phase.md")
            follow(instructions)

        elif task.status == "Testing":
            # Read testing-workflow.md NOW
            instructions = read("testing-workflow.md")
            follow(instructions)

        elif task.status == "Done Request":
            # Read resource-cleanup.md NOW
            instructions = read("resource-cleanup.md")
            follow(instructions)
```

### Layered Reading

Instructions are read in layers:

1. **Core concepts** (always loaded):
   - critical-restrictions.md
   - project-modes.md
   - orchestration-role.md

2. **Workflow guidance** (loaded when needed):
   - status-transitions.md
   - agent-selection-guide.md

3. **Phase-specific** (loaded for specific task states):
   - analysis-phase.md
   - testing-workflow.md
   - resource-cleanup.md

4. **Technical reference** (loaded when using specific tools):
   - rag-usage.md
   - mcp-commands.md

## Benefits

### 1. Reduced Cognitive Load

Agents don't need to remember everything - just know which instruction to read when needed.

### 2. Easier Updates

Update specific workflows without affecting others:
- Change analysis workflow → update analysis-phase.md only
- Change testing workflow → update testing-workflow.md only
- No risk of breaking unrelated workflows

### 3. Better Testing

Each instruction can be tested independently:
- Verify analysis phase works correctly
- Verify testing workflow handles edge cases
- Isolated testing prevents cascading failures

### 4. Improved Collaboration

Multiple developers can work on different instruction files simultaneously:
- Developer A updates analysis-phase.md
- Developer B updates testing-workflow.md
- No merge conflicts

### 5. Version Control

Track changes to specific workflows:
```bash
git log -- .claudetask/instructions/testing-workflow.md
# See all changes to testing workflow only
```

## Best Practices

### For Framework Developers

1. **Single Responsibility**: Each instruction file should focus on ONE workflow phase
2. **Clear Naming**: File names should immediately convey purpose
3. **Cross-References**: Link to related instructions when appropriate
4. **Examples**: Include practical examples in each instruction
5. **Validation**: Include checklist for verifying correct behavior

### For Coordinator Agents

1. **Read When Needed**: Don't load all instructions at start
2. **Follow Exactly**: Instructions are prescriptive - follow them precisely
3. **Reference Back**: Re-read instructions if uncertain
4. **Log Decisions**: Document which instruction guided each decision
5. **Report Issues**: Flag unclear or contradictory instructions

### For Project Maintainers

1. **Keep Updated**: Update instructions when workflow changes
2. **Test Changes**: Verify instruction changes work correctly
3. **Document Changes**: Explain why instruction was modified
4. **Review Regularly**: Periodic review ensures instructions stay current
5. **Gather Feedback**: Listen to agent behavior and adjust instructions

## Migration from Monolithic CLAUDE.md

### Before (Monolithic)

```markdown
# CLAUDE.md (5000+ lines)

## Task Management
[500 lines of task management instructions]

## Analysis Phase
[800 lines of analysis instructions]

## Testing Phase
[600 lines of testing instructions]

## ... (continues)
```

### After (Modular)

```markdown
# CLAUDE.md (300 lines)

## Task Management
📖 [Status Transitions](./.claudetask/instructions/status-transitions.md)

## Analysis Phase
📖 [Analysis Phase](./.claudetask/instructions/analysis-phase.md)

## Testing Phase
📖 [Testing Workflow](./.claudetask/instructions/testing-workflow.md)
```

Each referenced file contains detailed instructions for that specific phase.

## Instruction File Template

### Structure

```markdown
# [Instruction Name]

Complete guide for [specific workflow phase].

## When to Read This

Read this instruction when:
- Specific condition 1
- Specific condition 2
- Specific condition 3

## Prerequisites

Before following this instruction:
- Prerequisite 1
- Prerequisite 2

## Workflow Steps

### Step 1: [Action]
[Detailed instructions]

### Step 2: [Action]
[Detailed instructions]

## Expected Outcomes

After completing this workflow:
- Outcome 1
- Outcome 2

## Common Issues

### Issue 1
**Symptom**: [Description]
**Solution**: [Steps to resolve]

## Related Instructions

- [Link to related instruction 1]
- [Link to related instruction 2]

## Examples

### Example 1: [Scenario]
[Complete example]

### Example 2: [Scenario]
[Complete example]
```

## Troubleshooting

### Instruction Not Found

**Symptom**: Agent can't find instruction file

**Solutions**:
- Verify file exists in `.claudetask/instructions/`
- Check file path in CLAUDE.md is correct
- Ensure file has `.md` extension
- Verify file permissions allow reading

### Contradictory Instructions

**Symptom**: Two instructions provide conflicting guidance

**Solutions**:
- Review both instructions
- Identify contradiction
- Follow instruction with higher priority (critical-restrictions.md has highest priority)
- Report contradiction to maintainers

### Outdated Instructions

**Symptom**: Instruction doesn't match current codebase behavior

**Solutions**:
- Verify instruction file version
- Check if framework was recently updated
- Update instruction to match current behavior
- Test updated instruction thoroughly

## Related Documentation

- [Intelligent Workflow](./intelligent-workflow.md) - Complete workflow overview
- [Project Modes](./project-modes.md) - SIMPLE vs DEVELOPMENT modes
- [Orchestration Role](../../framework-assets/claude-configs/instructions/orchestration-role.md) - Coordinator responsibilities

---

**Last Updated**: 2025-11-21
**Version**: 1.0.0
**Status**: Active in DEVELOPMENT mode
