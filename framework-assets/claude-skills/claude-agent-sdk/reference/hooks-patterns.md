- Final logging
- Metrics aggregation
- Session archival

**Example - Cleanup Resources:**
```python
async def cleanup_on_stop(input_data, tool_use_id, context):
    """Clean up resources when agent stops."""
    exit_reason = input_data.get('exit_reason')
    session_id = input_data.get('session_id')

    logger.info(f"Session {session_id} stopped: {exit_reason}")

    # Close database connections
    if hasattr(context.metadata, 'db_connection'):
        await context.metadata['db_connection'].close()

    # Kill background processes
    if hasattr(context.metadata, 'background_processes'):
        for process_id in context.metadata['background_processes']:
            # Kill process logic here
            pass

    # Save session summary
    with open(f'/var/log/sessions/{session_id}.json', 'w') as f:
        json.dump({
            'session_id': session_id,
            'exit_reason': exit_reason,
            'total_turns': input_data.get('total_turns'),
            'total_cost': input_data.get('total_cost'),
            'timestamp': datetime.now().isoformat()
        }, f)

    return {}

options = ClaudeAgentOptions(
    hooks={
        'Stop': [
            HookMatcher(matcher='*', hooks=[cleanup_on_stop])
        ]
    }
)
```

### SubagentStop Event

**Trigger:** Subagent completes execution

**Input Data Structure:**
```python
input_data = {
    'agent_name': 'reviewer',
    'result': {
        'content': [...],
        'success': True
    },
    'duration': 12.5  # seconds
}
```

**Use Cases:**
- Aggregate subagent results
- Track subagent performance
- Coordinate multi-agent workflows

**Example - Aggregate Results:**
```python
async def aggregate_subagent_results(input_data, tool_use_id, context):
    """Collect and aggregate subagent outputs."""
    agent_name = input_data.get('agent_name')
    result = input_data.get('result')
    duration = input_data.get('duration')

    # Store in context for orchestrator access
    if 'subagent_results' not in context.metadata:
        context.metadata['subagent_results'] = {}

    context.metadata['subagent_results'][agent_name] = {
        'result': result,
        'duration': duration,
        'timestamp': datetime.now().isoformat()
    }

    logger.info(f"Subagent {agent_name} completed in {duration}s")

    return {}

options = ClaudeAgentOptions(
    hooks={
        'SubagentStop': [
            HookMatcher(matcher='*', hooks=[aggregate_subagent_results])
        ]
    }
)
```

### PreCompact Event

**Trigger:** Before message history compaction

**Input Data Structure:**
```python
input_data = {
    'message_count': 150,
    'messages': [...]  # List of messages to be compacted
}
```

**Use Cases:**
- Preserve critical messages
- Archive full history before compaction
- Selective message retention

**Example - Archive Before Compaction:**
```python
async def archive_before_compact(input_data, tool_use_id, context):
    """Archive messages before they're compacted."""
    messages = input_data.get('messages', [])
    session_id = context.session_id

    # Archive to database or file
    archive_path = f'/var/log/message-archives/{session_id}.jsonl'

    with open(archive_path, 'a') as f:
        for message in messages:
            f.write(json.dumps({
                'session_id': session_id,
                'timestamp': datetime.now().isoformat(),
                'message': message
            }) + '\n')

    logger.info(f"Archived {len(messages)} messages from session {session_id}")

    return {}

options = ClaudeAgentOptions(
    hooks={
        'PreCompact': [
            HookMatcher(matcher='*', hooks=[archive_before_compact])
        ]
    }
)
```

## Advanced Hook Patterns

### Pattern 1: Environment-Based Validation

```python
import os

async def environment_aware_validation(input_data, tool_use_id, context):
    """Different validation rules for different environments."""
    env = os.getenv('ENV', 'development')
    tool_name = input_data['tool_name']

    # Production restrictions
    if env == 'production':
        # Block all write operations
        if tool_name in ['Write', 'Edit', 'Bash']:
            return {
                'hookSpecificOutput': {
                    'hookEventName': 'PreToolUse',
                    'permissionDecision': 'deny',
                    'permissionDecisionReason': 'Write operations disabled in production'
                }
            }

    # Staging - require approval
    elif env == 'staging':
        if tool_name == 'Bash':
            # Could trigger manual approval flow here
            pass

    # Development - allow everything
    return {}
```

### Pattern 2: Rate Limiting

```python
from collections import defaultdict
from datetime import datetime, timedelta

class RateLimiter:
    def __init__(self):
        self.requests = defaultdict(list)

    async def check_rate_limit(self, input_data, tool_use_id, context):
        """Limit tool usage per session."""
        session_id = context.session_id
        tool_name = input_data['tool_name']
        now = datetime.now()

        # Clean old entries
        cutoff = now - timedelta(minutes=1)
        self.requests[session_id] = [
            req for req in self.requests[session_id]
            if req['timestamp'] > cutoff
        ]

        # Check limit (e.g., 10 bash commands per minute)
        if tool_name == 'Bash':
            bash_count = sum(
                1 for req in self.requests[session_id]
                if req['tool_name'] == 'Bash'
            )

            if bash_count >= 10:
                return {
                    'hookSpecificOutput': {
                        'hookEventName': 'PreToolUse',
                        'permissionDecision': 'deny',
                        'permissionDecisionReason': 'Rate limit exceeded (10 Bash commands/minute)'
                    }
                }

        # Record request
        self.requests[session_id].append({
            'tool_name': tool_name,
            'timestamp': now
        })

        return {}

rate_limiter = RateLimiter()

options = ClaudeAgentOptions(
    hooks={
        'PreToolUse': [
            HookMatcher(matcher='*', hooks=[rate_limiter.check_rate_limit])
        ]
    }
)
```

### Pattern 3: Tool Chaining Validation

```python
async def validate_tool_sequence(input_data, tool_use_id, context):
    """Ensure tools are used in valid sequences."""
    tool_name = input_data['tool_name']

    # Initialize sequence tracker
    if 'tool_sequence' not in context.metadata:
        context.metadata['tool_sequence'] = []

    sequence = context.metadata['tool_sequence']

    # Rule: Must Read before Edit
    if tool_name == 'Edit':
        file_path = input_data['tool_input'].get('file_path')
        last_read = next(
            (t for t in reversed(sequence) if t['tool'] == 'Read' and t['file'] == file_path),
            None
        )

        if not last_read:
            return {
                'hookSpecificOutput': {
                    'hookEventName': 'PreToolUse',
                    'permissionDecision': 'deny',
                    'permissionDecisionReason': 'Must Read file before Edit'
                }
            }

    # Record tool usage
    sequence.append({
        'tool': tool_name,
        'file': input_data['tool_input'].get('file_path'),
        'timestamp': datetime.now()
    })

    return {}
```

### Pattern 4: Multi-Hook Composition

```python
async def log_hook(input_data, tool_use_id, context):
    """Logging hook."""
    logger.info(f"Tool executed: {input_data['tool_name']}")
    return {}

async def validate_hook(input_data, tool_use_id, context):
    """Validation hook."""
    # Validation logic
    return {}

async def metrics_hook(input_data, tool_use_id, context):
    """Metrics collection hook."""
    # Metrics logic
    return {}

# All hooks execute in order
options = ClaudeAgentOptions(
    hooks={
        'PreToolUse': [
            HookMatcher(
                matcher='*',
                hooks=[log_hook, validate_hook, metrics_hook]
            )
        ]
    }
)
```

## Best Practices

**Design Principles:**
1. **Keep hooks simple and focused** - Each hook should do one thing
2. **Fail fast** - Return early for better performance
3. **Log decisions** - Track why hooks block or allow actions
4. **Use matcher specificity** - Prefer specific tool names over '*'
5. **Maintain stateless hooks** - Use context.metadata for state

**Performance:**
1. Avoid heavy computation in hooks
2. Use async operations for I/O
3. Cache validation results when possible
4. Minimize hook count per event

**Security:**
1. Validate all input data
2. Sanitize error messages (no sensitive data leakage)
3. Use allowlists over denylists
4. Log security decisions for audit

**Error Handling:**
```python
async def safe_hook(input_data, tool_use_id, context):
    """Hook with proper error handling."""
    try:
        # Hook logic
        return validation_result()
    except Exception as e:
        logger.error(f"Hook error: {e}", exc_info=True)
        # Decide: block on error (safe) or allow (permissive)
        return {}  # Allow by default
```

## Debugging Hooks

**Logging Pattern:**
```python
import logging

logger = logging.getLogger(__name__)

async def debug_hook(input_data, tool_use_id, context):
    """Debug hook with comprehensive logging."""
    logger.debug(f"Hook triggered: {input_data}")
    logger.debug(f"Tool use ID: {tool_use_id}")
    logger.debug(f"Context: session={context.session_id}, turn={context.turn_number}")

    result = {}  # Hook logic

    logger.debug(f"Hook result: {result}")
    return result
```

**Testing Hooks:**
```python
import pytest
from unittest.mock import Mock

@pytest.mark.asyncio
async def test_validate_bash_hook():
    """Test bash validation hook."""
    # Mock input data
    input_data = {
        'tool_name': 'Bash',
        'tool_input': {'command': 'rm -rf /'}
    }

    # Mock context
    context = Mock()
    context.session_id = 'test_session'

    # Execute hook
    result = await validate_bash_commands(input_data, 'test_id', context)

    # Assert blocked
    assert result['hookSpecificOutput']['permissionDecision'] == 'deny'
```

## Common Pitfalls

**Avoid These Mistakes:**
```
pitfalls[5]{mistake,problem,solution}:
Blocking on I/O,Slows agent execution,Use async operations
Returning None,Causes errors,Always return dict (empty or with data)
Modifying input_data,Unpredictable behavior,Treat as read-only
Raising exceptions,Breaks agent flow,Use try/except and return empty dict
Complex logic in hooks,Performance degradation,Keep hooks simple and fast
```

## See Also

- **Main Skill:** [../skill.md](../skill.md)
- **Options Reference:** [options.md](options.md)
- **Tools Reference:** [tools.md](tools.md)
- **Advanced Examples:** [../examples/advanced.md](../examples/advanced.md)
