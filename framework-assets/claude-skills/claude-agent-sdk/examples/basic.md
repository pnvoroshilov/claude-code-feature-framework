# Basic Examples - Claude Agent SDK

Getting started examples for common use cases with the Claude Agent SDK.

## Installation & Setup

```bash
# Install SDK
pip install claude-agent-sdk

# Verify installation
python -c "from claude_agent_sdk import query; print('SDK installed successfully')"
```

**Prerequisites:**
- Python 3.9+
- Claude Code CLI installed (`npm install -g @anthropic-ai/claude-code`)
- Valid Anthropic API key configured

## Example 1: Simple One-Off Query

**Use Case:** Execute a single task with no conversation continuity

```python
import asyncio
from claude_agent_sdk import query

async def simple_query():
    """Ask Claude a simple question."""
    async for message in query("What's 25 * 47?"):
        print(message)

# Run
asyncio.run(simple_query())
```

**Output:**
```
AssistantMessage(content=[TextBlock(text="25 * 47 = 1,175")])
ResultMessage(sessionId="session_abc123", totalCost=0.001, duration=1.2)
```

## Example 2: File Creation

**Use Case:** Generate a Python script

```python
import asyncio
from claude_agent_sdk import query, ClaudeAgentOptions

async def create_web_server():
    """Ask Claude to create a Flask web server."""
    options = ClaudeAgentOptions(
        permission_mode="acceptEdits",  # Auto-approve file creation
        cwd="/home/user/projects/my-app",
        allowed_tools=["Write", "Read"]
    )

    async for message in query(
        "Create a simple Flask web server with a hello world endpoint",
        options
    ):
        print(message)

asyncio.run(create_web_server())
```

**What Happens:**
1. Claude creates `/home/user/projects/my-app/app.py`
2. File contains Flask server with GET / endpoint
3. No permission prompt (auto-approved via `acceptEdits`)

## Example 3: Code Analysis

**Use Case:** Analyze existing codebase

```python
import asyncio
from claude_agent_sdk import query, ClaudeAgentOptions

async def analyze_code():
    """Analyze Python code for issues."""
    options = ClaudeAgentOptions(
        cwd="/home/user/my-project",
        allowed_tools=["Read", "Grep", "Glob"],
        permission_mode="default"
    )

    prompt = """Analyze this Python project:
    1. Find all Python files
    2. Check for security issues
    3. Identify code smells
    4. Suggest improvements
    """

    async for message in query(prompt, options):
        # Process messages
        if hasattr(message, 'content'):
            for block in message.content:
                if hasattr(block, 'text'):
                    print(block.text)

asyncio.run(analyze_code())
```

**Claude's Actions:**
1. Uses `Glob` to find all .py files
2. Uses `Read` to examine each file
3. Uses `Grep` to search for patterns (SQL injection, eval(), etc.)
4. Provides analysis report

## Example 4: Persistent Conversation

**Use Case:** Multi-turn conversation with context retention

```python
import asyncio
from claude_agent_sdk import ClaudeSDKClient, AssistantMessage, TextBlock

async def conversation():
    """Have a multi-turn conversation."""
    async with ClaudeSDKClient() as client:
        # First question
        await client.query("What files are in the current directory?")
        async for msg in client.receive_response():
            if isinstance(msg, AssistantMessage):
                for block in msg.content:
                    if isinstance(block, TextBlock):
                        print(f"Claude: {block.text}")

        # Follow-up (Claude remembers context)
        await client.query("Can you show me the largest file?")
        async for msg in client.receive_response():
            if isinstance(msg, AssistantMessage):
                for block in msg.content:
                    if isinstance(block, TextBlock):
                        print(f"Claude: {block.text}")

        # Another follow-up
        await client.query("What type of file is it?")
        async for msg in client.receive_response():
            if isinstance(msg, AssistantMessage):
                for block in msg.content:
                    if isinstance(block, TextBlock):
                        print(f"Claude: {block.text}")

asyncio.run(conversation())
```

**Key Point:** Each query remembers previous conversation. Claude knows which file you're referring to in the third question.

## Example 5: Tool Access Control

**Use Case:** Restrict agent to read-only operations

```python
import asyncio
from claude_agent_sdk import query, ClaudeAgentOptions

async def read_only_analysis():
    """Analyze code without allowing modifications."""
    options = ClaudeAgentOptions(
        allowed_tools=[
            "Read",
            "Grep",
            "Glob",
            "WebSearch"  # Allow internet research
        ],
        # Note: Bash, Write, Edit are NOT in allowed_tools
        cwd="/home/user/project"
    )

    async for message in query(
        "Analyze this project and suggest architectural improvements",
        options
    ):
        print(message)

asyncio.run(read_only_analysis())
```

**Security:** Claude cannot modify files, execute commands, or perform destructive operations.

## Example 6: Custom System Prompt

**Use Case:** Specialize Claude's expertise

```python
import asyncio
from claude_agent_sdk import query, ClaudeAgentOptions

async def specialized_agent():
    """Create a specialized DevOps agent."""
    options = ClaudeAgentOptions(
        system_prompt="""You are an expert DevOps engineer specializing in:
        - Kubernetes and container orchestration
        - CI/CD pipeline design
        - Infrastructure as Code (Terraform, CloudFormation)
        - Monitoring and observability

        Always consider:
        - Security best practices
        - High availability and scalability
        - Cost optimization
        """,
        allowed_tools=["Read", "Write", "Bash", "WebSearch"]
    )

    async for message in query(
        "Review this Kubernetes deployment and suggest improvements",
        options
    ):
        print(message)

asyncio.run(specialized_agent())
```

**Result:** Claude responds with DevOps-specific expertise and considerations.

## Example 7: Search and Process Files

**Use Case:** Find and process specific files

```python
import asyncio
from claude_agent_sdk import query, ClaudeAgentOptions

async def refactor_imports():
    """Find and refactor import statements."""
    options = ClaudeAgentOptions(
        permission_mode="acceptEdits",
        allowed_tools=["Grep", "Read", "Edit"],
        cwd="/home/user/project/src"
    )

    prompt = """
    1. Find all Python files importing 'old_module'
    2. Replace with 'new_module'
    3. Update import syntax to match new API
    """

    async for message in query(prompt, options):
        print(message)

asyncio.run(refactor_imports())
```

**Claude's Workflow:**
1. `Grep(pattern="import old_module", type="python")`
2. `Read` each file to understand context
3. `Edit` to replace old imports with new ones

## Example 8: Web Research

**Use Case:** Gather information from the internet

```python
import asyncio
from claude_agent_sdk import query, ClaudeAgentOptions

async def research_topic():
    """Research a technical topic online."""
    options = ClaudeAgentOptions(
        allowed_tools=["WebSearch", "WebFetch"],
        permission_mode="default"
    )

    async for message in query(
        "Research best practices for Python async programming in 2025",
        options
    ):
        print(message)

asyncio.run(research_topic())
```

**Claude's Actions:**
1. `WebSearch(query="Python async best practices 2025")`
2. `WebFetch` top results to analyze content
3. Synthesizes findings into comprehensive summary

## Example 9: Background Command Execution

**Use Case:** Start long-running process and monitor

```python
import asyncio
from claude_agent_sdk import query, ClaudeAgentOptions

async def run_tests_background():
    """Run test suite in background and monitor."""
    options = ClaudeAgentOptions(
        allowed_tools=["Bash", "BashOutput"],
        cwd="/home/user/project"
    )

    prompt = """
    1. Start pytest in background
    2. Monitor output every 5 seconds
    3. Report when complete
    """

    async for message in query(prompt, options):
        print(message)

asyncio.run(run_tests_background())
```

**Claude's Workflow:**
1. `Bash(command="pytest tests/", run_in_background=True)` → Returns shell_id
2. Periodically calls `BashOutput(bash_id=shell_id)` to check progress
3. Reports test results when complete

## Example 10: Error Handling

**Use Case:** Gracefully handle errors

```python
import asyncio
from claude_agent_sdk import (
    query,
    CLINotFoundError,
    ProcessError,
    CLIJSONDecodeError
)

async def safe_query():
    """Query with comprehensive error handling."""
    try:
        async for message in query("Analyze this project"):
            print(message)

    except CLINotFoundError:
        print("ERROR: Claude Code CLI not installed")
        print("Install: npm install -g @anthropic-ai/claude-code")

    except ProcessError as e:
        print(f"Process failed with exit code {e.exit_code}")
        if e.stderr:
            print(f"Error: {e.stderr}")

    except CLIJSONDecodeError as e:
        print(f"Failed to parse response: {e}")
        print("Try updating Claude Code CLI")

    except Exception as e:
        print(f"Unexpected error: {e}")

asyncio.run(safe_query())
```

## Example 11: Session Resume

**Use Case:** Continue previous session

```python
import asyncio
from claude_agent_sdk import query, ClaudeAgentOptions

async def resume_session():
    """Resume from previous session."""
    # First session
    print("=== First Session ===")
    async for message in query("List files in current directory"):
        if hasattr(message, 'sessionId'):
            session_id = message.sessionId
            print(f"Session ID: {session_id}")

    # Resume later
    print("\n=== Resumed Session ===")
    options = ClaudeAgentOptions(
        continue_conversation=True,
        resume=session_id,
        fork_session=True  # Create branch (don't modify original)
    )

    async for message in query(
        "What was the largest file?",
        options
    ):
        print(message)

asyncio.run(resume_session())
```

**Use Case:** Pause and resume work, or create alternative branches from same starting point.

## Example 12: Limit Conversation Turns

**Use Case:** Prevent infinite loops in automation

```python
import asyncio
from claude_agent_sdk import query, ClaudeAgentOptions

async def limited_conversation():
    """Limit agent to maximum 10 turns."""
    options = ClaudeAgentOptions(
        max_turns=10,
        allowed_tools=["Read", "Grep", "Glob"]
    )

    async for message in query(
        "Analyze all Python files in this large project",
        options
    ):
        print(message)

asyncio.run(limited_conversation())
```

**Safety:** Agent stops after 10 conversation turns even if task incomplete.

## Example 13: Message Filtering

**Use Case:** Process only specific message types

```python
import asyncio
from claude_agent_sdk import (
    query,
    AssistantMessage,
    TextBlock,
    ToolUseBlock,
    ResultMessage
)

async def filter_messages():
    """Extract only text responses."""
    text_responses = []

    async for message in query("Explain Python decorators"):
        if isinstance(message, AssistantMessage):
            for block in message.content:
                if isinstance(block, TextBlock):
                    text_responses.append(block.text)

        elif isinstance(message, ResultMessage):
            print(f"Session cost: ${message.totalCost}")

    # Print collected text
    full_response = "\n".join(text_responses)
    print(full_response)

asyncio.run(filter_messages())
```

## Example 14: Real-Time Tool Monitoring

**Use Case:** Track which tools Claude uses

```python
import asyncio
from claude_agent_sdk import query, ToolUseBlock, AssistantMessage

async def monitor_tools():
    """Monitor tool usage in real-time."""
    tools_used = []

    async for message in query("Analyze this codebase"):
        if isinstance(message, AssistantMessage):
            for block in message.content:
                if isinstance(block, ToolUseBlock):
                    tools_used.append({
                        'tool': block.toolName,
                        'input': block.toolInput
                    })
                    print(f"[TOOL] {block.toolName}: {block.toolInput}")

    print(f"\nTotal tools used: {len(tools_used)}")

asyncio.run(monitor_tools())
```

**Output:**
```
[TOOL] Glob: {'pattern': '**/*.py'}
[TOOL] Read: {'file_path': '/project/main.py'}
[TOOL] Grep: {'pattern': 'TODO', 'type': 'python'}

Total tools used: 3
```

## Example 15: Setting Sources Control

**Use Case:** Pure SDK mode without filesystem settings

```python
import asyncio
from claude_agent_sdk import query, ClaudeAgentOptions

async def pure_sdk_mode():
    """Run without loading any settings files."""
    options = ClaudeAgentOptions(
        setting_sources=[],  # Don't load user/project settings
        system_prompt="You are a Python expert",
        allowed_tools=["Read", "Write"],
        cwd="/tmp/workspace"
    )

    async for message in query("Create a hello world script", options):
        print(message)

asyncio.run(pure_sdk_mode())
```

**Use Case:** Portable SDK applications, containerized environments, testing.

## Common Patterns Summary (TOON)

```
patterns[10]{pattern,use_case,key_option}:
One-off query,Single task execution,"query() with options"
Persistent session,Multi-turn conversation,ClaudeSDKClient
Read-only,Safe analysis,"allowed_tools=['Read', 'Grep']"
Auto-approve,Automation workflows,permission_mode='acceptEdits'
Specialized agent,Domain expertise,system_prompt with expertise
Web research,Internet information,"allowed_tools=['WebSearch', 'WebFetch']"
Background execution,Long-running tasks,Bash with run_in_background
Session resume,Continue previous work,"continue_conversation=True"
Turn limiting,Prevent infinite loops,max_turns
Pure SDK,No filesystem deps,setting_sources=[]
```

## Next Steps

**After mastering basics:**
1. Explore [advanced.md](advanced.md) for MCP servers, hooks, and subagents
2. Review [../reference/options.md](../reference/options.md) for all configuration options
3. Study [../reference/tools.md](../reference/tools.md) for complete tool reference
4. Learn hooks in [../reference/hooks.md](../reference/hooks.md)

## See Also

- **Main Skill:** [../skill.md](../skill.md)
- **Advanced Examples:** [advanced.md](advanced.md)
- **Options Reference:** [../reference/options.md](../reference/options.md)
- **Tools Reference:** [../reference/tools.md](../reference/tools.md)
