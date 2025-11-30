# Advanced Hooks Examples

Security validation, audit logging, rate limiting, and production-ready hook patterns.

## Example 1: Security Validation Hooks

**Use Case:** Validate and block dangerous operations

```python
import asyncio
import re
from claude_agent_sdk import (
    query,
    ClaudeAgentOptions,
    HookMatcher,
    HookContext
)
from typing import Any

async def validate_bash_commands(
    input_data: dict[str, Any],
    tool_use_id: str | None,
    context: HookContext
) -> dict[str, Any]:
    """Block dangerous bash commands."""
    if input_data['tool_name'] != 'Bash':
        return {}

    command = input_data['tool_input'].get('command', '')

    # Dangerous patterns
    dangerous_patterns = [
        r'rm\s+-rf\s+/',
        r'mkfs',
        r':.*\{.*\|.*:.*&.*\}.*;:',  # Fork bomb
        r'dd\s+if=/dev/zero',
        r'>\s*/dev/sd[a-z]',
        r'chmod\s+-R\s+777',
        r'curl.*\|.*sh',  # Piping to shell
        r'wget.*&&.*chmod.*&&.*\./',
    ]

    for pattern in dangerous_patterns:
        if re.search(pattern, command):
            return {
                'hookSpecificOutput': {
                    'hookEventName': 'PreToolUse',
                    'permissionDecision': 'deny',
                    'permissionDecisionReason': f'Blocked dangerous pattern: {pattern}'
                }
            }

    return {}

async def validate_file_operations(
    input_data: dict[str, Any],
    tool_use_id: str | None,
    context: HookContext
) -> dict[str, Any]:
    """Ensure file operations stay within project directory."""
    tool_name = input_data['tool_name']

    if tool_name not in ['Read', 'Write', 'Edit']:
        return {}

    file_path = input_data['tool_input'].get('file_path', '')
    allowed_dirs = ['/home/user/project/', '/tmp/workspace/']

    if not any(file_path.startswith(d) for d in allowed_dirs):
        return {
            'hookSpecificOutput': {
                'hookEventName': 'PreToolUse',
                'permissionDecision': 'deny',
                'permissionDecisionReason': f'File access restricted to: {", ".join(allowed_dirs)}'
            }
        }

    return {}

async def main():
    options = ClaudeAgentOptions(
        allowed_tools=["Bash", "Read", "Write", "Edit", "Grep"],
        hooks={
            'PreToolUse': [
                HookMatcher(matcher='Bash', hooks=[validate_bash_commands]),
                HookMatcher(matcher='*', hooks=[validate_file_operations])
            ]
        }
    )

    async for message in query(
        "Delete all system files with rm -rf /",
        options
    ):
        print(message)

asyncio.run(main())
```

## Example 2: Audit Logging

**Use Case:** Log all tool executions to audit trail

```python
import asyncio
import logging
import json
from datetime import datetime
from claude_agent_sdk import (
    query,
    ClaudeAgentOptions,
    HookMatcher,
    HookContext
)
from typing import Any

# Setup logging
logging.basicConfig(
    filename='/var/log/claude-audit.log',
    level=logging.INFO,
    format='%(message)s'
)
logger = logging.getLogger(__name__)

async def audit_tool_usage(
    input_data: dict[str, Any],
    tool_use_id: str | None,
    context: HookContext
) -> dict[str, Any]:
    """Log all tool executions to audit trail."""
    tool_name = input_data['tool_name']
    tool_result = input_data.get('tool_result', {})

    # Determine success/failure
    is_error = tool_result.get('isError', False)

    # Create audit entry
    audit_entry = {
        'timestamp': datetime.now().isoformat(),
        'session_id': context.session_id,
        'turn_number': context.turn_number,
        'tool_name': tool_name,
        'tool_use_id': tool_use_id,
        'status': 'ERROR' if is_error else 'SUCCESS',
        'input': input_data['tool_input'] if 'tool_input' in input_data else None
    }

    # Log to file
    logger.info(json.dumps(audit_entry))

    # Also log to console for demo
    print(f"[AUDIT] {tool_name}: {'ERROR' if is_error else 'SUCCESS'}")

    return {}

async def main():
    options = ClaudeAgentOptions(
        allowed_tools=["Read", "Grep", "Bash"],
        hooks={
            'PostToolUse': [
                HookMatcher(matcher='*', hooks=[audit_tool_usage])
            ]
        }
    )

    async for message in query("List files and search for TODO comments", options):
        print(message)

asyncio.run(main())
```

**Audit Log Output:**
```json
{"timestamp": "2025-01-15T10:30:00", "session_id": "abc123", "tool_name": "Bash", "status": "SUCCESS"}
{"timestamp": "2025-01-15T10:30:05", "session_id": "abc123", "tool_name": "Grep", "status": "SUCCESS"}
```

## Example 3: Rate Limiting

**Use Case:** Prevent API abuse with rate limiting

```python
import asyncio
from collections import defaultdict
from datetime import datetime, timedelta
from claude_agent_sdk import (
    query,
    ClaudeAgentOptions,
    HookMatcher,
    HookContext
)
from typing import Any

class RateLimiter:
    def __init__(self):
        self.requests = defaultdict(list)

    async def check_rate_limit(
        self,
        input_data: dict[str, Any],
        tool_use_id: str | None,
        context: HookContext
    ) -> dict[str, Any]:
        """Limit tool usage per session."""
        session_id = context.session_id
        tool_name = input_data['tool_name']
        now = datetime.now()

        # Clean old entries (older than 1 minute)
        cutoff = now - timedelta(minutes=1)
        self.requests[session_id] = [
            req for req in self.requests[session_id]
            if req['timestamp'] > cutoff
        ]

        # Define limits per tool
        limits = {
            'Bash': 10,        # 10 bash commands per minute
            'WebSearch': 5,    # 5 searches per minute
            'WebFetch': 10,    # 10 fetches per minute
        }

        if tool_name in limits:
            count = sum(
                1 for req in self.requests[session_id]
                if req['tool_name'] == tool_name
            )

            if count >= limits[tool_name]:
                return {
                    'hookSpecificOutput': {
                        'hookEventName': 'PreToolUse',
                        'permissionDecision': 'deny',
                        'permissionDecisionReason': (
                            f'Rate limit exceeded: {limits[tool_name]} '
                            f'{tool_name} calls per minute'
                        )
                    }
                }

        # Record request
        self.requests[session_id].append({
            'tool_name': tool_name,
            'timestamp': now
        })

        return {}

async def main():
    rate_limiter = RateLimiter()

    options = ClaudeAgentOptions(
        allowed_tools=["Bash", "WebSearch", "WebFetch"],
        hooks={
            'PreToolUse': [
                HookMatcher(matcher='*', hooks=[rate_limiter.check_rate_limit])
            ]
        }
    )

    async for message in query("Research Python frameworks", options):
        print(message)

asyncio.run(main())
```

## See Also

- **Advanced MCP:** [advanced-mcp.md](advanced-mcp.md)
- **Advanced Agents:** [advanced-agents.md](advanced-agents.md)
- **Main Skill:** [../skill.md](../skill.md)
