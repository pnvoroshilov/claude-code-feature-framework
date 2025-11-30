# Hooks System - Complete Reference

Comprehensive guide to the Claude Agent SDK hooks system for lifecycle event interception.

## Overview

Hooks enable interception of agent lifecycle events for validation, logging, monitoring, and behavioral modification. Implement custom logic at critical execution points without modifying core agent behavior.

## What Are Hooks?

**Hooks are async functions that:**
- Execute at specific lifecycle events
- Receive event-specific input data
- Can block, modify, or observe operations
- Enable custom authorization and auditing
- Support tool-specific or global matching

**Key Use Cases:**
```
use_cases[7]{use_case,hook_type,example}:
Command validation,PreToolUse,Block dangerous bash commands
Authorization,PreToolUse,Check user permissions before file access
Audit logging,PostToolUse,Log all tool executions to file
Input sanitization,UserPromptSubmit,Filter sensitive data from prompts
Error handling,PostToolUse,Retry failed operations
Cleanup operations,Stop,Release resources on completion
Result processing,SubagentStop,Aggregate subagent outputs
```

## Hook Architecture

**Hook Flow (TOON):**
```
flow_stages[5]{stage,action,can_block}:
Event triggered,Agent reaches lifecycle point,No
Hook matching,Match patterns against event,No
Hook execution,Run matched hook functions in order,No
Response processing,Interpret hook return values,Yes
Action execution,Proceed or block based on response,N/A
```

## Hook Events

**Available Events (TOON):**
```
events[7]{event,trigger_point,input_data_includes}:
PreToolUse,Before tool execution,"tool_name, tool_input, tool_use_id"
PostToolUse,After tool completes,"tool_name, tool_result, tool_use_id"
UserPromptSubmit,User submits prompt,prompt_text
Stop,Agent execution stops,"exit_reason, session_id"
SubagentStop,Subagent completes,"agent_name, result"
PreCompact,Before message compaction,"message_count, messages"
AgentError,Error during execution,"error_type, error_message"
```

## Hook Function Signature

**Standard Hook Function:**
```python
async def hook_function(
    input_data: dict[str, Any],
    tool_use_id: str | None,
    context: HookContext
) -> dict[str, Any]:
    """
    Hook function signature.

    Args:
        input_data: Event-specific data (tool name, inputs, results, etc.)
        tool_use_id: Unique ID for tool execution (None for non-tool events)
        context: Hook execution context (session info, metadata)

    Returns:
        Dictionary with hook-specific output (empty dict for no action)
    """
    # Hook logic here
    return {}  # or return hook-specific output
```

**Parameters Explained:**
```
parameters[3]{parameter,type,description}:
input_data,dict[str: Any],"Event-specific data (varies by event type)"
tool_use_id,str | None,"Unique tool execution ID (None for non-tool events)"
context,HookContext,"Hook execution context (session, metadata, etc.)"
```

## HookContext Object

**Available Context Information:**
```python
class HookContext:
    session_id: str          # Current session identifier
    turn_number: int         # Current conversation turn
    timestamp: str           # Event timestamp (ISO 8601)
    metadata: dict          # Custom metadata
```

## Hook Configuration

**Configuration Structure:**
```python
from claude_agent_sdk import ClaudeAgentOptions, HookMatcher

options = ClaudeAgentOptions(
    hooks={
        'EventName': [
            HookMatcher(
                matcher="pattern",
                hooks=[hook_function1, hook_function2]
            )
        ]
    }
)
```

**HookMatcher Parameters:**
```
matcher_params[2]{parameter,type,description}:
matcher,str,"Pattern to match (tool name, '*' for all, 'mcp__server__*' for MCP tools)"
hooks,list[Callable],"List of async hook functions to execute"
```

**Matcher Patterns (TOON):**
```
patterns[4]{pattern,matches,example}:
'ToolName',Specific tool only,'Bash' matches Bash tool
'*',All tools/events,'*' matches everything
'mcp__server__*',All tools from MCP server,'mcp__calc__*' matches all calc tools
'mcp__server__tool',Specific MCP tool,'mcp__calc__add' matches only add
```

## Event-Specific Details

### PreToolUse Event

**Trigger:** Before any tool execution

**Input Data Structure:**
```python
input_data = {
    'tool_name': 'Bash',
    'tool_input': {
        'command': 'ls -la',
        'timeout': 120000
    }
}
```

**Hook Return for Blocking:**
```python
return {
    'hookSpecificOutput': {
        'hookEventName': 'PreToolUse',
        'permissionDecision': 'deny',  # or 'allow'
        'permissionDecisionReason': 'Dangerous command blocked'
    }
}
```

**Permission Decisions:**
```
decisions[3]{decision,effect,use_case}:
deny,Block tool execution,Security validation failure
allow,Force approval (override prompt),Trusted automation
(empty),Continue normal flow,No intervention
```

**Example - Block Dangerous Bash:**
```python
async def validate_bash_commands(input_data, tool_use_id, context):
    """Block dangerous bash commands."""
    if input_data['tool_name'] != 'Bash':
        return {}

    command = input_data['tool_input'].get('command', '')

    # Dangerous patterns
    dangerous = [
        'rm -rf /',
        'mkfs',
        ':(){:|:&};:',  # Fork bomb
        'dd if=/dev/zero',
        '> /dev/sda'
    ]

    for pattern in dangerous:
        if pattern in command:
            return {
                'hookSpecificOutput': {
                    'hookEventName': 'PreToolUse',
                    'permissionDecision': 'deny',
                    'permissionDecisionReason': f'Blocked dangerous pattern: {pattern}'
                }
            }

    return {}

options = ClaudeAgentOptions(
    hooks={
        'PreToolUse': [
            HookMatcher(matcher='Bash', hooks=[validate_bash_commands])
        ]
    }
)
```

**Example - Restrict File Paths:**
```python
async def validate_file_paths(input_data, tool_use_id, context):
    """Ensure file operations stay within project directory."""
    tool_name = input_data['tool_name']

    if tool_name not in ['Read', 'Write', 'Edit']:
        return {}

    file_path = input_data['tool_input'].get('file_path', '')
    allowed_prefix = '/home/user/project/'

    if not file_path.startswith(allowed_prefix):
        return {
            'hookSpecificOutput': {
                'hookEventName': 'PreToolUse',
                'permissionDecision': 'deny',
                'permissionDecisionReason': f'File access restricted to {allowed_prefix}'
            }
        }

    return {}

options = ClaudeAgentOptions(
    hooks={
        'PreToolUse': [
            HookMatcher(matcher='*', hooks=[validate_file_paths])
        ]
    }
)
```

### PostToolUse Event

**Trigger:** After tool execution completes

**Input Data Structure:**
```python
input_data = {
    'tool_name': 'Bash',
    'tool_result': {
        'content': [{'type': 'text', 'text': 'file1.txt\nfile2.txt'}],
        'exit_code': 0
    }
}
```

**Use Cases:**
- Audit logging
- Result transformation
- Error handling and retry logic
- Metrics collection

**Example - Audit Logging:**
```python
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

async def audit_tool_usage(input_data, tool_use_id, context):
    """Log all tool executions to audit trail."""
    tool_name = input_data['tool_name']
    tool_result = input_data.get('tool_result', {})

    # Determine success/failure
    is_error = tool_result.get('isError', False)
    status = 'ERROR' if is_error else 'SUCCESS'

    # Log to audit trail
    logger.info(
        f"[AUDIT] {datetime.now().isoformat()} | "
        f"Session: {context.session_id} | "
        f"Tool: {tool_name} | "
        f"Status: {status} | "
        f"Turn: {context.turn_number}"
    )

    # Persist to database or file
    with open('/var/log/claude-audit.log', 'a') as f:
        f.write(
            f"{datetime.now().isoformat()},{context.session_id},"
            f"{tool_name},{status},{tool_use_id}\n"
        )

    return {}

options = ClaudeAgentOptions(
    hooks={
        'PostToolUse': [
            HookMatcher(matcher='*', hooks=[audit_tool_usage])
        ]
    }
)
```

**Example - Error Handling:**
```python
async def retry_failed_operations(input_data, tool_use_id, context):
    """Retry failed tool executions with exponential backoff."""
    tool_result = input_data.get('tool_result', {})

    if not tool_result.get('isError'):
        return {}  # Success, no retry needed

    tool_name = input_data['tool_name']
    max_retries = 3

    # Track retry count in context metadata
    retry_key = f'retry_{tool_use_id}'
    retry_count = context.metadata.get(retry_key, 0)

    if retry_count < max_retries:
        context.metadata[retry_key] = retry_count + 1
        logger.warning(f"Retrying {tool_name} (attempt {retry_count + 1})")

        # Could trigger retry logic here
        # (implementation depends on SDK capabilities)

    return {}
```

### UserPromptSubmit Event

**Trigger:** When user submits a prompt

**Input Data Structure:**
```python
input_data = {
    'prompt_text': 'User query here...',
    'timestamp': '2025-01-15T10:30:00Z'
}
```

**Use Cases:**
- Input validation
- Sensitive data filtering
- Prompt augmentation
- Rate limiting

**Example - Sanitize Sensitive Data:**
```python
import re

async def sanitize_prompt(input_data, tool_use_id, context):
    """Remove sensitive information from prompts."""
    prompt = input_data.get('prompt_text', '')

    # Patterns to redact
    patterns = {
        'email': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
        'phone': r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b',
        'ssn': r'\b\d{3}-\d{2}-\d{4}\b',
        'api_key': r'[Aa]pi[_-]?[Kk]ey["\s:=]+[\w-]+',
        'password': r'[Pp]assword["\s:=]+\S+'
    }

    sanitized = prompt
    for pattern_name, regex in patterns.items():
        sanitized = re.sub(regex, f'[REDACTED_{pattern_name.upper()}]', sanitized)

    if sanitized != prompt:
        logger.warning(f"Sanitized sensitive data from prompt in session {context.session_id}")
        # Note: Actual prompt modification may require SDK support
        # This example demonstrates detection

    return {}

options = ClaudeAgentOptions(
    hooks={
        'UserPromptSubmit': [
            HookMatcher(matcher='*', hooks=[sanitize_prompt])
        ]
    }
)
```

### Stop Event

**Trigger:** Agent execution completes or stops

**Input Data Structure:**
```python
input_data = {
    'exit_reason': 'max_turns_reached',  # or 'user_interrupt', 'completion', 'error'
    'session_id': 'session_abc123',
    'total_turns': 45,
    'total_cost': 0.0234
}
```

**Use Cases:**
- Resource cleanup
