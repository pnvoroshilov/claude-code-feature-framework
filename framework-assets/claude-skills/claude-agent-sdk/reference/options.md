# ClaudeAgentOptions - Complete Reference

Comprehensive configuration dataclass for controlling Claude Agent SDK behavior.

## Overview

`ClaudeAgentOptions` is the primary configuration mechanism for both `query()` and `ClaudeSDKClient`. All parameters are optional with sensible defaults.

## Import

```python
from claude_agent_sdk import ClaudeAgentOptions
```

## Complete Parameter Reference (TOON Format)

### Session Control Parameters

```
session_params[5]{parameter,type,default,description}:
continue_conversation,bool,False,"Resume previous conversation (requires session ID)"
resume,str,None,"Session ID to resume from"
fork_session,bool,False,"Create new branch when resuming (preserves original)"
max_turns,int,None,"Maximum conversation turns (prevents infinite loops)"
cwd,str,current,"Working directory for tool execution"
```

**Example - Session Resumption:**
```python
# Resume from previous session
options = ClaudeAgentOptions(
    continue_conversation=True,
    resume="session_abc123xyz",
    fork_session=True  # Don't modify original session
)

# Limit conversation length
options = ClaudeAgentOptions(
    max_turns=100  # Stop after 100 turns
)

# Set working directory
options = ClaudeAgentOptions(
    cwd="/home/user/my-project"
)
```

### System Behavior Parameters

```
system_params[3]{parameter,type,default,description}:
system_prompt,str,None,"Custom system prompt or preset name"
permission_mode,str,default,"Execution mode: default|acceptEdits|plan|bypassPermissions"
include_partial_messages,bool,False,"Stream partial message updates during generation"
```

**Permission Modes Detailed:**
```
permission_modes[4]{mode,tool_execution,file_edits,use_case}:
default,Interactive prompts,Interactive prompts,Normal development workflow
acceptEdits,Interactive prompts,Auto-approved,Automated refactoring tasks
plan,No execution (plan only),No execution,Architecture design and planning
bypassPermissions,Auto-approved all,Auto-approved,Trusted automation (dangerous!)
```

**Example - System Configuration:**
```python
# Custom system prompt
options = ClaudeAgentOptions(
    system_prompt="You are an expert DevOps engineer specializing in Kubernetes"
)

# Auto-approve file edits
options = ClaudeAgentOptions(
    permission_mode="acceptEdits"
)

# Planning mode only
options = ClaudeAgentOptions(
    permission_mode="plan"
)

# Stream partial updates
options = ClaudeAgentOptions(
    include_partial_messages=True
)
```

### Tool Access Control

```
tool_control[3]{parameter,type,default,description}:
allowed_tools,list[str],all,"Whitelist of permitted tools"
disallowed_tools,list[str],[],"Blacklist of forbidden tools"
can_use_tool,Callable,None,"Custom permission function: (tool_name, tool_input) -> bool"
```

**Tool Access Patterns:**

**Whitelist Approach (Recommended for Security):**
```python
options = ClaudeAgentOptions(
    allowed_tools=[
        "Read",
        "Write",
        "Edit",
        "Grep",
        "Glob",
        "WebSearch"
    ]
)
```

**Blacklist Approach:**
```python
options = ClaudeAgentOptions(
    disallowed_tools=[
        "Bash",           # Block command execution
        "Write",          # Block file creation
        "Edit",           # Block file modification
        "WebFetch"        # Block external requests
    ]
)
```

**MCP Tool Naming:**
```python
# MCP tools use format: mcp__servername__toolname
options = ClaudeAgentOptions(
    allowed_tools=[
        "Read",
        "mcp__calculator__add",
        "mcp__calculator__multiply",
        "mcp__database__query"
    ]
)
```

**Custom Permission Function:**
```python
async def validate_tool_use(tool_name: str, tool_input: dict) -> bool:
    """Custom authorization logic."""

    # Block dangerous bash commands
    if tool_name == "Bash":
        command = tool_input.get("command", "")
        dangerous = ["rm -rf", "mkfs", "dd if=", ":(){:|:&};:"]
        if any(pattern in command for pattern in dangerous):
            return False

    # Restrict file operations to project directory
    if tool_name in ["Read", "Write", "Edit"]:
        file_path = tool_input.get("file_path", "")
        if not file_path.startswith("/home/user/project/"):
            return False

    # Block production environment modifications
    if os.getenv("ENV") == "production":
        if tool_name in ["Write", "Edit", "Bash"]:
            return False

    return True

options = ClaudeAgentOptions(
    can_use_tool=validate_tool_use
)
```

### MCP Server Configuration

```
mcp_params[1]{parameter,type,default,description}:
mcp_servers,dict[str: MCPServer],{},"MCP server instances keyed by server name"
```

**MCP Server Types:**
```
server_types[4]{type,protocol,use_case}:
SDK MCP,In-process,Custom tools via create_sdk_mcp_server()
stdio,Standard I/O,Local MCP servers
http,HTTP API,Remote MCP services
sse,Server-Sent Events,Streaming MCP endpoints
```

**Example - SDK MCP Server:**
```python
from claude_agent_sdk import tool, create_sdk_mcp_server, ClaudeAgentOptions

@tool("calculate", "Perform calculation", {"expr": str})
async def calculate(args):
    result = eval(args["expr"])  # Don't use eval in production!
    return {"content": [{"type": "text", "text": str(result)}]}

calculator = create_sdk_mcp_server(
    name="calculator",
    version="1.0.0",
    tools=[calculate]
)

options = ClaudeAgentOptions(
    mcp_servers={"calc": calculator},
    allowed_tools=["mcp__calc__calculate"]
)
```

**Example - stdio MCP Server:**
```python
from claude_agent_sdk import ClaudeAgentOptions

options = ClaudeAgentOptions(
    mcp_servers={
        "filesystem": {
            "type": "stdio",
            "command": "mcp-server-filesystem",
            "args": ["/home/user/documents"]
        }
    },
    allowed_tools=["mcp__filesystem__read", "mcp__filesystem__write"]
)
```

**Example - HTTP MCP Server:**
```python
options = ClaudeAgentOptions(
    mcp_servers={
        "api": {
            "type": "http",
            "url": "https://api.example.com/mcp",
            "headers": {
                "Authorization": "Bearer token123"
            }
        }
    }
)
```

### Output Configuration

```
output_params[1]{parameter,type,default,description}:
output_format,dict,None,"JSON Schema for structured output validation"
```

**Structured Output Schema:**
```python
# Simple schema
user_schema = {
    "type": "object",
    "properties": {
        "name": {"type": "string"},
        "age": {"type": "integer"}
    },
    "required": ["name"]
}

options = ClaudeAgentOptions(
    output_format={
        "type": "json_schema",
        "schema": user_schema
    }
)
```

**Complex Schema Example:**
```python
analysis_schema = {
    "type": "object",
    "properties": {
        "summary": {"type": "string"},
        "findings": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "severity": {"type": "string", "enum": ["low", "medium", "high"]},
                    "description": {"type": "string"},
                    "file": {"type": "string"},
                    "line": {"type": "integer"}
                },
                "required": ["severity", "description"]
            }
        },
        "metrics": {
            "type": "object",
            "properties": {
                "files_analyzed": {"type": "integer"},
                "issues_found": {"type": "integer"}
            }
        }
    },
    "required": ["summary", "findings"]
}

options = ClaudeAgentOptions(
    output_format={
        "type": "json_schema",
        "schema": analysis_schema
    }
)
```

### Hooks Configuration

```
hooks_param[1]{parameter,type,default,description}:
hooks,dict[str: list[HookMatcher]],{},"Event hooks by event type"
```

**Hook Event Types:**
```
hook_events[6]{event,trigger,input_data_fields}:
PreToolUse,Before tool execution,"tool_name, tool_input"
PostToolUse,After tool completes,"tool_name, tool_result"
UserPromptSubmit,User submits prompt,prompt_text
Stop,Agent stops,exit_reason
SubagentStop,Subagent completes,agent_name
PreCompact,Before message compaction,message_count
```

**HookMatcher Structure:**
```python
from claude_agent_sdk import HookMatcher

matcher = HookMatcher(
    matcher="*",           # Tool pattern: specific name, "*", or "mcp__server__*"
    hooks=[hook_function]  # List of async hook functions
)
```

**Example - Multiple Hooks:**
```python
from claude_agent_sdk import ClaudeAgentOptions, HookMatcher

async def log_bash_commands(input_data, tool_use_id, context):
    """Log all bash commands."""
    if input_data['tool_name'] == 'Bash':
        command = input_data['tool_input'].get('command')
        print(f"[LOG] Executing: {command}")
    return {}

async def validate_file_paths(input_data, tool_use_id, context):
    """Ensure file operations stay in project directory."""
    if input_data['tool_name'] in ['Write', 'Edit', 'Read']:
        file_path = input_data['tool_input'].get('file_path', '')
        if not file_path.startswith('/home/user/project/'):
            return {
                'hookSpecificOutput': {
                    'hookEventName': 'PreToolUse',
                    'permissionDecision': 'deny',
                    'permissionDecisionReason': 'File path outside project directory'
                }
            }
    return {}

async def on_completion(input_data, tool_use_id, context):
    """Cleanup on agent stop."""
    print("[INFO] Agent execution completed")
    # Perform cleanup tasks
    return {}

options = ClaudeAgentOptions(
    hooks={
        'PreToolUse': [
            HookMatcher(matcher='Bash', hooks=[log_bash_commands]),
            HookMatcher(matcher='*', hooks=[validate_file_paths])
        ],
        'Stop': [
            HookMatcher(matcher='*', hooks=[on_completion])
        ]
    }
)
```

### Subagent Configuration

```
subagent_param[1]{parameter,type,default,description}:
agents,dict[str: AgentDefinition],{},"Specialized subagents keyed by name"
```

**AgentDefinition Structure:**
```python
from claude_agent_sdk import AgentDefinition

agent = AgentDefinition(
    description="Agent purpose and capabilities",
    prompt="System prompt for this agent",
    tools=["Read", "Write"],        # Tools available to agent
    model="sonnet"                   # Model override (optional)
)
```

**Example - Multiple Specialized Agents:**
```python
from claude_agent_sdk import ClaudeAgentOptions, AgentDefinition

# Define agents
code_reviewer = AgentDefinition(
    description="Expert code reviewer for Python projects",
    prompt="""You are a senior Python developer. Review code for:
    - Bugs and logic errors
    - Security vulnerabilities
    - Performance issues
    - Code style and best practices
    Provide detailed, actionable feedback.""",
    tools=["Read", "Grep", "Glob"],
    model="sonnet"
)

test_writer = AgentDefinition(
    description="Automated test case generator",
    prompt="""You write comprehensive unit tests using pytest.
    Follow TDD principles and aim for 100% coverage.""",
    tools=["Read", "Write", "Bash"],
    model="sonnet"
)

documentation_writer = AgentDefinition(
    description="Technical documentation specialist",
    prompt="""You write clear, comprehensive documentation including:
    - API references
    - Usage examples
    - Architecture diagrams""",
    tools=["Read", "Write", "Glob"],
    model="haiku"  # Faster model for docs
)

refactoring_agent = AgentDefinition(
    description="Code refactoring specialist",
    prompt="""You refactor code to improve:
    - Readability
    - Maintainability
    - Performance
    Preserve functionality while improving structure.""",
    tools=["Read", "Write", "Edit", "Bash"],
    model="sonnet"
)

# Configure options
options = ClaudeAgentOptions(
    agents={
        "reviewer": code_reviewer,
        "tester": test_writer,
        "documenter": documentation_writer,
        "refactor": refactoring_agent
    },
    allowed_tools=["Task", "Read"]  # Orchestrator delegates via Task
)
```

**Subagent Delegation Pattern:**
```python
# Claude automatically uses Task tool to invoke subagents
async for message in query(
    "Review this codebase, write tests, and create documentation",
    options
):
    # Claude delegates to appropriate agents:
    # 1. "reviewer" agent analyzes code
    # 2. "tester" agent writes tests
    # 3. "documenter" agent creates docs
    print(message)
```

### Setting Sources Configuration

```
settings_param[1]{parameter,type,default,description}:
setting_sources,list[str],"['user', 'project']","Config file sources to load"
```

**Available Sources:**
```
sources[3]{source,file_path,priority}:
user,~/.claude/settings.json,1 (lowest)
project,.claude/settings.json + CLAUDE.md,2
local,.claude/settings.local.json,3 (highest)
```

**Configuration Priority:**
- Settings merge with later sources overriding earlier ones
- `local` overrides `project` overrides `user`
- SDK parameters override all file-based settings

**Example - Source Control:**
```python
# Default: Load user and project settings
options = ClaudeAgentOptions()

# Project only (ignore user preferences)
options = ClaudeAgentOptions(
    setting_sources=["project"]
)

# Pure SDK mode (no file dependencies)
options = ClaudeAgentOptions(
    setting_sources=[]
)

# All sources (full hierarchy)
options = ClaudeAgentOptions(
    setting_sources=["user", "project", "local"]
)
```

**Use Cases by Source Configuration:**
```
use_cases[4]{sources,scenario,benefit}:
[],"Pure SDK applications","No filesystem dependencies, portable"
['project'],"Project-specific automation","Consistent project behavior across users"
"['user', 'project']","Development workflows (default)","Balanced personalization and project standards"
"['user', 'project', 'local']","Advanced development","Full customization with local overrides"
```

## Complete Configuration Example

**Production-Ready Configuration:**
```python
from claude_agent_sdk import ClaudeAgentOptions, AgentDefinition, HookMatcher

# Hook functions
async def audit_tool_use(input_data, tool_use_id, context):
    """Audit all tool usage to log file."""
    with open("/var/log/claude-audit.log", "a") as f:
        f.write(f"{datetime.now()}: {input_data['tool_name']}\n")
    return {}

async def block_production_writes(input_data, tool_use_id, context):
    """Block file modifications in production."""
    if os.getenv("ENV") == "production":
        if input_data['tool_name'] in ['Write', 'Edit']:
            return {
                'hookSpecificOutput': {
                    'hookEventName': 'PreToolUse',
                    'permissionDecision': 'deny',
                    'permissionDecisionReason': 'File modifications disabled in production'
                }
            }
    return {}

# Subagents
security_scanner = AgentDefinition(
    description="Security vulnerability scanner",
    prompt="Analyze code for security issues. Check OWASP Top 10.",
    tools=["Read", "Grep", "WebSearch"],
    model="sonnet"
)

# Complete options
options = ClaudeAgentOptions(
    # Session control
    cwd="/app/project",
    max_turns=200,

    # System behavior
    system_prompt="You are a production automation system. Be precise and cautious.",
    permission_mode="default",
    include_partial_messages=True,

    # Tool access (whitelist approach)
    allowed_tools=[
        "Read",
        "Grep",
        "Glob",
        "WebSearch",
        "Task",
        "mcp__database__query"
    ],

    # MCP servers
    mcp_servers={
        "database": {
            "type": "http",
            "url": "https://db-api.example.com/mcp"
        }
    },

    # Structured output
    output_format={
        "type": "json_schema",
        "schema": {
            "type": "object",
            "properties": {
                "status": {"type": "string", "enum": ["success", "failure"]},
                "results": {"type": "array", "items": {"type": "object"}}
            },
            "required": ["status"]
        }
    },

    # Hooks
    hooks={
        'PreToolUse': [
            HookMatcher(matcher='*', hooks=[audit_tool_use, block_production_writes])
        ]
    },

    # Subagents
    agents={
        "security": security_scanner
    },

    # Settings
    setting_sources=["project"]
)
```

## Parameter Validation

**Type Checking:**
- All parameters are type-checked at runtime
- Invalid types raise `TypeError`
- Use IDE with type hints for autocomplete

**Common Validation Errors:**
```
errors[5]{error,cause,solution}:
TypeError,Invalid parameter type,"Use correct type (str, list, dict, etc.)"
ValueError,Invalid permission_mode,"Use: default|acceptEdits|plan|bypassPermissions"
KeyError,Missing required hook fields,Ensure hook returns proper structure
ValidationError,Invalid JSON schema,Validate schema with JSON Schema validator
AttributeError,Unknown parameter,Check spelling and parameter availability
```

## Best Practices

**Security:**
1. Use `allowed_tools` whitelist instead of `disallowed_tools` blacklist
2. Implement `can_use_tool` for dynamic permission logic
3. Never use `bypassPermissions` without explicit user consent
4. Validate file paths in PreToolUse hooks
5. Load minimal `setting_sources` for security-critical applications

**Performance:**
1. Set `max_turns` to prevent infinite loops
2. Use `permission_mode="acceptEdits"` for automated workflows
3. Enable `include_partial_messages` only when needed
4. Choose appropriate model for subagents (haiku for simple tasks)

**Maintainability:**
1. Document custom `system_prompt` for team understanding
2. Keep hook functions simple and focused
3. Use descriptive agent names and descriptions
4. Centralize configuration in reusable options objects

**Debugging:**
1. Start with minimal options and add complexity gradually
2. Use `permission_mode="plan"` to test without execution
3. Enable `include_partial_messages` to see real-time progress
4. Add logging hooks to track tool usage

## Common Configuration Patterns

### Pattern 1: Read-Only Analysis

```python
options = ClaudeAgentOptions(
    allowed_tools=["Read", "Grep", "Glob", "WebSearch"],
    permission_mode="default",
    max_turns=50
)
```

### Pattern 2: Automated Refactoring

```python
options = ClaudeAgentOptions(
    permission_mode="acceptEdits",
    allowed_tools=["Read", "Write", "Edit", "Grep", "Bash"],
    cwd="/project/src",
    max_turns=100
)
```

### Pattern 3: Secure Production Automation

```python
async def production_validator(tool_name, tool_input):
    """Strict validation for production."""
    # Only allow reads
    return tool_name in ["Read", "Grep"]

options = ClaudeAgentOptions(
    can_use_tool=production_validator,
    permission_mode="default",
    setting_sources=["project"],
    max_turns=25
)
```

### Pattern 4: Multi-Agent Orchestration

```python
options = ClaudeAgentOptions(
    agents={
        "analyzer": AgentDefinition(...),
        "implementer": AgentDefinition(...),
        "tester": AgentDefinition(...)
    },
    allowed_tools=["Task", "Read"],
    max_turns=150
)
```

## See Also

- **Main Skill:** [../skill.md](../skill.md)
- **Tools Reference:** [tools.md](tools.md)
- **Hooks Reference:** [hooks.md](hooks.md)
- **Examples:** [../examples/basic.md](../examples/basic.md)
