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

## Core API Reference

### query() Function

**Purpose:** Execute one-off queries with fresh sessions (no memory)

**Signature:**
```python
async def query(
    prompt: str | AsyncIterable[dict],
    options: ClaudeAgentOptions = None
) -> AsyncIterator[Message]
```

**Parameters:**
```
parameters[2]{name,type,description}:
prompt,str | AsyncIterable[dict],User prompt or async stream of message dictionaries
options,ClaudeAgentOptions,Configuration options (see reference/options.md)
```

**Returns:** Async iterator yielding Message objects

**When to use:**
- Independent automation tasks
- Scripts with no conversation continuity
- Batch processing where each item is isolated
- Stateless operations

**Example:**
```python
from claude_agent_sdk import query, ClaudeAgentOptions

options = ClaudeAgentOptions(
    permission_mode="acceptEdits",
    cwd="/home/user/project",
    allowed_tools=["Read", "Write", "Bash"]
)

async for message in query("Analyze this codebase", options):
    print(message)
```

### ClaudeSDKClient Class

**Purpose:** Maintain persistent conversation sessions with context

**Key Methods:**
```
methods[5]{method,returns,description}:
connect(),None,Establish connection to Claude Code CLI
query(prompt),None,Submit query to current session
receive_response(),AsyncIterator[Message],Iterate messages until ResultMessage
interrupt(),None,Stop current execution mid-stream
disconnect(),None,Close session and cleanup
```

**Usage Pattern:**
```python
# Recommended: Async context manager
async with ClaudeSDKClient() as client:
    await client.query("First question")
    async for msg in client.receive_response():
        process(msg)

    # Context maintained
    await client.query("Follow-up question")
    async for msg in client.receive_response():
        process(msg)

# Manual lifecycle
client = ClaudeSDKClient()
await client.connect()
try:
    await client.query("Question")
    async for msg in client.receive_response():
        process(msg)
finally:
    await client.disconnect()
```

**When to use:**
- Interactive applications requiring conversation memory
- Multi-turn dialogues
- Iterative development workflows
- Applications needing interrupt capability

### Message Types

**Union Type:** Message = UserMessage | AssistantMessage | SystemMessage | ResultMessage

**Message Attributes:**
```
message_types[4]{type,key_attributes,description}:
UserMessage,content: list[ContentBlock],User input to Claude
AssistantMessage,content: list[ContentBlock],Claude's response content
SystemMessage,message: str,System status and metadata
ResultMessage,"sessionId, totalCost, duration",Final result with metrics
```

**Content Block Types:**
```
content_blocks[4]{block_type,attributes,purpose}:
TextBlock,text: str,Text responses from Claude
ThinkingBlock,thinking: str,Internal reasoning (if available)
ToolUseBlock,"toolName, toolInput, toolUseId",Tool invocation request
ToolResultBlock,"toolUseId, content",Tool execution result
```

**Iteration Pattern:**
```python
from claude_agent_sdk import (
    AssistantMessage,
    TextBlock,
    ToolUseBlock,
    ResultMessage
)

async for message in client.receive_response():
    if isinstance(message, AssistantMessage):
        for block in message.content:
            if isinstance(block, TextBlock):
                print(f"Claude: {block.text}")
            elif isinstance(block, ToolUseBlock):
                print(f"Using tool: {block.toolName}")

    elif isinstance(message, ResultMessage):
        print(f"Session: {message.sessionId}")
        print(f"Cost: ${message.totalCost}")
        break
```

## Configuration with ClaudeAgentOptions

**Full reference:** See [reference/options.md](reference/options.md)

**Common Options (TOON Format):**
```
common_options[8]{option,type,default,description}:
permission_mode,str,default,"Execution mode: default|acceptEdits|plan|bypassPermissions"
cwd,str,current,"Working directory for tool execution"
system_prompt,str,None,"Custom system prompt or preset name"
allowed_tools,list[str],all,"Tool whitelist (e.g., ['Read', 'Write'])"
disallowed_tools,list[str],[],"Tool blacklist"
max_turns,int,None,"Maximum conversation turns"
output_format,dict,None,"JSON schema for structured output"
setting_sources,list[str],"['user','project']","Config sources to load"
```

**Permission Modes:**
```
permission_modes[4]{mode,behavior,use_case}:
default,Standard interactive mode,Normal development workflows
acceptEdits,Auto-approve file changes,Automated refactoring scripts
plan,Planning only - no execution,Design and architecture analysis
bypassPermissions,Skip all permission checks,Trusted automation (use cautiously)
```

**Example with Multiple Options:**
```python
from claude_agent_sdk import ClaudeAgentOptions

options = ClaudeAgentOptions(
    permission_mode="acceptEdits",
    cwd="/home/user/my-project",
    system_prompt="You are an expert Python developer",
    allowed_tools=["Read", "Write", "Edit", "Bash", "Grep"],
    max_turns=50,
    setting_sources=["project"]  # Load only .claude/settings.json
)
```

## Built-in Tools

**Full reference:** See [reference/tools.md](reference/tools.md)

**Tool Categories (TOON Format):**
```
tool_categories[6]{category,tools,primary_use}:
File Operations,"Read, Write, Edit, Glob, Grep",File system manipulation
Execution,"Bash, BashOutput, KillShell",Command execution and monitoring
Web Access,"WebSearch, WebFetch",Internet data retrieval
Development,"NotebookEdit, TodoWrite",Development workflows
Orchestration,"Task, Skill",Subagent delegation
MCP,"ListMcpResources, ReadMcpResource",MCP server resource access
```

**Most Common Tools:**
```
common_tools[10]{tool_name,purpose,key_parameters}:
Read,Read file contents,"file_path, offset, limit"
Write,Create or overwrite file,"file_path, content"
Edit,Replace text in file,"file_path, old_string, new_string"
Bash,Execute shell commands,"command, timeout, run_in_background"
Grep,Search files with regex,"pattern, path, output_mode"
Glob,Find files by pattern,"pattern, path"
WebSearch,Search the internet,"query, allowed_domains, blocked_domains"
WebFetch,Fetch and analyze URLs,"url, prompt"
Task,Delegate to subagent,"agent_name, instructions"
NotebookEdit,Edit Jupyter notebooks,"notebook_path, cell_id, new_source"
```

**Tool Access Control:**
```python
# Whitelist specific tools
options = ClaudeAgentOptions(
    allowed_tools=["Read", "Grep", "WebSearch"]
)

# Blacklist dangerous tools
options = ClaudeAgentOptions(
    disallowed_tools=["Bash", "Write", "Edit"]
)

# MCP tool naming: mcp__servername__toolname
options = ClaudeAgentOptions(
    allowed_tools=["Read", "mcp__calculator__add"]
)
```

## Custom Tools with @tool Decorator

**Create MCP tools programmatically:**

```python
from claude_agent_sdk import tool
from typing import Any

@tool(
    name="calculate_sum",
    description="Add two numbers together",
    input_schema={"a": float, "b": float}
)
async def calculate_sum(args: dict[str, Any]) -> dict[str, Any]:
    result = args["a"] + args["b"]
    return {
        "content": [{
            "type": "text",
            "text": f"The sum is {result}"
        }]
    }

# JSON Schema format also supported
@tool(
    name="greet_user",
    description="Greet a user by name",
    input_schema={
        "type": "object",
        "properties": {
            "name": {"type": "string"},
            "formal": {"type": "boolean"}
        },
        "required": ["name"]
    }
)
async def greet_user(args: dict[str, Any]) -> dict[str, Any]:
    name = args["name"]
    formal = args.get("formal", False)
    greeting = f"Good day, {name}" if formal else f"Hey {name}!"

    return {
        "content": [{
            "type": "text",
            "text": greeting
        }]
    }
```

**Tool Return Format:**
```
tool_return[2]{field,type,description}:
content,list[dict],List of content blocks (text/image/etc)
isError,bool,Optional: mark as error result
```

**Input Schema Formats:**
```
schema_formats[2]{format,example,use_case}:
Simple type map,"{\"name\": str, \"age\": int}",Quick tool definitions
JSON Schema,"{\"type\": \"object\", \"properties\": {...}}",Complex validation
```

## MCP Server Creation

**Bundle custom tools into MCP servers:**

```python
from claude_agent_sdk import tool, create_sdk_mcp_server

@tool("add", "Add numbers", {"a": float, "b": float})
async def add(args):
    return {"content": [{"type": "text", "text": str(args["a"] + args["b"])}]}

@tool("multiply", "Multiply numbers", {"a": float, "b": float})
async def multiply(args):
    return {"content": [{"type": "text", "text": str(args["a"] * args["b"])}]}

# Create server
calculator = create_sdk_mcp_server(
    name="calculator",
    version="1.0.0",
    tools=[add, multiply]
)

# Use in options
options = ClaudeAgentOptions(
    mcp_servers={"calc": calculator},
    allowed_tools=["mcp__calc__add", "mcp__calc__multiply"]
)
```

**Server Configuration:**
```
server_params[3]{parameter,type,description}:
name,str,MCP server identifier
version,str,Server version (optional)
tools,list[callable],List of @tool decorated functions
```

**MCP Tool Naming:** `mcp__<server_name>__<tool_name>`

## Hooks System

**Full reference:** See [reference/hooks.md](reference/hooks.md)

**Intercept lifecycle events for validation and control**

**Hook Events (TOON Format):**
```
