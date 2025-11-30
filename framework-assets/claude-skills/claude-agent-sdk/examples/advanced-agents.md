# Advanced Agent Examples

Multi-agent orchestration, structured output, production configurations, and streaming patterns.

## Example 1: Multi-Agent Orchestration

**Use Case:** Coordinate specialized agents for complex workflow

```python
import asyncio
from claude_agent_sdk import (
    query,
    ClaudeAgentOptions,
    AgentDefinition
)

# Define specialized agents
code_reviewer = AgentDefinition(
    description="Expert Python code reviewer focusing on security and best practices",
    prompt="""You are a senior Python developer. Review code for:
    - Security vulnerabilities (SQL injection, XSS, etc.)
    - Performance issues
    - Code style and PEP 8 compliance
    - Best practices and design patterns
    Provide specific, actionable feedback.""",
    tools=["Read", "Grep", "Glob"],
    model="sonnet"
)

test_writer = AgentDefinition(
    description="Automated test case generator using pytest",
    prompt="""You write comprehensive unit tests using pytest.
    - Aim for 100% code coverage
    - Include edge cases and error conditions
    - Use fixtures and parameterization
    - Follow AAA pattern (Arrange, Act, Assert)""",
    tools=["Read", "Write", "Bash"],
    model="sonnet"
)

documentation_writer = AgentDefinition(
    description="Technical documentation specialist",
    prompt="""You write clear, comprehensive documentation:
    - API references with examples
    - Usage guides
    - Architecture explanations
    Use markdown format with proper structure.""",
    tools=["Read", "Write", "Glob"],
    model="haiku"  # Faster model for docs
)

refactoring_expert = AgentDefinition(
    description="Code refactoring specialist",
    prompt="""You refactor code to improve:
    - Readability and maintainability
    - Performance
    - Modularity and reusability
    Preserve functionality while improving structure.""",
    tools=["Read", "Write", "Edit", "Bash"],
    model="sonnet"
)

async def main():
    options = ClaudeAgentOptions(
        agents={
            "reviewer": code_reviewer,
            "tester": test_writer,
            "documenter": documentation_writer,
            "refactor": refactoring_expert
        },
        allowed_tools=["Task", "Read", "Glob"],
        cwd="/home/user/my-project"
    )

    prompt = """Complete project improvement workflow:
    1. Review all Python files for issues
    2. Refactor problematic code
    3. Write comprehensive tests
    4. Generate API documentation

    Coordinate between specialized agents as needed.
    """

    async for message in query(prompt, options):
        print(message)

asyncio.run(main())
```

**Orchestration Flow:**
1. Main agent delegates to "reviewer" → Identifies issues
2. Main agent delegates to "refactor" → Fixes issues
3. Main agent delegates to "tester" → Writes tests
4. Main agent delegates to "documenter" → Creates docs

## Example 2: Structured Output with JSON Schema

**Use Case:** Guarantee structured, parseable output

```python
import asyncio
import json
from claude_agent_sdk import query, ClaudeAgentOptions

async def extract_structured_data():
    """Extract user data in guaranteed JSON format."""
    user_schema = {
        "type": "object",
        "properties": {
            "name": {"type": "string"},
            "age": {"type": "integer", "minimum": 0, "maximum": 150},
            "email": {"type": "string", "format": "email"},
            "role": {"type": "string", "enum": ["admin", "user", "moderator"]},
            "skills": {
                "type": "array",
                "items": {"type": "string"}
            },
            "active": {"type": "boolean"}
        },
        "required": ["name", "email", "role"]
    }

    options = ClaudeAgentOptions(
        output_format={
            "type": "json_schema",
            "schema": user_schema
        },
        allowed_tools=["Read", "Grep"]
    )

    async for message in query(
        "Extract user information from the config file at /app/users.yaml",
        options
    ):
        if hasattr(message, 'content'):
            for block in message.content:
                if hasattr(block, 'text'):
                    user_data = json.loads(block.text)
                    print(f"Name: {user_data['name']}")
                    print(f"Email: {user_data['email']}")
                    print(f"Skills: {', '.join(user_data.get('skills', []))}")

asyncio.run(extract_structured_data())
```

## Example 3: Code Analysis with Structured Output

**Use Case:** Structured code analysis findings

```python
import asyncio
from claude_agent_sdk import query, ClaudeAgentOptions

async def code_analysis():
    """Analyze code with structured output."""
    analysis_schema = {
        "type": "object",
        "properties": {
            "summary": {"type": "string"},
            "findings": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "severity": {
                            "type": "string",
                            "enum": ["critical", "high", "medium", "low", "info"]
                        },
                        "category": {
                            "type": "string",
                            "enum": ["security", "performance", "style", "bug", "design"]
                        },
                        "description": {"type": "string"},
                        "file": {"type": "string"},
                        "line": {"type": "integer"},
                        "suggestion": {"type": "string"}
                    },
                    "required": ["severity", "category", "description"]
                }
            },
            "metrics": {
                "type": "object",
                "properties": {
                    "files_analyzed": {"type": "integer"},
                    "lines_of_code": {"type": "integer"},
                    "issues_found": {"type": "integer"},
                    "critical_issues": {"type": "integer"}
                }
            }
        },
        "required": ["summary", "findings", "metrics"]
    }

    options = ClaudeAgentOptions(
        output_format={"type": "json_schema", "schema": analysis_schema},
        allowed_tools=["Read", "Grep", "Glob"],
        cwd="/home/user/project"
    )

    async for message in query(
        "Perform comprehensive security analysis of all Python files",
        options
    ):
        print(message)

asyncio.run(code_analysis())
```

## Example 4: Production-Ready Configuration

**Use Case:** Complete production configuration with all safeguards

```python
import asyncio
import os
import logging
from claude_agent_sdk import (
    query,
    ClaudeAgentOptions,
    HookMatcher,
    HookContext,
    AgentDefinition
)
from typing import Any

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def production_security(
    input_data: dict[str, Any],
    tool_use_id: str | None,
    context: HookContext
) -> dict[str, Any]:
    """Production security checks."""
    if os.getenv("ENV") != "production":
        return {}

    tool_name = input_data['tool_name']

    # Block all write operations in production
    if tool_name in ['Write', 'Edit', 'Bash']:
        return {
            'hookSpecificOutput': {
                'hookEventName': 'PreToolUse',
                'permissionDecision': 'deny',
                'permissionDecisionReason': 'Write operations disabled in production'
            }
        }

    return {}

async def audit_logger(
    input_data: dict[str, Any],
    tool_use_id: str | None,
    context: HookContext
) -> dict[str, Any]:
    """Comprehensive audit logging."""
    logger.info(
        f"[AUDIT] Session: {context.session_id}, "
        f"Tool: {input_data['tool_name']}, "
        f"Turn: {context.turn_number}"
    )
    return {}

security_scanner = AgentDefinition(
    description="Security vulnerability scanner",
    prompt="Analyze code for security issues. Check OWASP Top 10.",
    tools=["Read", "Grep", "WebSearch"],
    model="sonnet"
)

async def production_agent():
    """Production-ready agent configuration."""
    options = ClaudeAgentOptions(
        # Session control
        cwd="/app/project",
        max_turns=100,

        # System behavior
        system_prompt="You are a production security analysis system. Be thorough and cautious.",
        permission_mode="default",

        # Tool access (strict whitelist)
        allowed_tools=["Read", "Grep", "Glob", "WebSearch", "Task"],

        # Structured output
        output_format={
            "type": "json_schema",
            "schema": {
                "type": "object",
                "properties": {
                    "status": {"type": "string", "enum": ["safe", "issues_found"]},
                    "findings": {"type": "array", "items": {"type": "object"}}
                },
                "required": ["status"]
            }
        },

        # Hooks
        hooks={
            'PreToolUse': [
                HookMatcher(matcher='*', hooks=[production_security, audit_logger])
            ],
            'PostToolUse': [
                HookMatcher(matcher='*', hooks=[audit_logger])
            ]
        },

        # Subagents
        agents={"security": security_scanner},

        # Settings
        setting_sources=["project"]
    )

    async for message in query("Perform security analysis of the application", options):
        print(message)

asyncio.run(production_agent())
```

## Example 5: Streaming Input Construction

**Use Case:** Dynamically build context during execution

```python
import asyncio
from claude_agent_sdk import ClaudeSDKClient

async def dynamic_context_builder():
    """Build prompt context dynamically."""
    yield {"type": "text", "text": "Analyze the following data:\n\n"}

    # Simulate fetching data from multiple sources
    data_sources = [
        "/data/metrics.json",
        "/data/logs.txt",
        "/data/config.yaml"
    ]

    for source in data_sources:
        await asyncio.sleep(0.5)
        content = f"Content from {source}..."

        yield {
            "type": "text",
            "text": f"\n\n## {source}\n{content}"
        }

    yield {"type": "text", "text": "\n\nProvide comprehensive analysis."}

async def main():
    async with ClaudeSDKClient() as client:
        await client.query(dynamic_context_builder())
        async for message in client.receive_response():
            print(message)

asyncio.run(main())
```

## Example 6: Interrupt Handling

**Use Case:** Stop long-running agent execution

```python
import asyncio
from claude_agent_sdk import ClaudeSDKClient

async def interruptible_agent():
    """Agent that can be interrupted."""
    async with ClaudeSDKClient() as client:
        await client.query("Analyze every file in this massive codebase")

        async for message in client.receive_response():
            print(message)

            # Check for interrupt condition
            if should_interrupt():
                await client.interrupt()
                print("Agent interrupted by user")
                break

def should_interrupt():
    """Check if interrupt is requested."""
    # Implementation depends on your use case
    return False

asyncio.run(interruptible_agent())
```

## See Also

- **Advanced MCP:** [advanced-mcp.md](advanced-mcp.md)
- **Advanced Hooks:** [advanced-hooks.md](advanced-hooks.md)
- **Main Skill:** [../skill.md](../skill.md)
