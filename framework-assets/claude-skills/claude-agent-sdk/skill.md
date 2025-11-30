---
name: claude-agent-sdk
description: Complete reference for Claude Agent SDK (Python) - building autonomous agents with query(), ClaudeSDKClient, MCP servers, hooks, and all built-in tools
version: 1.0.0
tags: [sdk, python, agents, automation, mcp, hooks, claude-code, autonomous]
---

# Claude Agent SDK (Python)

Expert skill for building autonomous agents using the Claude Agent SDK. Build intelligent automation, maintain persistent conversations, create custom tools, and orchestrate complex workflows.

## What is Claude Agent SDK?

Python SDK for programmatic interaction with Claude via Claude Code. Two core patterns:
- **query()** - One-off tasks with fresh sessions (no memory retention)
- **ClaudeSDKClient** - Persistent sessions maintaining conversation context

**Key capabilities:**
- Programmatic agent control with full tool access
- Custom MCP tool creation with @tool decorator
- Lifecycle hooks for validation and control
- Structured JSON output with schema validation
- Subagent orchestration for specialized tasks
- Real-time streaming and async iteration

## Installation & Setup

```bash
pip install claude-agent-sdk
```

**Requirements:**
- Python 3.9+
- Claude Code CLI installed and configured
- Valid Anthropic API key

## Quick Start

### Simple One-Off Query

```python
import asyncio
from claude_agent_sdk import query

async def main():
    async for message in query("Create a Python hello world script"):
        print(message)

asyncio.run(main())
```

### Persistent Conversation

```python
import asyncio
from claude_agent_sdk import ClaudeSDKClient

async def main():
    async with ClaudeSDKClient() as client:
        await client.query("What's 2+2?")
        async for msg in client.receive_response():
            print(msg)

        # Maintains context
        await client.query("Multiply that by 10")
        async for msg in client.receive_response():
            print(msg)

asyncio.run(main())
```

## Documentation Structure

This skill is organized into focused modules for easy navigation:

### Core Concepts
- **[skill-core.md](skill-core.md)** - Core API, message types, and basic patterns
- **[skill-advanced.md](skill-advanced.md)** - Custom tools, MCP servers, hooks, and subagents

### Complete Reference
- **[reference/options.md](reference/options.md)** - ClaudeAgentOptions complete reference
- **[reference/tools-file-exec.md](reference/tools-file-exec.md)** - File operations and execution tools
- **[reference/tools-reference.md](reference/tools-reference.md)** - Web, development, and MCP tools
- **[reference/hooks-events.md](reference/hooks-events.md)** - Hook system and event types
- **[reference/hooks-patterns.md](reference/hooks-patterns.md)** - Advanced hook patterns and best practices

### Practical Examples
- **[examples/basic.md](examples/basic.md)** - Getting started examples
- **[examples/advanced-mcp.md](examples/advanced-mcp.md)** - Custom MCP servers and database integration
- **[examples/advanced-hooks.md](examples/advanced-hooks.md)** - Security hooks, audit logging, rate limiting
- **[examples/advanced-agents.md](examples/advanced-agents.md)** - Multi-agent orchestration and production configs

## Quick Reference (TOON Format)

**Common Operations:**
```
operations[8]{operation,code_pattern,use_case}:
One-off query,"query('prompt', options)",Single task execution
Persistent session,"ClaudeSDKClient() as client",Multi-turn conversation
Custom tool,"@tool('name', 'desc', schema)",Create MCP tool
MCP server,"create_sdk_mcp_server(name, tools)",Bundle custom tools
Security hook,"PreToolUse + permissionDecision",Validate operations
Audit logging,"PostToolUse + file logging",Track tool usage
Structured output,"output_format + JSON schema",Guarantee format
Multi-agent,"agents={} + Task tool",Specialized delegation
```

**Import Statements:**
```python
# Core
from claude_agent_sdk import query, ClaudeSDKClient, ClaudeAgentOptions

# Message types
from claude_agent_sdk import (
    AssistantMessage,
    TextBlock,
    ToolUseBlock,
    ResultMessage
)

# Custom tools
from claude_agent_sdk import tool, create_sdk_mcp_server

# Hooks
from claude_agent_sdk import HookMatcher, HookContext

# Subagents
from claude_agent_sdk import AgentDefinition

# Errors
from claude_agent_sdk import (
    CLINotFoundError,
    ProcessError,
    CLIJSONDecodeError
)
```

## Core Concepts Summary

**query() Function:**
- One-off tasks with fresh sessions
- Returns async iterator of messages
- No conversation memory retention

**ClaudeSDKClient:**
- Maintains persistent conversation context
- Use as async context manager
- Supports interrupts and session control

**ClaudeAgentOptions:**
- Primary configuration mechanism
- Controls tools, permissions, hooks, agents
- See [reference/options.md](reference/options.md)

**Built-in Tools:**
- 20+ tools for files, execution, web, development
- Access control via allowed_tools/disallowed_tools
- See [reference/tools-file-exec.md](reference/tools-file-exec.md) and [reference/tools-reference.md](reference/tools-reference.md)

**Custom MCP Tools:**
- Define with @tool decorator
- Bundle with create_sdk_mcp_server()
- See [examples/advanced-mcp.md](examples/advanced-mcp.md)

**Hooks System:**
- Intercept lifecycle events (PreToolUse, PostToolUse, etc.)
- Validate, log, or modify behavior
- See [reference/hooks-events.md](reference/hooks-events.md)

**Subagents:**
- Specialized agents via AgentDefinition
- Delegate via Task tool
- See [examples/advanced-agents.md](examples/advanced-agents.md)

**Structured Output:**
- Enforce JSON schema on responses
- Guarantee parseable results
- Configure via output_format

## Common Use Cases

**Read-Only Analysis:**
```python
options = ClaudeAgentOptions(
    allowed_tools=["Read", "Grep", "Glob", "WebSearch"],
    permission_mode="default"
)
```

**Automated Refactoring:**
```python
options = ClaudeAgentOptions(
    permission_mode="acceptEdits",
    allowed_tools=["Read", "Write", "Edit", "Bash"]
)
```

**Production Security:**
```python
options = ClaudeAgentOptions(
    allowed_tools=["Read", "Grep"],  # Whitelist
    permission_mode="default",
    hooks={'PreToolUse': [security_validator]},
    max_turns=50
)
```

**Multi-Agent Workflow:**
```python
options = ClaudeAgentOptions(
    agents={
        "reviewer": code_reviewer,
        "tester": test_writer
    },
    allowed_tools=["Task", "Read"]
)
```

## Best Practices

**Security:**
1. Use `allowed_tools` whitelist (not `disallowed_tools` blacklist)
2. Implement `can_use_tool` or PreToolUse hooks for validation
3. Never use `bypassPermissions` without explicit user consent
4. Validate file paths in hooks
5. Load minimal `setting_sources` for security-critical apps

**Performance:**
1. Set `max_turns` to prevent infinite loops
2. Use `permission_mode="acceptEdits"` for automation
3. Enable `include_partial_messages` only when needed
4. Choose appropriate models for subagents (haiku for simple tasks)

**Error Handling:**
1. Always catch `CLINotFoundError`
2. Log `ProcessError` stderr for debugging
3. Implement retries for `CLIConnectionError`
4. Use try/except in hooks (return {} on error)

## Navigation Guide

**New to the SDK?**
1. Read [skill-core.md](skill-core.md) - Core API and message types
2. Study [examples/basic.md](examples/basic.md) - Getting started examples
3. Review [reference/options.md](reference/options.md) - Configuration options

**Building custom tools?**
1. Read [skill-advanced.md](skill-advanced.md) - Custom tools section
2. Study [examples/advanced-mcp.md](examples/advanced-mcp.md) - MCP server examples
3. Reference [reference/tools-file-exec.md](reference/tools-file-exec.md) - Built-in tools

**Adding security/validation?**
1. Read [reference/hooks-events.md](reference/hooks-events.md) - Hook system
2. Study [examples/advanced-hooks.md](examples/advanced-hooks.md) - Hook patterns
3. Reference [reference/hooks-patterns.md](reference/hooks-patterns.md) - Advanced patterns

**Multi-agent orchestration?**
1. Read [skill-advanced.md](skill-advanced.md) - Subagents section
2. Study [examples/advanced-agents.md](examples/advanced-agents.md) - Orchestration examples
3. Review [reference/options.md](reference/options.md) - Agent configuration

## Quick Reference Card

```python
# One-off query
from claude_agent_sdk import query
async for msg in query("Task"): ...

# Persistent session
from claude_agent_sdk import ClaudeSDKClient
async with ClaudeSDKClient() as client:
    await client.query("Question")
    async for msg in client.receive_response(): ...

# Custom tool
from claude_agent_sdk import tool
@tool("name", "desc", {"param": type})
async def func(args): return {"content": [...]}

# MCP server
from claude_agent_sdk import create_sdk_mcp_server
server = create_sdk_mcp_server("name", "1.0", [tool1, tool2])

# Hooks
options = ClaudeAgentOptions(hooks={
    'PreToolUse': [HookMatcher(matcher='Tool', hooks=[hook_fn])]
})

# Structured output
options = ClaudeAgentOptions(output_format={
    "type": "json_schema",
    "schema": {...}
})

# Subagents
options = ClaudeAgentOptions(agents={
    "name": AgentDefinition(description="...", prompt="...", tools=[...])
})
```

## Complete File Index

**Core Documentation:**
- [skill-core.md](skill-core.md) - Core API reference
- [skill-advanced.md](skill-advanced.md) - Advanced features

**Reference:**
- [reference/options.md](reference/options.md) - ClaudeAgentOptions
- [reference/tools-file-exec.md](reference/tools-file-exec.md) - File/exec tools
- [reference/tools-reference.md](reference/tools-reference.md) - Web/dev tools
- [reference/hooks-events.md](reference/hooks-events.md) - Hook events
- [reference/hooks-patterns.md](reference/hooks-patterns.md) - Hook patterns

**Examples:**
- [examples/basic.md](examples/basic.md) - Getting started
- [examples/advanced-mcp.md](examples/advanced-mcp.md) - MCP servers
- [examples/advanced-hooks.md](examples/advanced-hooks.md) - Hooks
- [examples/advanced-agents.md](examples/advanced-agents.md) - Multi-agent

## External Resources

- **Official Docs:** https://platform.claude.com/docs/en/agent-sdk/python
- **GitHub:** https://github.com/anthropics/claude-agent-sdk-python
- **PyPI:** https://pypi.org/project/claude-agent-sdk/

---

**Ready to build autonomous agents with Claude? Start with [skill-core.md](skill-core.md) or jump to [examples/basic.md](examples/basic.md) for hands-on learning.**
