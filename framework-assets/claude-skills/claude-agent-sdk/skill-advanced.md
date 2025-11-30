hook_events[6]{event,trigger_point,use_case}:
PreToolUse,Before tool execution,Validation and blocking
PostToolUse,After tool completes,Logging and monitoring
UserPromptSubmit,User submits prompt,Input sanitization
Stop,Agent stops,Cleanup operations
SubagentStop,Subagent completes,Result processing
PreCompact,Before message compaction,Message preservation
```

**Hook Function Signature:**
```python
async def hook_function(
    input_data: dict[str, Any],
    tool_use_id: str | None,
    context: HookContext
) -> dict[str, Any]:
    # Return {} for no action
    # Return hook-specific output to modify behavior
    pass
```

**Example - Block Dangerous Commands:**
```python
from claude_agent_sdk import ClaudeAgentOptions, HookMatcher

async def validate_bash(input_data, tool_use_id, context):
    """Block dangerous bash commands."""
    if input_data['tool_name'] == 'Bash':
        command = input_data['tool_input'].get('command', '')

        dangerous_patterns = ['rm -rf /', 'mkfs', ':(){:|:&};:']
        for pattern in dangerous_patterns:
            if pattern in command:
                return {
                    'hookSpecificOutput': {
                        'hookEventName': 'PreToolUse',
                        'permissionDecision': 'deny',
                        'permissionDecisionReason': f'Blocked: {pattern}'
                    }
                }
    return {}

options = ClaudeAgentOptions(
    hooks={
        'PreToolUse': [
            HookMatcher(matcher='Bash', hooks=[validate_bash])
        ]
    }
)
```

**Hook Matcher Patterns:**
```
matcher_patterns[3]{matcher_value,matches,example}:
'ToolName',Specific tool,'Bash' matches Bash tool only
'*',All tools,'*' matches any tool
'mcp__server__*',MCP server tools,'mcp__calc__*' matches all calc tools
```

## Structured Output

**Enforce JSON schema validation on Claude's responses:**

```python
from claude_agent_sdk import query, ClaudeAgentOptions

# Define schema
user_schema = {
    "type": "object",
    "properties": {
        "name": {"type": "string"},
        "age": {"type": "integer", "minimum": 0},
        "email": {"type": "string", "format": "email"},
        "skills": {
            "type": "array",
            "items": {"type": "string"}
        }
    },
    "required": ["name", "email"]
}

options = ClaudeAgentOptions(
    output_format={
        "type": "json_schema",
        "schema": user_schema
    }
)

async for message in query("Extract developer info", options):
    print(message)
```

**Benefits:**
- Guaranteed structure for programmatic parsing
- Type validation at API level
- Reduced parsing errors
- Consistent response format

**Output Format Structure:**
```
output_format[2]{field,value,description}:
type,json_schema,Must be 'json_schema'
schema,dict,Valid JSON Schema object
```

## Subagents

**Delegate specialized work to purpose-built agents:**

```python
from claude_agent_sdk import query, ClaudeAgentOptions, AgentDefinition

# Define specialized agents
code_reviewer = AgentDefinition(
    description="Expert Python code reviewer",
    prompt="You are a senior Python developer. Review code for bugs, style, and best practices.",
    tools=["Read", "Grep"],
    model="sonnet"
)

documentation_writer = AgentDefinition(
    description="Technical documentation specialist",
    prompt="You write clear, comprehensive documentation.",
    tools=["Read", "Write", "Grep"],
    model="haiku"
)

# Configure agents
options = ClaudeAgentOptions(
    agents={
        "reviewer": code_reviewer,
        "docs": documentation_writer
    },
    allowed_tools=["Task", "Read"]
)

# Orchestrator delegates to agents
async for message in query("Review and document this project", options):
    print(message)
```

**AgentDefinition Parameters:**
```
agent_params[4]{parameter,type,description}:
description,str,Agent purpose and capabilities
prompt,str,System prompt for the agent
tools,list[str],Tools available to agent
model,str,"Model override (e.g., 'sonnet', 'haiku')"
```

**Delegation via Task Tool:**
- Claude automatically invokes `Task` tool when subagent needed
- Passes instructions to appropriate agent
- Subagent executes with limited tool access
- Results returned to orchestrator

## Error Handling

**SDK Exception Types (TOON Format):**
```
exceptions[4]{exception,trigger,attributes}:
CLINotFoundError,Claude Code CLI not installed,message
CLIConnectionError,Connection failure,message
ProcessError,Process exit with error,"exit_code, stderr, stdout"
CLIJSONDecodeError,Response parsing failure,"line, original_error"
```

**Comprehensive Error Handling:**
```python
from claude_agent_sdk import (
    query,
    CLINotFoundError,
    CLIConnectionError,
    ProcessError,
    CLIJSONDecodeError
)

async def safe_query(prompt: str):
    try:
        async for message in query(prompt):
            yield message

    except CLINotFoundError:
        print("ERROR: Claude Code CLI not installed")
        print("Install: npm install -g @anthropic-ai/claude-code")

    except CLIConnectionError as e:
        print(f"Connection failed: {e}")
        print("Check Claude Code service status")

    except ProcessError as e:
        print(f"Process failed with exit code {e.exit_code}")
        if e.stderr:
            print(f"Error output: {e.stderr}")
        if e.stdout:
            print(f"Standard output: {e.stdout}")

    except CLIJSONDecodeError as e:
        print(f"Failed to parse response at line: {e.line}")
        print(f"Underlying error: {e.original_error}")

    except Exception as e:
        print(f"Unexpected error: {e}")
        raise

# Usage
async for msg in safe_query("Analyze code"):
    process(msg)
```

## Setting Sources

**Control which configuration files load:**

```
setting_sources[3]{source,location,contains}:
user,~/.claude/settings.json,User-global settings
project,.claude/settings.json + CLAUDE.md,Project-specific config
local,.claude/settings.local.json,Local overrides (gitignored)
```

**Configuration Loading:**
```python
# Default: Load user and project settings
options = ClaudeAgentOptions()

# Project only (ignore user settings)
options = ClaudeAgentOptions(
    setting_sources=["project"]
)

# No filesystem settings (pure SDK)
options = ClaudeAgentOptions(
    setting_sources=[]
)

# Custom combination
options = ClaudeAgentOptions(
    setting_sources=["user", "local"]
)
```

**Use Cases:**
- `setting_sources=[]` - Pure SDK applications (no file dependencies)
- `setting_sources=["project"]` - Project-specific automation
- `setting_sources=["user", "project", "local"]` - Full config hierarchy

## Common Patterns

### Pattern 1: Continuous Monitoring

```python
async with ClaudeSDKClient() as client:
    await client.query("Monitor system status")

    async for message in client.receive_response():
        if isinstance(message, AssistantMessage):
            for block in message.content:
                if isinstance(block, ToolUseBlock):
                    print(f"Executing: {block.toolName}")
                elif isinstance(block, TextBlock):
                    print(f"Status: {block.text}")

        if isinstance(message, ResultMessage):
            print(f"Monitoring complete. Cost: ${message.totalCost}")
            break
```

### Pattern 2: Custom Permission Control

```python
async def can_use_tool(tool_name: str, tool_input: dict) -> bool:
    """Custom tool authorization."""
    # Block network tools in production
    if os.getenv("ENV") == "production":
        if tool_name in ["WebSearch", "WebFetch"]:
            return False

    # Limit Bash to safe commands
    if tool_name == "Bash":
        command = tool_input.get("command", "")
        allowed_prefixes = ["ls", "cat", "grep", "find"]
        return any(command.startswith(cmd) for cmd in allowed_prefixes)

    return True

options = ClaudeAgentOptions(
    can_use_tool=can_use_tool
)
```

### Pattern 3: Streaming Input Construction

```python
async def build_context():
    """Dynamically generate input context."""
    yield {"type": "text", "text": "Analyze the following data:"}

    for file in get_data_files():
        content = await read_file(file)
        yield {"type": "text", "text": f"\n\nFile {file}:\n{content}"}

async with ClaudeSDKClient() as client:
    await client.query(build_context())
    async for msg in client.receive_response():
        process(msg)
```

## Best Practices

**Tool Selection:**
- Use `allowed_tools` whitelist for security-critical applications
- Minimize tool access to reduce attack surface
- Grant `Bash` access cautiously (consider `can_use_tool` hook)

**Session Management:**
- Use `ClaudeSDKClient` as context manager for automatic cleanup
- Call `disconnect()` in finally block for manual lifecycle
- Handle interrupts gracefully with try/except

**Error Handling:**
- Always catch `CLINotFoundError` for better user experience
- Log `ProcessError` stderr for debugging
- Implement retries for transient `CLIConnectionError`

**Performance:**
- Use `max_turns` to prevent infinite loops
- Set reasonable timeouts for Bash commands
- Stream results instead of buffering entire response

**Security:**
- Never use `bypassPermissions` without user consent
- Validate tool inputs in PreToolUse hooks
- Sanitize file paths to prevent directory traversal
- Review `setting_sources` to avoid unwanted config loading

## Additional Resources

- **Options Reference:** [reference/options.md](reference/options.md) - Complete ClaudeAgentOptions documentation
- **Tools Reference:** [reference/tools.md](reference/tools.md) - All built-in tools with examples
- **Hooks Reference:** [reference/hooks.md](reference/hooks.md) - Hook system deep dive
- **Basic Examples:** [examples/basic.md](examples/basic.md) - Getting started examples
- **Advanced Examples:** [examples/advanced.md](examples/advanced.md) - MCP, hooks, and subagents

## Quick Reference Card

```
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
```
